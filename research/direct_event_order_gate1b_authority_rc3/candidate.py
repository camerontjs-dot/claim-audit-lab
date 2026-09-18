"""Argument-level coreference-safe event-order source completion for Gate-1B RC3."""

from __future__ import annotations

import re
from typing import Any

from claim_audit_lab.production_v1.semantic.authority import (
    AuthorityReceipt,
    AuthorityRefusal,
    SemanticAtom,
)
from claim_audit_lab.production_v1.semantic.measurements import (
    EVENT_INSTRUMENT_ID,
    EVENT_INSTRUMENT_VERSION,
    MeasurementReceipt,
    verify_measurement_receipt,
)
from claim_audit_lab.production_v1.semantic.models import (
    AuditContext,
    SemanticFamily,
    stable_id,
)

_PAST_TO_BASE = {
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

_PRONOUN_ARGUMENTS = frozenset(
    {
        "i",
        "me",
        "my",
        "mine",
        "you",
        "your",
        "yours",
        "he",
        "him",
        "his",
        "she",
        "her",
        "hers",
        "it",
        "its",
        "we",
        "us",
        "our",
        "ours",
        "they",
        "them",
        "their",
        "theirs",
        "this",
        "that",
        "these",
        "those",
    }
)


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip(" .,:;\"'")).casefold()


def _scope_guard(text: str) -> None:
    low = _norm(text)

    if re.search(
        r"\b(?:perhaps|maybe|possibly|allegedly|reportedly|purportedly|"
        r"supposedly|apparently)\b",
        low,
    ):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "epistemic or attribution wrapper is outside direct event-order authority",
        )

    if re.match(r"^if\b", low):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "conditional event-order wrapper is outside direct authority",
        )

    if re.search(r"\baccording\s+to\b", low):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "attributed event order is outside narrator authority",
        )

    if re.search(
        r"\bas\s+(?:reported|stated|claimed)\s+by\b",
        low,
    ):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "attributed event order is outside narrator authority",
        )

    if re.search(
        r"\b(?:not|immediately|shortly|just|directly)\s+(?:before|after)\b",
        low,
    ):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "temporal relation modifier is not represented by plain BEFORE/AFTER",
        )

    if re.search(r"\b(?:because|since)\b", low):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "causal residue is outside direct event-order authority",
        )


def _parse_event(text: str) -> dict[str, str]:
    segment = text.strip()
    subject = r"(?P<subject>[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?)"
    obj = r"(?P<object>[A-Za-z0-9-]+(?:\s+[A-Za-z0-9-]+){0,5})"

    negative = re.fullmatch(
        subject
        + r"\s+did\s+not\s+"
        + r"(?P<verb>review|sign|inspect|release|approve|archive|process|verify|record)\s+"
        + obj,
        segment,
    )
    if negative is not None:
        event = {
            "subject": _norm(negative.group("subject")),
            "predicate": negative.group("verb").casefold(),
            "object": _norm(negative.group("object")),
            "polarity": "negative",
        }
    else:
        positive = re.fullmatch(
            subject
            + r"\s+"
            + (
                r"(?P<verb>reviewed|signed|inspected|released|approved|archived|"
                r"processed|verified|recorded)\s+"
            )
            + obj,
            segment,
        )
        if positive is None:
            raise AuthorityRefusal(
                "SOURCE_COMPLETION_FAILED",
                "event side not independently reconstructable",
            )
        event = {
            "subject": _norm(positive.group("subject")),
            "predicate": _PAST_TO_BASE[positive.group("verb").casefold()],
            "object": _norm(positive.group("object")),
            "polarity": "positive",
        }

    argument_tokens = set(event["subject"].split()) | set(event["object"].split())
    if argument_tokens & _PRONOUN_ARGUMENTS:
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "event identity argument contains unresolved coreference",
        )
    return event


def _source_fields(text: str) -> dict[str, str]:
    _scope_guard(text)
    body = text.strip()
    if body.endswith("."):
        body = body[:-1]

    cues = list(re.finditer(r"\b(before|after)\b", body, re.IGNORECASE))
    if len(cues) != 1:
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "requires exactly one unmodified BEFORE/AFTER cue",
        )

    cue = cues[0]
    left = _parse_event(body[: cue.start()])
    right = _parse_event(body[cue.end() :])

    fields = {f"left_{key}": value for key, value in left.items()}
    fields["temporal_relation"] = cue.group(1).upper()
    fields.update({f"right_{key}": value for key, value in right.items()})
    return fields


def _measurement_fields(receipt: MeasurementReceipt) -> dict[str, str]:
    raw = receipt.raw_measurement()
    if raw.get("status") != "CLAIMED":
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            str(raw.get("status")),
        )
    proposals = raw.get("proposals")
    if (
        not isinstance(proposals, list)
        or len(proposals) != 1
        or not isinstance(proposals[0], dict)
    ):
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "one event-order proposal required",
        )

    proposal = proposals[0]
    left = proposal.get("left_event")
    right = proposal.get("right_event")
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "event proposal shape",
        )

    return {
        "left_subject": str(left.get("subject", "")),
        "left_predicate": str(left.get("predicate", "")),
        "left_object": str(left.get("object", "")),
        "left_polarity": str(left.get("polarity", "")),
        "temporal_relation": str(proposal.get("relation", "")),
        "right_subject": str(right.get("subject", "")),
        "right_predicate": str(right.get("predicate", "")),
        "right_object": str(right.get("object", "")),
        "right_polarity": str(right.get("polarity", "")),
    }


def complete_and_warrant_event_order_rc3(
    context: AuditContext,
    receipt: MeasurementReceipt,
    passage_id: str,
) -> AuthorityReceipt:
    try:
        verify_measurement_receipt(context, receipt)
    except ValueError as exc:
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            str(exc),
        ) from exc

    if context.proposition.semantic_family is not SemanticFamily.DIRECT_EVENT_ORDER:
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "proposition family mismatch",
        )
    if receipt.semantic_family is not SemanticFamily.DIRECT_EVENT_ORDER:
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "measurement family mismatch",
        )
    if (
        receipt.instrument_id != EVENT_INSTRUMENT_ID
        or receipt.instrument_version != EVENT_INSTRUMENT_VERSION
    ):
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "event instrument identity mismatch",
        )
    if receipt.consumed_passage_ids != (passage_id,):
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "authority requires exactly one named passage",
        )

    passage = context.evidence_world.passage(passage_id)
    measured = _measurement_fields(receipt)
    completed = _source_fields(passage.text)
    if measured != completed:
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "measurement semantics do not match independent source completion",
        )

    atom_material = {
        "semantic_family": receipt.semantic_family.value,
        "audit_context_sha256": context.context_sha256,
        "evidence_world_sha256": context.evidence_world.evidence_world_sha256,
        "passage_id": passage_id,
        "source_id": passage.source_id,
        "fields": completed,
        "measurement_receipt_id": receipt.receipt_id,
    }
    atom = SemanticAtom(
        atom_id=stable_id("semantic-atom", atom_material),
        semantic_family=receipt.semantic_family,
        audit_context_sha256=context.context_sha256,
        evidence_world_sha256=context.evidence_world.evidence_world_sha256,
        passage_id=passage_id,
        source_id=passage.source_id,
        fields=tuple(sorted(completed.items())),
        measurement_receipt_id=receipt.receipt_id,
    )
    authority_material: dict[str, Any] = {
        "atom_id": atom.atom_id,
        "audit_context_sha256": atom.audit_context_sha256,
        "evidence_world_sha256": atom.evidence_world_sha256,
        "status": "WARRANTED",
        "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
    }
    return AuthorityReceipt(
        authority_id=stable_id("semantic-authority", authority_material),
        audit_context_sha256=context.context_sha256,
        evidence_world_sha256=context.evidence_world.evidence_world_sha256,
        atom=atom,
    )
