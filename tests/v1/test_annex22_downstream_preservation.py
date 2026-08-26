"""Downstream preservation and Annex 22 stress vectors.

These tests begin at the CAL-facing apparatus boundary. Claim decomposition, source
collection, and authority classification are assumed to have happened upstream.
The subject under test is whether CAL preserves every admitted contribution while
using eligibility, semantic validity, aperture, and later resolution as non-destructive
decision views.
"""

from __future__ import annotations

from typing import Literal

from claim_audit_lab.v1.decision_model import (
    CANONICAL_STAGE_ORDER,
    ChannelApertureAssessment,
    ChannelMeasurement,
    EligibilityAssessment,
    EvidenceContribution,
    EvidenceDecisionInput,
    EvidenceDecisionTrace,
    StageReceipt,
    ValidityAssessment,
    evaluate_evidence,
)

_RECEIPT = "sha256:" + "7" * 64
_POLICY_RECEIPT = "sha256:" + "8" * 64


def _assessment(
    *,
    eligibility: Literal["eligible", "ineligible", "unknown"] = "eligible",
    validity: Literal["valid", "invalid", "unknown"] = "valid",
    operator: str = "contract_supplied_relation",
) -> tuple[EligibilityAssessment, ValidityAssessment]:
    return (
        EligibilityAssessment(
            status=eligibility,
            reason=f"constructed downstream eligibility: {eligibility}",
            evidence_path="apparatus-contract / eligibility",
            receipt_sha256=_RECEIPT,
        ),
        ValidityAssessment(
            status=validity,
            reason=f"constructed downstream semantic validity: {validity}",
            evidence_path="apparatus-contract / semantic-validity",
            receipt_sha256=_RECEIPT,
            operator=operator,
        ),
    )


def _contribution(
    contribution_id: str,
    passage_id: str,
    *,
    channel: Literal["support", "refutation"],
    score: float,
    eligibility: Literal["eligible", "ineligible", "unknown"] = "eligible",
    validity: Literal["valid", "invalid", "unknown"] = "valid",
    operator: str = "contract_supplied_relation",
) -> EvidenceContribution:
    eligible, valid = _assessment(
        eligibility=eligibility,
        validity=validity,
        operator=operator,
    )
    return EvidenceContribution(
        contribution_id=contribution_id,
        channel=channel,
        passage_ids=(passage_id,),
        score=score,
        score_method="direct_nli_probability",
        score_receipt_sha256=_RECEIPT,
        origin="direct_nli",
        eligibility=eligible,
        validity=valid,
    )


def _stage_receipts() -> tuple[StageReceipt, ...]:
    return tuple(
        StageReceipt(
            stage=stage,
            evidence_path=f"apparatus-contract / {stage}",
            receipt_sha256="sha256:" + f"{index + 10:064x}",
        )
        for index, stage in enumerate(CANONICAL_STAGE_ORDER)
    )


def _apertures(
    *,
    support: Literal["complete", "incomplete", "unknown"] = "complete",
    refutation: Literal["complete", "incomplete", "unknown"] = "complete",
) -> tuple[ChannelApertureAssessment, ...]:
    return (
        ChannelApertureAssessment(
            channel="support",
            status=support,
            reason=f"constructed downstream support aperture: {support}",
            evidence_path="apparatus-contract / support-aperture",
            receipt_sha256=_RECEIPT,
        ),
        ChannelApertureAssessment(
            channel="refutation",
            status=refutation,
            reason=f"constructed downstream refutation aperture: {refutation}",
            evidence_path="apparatus-contract / refutation-aperture",
            receipt_sha256=_RECEIPT,
        ),
    )


def _evaluate(
    *contributions: EvidenceContribution,
    apertures: tuple[ChannelApertureAssessment, ...] | None = None,
) -> EvidenceDecisionTrace:
    passage_ids = tuple(sorted(item.passage_ids[0] for item in contributions))
    measurements: list[ChannelMeasurement] = []
    for contribution in contributions:
        support_score = contribution.score if contribution.channel == "support" else 0.01
        refutation_score = (
            contribution.score if contribution.channel == "refutation" else 0.01
        )
        measurements.append(
            ChannelMeasurement(
                passage_id=contribution.passage_ids[0],
                support_score=support_score,
                refutation_score=refutation_score,
                evidence_path="apparatus-contract / measurement",
                receipt_sha256=_RECEIPT,
            )
        )
    return evaluate_evidence(
        EvidenceDecisionInput(
            claim_id="contract-supplied-obligation",
            scope_status="in_scope",
            stage_receipts=_stage_receipts(),
            admitted_passage_ids=passage_ids,
            measurements=tuple(measurements),
            apertures=_apertures() if apertures is None else apertures,
            signal_floor=0.20,
            support_threshold=0.70,
            refutation_threshold=0.70,
            policy_id="annex22-downstream-preservation-v1",
            policy_receipt_sha256=_POLICY_RECEIPT,
            contributions=tuple(contributions),
        )
    )


def _ledger_ids(trace: EvidenceDecisionTrace) -> tuple[str, ...]:
    return tuple(item.contribution_id for item in trace.inputs.contributions)


def test_g01_filtering_changes_views_never_the_input_ledger() -> None:
    trace = _evaluate(
        _contribution("support-valid", "p1", channel="support", score=0.90),
        _contribution(
            "refute-ineligible",
            "p2",
            channel="refutation",
            score=0.99,
            eligibility="ineligible",
        ),
        _contribution(
            "refute-invalid",
            "p3",
            channel="refutation",
            score=0.98,
            validity="invalid",
        ),
        _contribution(
            "refute-unknown",
            "p4",
            channel="refutation",
            score=0.97,
            validity="unknown",
        ),
    )

    assert _ledger_ids(trace) == (
        "support-valid",
        "refute-ineligible",
        "refute-invalid",
        "refute-unknown",
    )
    assert set(trace.raw.contribution_ids) == set(_ledger_ids(trace))
    assert set(trace.eligible.contribution_ids) == {
        "support-valid",
        "refute-invalid",
        "refute-unknown",
    }
    assert trace.valid.contribution_ids == ("support-valid",)
    assert trace.decision.reason_code == "semantic_validity_unknown"


def test_g02_later_reclassification_produces_a_new_trace_without_erasure() -> None:
    unresolved = _contribution(
        "supplier-refute",
        "p2",
        channel="refutation",
        score=0.96,
        eligibility="unknown",
    )
    initial = _evaluate(
        _contribution("support-valid", "p1", channel="support", score=0.91),
        unresolved,
    )
    revised_eligibility = EligibilityAssessment(
        status="ineligible",
        reason="later supplier qualification showed this assertion is non-deciding",
        evidence_path="apparatus-contract / later-eligibility",
        receipt_sha256=_RECEIPT,
    )
    revised = unresolved.model_copy(update={"eligibility": revised_eligibility})
    reevaluated = _evaluate(
        _contribution("support-valid", "p1", channel="support", score=0.91),
        revised,
    )

    assert initial.inputs.contributions[1].eligibility.status == "unknown"
    assert reevaluated.inputs.contributions[1].eligibility.status == "ineligible"
    assert "supplier-refute" in initial.raw.contribution_ids
    assert "supplier-refute" in reevaluated.raw.contribution_ids
    assert initial.decision.reason_code == "eligibility_unknown"
    assert reevaluated.decision.verdict == "supported"


def test_a22_01_workshop_interest_does_not_override_current_draft_scope() -> None:
    trace = _evaluate(
        _contribution(
            "workshop-risk-based-pathway",
            "ema-workshop",
            channel="support",
            score=0.93,
            validity="invalid",
            operator="authority_and_status_scope",
        ),
        _contribution(
            "draft-critical-use-restriction",
            "annex22-draft",
            channel="refutation",
            score=0.91,
            operator="authority_and_status_scope",
        ),
    )

    assert set(_ledger_ids(trace)) == {
        "workshop-risk-based-pathway",
        "draft-critical-use-restriction",
    }
    assert trace.valid.refutation_contribution_ids == (
        "draft-critical-use-restriction",
    )
    assert trace.decision.verdict == "contradicted"


def test_a22_02_guardrail_success_and_failure_remain_mixed() -> None:
    trace = _evaluate(
        _contribution(
            "guardrail-validation",
            "validation-report",
            channel="support",
            score=0.94,
            operator="guardrail_reliability",
        ),
        _contribution(
            "guardrail-incident",
            "incident-report",
            channel="refutation",
            score=0.97,
            operator="guardrail_reliability",
        ),
    )

    assert trace.valid.state == "mixed"
    assert trace.decision.reason_code == "mixed_valid_evidence"
    assert set(trace.decision.basis_contribution_ids) == set(_ledger_ids(trace))


def test_a22_03_guardrail_evidence_does_not_prove_human_oversight() -> None:
    trace = _evaluate(
        _contribution(
            "guardrail-validation",
            "validation-report",
            channel="support",
            score=0.98,
            validity="invalid",
            operator="human_oversight_scope",
        )
    )

    assert trace.raw.contribution_ids == ("guardrail-validation",)
    assert trace.valid.contribution_ids == ()
    assert trace.decision.reason_code == "no_valid_contribution"


def test_a22_04_pre_update_validation_does_not_launder_post_update_failure() -> None:
    trace = _evaluate(
        _contribution(
            "pre-update-validation",
            "validation-v1",
            channel="support",
            score=0.96,
            validity="invalid",
            operator="lifecycle_temporal_scope",
        ),
        _contribution(
            "post-update-failure",
            "stress-test-v2",
            channel="refutation",
            score=0.89,
            operator="lifecycle_temporal_scope",
        ),
    )

    assert set(_ledger_ids(trace)) == {
        "pre-update-validation",
        "post-update-failure",
    }
    assert trace.valid.refutation_contribution_ids == ("post-update-failure",)
    assert trace.decision.verdict == "contradicted"


def test_a22_05_unknown_strategic_aperture_blocks_strong_local_support() -> None:
    trace = _evaluate(
        _contribution(
            "critical-use-validation",
            "critical-use-study",
            channel="support",
            score=0.99,
            operator="critical_use_evidence",
        ),
        apertures=_apertures(refutation="unknown"),
    )

    assert trace.inputs.contributions[0].contribution_id == "critical-use-validation"
    assert trace.valid.state == "support_only"
    assert trace.decision.reason_code == "aperture_unknown"


def test_a22_06_unresolved_supplier_control_stays_visible_and_blocks_resolution() -> None:
    trace = _evaluate(
        _contribution(
            "supplier-attestation",
            "cloud-provider-record",
            channel="support",
            score=0.95,
            eligibility="unknown",
            operator="supplier_control",
        )
    )

    assert trace.raw.contribution_ids == ("supplier-attestation",)
    assert trace.inputs.contributions[0].eligibility.status == "unknown"
    assert trace.decision.reason_code == "eligibility_unknown"


def test_fda_01_ai_generated_synthesis_is_not_quality_unit_review_evidence() -> None:
    trace = _evaluate(
        _contribution(
            "ai-generated-procedure",
            "generated-document",
            channel="support",
            score=0.99,
            validity="invalid",
            operator="human_authority_scope",
        ),
        _contribution(
            "inspection-review-gap",
            "inspection-record",
            channel="refutation",
            score=0.92,
            operator="human_authority_scope",
        ),
    )

    assert set(_ledger_ids(trace)) == {
        "ai-generated-procedure",
        "inspection-review-gap",
    }
    assert trace.valid.refutation_contribution_ids == ("inspection-review-gap",)
    assert trace.decision.verdict == "contradicted"
