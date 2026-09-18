"""Frozen evaluator for strict-comparison Gate-1B authority RC2."""

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


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    text: str
    should_warrant: bool


CLEAN: tuple[Case, ...] = (
    Case("S2W01", "Women had a higher rate than Men.", True),
    Case("S2W02", "Sector A exceeded Sector B by 4 units.", True),
    Case("S2W03", "Sector A had a lower score than Sector B.", True),
    Case("S2W04", "Sector A processed 20 units, 3 more than Sector B.", True),
    Case("S2W05", "Sector A was higher than Sector B.", True),
    Case("S2W06", "Sector A recorded a higher output than Sector B.", True),
)

REFUSE: tuple[Case, ...] = (
    Case("S2R01", "Sector A was not higher than Sector B.", False),
    Case("S2R02", "Sector A was no higher than Sector B.", False),
    Case("S2R03", "Sector A was probably higher than Sector B.", False),
    Case("S2R04", "Sector A was allegedly higher than Sector B.", False),
    Case("S2R05", "Sector A may be higher than Sector B.", False),
    Case("S2R06", "Sector A could be higher than Sector B.", False),
    Case("S2R07", "The report says Sector A is higher than Sector B.", False),
    Case("S2R08", "Sector A was never higher than Sector B.", False),
    Case("S2R09", "Sector A appears higher than Sector B.", False),
    Case("S2R10", "Sector A is supposedly higher than Sector B.", False),
    Case("S2R11", "According to QA, Sector A is higher than Sector B.", False),
)

CASES = CLEAN + REFUSE
AuthorityCandidate = Callable[[AuditContext, MeasurementReceipt, str], object]


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _context(case: Case) -> AuditContext:
    passage = AdmittedPassage.create("p1", "source-1", case.text)
    world = EvidenceWorld.create(
        "1.2.0",
        f"strict-rc2-{case.case_id.lower()}",
        f"sha256:{_hex('bundle:' + case.case_id)}",
        (passage,),
        {
            "search_scope": {"corpus": "strict-authority-rc2"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        f"claim-{case.case_id.lower()}",
        SemanticFamily.STRICT_COMPARISON,
        {},
        text_sha256=_hex(case.text),
    )
    return AuditContext(case.text, proposition, world)


def observe(case: Case, candidate: AuthorityCandidate) -> tuple[str, str]:
    context = _context(case)
    receipt = measure_strict_comparison(context, "p1")
    measurement = str(receipt.raw_measurement().get("status"))
    try:
        candidate(context, receipt, "p1")
    except Exception:
        authority = "REFUSED"
    else:
        authority = "WARRANTED"
    return measurement, authority


def failures(candidate: AuthorityCandidate) -> tuple[str, ...]:
    result: list[str] = []
    for case in CASES:
        measurement, authority = observe(case, candidate)
        if measurement != "CLAIMED":
            result.append(f"{case.case_id}:measurement-{measurement}")
            continue
        expected = "WARRANTED" if case.should_warrant else "REFUSED"
        if authority != expected:
            result.append(f"{case.case_id}:{authority}-expected-{expected}")
    return tuple(result)


def weak_trust_measurement(
    context: AuditContext,
    receipt: MeasurementReceipt,
    passage_id: str,
) -> object:
    del context, passage_id
    if receipt.raw_measurement().get("status") != "CLAIMED":
        raise ValueError("not claimed")
    return object()
