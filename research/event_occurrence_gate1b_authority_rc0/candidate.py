"""Independent source completion for bounded event-occurrence Gate-1B RC0."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from research.event_occurrence_measurement_machinery_rc0.cohort import (
    EventAtom,
    Polarity,
)


@dataclass(frozen=True, slots=True)
class EventOccurrenceAuthority:
    atom: EventAtom
    source_sha256: str
    status: str = "WARRANTED"


_ACTORS = {
    "qa": "qa",
    "ops": "ops",
    "system": "system",
}

_PAST = {
    "approved": "approve",
    "released": "release",
    "signed": "sign",
    "recorded": "record",
    "quarantined": "quarantine",
}

_OBJECTS = {
    "the batch": "batch",
    "the record": "record",
    "the event": "event",
    "batch": "batch",
}


def _clean(text: str) -> str:
    compact = " ".join(text.strip().split())
    return compact[:-1] if compact.endswith(".") else compact


def _event(
    actor: str,
    action: str,
    obj: str,
    polarity: Polarity = Polarity.OCCURRED,
    *,
    time: str | None = None,
) -> EventAtom:
    return EventAtom(
        actor=actor,
        action=action,
        object=obj,
        polarity=polarity,
        scope="NARRATOR",
        time=time,
    )


def _source_atom(text: str) -> EventAtom:
    compact = _clean(text)

    active = re.fullmatch(
        r"(?P<actor>QA|Ops|System)\s+"
        r"(?P<verb>approved|released|signed|recorded)\s+"
        r"(?P<object>the batch|the record|the event)"
        r"(?:\s+at\s+(?P<time>T\d+))?",
        compact,
        re.IGNORECASE,
    )
    if active is not None:
        return _event(
            _ACTORS[active.group("actor").casefold()],
            _PAST[active.group("verb").casefold()],
            _OBJECTS[active.group("object").casefold()],
            time=active.group("time"),
        )

    negative = re.fullmatch(
        r"(?P<actor>QA|Ops|System)\s+did\s+not\s+"
        r"(?P<verb>approve|release|sign|record)\s+"
        r"(?P<object>the batch|the record|the event)"
        r"(?:\s+at\s+(?P<time>T\d+))?",
        compact,
        re.IGNORECASE,
    )
    if negative is not None:
        return _event(
            _ACTORS[negative.group("actor").casefold()],
            negative.group("verb").casefold(),
            _OBJECTS[negative.group("object").casefold()],
            Polarity.DID_NOT_OCCUR,
            time=negative.group("time"),
        )

    passive = re.fullmatch(
        r"The batch was (?P<neg>not\s+)?approved by QA",
        compact,
        re.IGNORECASE,
    )
    if passive is not None:
        polarity = (
            Polarity.DID_NOT_OCCUR
            if passive.group("neg") is not None
            else Polarity.OCCURRED
        )
        return _event("qa", "approve", "batch", polarity)

    quarantine = re.fullmatch(
        r"QA quarantined the batch",
        compact,
        re.IGNORECASE,
    )
    if quarantine is not None:
        return _event("qa", "quarantine", "batch")

    nominal = re.fullmatch(
        r"QA's approval of the batch occurred",
        compact,
        re.IGNORECASE,
    )
    if nominal is not None:
        return _event("qa", "approve", "batch")

    event_log = re.fullmatch(
        r"Event:\s*QA approved batch",
        compact,
        re.IGNORECASE,
    )
    if event_log is not None:
        return _event("qa", "approve", "batch")

    raise ValueError("event occurrence source not independently reconstructable")


def complete_and_warrant_event_occurrence(
    text: str,
    measured: EventAtom,
) -> EventOccurrenceAuthority:
    completed = _source_atom(text)
    if completed != measured:
        raise ValueError("measurement/source semantic mismatch")
    return EventOccurrenceAuthority(
        atom=completed,
        source_sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
