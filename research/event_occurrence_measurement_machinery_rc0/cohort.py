"""Frozen text cohort for Event Occurrence Measurement Machinery RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Polarity(StrEnum):
    OCCURRED = "OCCURRED"
    DID_NOT_OCCUR = "DID_NOT_OCCUR"


class Status(StrEnum):
    CLAIMED = "CLAIMED"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Bucket(StrEnum):
    MUST_HANDLE = "MUST_HANDLE"
    DIAGNOSTIC = "DIAGNOSTIC"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True, slots=True)
class EventAtom:
    actor: str
    action: str
    object: str
    polarity: Polarity
    scope: str = "NARRATOR"
    time: str | None = None


@dataclass(frozen=True, slots=True)
class Observation:
    status: Status
    atom: EventAtom | None = None
    detail: str = ""

    @classmethod
    def claimed(cls, atom: EventAtom) -> Observation:
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
    expected: EventAtom | None
    note: str = ""


def e(
    actor: str,
    action: str,
    obj: str,
    polarity: Polarity = Polarity.OCCURRED,
    *,
    time: str | None = None,
) -> EventAtom:
    return EventAtom(actor, action, obj, polarity, time=time)


CASES: tuple[Case, ...] = (
    Case("EM01", Bucket.MUST_HANDLE, "QA approved the batch.", e("qa", "approve", "batch")),
    Case(
        "EM02",
        Bucket.MUST_HANDLE,
        "QA did not approve the batch.",
        e("qa", "approve", "batch", Polarity.DID_NOT_OCCUR),
    ),
    Case("EM03", Bucket.MUST_HANDLE, "Ops released the batch.", e("ops", "release", "batch")),
    Case("EM04", Bucket.MUST_HANDLE, "QA signed the record.", e("qa", "sign", "record")),
    Case("EM05", Bucket.MUST_HANDLE, "System recorded the event.", e("system", "record", "event")),
    Case(
        "EM06",
        Bucket.MUST_HANDLE,
        "QA approved the batch at T1.",
        e("qa", "approve", "batch", time="T1"),
    ),
    Case(
        "ED01",
        Bucket.DIAGNOSTIC,
        "The batch was approved by QA.",
        e("qa", "approve", "batch"),
    ),
    Case(
        "ED02",
        Bucket.DIAGNOSTIC,
        "The batch was not approved by QA.",
        e("qa", "approve", "batch", Polarity.DID_NOT_OCCUR),
    ),
    Case(
        "ED03",
        Bucket.DIAGNOSTIC,
        "QA quarantined the batch.",
        e("qa", "quarantine", "batch"),
    ),
    Case(
        "ED04",
        Bucket.DIAGNOSTIC,
        "QA's approval of the batch occurred.",
        e("qa", "approve", "batch"),
    ),
    Case(
        "ED05",
        Bucket.DIAGNOSTIC,
        "Event: QA approved batch.",
        e("qa", "approve", "batch"),
    ),
    Case(
        "EF01",
        Bucket.FAIL_CLOSED,
        "The report says QA approved the batch.",
        None,
        "Reporting scope.",
    ),
    Case(
        "EF02",
        Bucket.FAIL_CLOSED,
        '"QA approved the batch," the witness said.',
        None,
        "Quotation scope.",
    ),
    Case(
        "EF03",
        Bucket.FAIL_CLOSED,
        "QA may have approved the batch.",
        None,
        "Epistemic possibility.",
    ),
    Case(
        "EF04",
        Bucket.FAIL_CLOSED,
        "QA must approve the batch.",
        None,
        "Deontic obligation is not occurrence.",
    ),
    Case(
        "EF05",
        Bucket.FAIL_CLOSED,
        "QA plans to approve the batch.",
        None,
        "Intention is not occurrence.",
    ),
    Case(
        "EF06",
        Bucket.FAIL_CLOSED,
        "QA approved the batch before Ops released the record.",
        None,
        "Order-only surface is excluded by the Gate-0 occurrence contract.",
    ),
    Case(
        "EF07",
        Bucket.FAIL_CLOSED,
        "QA approval of the batch was not documented.",
        None,
        "Documentation failure is not event negation.",
    ),
    Case(
        "EF08",
        Bucket.FAIL_CLOSED,
        "QA approved or rejected the batch.",
        None,
        "Disjunction requires composition.",
    ),
    Case(
        "EF09",
        Bucket.FAIL_CLOSED,
        "QA approved and archived the batch.",
        None,
        "Multiple events require composition.",
    ),
    Case(
        "EF10",
        Bucket.FAIL_CLOSED,
        "The batch is approved.",
        None,
        "State is not occurrence.",
    ),
)


CASES_BY_ID = {case.case_id: case for case in CASES}
METAMORPHIC_PAIRS: tuple[tuple[str, str], ...] = (
    ("EM01", "EM02"),
    ("EM01", "EF01"),
    ("EM01", "EF03"),
    ("EM01", "EF04"),
    ("EM01", "EF06"),
    ("EM01", "EF10"),
)
