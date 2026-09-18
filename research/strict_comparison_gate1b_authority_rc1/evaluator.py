"""Frozen evaluator for strict-comparison Gate-1B authority RC1."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from claim_audit_lab.production_v1.semantic.measurements import (
    MeasurementReceipt,
    measure_strict_comparison,
)
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)

from .cohort import CASES, Case, Expected


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def context_for(case: Case) -> AuditContext:
    passage = AdmittedPassage.create("p1", "source-1", case.text)
    world = EvidenceWorld.create(
        "1.2.0",
        f"bundle-{case.case_id.lower()}",
        _tagged(f"bundle-{case.case_id.lower()}"),
        (passage,),
        {
            "search_scope": {"corpus": "strict-gate1b-authority-rc1"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        f"claim-{case.case_id.lower()}",
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Sector A",
            "rhs_entity": "Sector B",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=_hex(case.text),
    )
    return AuditContext(case.text, proposition, world)


AuthorityCandidate = Callable[[AuditContext, MeasurementReceipt, str], object]


@dataclass(frozen=True, slots=True)
class Observation:
    case_id: str
    expected: Expected
    measurement_status: str
    authority_status: str


def observe(case: Case, candidate: AuthorityCandidate) -> Observation:
    context = context_for(case)
    receipt = measure_strict_comparison(context, "p1")
    status = str(receipt.raw_measurement().get("status"))
    try:
        candidate(context, receipt, "p1")
    except Exception:
        authority_status = "REFUSED"
    else:
        authority_status = "WARRANTED"
    return Observation(case.case_id, case.expected, status, authority_status)


def failures(candidate: AuthorityCandidate) -> tuple[str, ...]:
    result: list[str] = []
    for case in CASES:
        observation = observe(case, candidate)
        if observation.measurement_status != "CLAIMED":
            result.append(f"{case.case_id}:measurement-{observation.measurement_status}")
            continue
        expected_status = (
            "WARRANTED" if case.expected is Expected.WARRANT else "REFUSED"
        )
        if observation.authority_status != expected_status:
            result.append(
                f"{case.case_id}:{observation.authority_status}-expected-{expected_status}"
            )
    return tuple(result)


def weak_permissive_authority(
    context: AuditContext,
    receipt: MeasurementReceipt,
    passage_id: str,
) -> object:
    del context, passage_id
    if receipt.raw_measurement().get("status") != "CLAIMED":
        raise ValueError("not claimed")
    return object()
