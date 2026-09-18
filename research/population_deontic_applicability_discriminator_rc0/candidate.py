"""Typed population-to-deontic applicability candidate RC0."""

from __future__ import annotations

from .apparatus import (
    AppliedNorm,
    MembershipContribution,
    MembershipStatus,
    NormContribution,
    Relation,
    SubjectKind,
)


def _applied(norm: NormContribution, entity: str) -> AppliedNorm:
    return AppliedNorm(
        entity=entity,
        mode=norm.norm.mode,
        action=norm.norm.action,
        exceptions=norm.norm.exceptions,
        condition=norm.norm.condition,
        temporal_relation=norm.norm.temporal_relation,
        temporal_reference=norm.norm.temporal_reference,
    )


def compose_applicability(
    norm: NormContribution,
    membership: MembershipContribution,
    query: AppliedNorm,
) -> Relation:
    if not norm.warranted or not membership.warranted:
        return Relation.UNRESOLVED

    if norm.subject_kind is not SubjectKind.POPULATION:
        return Relation.UNRESOLVED

    if membership.status is not MembershipStatus.MEMBER:
        return Relation.UNRESOLVED

    if norm.norm.subject != membership.population:
        return Relation.UNRESOLVED

    if query != _applied(norm, membership.entity):
        return Relation.UNRESOLVED

    return Relation.SUPPORTS
