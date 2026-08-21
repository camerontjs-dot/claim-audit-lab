"""Tests for the explicitly experimental shadow decision table."""

from __future__ import annotations

import pytest

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.evidence_state import project_evidence_state
from claim_audit_lab.v1.models import (
    AuditTrace,
    EntailResult,
    ExtractedFeatures,
    SupportSignal,
    Verdict,
    VerdictReason,
)
from scripts.evidence_state_shadow import shadow_decide

_CONFIG = load_default_audit_config()


def _result(pid: str, support: float, refutation: float) -> EntailResult:
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
        ([], "not_checkable"),
        ([_result("p1", 0.19, 0.19)], "unsupported"),
        ([_result("p1", 0.4, 0.1)], "partially_supported"),
        ([_result("p1", 0.8, 0.1)], "supported"),
        ([_result("p1", 0.1, 0.4)], "unsupported"),
        ([_result("p1", 0.1, 0.8)], "contradicted"),
        ([_result("p1", 0.4, 0.4)], "needs_review"),
    ],
)
def test_shadow_decision_table(results: list[EntailResult], expected: str) -> None:
    trace = _trace(results)
    assert shadow_decide(trace, project_evidence_state(trace), _CONFIG).verdict == expected


def test_out_of_scope_remains_not_checkable_in_shadow() -> None:
    reason: VerdictReason = "out_of_scope"
    trace = _trace([_result("p1", 0.8, 0.1)], reason=reason)
    decision = shadow_decide(trace, project_evidence_state(trace), _CONFIG)
    assert decision.verdict == "not_checkable"
    assert decision.support_verdict_reason == "out_of_scope"
