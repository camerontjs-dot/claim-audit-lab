"""Semantics-first cohort for CAL Deontic Norm Family Contract RC0."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Mode(StrEnum):
    PERMITTED = "PERMITTED"
    PROHIBITED = "PROHIBITED"
    OBLIGATORY = "OBLIGATORY"
    PERMISSION_RESTRICTED_TO = "PERMISSION_RESTRICTED_TO"


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
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
class Case:
    case_id: str
    source: Norm
    query: Norm


TECH = "qualified_technician"
QA = "qa_reviewer"
AUDITOR = "auditor"
VENDOR = "vendor"
RELEASE = "release_batch"
APPROVE = "approve_record"
SIGNED = "record_signed"
VALIDATED = "record_validated"
AUDIT = "audit"
INSPECTION = "inspection"


def n(
    mode: Mode,
    *,
    subject: str = TECH,
    action: str = RELEASE,
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
    # Exact-mode controls.
    Case("D01", n(Mode.PERMITTED), n(Mode.PERMITTED)),
    Case("D02", n(Mode.PROHIBITED), n(Mode.PROHIBITED)),
    Case("D03", n(Mode.OBLIGATORY), n(Mode.OBLIGATORY)),
    Case("D04", n(Mode.PERMISSION_RESTRICTED_TO), n(Mode.PERMISSION_RESTRICTED_TO)),
    # Direct conflicts.
    Case("D05", n(Mode.PERMITTED), n(Mode.PROHIBITED)),
    Case("D06", n(Mode.PROHIBITED), n(Mode.PERMITTED)),
    Case("D07", n(Mode.OBLIGATORY), n(Mode.PROHIBITED)),
    Case("D08", n(Mode.PROHIBITED), n(Mode.OBLIGATORY)),
    # Deliberately unresolved cross-mode implications.
    Case("D09", n(Mode.OBLIGATORY), n(Mode.PERMITTED)),
    Case("D10", n(Mode.PERMITTED), n(Mode.OBLIGATORY)),
    Case("D11", n(Mode.PERMISSION_RESTRICTED_TO), n(Mode.PERMITTED)),
    Case("D12", n(Mode.PERMITTED), n(Mode.PERMISSION_RESTRICTED_TO)),
    # Subject/action substitution.
    Case("D13", n(Mode.PERMITTED), n(Mode.PERMITTED, subject=QA)),
    Case("D14", n(Mode.PERMITTED), n(Mode.PERMITTED, action=APPROVE)),
    # Exception scope.
    Case(
        "D15",
        n(Mode.PERMITTED, exceptions=(VENDOR,)),
        n(Mode.PERMITTED, exceptions=(VENDOR,)),
    ),
    Case(
        "D16",
        n(Mode.PERMITTED, exceptions=(VENDOR,)),
        n(Mode.PERMITTED, exceptions=(AUDITOR,)),
    ),
    Case("D17", n(Mode.PERMITTED, exceptions=(VENDOR,)), n(Mode.PERMITTED)),
    # Condition scope.
    Case(
        "D18",
        n(Mode.OBLIGATORY, condition=SIGNED),
        n(Mode.OBLIGATORY, condition=SIGNED),
    ),
    Case(
        "D19",
        n(Mode.OBLIGATORY, condition=SIGNED),
        n(Mode.OBLIGATORY, condition=VALIDATED),
    ),
    Case("D20", n(Mode.OBLIGATORY, condition=SIGNED), n(Mode.OBLIGATORY)),
    # Temporal scope.
    Case(
        "D21",
        n(Mode.PROHIBITED, temporal_relation="BEFORE", temporal_reference=AUDIT),
        n(Mode.PROHIBITED, temporal_relation="BEFORE", temporal_reference=AUDIT),
    ),
    Case(
        "D22",
        n(Mode.PROHIBITED, temporal_relation="BEFORE", temporal_reference=AUDIT),
        n(Mode.PROHIBITED, temporal_relation="AFTER", temporal_reference=AUDIT),
    ),
    Case(
        "D23",
        n(Mode.PROHIBITED, temporal_relation="BEFORE", temporal_reference=AUDIT),
        n(Mode.PROHIBITED, temporal_relation="BEFORE", temporal_reference=INSPECTION),
    ),
    Case(
        "D24",
        n(Mode.PROHIBITED, temporal_relation="BEFORE", temporal_reference=AUDIT),
        n(Mode.PROHIBITED),
    ),
    # Compound modifier binding.
    Case(
        "D25",
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            exceptions=(VENDOR,),
            condition=SIGNED,
            temporal_relation="UNTIL",
            temporal_reference=AUDIT,
        ),
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            exceptions=(VENDOR,),
            condition=SIGNED,
            temporal_relation="UNTIL",
            temporal_reference=AUDIT,
        ),
    ),
    Case(
        "D26",
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            exceptions=(VENDOR,),
            condition=SIGNED,
            temporal_relation="UNTIL",
            temporal_reference=AUDIT,
        ),
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            condition=SIGNED,
            temporal_relation="UNTIL",
            temporal_reference=AUDIT,
        ),
    ),
    Case(
        "D27",
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            exceptions=(VENDOR,),
            condition=SIGNED,
            temporal_relation="UNTIL",
            temporal_reference=AUDIT,
        ),
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            exceptions=(VENDOR,),
            temporal_relation="UNTIL",
            temporal_reference=AUDIT,
        ),
    ),
    Case(
        "D28",
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            exceptions=(VENDOR,),
            condition=SIGNED,
            temporal_relation="UNTIL",
            temporal_reference=AUDIT,
        ),
        n(
            Mode.PERMISSION_RESTRICTED_TO,
            exceptions=(VENDOR,),
            condition=SIGNED,
            temporal_relation="AFTER",
            temporal_reference=AUDIT,
        ),
    ),
    # Conflict semantics must survive modifiers.
    Case(
        "D29",
        n(Mode.PERMITTED, exceptions=(VENDOR,)),
        n(Mode.PROHIBITED, exceptions=(VENDOR,)),
    ),
    Case(
        "D30",
        n(Mode.OBLIGATORY, temporal_relation="AFTER", temporal_reference=AUDIT),
        n(Mode.PROHIBITED, temporal_relation="AFTER", temporal_reference=AUDIT),
    ),
    Case(
        "D31",
        n(Mode.OBLIGATORY, temporal_relation="AFTER", temporal_reference=AUDIT),
        n(Mode.PERMITTED, temporal_relation="AFTER", temporal_reference=AUDIT),
    ),
    Case(
        "D32",
        n(Mode.PERMISSION_RESTRICTED_TO, exceptions=(VENDOR,)),
        n(Mode.PERMITTED, exceptions=(VENDOR,)),
    ),
    # Additional direction/substitution sentinels.
    Case("D33", n(Mode.PROHIBITED, subject=QA), n(Mode.PROHIBITED, subject=QA)),
    Case("D34", n(Mode.PROHIBITED, subject=QA), n(Mode.PROHIBITED, subject=TECH)),
    Case("D35", n(Mode.OBLIGATORY, action=APPROVE), n(Mode.OBLIGATORY, action=APPROVE)),
    Case("D36", n(Mode.OBLIGATORY, action=APPROVE), n(Mode.OBLIGATORY, action=RELEASE)),
)


# Each pair changes exactly one intended semantic dimension and must change relation.
METAMORPHIC_PAIRS: tuple[tuple[str, str], ...] = (
    ("D01", "D05"),  # query mode PERMITTED -> PROHIBITED
    ("D07", "D09"),  # query PROHIBITED -> PERMITTED under OBLIGATORY source
    ("D04", "D11"),  # exact RESTRICTED_TO -> direct PERMITTED query
    ("D15", "D16"),  # exception identity
    ("D18", "D19"),  # condition identity
    ("D21", "D22"),  # temporal relation
    ("D21", "D23"),  # temporal reference
    ("D01", "D13"),  # subject
    ("D01", "D14"),  # action
    ("D25", "D26"),  # exception removal
    ("D25", "D27"),  # condition removal
    ("D25", "D28"),  # temporal relation under compound scope
)


CASE_BY_ID = {case.case_id: case for case in CASES}
assert len(CASE_BY_ID) == len(CASES)
