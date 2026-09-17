"""Proposal-only typed claim compiler for CAL V1 RC0.

This module does not produce semantic authority, categorical relations, or verdicts.
It only proposes the exact typed target shape consumed by the existing Contract B
input boundary.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .semantic.models import SemanticFamily, TypedProposition, canonical_json_bytes, stable_id


class CompilerStatus(str, Enum):
    ESTABLISHED = "ESTABLISHED"
    AMBIGUOUS = "AMBIGUOUS"
    EXTRACTION_UNRESOLVED = "EXTRACTION_UNRESOLVED"
    OUT_OF_JURISDICTION = "OUT_OF_JURISDICTION"


@dataclass(frozen=True, slots=True)
class CompilerObservation:
    instrument_id: str
    semantic_family: SemanticFamily
    status: str
    fields: tuple[tuple[str, str], ...] = ()
    detail: str = ""

    @classmethod
    def candidate(
        cls,
        instrument_id: str,
        family: SemanticFamily,
        fields: dict[str, str],
    ) -> CompilerObservation:
        return cls(
            instrument_id=instrument_id,
            semantic_family=family,
            status="CANDIDATE",
            fields=tuple(sorted(fields.items())),
        )

    @classmethod
    def unresolved(
        cls, instrument_id: str, family: SemanticFamily, detail: str
    ) -> CompilerObservation:
        return cls(instrument_id, family, "UNRESOLVED", (), detail)

    @classmethod
    def not_applicable(
        cls, instrument_id: str, family: SemanticFamily
    ) -> CompilerObservation:
        return cls(instrument_id, family, "NOT_APPLICABLE")

    def field_map(self) -> dict[str, str]:
        return dict(self.fields)

    def as_material(self) -> dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "semantic_family": self.semantic_family.value,
            "status": self.status,
            "fields": dict(self.fields),
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class CompilerReceipt:
    receipt_id: str
    claim_id: str
    claim_text_sha256: str
    status: CompilerStatus
    observations: tuple[CompilerObservation, ...]
    proposition: TypedProposition | None = None

    def target(self) -> dict[str, Any] | None:
        if self.status is not CompilerStatus.ESTABLISHED or self.proposition is None:
            return None
        return {
            "claim_id": self.claim_id,
            "proposition": {
                "proposition_id": self.proposition.proposition_id,
                "text_sha256": self.proposition.text_sha256,
                "semantic_family": self.proposition.semantic_family.value,
                "fields": self.proposition.field_map(),
            },
        }

    def verify(self) -> None:
        material = _receipt_material(
            claim_id=self.claim_id,
            claim_text_sha256=self.claim_text_sha256,
            status=self.status,
            observations=self.observations,
            proposition=self.proposition,
        )
        if self.receipt_id != stable_id("claim-compiler", material):
            raise ValueError("compiler receipt identity mismatch")
        if self.status is CompilerStatus.ESTABLISHED:
            if self.proposition is None:
                raise ValueError("ESTABLISHED compiler receipt requires proposition")
            if self.proposition.proposition_id != self.claim_id:
                raise ValueError("compiler proposition_id mismatch")
            if self.proposition.text_sha256 != self.claim_text_sha256:
                raise ValueError("compiler proposition text hash mismatch")
        elif self.proposition is not None:
            raise ValueError("non-established compiler receipt must not carry proposition")


_REL = {
    "more": "MORE_THAN",
    "greater": "MORE_THAN",
    "higher": "MORE_THAN",
    "larger": "MORE_THAN",
    "exceeded": "MORE_THAN",
    "fewer": "LESS_THAN",
    "less": "LESS_THAN",
    "lower": "LESS_THAN",
    "smaller": "LESS_THAN",
    "trailed": "LESS_THAN",
}
_COMPARISON_CUES = tuple(_REL)
_ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
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
_BASE_VERBS = set(_PAST_TO_BASE.values())


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip(" .,:;\"'")).casefold()


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _leading_entity(tokens: list[str]) -> str | None:
    selected: list[str] = []
    for token in tokens[:2]:
        if token and token[0].isupper():
            selected.append(token)
        else:
            break
    if not selected:
        return None
    return _norm(" ".join(selected))


def _word_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9-]+", text)


def _comparison_regex(text: str) -> CompilerObservation:
    instrument = "cal-v1-claim-compiler-comparison-regex-v1"
    family = SemanticFamily.STRICT_COMPARISON
    compact = " ".join(text.strip().split())
    verb = re.fullmatch(
        rf"(?P<left>{_ENTITY})\s+(?P<rel>(?i:exceeded|trailed))\s+"
        rf"(?P<right>{_ENTITY})(?:\s+by\s+.+)?\.?",
        compact,
    )
    if verb is not None:
        return CompilerObservation.candidate(
            instrument,
            family,
            {
                "lhs_entity": _norm(verb.group("left")),
                "rhs_entity": _norm(verb.group("right")),
                "comparison_direction": _REL[verb.group("rel").casefold()],
            },
        )

    pattern = re.fullmatch(
        rf"(?P<left>{_ENTITY})\s+.+?\b"
        rf"(?P<rel>(?i:more|fewer|less|greater|higher|larger|lower|smaller))"
        rf"(?:\s+[A-Za-z0-9-]+){{0,3}}\s+than\s+(?P<right>{_ENTITY})\.?",
        compact,
    )
    if pattern is not None:
        return CompilerObservation.candidate(
            instrument,
            family,
            {
                "lhs_entity": _norm(pattern.group("left")),
                "rhs_entity": _norm(pattern.group("right")),
                "comparison_direction": _REL[pattern.group("rel").casefold()],
            },
        )
    if re.search(r"\b(" + "|".join(_COMPARISON_CUES) + r")\b", compact, re.I):
        return CompilerObservation.unresolved(
            instrument, family, "comparison cue without exact parse"
        )
    return CompilerObservation.not_applicable(instrument, family)


def _comparison_tokens(text: str) -> CompilerObservation:
    instrument = "cal-v1-claim-compiler-comparison-tokens-v1"
    family = SemanticFamily.STRICT_COMPARISON
    tokens = _word_tokens(text)
    lowered = [token.casefold() for token in tokens]
    cue_positions = [i for i, token in enumerate(lowered) if token in _REL]
    if not cue_positions:
        return CompilerObservation.not_applicable(instrument, family)
    if len(cue_positions) != 1:
        return CompilerObservation.unresolved(instrument, family, "multiple comparison cues")
    cue_i = cue_positions[0]
    cue = lowered[cue_i]
    left = _leading_entity(tokens)
    if left is None:
        return CompilerObservation.unresolved(instrument, family, "missing left entity")

    if cue in {"exceeded", "trailed"}:
        right_tokens = tokens[cue_i + 1 :]
    else:
        try:
            than_i = lowered.index("than", cue_i + 1)
        except ValueError:
            return CompilerObservation.unresolved(
                instrument, family, "comparison cue missing than"
            )
        right_tokens = tokens[than_i + 1 :]

    right = _leading_entity(right_tokens)
    if right is None:
        return CompilerObservation.unresolved(instrument, family, "missing right entity")
    return CompilerObservation.candidate(
        instrument,
        family,
        {
            "lhs_entity": left,
            "rhs_entity": right,
            "comparison_direction": _REL[cue],
        },
    )


def _event_side_regex(text: str) -> dict[str, str] | None:
    text = text.strip(" .")
    subject = r"(?P<subject>[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?)"
    obj = r"(?P<object>[A-Za-z0-9-]+(?:\s+[A-Za-z0-9-]+){0,5})"
    negative = re.fullmatch(
        subject
        + r"\s+(?i:did\s+not)\s+"
        + r"(?P<verb>(?i:review|sign|inspect|release|approve|archive|process|verify|record))\s+"
        + obj,
        text,
    )
    if negative is not None:
        return {
            "subject": _norm(negative.group("subject")),
            "predicate": negative.group("verb").casefold(),
            "object": _norm(negative.group("object")),
            "polarity": "negative",
        }
    positive = re.fullmatch(
        subject
        + r"\s+"
        + r"(?P<verb>(?i:reviewed|signed|inspected|released|approved|archived|processed|"
        + r"verified|recorded))\s+"
        + obj,
        text,
    )
    if positive is None:
        return None
    return {
        "subject": _norm(positive.group("subject")),
        "predicate": _PAST_TO_BASE[positive.group("verb").casefold()],
        "object": _norm(positive.group("object")),
        "polarity": "positive",
    }


def _event_fields(
    left: dict[str, str], relation: str, right: dict[str, str]
) -> dict[str, str]:
    return {
        "left_subject": left["subject"],
        "left_predicate": left["predicate"],
        "left_object": left["object"],
        "left_polarity": left["polarity"],
        "temporal_relation": relation,
        "right_subject": right["subject"],
        "right_predicate": right["predicate"],
        "right_object": right["object"],
        "right_polarity": right["polarity"],
    }


def _event_regex(text: str) -> CompilerObservation:
    instrument = "cal-v1-claim-compiler-event-regex-v1"
    family = SemanticFamily.DIRECT_EVENT_ORDER
    cues = list(re.finditer(r"\b(before|after)\b", text, re.I))
    if not cues:
        return CompilerObservation.not_applicable(instrument, family)
    if len(cues) != 1:
        return CompilerObservation.unresolved(instrument, family, "multiple temporal cues")
    cue = cues[0]
    left = _event_side_regex(text[: cue.start()])
    right = _event_side_regex(text[cue.end() :])
    if left is None or right is None:
        return CompilerObservation.unresolved(
            instrument, family, "temporal cue without two exact events"
        )
    return CompilerObservation.candidate(
        instrument, family, _event_fields(left, cue.group(1).upper(), right)
    )


def _event_side_tokens(tokens: list[str]) -> dict[str, str] | None:
    if len(tokens) < 3:
        return None
    subject_tokens: list[str] = []
    index = 0
    while index < min(2, len(tokens)) and tokens[index] and tokens[index][0].isupper():
        subject_tokens.append(tokens[index])
        index += 1
    if not subject_tokens:
        return None
    remainder = [token.casefold() for token in tokens[index:]]
    polarity = "positive"
    if (
        len(remainder) >= 3
        and remainder[:2] == ["did", "not"]
        and remainder[2] in _BASE_VERBS
    ):
        predicate = remainder[2]
        index += 3
        polarity = "negative"
    elif remainder and remainder[0] in _PAST_TO_BASE:
        predicate = _PAST_TO_BASE[remainder[0]]
        index += 1
    else:
        return None
    object_tokens = tokens[index:]
    if not object_tokens:
        return None
    return {
        "subject": _norm(" ".join(subject_tokens)),
        "predicate": predicate,
        "object": _norm(" ".join(object_tokens)),
        "polarity": polarity,
    }


def _event_tokens(text: str) -> CompilerObservation:
    instrument = "cal-v1-claim-compiler-event-tokens-v1"
    family = SemanticFamily.DIRECT_EVENT_ORDER
    tokens = _word_tokens(text)
    lowered = [token.casefold() for token in tokens]
    cue_positions = [i for i, token in enumerate(lowered) if token in {"before", "after"}]
    if not cue_positions:
        return CompilerObservation.not_applicable(instrument, family)
    if len(cue_positions) != 1:
        return CompilerObservation.unresolved(instrument, family, "multiple temporal cues")
    cue_i = cue_positions[0]
    left = _event_side_tokens(tokens[:cue_i])
    right = _event_side_tokens(tokens[cue_i + 1 :])
    if left is None or right is None:
        return CompilerObservation.unresolved(
            instrument, family, "temporal cue without two exact events"
        )
    return CompilerObservation.candidate(
        instrument, family, _event_fields(left, lowered[cue_i].upper(), right)
    )


def _candidate_key(
    observation: CompilerObservation,
) -> tuple[str, tuple[tuple[str, str], ...]]:
    return observation.semantic_family.value, observation.fields


def _resolve_observations(
    claim_id: str,
    claim_text: str,
    observations: tuple[CompilerObservation, ...],
) -> CompilerReceipt:
    candidates = [row for row in observations if row.status == "CANDIDATE"]
    unique_candidates = {_candidate_key(row) for row in candidates}
    unresolved = any(row.status == "UNRESOLVED" for row in observations)

    proposition: TypedProposition | None = None
    if len(unique_candidates) > 1:
        status = CompilerStatus.AMBIGUOUS
    elif len(unique_candidates) == 1:
        family_value, fields = next(iter(unique_candidates))
        matching = [
            row
            for row in candidates
            if row.semantic_family.value == family_value and row.fields == fields
        ]
        other_family_signal = any(
            row.semantic_family.value != family_value
            and row.status in {"CANDIDATE", "UNRESOLVED"}
            for row in observations
        )
        if len(matching) == 2 and not other_family_signal and not unresolved:
            status = CompilerStatus.ESTABLISHED
            proposition = TypedProposition.create(
                claim_id,
                SemanticFamily(family_value),
                dict(fields),
                text_sha256=_text_sha256(claim_text),
            )
        else:
            status = CompilerStatus.EXTRACTION_UNRESOLVED
    elif unresolved:
        status = CompilerStatus.EXTRACTION_UNRESOLVED
    else:
        status = CompilerStatus.OUT_OF_JURISDICTION

    claim_hash = _text_sha256(claim_text)
    material = _receipt_material(
        claim_id=claim_id,
        claim_text_sha256=claim_hash,
        status=status,
        observations=observations,
        proposition=proposition,
    )
    receipt = CompilerReceipt(
        receipt_id=stable_id("claim-compiler", material),
        claim_id=claim_id,
        claim_text_sha256=claim_hash,
        status=status,
        observations=observations,
        proposition=proposition,
    )
    receipt.verify()
    return receipt


def _receipt_material(
    *,
    claim_id: str,
    claim_text_sha256: str,
    status: CompilerStatus,
    observations: tuple[CompilerObservation, ...],
    proposition: TypedProposition | None,
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "claim_text_sha256": claim_text_sha256,
        "status": status.value,
        "observations": [row.as_material() for row in observations],
        "proposition": (
            None
            if proposition is None
            else {
                "proposition_id": proposition.proposition_id,
                "text_sha256": proposition.text_sha256,
                "semantic_family": proposition.semantic_family.value,
                "fields": proposition.field_map(),
                "proposition_sha256": proposition.sha256,
            }
        ),
    }


def compile_claim(claim_id: str, claim_text: str) -> CompilerReceipt:
    if not claim_id.strip():
        raise ValueError("claim_id must be non-empty")
    if not claim_text.strip():
        raise ValueError("claim_text must be non-empty")
    observations = (
        _comparison_regex(claim_text),
        _comparison_tokens(claim_text),
        _event_regex(claim_text),
        _event_tokens(claim_text),
    )
    return _resolve_observations(claim_id, claim_text, observations)


def canonical_target_bytes(receipt: CompilerReceipt) -> bytes:
    receipt.verify()
    target = receipt.target()
    if target is None:
        raise ValueError("compiler receipt is not established")
    return canonical_json_bytes(target) + b"\n"


__all__ = [
    "CompilerObservation",
    "CompilerReceipt",
    "CompilerStatus",
    "canonical_target_bytes",
    "compile_claim",
]
