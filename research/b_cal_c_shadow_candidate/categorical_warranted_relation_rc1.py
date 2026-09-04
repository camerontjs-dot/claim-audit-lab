"""Research-only categorical participation for already-warranted comparison atoms.

This module deliberately does not modify the production decision model. It tests
whether a proposition-relative relation can be derived from typed semantic
content after RC8J warrant, then composed without scalar strength or a caller-
supplied support/refutation channel.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


CategoricalRelation = Literal["SUPPORTS", "REFUTES", "IRRELEVANT", "UNRESOLVED"]
CategoricalVerdict = Literal["supported", "contradicted"]
CategoricalReason = Literal[
    "categorical_support",
    "categorical_refutation",
    "mixed_categorical_relations",
    "unresolved_categorical_relation",
    "no_deciding_categorical_relation",
]
ComparisonDirection = Literal["greater_than", "less_than", "at_least"]


class _StrictModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class ComparisonProposition(_StrictModel):
    """A strict research proposition target with no polarity/score side channel."""

    claim_id: str = Field(min_length=1)
    family: Literal["comparison"]
    lhs_entity: str = Field(min_length=1)
    rhs_entity: str = Field(min_length=1)
    comparison_direction: ComparisonDirection

    @model_validator(mode="after")
    def _distinct_entities(self) -> "ComparisonProposition":
        if self.lhs_entity == self.rhs_entity:
            raise ValueError("comparison proposition requires distinct entities")
        return self


class WarrantedRelationReceipt(_StrictModel):
    """Categorical relation derived only after external authority is WARRANTED."""

    relation_id: str = Field(min_length=1)
    claim_id: str = Field(min_length=1)
    atom_id: str = Field(min_length=1)
    authority_status: Literal["WARRANTED"]
    authority_reason: str = Field(min_length=1)
    relation: CategoricalRelation
    relation_reason: str = Field(min_length=1)
    proposition: ComparisonProposition
    atom_family: str = Field(min_length=1)
    atom_lhs_entity: str = Field(min_length=1)
    atom_rhs_entity: str = Field(min_length=1)
    atom_comparison_direction: str = Field(min_length=1)


class CategoricalConclusion(_StrictModel):
    """Scoreless proposition result over relation receipts."""

    claim_id: str = Field(min_length=1)
    disposition: Literal["decided", "abstained"]
    verdict: CategoricalVerdict | None
    reason_code: CategoricalReason
    basis_relation_ids: tuple[str, ...]

    @model_validator(mode="after")
    def _pairing(self) -> "CategoricalConclusion":
        if self.disposition == "decided" and self.verdict is None:
            raise ValueError("decided categorical conclusion requires a verdict")
        if self.disposition == "abstained" and self.verdict is not None:
            raise ValueError("categorical abstention may not carry a verdict")
        return self


def _require_warranted(authority_result: dict[str, Any]) -> tuple[str, str]:
    authority = authority_result.get("authority")
    if not isinstance(authority, dict):
        raise ValueError("authority result must contain an authority object")
    status = authority.get("status")
    reason = authority.get("reason")
    if status != "WARRANTED":
        raise ValueError(f"categorical relation requires WARRANTED authority, got {status}/{reason}")
    if not isinstance(reason, str) or not reason:
        raise ValueError("warranted authority result requires a reason")
    return status, reason


def _extract_comparison_atom(case: dict[str, Any], proposition: ComparisonProposition) -> tuple[str, str, str, str, str]:
    raw_claim_id = case.get("raw_claim_id")
    if raw_claim_id != proposition.claim_id:
        raise ValueError(
            "RC8J claim binding authorizes the atom only for its bound claim; "
            f"got atom claim {raw_claim_id!r} and proposition claim {proposition.claim_id!r}"
        )

    atom_id = case.get("target_atom_id")
    proposal = case.get("proposal")
    if not isinstance(atom_id, str) or not atom_id:
        raise ValueError("warranted atom is missing target_atom_id")
    if not isinstance(proposal, dict):
        raise ValueError("warranted atom is missing proposal payload")

    family = proposal.get("family")
    fields = proposal.get("fields")
    if not isinstance(family, str) or not family:
        raise ValueError("warranted atom is missing semantic family")
    if not isinstance(fields, dict):
        raise ValueError("warranted atom is missing semantic fields")

    lhs = fields.get("lhs_entity")
    rhs = fields.get("rhs_entity")
    direction = fields.get("comparison_direction")
    if not all(isinstance(value, str) and value for value in (lhs, rhs, direction)):
        raise ValueError("comparison atom fields are incomplete")
    return atom_id, family, lhs, rhs, direction


def derive_categorical_relation(
    *,
    case: dict[str, Any],
    authority_result: dict[str, Any],
    proposition: ComparisonProposition,
) -> WarrantedRelationReceipt:
    """Derive a bounded comparison relation without caller polarity or score."""
    status, authority_reason = _require_warranted(authority_result)
    atom_id, family, atom_lhs, atom_rhs, atom_direction = _extract_comparison_atom(
        case, proposition
    )

    if family != "comparison":
        relation: CategoricalRelation = "UNRESOLVED"
        reason = "warranted atom family is outside the bounded comparison relation operator"
    else:
        same_pair = atom_lhs == proposition.lhs_entity and atom_rhs == proposition.rhs_entity
        swapped_pair = atom_lhs == proposition.rhs_entity and atom_rhs == proposition.lhs_entity

        if not (same_pair or swapped_pair):
            relation = "IRRELEVANT"
            reason = "warranted comparison atom concerns a different entity pair"
        elif atom_direction not in {"greater_than", "less_than"} or proposition.comparison_direction not in {
            "greater_than",
            "less_than",
        }:
            relation = "UNRESOLVED"
            reason = "same-pair comparison direction is outside the implemented strict-order relation table"
        elif same_pair:
            if atom_direction == proposition.comparison_direction:
                relation = "SUPPORTS"
                reason = "same ordered pair has the same strict comparison direction"
            else:
                relation = "REFUTES"
                reason = "same ordered pair has the opposite strict comparison direction"
        else:
            if atom_direction != proposition.comparison_direction:
                relation = "SUPPORTS"
                reason = "swapped entity pair has the logically inverse strict comparison direction"
            else:
                relation = "REFUTES"
                reason = "swapped entity pair has the same strict direction and therefore opposes the proposition"

    return WarrantedRelationReceipt(
        relation_id=f"relation:{atom_id}:{proposition.claim_id}",
        claim_id=proposition.claim_id,
        atom_id=atom_id,
        authority_status=status,
        authority_reason=authority_reason,
        relation=relation,
        relation_reason=reason,
        proposition=proposition,
        atom_family=family,
        atom_lhs_entity=atom_lhs,
        atom_rhs_entity=atom_rhs,
        atom_comparison_direction=atom_direction,
    )


def compose_categorical_relations(
    proposition: ComparisonProposition,
    relations: tuple[WarrantedRelationReceipt, ...],
) -> CategoricalConclusion:
    """Compose categorical relations without scores, thresholds, or vote counts."""
    relation_ids = [item.relation_id for item in relations]
    if len(set(relation_ids)) != len(relation_ids):
        raise ValueError("categorical relation IDs must be unique within one proposition composition")

    for item in relations:
        if item.claim_id != proposition.claim_id or item.proposition != proposition:
            raise ValueError("all categorical relation receipts must target the exact same proposition")
        if item.authority_status != "WARRANTED":
            raise ValueError("only warranted relation receipts may enter composition")

    ordered = tuple(sorted(relations, key=lambda item: item.relation_id))
    supports = tuple(item for item in ordered if item.relation == "SUPPORTS")
    refutes = tuple(item for item in ordered if item.relation == "REFUTES")
    unresolved = tuple(item for item in ordered if item.relation == "UNRESOLVED")

    if unresolved:
        return CategoricalConclusion(
            claim_id=proposition.claim_id,
            disposition="abstained",
            verdict=None,
            reason_code="unresolved_categorical_relation",
            basis_relation_ids=tuple(item.relation_id for item in unresolved),
        )
    if supports and refutes:
        return CategoricalConclusion(
            claim_id=proposition.claim_id,
            disposition="abstained",
            verdict=None,
            reason_code="mixed_categorical_relations",
            basis_relation_ids=tuple(item.relation_id for item in (*supports, *refutes)),
        )
    if supports:
        return CategoricalConclusion(
            claim_id=proposition.claim_id,
            disposition="decided",
            verdict="supported",
            reason_code="categorical_support",
            basis_relation_ids=tuple(item.relation_id for item in supports),
        )
    if refutes:
        return CategoricalConclusion(
            claim_id=proposition.claim_id,
            disposition="decided",
            verdict="contradicted",
            reason_code="categorical_refutation",
            basis_relation_ids=tuple(item.relation_id for item in refutes),
        )
    return CategoricalConclusion(
        claim_id=proposition.claim_id,
        disposition="abstained",
        verdict=None,
        reason_code="no_deciding_categorical_relation",
        basis_relation_ids=tuple(item.relation_id for item in ordered),
    )


__all__ = [
    "CategoricalConclusion",
    "CategoricalRelation",
    "ComparisonProposition",
    "WarrantedRelationReceipt",
    "compose_categorical_relations",
    "derive_categorical_relation",
]
