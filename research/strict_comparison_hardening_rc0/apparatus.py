"""Adversarial hardening corpus for the frozen RC7F-B1 comparator."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from research.comparative_relation_measurement_rc7fb1.comparator import measure


class Bucket(StrEnum):
    MUST_RETAIN = "MUST_RETAIN"
    DIAGNOSTIC = "DIAGNOSTIC"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True, slots=True)
class Atom:
    left: str
    relation: str
    right: str


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    bucket: Bucket
    text: str
    expected: Atom | None


def atom(left: str, relation: str, right: str) -> Atom:
    return Atom(left.lower(), relation, right.lower())


CASES: tuple[Case, ...] = (
    Case(
        "SCM01",
        Bucket.MUST_RETAIN,
        "Sector A processed 20 units, 3 more than Sector B.",
        atom("Sector A", "MORE_THAN", "Sector B"),
    ),
    Case(
        "SCM02",
        Bucket.MUST_RETAIN,
        "Sector A recorded a higher output than Sector B.",
        atom("Sector A", "GREATER_THAN", "Sector B"),
    ),
    Case(
        "SCM03",
        Bucket.MUST_RETAIN,
        "Sector A exceeded Sector B by 4 units.",
        atom("Sector A", "MORE_THAN", "Sector B"),
    ),
    Case(
        "SCM04",
        Bucket.MUST_RETAIN,
        "Sector A produced a total equal to Sector B.",
        atom("Sector A", "EQUAL_TO", "Sector B"),
    ),
    Case(
        "SCM05",
        Bucket.MUST_RETAIN,
        "Sector A produced twice as many units as Sector B.",
        atom("Sector A", "MULTIPLE_OF", "Sector B"),
    ),
    Case(
        "SCM06",
        Bucket.MUST_RETAIN,
        "Pressure was more than 30 units.",
        atom("Pressure", "MORE_THAN", "30 units"),
    ),
    Case(
        "SCD01",
        Bucket.DIAGNOSTIC,
        "Women recorded a higher rate than Men.",
        atom("Women", "GREATER_THAN", "Men"),
    ),
    Case(
        "SCD02",
        Bucket.DIAGNOSTIC,
        "Region-1 recorded a lower score than Region-2.",
        atom("Region-1", "LESS_THAN", "Region-2"),
    ),
    Case(
        "SCD03",
        Bucket.DIAGNOSTIC,
        "Sector A was slightly higher than Sector B.",
        atom("Sector A", "GREATER_THAN", "Sector B"),
    ),
    Case(
        "SCD04",
        Bucket.DIAGNOSTIC,
        "Sector A trailed Sector B by 2 percentage points.",
        atom("Sector A", "LESS_THAN", "Sector B"),
    ),
    Case(
        "SCD05",
        Bucket.DIAGNOSTIC,
        "Sector A produced half as many units as Sector B.",
        atom("Sector A", "MULTIPLE_OF", "Sector B"),
    ),
    Case(
        "SCD06",
        Bucket.DIAGNOSTIC,
        "Temperature remained less than 5 units.",
        atom("Temperature", "LESS_THAN", "5 units"),
    ),
    Case("SCF01", Bucket.FAIL_CLOSED, "Sector A was not higher than Sector B.", None),
    Case("SCF02", Bucket.FAIL_CLOSED, "Sector A was no higher than Sector B.", None),
    Case("SCF03", Bucket.FAIL_CLOSED, "Sector A was probably higher than Sector B.", None),
    Case("SCF04", Bucket.FAIL_CLOSED, "Sector A was allegedly higher than Sector B.", None),
    Case("SCF05", Bucket.FAIL_CLOSED, "Sector A may be higher than Sector B.", None),
    Case("SCF06", Bucket.FAIL_CLOSED, "Sector A could be higher than Sector B.", None),
    Case("SCF07", Bucket.FAIL_CLOSED, "If Sector A is higher than Sector B, notify QA.", None),
    Case("SCF08", Bucket.FAIL_CLOSED, "The report says Sector A is higher than Sector B.", None),
    Case("SCF09", Bucket.FAIL_CLOSED, "Sector A is not equal to Sector B.", None),
    Case("SCF10", Bucket.FAIL_CLOSED, "Sector A is not the same as Sector B.", None),
    Case("SCF11", Bucket.FAIL_CLOSED, "Sector A produced not twice as many units as Sector B.", None),
    Case("SCF12", Bucket.FAIL_CLOSED, "Sector A is higher than Sector B and Sector C.", None),
    Case("SCF13", Bucket.FAIL_CLOSED, "Sector A is higher than Sector B or Sector C.", None),
)


def observe(text: str) -> Atom | None:
    result = measure(text)
    if result["status"] != "CLAIMED":
        return None
    proposals = result["proposals"]
    if len(proposals) != 1:
        raise AssertionError(f"unexpected proposal cardinality: {len(proposals)}")
    proposal = proposals[0]
    return Atom(
        left=proposal["left"],
        relation=proposal["relation"],
        right=proposal["right"],
    )


def failures() -> dict[str, tuple[str, ...]]:
    retain: list[str] = []
    diagnostic_wrong: list[str] = []
    unsafe: list[str] = []
    for case in CASES:
        observed = observe(case.text)
        if case.bucket is Bucket.MUST_RETAIN:
            if observed != case.expected:
                retain.append(case.case_id)
        elif case.bucket is Bucket.DIAGNOSTIC:
            if observed is not None and observed != case.expected:
                diagnostic_wrong.append(case.case_id)
        elif observed is not None:
            unsafe.append(case.case_id)
    return {
        "must_retain_failures": tuple(retain),
        "diagnostic_wrong_claims": tuple(diagnostic_wrong),
        "fail_closed_unsafe": tuple(unsafe),
    }
