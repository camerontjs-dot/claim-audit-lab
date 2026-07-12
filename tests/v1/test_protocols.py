"""Protocol conformance tests for the v1 swappable layers.

These verify that the v1 impl classes structurally satisfy their protocols.
They only assert structural conformance (``isinstance`` against the
``@runtime_checkable`` protocols) and exercise the dependency-free aggregator;
the real model-loading retriever/entailer behaviour is covered by
``test_retriever.py`` / ``test_entailer.py``, so these tests load no models.
"""

from __future__ import annotations

import pytest

from claim_audit_lab.v1.impl import (
    BiEncoderRetriever,
    DeBERTaEntailer,
    MaxEntailmentAggregator,
    VerdictRules,
)
from claim_audit_lab.v1.models import (
    EntailResult,
    ModelRevision,
    SupportSignal,
)
from claim_audit_lab.v1.protocols import Aggregator, Entailer, Retriever, Rules


def test_bi_encoder_retriever_satisfies_protocol() -> None:
    impl = BiEncoderRetriever(
        revision=ModelRevision(
            model_id="sentence-transformers/all-MiniLM-L6-v2",
            hf_revision_sha="a" * 40,
        )
    )
    assert isinstance(impl, Retriever)


def test_deberta_entailer_satisfies_protocol() -> None:
    impl = DeBERTaEntailer(
        revision=ModelRevision(
            model_id="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
            hf_revision_sha="b" * 40,
        )
    )
    assert isinstance(impl, Entailer)


def test_max_entailment_aggregator_satisfies_protocol() -> None:
    assert isinstance(MaxEntailmentAggregator(), Aggregator)


def test_verdict_rules_satisfies_protocol() -> None:
    assert isinstance(VerdictRules(rules_file_sha="0" * 64), Rules)


def test_aggregator_picks_highest_score() -> None:
    """Among support-bearing passages, the highest-scoring one wins."""
    agg = MaxEntailmentAggregator()
    results = [
        EntailResult(passage_id="p-1", label="entail", score=0.10, raw_logits=(0.1, 0.0, 0.0)),
        EntailResult(passage_id="p-2", label="entail", score=0.92, raw_logits=(2.0, 0.0, 0.0)),
        EntailResult(
            passage_id="p-3",
            label="neutral",
            score=0.45,
            raw_logits=(0.5, 0.5, 0.0),
        ),
    ]
    signal = agg.aggregate(results)
    assert signal.label == "entail"
    assert signal.max_entailment_score == pytest.approx(0.92)
    assert signal.contributing_passage_id == "p-2"


def test_aggregator_neutral_does_not_mask_entail() -> None:
    """A confidently-neutral passage must not outrank a real entailment.

    The real-inference masking bug (DECISIONS.md § 2026-06-29): a neutral score is
    confidence the passage is *irrelevant*, not evidence against the claim, so it
    abstains rather than competing.
    """
    agg = MaxEntailmentAggregator()
    results = [
        EntailResult(passage_id="p-1", label="entail", score=0.95, raw_logits=(3.0, 0.0, -3.0)),
        EntailResult(passage_id="p-2", label="neutral", score=0.99, raw_logits=(-2.0, 4.0, -2.0)),
    ]
    signal = agg.aggregate(results)
    assert signal.label == "entail"
    assert signal.contributing_passage_id == "p-1"
    assert signal.max_entailment_score == pytest.approx(0.95)


def test_aggregator_neutral_does_not_mask_contradict() -> None:
    """A confidently-neutral passage must not outrank a real contradiction.

    The masked-contradiction case is the dangerous one — the rules-layer A4 gate
    never sees a contradiction the aggregator threw away.
    """
    agg = MaxEntailmentAggregator()
    results = [
        EntailResult(passage_id="p-1", label="contradict", score=0.96, raw_logits=(-3.0, 0.0, 3.0)),
        EntailResult(passage_id="p-2", label="neutral", score=0.99, raw_logits=(-2.0, 4.0, -2.0)),
    ]
    signal = agg.aggregate(results)
    assert signal.label == "contradict"
    assert signal.contributing_passage_id == "p-1"
    assert signal.max_entailment_score == pytest.approx(0.96)


def test_aggregator_all_neutral_falls_back_to_top_neutral() -> None:
    """With no support-bearing passage, the strongest neutral is the signal
    (the rules layer reads this as no_entail_signal → not_checkable)."""
    agg = MaxEntailmentAggregator()
    results = [
        EntailResult(passage_id="p-1", label="neutral", score=0.40, raw_logits=(0.0, 0.4, 0.0)),
        EntailResult(passage_id="p-2", label="neutral", score=0.80, raw_logits=(0.0, 0.8, 0.0)),
    ]
    signal = agg.aggregate(results)
    assert signal.label == "neutral"
    assert signal.contributing_passage_id == "p-2"
    assert signal.max_entailment_score == pytest.approx(0.80)


def test_aggregator_conflicting_evidence_higher_score_wins() -> None:
    """Documented residual: with both a strong entail and a strong contradict on
    the same claim, the higher-scoring one wins and the other is not surfaced.

    Genuinely conflicting evidence; the single-signal contract cannot carry both.
    The two-signal upgrade (DECISIONS.md § 2026-06-29) is the fix if Phase-4
    calibration shows this case matters. Locked here so the behaviour is explicit.
    """
    agg = MaxEntailmentAggregator()
    results = [
        EntailResult(passage_id="p-1", label="entail", score=0.96, raw_logits=(3.0, 0.0, -3.0)),
        EntailResult(passage_id="p-2", label="contradict", score=0.95, raw_logits=(-3.0, 0.0, 3.0)),
    ]
    signal = agg.aggregate(results)
    assert signal.label == "entail"
    assert signal.contributing_passage_id == "p-1"


def test_aggregator_handles_empty_input() -> None:
    signal = MaxEntailmentAggregator().aggregate([])
    assert signal == SupportSignal(
        label="neutral", max_entailment_score=0.0, contributing_passage_id=None
    )
