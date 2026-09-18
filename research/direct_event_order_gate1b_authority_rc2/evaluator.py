"""Frozen evaluator for direct-event-order Gate-1B authority RC2."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from claim_audit_lab.production_v1.semantic.measurements import (
    MeasurementReceipt,
    measure_direct_event_order,
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
    Case(
        "E2W01",
        "Talia reviewed packet u before Ravi signed ledger c.",
        True,
    ),
    Case(
        "E2W02",
        "Talia reviewed packet u after Ravi signed ledger c.",
        True,
    ),
    Case(
        "E2W03",
        "Talia did not review packet u before Ravi signed ledger c.",
        True,
    ),
    Case(
        "E2W04",
        "Talia reviewed packet u after Ravi did not sign ledger c.",
        True,
    ),
)

REFUSE: tuple[Case, ...] = (
    Case(
        "E2R01",
        "Perhaps Talia reviewed packet u before Ravi signed ledger c.",
        False,
    ),
    Case(
        "E2R02",
        "If Talia reviewed packet u before Ravi signed ledger c.",
        False,
    ),
    Case(
        "E2R03",
        "Talia reviewed packet u not before Ravi signed ledger c.",
        False,
    ),
    Case(
        "E2R04",
        "Talia reviewed packet u immediately before Ravi signed ledger c.",
        False,
    ),
    Case(
        "E2R05",
        "Talia reviewed packet u shortly before Ravi signed ledger c.",
        False,
    ),
    Case(
        "E2R06",
        "Talia reviewed packet u before Ravi signed ledger c because QA requested it.",
        False,
    ),
    Case(
        "E2R07",
        "Allegedly Talia reviewed packet u before Ravi signed ledger c.",
        False,
    ),
    Case(
        "E2R08",
        "Reportedly Talia reviewed packet u before Ravi signed ledger c.",
        False,
    ),
    Case(
        "E2R09",
        "Talia reviewed packet u before Ravi signed ledger c according to QA.",
        False,
    ),
    Case(
        "E2R10",
        "Talia reviewed packet u before Ravi signed ledger c reportedly.",
        False,
    ),
    Case(
        "E2R11",
        "QA approved the batch before Ops released it.",
        False,
    ),
)

CASES = CLEAN + REFUSE
AuthorityCandidate = Callable[[AuditContext, MeasurementReceipt, str], object]


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _context(case: Case) -> AuditContext:
    passage = AdmittedPassage.create("p1", "source-1", case.text)
    world = EvidenceWorld.create(
        "1.2.0",
        f"event-rc2-{case.case_id.lower()}",
        f"sha256:{_hex('bundle:' + case.case_id)}",
        (passage,),
        {
            "search_scope": {"corpus": "event-order-authority-rc2"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        f"claim-{case.case_id.lower()}",
        SemanticFamily.DIRECT_EVENT_ORDER,
        {},
        text_sha256=_hex(case.text),
    )
    return AuditContext(case.text, proposition, world)


def observe(case: Case, candidate: AuthorityCandidate) -> tuple[str, str]:
    context = _context(case)
    receipt = measure_direct_event_order(context, "p1")
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
