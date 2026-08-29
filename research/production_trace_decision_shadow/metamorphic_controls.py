"""Label-free metamorphic controls for the explicit CAL decision machinery."""

from __future__ import annotations

import hashlib
from typing import Any

from claim_audit_lab.v1.decision_model import (
    CANONICAL_STAGE_ORDER,
    ChannelApertureAssessment,
    ChannelMeasurement,
    EligibilityAssessment,
    EvidenceContribution,
    EvidenceDecisionInput,
    StageReceipt,
    ValidityAssessment,
    evaluate_evidence,
)


def _sha(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _eligibility(status: str, label: str) -> EligibilityAssessment:
    return EligibilityAssessment(
        status=status,
        reason=f"metamorphic control eligibility: {status}",
        evidence_path=f"control:{label}:eligibility",
        receipt_sha256=_sha(f"{label}:eligibility:{status}"),
    )


def _validity(status: str, label: str, operator: str = "control_direct") -> ValidityAssessment:
    return ValidityAssessment(
        status=status,
        reason=f"metamorphic control validity: {status}",
        evidence_path=f"control:{label}:validity",
        receipt_sha256=_sha(f"{label}:validity:{status}:{operator}"),
        operator=operator,
    )


def _stages(label: str) -> tuple[StageReceipt, ...]:
    return tuple(
        StageReceipt(
            stage=stage,
            evidence_path=f"control:{label}:{stage}",
            receipt_sha256=_sha(f"{label}:{stage}"),
        )
        for stage in CANONICAL_STAGE_ORDER
    )


def _apertures(
    label: str,
    *,
    support: str = "complete",
    refutation: str = "complete",
) -> tuple[ChannelApertureAssessment, ...]:
    return (
        ChannelApertureAssessment(
            channel="support",
            status=support,
            reason=f"metamorphic support aperture: {support}",
            evidence_path=f"control:{label}:support-aperture",
            receipt_sha256=_sha(f"{label}:support-aperture:{support}"),
        ),
        ChannelApertureAssessment(
            channel="refutation",
            status=refutation,
            reason=f"metamorphic refutation aperture: {refutation}",
            evidence_path=f"control:{label}:refutation-aperture",
            receipt_sha256=_sha(f"{label}:refutation-aperture:{refutation}"),
        ),
    )


def _measurement(
    passage_id: str,
    support: float,
    refutation: float,
    label: str,
) -> ChannelMeasurement:
    return ChannelMeasurement(
        passage_id=passage_id,
        support_score=support,
        refutation_score=refutation,
        evidence_path=f"control:{label}:measurement:{passage_id}",
        receipt_sha256=_sha(f"{label}:measurement:{passage_id}:{support}:{refutation}"),
    )


def _direct(
    *,
    passage_id: str,
    channel: str,
    score: float,
    measurement: ChannelMeasurement,
    label: str,
    eligibility: str = "eligible",
    validity: str = "valid",
) -> EvidenceContribution:
    return EvidenceContribution(
        contribution_id=f"{label}:direct:{channel}:{passage_id}",
        channel=channel,
        passage_ids=(passage_id,),
        score=score,
        score_method="direct_nli_probability",
        score_receipt_sha256=measurement.receipt_sha256,
        origin="direct_nli",
        eligibility=_eligibility(eligibility, f"{label}:{passage_id}:{channel}"),
        validity=_validity(validity, f"{label}:{passage_id}:{channel}"),
    )


def _input(
    *,
    label: str,
    admitted: tuple[str, ...],
    measurements: tuple[ChannelMeasurement, ...],
    contributions: tuple[EvidenceContribution, ...],
    apertures: tuple[ChannelApertureAssessment, ...] | None = None,
    stage_receipts: tuple[StageReceipt, ...] | None = None,
) -> EvidenceDecisionInput:
    return EvidenceDecisionInput(
        claim_id=f"control-{label}",
        scope_status="in_scope",
        stage_receipts=stage_receipts if stage_receipts is not None else _stages(label),
        admitted_passage_ids=admitted,
        measurements=measurements,
        apertures=apertures if apertures is not None else _apertures(label),
        signal_floor=0.20,
        support_threshold=0.70,
        refutation_threshold=0.70,
        policy_id="cal-shadow-metamorphic-v0.1",
        policy_receipt_sha256=_sha("cal-shadow-metamorphic-v0.1"),
        contributions=contributions,
    )


def run_controls() -> dict[str, Any]:
    results: list[dict[str, Any]] = []

    # 1. Irrelevant-evidence addition.
    m1 = _measurement("p-support", 0.90, 0.05, "irrelevant-base")
    c1 = _direct(
        passage_id="p-support",
        channel="support",
        score=0.90,
        measurement=m1,
        label="irrelevant-base",
    )
    base = evaluate_evidence(
        _input(
            label="irrelevant-base",
            admitted=("p-support",),
            measurements=(m1,),
            contributions=(c1,),
        )
    )
    m2 = _measurement("p-irrelevant", 0.10, 0.10, "irrelevant-added")
    added = evaluate_evidence(
        _input(
            label="irrelevant-added",
            admitted=("p-support", "p-irrelevant"),
            measurements=(m1, m2),
            contributions=(c1,),
        )
    )
    results.append(
        {
            "name": "irrelevant_evidence_addition",
            "pass": (
                base.decision.verdict == "supported"
                and added.decision.verdict == "supported"
                and base.decision.basis_contribution_ids
                == added.decision.basis_contribution_ids
                and "p-irrelevant" not in " ".join(added.decision.basis_contribution_ids)
            ),
            "base": base.decision.model_dump(),
            "mutated": added.decision.model_dump(),
        }
    )

    # 2. Ineligible support remains raw but cannot participate downstream.
    m3 = _measurement("p-support", 0.90, 0.05, "ineligible")
    c3 = _direct(
        passage_id="p-support",
        channel="support",
        score=0.90,
        measurement=m3,
        label="ineligible",
        eligibility="ineligible",
    )
    ineligible = evaluate_evidence(
        _input(
            label="ineligible",
            admitted=("p-support",),
            measurements=(m3,),
            contributions=(c3,),
        )
    )
    results.append(
        {
            "name": "ineligible_support_mutation",
            "pass": (
                ineligible.raw.state == "support_only"
                and ineligible.eligible.state == "read_silent"
                and ineligible.valid.state == "read_silent"
                and ineligible.decision.disposition == "abstained"
                and ineligible.decision.reason_code == "no_eligible_contribution"
            ),
            "trace": ineligible.model_dump(),
        }
    )

    # 3. Unknown validity remains unknown and does not become refutation.
    m4 = _measurement("p-support", 0.90, 0.05, "unknown-validity")
    c4 = _direct(
        passage_id="p-support",
        channel="support",
        score=0.90,
        measurement=m4,
        label="unknown-validity",
        validity="unknown",
    )
    unknown = evaluate_evidence(
        _input(
            label="unknown-validity",
            admitted=("p-support",),
            measurements=(m4,),
            contributions=(c4,),
        )
    )
    results.append(
        {
            "name": "unknown_validity_mutation",
            "pass": (
                unknown.raw.state == "support_only"
                and unknown.eligible.state == "support_only"
                and unknown.valid.state == "read_silent"
                and not unknown.valid.refutation_contribution_ids
                and unknown.decision.reason_code == "semantic_validity_unknown"
            ),
            "trace": unknown.model_dump(),
        }
    )

    # 4. Adding valid refutation preserves support and exposes a mixed state.
    ms = _measurement("p-support", 0.90, 0.05, "mixed")
    mr = _measurement("p-refute", 0.05, 0.92, "mixed")
    cs = _direct(
        passage_id="p-support",
        channel="support",
        score=0.90,
        measurement=ms,
        label="mixed",
    )
    cr = _direct(
        passage_id="p-refute",
        channel="refutation",
        score=0.92,
        measurement=mr,
        label="mixed",
    )
    mixed = evaluate_evidence(
        _input(
            label="mixed",
            admitted=("p-support", "p-refute"),
            measurements=(ms, mr),
            contributions=(cs, cr),
        )
    )
    results.append(
        {
            "name": "refutation_channel_mutation",
            "pass": (
                mixed.valid.state == "mixed"
                and cs.contribution_id in mixed.valid.support_contribution_ids
                and cr.contribution_id in mixed.valid.refutation_contribution_ids
                and mixed.decision.reason_code == "mixed_valid_evidence"
            ),
            "trace": mixed.model_dump(),
        }
    )

    # 5. A passage-set contribution decides only while the set is complete.
    mp1 = _measurement("p-set-1", 0.10, 0.10, "set-base")
    mp2 = _measurement("p-set-2", 0.10, 0.10, "set-base")
    set_contribution = EvidenceContribution(
        contribution_id="set-base:semantic:support:p-set-1+p-set-2",
        channel="support",
        passage_ids=("p-set-1", "p-set-2"),
        score=0.90,
        score_method="receipt_bound_passage_set_control",
        score_receipt_sha256=_sha("set-base:score"),
        origin="semantic_operator",
        eligibility=_eligibility("eligible", "set-base"),
        validity=_validity("valid", "set-base", "compound_supporting_set"),
    )
    complete_set = evaluate_evidence(
        _input(
            label="set-base",
            admitted=("p-set-1", "p-set-2"),
            measurements=(mp1, mp2),
            contributions=(set_contribution,),
        )
    )
    incomplete_set = evaluate_evidence(
        _input(
            label="set-incomplete",
            admitted=("p-set-1",),
            measurements=(mp1,),
            contributions=(),
            apertures=_apertures("set-incomplete", support="incomplete"),
        )
    )
    results.append(
        {
            "name": "passage_set_mutation",
            "pass": (
                complete_set.decision.verdict == "supported"
                and set_contribution.contribution_id
                in complete_set.decision.basis_contribution_ids
                and incomplete_set.decision.disposition == "abstained"
                and incomplete_set.decision.reason_code == "aperture_incomplete"
                and incomplete_set.valid.state == "read_silent"
            ),
            "base": complete_set.model_dump(),
            "mutated": incomplete_set.model_dump(),
        }
    )

    # 6. Missing a required receipt must fail as execution/contract failure,
    # never turn into an epistemic abstention.
    execution_failure_type: str | None = None
    try:
        mf = _measurement("p-support", 0.90, 0.05, "missing-receipt")
        cf = _direct(
            passage_id="p-support",
            channel="support",
            score=0.90,
            measurement=mf,
            label="missing-receipt",
        )
        _input(
            label="missing-receipt",
            admitted=("p-support",),
            measurements=(mf,),
            contributions=(cf,),
            stage_receipts=_stages("missing-receipt")[:-1],
        )
    except ValueError as exc:
        execution_failure_type = type(exc).__name__
    results.append(
        {
            "name": "execution_failure_mutation",
            "pass": execution_failure_type == "ValidationError",
            "observed_exception": execution_failure_type,
            "expected": "ValidationError before EvidenceDecisionTrace exists",
        }
    )

    return {
        "schema_version": "cal-production-trace-shadow-metamorphic-v0.1",
        "n_controls": len(results),
        "n_passed": sum(bool(item["pass"]) for item in results),
        "all_passed": all(bool(item["pass"]) for item in results),
        "results": results,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_controls(), indent=2, sort_keys=True))
