"""Tests for the real bi-encoder retriever (Phase 2 Unit 1 / B10).

Exercises ``BiEncoderRetriever`` against the pinned
``sentence-transformers/all-MiniLM-L6-v2`` revision. The 3-claim × 5-passage
fixture is written so the cosine ordering is obvious by eye (each claim has one
clearly on-topic passage; ``p-weather`` and ``p-recipe`` are off-topic for every
claim). Two properties matter for the trace contract: the expected top-k ordering
and run-to-run determinism (byte-identical scores).

The model loads once for the module via the session-scoped fixture (the
``BiEncoderRetriever`` itself relies on the module-level ``_load_model`` cache).
"""

from __future__ import annotations

import pytest

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.retriever import BiEncoderRetriever
from claim_audit_lab.v1.models import ModelRevision, Passage

_CONFIG = load_default_audit_config()

# 5 topically distinct passages, reused across the 3 claims.
_PASSAGES = [
    Passage(
        passage_id="p-enc", text="All stored customer data is encrypted at rest using AES-256."
    ),
    Passage(
        passage_id="p-uptime",
        text="The service maintained 99.95 percent uptime over the last quarter.",
    ),
    Passage(
        passage_id="p-audit",
        text="Every administrator action is recorded in an immutable audit log.",
    ),
    Passage(
        passage_id="p-weather",
        text="The local weather forecast predicts rain on Thursday afternoon.",
    ),
    Passage(
        passage_id="p-recipe", text="This recipe calls for two cups of flour and a pinch of salt."
    ),
]

# Each claim's hand-checked best-matching passage (verified against the model).
_CLAIM_EXPECTED_TOP = [
    ("Customer data is encrypted when stored.", "p-enc"),
    ("Administrator actions are logged.", "p-audit"),
    ("The platform has high availability.", "p-uptime"),
]

_OFF_TOPIC = {"p-weather", "p-recipe"}


@pytest.fixture(scope="module")
def retriever() -> BiEncoderRetriever:
    return BiEncoderRetriever(revision=_CONFIG.retriever)


def test_loads_from_pinned_revision(retriever: BiEncoderRetriever) -> None:
    # The revision under test is the pinned default SHA; a successful retrieve
    # proves the model loaded from that revision.
    assert retriever.revision.hf_revision_sha == "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
    assert retriever.retrieve("anything", _PASSAGES, top_k=5)


@pytest.mark.parametrize(
    ("claim", "expected_top"),
    _CLAIM_EXPECTED_TOP,
    ids=[expected for _, expected in _CLAIM_EXPECTED_TOP],
)
def test_expected_top_ranking(retriever: BiEncoderRetriever, claim: str, expected_top: str) -> None:
    results = retriever.retrieve(claim, _PASSAGES, top_k=5)
    assert [r.passage_id for r in results][0] == expected_top
    # Scores are sorted strictly descending (stable on ties).
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)
    # The two clearly off-topic passages never beat the on-topic match.
    assert set([r.passage_id for r in results][-2:]) == _OFF_TOPIC


def test_top_k_truncates(retriever: BiEncoderRetriever) -> None:
    results = retriever.retrieve("Customer data is encrypted when stored.", _PASSAGES, top_k=2)
    assert len(results) == 2
    assert results[0].passage_id == "p-enc"


def test_determinism_byte_identical_scores(retriever: BiEncoderRetriever) -> None:
    claim = "Customer data is encrypted when stored."
    first = retriever.retrieve(claim, _PASSAGES, top_k=5)
    second = retriever.retrieve(claim, _PASSAGES, top_k=5)
    assert [r.model_dump_json() for r in first] == [r.model_dump_json() for r in second]


def test_empty_passages_returns_empty(retriever: BiEncoderRetriever) -> None:
    assert retriever.retrieve("anything", [], top_k=5) == []


def test_unpinned_revision_raises() -> None:
    unpinned = BiEncoderRetriever(
        revision=ModelRevision(
            model_id="sentence-transformers/all-MiniLM-L6-v2", hf_revision_sha=""
        )
    )
    with pytest.raises(ValueError, match="pinned hf_revision_sha"):
        unpinned.retrieve("anything", _PASSAGES, top_k=5)
