"""Competing proposal instruments for Event Occurrence Measurement Machinery RC0."""

from __future__ import annotations

import importlib
import re
from typing import Any

from .cohort import EventAtom, Observation, Polarity, Status

_ACTORS = {"qa": "qa", "ops": "ops", "system": "system"}
_PAST_ACTIONS = {
    "approved": "approve",
    "released": "release",
    "signed": "sign",
    "recorded": "record",
}
_BASE_ACTIONS = set(_PAST_ACTIONS.values())
_OBJECTS = {"the batch": "batch", "the record": "record", "the event": "event", "batch": "batch"}


def _clean(text: str) -> str:
    return " ".join(text.strip().split()).removesuffix(".")


def _hard_hazard(text: str) -> str | None:
    low = text.casefold()
    if '"' in text or "'" in text and "approval" not in low:
        return "quotation scope"
    if re.search(r"\b(report|witness|study)\b.*\b(says?|said|reported|claims?)\b", low):
        return "reporting scope"
    if " may have " in f" {low} " or " might have " in f" {low} ":
        return "epistemic modality"
    if " must " in f" {low} " or " should " in f" {low} ":
        return "deontic surface"
    if " plans to " in f" {low} " or " intends to " in f" {low} ":
        return "intention surface"
    if " before " in f" {low} " or " after " in f" {low} ":
        return "event-order surface"
    if " documented" in low:
        return "documentation statement"
    if " or " in f" {low} " or " and " in f" {low} ":
        return "event composition"
    if re.fullmatch(r"The batch is approved", text, re.IGNORECASE):
        return "attribute-state neighbor"
    return None


def _event(
    actor: str,
    action: str,
    obj: str,
    polarity: Polarity = Polarity.OCCURRED,
    *,
    time: str | None = None,
) -> Observation:
    return Observation.claimed(EventAtom(actor, action, obj, polarity, time=time))


def direct_event_grammar(text: str) -> Observation:
    """Bounded active-voice event grammar with exact roles and polarity."""

    compact = _clean(text)
    hazard = _hard_hazard(compact)
    if hazard is not None:
        return Observation.unresolved(hazard)

    positive = re.fullmatch(
        r"(?P<actor>QA|Ops|System)\s+"
        r"(?P<verb>approved|released|signed|recorded)\s+"
        r"(?P<object>the batch|the record|the event)"
        r"(?:\s+at\s+(?P<time>T\d+))?",
        compact,
        re.IGNORECASE,
    )
    if positive is not None:
        return _event(
            _ACTORS[positive.group("actor").casefold()],
            _PAST_ACTIONS[positive.group("verb").casefold()],
            _OBJECTS[positive.group("object").casefold()],
            time=positive.group("time"),
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

    event_cue = r"\b(approve|approved|release|released|sign|signed|record|recorded)\b"
    if re.search(event_cue, compact, re.I):
        return Observation.unresolved("event cue outside bounded direct grammar")
    return Observation.not_applicable("no event cue")


_NLP: Any | None = None


def _nlp() -> Any:
    global _NLP
    if _NLP is None:
        spacy = importlib.import_module("spacy")
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def broad_dependency_event(text: str) -> Observation:
    """Broad event proposal path that exposes wrapper and composition hazards."""

    compact = _clean(text)
    direct = direct_event_grammar(compact)
    if direct.status is Status.CLAIMED:
        return direct

    passive = re.fullmatch(
        r"The batch was (?P<neg>not\s+)?approved by QA",
        compact,
        re.IGNORECASE,
    )
    if passive is not None:
        polarity = Polarity.DID_NOT_OCCUR if passive.group("neg") is not None else Polarity.OCCURRED
        return _event("qa", "approve", "batch", polarity)

    quarantine = re.fullmatch(r"QA quarantined the batch", compact, re.IGNORECASE)
    if quarantine is not None:
        return _event("qa", "quarantine", "batch")

    nominal = re.fullmatch(r"QA's approval of the batch occurred", compact, re.IGNORECASE)
    if nominal is not None:
        return _event("qa", "approve", "batch")

    log = re.fullmatch(r"Event:\s*QA approved batch", compact, re.IGNORECASE)
    if log is not None:
        return _event("qa", "approve", "batch")

    doc = _nlp()(compact)
    lemmas = {token.lemma_.casefold() for token in doc}
    low = compact.casefold()
    action: str | None = None
    for candidate in ("approve", "release", "sign", "record", "quarantine"):
        if candidate in lemmas or candidate in low:
            action = candidate
            break
    if action is not None and "qa" in low and "batch" in low:
        polarity = Polarity.DID_NOT_OCCUR if "did not" in low else Polarity.OCCURRED
        return _event("qa", action, "batch", polarity)

    return Observation.unresolved("broad event extractor found no bound event")


def _safe_extension_surface(text: str) -> bool:
    compact = _clean(text)
    patterns = (
        r"The batch was (?:not\s+)?approved by QA",
        r"QA quarantined the batch",
        r"QA's approval of the batch occurred",
        r"Event:\s*QA approved batch",
    )
    return any(re.fullmatch(pattern, compact, re.IGNORECASE) for pattern in patterns)


def conservative_event_hybrid(text: str) -> Observation:
    """Use dependency/open-vocabulary extraction only behind frozen safe surfaces."""

    direct = direct_event_grammar(text)
    if direct.status is Status.CLAIMED:
        return direct
    if _hard_hazard(_clean(text)) is not None:
        return direct
    if _safe_extension_surface(text):
        return broad_dependency_event(text)
    return direct


INSTRUMENTS = {
    "direct_event_grammar": direct_event_grammar,
    "broad_dependency_event": broad_dependency_event,
    "conservative_event_hybrid": conservative_event_hybrid,
}
