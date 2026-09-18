"""Pressure RC1 strict-comparison authority with PR #139 counterexamples."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from claim_audit_lab.cal_v1_candidate.engine import AuditResult, audit
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


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    text: str
    expected: Conclusion


TARGET_TEXT = "Sector A is higher than Sector B."
TARGET_FIELDS = {
    "lhs_entity": "Sector A",
    "rhs_entity": "Sector B",
    "comparison_direction": "MORE_THAN",
}

CASES: tuple[Case, ...] = (
    Case("SC-RC1-POS", "Sector A was higher than Sector B.", Conclusion.SUPPORTED),
    Case("SC-RC1-01", "Sector A was not higher than Sector B.", Conclusion.NOT_CHECKABLE),
    Case("SC-RC1-02", "Sector A was no higher than Sector B.", Conclusion.NOT_CHECKABLE),
    Case("SC-RC1-03", "Sector A was probably higher than Sector B.", Conclusion.NOT_CHECKABLE),
    Case("SC-RC1-04", "Sector A was allegedly higher than Sector B.", Conclusion.NOT_CHECKABLE),
    Case("SC-RC1-05", "Sector A may be higher than Sector B.", Conclusion.NOT_CHECKABLE),
    Case("SC-RC1-06", "Sector A could be higher than Sector B.", Conclusion.NOT_CHECKABLE),
    Case(
        "SC-RC1-07",
        "If Sector A is higher than Sector B, notify QA.",
        Conclusion.NOT_CHECKABLE,
    ),
    Case(
        "SC-RC1-08",
        "The report says Sector A is higher than Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    Case("SC-RC1-09", "Sector A is not equal to Sector B.", Conclusion.NOT_CHECKABLE),
    Case("SC-RC1-10", "Sector A is not the same as Sector B.", Conclusion.NOT_CHECKABLE),
    Case(
        "SC-RC1-11",
        "Sector A produced not twice as many units as Sector B.",
        Conclusion.NOT_CHECKABLE,
    ),
    Case(
        "SC-RC1-12",
        "Sector A is higher than Sector B and Sector C.",
        Conclusion.NOT_CHECKABLE,
    ),
    Case(
        "SC-RC1-13",
        "Sector A is higher than Sector B or Sector C.",
        Conclusion.NOT_CHECKABLE,
    ),
)


def context_for(case: Case) -> AuditContext:
    proposition = TypedProposition.create(
        proposition_id="strict-pressure-target",
        semantic_family=SemanticFamily.STRICT_COMPARISON,
        fields=TARGET_FIELDS,
        text_sha256=sha256_hex(TARGET_TEXT.encode()),
    )
    passage = AdmittedPassage.create(
        passage_id="P1",
        source_id="S1",
        text=case.text,
    )
    world = EvidenceWorld.create(
        contract_b_version="1.2.0",
        bundle_id=f"bundle-{case.case_id.lower()}",
        bundle_hash=tagged_sha256(case.text.encode()),
        admitted_passages=(passage,),
        aperture_observation={"status": "bounded_test_world"},
    )
    return AuditContext(
        original_claim=TARGET_TEXT,
        proposition=proposition,
        evidence_world=world,
    )


def execute(case: Case) -> AuditResult:
    return audit(context_for(case))


def row(case: Case) -> dict:
    result = execute(case)
    trace = result.traces[0]
    raw = trace.measurement.raw_measurement() if trace.measurement is not None else None
    relation = (
        trace.relation.categorical_relation.value if trace.relation is not None else None
    )
    return {
        "case": asdict(case),
        "conclusion": result.conclusion.value,
        "failure_code": result.failure_code.value if result.failure_code else None,
        "measurement": raw,
        "authority_status": trace.authority.status if trace.authority else None,
        "relation": relation,
        "trace_failure": trace.failure_code.value if trace.failure_code else None,
        "detail": trace.detail,
    }


def unsafe_cases() -> tuple[str, ...]:
    unsafe: list[str] = []
    for case in CASES:
        result = execute(case)
        if case.expected is Conclusion.NOT_CHECKABLE and result.conclusion in {
            Conclusion.SUPPORTED,
            Conclusion.CONTRADICTED,
        }:
            unsafe.append(case.case_id)
    return tuple(unsafe)
