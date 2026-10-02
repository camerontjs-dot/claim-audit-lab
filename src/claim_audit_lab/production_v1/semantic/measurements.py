from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

from .models import AuditContext, SemanticFamily, stable_id

STRICT_INSTRUMENT_ID = "rc7fb1-strict-comparison"
STRICT_INSTRUMENT_VERSION = "strict-comparison-polarity-rc0"
EVENT_INSTRUMENT_ID = "rc7fc-event-order"
EVENT_INSTRUMENT_VERSION = "rc7fc-event-order-1"


@dataclass(frozen=True, slots=True)
class MeasurementReceipt:
    receipt_id: str
    audit_context_sha256: str
    semantic_family: SemanticFamily
    instrument_id: str
    instrument_version: str
    available_passage_ids: tuple[str, ...]
    consumed_passage_ids: tuple[str, ...]
    raw_measurement_json: str
    diagnostics: tuple[tuple[str, str], ...] = ()

    def raw_measurement(self) -> dict[str, Any]:
        value: Any = json.loads(self.raw_measurement_json)
        if not isinstance(value, dict):
            raise ValueError("measurement payload must decode to an object")
        return cast(dict[str, Any], value)


def _make_receipt(
    *,
    context: AuditContext,
    family: SemanticFamily,
    instrument_id: str,
    instrument_version: str,
    consumed_passage_ids: tuple[str, ...],
    raw_measurement: Mapping[str, Any],
    diagnostics: Mapping[str, str] | None = None,
) -> MeasurementReceipt:
    available = tuple(passage.passage_id for passage in context.evidence_world.admitted_passages)
    if not set(consumed_passage_ids).issubset(set(available)):
        raise ValueError("measurement consumed passage outside admitted evidence world")
    raw_json = json.dumps(raw_measurement, sort_keys=True, separators=(",", ":"))
    diagnostic_items = tuple(sorted((diagnostics or {}).items()))
    material = {
        "audit_context_sha256": context.context_sha256,
        "semantic_family": family.value,
        "instrument_id": instrument_id,
        "instrument_version": instrument_version,
        "available_passage_ids": list(available),
        "consumed_passage_ids": list(consumed_passage_ids),
        "raw_measurement": raw_measurement,
        "diagnostics": dict(diagnostic_items),
    }
    return MeasurementReceipt(
        receipt_id=stable_id("measurement", material),
        audit_context_sha256=context.context_sha256,
        semantic_family=family,
        instrument_id=instrument_id,
        instrument_version=instrument_version,
        available_passage_ids=available,
        consumed_passage_ids=consumed_passage_ids,
        raw_measurement_json=raw_json,
        diagnostics=diagnostic_items,
    )


def verify_measurement_receipt(context: AuditContext, receipt: MeasurementReceipt) -> None:
    if receipt.audit_context_sha256 != context.context_sha256:
        raise ValueError("stale or foreign measurement context")
    expected = tuple(passage.passage_id for passage in context.evidence_world.admitted_passages)
    if receipt.available_passage_ids != expected:
        raise ValueError("measurement available-evidence aperture mismatch")
    material = {
        "audit_context_sha256": receipt.audit_context_sha256,
        "semantic_family": receipt.semantic_family.value,
        "instrument_id": receipt.instrument_id,
        "instrument_version": receipt.instrument_version,
        "available_passage_ids": list(receipt.available_passage_ids),
        "consumed_passage_ids": list(receipt.consumed_passage_ids),
        "raw_measurement": receipt.raw_measurement(),
        "diagnostics": dict(receipt.diagnostics),
    }
    if receipt.receipt_id != stable_id("measurement", material):
        raise ValueError("measurement receipt identity mismatch")


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip(" .,:;\"'")).casefold()


_ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
_MEASURE = r"share|rate|percentage|proportion|output|count|volume|score|yield"
_REL = {
    "more": "MORE_THAN",
    "fewer": "LESS_THAN",
    "less": "LESS_THAN",
    "greater": "MORE_THAN",
    "higher": "MORE_THAN",
    "larger": "MORE_THAN",
    "lower": "LESS_THAN",
    "smaller": "LESS_THAN",
}
# Refusal boundary for assertion polarity. Only one adjacent "did not" is a
# representable negative comparison. Every other overt marker fails closed.
_OVERT_NEGATION = re.compile(r"(?i)(?:n't|\b(?:not|never|no|without|neither|nor|cannot)\b)")


def _assertion_polarity(span: str) -> str | None:
    markers = list(_OVERT_NEGATION.finditer(span))
    if not markers:
        return "positive"
    if len(markers) == 1 and markers[0].group(0).casefold() == "not":
        preceding = span[: markers[0].start()].split()
        if preceding and preceding[-1].casefold() == "did":
            return "negative"
    return None


def _comparison_proposal(
    match: re.Match[str],
    *,
    relation: str,
    cue_group: str,
) -> dict[str, Any] | None:
    polarity = _assertion_polarity(match.string[match.end("left") : match.start(cue_group)])
    if polarity is None:
        return None
    return {
        "left": _norm(match.group("left")),
        "relation": relation,
        "right": _norm(match.group("right")),
        "assertion_polarity": polarity,
        "cue_span": list(match.span(cue_group)),
    }


def measure_strict_comparison(context: AuditContext, passage_id: str) -> MeasurementReceipt:
    passage = context.evidence_world.passage(passage_id)
    text = " ".join(passage.text.strip().split())
    proposal: dict[str, Any] | None = None
    unsafe_polarity = False
    patterns = (
        re.compile(
            rf"^(?P<left>{_ENTITY})\s+.+?,\s*(?P<delta>.+?)\s+"
            rf"(?P<rel>(?i:more|fewer|less))\s+than\s+(?P<right>{_ENTITY})\.?$"
        ),
        re.compile(
            rf"^(?P<left>{_ENTITY})\s+.+?(?:,\s*|\s+)(?:a\s+)?"
            rf"(?P<rel>(?i:greater|higher|larger|lower|smaller))\s+"
            rf"(?P<measure>(?i:{_MEASURE}))\s+than\s+(?P<right>{_ENTITY})\.?$"
        ),
        re.compile(
            rf"^(?P<left>{_ENTITY})\s+.+?\b"
            rf"(?P<rel>(?i:greater|higher|larger|lower|smaller))\s+than\s+"
            rf"(?P<right>{_ENTITY})\.?$"
        ),
    )
    for pattern in patterns:
        match = pattern.match(text)
        if match is None:
            continue
        proposal = _comparison_proposal(
            match,
            relation=_REL[match.group("rel").casefold()],
            cue_group="rel",
        )
        unsafe_polarity = proposal is None
        break
    if proposal is None and not unsafe_polarity:
        verb = re.match(
            rf"^(?P<left>{_ENTITY})\s+(?P<verb>(?i:exceeded|trailed))\s+"
            rf"(?P<right>{_ENTITY})(?:\s+by\s+.+)?\.?$",
            text,
        )
        if verb is not None:
            relation = "MORE_THAN" if verb.group("verb").casefold() == "exceeded" else "LESS_THAN"
            proposal = _comparison_proposal(verb, relation=relation, cue_group="verb")
            unsafe_polarity = proposal is None
    diagnostics: dict[str, str] | None = None
    if unsafe_polarity:
        raw: Mapping[str, Any] = {"status": "UNRESOLVED", "proposals": []}
        diagnostics = {"polarity": "unrepresentable"}
    elif proposal is None:
        status = (
            "UNRESOLVED"
            if re.search(
                r"\b(more|fewer|less|greater|higher|larger|lower|smaller|exceeded|trailed)\b",
                text,
                re.I,
            )
            else "NOT_APPLICABLE"
        )
        raw = {"status": status, "proposals": []}
    else:
        raw = {"status": "CLAIMED", "proposals": [proposal]}
    return _make_receipt(
        context=context,
        family=SemanticFamily.STRICT_COMPARISON,
        instrument_id=STRICT_INSTRUMENT_ID,
        instrument_version=STRICT_INSTRUMENT_VERSION,
        consumed_passage_ids=(passage_id,),
        raw_measurement=raw,
        diagnostics=diagnostics,
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


def _measurement_event_side(text: str) -> dict[str, str] | None:
    text = text.strip()
    subject = r"(?P<subject>[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?)"
    obj = r"(?P<object>[A-Za-z0-9-]+(?:\s+[A-Za-z0-9-]+){0,5})"
    negative = re.fullmatch(
        subject
        + r"\s+did\s+not\s+"
        + r"(?P<verb>review|sign|inspect|release|approve|archive|process|verify|record)\s+"
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
        + r"(?P<verb>reviewed|signed|inspected|released|approved|archived|processed|"
        + r"verified|recorded)\s+"
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


def measure_direct_event_order(context: AuditContext, passage_id: str) -> MeasurementReceipt:
    passage = context.evidence_world.passage(passage_id)
    text = passage.text.strip()
    cues = list(re.finditer(r"\b(before|after)\b", text, re.I))
    raw: Mapping[str, Any]
    if len(cues) != 1:
        raw = {
            "status": "NOT_APPLICABLE" if not cues else "UNRESOLVED",
            "proposals": [],
        }
    else:
        cue = cues[0]
        left = _measurement_event_side(text[: cue.start()])
        right_text = text[cue.end() :].strip()
        if right_text.endswith("."):
            right_text = right_text[:-1]
        right = _measurement_event_side(right_text)
        if left is None or right is None:
            raw = {"status": "UNRESOLVED", "proposals": []}
        else:
            raw = {
                "status": "CLAIMED",
                "proposals": [
                    {
                        "left_event": left,
                        "relation": cue.group(1).upper(),
                        "right_event": right,
                        "span": [cue.start(), cue.end()],
                    }
                ],
            }
    return _make_receipt(
        context=context,
        family=SemanticFamily.DIRECT_EVENT_ORDER,
        instrument_id=EVENT_INSTRUMENT_ID,
        instrument_version=EVENT_INSTRUMENT_VERSION,
        consumed_passage_ids=(passage_id,),
        raw_measurement=raw,
    )
