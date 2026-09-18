# ruff: noqa: I001
"""Narrow positive structural aperture in front of frozen PR #96 authority."""

import re
from dataclasses import dataclass

from research.cal_event_order_authority_rc0 import candidate as parent
from research.cal_measurement_envelope_rc0.envelope import AuditContext, MeasurementReceipt

_PAST = "reviewed|signed|inspected|released|approved|archived|processed|verified|recorded"
_BASE = "review|sign|inspect|release|approve|archive|process|verify|record"
_SUBJECT = r"[A-Z][A-Za-z0-9-]*"
_OBJECT = r"[A-Za-z0-9-]+(?:\s+[A-Za-z0-9-]+)?"

_POSITIVE = re.compile(
    rf"^(?P<subject>{_SUBJECT})\s+(?P<verb>{_PAST})\s+"
    rf"(?P<object>{_OBJECT})$",
    re.IGNORECASE,
)
_NEGATIVE = re.compile(
    rf"^(?P<subject>{_SUBJECT})\s+did\s+not\s+(?P<verb>{_BASE})\s+"
    rf"(?P<object>{_OBJECT})$",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class Eligibility:
    eligible: bool
    reason: str


def _event_side_allowed(text: str) -> bool:
    side = " ".join(text.strip().split())
    return _POSITIVE.fullmatch(side) is not None or _NEGATIVE.fullmatch(side) is not None


def eligibility(text: str) -> Eligibility:
    if not isinstance(text, str) or not text or text != text.strip():
        return Eligibility(False, "SURFACE_INVALID")
    body = text[:-1] if text.endswith(".") else text
    if "." in body:
        return Eligibility(False, "INTERNAL_SENTENCE_BOUNDARY")
    if any(not (char.isalnum() or char.isspace() or char == "-") for char in body):
        return Eligibility(False, "PUNCTUATION_OUTSIDE_APERTURE")
    cues = list(re.finditer(r"\b(before|after)\b", body, re.IGNORECASE))
    if len(cues) != 1:
        return Eligibility(False, "TEMPORAL_CUE_CARDINALITY")
    cue = cues[0]
    if not _event_side_allowed(body[: cue.start()]):
        return Eligibility(False, "LEFT_EVENT_OUTSIDE_APERTURE")
    if not _event_side_allowed(body[cue.end() :]):
        return Eligibility(False, "RIGHT_EVENT_OUTSIDE_APERTURE")
    return Eligibility(True, "DIRECT_EVENT_ORDER_ELIGIBLE")


def complete_event_order_atom(
    *,
    context: AuditContext,
    receipt: MeasurementReceipt,
    passage_id: str,
):
    passage = context.passage(passage_id)
    gate = eligibility(passage.passage_text)
    if not gate.eligible:
        raise parent.EventAuthorityRefusal(
            "STRUCTURAL_EVENT_APERTURE_REFUSED",
            gate.reason,
        )
    return parent.complete_event_order_atom(
        context=context,
        receipt=receipt,
        passage_id=passage_id,
    )


build_rc8j_case = parent.build_rc8j_case
WARRANTED_REASON = parent.WARRANTED_REASON
