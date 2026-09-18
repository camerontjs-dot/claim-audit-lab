"""Gate-1B discriminator for the frozen direct-event-order authority path."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from claim_audit_lab.production_v1.semantic.authority import (
    AuthorityReceipt,
    AuthorityRefusal,
    complete_and_warrant,
)
from claim_audit_lab.production_v1.semantic.measurements import measure_direct_event_order
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    text: str
    should_warrant: bool


CLEAN: tuple[Case, ...] = (
    Case(
        "EW01",
        "Talia reviewed packet u before Ravi signed ledger c.",
        True,
    ),
    Case(
        "EW02",
        "Talia reviewed packet u after Ravi signed ledger c.",
        True,
    ),
    Case(
        "EW03",
        "Talia did not review packet u before Ravi signed ledger c.",
        True,
    ),
)

LOSSY: tuple[Case, ...] = (
    Case(
        "ER01",
        "The report says Talia reviewed packet u before Ravi signed ledger c.",
        False,
    ),
    Case(
        "ER02",
        "Perhaps Talia reviewed packet u before Ravi signed ledger c.",
        False,
    ),
    Case(
        "ER03",
        "If Talia reviewed packet u before Ravi signed ledger c.",
        False,
    ),
    Case(
        "ER04",
        "Talia reviewed packet u not before Ravi signed ledger c.",
        False,
    ),
    Case(
        "ER05",
        "Talia reviewed packet u immediately before Ravi signed ledger c.",
        False,
    ),
    Case(
        "ER06",
        "Talia reviewed packet u shortly before Ravi signed ledger c.",
        False,
    ),
    Case(
        "ER07",
        "Talia reviewed packet u before Ravi signed ledger c because QA requested it.",
        False,
    ),
    Case(
        "ER08",
        "Talia reviewed packet u before Ravi signed ledger c and Ivo released form j.",
        False,
    ),
    Case(
        "ER09",
        "Talia reviewed packet u before Ravi signed ledger c or Mona inspected batch w.",
        False,
    ),
)

CASES = CLEAN + LOSSY


def context_for(case: Case) -> AuditContext:
    passage = AdmittedPassage.create("p1", "source-1", case.text)
    world = EvidenceWorld.create(
        "1.2.0",
        f"bundle-{case.case_id.lower()}",
        _tagged(f"bundle-{case.case_id.lower()}"),
        (passage,),
        {
            "search_scope": {"corpus": "event-order-gate1b-rc0"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        f"claim-{case.case_id.lower()}",
        SemanticFamily.DIRECT_EVENT_ORDER,
        {
            "left_event": "talia:review:packet u",
            "relation": "BEFORE",
            "right_event": "ravi:sign:ledger c",
        },
        text_sha256=_hex(case.text),
    )
    return AuditContext(case.text, proposition, world)


@dataclass(frozen=True, slots=True)
class Observation:
    case_id: str
    measurement_status: str
    authority_status: str
    refusal_code: str | None
    authority: AuthorityReceipt | None


def observe(case: Case) -> Observation:
    context = context_for(case)
    receipt = measure_direct_event_order(context, "p1")
    measurement_status = str(receipt.raw_measurement().get("status"))
    try:
        authority = complete_and_warrant(context, receipt, "p1")
    except AuthorityRefusal as exc:
        return Observation(case.case_id, measurement_status, "REFUSED", exc.code, None)
    return Observation(case.case_id, measurement_status, authority.status, None, authority)
