"""Bounded event-order source completion and RC8J case construction.

Research-only. RC7F-C remains a measurement instrument. This module independently
reconstructs a narrow direct event-order atom from source text, requires exact
agreement with the measurement proposal, and only then constructs an RC8J case.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping

from research.cal_measurement_envelope_rc0.envelope import (
    AuditContext,
    EnvelopeRefusal,
    MeasurementReceipt,
    canonical_json_bytes,
    verify_measurement_receipt,
)

EVENT_FAMILY = "event_ordering"
EVENT_INSTRUMENT_ID = "rc7fc-event-order"
EVENT_INSTRUMENT_VERSION = "rc7fc-event-order-1"
WARRANTED_REASON = "ALL_REQUIRED_WARRANT_ESTABLISHED"

PAST_TO_BASE = {
    "reviewed": "review",
    "signed": "sign",
    "inspected": "inspect",
    "released": "release",
    "approved": "approve",
    "archived": "archive",
    "processed": "process",
    "verified": "verify",
    "recorded": "record",
}
BASE_VERBS = frozenset(PAST_TO_BASE.values())
REPORTING_WORDS = frozenset(
    {
        "according",
        "alleged",
        "allegedly",
        "author",
        "authors",
        "claim",
        "claimed",
        "claims",
        "report",
        "reported",
        "reports",
        "said",
        "says",
        "stated",
        "states",
        "study",
        "suggested",
        "suggests",
    }
)
REQUIRED_FIELDS = (
    "left_subject",
    "left_predicate",
    "left_object",
    "left_polarity",
    "temporal_relation",
    "right_subject",
    "right_predicate",
    "right_object",
    "right_polarity",
)


class EventAuthorityRefusal(ValueError):
    """Fail-closed event-authority refusal with a typed code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True, slots=True)
class _Token:
    surface: str
    start: int
    end: int

    @property
    def lower(self) -> str:
        return self.surface.casefold()


@dataclass(frozen=True, slots=True)
class ParsedEvent:
    subject: str
    predicate: str
    object: str
    polarity: str
    subject_span: tuple[int, int]
    predicate_span: tuple[int, int]
    object_span: tuple[int, int]
    polarity_span: tuple[int, int]
    event_span: tuple[int, int]

    def semantic_payload(self) -> dict[str, str]:
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "polarity": self.polarity,
        }


@dataclass(frozen=True, slots=True)
class ParsedEventOrder:
    left: ParsedEvent
    relation: str
    relation_span: tuple[int, int]
    right: ParsedEvent
    source_span: tuple[int, int]

    def flattened_fields(self) -> dict[str, str]:
        return {
            "left_subject": self.left.subject,
            "left_predicate": self.left.predicate,
            "left_object": self.left.object,
            "left_polarity": self.left.polarity,
            "temporal_relation": self.relation,
            "right_subject": self.right.subject,
            "right_predicate": self.right.predicate,
            "right_object": self.right.object,
            "right_polarity": self.right.polarity,
        }

    def field_spans(self) -> dict[str, tuple[int, int]]:
        return {
            "left_subject": self.left.subject_span,
            "left_predicate": self.left.predicate_span,
            "left_object": self.left.object_span,
            "left_polarity": self.left.polarity_span,
            "temporal_relation": self.relation_span,
            "right_subject": self.right.subject_span,
            "right_predicate": self.right.predicate_span,
            "right_object": self.right.object_span,
            "right_polarity": self.right.polarity_span,
        }


@dataclass(frozen=True, slots=True)
class EventOrderAtom:
    atom_id: str
    claim_id: str
    source_id: str
    bundle_id: str
    passage_id: str
    audit_context_sha256: str
    source_span: tuple[int, int]
    fields: dict[str, str]
    field_spans: dict[str, tuple[int, int]]
    measurement_receipt_id: str


def _stable_id(namespace: str, value: Any) -> str:
    digest = hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    return f"{namespace}:{digest}"


def _tokens(text: str) -> tuple[_Token, ...]:
    return tuple(
        _Token(match.group(0), match.start(), match.end())
        for match in re.finditer(r"[A-Za-z0-9-]+", text)
    )


def _direct_surface_allowed(text: str) -> bool:
    if not isinstance(text, str) or not text or text != text.strip():
        return False
    body = text[:-1] if text.endswith(".") else text
    if "." in body:
        return False
    for char in body:
        if not (char.isalnum() or char.isspace() or char == "-"):
            return False
    return bool(body.strip())


def _subject_ok(tokens: tuple[_Token, ...]) -> bool:
    return 1 <= len(tokens) <= 2 and all(
        token.surface and token.surface[0].isupper() for token in tokens
    )


def _normalize_tokens(tokens: tuple[_Token, ...]) -> str:
    return " ".join(token.lower for token in tokens)


def _parse_event_side(tokens: tuple[_Token, ...]) -> ParsedEvent | None:
    candidates: list[ParsedEvent] = []
    if not tokens or any(token.lower in REPORTING_WORDS for token in tokens):
        return None

    for index, token in enumerate(tokens):
        # Positive event: subject + frozen past verb + object.
        if token.lower in PAST_TO_BASE:
            subject_tokens = tokens[:index]
            object_tokens = tokens[index + 1 :]
            if not _subject_ok(subject_tokens) or not (1 <= len(object_tokens) <= 6):
                continue
            candidates.append(
                ParsedEvent(
                    subject=_normalize_tokens(subject_tokens),
                    predicate=PAST_TO_BASE[token.lower],
                    object=_normalize_tokens(object_tokens),
                    polarity="positive",
                    subject_span=(subject_tokens[0].start, subject_tokens[-1].end),
                    predicate_span=(token.start, token.end),
                    object_span=(object_tokens[0].start, object_tokens[-1].end),
                    polarity_span=(token.start, token.end),
                    event_span=(subject_tokens[0].start, object_tokens[-1].end),
                )
            )

        # Negative event: subject + did not + frozen base verb + object.
        if (
            token.lower == "did"
            and index + 2 < len(tokens)
            and tokens[index + 1].lower == "not"
            and tokens[index + 2].lower in BASE_VERBS
        ):
            subject_tokens = tokens[:index]
            object_tokens = tokens[index + 3 :]
            if not _subject_ok(subject_tokens) or not (1 <= len(object_tokens) <= 6):
                continue
            verb = tokens[index + 2]
            candidates.append(
                ParsedEvent(
                    subject=_normalize_tokens(subject_tokens),
                    predicate=verb.lower,
                    object=_normalize_tokens(object_tokens),
                    polarity="negative",
                    subject_span=(subject_tokens[0].start, subject_tokens[-1].end),
                    predicate_span=(verb.start, verb.end),
                    object_span=(object_tokens[0].start, object_tokens[-1].end),
                    polarity_span=(token.start, tokens[index + 1].end),
                    event_span=(subject_tokens[0].start, object_tokens[-1].end),
                )
            )

    if len(candidates) != 1:
        return None
    return candidates[0]


def parse_direct_event_order(text: str) -> ParsedEventOrder:
    """Independently reconstruct the narrow direct event-order grammar."""
    if not _direct_surface_allowed(text):
        raise EventAuthorityRefusal(
            "DIRECT_ASSERTION_GRAMMAR_REFUSED", "surface outside accepted direct grammar"
        )
    tokens = _tokens(text)
    cue_indices = [
        index for index, token in enumerate(tokens) if token.lower in {"before", "after"}
    ]
    if len(cue_indices) != 1:
        raise EventAuthorityRefusal(
            "DIRECT_ASSERTION_GRAMMAR_REFUSED", "requires exactly one before/after cue"
        )
    cue_index = cue_indices[0]
    left = _parse_event_side(tokens[:cue_index])
    right = _parse_event_side(tokens[cue_index + 1 :])
    if left is None or right is None:
        raise EventAuthorityRefusal(
            "DIRECT_ASSERTION_GRAMMAR_REFUSED", "could not reconstruct two direct events"
        )
    cue = tokens[cue_index]
    return ParsedEventOrder(
        left=left,
        relation=cue.lower.upper(),
        relation_span=(cue.start, cue.end),
        right=right,
        source_span=(0, len(text)),
    )


def _measurement_semantics(raw: Mapping[str, Any]) -> tuple[dict[str, str], tuple[int, int]]:
    if raw.get("status") != "CLAIMED":
        raise EventAuthorityRefusal("MEASUREMENT_NOT_CLAIMED", str(raw.get("status")))
    proposals = raw.get("proposals")
    if not isinstance(proposals, list) or len(proposals) != 1 or not isinstance(proposals[0], Mapping):
        raise EventAuthorityRefusal("MEASUREMENT_SHAPE_INVALID", "one proposal required")
    proposal = proposals[0]
    left = proposal.get("left_event")
    right = proposal.get("right_event")
    if not isinstance(left, Mapping) or not isinstance(right, Mapping):
        raise EventAuthorityRefusal("MEASUREMENT_SHAPE_INVALID", "event objects required")
    required_event = {"subject", "predicate", "object", "polarity"}
    if set(left) != required_event or set(right) != required_event:
        raise EventAuthorityRefusal("MEASUREMENT_SHAPE_INVALID", "unexpected event shape")
    relation = proposal.get("relation")
    if relation not in {"BEFORE", "AFTER"}:
        raise EventAuthorityRefusal("MEASUREMENT_SHAPE_INVALID", "unsupported relation")
    span = proposal.get("span")
    if (
        not isinstance(span, list)
        or len(span) != 2
        or not all(isinstance(item, int) and not isinstance(item, bool) for item in span)
    ):
        raise EventAuthorityRefusal("MEASUREMENT_SHAPE_INVALID", "cue span required")
    fields = {
        "left_subject": str(left["subject"]),
        "left_predicate": str(left["predicate"]),
        "left_object": str(left["object"]),
        "left_polarity": str(left["polarity"]),
        "temporal_relation": str(relation),
        "right_subject": str(right["subject"]),
        "right_predicate": str(right["predicate"]),
        "right_object": str(right["object"]),
        "right_polarity": str(right["polarity"]),
    }
    return fields, (span[0], span[1])


def complete_event_order_atom(
    *, context: AuditContext, receipt: MeasurementReceipt, passage_id: str
) -> EventOrderAtom:
    """Complete from source independently, then require exact measurement agreement."""
    try:
        verify_measurement_receipt(context=context, receipt=receipt)
    except EnvelopeRefusal as exc:
        raise EventAuthorityRefusal("MEASUREMENT_RECEIPT_INVALID", str(exc)) from exc
    if receipt.instrument_id != EVENT_INSTRUMENT_ID:
        raise EventAuthorityRefusal("INSTRUMENT_ID_MISMATCH", receipt.instrument_id)
    if receipt.instrument_version != EVENT_INSTRUMENT_VERSION:
        raise EventAuthorityRefusal("INSTRUMENT_VERSION_MISMATCH", receipt.instrument_version)
    if receipt.semantic_family != EVENT_FAMILY:
        raise EventAuthorityRefusal("MEASUREMENT_FAMILY_MISMATCH", receipt.semantic_family)
    if receipt.consumed_passage_ids != (passage_id,):
        raise EventAuthorityRefusal(
            "MEASUREMENT_APERTURE_MISMATCH", "event authority requires exactly one named passage"
        )

    passage = context.passage(passage_id)
    parsed = parse_direct_event_order(passage.passage_text)
    measured_fields, measured_cue_span = _measurement_semantics(receipt.raw_measurement)
    parsed_fields = parsed.flattened_fields()
    if measured_fields != parsed_fields:
        raise EventAuthorityRefusal(
            "MEASUREMENT_SOURCE_SEMANTIC_MISMATCH",
            json.dumps({"measured": measured_fields, "source": parsed_fields}, sort_keys=True),
        )
    if measured_cue_span != parsed.relation_span:
        raise EventAuthorityRefusal(
            "MEASUREMENT_SOURCE_SPAN_MISMATCH",
            f"{measured_cue_span!r} != {parsed.relation_span!r}",
        )

    material = {
        "profile": "cal-event-order-authority-rc0",
        "claim_id": context.proposition_id,
        "audit_context_sha256": context.context_sha256,
        "source_id": passage.source_id,
        "bundle_id": context.bundle_id,
        "passage_id": passage.passage_id,
        "source_span": list(parsed.source_span),
        "fields": parsed_fields,
        "field_spans": {
            field: list(span) for field, span in parsed.field_spans().items()
        },
        "measurement_receipt_id": receipt.receipt_id,
    }
    return EventOrderAtom(
        atom_id=_stable_id("event-atom", material),
        claim_id=context.proposition_id,
        source_id=passage.source_id,
        bundle_id=context.bundle_id,
        passage_id=passage.passage_id,
        audit_context_sha256=context.context_sha256,
        source_span=parsed.source_span,
        fields=parsed_fields,
        field_spans=parsed.field_spans(),
        measurement_receipt_id=receipt.receipt_id,
    )


def build_rc8j_case(*, atom: EventOrderAtom) -> dict[str, Any]:
    subject_id = _stable_id(
        "event-authority-subject",
        {
            "claim_id": atom.claim_id,
            "atom_id": atom.atom_id,
            "bundle_id": atom.bundle_id,
            "source_id": atom.source_id,
            "passage_id": atom.passage_id,
            "audit_context_sha256": atom.audit_context_sha256,
        },
    )
    warrants = {
        field: {
            "authority_subject_id": subject_id,
            "span": list(atom.field_spans[field]),
            "status": "established",
            "value": atom.fields[field],
        }
        for field in REQUIRED_FIELDS
    }
    return {
        "execution_state": "completed",
        "evidence_admitted": True,
        "authority_subject_id": subject_id,
        "raw_source_id": atom.source_id,
        "authority_subject_source_id": atom.source_id,
        "raw_bundle_id": atom.bundle_id,
        "authority_subject_bundle_id": atom.bundle_id,
        "raw_passage_id": atom.passage_id,
        "authority_subject_passage_id": atom.passage_id,
        "admitted_passage_span": list(atom.source_span),
        "raw_claim_id": atom.claim_id,
        "authority_subject_claim_id": atom.claim_id,
        "target_atom_id": atom.atom_id,
        "authority_subject_atom_id": atom.atom_id,
        "proposal": {
            "authority_subject_id": subject_id,
            "family": EVENT_FAMILY,
            "source_span": list(atom.source_span),
            "extra_modifiers": [],
            "fields": dict(atom.fields),
        },
        "assertion": {"authority_subject_id": subject_id, "state": "asserted"},
        "operator": {
            "authority_subject_id": subject_id,
            "domain": EVENT_FAMILY,
            "applicability": "applicable",
            "governed_span": list(atom.source_span),
            "jurisdiction_fields": list(REQUIRED_FIELDS),
        },
        "field_warrants": warrants,
        "required_fields": list(REQUIRED_FIELDS),
        "composition": {
            "authority_subject_id": subject_id,
            "required": False,
            "state": "not_required",
        },
        "aperture": {
            "authority_subject_id": subject_id,
            "required": False,
            "state": "not_required",
        },
    }


def weak_caller_stipulated_case(
    *, context: AuditContext, receipt: MeasurementReceipt, passage_id: str
) -> dict[str, Any]:
    """Deliberately weak control: trust measurement values and broad spans by fiat."""
    passage = context.passage(passage_id)
    fields, _ = _measurement_semantics(receipt.raw_measurement)
    atom_id = _stable_id(
        "weak-event-atom",
        {
            "claim_id": context.proposition_id,
            "source_id": passage.source_id,
            "bundle_id": context.bundle_id,
            "passage_id": passage.passage_id,
            "fields": fields,
        },
    )
    subject_id = _stable_id(
        "weak-event-authority-subject",
        {"claim_id": context.proposition_id, "atom_id": atom_id},
    )
    broad = [0, len(passage.passage_text)]
    return {
        "execution_state": "completed",
        "evidence_admitted": True,
        "authority_subject_id": subject_id,
        "raw_source_id": passage.source_id,
        "authority_subject_source_id": passage.source_id,
        "raw_bundle_id": context.bundle_id,
        "authority_subject_bundle_id": context.bundle_id,
        "raw_passage_id": passage.passage_id,
        "authority_subject_passage_id": passage.passage_id,
        "admitted_passage_span": broad,
        "raw_claim_id": context.proposition_id,
        "authority_subject_claim_id": context.proposition_id,
        "target_atom_id": atom_id,
        "authority_subject_atom_id": atom_id,
        "proposal": {
            "authority_subject_id": subject_id,
            "family": EVENT_FAMILY,
            "source_span": broad,
            "extra_modifiers": [],
            "fields": fields,
        },
        "assertion": {"authority_subject_id": subject_id, "state": "asserted"},
        "operator": {
            "authority_subject_id": subject_id,
            "domain": EVENT_FAMILY,
            "applicability": "applicable",
            "governed_span": broad,
            "jurisdiction_fields": list(REQUIRED_FIELDS),
        },
        "field_warrants": {
            field: {
                "authority_subject_id": subject_id,
                "span": broad,
                "status": "established",
                "value": value,
            }
            for field, value in fields.items()
        },
        "required_fields": list(REQUIRED_FIELDS),
        "composition": {
            "authority_subject_id": subject_id,
            "required": False,
            "state": "not_required",
        },
        "aperture": {
            "authority_subject_id": subject_id,
            "required": False,
            "state": "not_required",
        },
    }


__all__ = [
    "EVENT_FAMILY",
    "EVENT_INSTRUMENT_ID",
    "EVENT_INSTRUMENT_VERSION",
    "EventAuthorityRefusal",
    "EventOrderAtom",
    "ParsedEvent",
    "ParsedEventOrder",
    "REQUIRED_FIELDS",
    "WARRANTED_REASON",
    "build_rc8j_case",
    "complete_event_order_atom",
    "parse_direct_event_order",
    "weak_caller_stipulated_case",
]
