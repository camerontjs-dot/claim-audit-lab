"""Frozen text cohort for Attribute State Measurement Machinery RC1."""

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
class StateAtom:
    entity: str
    attribute: str
    domain: str
    value: str
    functional: bool


@dataclass(frozen=True, slots=True)
class Observation:
    status: Status
    atom: StateAtom | None = None
    detail: str = ""

    @classmethod
    def claimed(cls, atom: StateAtom) -> Observation:
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
    expected: StateAtom | None


def s(entity: str, attribute: str, domain: str, value: str, functional: bool) -> StateAtom:
    return StateAtom(entity, attribute, domain, value, functional)


CASES: tuple[Case, ...] = (
    Case("AM01", Bucket.MUST_HANDLE, "Batch status is released.", s("batch","status","batch_status","released",True)),
    Case("AM02", Bucket.MUST_HANDLE, "Batch status is held.", s("batch","status","batch_status","held",True)),
    Case("AM03", Bucket.MUST_HANDLE, "Device mode is standby.", s("device","mode","device_mode","standby",True)),
    Case("AM04", Bucket.MUST_HANDLE, "Device mode is active.", s("device","mode","device_mode","active",True)),
    Case("AM05", Bucket.MUST_HANDLE, "Record tag is critical.", s("record","tag","labels","critical",False)),
    Case("AM06", Bucket.MUST_HANDLE, "Record tag is reviewed.", s("record","tag","labels","reviewed",False)),
    Case("AM07", Bucket.MUST_HANDLE, "System availability is unavailable.", s("system","availability","availability","unavailable",True)),
    Case("AD01", Bucket.DIAGNOSTIC, "The batch's status is released.", s("batch","status","batch_status","released",True)),
    Case("AD02", Bucket.DIAGNOSTIC, "Batch status: released.", s("batch","status","batch_status","released",True)),
    Case("AD03", Bucket.DIAGNOSTIC, "The device is in standby mode.", s("device","mode","device_mode","standby",True)),
    Case("AD04", Bucket.DIAGNOSTIC, "The batch remains held.", s("batch","status","batch_status","held",True)),
    Case("AD05", Bucket.DIAGNOSTIC, "Device mode is maintenance.", s("device","mode","device_mode","maintenance",True)),
    Case("AD06", Bucket.DIAGNOSTIC, "Other batch status is released.", s("other_batch","status","batch_status","released",True)),
    Case("AD07", Bucket.DIAGNOSTIC, "Document status is released.", s("document","status","document_status","released",True)),
    Case("AF01", Bucket.FAIL_CLOSED, "Alice is a reviewer.", None),
    Case("AF02", Bucket.FAIL_CLOSED, "The batch became held.", None),
    Case("AF03", Bucket.FAIL_CLOSED, "The batch was released yesterday.", None),
    Case("AF04", Bucket.FAIL_CLOSED, "Batch status may be released.", None),
    Case("AF05", Bucket.FAIL_CLOSED, "Batch status must be released.", None),
    Case("AF06", Bucket.FAIL_CLOSED, "The report says batch status is released.", None),
    Case("AF07", Bucket.FAIL_CLOSED, '"Batch status is released," QA said.', None),
    Case("AF08", Bucket.FAIL_CLOSED, "Record tag is critical and reviewed.", None),
    Case("AF09", Bucket.FAIL_CLOSED, "Device mode is active or standby.", None),
    Case("AF10", Bucket.FAIL_CLOSED, "Batch temperature is 5 °C.", None),
)

CASES_BY_ID={case.case_id:case for case in CASES}
METAMORPHIC_PAIRS=(
    ("AM01","AF06"),
    ("AM01","AF04"),
    ("AM01","AF02"),
    ("AM03","AF09"),
    ("AM01","AD06"),
    ("AM01","AD07"),
)
