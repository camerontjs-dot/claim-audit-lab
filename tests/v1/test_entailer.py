"""Tests for the real DeBERTa entailer (Phase 2 Unit 2 / B11).

Exercises ``DeBERTaEntailer`` against the pinned
``MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`` revision. The 5-pair fixture
covers all three classes (3 entail, 1 neutral, 1 contradict) with hand-checked
labels. Three properties matter: the expected labels, byte-identical raw_logits
across runs (the trace-reproducibility property), and that ``raw_logits`` is
captured correctly — re-deriving the label by argmax over the recorded logits
matches the entailer's own output.
"""

from __future__ import annotations

import pytest

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer, _load_model
from claim_audit_lab.v1.models import EntailLabel, ModelRevision

_CONFIG = load_default_audit_config()

# (passage_id, claim, premise, expected_label) — verified against the model.
_PAIRS: list[tuple[str, str, str, EntailLabel]] = [
    ("e1", "The system encrypts stored data.", "All stored data is encrypted at rest.", "entail"),
    (
        "e2",
        "Administrator actions are logged.",
        "Every administrator action is recorded in an audit log.",
        "entail",
    ),
    (
        "e3",
        "The service has high uptime.",
        "The service maintained 99.95 percent uptime.",
        "entail",
    ),
    (
        "n1",
        "The system encrypts stored data.",
        "The local weather forecast predicts rain on Thursday.",
        "neutral",
    ),
    (
        "c1",
        "The platform logs administrator actions.",
        "The platform does not log any administrator actions.",
        "contradict",
    ),
]


@pytest.fixture(scope="module")
def entailer() -> DeBERTaEntailer:
    return DeBERTaEntailer(revision=_CONFIG.entailer)


def test_loads_from_pinned_revision(entailer: DeBERTaEntailer) -> None:
    assert entailer.revision.hf_revision_sha == "6f5cf0a2b59cabb106aca4c287eed12e357e90eb"


@pytest.mark.parametrize(
    ("passage_id", "claim", "premise", "expected"),
    _PAIRS,
    ids=[pair[0] for pair in _PAIRS],
)
def test_expected_labels(
    entailer: DeBERTaEntailer,
    passage_id: str,
    claim: str,
    premise: str,
    expected: EntailLabel,
) -> None:
    result = entailer.entail(claim, premise, passage_id)
    assert result.label == expected
    assert result.passage_id == passage_id
    assert 0.0 <= result.score <= 1.0
    assert len(result.raw_logits) == 3


def test_determinism_byte_identical_raw_logits(entailer: DeBERTaEntailer) -> None:
    claim, premise = "The system encrypts stored data.", "All stored data is encrypted at rest."
    first = entailer.entail(claim, premise, "p")
    second = entailer.entail(claim, premise, "p")
    assert first.model_dump_json() == second.model_dump_json()
    assert first.raw_logits == second.raw_logits


@pytest.mark.parametrize(
    ("passage_id", "claim", "premise", "expected"),
    _PAIRS,
    ids=[pair[0] for pair in _PAIRS],
)
def test_raw_logits_label_crosscheck(
    entailer: DeBERTaEntailer,
    passage_id: str,
    claim: str,
    premise: str,
    expected: EntailLabel,
) -> None:
    """Re-deriving the label from the recorded raw_logits (argmax → label_order)
    must match the entailer's own label — proof the logits are captured in the
    model's native class order, so a downstream consumer can re-threshold them."""
    _, _, label_order = _load_model(_CONFIG.entailer.model_id, _CONFIG.entailer.hf_revision_sha)
    result = entailer.entail(claim, premise, passage_id)
    argmax_index = max(range(3), key=lambda i: result.raw_logits[i])
    assert label_order[argmax_index] == result.label


def test_unpinned_revision_raises() -> None:
    unpinned = DeBERTaEntailer(
        revision=ModelRevision(
            model_id="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli", hf_revision_sha=""
        )
    )
    with pytest.raises(ValueError, match="pinned hf_revision_sha"):
        unpinned.entail("a", "b", "p")
