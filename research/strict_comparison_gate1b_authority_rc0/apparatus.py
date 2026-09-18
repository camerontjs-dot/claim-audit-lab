"""Gate-1B discriminator for the frozen strict-comparison authority path."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from claim_audit_lab.production_v1.semantic.authority import (
    AuthorityReceipt,
    AuthorityRefusal,
    complete_and_warrant,
)
from claim_audit_lab.production_v1.semantic.measurements import measure_strict_comparison
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
    Case("SW01", "Women had a higher rate than Men.", True),
    Case("SW02", "Sector A exceeded Sector B by 4 units.", True),
    Case("SW03", "Sector A had a lower score than Sector B.", True),
)

LOSSY: tuple[Case, ...] = (
    Case("SR01", "Sector A was not higher than Sector B.", False),
    Case("SR02", "Sector A was no higher than Sector B.", False),
    Case("SR03", "Sector A was probably higher than Sector B.", False),
    Case("SR04", "Sector A was allegedly higher than Sector B.", False),
    Case("SR05", "Sector A may be higher than Sector B.", False),
    Case("SR06", "Sector A could be higher than Sector B.", False),
    Case("SR07", "The report says Sector A is higher than Sector B.", False),
    Case("SR08", "Sector A is not equal to Sector B.", False),
    Case("SR09", "Sector A is not the same as Sector B.", False),
    Case("SR10", "Sector A produced not twice as many units as Sector B.", False),
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
            "search_scope": {"corpus": "strict-gate1b-rc0"},
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


@dataclass(frozen=True, slots=True)
class Observation:
    case_id: str
    measurement_status: str
    authority_status: str
    refusal_code: str | None
    authority: AuthorityReceipt | None


def observe(case: Case) -> Observation:
    context = context_for(case)
    receipt = measure_strict_comparison(context, "p1")
    measurement_status = str(receipt.raw_measurement().get("status"))

    try:
        authority = complete_and_warrant(context, receipt, "p1")
    except AuthorityRefusal as exc:
        return Observation(
            case.case_id,
            measurement_status,
            "REFUSED",
            exc.code,
            None,
        )

    return Observation(
        case.case_id,
        measurement_status,
        authority.status,
        None,
        authority,
    )
