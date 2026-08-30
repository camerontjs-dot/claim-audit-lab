"""Research-only semantic authority jurisdiction primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Domain = Literal[
    "structural_negation",
    "numeric_relation",
    "source_boundary",
    "scope",
    "composition",
]

Status = Literal["valid", "invalid", "unknown", "inapplicable"]


@dataclass(frozen=True)
class AuthorityReceipt:
    receipt_id: str
    domain: Domain
    operation: str
    target_id: str
    current: bool
    applicable: bool
    status: Status
    reason: str

    def may_decide(self, *, required_domain: Domain, operation: str, target_id: str) -> bool:
        return (
            self.current
            and self.applicable
            and self.domain == required_domain
            and self.operation == operation
            and self.target_id == target_id
            and self.status in {"valid", "invalid"}
        )


@dataclass(frozen=True)
class Quantity:
    property_id: str
    scope_id: str
    value: float
    unit: str
    relation: Literal["eq", "max", "min", "gt", "lt"]


def comparable(a: Quantity, b: Quantity) -> tuple[bool, str]:
    if a.property_id != b.property_id:
        return False, "property_mismatch"
    if a.scope_id != b.scope_id:
        return False, "scope_mismatch"
    if a.unit != b.unit:
        return False, "unit_mismatch"
    return True, "comparable"


def assess_numeric_relation(
    *,
    claim: Quantity,
    evidence: Quantity,
    target_id: str,
    receipt_id: str,
) -> AuthorityReceipt:
    ok, reason = comparable(claim, evidence)
    if not ok:
        return AuthorityReceipt(
            receipt_id, "numeric_relation", "semantic.validate_numeric", target_id,
            True, False, "inapplicable", reason
        )

    # Exact point equality.
    if claim.relation == "eq" and evidence.relation == "eq":
        status = "valid" if claim.value == evidence.value else "invalid"
        return AuthorityReceipt(
            receipt_id, "numeric_relation", "semantic.validate_numeric", target_id,
            True, True, status, "point_equality"
        )

    # Claim says the allowed maximum is X; evidence establishes a stricter/different maximum Y.
    if claim.relation == "max" and evidence.relation == "max":
        status = "valid" if claim.value == evidence.value else "invalid"
        return AuthorityReceipt(
            receipt_id, "numeric_relation", "semantic.validate_numeric", target_id,
            True, True, status, "maximum_bound_comparison"
        )

    # Condition checking: evidence threshold is a minimum/greater-than rule and claim observation is point.
    if claim.relation == "eq" and evidence.relation in {"min", "gt"}:
        satisfied = claim.value > evidence.value if evidence.relation == "gt" else claim.value >= evidence.value
        return AuthorityReceipt(
            receipt_id, "numeric_relation", "semantic.evaluate_condition", target_id,
            True, True, "valid" if satisfied else "invalid", "threshold_condition"
        )

    return AuthorityReceipt(
        receipt_id, "numeric_relation", "semantic.validate_numeric", target_id,
        True, True, "unknown", "relation_geometry_unmodeled"
    )


def assess_absence_boundary(
    *,
    boundary: str,
    topic: str,
    named_gaps: tuple[str, ...],
    claimed_material_is_named_gap: bool,
    target_id: str,
    receipt_id: str,
) -> AuthorityReceipt:
    if boundary == "bounded":
        return AuthorityReceipt(
            receipt_id, "source_boundary", "semantic.validate_absence", target_id,
            True, True, "unknown", "bounded_aperture_cannot_establish_absence"
        )
    if boundary == "exhaustive":
        return AuthorityReceipt(
            receipt_id, "source_boundary", "semantic.validate_absence", target_id,
            True, True, "valid", "exhaustive_aperture_supports_absence_assessment"
        )
    if boundary == "named_missing_material":
        if claimed_material_is_named_gap and topic in named_gaps:
            return AuthorityReceipt(
                receipt_id, "source_boundary", "semantic.validate_absence", target_id,
                True, True, "invalid", "claimed_absence_conflicts_with_named_missing_material"
            )
        return AuthorityReceipt(
            receipt_id, "source_boundary", "semantic.validate_absence", target_id,
            True, True, "unknown", "named_gap_receipt_does_not_cover_claimed_topic"
        )
    return AuthorityReceipt(
        receipt_id, "source_boundary", "semantic.validate_absence", target_id,
        True, False, "inapplicable", "unknown_boundary_kind"
    )
