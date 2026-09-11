from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .measurements import (
    EVENT_INSTRUMENT_ID,
    EVENT_INSTRUMENT_VERSION,
    STRICT_INSTRUMENT_ID,
    STRICT_INSTRUMENT_VERSION,
    MeasurementReceipt,
    verify_measurement_receipt,
)
from .models import AuditContext, SemanticFamily, stable_id


@dataclass(frozen=True, slots=True)
class SemanticAtom:
    atom_id: str
    semantic_family: SemanticFamily
    audit_context_sha256: str
    evidence_world_sha256: str
    passage_id: str
    source_id: str
    fields: tuple[tuple[str, str], ...]
    measurement_receipt_id: str

    def field_map(self) -> dict[str, str]:
        return dict(self.fields)


@dataclass(frozen=True, slots=True)
class AuthorityReceipt:
    authority_id: str
    audit_context_sha256: str
    evidence_world_sha256: str
    atom: SemanticAtom
    status: str = "WARRANTED"
    reason: str = "ALL_REQUIRED_WARRANT_ESTABLISHED"


class AuthorityRefusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip(" .,:;\"'")).casefold()


def _strict_source_fields(text: str) -> dict[str, str]:
    entity = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
    patterns = (
        (
            rf"^(?P<left>{entity})\s+.+?,\s*.+?\s+"
            rf"(?P<rel>(?i:more|fewer|less))\s+than\s+(?P<right>{entity})\.?$",
            {"more": "MORE_THAN", "fewer": "LESS_THAN", "less": "LESS_THAN"},
        ),
        (
            rf"^(?P<left>{entity})\s+.+?\b"
            rf"(?P<rel>(?i:greater|higher|larger|lower|smaller))\b"
            rf"(?:\s+(?:share|rate|percentage|proportion|output|count|volume|score|yield))?"
            rf"\s+than\s+(?P<right>{entity})\.?$",
            {
                "greater": "MORE_THAN",
                "higher": "MORE_THAN",
                "larger": "MORE_THAN",
                "lower": "LESS_THAN",
                "smaller": "LESS_THAN",
            },
        ),
    )
    normalized = " ".join(text.strip().split())
    for pattern, relation_map in patterns:
        match = re.match(pattern, normalized)
        if match is not None:
            relation = relation_map[match.group("rel").casefold()]
            return {
                "left": _norm(match.group("left")),
                "relation": relation,
                "right": _norm(match.group("right")),
            }
    verb = re.match(
        rf"^(?P<left>{entity})\s+(?P<verb>(?i:exceeded|trailed))\s+"
        rf"(?P<right>{entity})(?:\s+by\s+.+)?\.?$",
        normalized,
    )
    if verb is not None:
        return {
            "left": _norm(verb.group("left")),
            "relation": (
                "MORE_THAN" if verb.group("verb").casefold() == "exceeded" else "LESS_THAN"
            ),
            "right": _norm(verb.group("right")),
        }
    raise AuthorityRefusal(
        "SOURCE_COMPLETION_FAILED",
        "strict comparison source not independently reconstructable",
    )


_REPORTING_WORDS = frozenset(
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
_BASE_VERBS = frozenset(_PAST_TO_BASE.values())


def _source_event_side(text: str) -> dict[str, str]:
    tokens = re.findall(r"[A-Za-z0-9-]+", text)
    if not tokens or any(token.casefold() in _REPORTING_WORDS for token in tokens):
        raise AuthorityRefusal("SOURCE_COMPLETION_FAILED", "reporting/scope surface refused")
    candidates: list[dict[str, str]] = []
    for index, token in enumerate(tokens):
        lower = token.casefold()
        if lower in _PAST_TO_BASE:
            subject = tokens[:index]
            obj = tokens[index + 1 :]
            if (
                1 <= len(subject) <= 2
                and 1 <= len(obj) <= 6
                and all(part[0].isupper() for part in subject)
            ):
                candidates.append(
                    {
                        "subject": _norm(" ".join(subject)),
                        "predicate": _PAST_TO_BASE[lower],
                        "object": _norm(" ".join(obj)),
                        "polarity": "positive",
                    }
                )
        if (
            lower == "did"
            and index + 2 < len(tokens)
            and tokens[index + 1].casefold() == "not"
            and tokens[index + 2].casefold() in _BASE_VERBS
        ):
            subject = tokens[:index]
            obj = tokens[index + 3 :]
            if (
                1 <= len(subject) <= 2
                and 1 <= len(obj) <= 6
                and all(part[0].isupper() for part in subject)
            ):
                candidates.append(
                    {
                        "subject": _norm(" ".join(subject)),
                        "predicate": tokens[index + 2].casefold(),
                        "object": _norm(" ".join(obj)),
                        "polarity": "negative",
                    }
                )
    if len(candidates) != 1:
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "requires exactly one supported event on each side",
        )
    return candidates[0]


def _event_source_fields(text: str) -> dict[str, str]:
    if not text or text != text.strip():
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED", "surface whitespace outside direct grammar"
        )
    body = text[:-1] if text.endswith(".") else text
    if any(not (char.isalnum() or char.isspace() or char == "-") for char in body):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED", "surface punctuation outside direct grammar"
        )
    cues = list(re.finditer(r"\b(before|after)\b", body, re.I))
    if len(cues) != 1:
        raise AuthorityRefusal("SOURCE_COMPLETION_FAILED", "requires exactly one before/after cue")
    cue = cues[0]
    left = _source_event_side(body[: cue.start()])
    right = _source_event_side(body[cue.end() :])
    fields = {f"left_{key}": value for key, value in left.items()}
    fields["temporal_relation"] = cue.group(1).upper()
    fields.update({f"right_{key}": value for key, value in right.items()})
    return fields


def _measurement_fields(receipt: MeasurementReceipt) -> dict[str, str]:
    raw = receipt.raw_measurement()
    if raw.get("status") != "CLAIMED":
        raise AuthorityRefusal("SEMANTIC_AUTHORITY_UNRESOLVED", str(raw.get("status")))
    proposals = raw.get("proposals")
    if not isinstance(proposals, list) or len(proposals) != 1 or not isinstance(proposals[0], dict):
        raise AuthorityRefusal("SEMANTIC_AUTHORITY_UNRESOLVED", "one proposal required")
    proposal = proposals[0]
    if receipt.semantic_family is SemanticFamily.STRICT_COMPARISON:
        try:
            return {
                "left": str(proposal["left"]),
                "relation": str(proposal["relation"]),
                "right": str(proposal["right"]),
            }
        except KeyError as exc:
            raise AuthorityRefusal(
                "SEMANTIC_AUTHORITY_UNRESOLVED", "comparison proposal shape"
            ) from exc
    if receipt.semantic_family is SemanticFamily.DIRECT_EVENT_ORDER:
        left = proposal.get("left_event")
        right = proposal.get("right_event")
        if not isinstance(left, dict) or not isinstance(right, dict):
            raise AuthorityRefusal("SEMANTIC_AUTHORITY_UNRESOLVED", "event proposal shape")
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
    raise AuthorityRefusal("SEMANTIC_AUTHORITY_UNRESOLVED", "unsupported family")


def complete_and_warrant(
    context: AuditContext, receipt: MeasurementReceipt, passage_id: str
) -> AuthorityReceipt:
    try:
        verify_measurement_receipt(context, receipt)
    except ValueError as exc:
        raise AuthorityRefusal("SEMANTIC_AUTHORITY_UNRESOLVED", str(exc)) from exc
    if receipt.consumed_passage_ids != (passage_id,):
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "authority requires exactly one named consumed passage",
        )
    passage = context.evidence_world.passage(passage_id)
    measured = _measurement_fields(receipt)
    if receipt.semantic_family is SemanticFamily.STRICT_COMPARISON:
        if (
            receipt.instrument_id != STRICT_INSTRUMENT_ID
            or receipt.instrument_version != STRICT_INSTRUMENT_VERSION
        ):
            raise AuthorityRefusal(
                "SEMANTIC_AUTHORITY_UNRESOLVED", "strict instrument identity mismatch"
            )
        completed = _strict_source_fields(passage.text)
    elif receipt.semantic_family is SemanticFamily.DIRECT_EVENT_ORDER:
        if (
            receipt.instrument_id != EVENT_INSTRUMENT_ID
            or receipt.instrument_version != EVENT_INSTRUMENT_VERSION
        ):
            raise AuthorityRefusal(
                "SEMANTIC_AUTHORITY_UNRESOLVED", "event instrument identity mismatch"
            )
        completed = _event_source_fields(passage.text)
    else:
        raise AuthorityRefusal("SEMANTIC_AUTHORITY_UNRESOLVED", "unsupported semantic family")
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
