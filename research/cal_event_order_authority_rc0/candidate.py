"""Decisive event-order authority candidate wrapper.

Adds the pre-science one-event-per-side aperture check recorded in
DEVELOPMENT_NOTES.md, then delegates exact completion/case construction to the
frozen candidate implementation in event_authority.py.
"""
from __future__ import annotations

import re

from research.cal_measurement_envelope_rc0.envelope import AuditContext, MeasurementReceipt

from . import event_authority as base

EVENT_FAMILY = base.EVENT_FAMILY
EVENT_INSTRUMENT_ID = base.EVENT_INSTRUMENT_ID
EVENT_INSTRUMENT_VERSION = base.EVENT_INSTRUMENT_VERSION
EventAuthorityRefusal = base.EventAuthorityRefusal
EventOrderAtom = base.EventOrderAtom
REQUIRED_FIELDS = base.REQUIRED_FIELDS
WARRANTED_REASON = base.WARRANTED_REASON
build_rc8j_case = base.build_rc8j_case
weak_caller_stipulated_case = base.weak_caller_stipulated_case


def _event_construction_count(text: str) -> int:
    words = [match.group(0).casefold() for match in re.finditer(r"[A-Za-z0-9-]+", text)]
    count = sum(word in base.PAST_TO_BASE for word in words)
    count += sum(
        1
        for index in range(len(words) - 2)
        if words[index] == "did"
        and words[index + 1] == "not"
        and words[index + 2] in base.BASE_VERBS
    )
    return count


def _require_one_event_per_side(text: str) -> None:
    tokens = list(re.finditer(r"\b(before|after)\b", text, re.IGNORECASE))
    if len(tokens) != 1:
        raise EventAuthorityRefusal(
            "DIRECT_ASSERTION_GRAMMAR_REFUSED",
            "requires exactly one temporal cue before event counting",
        )
    cue = tokens[0]
    left_count = _event_construction_count(text[: cue.start()])
    right_count = _event_construction_count(text[cue.end() :])
    if left_count != 1 or right_count != 1:
        raise EventAuthorityRefusal(
            "DIRECT_ASSERTION_GRAMMAR_REFUSED",
            f"requires exactly one supported event per side; observed {left_count}/{right_count}",
        )


def parse_direct_event_order(text: str) -> base.ParsedEventOrder:
    _require_one_event_per_side(text)
    return base.parse_direct_event_order(text)


def complete_event_order_atom(
    *, context: AuditContext, receipt: MeasurementReceipt, passage_id: str
) -> EventOrderAtom:
    passage = context.passage(passage_id)
    _require_one_event_per_side(passage.passage_text)
    return base.complete_event_order_atom(
        context=context,
        receipt=receipt,
        passage_id=passage_id,
    )


__all__ = [
    "EVENT_FAMILY",
    "EVENT_INSTRUMENT_ID",
    "EVENT_INSTRUMENT_VERSION",
    "EventAuthorityRefusal",
    "EventOrderAtom",
    "REQUIRED_FIELDS",
    "WARRANTED_REASON",
    "build_rc8j_case",
    "complete_event_order_atom",
    "parse_direct_event_order",
    "weak_caller_stipulated_case",
]
