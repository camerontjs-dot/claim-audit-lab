"""Frozen text cohort for CAL Causal Measurement Machinery RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Kind(StrEnum):
    CAUSES = "CAUSES"
    CONTRIBUTES_TO = "CONTRIBUTES_TO"
    PREVENTS = "PREVENTS"
    CORRELATES_WITH = "CORRELATES_WITH"
    PRECEDES = "PRECEDES"
    CO_OCCURS = "CO_OCCURS"


class Status(StrEnum):
    CLAIMED = "CLAIMED"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Bucket(StrEnum):
    MUST_HANDLE = "MUST_HANDLE"
    DIAGNOSTIC = "DIAGNOSTIC"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True, slots=True)
class CausalAtom:
    cause: str
    effect: str
    kind: Kind


@dataclass(frozen=True, slots=True)
class Observation:
    status: Status
    atom: CausalAtom | None = None
    detail: str = ""

    @classmethod
    def claimed(cls, atom: CausalAtom) -> Observation:
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
    expected: CausalAtom | None


def a(cause: str, effect: str, kind: Kind) -> CausalAtom:
    return CausalAtom(cause.casefold(), effect.casefold(), kind)


CASES: tuple[Case, ...] = (
    Case("CM01", Bucket.MUST_HANDLE, "A causes B.", a("A","B",Kind.CAUSES)),
    Case("CM02", Bucket.MUST_HANDLE, "A contributes to B.", a("A","B",Kind.CONTRIBUTES_TO)),
    Case("CM03", Bucket.MUST_HANDLE, "A prevents B.", a("A","B",Kind.PREVENTS)),
    Case("CM04", Bucket.MUST_HANDLE, "A correlates with B.", a("A","B",Kind.CORRELATES_WITH)),
    Case("CM05", Bucket.MUST_HANDLE, "A precedes B.", a("A","B",Kind.PRECEDES)),
    Case("CM06", Bucket.MUST_HANDLE, "A co-occurs with B.", a("A","B",Kind.CO_OCCURS)),
    Case("CM07", Bucket.MUST_HANDLE, "X causes Y.", a("X","Y",Kind.CAUSES)),
    Case("CD01", Bucket.DIAGNOSTIC, "B is caused by A.", a("A","B",Kind.CAUSES)),
    Case("CD02", Bucket.DIAGNOSTIC, "B is prevented by A.", a("A","B",Kind.PREVENTS)),
    Case("CD03", Bucket.DIAGNOSTIC, "A is a contributing factor to B.", a("A","B",Kind.CONTRIBUTES_TO)),
    Case("CD04", Bucket.DIAGNOSTIC, "A and B are correlated.", a("A","B",Kind.CORRELATES_WITH)),
    Case("CD05", Bucket.DIAGNOSTIC, "A occurs before B.", a("A","B",Kind.PRECEDES)),
    Case("CD06", Bucket.DIAGNOSTIC, "A occurs together with B.", a("A","B",Kind.CO_OCCURS)),
    Case("CF01", Bucket.FAIL_CLOSED, "The report says A causes B.", None),
    Case("CF02", Bucket.FAIL_CLOSED, "A may cause B.", None),
    Case("CF03", Bucket.FAIL_CLOSED, "A is a risk factor for B.", None),
    Case("CF04", Bucket.FAIL_CLOSED, "A predicts B.", None),
    Case("CF05", Bucket.FAIL_CLOSED, "A causes B and C.", None),
    Case("CF06", Bucket.FAIL_CLOSED, "A causes B or C.", None),
    Case("CF07", Bucket.FAIL_CLOSED, "A was manipulated and B changed.", None),
    Case("CF08", Bucket.FAIL_CLOSED, "A is associated with B.", None),
    Case("CF09", Bucket.FAIL_CLOSED, "A explains B.", None),
    Case("CF10", Bucket.FAIL_CLOSED, "A is sufficient for B.", None),
)

CASES_BY_ID = {case.case_id: case for case in CASES}

METAMORPHIC_PAIRS: tuple[tuple[str, str], ...] = (
    ("CM01", "CM02"),
    ("CM01", "CM04"),
    ("CM01", "CM05"),
    ("CM01", "CF01"),
    ("CM01", "CF02"),
    ("CM01", "CF05"),
    ("CM01", "CM07"),
)
