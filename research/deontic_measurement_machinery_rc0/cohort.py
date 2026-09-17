"""Frozen text cohort for CAL Deontic Measurement Machinery RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Mode(StrEnum):
    PERMITTED = "PERMITTED"
    PROHIBITED = "PROHIBITED"
    OBLIGATORY = "OBLIGATORY"
    PERMISSION_RESTRICTED_TO = "PERMISSION_RESTRICTED_TO"


class Status(StrEnum):
    CLAIMED = "CLAIMED"
    UNRESOLVED = "UNRESOLVED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Bucket(StrEnum):
    MUST_HANDLE = "MUST_HANDLE"
    DIAGNOSTIC = "DIAGNOSTIC"
    FAIL_CLOSED = "FAIL_CLOSED"


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
class Observation:
    status: Status
    norm: Norm | None = None
    detail: str = ""

    @classmethod
    def claimed(cls, norm: Norm) -> "Observation":
        return cls(Status.CLAIMED, norm)

    @classmethod
    def unresolved(cls, detail: str = "") -> "Observation":
        return cls(Status.UNRESOLVED, None, detail)

    @classmethod
    def not_applicable(cls, detail: str = "") -> "Observation":
        return cls(Status.NOT_APPLICABLE, None, detail)


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    bucket: Bucket
    text: str
    expected: Norm | None
    note: str = ""


TECH = "qualified_technicians"
QA = "qa"
CONTRACTORS = "contractors"
RELEASE_BATCH = "release_batch"
APPROVE_RECORD = "approve_record"
ARCHIVE_RECORD = "archive_record"
RECONCILE_DISCREPANCY = "reconcile_discrepancy"
QA_APPROVES = "qa_approves"
QA_SIGNS = "qa_signs"


def n(
    mode: Mode,
    *,
    subject: str = TECH,
    action: str = RELEASE_BATCH,
    exceptions: tuple[str, ...] = (),
    condition: str | None = None,
    temporal_relation: str | None = None,
    temporal_reference: str | None = None,
) -> Norm:
    return Norm(
        mode=mode,
        subject=subject,
        action=action,
        exceptions=exceptions,
        condition=condition,
        temporal_relation=temporal_relation,
        temporal_reference=temporal_reference,
    )


CASES: tuple[Case, ...] = (
    # MUST_HANDLE: direct canonical forms.
    Case("DM01", Bucket.MUST_HANDLE, "Qualified technicians may release the batch.", n(Mode.PERMITTED)),
    Case("DM02", Bucket.MUST_HANDLE, "Qualified technicians must not release the batch.", n(Mode.PROHIBITED)),
    Case("DM03", Bucket.MUST_HANDLE, "Qualified technicians must release the batch.", n(Mode.OBLIGATORY)),
    Case(
        "DM04",
        Bucket.MUST_HANDLE,
        "Only qualified technicians may release the batch.",
        n(Mode.PERMISSION_RESTRICTED_TO),
    ),
    Case(
        "DM05",
        Bucket.MUST_HANDLE,
        "Qualified technicians are permitted to release the batch.",
        n(Mode.PERMITTED),
    ),
    Case(
        "DM06",
        Bucket.MUST_HANDLE,
        "Qualified technicians are prohibited from releasing the batch.",
        n(Mode.PROHIBITED),
    ),
    Case(
        "DM07",
        Bucket.MUST_HANDLE,
        "Qualified technicians are required to release the batch.",
        n(Mode.OBLIGATORY),
    ),
    Case(
        "DM08",
        Bucket.MUST_HANDLE,
        "QA may approve the record.",
        n(Mode.PERMITTED, subject=QA, action=APPROVE_RECORD),
        "Direct permission reading is frozen only for this unhedged actor/action grammar.",
    ),
    Case(
        "DM09",
        Bucket.MUST_HANDLE,
        "Qualified technicians may archive the record.",
        n(Mode.PERMITTED, action=ARCHIVE_RECORD),
    ),
    # MUST_HANDLE: simple modifier binding.
    Case(
        "DM10",
        Bucket.MUST_HANDLE,
        "Qualified technicians may release the batch if QA approves.",
        n(Mode.PERMITTED, condition=QA_APPROVES),
    ),
    Case(
        "DM11",
        Bucket.MUST_HANDLE,
        "Qualified technicians must release the batch after QA signs.",
        n(Mode.OBLIGATORY, temporal_relation="AFTER", temporal_reference=QA_SIGNS),
    ),
    Case(
        "DM12",
        Bucket.MUST_HANDLE,
        "Qualified technicians may release the batch before QA signs.",
        n(Mode.PERMITTED, temporal_relation="BEFORE", temporal_reference=QA_SIGNS),
    ),
    Case(
        "DM13",
        Bucket.MUST_HANDLE,
        "Qualified technicians may release the batch except contractors.",
        n(Mode.PERMITTED, exceptions=(CONTRACTORS,)),
    ),
    Case(
        "DM14",
        Bucket.MUST_HANDLE,
        "Only qualified technicians may release the batch after QA signs.",
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            temporal_relation="AFTER",
            temporal_reference=QA_SIGNS,
        ),
    ),
    # DIAGNOSTIC: useful coverage, not a promotion prerequisite.
    Case(
        "DD01",
        Bucket.DIAGNOSTIC,
        "The batch may be released by qualified technicians.",
        n(Mode.PERMITTED),
        "Passive voice.",
    ),
    Case(
        "DD02",
        Bucket.DIAGNOSTIC,
        "Qualified technicians shall release the batch.",
        n(Mode.OBLIGATORY),
        "Regulatory shall.",
    ),
    Case(
        "DD03",
        Bucket.DIAGNOSTIC,
        "Qualified technicians shall not release the batch.",
        n(Mode.PROHIBITED),
        "Regulatory shall-not.",
    ),
    Case(
        "DD04",
        Bucket.DIAGNOSTIC,
        "Release of the batch is limited to qualified technicians.",
        n(Mode.PERMISSION_RESTRICTED_TO),
        "Alternate restricted-to surface.",
    ),
    Case(
        "DD05",
        Bucket.DIAGNOSTIC,
        "Qualified technicians must reconcile the discrepancy.",
        n(Mode.OBLIGATORY, action=RECONCILE_DISCREPANCY),
        "Unfamiliar action tests open-vocabulary behavior.",
    ),
    Case(
        "DD06",
        Bucket.DIAGNOSTIC,
        "The SOP permits qualified technicians to release the batch.",
        n(Mode.PERMITTED),
        "Attribution surface: exact claim is allowed only if attribution is retained or safely reconstructed later.",
    ),
    # FAIL_CLOSED: modal/scope/cross-family traps.
    Case(
        "DF01",
        Bucket.FAIL_CLOSED,
        "The batch may fail sterility testing.",
        None,
        "Epistemic possibility, not deontic permission.",
    ),
    Case(
        "DF02",
        Bucket.FAIL_CLOSED,
        "Qualified technicians may be tired after the shift.",
        None,
        "Epistemic/state possibility.",
    ),
    Case(
        "DF03",
        Bucket.FAIL_CLOSED,
        "Qualified technicians may not release the batch.",
        None,
        "May-not is scope-ambiguous in RC0.",
    ),
    Case(
        "DF04",
        Bucket.FAIL_CLOSED,
        "Qualified technicians are not required to release the batch.",
        None,
        "Negated obligation is not direct permission.",
    ),
    Case(
        "DF05",
        Bucket.FAIL_CLOSED,
        "The report says qualified technicians may release the batch.",
        None,
        "Reporting wrapper cannot be erased.",
    ),
    Case(
        "DF06",
        Bucket.FAIL_CLOSED,
        '"Qualified technicians may release the batch," the witness said.',
        None,
        "Quotation/attribution wrapper.",
    ),
    Case(
        "DF07",
        Bucket.FAIL_CLOSED,
        "Qualified technicians may release and archive the batch.",
        None,
        "Multiple actions require composition or explicit conjunction semantics.",
    ),
    Case(
        "DF08",
        Bucket.FAIL_CLOSED,
        "Qualified technicians must release either batch A or batch B.",
        None,
        "Disjunction scope is outside RC0.",
    ),
    Case(
        "DF09",
        Bucket.FAIL_CLOSED,
        "If QA approves, qualified technicians may release the batch unless a deviation is open.",
        None,
        "Nested condition plus exception.",
    ),
    Case(
        "DF10",
        Bucket.FAIL_CLOSED,
        "Only qualified technicians must release the batch.",
        None,
        "Only + obligation scope is not Gate-0 restricted-permission semantics.",
    ),
    Case(
        "DF11",
        Bucket.FAIL_CLOSED,
        "The system may record the event after restart.",
        None,
        "Epistemic/ability reading; event-occurrence neighbor.",
    ),
    Case(
        "DF12",
        Bucket.FAIL_CLOSED,
        "Qualified technicians can release the batch.",
        None,
        "Ability/capability is not automatically permission.",
    ),
)


CASES_BY_ID = {case.case_id: case for case in CASES}

METAMORPHIC_PAIRS: tuple[tuple[str, str], ...] = (
    ("DM01", "DM02"),  # permission -> prohibition
    ("DM01", "DM04"),  # direct -> restricted-to
    ("DM01", "DM10"),  # condition added
    ("DM01", "DF05"),  # reporting wrapper
    ("DM01", "DF01"),  # deontic may -> epistemic may
)
