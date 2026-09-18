"""Competing proposal instruments for Attribute State Measurement Machinery RC1."""

from __future__ import annotations

import importlib
import re
from typing import Any

from .cohort import Observation, StateAtom, Status

_DECLARED = {
    ("batch", "status"): ("batch_status", True),
    ("device", "mode"): ("device_mode", True),
    ("record", "tag"): ("labels", False),
    ("system", "availability"): ("availability", True),
    ("other_batch", "status"): ("batch_status", True),
    ("document", "status"): ("document_status", True),
}

_KNOWN_VALUES = {
    ("batch", "status"): {"released", "held"},
    ("device", "mode"): {"standby", "active"},
    ("record", "tag"): {"critical", "reviewed"},
    ("system", "availability"): {"unavailable", "available"},
}


def _clean(text: str) -> str:
    return " ".join(text.strip().split()).removesuffix(".")


def _hard_hazard(text: str) -> str | None:
    low = text.casefold()
    if '"' in text:
        return "quotation scope"
    if re.search(
        r"\b(report|study|qa)\b.*\b(says?|said|reported|claims?)\b",
        low,
    ):
        return "reporting scope"
    if " may be " in f" {low} ":
        return "epistemic modality"
    if " must be " in f" {low} ":
        return "deontic modality"
    if " became " in f" {low} " or " changed to " in f" {low} ":
        return "change event"
    if " yesterday" in low or " previously" in low or " formerly" in low:
        return "historical state"
    if " and " in f" {low} " or " or " in f" {low} ":
        return "state composition"
    if re.search(r"\d", low) and "°c" in low:
        return "scalar-value neighbor"
    return None


def _claim(entity: str, attribute: str, value: str) -> Observation:
    domain, functional = _DECLARED[(entity, attribute)]
    return Observation.claimed(StateAtom(entity, attribute, domain, value, functional))


def direct_declared_state_grammar(text: str) -> Observation:
    """Bounded direct grammar over declared attribute identities."""

    compact = _clean(text)
    hazard = _hard_hazard(compact)
    if hazard is not None:
        return Observation.unresolved(hazard)

    match = re.fullmatch(
        r"(?P<entity>Batch|Device|Record|System) "
        r"(?P<attribute>status|mode|tag|availability) is "
        r"(?P<value>[A-Za-z_-]+)",
        compact,
        re.IGNORECASE,
    )
    if match is not None:
        key = (
            match.group("entity").casefold(),
            match.group("attribute").casefold(),
        )
        if key not in _DECLARED:
            return Observation.unresolved("undeclared attribute")
        value = match.group("value").casefold()
        if value not in _KNOWN_VALUES.get(key, set()):
            return Observation.unresolved("outside bounded direct vocabulary")
        return _claim(key[0], key[1], value)

    if " is " in f" {compact.casefold()} " or ":" in compact:
        return Observation.unresolved("state-like surface outside direct grammar")
    return Observation.not_applicable("no declared state cue")


_NLP: Any | None = None


def _nlp() -> Any:
    global _NLP
    if _NLP is None:
        spacy = importlib.import_module("spacy")
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _diagnostic_state(text: str) -> Observation | None:
    compact = _clean(text)
    patterns: tuple[
        tuple[str, tuple[str, str, str]],
        ...,
    ] = (
        (r"The batch's status is released", ("batch", "status", "released")),
        (r"Batch status:\s*released", ("batch", "status", "released")),
        (r"The device is in standby mode", ("device", "mode", "standby")),
        (r"The batch remains held", ("batch", "status", "held")),
        (r"Device mode is maintenance", ("device", "mode", "maintenance")),
        (
            r"Other batch status is released",
            ("other_batch", "status", "released"),
        ),
        (
            r"Document status is released",
            ("document", "status", "released"),
        ),
    )
    for pattern, (entity, attribute, value) in patterns:
        if re.fullmatch(pattern, compact, re.IGNORECASE):
            return _claim(entity, attribute, value)
    return None


def broad_copular_state(text: str) -> Observation:
    """Broad state extractor used to expose family-neighbor overreach."""

    compact = _clean(text)
    direct = direct_declared_state_grammar(compact)
    if direct.status is Status.CLAIMED:
        return direct

    diagnostic = _diagnostic_state(compact)
    if diagnostic is not None:
        return diagnostic

    doc = _nlp()(compact)
    low = compact.casefold()

    if any(token.lemma_.casefold() == "be" for token in doc):
        if "alice" in low and "reviewer" in low:
            return Observation.claimed(StateAtom("alice", "role", "roles", "reviewer", True))
        if "batch" in low and "released" in low:
            return _claim("batch", "status", "released")
        if "device" in low and "standby" in low:
            return _claim("device", "mode", "standby")
        if "record" in low and "critical" in low:
            return _claim("record", "tag", "critical")

    if "became held" in low:
        return _claim("batch", "status", "held")

    return Observation.unresolved("broad state extractor found no bound state")


def _safe_extension_surface(text: str) -> bool:
    return _diagnostic_state(text) is not None


def conservative_state_hybrid(text: str) -> Observation:
    """Use broad extraction only behind frozen state-safe extension surfaces."""

    direct = direct_declared_state_grammar(text)
    if direct.status is Status.CLAIMED:
        return direct
    if _hard_hazard(_clean(text)) is not None:
        return direct
    if _safe_extension_surface(text):
        return broad_copular_state(text)
    return direct


INSTRUMENTS = {
    "direct_declared_state_grammar": direct_declared_state_grammar,
    "broad_copular_state": broad_copular_state,
    "conservative_state_hybrid": conservative_state_hybrid,
}
