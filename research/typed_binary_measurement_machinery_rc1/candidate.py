"""Competing proposal instruments for Typed Binary Relation Measurement Machinery RC1."""

from __future__ import annotations

import re

from .cohort import Observation, RelationAtom, Status


def _clean(text: str) -> str:
    return " ".join(text.strip().split()).removesuffix(".")


def _hard_hazard(text: str) -> str | None:
    low = text.casefold()
    if re.search(
        r"\b(report|study|article)\b.*\b(says?|said|reported|claims?)\b",
        low,
    ):
        return "reporting scope"
    if " may " in f" {low} " or " might " in f" {low} ":
        return "epistemic modality"
    if " and " in f" {low} " or " or " in f" {low} ":
        return "relation composition"
    if ", so " in low or " therefore " in low:
        return "inferred relation"
    if re.search(r"\b\d+(?:\.\d+)?\s*m\s+north of\b", low):
        return "metric geometry"
    return None


def _claim(
    subject: str,
    predicate: str,
    obj: str,
    positive: bool = True,
) -> Observation:
    return Observation.claimed(
        RelationAtom(subject.casefold(), predicate, obj.casefold(), positive)
    )


def direct_relation_grammar(text: str) -> Observation:
    """Bounded grammar over the closed Gate-0 predicate inventory."""

    compact = _clean(text)
    hazard = _hard_hazard(compact)
    if hazard is not None:
        return Observation.unresolved(hazard)

    owns = re.fullmatch(
        r"(?P<subject>A|B) owns (?P<object>A|B)",
        compact,
        re.IGNORECASE,
    )
    if owns is not None:
        return _claim(owns.group("subject"), "OWNS", owns.group("object"))

    not_owns = re.fullmatch(
        r"(?P<subject>A|B) does not own (?P<object>A|B)",
        compact,
        re.IGNORECASE,
    )
    if not_owns is not None:
        return _claim(
            not_owns.group("subject"),
            "OWNS",
            not_owns.group("object"),
            False,
        )

    owned_by = re.fullmatch(
        r"(?P<subject>A|B) is owned by (?P<object>A|B)",
        compact,
        re.IGNORECASE,
    )
    if owned_by is not None:
        return _claim(
            owned_by.group("subject"),
            "OWNED_BY",
            owned_by.group("object"),
        )

    adjacent = re.fullmatch(
        r"(?P<subject>A|B) is adjacent to (?P<object>A|B)",
        compact,
        re.IGNORECASE,
    )
    if adjacent is not None:
        return _claim(
            adjacent.group("subject"),
            "ADJACENT_TO",
            adjacent.group("object"),
        )

    north = re.fullmatch(
        r"(?P<subject>A|B) is north of (?P<object>A|B)",
        compact,
        re.IGNORECASE,
    )
    if north is not None:
        return _claim(
            north.group("subject"),
            "NORTH_OF",
            north.group("object"),
        )

    south = re.fullmatch(
        r"(?P<subject>A|B) is south of (?P<object>A|B)",
        compact,
        re.IGNORECASE,
    )
    if south is not None:
        return _claim(
            south.group("subject"),
            "SOUTH_OF",
            south.group("object"),
        )

    inside = re.fullmatch(
        r"(?P<subject>Room) is in (?P<object>Zone)",
        compact,
        re.IGNORECASE,
    )
    if inside is not None:
        return _claim(
            inside.group("subject"),
            "IN",
            inside.group("object"),
        )

    contains = re.fullmatch(
        r"(?P<subject>Zone) contains (?P<object>Room)",
        compact,
        re.IGNORECASE,
    )
    if contains is not None:
        return _claim(
            contains.group("subject"),
            "CONTAINS",
            contains.group("object"),
        )

    return Observation.unresolved("outside bounded relation grammar")


def _diagnostic_relation(text: str) -> Observation | None:
    compact = _clean(text)

    belongs = re.fullmatch(
        r"(?P<subject>B) belongs to (?P<object>A)",
        compact,
        re.IGNORECASE,
    )
    if belongs is not None:
        return _claim(
            belongs.group("subject"),
            "OWNED_BY",
            belongs.group("object"),
        )

    north = re.fullmatch(
        r"(?P<subject>A) lies north of (?P<object>B)",
        compact,
        re.IGNORECASE,
    )
    if north is not None:
        return _claim(
            north.group("subject"),
            "NORTH_OF",
            north.group("object"),
        )

    within = re.fullmatch(
        r"(?P<subject>Room) lies within (?P<object>Zone)",
        compact,
        re.IGNORECASE,
    )
    if within is not None:
        return _claim(
            within.group("subject"),
            "IN",
            within.group("object"),
        )

    adjacent = re.fullmatch(
        r"(?P<subject>A) and (?P<object>B) are adjacent",
        compact,
        re.IGNORECASE,
    )
    if adjacent is not None:
        return _claim(
            adjacent.group("subject"),
            "ADJACENT_TO",
            adjacent.group("object"),
        )

    return None


def broad_relation_extractor(text: str) -> Observation:
    """Broad lexical relation extractor used to expose overreach."""

    compact = _clean(text)
    direct = direct_relation_grammar(compact)
    if direct.status is Status.CLAIMED:
        return direct

    diagnostic = _diagnostic_relation(compact)
    if diagnostic is not None:
        return diagnostic

    low = compact.casefold()

    if "near" in low and "a" in low and "b" in low:
        return _claim("a", "NEAR", "b")

    if "north of" in low and "a" in low and "b" in low:
        return _claim("a", "NORTH_OF", "b")

    if "owns" in low and "a" in low and "b" in low:
        return _claim("a", "OWNS", "b")

    return Observation.unresolved("broad relation extractor found no atom")


def conservative_relation_hybrid(text: str) -> Observation:
    """Use broad extraction only behind frozen safe-extension surfaces."""

    direct = direct_relation_grammar(text)
    if direct.status is Status.CLAIMED:
        return direct
    if _hard_hazard(_clean(text)) is not None:
        return direct
    diagnostic = _diagnostic_relation(text)
    if diagnostic is not None:
        return diagnostic
    return direct


INSTRUMENTS = {
    "direct_relation_grammar": direct_relation_grammar,
    "broad_relation_extractor": broad_relation_extractor,
    "conservative_relation_hybrid": conservative_relation_hybrid,
}
