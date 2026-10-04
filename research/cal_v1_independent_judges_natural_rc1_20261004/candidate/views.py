"""Private parse of one string. Nothing in here reads another lane's output."""

from __future__ import annotations

import re
from typing import Any

_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_NUMBER = re.compile(
    r"(?P<sign>-)?(?P<number>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d+)\s*(?P<unit>million|billion|trillion|percent|%)?"
)
_QUANTIFIER = re.compile(r"\b(all|some|every|most|each)\b", re.IGNORECASE)
_HEDGE = re.compile(r"\b(alleged|reportedly|projected|projection|according to)\b", re.IGNORECASE)
_NEGATION = re.compile(r"\b(not|no|never|n't)\b", re.IGNORECASE)

_DECREASE = (
    "edged down",
    "decreased",
    "decreasing",
    "decrease",
    "declined",
    "declining",
    "dropped",
    "dropping",
    "fell",
    "falling",
    "lower",
    "fewer",
    "reduced",
    "reduction",
)
_INCREASE = (
    "edged up",
    "increased",
    "increasing",
    "increase",
    "grew",
    "growing",
    "higher",
    "greater",
    "rose",
    "rising",
)
_UNCHANGED = ("unchanged", "no change", "was flat")
# Bare up/down govern a quantity only when a digit follows. "drop" is the
# bare form of dropped; the longer forms are matched first and consume the span.
_EXTRA_CUES = (
    (re.compile(r"\bdrop\b"), "decrease"),
    (re.compile(r"\bup(?=\s+\d)"), "increase"),
    (re.compile(r"\bdown(?=\s+\d)"), "decrease"),
)
_GAP = re.compile(
    r"^(?:[\s,]+|by|of|a|an|to|from|percent|%|million|billion|trillion)*$",
    re.IGNORECASE,
)


def _unit(raw: str | None) -> str:
    if not raw:
        return ""
    if raw == "%":
        return "percent"
    return raw


def _cues(text: str) -> list[dict[str, Any]]:
    lowered = text.casefold()
    phrases = (
        [(phrase, "unchanged") for phrase in _UNCHANGED]
        + [(phrase, "decrease") for phrase in _DECREASE]
        + [(phrase, "increase") for phrase in _INCREASE]
    )
    phrases.sort(key=lambda item: len(item[0]), reverse=True)
    patterns = [(re.compile(rf"\b{re.escape(phrase)}\b"), label) for phrase, label in phrases]
    patterns.extend(_EXTRA_CUES)
    found: list[tuple[int, int, str]] = []
    for pattern, label in patterns:
        for match in pattern.finditer(lowered):
            found.append((match.start(), match.end(), label))
    found.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    chosen: list[dict[str, Any]] = []
    last_end = -1
    for start, end, label in found:
        if start < last_end:
            continue
        polarity = "negative" if _NEGATION.search(lowered[:start][-40:]) else "positive"
        chosen.append({"start": start, "end": end, "direction": label, "polarity": polarity})
        last_end = end
    return chosen


def _governing_cue(start: int, end: int, cues: list[dict[str, Any]], text: str) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_distance: int | None = None
    for cue in cues:
        if cue["end"] <= start:
            gap = text[cue["end"]:start]
            distance = start - cue["end"]
        elif cue["start"] >= end:
            gap = text[end:cue["start"]]
            distance = cue["start"] - end
        else:
            continue
        if re.search(r"\d", gap) or _GAP.fullmatch(gap) is None:
            continue
        if best_distance is None or distance < best_distance:
            best = cue
            best_distance = distance
    return best


def _numbers(text: str, cues: list[dict[str, Any]]) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for match in _NUMBER.finditer(text):
        number = match.group("number").replace(",", "")
        if "." in number:
            number = number.rstrip("0").rstrip(".")
        cue = _governing_cue(match.start(), match.end(), cues, text)
        found.append(
            {
                "number": number,
                "unit": _unit(match.group("unit")),
                "sign": "-" if match.group("sign") else "",
                "direction": None if cue is None else str(cue["direction"]),
                "polarity": None if cue is None else str(cue["polarity"]),
            }
        )
    return found


def parse_view(text: str) -> dict[str, Any]:
    cues = _cues(text)
    numbers = _numbers(text, cues)
    attached = {
        (item["direction"], item["polarity"])
        for item in numbers
        if item["direction"] is not None
    }
    if len(attached) == 1:
        direction, polarity = next(iter(attached))
    elif len(cues) == 1 and not attached:
        direction, polarity = str(cues[0]["direction"]), str(cues[0]["polarity"])
    else:
        direction, polarity = None, None
    return {
        "years": _YEAR.findall(text),
        "numbers": numbers,
        "direction": direction,
        "polarity": polarity,
        "quantifiers": [item.casefold() for item in _QUANTIFIER.findall(text)],
        "hedges": [item.casefold() for item in _HEDGE.findall(text)],
    }
