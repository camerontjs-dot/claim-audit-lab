"""Frozen text cohort for CAL Scalar Measurement Machinery RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction


class Status(StrEnum):
    CLAIMED = "CLAIMED"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Bucket(StrEnum):
    MUST_HANDLE = "MUST_HANDLE"
    DIAGNOSTIC = "DIAGNOSTIC"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True, slots=True)
class Target:
    entity: str
    metric: str
    unit: str


@dataclass(frozen=True, slots=True)
class ScalarAtom:
    entity: str
    metric: str
    unit: str
    low: Fraction
    high: Fraction
    exact: bool = True


@dataclass(frozen=True, slots=True)
class Observation:
    status: Status
    atom: ScalarAtom | None = None
    detail: str = ""

    @classmethod
    def claimed(cls, atom: ScalarAtom) -> Observation:
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
    target: Target
    expected: ScalarAtom | None
    note: str = ""


F = Fraction
BATCH_YIELD = Target("batch", "yield", "%")
BATCH_COUNT = Target("batch", "count", "count")
BATCH_TEMP_C = Target("batch", "temperature", "degC")
BATCH_TEMP_F = Target("batch", "temperature", "degF")
BATCH_MASS = Target("batch", "mass", "mg")
BATCH_DURATION = Target("batch", "duration", "min")


def point(target: Target, value: Fraction, *, exact: bool = True) -> ScalarAtom:
    return ScalarAtom(target.entity, target.metric, target.unit, value, value, exact)


def interval(
    target: Target,
    low: Fraction,
    high: Fraction,
    *,
    exact: bool = True,
) -> ScalarAtom:
    return ScalarAtom(target.entity, target.metric, target.unit, low, high, exact)


CASES: tuple[Case, ...] = (
    Case(
        "SM01",
        Bucket.MUST_HANDLE,
        "Batch yield was 92%.",
        BATCH_YIELD,
        point(BATCH_YIELD, F(92)),
    ),
    Case(
        "SM02",
        Bucket.MUST_HANDLE,
        "Batch yield was 92.5%.",
        BATCH_YIELD,
        point(BATCH_YIELD, F(185, 2)),
    ),
    Case(
        "SM03",
        Bucket.MUST_HANDLE,
        "Batch yield was between 90% and 94%.",
        BATCH_YIELD,
        interval(BATCH_YIELD, F(90), F(94)),
    ),
    Case(
        "SM04",
        Bucket.MUST_HANDLE,
        "Batch yield ranged from 90% to 94%.",
        BATCH_YIELD,
        interval(BATCH_YIELD, F(90), F(94)),
    ),
    Case(
        "SM05",
        Bucket.MUST_HANDLE,
        "Batch count was 17.",
        BATCH_COUNT,
        point(BATCH_COUNT, F(17)),
    ),
    Case(
        "SM06",
        Bucket.MUST_HANDLE,
        "Batch temperature was 5 °C.",
        BATCH_TEMP_C,
        point(BATCH_TEMP_C, F(5)),
    ),
    Case(
        "SM07",
        Bucket.MUST_HANDLE,
        "Batch mass was 12 mg.",
        BATCH_MASS,
        point(BATCH_MASS, F(12)),
    ),
    Case(
        "SM08",
        Bucket.MUST_HANDLE,
        "Batch duration was 30 min.",
        BATCH_DURATION,
        point(BATCH_DURATION, F(30)),
    ),
    Case(
        "SM09",
        Bucket.MUST_HANDLE,
        "The batch yield measured 91%.",
        BATCH_YIELD,
        point(BATCH_YIELD, F(91)),
    ),
    Case(
        "SD01",
        Bucket.DIAGNOSTIC,
        "Batch yield was approximately 92%.",
        BATCH_YIELD,
        point(BATCH_YIELD, F(92), exact=False),
    ),
    Case(
        "SD02",
        Bucket.DIAGNOSTIC,
        "Batch yield was about 92.5 percent.",
        BATCH_YIELD,
        point(BATCH_YIELD, F(185, 2), exact=False),
    ),
    Case(
        "SD03",
        Bucket.DIAGNOSTIC,
        "Batch yield: 92%.",
        BATCH_YIELD,
        point(BATCH_YIELD, F(92)),
    ),
    Case(
        "SD04",
        Bucket.DIAGNOSTIC,
        "The yield of the batch was 92%.",
        BATCH_YIELD,
        point(BATCH_YIELD, F(92)),
    ),
    Case(
        "SD05",
        Bucket.DIAGNOSTIC,
        "Batch temperature was 41 °F.",
        BATCH_TEMP_F,
        point(BATCH_TEMP_F, F(41)),
    ),
    Case(
        "SD06",
        Bucket.DIAGNOSTIC,
        "Batch yield was 92 ± 2%.",
        BATCH_YIELD,
        interval(BATCH_YIELD, F(90), F(94), exact=False),
    ),
    Case(
        "SF01",
        Bucket.FAIL_CLOSED,
        "The batch was released on 2026-09-17.",
        BATCH_YIELD,
        None,
        "Date number is not yield.",
    ),
    Case(
        "SF02",
        Bucket.FAIL_CLOSED,
        "Batch yield increased from 80% to 90%.",
        BATCH_YIELD,
        None,
        "Quantitative change needs composition.",
    ),
    Case(
        "SF03",
        Bucket.FAIL_CLOSED,
        "Batch yield increased by 10 percentage points.",
        BATCH_YIELD,
        None,
        "Percentage-point change is not a scalar state.",
    ),
    Case(
        "SF04",
        Bucket.FAIL_CLOSED,
        "Batch yield was more than 90%.",
        BATCH_YIELD,
        None,
        "Open bound is outside the finite interval RC0 contract.",
    ),
    Case(
        "SF05",
        Bucket.FAIL_CLOSED,
        "The report says batch yield was 92%.",
        BATCH_YIELD,
        None,
        "Reporting scope cannot be erased.",
    ),
    Case(
        "SF06",
        Bucket.FAIL_CLOSED,
        "Batch yield may be 92%.",
        BATCH_YIELD,
        None,
        "Epistemic modality does not establish a scalar state.",
    ),
    Case(
        "SF07",
        Bucket.FAIL_CLOSED,
        "Batch yield was 92% or 94%.",
        BATCH_YIELD,
        None,
        "Disjunction is not a closed interval.",
    ),
    Case(
        "SF08",
        Bucket.FAIL_CLOSED,
        "Batch yield was 92% at T1 and 94% at T2.",
        BATCH_YIELD,
        None,
        "Multiple temporal states require composition.",
    ),
    Case(
        "SF09",
        Bucket.FAIL_CLOSED,
        "Batch count was 92.",
        BATCH_YIELD,
        None,
        "Metric mismatch.",
    ),
    Case(
        "SF10",
        Bucket.FAIL_CLOSED,
        "Other batch yield was 92%.",
        BATCH_YIELD,
        None,
        "Entity mismatch.",
    ),
    Case(
        "SF11",
        Bucket.FAIL_CLOSED,
        "Batch yield was 0.92 fraction.",
        BATCH_YIELD,
        None,
        "Unit conversion is not qualified.",
    ),
    Case(
        "SF12",
        Bucket.FAIL_CLOSED,
        "Batch temperature ranged from 5 °C to 41 °F.",
        BATCH_TEMP_C,
        None,
        "Mixed-unit range.",
    ),
    Case(
        "SF13",
        Bucket.FAIL_CLOSED,
        "Software version was 3.2.",
        BATCH_YIELD,
        None,
        "Version number is not yield.",
    ),
)


CASES_BY_ID = {case.case_id: case for case in CASES}

METAMORPHIC_PAIRS: tuple[tuple[str, str], ...] = (
    ("SM01", "SD01"),
    ("SM01", "SF05"),
    ("SM01", "SF06"),
    ("SM01", "SF09"),
    ("SM01", "SF11"),
    ("SM03", "SF04"),
    ("SM01", "SF02"),
)
