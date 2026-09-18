"""Evaluate the frozen modifier gate against the fresh post-freeze cohort."""

from __future__ import annotations

import json

from claim_audit_lab.cal_v1_candidate.models import (
    AdmittedPassage,
    AuditContext,
    Conclusion,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
    sha256_hex,
    tagged_sha256,
)

from .candidate import deciding_conclusion, eligibility
from .fresh_cohort import FRESH_CASES, FreshCase

TARGET_TEXT = "Sector A is higher than Sector B."


def context_for(case: FreshCase) -> AuditContext:
    proposition = TypedProposition.create(
        proposition_id=f"strict-gate-{case.case_id}",
        semantic_family=SemanticFamily.STRICT_COMPARISON,
        fields={
            "lhs_entity": "Sector A",
            "rhs_entity": "Sector B",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=sha256_hex(TARGET_TEXT.encode()),
    )
    passage = AdmittedPassage.create("P1", "S1", case.text)
    world = EvidenceWorld.create(
        contract_b_version="1.2.0",
        bundle_id=f"bundle-{case.case_id.lower()}",
        bundle_hash=tagged_sha256(case.text.encode()),
        admitted_passages=(passage,),
        aperture_observation={"status": "fresh_pressure"},
    )
    return AuditContext(TARGET_TEXT, proposition, world)


def observations() -> list[dict[str, str | bool]]:
    rows: list[dict[str, str | bool]] = []
    for case in FRESH_CASES:
        gate = eligibility(case.text)
        observed = deciding_conclusion(context_for(case))
        rows.append(
            {
                "case_id": case.case_id,
                "text": case.text,
                "eligible": gate.eligible,
                "eligibility_reason": gate.reason,
                "expected": case.expected.value,
                "observed": observed.value,
                "match": observed is case.expected,
            }
        )
    return rows


def unsafe_cases() -> tuple[str, ...]:
    unsafe: list[str] = []
    for case in FRESH_CASES:
        observed = deciding_conclusion(context_for(case))
        if case.expected is Conclusion.NOT_CHECKABLE and observed in {
            Conclusion.SUPPORTED,
            Conclusion.CONTRADICTED,
        }:
            unsafe.append(case.case_id)
    return tuple(unsafe)


def positive_failures() -> tuple[str, ...]:
    failures: list[str] = []
    for case in FRESH_CASES:
        if case.expected is Conclusion.NOT_CHECKABLE:
            continue
        if deciding_conclusion(context_for(case)) is not case.expected:
            failures.append(case.case_id)
    return tuple(failures)


def main() -> None:
    print(
        json.dumps(
            {
                "unsafe_cases": unsafe_cases(),
                "positive_failures": positive_failures(),
                "observations": observations(),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
