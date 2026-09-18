"""Independent source completion for bounded deontic Gate-1B RC0."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from research.deontic_measurement_machinery_rc0.cohort import (
    APPROVE_RECORD,
    ARCHIVE_RECORD,
    CONTRACTORS,
    QA,
    QA_APPROVES,
    QA_SIGNS,
    RELEASE_BATCH,
    TECH,
    Mode,
    Norm,
)


@dataclass(frozen=True, slots=True)
class DeonticAuthority:
    norm: Norm
    source_sha256: str
    status: str = "WARRANTED"


_SUBJECTS = {
    "qualified technicians": TECH,
    "qa": QA,
}

_ACTIONS = {
    "release the batch": RELEASE_BATCH,
    "approve the record": APPROVE_RECORD,
    "archive the record": ARCHIVE_RECORD,
}

_GERUNDS = {
    "releasing the batch": RELEASE_BATCH,
    "approving the record": APPROVE_RECORD,
    "archiving the record": ARCHIVE_RECORD,
}


def _clean(text: str) -> str:
    compact = " ".join(text.strip().split())
    return compact[:-1] if compact.endswith(".") else compact


def _split_modifiers(
    text: str,
) -> tuple[str, tuple[str, ...], str | None, str | None, str | None]:
    body = text
    exceptions: tuple[str, ...] = ()
    condition: str | None = None
    temporal_relation: str | None = None
    temporal_reference: str | None = None

    exception = re.search(r"\s+except\s+contractors$", body, re.IGNORECASE)
    if exception is not None:
        exceptions = (CONTRACTORS,)
        body = body[: exception.start()]

    condition_match = re.search(
        r"\s+if\s+QA\s+approves$",
        body,
        re.IGNORECASE,
    )
    if condition_match is not None:
        condition = QA_APPROVES
        body = body[: condition_match.start()]

    temporal = re.search(
        r"\s+(after|before)\s+QA\s+signs$",
        body,
        re.IGNORECASE,
    )
    if temporal is not None:
        temporal_relation = temporal.group(1).upper()
        temporal_reference = QA_SIGNS
        body = body[: temporal.start()]

    return (
        body,
        exceptions,
        condition,
        temporal_relation,
        temporal_reference,
    )


def _norm(
    mode: Mode,
    subject: str,
    action: str,
    *,
    exceptions: tuple[str, ...],
    condition: str | None,
    temporal_relation: str | None,
    temporal_reference: str | None,
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


def _source_norm(text: str) -> Norm:
    compact = _clean(text)
    (
        body,
        exceptions,
        condition,
        temporal_relation,
        temporal_reference,
    ) = _split_modifiers(compact)

    restricted = re.fullmatch(
        r"Only\s+(?P<subject>Qualified technicians)\s+may\s+"
        r"(?P<action>release the batch|approve the record|archive the record)",
        body,
        re.IGNORECASE,
    )
    if restricted is not None:
        return _norm(
            Mode.PERMISSION_RESTRICTED_TO,
            _SUBJECTS[restricted.group("subject").casefold()],
            _ACTIONS[restricted.group("action").casefold()],
            exceptions=exceptions,
            condition=condition,
            temporal_relation=temporal_relation,
            temporal_reference=temporal_reference,
        )

    modal = re.fullmatch(
        r"(?P<subject>Qualified technicians|QA)\s+"
        r"(?P<modal>may|must not|must)\s+"
        r"(?P<action>release the batch|approve the record|archive the record)",
        body,
        re.IGNORECASE,
    )
    if modal is not None:
        mode = {
            "may": Mode.PERMITTED,
            "must not": Mode.PROHIBITED,
            "must": Mode.OBLIGATORY,
        }[modal.group("modal").casefold()]
        return _norm(
            mode,
            _SUBJECTS[modal.group("subject").casefold()],
            _ACTIONS[modal.group("action").casefold()],
            exceptions=exceptions,
            condition=condition,
            temporal_relation=temporal_relation,
            temporal_reference=temporal_reference,
        )

    permitted = re.fullmatch(
        r"(?P<subject>Qualified technicians|QA)\s+are\s+permitted\s+to\s+"
        r"(?P<action>release the batch|approve the record|archive the record)",
        body,
        re.IGNORECASE,
    )
    if permitted is not None:
        return _norm(
            Mode.PERMITTED,
            _SUBJECTS[permitted.group("subject").casefold()],
            _ACTIONS[permitted.group("action").casefold()],
            exceptions=exceptions,
            condition=condition,
            temporal_relation=temporal_relation,
            temporal_reference=temporal_reference,
        )

    prohibited = re.fullmatch(
        r"(?P<subject>Qualified technicians|QA)\s+are\s+prohibited\s+from\s+"
        r"(?P<action>releasing the batch|approving the record|archiving the record)",
        body,
        re.IGNORECASE,
    )
    if prohibited is not None:
        return _norm(
            Mode.PROHIBITED,
            _SUBJECTS[prohibited.group("subject").casefold()],
            _GERUNDS[prohibited.group("action").casefold()],
            exceptions=exceptions,
            condition=condition,
            temporal_relation=temporal_relation,
            temporal_reference=temporal_reference,
        )

    required = re.fullmatch(
        r"(?P<subject>Qualified technicians|QA)\s+are\s+required\s+to\s+"
        r"(?P<action>release the batch|approve the record|archive the record)",
        body,
        re.IGNORECASE,
    )
    if required is not None:
        return _norm(
            Mode.OBLIGATORY,
            _SUBJECTS[required.group("subject").casefold()],
            _ACTIONS[required.group("action").casefold()],
            exceptions=exceptions,
            condition=condition,
            temporal_relation=temporal_relation,
            temporal_reference=temporal_reference,
        )

    raise ValueError("deontic source not independently reconstructable")


def complete_and_warrant_deontic(text: str, measured: Norm) -> DeonticAuthority:
    completed = _source_norm(text)
    if completed != measured:
        raise ValueError("measurement/source semantic mismatch")
    return DeonticAuthority(
        norm=completed,
        source_sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
