"""Adversarial hardening corpus for the frozen RC7F-C event-order instrument."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from research.event_ordering_measurement_rc7fc.event_order import measure


class Bucket(StrEnum):
    MUST_RETAIN = "MUST_RETAIN"
    DIAGNOSTIC = "DIAGNOSTIC"
    FAIL_CLOSED = "FAIL_CLOSED"


@dataclass(frozen=True, slots=True)
class Event:
    subject: str
    predicate: str
    object: str
    polarity: str = "positive"


@dataclass(frozen=True, slots=True)
class OrderAtom:
    left_event: Event
    relation: str
    right_event: Event


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    bucket: Bucket
    text: str
    expected: OrderAtom | None


def event(
    subject: str,
    predicate: str,
    obj: str,
    polarity: str = "positive",
) -> Event:
    return Event(subject.lower(), predicate, obj.lower(), polarity)


def order(left: Event, relation: str, right: Event) -> OrderAtom:
    return OrderAtom(left, relation, right)


CASES: tuple[Case, ...] = (
    Case(
        "EOM01",
        Bucket.MUST_RETAIN,
        "Talia reviewed packet u before Ravi signed ledger c.",
        order(event("Talia", "review", "packet u"), "BEFORE", event("Ravi", "sign", "ledger c")),
    ),
    Case(
        "EOM02",
        Bucket.MUST_RETAIN,
        "Talia reviewed packet u after Ravi signed ledger c.",
        order(event("Talia", "review", "packet u"), "AFTER", event("Ravi", "sign", "ledger c")),
    ),
    Case(
        "EOM03",
        Bucket.MUST_RETAIN,
        "Talia did not review packet u before Ravi signed ledger c.",
        order(
            event("Talia", "review", "packet u", "negative"),
            "BEFORE",
            event("Ravi", "sign", "ledger c"),
        ),
    ),
    Case(
        "EOM04",
        Bucket.MUST_RETAIN,
        "Talia reviewed packet u after Ravi did not sign ledger c.",
        order(
            event("Talia", "review", "packet u"),
            "AFTER",
            event("Ravi", "sign", "ledger c", "negative"),
        ),
    ),
    Case(
        "EOM05",
        Bucket.MUST_RETAIN,
        "The dashboard is blue. Talia reviewed packet u before Ravi signed ledger c.",
        order(event("Talia", "review", "packet u"), "BEFORE", event("Ravi", "sign", "ledger c")),
    ),
    Case(
        "EOD01",
        Bucket.DIAGNOSTIC,
        "Agent-1 reviewed packet u before Ravi signed ledger c.",
        order(event("Agent-1", "review", "packet u"), "BEFORE", event("Ravi", "sign", "ledger c")),
    ),
    Case(
        "EOD02",
        Bucket.DIAGNOSTIC,
        "Talia reviewed long packet alpha before Ravi verified release record beta.",
        order(
            event("Talia", "review", "long packet alpha"),
            "BEFORE",
            event("Ravi", "verify", "release record beta"),
        ),
    ),
    Case(
        "EOD03",
        Bucket.DIAGNOSTIC,
        "Talia archived dossier t after Ravi recorded ledger c.",
        order(event("Talia", "archive", "dossier t"), "AFTER", event("Ravi", "record", "ledger c")),
    ),
    Case(
        "EOF01",
        Bucket.FAIL_CLOSED,
        "The report says Talia reviewed packet u before Ravi signed ledger c.",
        None,
    ),
    Case(
        "EOF02",
        Bucket.FAIL_CLOSED,
        "Perhaps Talia reviewed packet u before Ravi signed ledger c.",
        None,
    ),
    Case(
        "EOF03",
        Bucket.FAIL_CLOSED,
        "If Talia reviewed packet u before Ravi signed ledger c.",
        None,
    ),
    Case(
        "EOF04",
        Bucket.FAIL_CLOSED,
        "Talia reviewed packet u not before Ravi signed ledger c.",
        None,
    ),
    Case(
        "EOF05",
        Bucket.FAIL_CLOSED,
        "Talia reviewed packet u immediately before Ravi signed ledger c.",
        None,
    ),
    Case(
        "EOF06",
        Bucket.FAIL_CLOSED,
        "Talia reviewed packet u shortly before Ravi signed ledger c.",
        None,
    ),
    Case(
        "EOF07",
        Bucket.FAIL_CLOSED,
        "Talia reviewed packet u before Ravi signed ledger c because QA requested it.",
        None,
    ),
    Case(
        "EOF08",
        Bucket.FAIL_CLOSED,
        "Talia reviewed packet u before Ravi signed ledger c and Ivo released form j.",
        None,
    ),
    Case(
        "EOF09",
        Bucket.FAIL_CLOSED,
        "Talia reviewed packet u before Ravi signed ledger c or Mona inspected batch w.",
        None,
    ),
    Case(
        "EOF10",
        Bucket.FAIL_CLOSED,
        "Talia reviewed packet u before Ravi signed ledger c after Mona inspected batch w.",
        None,
    ),
    Case(
        "EOF11",
        Bucket.FAIL_CLOSED,
        "Before 2025, the registry was empty.",
        None,
    ),
    Case(
        "EOF12",
        Bucket.FAIL_CLOSED,
        "After lunch, the office reopened.",
        None,
    ),
)


def _event_from_raw(raw: dict) -> Event:
    return Event(
        subject=raw["subject"],
        predicate=raw["predicate"],
        object=raw["object"],
        polarity=raw["polarity"],
    )


def observe(text: str) -> OrderAtom | None:
    result = measure(text)
    if result["status"] != "CLAIMED":
        return None
    proposals = result["proposals"]
    if len(proposals) != 1:
        raise AssertionError(f"unexpected proposal cardinality: {len(proposals)}")
    proposal = proposals[0]
    return OrderAtom(
        left_event=_event_from_raw(proposal["left_event"]),
        relation=proposal["relation"],
        right_event=_event_from_raw(proposal["right_event"]),
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
