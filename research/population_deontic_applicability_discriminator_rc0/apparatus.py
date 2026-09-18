"""Frozen apparatus for population + deontic applicability discriminator RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Mode(StrEnum):
    PERMITTED = "PERMITTED"
    PROHIBITED = "PROHIBITED"
    OBLIGATORY = "OBLIGATORY"
    PERMISSION_RESTRICTED_TO = "PERMISSION_RESTRICTED_TO"


class MembershipStatus(StrEnum):
    MEMBER = "MEMBER"
    NON_MEMBER = "NON_MEMBER"
    UNKNOWN = "UNKNOWN"


class SubjectKind(StrEnum):
    POPULATION = "POPULATION"
    ENTITY = "ENTITY"


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class Norm:
    mode: Mode
    subject: str
    action: str
    exceptions: tuple[str, ...] = ()
    condition: str | None = None
    temporal_relation: str | None = None
    temporal_reference: str | None = None


@dataclass(frozen=True, slots=True)
class NormContribution:
    norm: Norm
    authority_id: str
    warranted: bool
    subject_kind: SubjectKind


@dataclass(frozen=True, slots=True)
class MembershipContribution:
    entity: str
    population: str
    status: MembershipStatus
    authority_id: str
    warranted: bool


@dataclass(frozen=True, slots=True)
class AppliedNorm:
    entity: str
    mode: Mode
    action: str
    exceptions: tuple[str, ...] = ()
    condition: str | None = None
    temporal_relation: str | None = None
    temporal_reference: str | None = None


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    norm: NormContribution
    membership: MembershipContribution
    query: AppliedNorm
    expected: Relation


TECH = "qualified_technicians"
PERSONNEL = "qualified_personnel"
ALICE = "alice"
BOB = "bob"
RELEASE = "release_batch"
APPROVE = "approve_record"
CONTRACTORS = "contractors"
SIGNED = "qa_signed"
AUDIT = "audit"


def n(
    mode: Mode,
    *,
    subject: str = TECH,
    action: str = RELEASE,
    exceptions: tuple[str, ...] = (),
    condition: str | None = None,
    temporal_relation: str | None = None,
    temporal_reference: str | None = None,
    authority_id: str = "norm-1",
    warranted: bool = True,
    subject_kind: SubjectKind = SubjectKind.POPULATION,
) -> NormContribution:
    return NormContribution(
        Norm(
            mode,
            subject,
            action,
            exceptions,
            condition,
            temporal_relation,
            temporal_reference,
        ),
        authority_id,
        warranted,
        subject_kind,
    )


def m(
    status: MembershipStatus = MembershipStatus.MEMBER,
    *,
    entity: str = ALICE,
    population: str = TECH,
    authority_id: str = "member-1",
    warranted: bool = True,
) -> MembershipContribution:
    return MembershipContribution(entity, population, status, authority_id, warranted)


def q(
    mode: Mode,
    *,
    entity: str = ALICE,
    action: str = RELEASE,
    exceptions: tuple[str, ...] = (),
    condition: str | None = None,
    temporal_relation: str | None = None,
    temporal_reference: str | None = None,
) -> AppliedNorm:
    return AppliedNorm(
        entity,
        mode,
        action,
        exceptions,
        condition,
        temporal_relation,
        temporal_reference,
    )


CASES: tuple[Case, ...] = (
    Case("ND01", n(Mode.PERMITTED), m(), q(Mode.PERMITTED), Relation.SUPPORTS),
    Case(
        "ND02",
        n(Mode.OBLIGATORY, condition=SIGNED),
        m(),
        q(Mode.OBLIGATORY, condition=SIGNED),
        Relation.SUPPORTS,
    ),
    Case(
        "ND03",
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            exceptions=(CONTRACTORS,),
            temporal_relation="AFTER",
            temporal_reference=AUDIT,
        ),
        m(),
        q(
            Mode.PERMISSION_RESTRICTED_TO,
            exceptions=(CONTRACTORS,),
            temporal_relation="AFTER",
            temporal_reference=AUDIT,
        ),
        Relation.SUPPORTS,
    ),
    Case(
        "ND04",
        n(Mode.PROHIBITED, action=APPROVE),
        m(),
        q(Mode.PROHIBITED, action=APPROVE),
        Relation.SUPPORTS,
    ),
    Case(
        "NU01",
        n(Mode.PERMITTED),
        m(MembershipStatus.NON_MEMBER),
        q(Mode.PERMITTED),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU02",
        n(Mode.PERMITTED),
        m(MembershipStatus.UNKNOWN),
        q(Mode.PERMITTED),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU03",
        n(Mode.PERMITTED),
        m(population=PERSONNEL),
        q(Mode.PERMITTED),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU04",
        n(Mode.PERMITTED),
        m(entity=BOB),
        q(Mode.PERMITTED, entity=ALICE),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU05",
        n(Mode.PERMITTED, warranted=False),
        m(),
        q(Mode.PERMITTED),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU06",
        n(Mode.PERMITTED),
        m(warranted=False),
        q(Mode.PERMITTED),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU07",
        n(Mode.PERMITTED, subject_kind=SubjectKind.ENTITY),
        m(),
        q(Mode.PERMITTED),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU08",
        n(Mode.OBLIGATORY, condition=SIGNED),
        m(),
        q(Mode.OBLIGATORY),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU09",
        n(Mode.PERMITTED, exceptions=(CONTRACTORS,)),
        m(),
        q(Mode.PERMITTED),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU10",
        n(
            Mode.PROHIBITED,
            temporal_relation="BEFORE",
            temporal_reference=AUDIT,
        ),
        m(),
        q(
            Mode.PROHIBITED,
            temporal_relation="AFTER",
            temporal_reference=AUDIT,
        ),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU11",
        n(Mode.PERMITTED),
        m(),
        q(Mode.OBLIGATORY),
        Relation.UNRESOLVED,
    ),
    Case(
        "NU12",
        n(Mode.PERMITTED, subject=PERSONNEL),
        m(population=TECH),
        q(Mode.PERMITTED),
        Relation.UNRESOLVED,
    ),
)


def _exact_applied(norm: Norm, entity: str) -> AppliedNorm:
    return AppliedNorm(
        entity,
        norm.mode,
        norm.action,
        norm.exceptions,
        norm.condition,
        norm.temporal_relation,
        norm.temporal_reference,
    )


def weak_string_only(
    norm: NormContribution,
    membership: MembershipContribution,
    query: AppliedNorm,
) -> Relation:
    if norm.norm.subject != membership.population:
        return Relation.UNRESOLVED
    if query.entity != membership.entity:
        return Relation.UNRESOLVED
    if query.mode != norm.norm.mode or query.action != norm.norm.action:
        return Relation.UNRESOLVED
    return Relation.SUPPORTS


def weak_ignore_status(
    norm: NormContribution,
    membership: MembershipContribution,
    query: AppliedNorm,
) -> Relation:
    if not norm.warranted or not membership.warranted:
        return Relation.UNRESOLVED
    if norm.subject_kind is not SubjectKind.POPULATION:
        return Relation.UNRESOLVED
    if norm.norm.subject != membership.population:
        return Relation.UNRESOLVED
    if query == _exact_applied(norm.norm, membership.entity):\n        return Relation.SUPPORTS\n    return Relation.UNRESOLVED


def weak_ignore_subject_kind(
    norm: NormContribution,
    membership: MembershipContribution,
    query: AppliedNorm,
) -> Relation:
    if not norm.warranted or not membership.warranted:
        return Relation.UNRESOLVED
    if membership.status is not MembershipStatus.MEMBER:
        return Relation.UNRESOLVED
    if norm.norm.subject != membership.population:
        return Relation.UNRESOLVED
    if query == _exact_applied(norm.norm, membership.entity):\n        return Relation.SUPPORTS\n    return Relation.UNRESOLVED


def weak_drop_modifiers(
    norm: NormContribution,
    membership: MembershipContribution,
    query: AppliedNorm,
) -> Relation:
    if (
        not norm.warranted
        or not membership.warranted
        or norm.subject_kind is not SubjectKind.POPULATION
        or membership.status is not MembershipStatus.MEMBER
        or norm.norm.subject != membership.population
    ):
        return Relation.UNRESOLVED
    if (
        query.entity == membership.entity
        and query.mode is norm.norm.mode
        and query.action == norm.norm.action
    ):
        return Relation.SUPPORTS
    return Relation.UNRESOLVED


def weak_ignore_warrant(
    norm: NormContribution,
    membership: MembershipContribution,
    query: AppliedNorm,
) -> Relation:
    if norm.subject_kind is not SubjectKind.POPULATION:
        return Relation.UNRESOLVED
    if membership.status is not MembershipStatus.MEMBER:
        return Relation.UNRESOLVED
    if norm.norm.subject != membership.population:
        return Relation.UNRESOLVED
    if query == _exact_applied(norm.norm, membership.entity):\n        return Relation.SUPPORTS\n    return Relation.UNRESOLVED
