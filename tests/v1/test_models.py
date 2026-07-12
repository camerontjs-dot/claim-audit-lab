"""Pydantic round-trip + validation tests for the v1 contract types.

These pin the contract: any field rename or shape change shows up here
before it shows up in a consumer.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from claim_audit_lab.v1.models import (
    AuditConfig,
    AuditRequest,
    AuditTrace,
    EntailResult,
    ExtractedFeatures,
    ModelRevision,
    Passage,
    Quantity,
    RetrievalResult,
    RuleFired,
    SupportSignal,
    Verdict,
)


def _audit_config() -> AuditConfig:
    return AuditConfig(
        top_k=5,
        retrieval_floor=0.40,
        supported_threshold=0.70,
        contradicted_threshold=0.70,
        aggregation="max_entailment",
        rules_file_sha="0" * 64,
        retriever=ModelRevision(
            model_id="sentence-transformers/all-MiniLM-L6-v2",
            hf_revision_sha="a" * 40,
        ),
        entailer=ModelRevision(
            model_id="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
            hf_revision_sha="b" * 40,
        ),
    )


def test_passage_round_trip() -> None:
    passage = Passage(passage_id="p-1", text="Some evidence.", source_meta={"src": "doc-1"})
    assert Passage.model_validate(passage.model_dump()) == passage


def test_audit_config_defaults_validate() -> None:
    cfg = _audit_config()
    assert cfg.top_k == 5
    assert cfg.aggregation == "max_entailment"


def test_audit_config_rejects_out_of_range_thresholds() -> None:
    with pytest.raises(ValidationError):
        AuditConfig(
            top_k=5,
            retrieval_floor=1.5,
            supported_threshold=0.70,
            contradicted_threshold=0.70,
            aggregation="max_entailment",
            rules_file_sha="0" * 64,
            retriever=ModelRevision(model_id="r", hf_revision_sha="a" * 40),
            entailer=ModelRevision(model_id="e", hf_revision_sha="b" * 40),
        )


def test_audit_request_round_trip() -> None:
    req = AuditRequest(
        claim_id="clm-1",
        claim_text="The system reduces unsupported claims.",
        passages=[Passage(passage_id="p-1", text="Some evidence.")],
        audit_config=_audit_config(),
    )
    round_tripped = AuditRequest.model_validate(req.model_dump())
    assert round_tripped == req


def test_audit_trace_round_trip() -> None:
    trace = AuditTrace(
        claim_id="clm-1",
        claim_text="X.",
        retrieval=[RetrievalResult(passage_id="p-1", score=0.75)],
        entailment=[
            EntailResult(
                passage_id="p-1",
                label="entail",
                score=0.92,
                raw_logits=(2.1, -1.0, -0.5),
            )
        ],
        features=ExtractedFeatures(
            numerical_values=[Quantity(value=5.0, unit="percent", surface_text="5%")],
            has_explicit_negation=False,
            has_universal_quantifier=False,
            modal_strength="asserts",
        ),
        support_signal=SupportSignal(
            label="entail",
            max_entailment_score=0.92,
            contributing_passage_id="p-1",
        ),
        rules_fired=[RuleFired(rule_id="r-numeric-agreement", reason="exact match")],
        verdict=Verdict(support_verdict="supported"),
        audit_config_hash="0" * 64,
        library_version="1.0.0",
    )
    assert AuditTrace.model_validate(trace.model_dump()) == trace


def test_verdict_two_axis_shape() -> None:
    """The verdict is two-axis (C-B v2.0.0): a degree + non-exclusive flags +
    an orthogonal citation status. ``overstated`` is a flag, not a degree."""
    v = Verdict(
        support_verdict="partially_supported",
        audit_flags=["overstated"],
        citation_status="wrong_source",
        audit_confidence="high",
    )
    assert v.support_verdict == "partially_supported"
    assert "overstated" in v.audit_flags
    assert v.citation_status == "wrong_source"
    assert v.audit_confidence == "high"


def test_verdict_defaults_and_not_checkable_reason() -> None:
    """Degree defaults: no flags, not_applicable citation, medium confidence.
    ``support_verdict_reason`` carries the not_checkable sub-classification."""
    plain = Verdict(support_verdict="supported")
    assert plain.audit_flags == []
    assert plain.citation_status == "not_applicable"
    assert plain.audit_confidence == "medium"
    nc = Verdict(support_verdict="not_checkable", support_verdict_reason="no_evidence")
    assert nc.support_verdict_reason == "no_evidence"


def test_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Passage.model_validate({"passage_id": "p-1", "text": "x", "bogus": True})


def test_models_are_frozen() -> None:
    passage = Passage(passage_id="p-1", text="x")
    with pytest.raises(ValidationError):
        passage.passage_id = "p-2"  # type: ignore[misc]
