"""Frozen typed cohort for CAL Population Family Discriminator RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MembershipStatus(StrEnum):
    MEMBER = "MEMBER"
    NON_MEMBER = "NON_MEMBER"
    UNKNOWN = "UNKNOWN"


class SubsetEdge(StrEnum):
    NONE = "NONE"
    A_SUB_B = "A_SUB_B"
    B_SUB_A = "B_SUB_A"


class QueryPolarity(StrEnum):
    MEMBER_OF = "MEMBER_OF"
    NOT_MEMBER_OF = "NOT_MEMBER_OF"


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class Authority:
    entity: str
    population: str
    status: MembershipStatus
    subset_edge: SubsetEdge = SubsetEdge.NONE


@dataclass(frozen=True, slots=True)
class Query:
    entity: str
    population: str
    polarity: QueryPolarity


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    authority: Authority
    query: Query


X = "x"
Y = "y"
A = "A"
B = "B"


def a(
    population: str,
    status: MembershipStatus,
    edge: SubsetEdge = SubsetEdge.NONE,
    *,
    entity: str = X,
) -> Authority:
    return Authority(entity=entity, population=population, status=status, subset_edge=edge)


def q(population: str, polarity: QueryPolarity, *, entity: str = X) -> Query:
    return Query(entity=entity, population=population, polarity=polarity)


CASES: tuple[Case, ...] = (
    Case("P01", a(A, MembershipStatus.MEMBER), q(A, QueryPolarity.MEMBER_OF)),
    Case("P02", a(A, MembershipStatus.MEMBER), q(A, QueryPolarity.NOT_MEMBER_OF)),
    Case("P03", a(A, MembershipStatus.NON_MEMBER), q(A, QueryPolarity.MEMBER_OF)),
    Case("P04", a(A, MembershipStatus.NON_MEMBER), q(A, QueryPolarity.NOT_MEMBER_OF)),
    Case("P05", a(A, MembershipStatus.UNKNOWN), q(A, QueryPolarity.MEMBER_OF)),
    Case("P06", a(A, MembershipStatus.UNKNOWN), q(A, QueryPolarity.NOT_MEMBER_OF)),
    # A subset B: valid upward positive and downward negative inheritance.
    Case("P07", a(A, MembershipStatus.MEMBER, SubsetEdge.A_SUB_B), q(B, QueryPolarity.MEMBER_OF)),
    Case("P08", a(A, MembershipStatus.MEMBER, SubsetEdge.A_SUB_B), q(B, QueryPolarity.NOT_MEMBER_OF)),
    Case("P09", a(B, MembershipStatus.MEMBER, SubsetEdge.A_SUB_B), q(A, QueryPolarity.MEMBER_OF)),
    Case("P10", a(B, MembershipStatus.MEMBER, SubsetEdge.A_SUB_B), q(A, QueryPolarity.NOT_MEMBER_OF)),
    Case("P11", a(B, MembershipStatus.NON_MEMBER, SubsetEdge.A_SUB_B), q(A, QueryPolarity.MEMBER_OF)),
    Case("P12", a(B, MembershipStatus.NON_MEMBER, SubsetEdge.A_SUB_B), q(A, QueryPolarity.NOT_MEMBER_OF)),
    Case("P13", a(A, MembershipStatus.NON_MEMBER, SubsetEdge.A_SUB_B), q(B, QueryPolarity.MEMBER_OF)),
    Case("P14", a(A, MembershipStatus.NON_MEMBER, SubsetEdge.A_SUB_B), q(B, QueryPolarity.NOT_MEMBER_OF)),
    # Mirror B subset A.
    Case("P15", a(B, MembershipStatus.MEMBER, SubsetEdge.B_SUB_A), q(A, QueryPolarity.MEMBER_OF)),
    Case("P16", a(B, MembershipStatus.MEMBER, SubsetEdge.B_SUB_A), q(A, QueryPolarity.NOT_MEMBER_OF)),
    Case("P17", a(A, MembershipStatus.MEMBER, SubsetEdge.B_SUB_A), q(B, QueryPolarity.MEMBER_OF)),
    Case("P18", a(A, MembershipStatus.MEMBER, SubsetEdge.B_SUB_A), q(B, QueryPolarity.NOT_MEMBER_OF)),
    Case("P19", a(A, MembershipStatus.NON_MEMBER, SubsetEdge.B_SUB_A), q(B, QueryPolarity.MEMBER_OF)),
    Case("P20", a(A, MembershipStatus.NON_MEMBER, SubsetEdge.B_SUB_A), q(B, QueryPolarity.NOT_MEMBER_OF)),
    Case("P21", a(B, MembershipStatus.NON_MEMBER, SubsetEdge.B_SUB_A), q(A, QueryPolarity.MEMBER_OF)),
    Case("P22", a(B, MembershipStatus.NON_MEMBER, SubsetEdge.B_SUB_A), q(A, QueryPolarity.NOT_MEMBER_OF)),
    # Identity, absent-edge, and unknown sentinels.
    Case("P23", a(A, MembershipStatus.MEMBER), q(A, QueryPolarity.MEMBER_OF, entity=Y)),
    Case("P24", a(A, MembershipStatus.MEMBER), q(B, QueryPolarity.MEMBER_OF)),
    Case("P25", a(A, MembershipStatus.UNKNOWN, SubsetEdge.A_SUB_B), q(B, QueryPolarity.MEMBER_OF)),
    Case("P26", a(B, MembershipStatus.UNKNOWN, SubsetEdge.A_SUB_B), q(A, QueryPolarity.NOT_MEMBER_OF)),
)


METAMORPHIC_PAIRS: tuple[tuple[str, str], ...] = (
    ("P01", "P02"),
    ("P01", "P23"),
    ("P07", "P09"),
    ("P07", "P24"),
    ("P11", "P13"),
    ("P12", "P14"),
    ("P15", "P17"),
    ("P19", "P21"),
    ("P01", "P05"),
)

CASE_BY_ID = {case.case_id: case for case in CASES}
assert len(CASE_BY_ID) == len(CASES)
