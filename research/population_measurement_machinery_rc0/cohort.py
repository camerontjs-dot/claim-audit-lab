"""Frozen text cohort for CAL Population Measurement Machinery RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias


class MembershipStatus(StrEnum):
    MEMBER = "MEMBER"
    NON_MEMBER = "NON_MEMBER"


class Status(StrEnum):
    CLAIMED = "CLAIMED"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Bucket(StrEnum):
    MUST_HANDLE = "MUST_HANDLE"
    DIAGNOSTIC = "DIAGNOSTIC"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True, slots=True)
class MembershipAtom:
    entity: str
    population: str
    status: MembershipStatus


@dataclass(frozen=True, slots=True)
class SubsetAtom:
    child: str
    parent: str


Atom: TypeAlias = MembershipAtom | SubsetAtom


@dataclass(frozen=True, slots=True)
class Observation:
    status: Status
    atom: Atom | None = None
    detail: str = ""

    @classmethod
    def claimed(cls, atom: Atom) -> Observation:
        return cls(Status.CLAIMED, atom)

    @classmethod
    def unresolved(cls, detail: str = "") -> Observation:
        return cls(Status.UNRESOLVED, None, detail)

    @classmethod
    def not_applicable(cls, detail: str = "") -> Observation:
        return cls(Status.NOT_APPLICABLE, None, detail)


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    bucket: Bucket
    text: str
    expected: Atom | None
    note: str = ""


ALICE = "alice"
BOB = "bob"
QUALIFIED_TECHNICIANS = "qualified_technicians"
STERILE_TECHNICIANS = "sterile_technicians"
TRAINED_PERSONNEL = "trained_personnel"
REVIEWERS = "reviewers"
QUALIFIED_PERSONNEL = "qualified_personnel"
GROUP_A = "group_a"


def member(entity: str, population: str) -> MembershipAtom:
    return MembershipAtom(entity, population, MembershipStatus.MEMBER)


def nonmember(entity: str, population: str) -> MembershipAtom:
    return MembershipAtom(entity, population, MembershipStatus.NON_MEMBER)


def subset(child: str, parent: str) -> SubsetAtom:
    return SubsetAtom(child, parent)


CASES: tuple[Case, ...] = (
    Case(
        "PM01",
        Bucket.MUST_HANDLE,
        "Alice is a qualified technician.",
        member(ALICE, QUALIFIED_TECHNICIANS),
    ),
    Case(
        "PM02",
        Bucket.MUST_HANDLE,
        "Alice is not a qualified technician.",
        nonmember(ALICE, QUALIFIED_TECHNICIANS),
    ),
    Case(
        "PM03",
        Bucket.MUST_HANDLE,
        "Alice is a member of Group A.",
        member(ALICE, GROUP_A),
    ),
    Case(
        "PM04",
        Bucket.MUST_HANDLE,
        "Alice is not a member of Group A.",
        nonmember(ALICE, GROUP_A),
    ),
    Case(
        "PM05",
        Bucket.MUST_HANDLE,
        "Sterile technicians are trained personnel.",
        subset(STERILE_TECHNICIANS, TRAINED_PERSONNEL),
    ),
    Case(
        "PM06",
        Bucket.MUST_HANDLE,
        "All sterile technicians are trained personnel.",
        subset(STERILE_TECHNICIANS, TRAINED_PERSONNEL),
    ),
    Case(
        "PM07",
        Bucket.MUST_HANDLE,
        "Every sterile technician is trained personnel.",
        subset(STERILE_TECHNICIANS, TRAINED_PERSONNEL),
    ),
    Case(
        "PM08",
        Bucket.MUST_HANDLE,
        "Reviewers are qualified personnel.",
        subset(REVIEWERS, QUALIFIED_PERSONNEL),
    ),
    Case("PM09", Bucket.MUST_HANDLE, "Bob is a reviewer.", member(BOB, REVIEWERS)),
    Case("PM10", Bucket.MUST_HANDLE, "Bob is not a reviewer.", nonmember(BOB, REVIEWERS)),
    Case(
        "PD01",
        Bucket.DIAGNOSTIC,
        "Alice belongs to Group A.",
        member(ALICE, GROUP_A),
    ),
    Case(
        "PD02",
        Bucket.DIAGNOSTIC,
        "Alice is among the qualified technicians.",
        member(ALICE, QUALIFIED_TECHNICIANS),
    ),
    Case(
        "PD03",
        Bucket.DIAGNOSTIC,
        "Qualified technicians include Alice.",
        member(ALICE, QUALIFIED_TECHNICIANS),
    ),
    Case(
        "PD04",
        Bucket.DIAGNOSTIC,
        "Sterile technicians form a subset of trained personnel.",
        subset(STERILE_TECHNICIANS, TRAINED_PERSONNEL),
    ),
    Case(
        "PD05",
        Bucket.DIAGNOSTIC,
        "Each sterile technician is trained personnel.",
        subset(STERILE_TECHNICIANS, TRAINED_PERSONNEL),
    ),
    Case(
        "PD06",
        Bucket.DIAGNOSTIC,
        "Alice serves as a reviewer.",
        member(ALICE, REVIEWERS),
    ),
    Case(
        "PF01",
        Bucket.FAIL_CLOSED,
        "Some sterile technicians are trained personnel.",
        None,
        "Existential overlap is not universal subset.",
    ),
    Case(
        "PF02",
        Bucket.FAIL_CLOSED,
        "Most sterile technicians are trained personnel.",
        None,
        "Majority is not universal subset.",
    ),
    Case(
        "PF03",
        Bucket.FAIL_CLOSED,
        "Only sterile technicians are trained personnel.",
        None,
        "Only-direction semantics are not the tested subset surface.",
    ),
    Case(
        "PF04",
        Bucket.FAIL_CLOSED,
        "No contractor is an employee.",
        None,
        "Class disjointness is outside the narrow atom contract.",
    ),
    Case(
        "PF05",
        Bucket.FAIL_CLOSED,
        "Alice worked with qualified technicians.",
        None,
        "Association is not membership.",
    ),
    Case(
        "PF06",
        Bucket.FAIL_CLOSED,
        "Alice was a qualified technician.",
        None,
        "Past membership does not establish current membership.",
    ),
    Case(
        "PF07",
        Bucket.FAIL_CLOSED,
        "Alice may be a qualified technician.",
        None,
        "Epistemic possibility is not established membership.",
    ),
    Case(
        "PF08",
        Bucket.FAIL_CLOSED,
        "The report says Alice is a qualified technician.",
        None,
        "Reporting scope cannot be erased.",
    ),
    Case(
        "PF09",
        Bucket.FAIL_CLOSED,
        "Alice joined Group A.",
        None,
        "Join event is not timeless membership.",
    ),
    Case(
        "PF10",
        Bucket.FAIL_CLOSED,
        "Alice is qualified.",
        None,
        "Attribute state is not class membership.",
    ),
    Case(
        "PF11",
        Bucket.FAIL_CLOSED,
        "Alice is a reviewer or an auditor.",
        None,
        "Disjunction requires composition.",
    ),
    Case(
        "PF12",
        Bucket.FAIL_CLOSED,
        "Alice is not only a reviewer but also an auditor.",
        None,
        "Multi-role scope is outside RC0.",
    ),
)


CASES_BY_ID = {case.case_id: case for case in CASES}

METAMORPHIC_PAIRS: tuple[tuple[str, str], ...] = (
    ("PM01", "PM02"),
    ("PM05", "PF01"),
    ("PM05", "PF03"),
    ("PM01", "PF08"),
    ("PM01", "PF07"),
)
