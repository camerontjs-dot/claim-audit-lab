"""Frozen text cohort for Typed Binary Relation Measurement Machinery RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    CLAIMED = "CLAIMED"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Bucket(StrEnum):
    MUST_HANDLE = "MUST_HANDLE"
    DIAGNOSTIC = "DIAGNOSTIC"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True, slots=True)
class RelationAtom:
    subject: str
    predicate: str
    object: str
    positive: bool = True


@dataclass(frozen=True, slots=True)
class Observation:
    status: Status
    atom: RelationAtom | None = None
    detail: str = ""

    @classmethod
    def claimed(cls, atom: RelationAtom) -> Observation:
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
    expected: RelationAtom | None


CASES: tuple[Case, ...] = (
    Case("RM01", Bucket.MUST_HANDLE, "A owns B.", RelationAtom("a","OWNS","b")),
    Case("RM02", Bucket.MUST_HANDLE, "B is owned by A.", RelationAtom("b","OWNED_BY","a")),
    Case("RM03", Bucket.MUST_HANDLE, "A is adjacent to B.", RelationAtom("a","ADJACENT_TO","b")),
    Case("RM04", Bucket.MUST_HANDLE, "A is north of B.", RelationAtom("a","NORTH_OF","b")),
    Case("RM05", Bucket.MUST_HANDLE, "B is south of A.", RelationAtom("b","SOUTH_OF","a")),
    Case("RM06", Bucket.MUST_HANDLE, "Room is in Zone.", RelationAtom("room","IN","zone")),
    Case("RM07", Bucket.MUST_HANDLE, "Zone contains Room.", RelationAtom("zone","CONTAINS","room")),
    Case("RM08", Bucket.MUST_HANDLE, "A does not own B.", RelationAtom("a","OWNS","b",False)),
    Case("RD01", Bucket.DIAGNOSTIC, "B belongs to A.", RelationAtom("b","OWNED_BY","a")),
    Case("RD02", Bucket.DIAGNOSTIC, "A lies north of B.", RelationAtom("a","NORTH_OF","b")),
    Case("RD03", Bucket.DIAGNOSTIC, "Room lies within Zone.", RelationAtom("room","IN","zone")),
    Case("RD04", Bucket.DIAGNOSTIC, "A and B are adjacent.", RelationAtom("a","ADJACENT_TO","b")),
    Case("RF01", Bucket.FAIL_CLOSED, "A is near B.", None),
    Case("RF02", Bucket.FAIL_CLOSED, "A is north of B and B is north of C.", None),
    Case("RF03", Bucket.FAIL_CLOSED, "A is north of B, so A is north of C.", None),
    Case("RF04", Bucket.FAIL_CLOSED, "A is 5 m north of B.", None),
    Case("RF05", Bucket.FAIL_CLOSED, "The report says A owns B.", None),
    Case("RF06", Bucket.FAIL_CLOSED, "A may own B.", None),
    Case("RF07", Bucket.FAIL_CLOSED, "A owns B or C.", None),
    Case("RF08", Bucket.FAIL_CLOSED, "A owns B and C.", None),
    Case("RF09", Bucket.FAIL_CLOSED, "Alice is a reviewer.", None),
    Case("RF10", Bucket.FAIL_CLOSED, "Batch status is released.", None),
    Case("RF11", Bucket.FAIL_CLOSED, "B owns A.", None),
)

CASES_BY_ID={case.case_id:case for case in CASES}
METAMORPHIC_PAIRS=(("RM01","RM08"),("RM01","RF05"),("RM04","RF04"),("RM04","RF02"),("RM01","RF06"))
