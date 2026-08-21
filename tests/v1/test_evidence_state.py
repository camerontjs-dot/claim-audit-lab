"""Stage 1-2 evidence-state projection and shadow-table tests."""

from __future__ import annotations

import pytest

from claim_audit_lab.v1.evidence_state import (
    project_evidence_state,
    with_derived_channel_probabilities,
)
from claim_audit_lab.v1.models import (
    AuditTrace,
    EntailResult,
    ExtractedFeatures,
    SupportSignal,
    Verdict,
    VerdictReason,
)


def _result(pid: str, support: float | None, refutation: float | None) -> EntailResult:
    return EntailResult(
        passage_id=pid,
        label="neutral",
        score=0.9,
        raw_logits=(0.0, 0.0, 0.0),
        p_entail=support,
        p_contradict=refutation,
    )


def _trace(
    results: list[EntailResult], *, reason: VerdictReason | None = "no_entail_signal"
) -> AuditTrace:
    return AuditTrace(
        claim_id="claim-1",
        claim_text="The system records each review outcome.",
        retrieval=[],
        entailment=results,
        features=ExtractedFeatures(),
        support_signal=SupportSignal(
            label="neutral", max_entailment_score=0.9, contributing_passage_id="p1"
        ),
        rules_fired=[],
        verdict=Verdict(
            support_verdict="not_checkable", support_verdict_reason=reason, audit_confidence="low"
        ),
        audit_config_hash="sha256:test",
        library_version="test",
    )


@pytest.mark.parametrize(
    ("results", "expected"),
    [
        ([], "no_evidence"),
        ([_result("p1", None, None)], "unmeasured"),
        ([_result("p1", 0.19, 0.19)], "read_silent"),
        ([_result("p1", 0.20, 0.19)], "support_only"),
        ([_result("p1", 0.19, 0.20)], "refutation_only"),
        ([_result("p1", 0.20, 0.20)], "mixed"),
    ],
)
def test_projection_state_matrix(results: list[EntailResult], expected: str) -> None:
    assert project_evidence_state(_trace(results)).state == expected


def test_projection_preserves_sorted_channel_provenance_sets() -> None:
    projection = project_evidence_state(_trace([_result("p2", 0.4, 0.3), _result("p1", 0.6, 0.8)]))
    assert [(item.passage_id, item.score) for item in projection.support_candidates] == [
        ("p1", 0.6),
        ("p2", 0.4),
    ]
    assert [(item.passage_id, item.score) for item in projection.refutation_candidates] == [
        ("p1", 0.8),
        ("p2", 0.3),
    ]


def test_legacy_batch_derives_channels_from_recorded_logits_without_mutation() -> None:
    legacy_entail = EntailResult(
        passage_id="p1",
        label="entail",
        score=0.8,
        raw_logits=(2.0, 0.0, -1.0),
    )
    legacy_contradict = EntailResult(
        passage_id="p2",
        label="contradict",
        score=0.8,
        raw_logits=(-1.0, 0.0, 2.0),
    )
    trace = _trace([legacy_entail, legacy_contradict])
    (enriched,) = with_derived_channel_probabilities([trace])
    assert trace.entailment[0].p_entail is None
    assert enriched.entailment[0].p_entail is not None
    assert enriched.entailment[1].p_contradict is not None
    assert project_evidence_state(enriched).state == "mixed"
