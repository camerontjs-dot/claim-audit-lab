"""Bounded quantity-relation binding for CAL #210.

A shared verb or a matching number is not a relation. The binder keeps the
comparator, the two roles, the measure, the quantity and unit, and the year
scope as separate fields. It abstains when those fields are not uniquely bound.
"""

from __future__ import annotations

import re
from typing import Any

INSTRUMENT_ID = "quantity-comparator-binding-rc2-s2"

_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_SPLIT = re.compile(r",\s*while\s+|;\s+", re.IGNORECASE)
_NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_UNIT = r"percentage points|percent|%|million|billion|trillion"
_COMP = r"more|fewer|higher|lower|greater|less"
_ANAPHOR = {"their", "his", "her", "its", "they", "it"}
_SECOND_CUE = re.compile(
    r"\b(?:more|fewer|higher|lower|greater|less|faster|slower)\s+than\b"
    r"|\b(?:had|has|have)\s+(?:higher|lower|more|fewer|less|greater)\b"
    r"|\b(?:increased|decreased|rose|fell)\b",
    re.IGNORECASE,
)
_TIME_SCENE = re.compile(
    r"^(?:from|in|during)\s+(?:the\s+)?(?:preceding|same|prior|previous|following|current)?\s*"
    r"(?:month|year|quarter)\b[^,]{0,40},\s*",
    re.IGNORECASE,
)
_TIME_WORD = re.compile(
    r"\b(?:for|in|during)\s+(?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december|(?:19|20)\d{2})\b",
    re.IGNORECASE,
)

_NOT_MORE = re.compile(
    rf"(?P<left>.+?)\s+did not have more\s+(?P<measure>.+?)\s+than\s+(?P<right>.+)",
    re.IGNORECASE,
)
_NOT_ADJ = re.compile(
    rf"(?P<left>.+?)\s+(?:was|were|is|are)\s+not\s+"
    rf"(?P<word>more|higher|greater|less|fewer|lower)\s+than\s+(?P<right>.+)",
    re.IGNORECASE,
)
_RATE_YEARS = re.compile(
    rf"(?P<left>.+?)\s+(?P<verb>grew|increased|rose|fell|declined|decreased)\s+"
    rf"(?P<comp>faster|slower)\s+in\s+(?P<y1>(?:19|20)\d{{2}})\s+than\s+in\s+"
    rf"(?P<y2>(?:19|20)\d{{2}})",
    re.IGNORECASE,
)
_RATE_THAN = re.compile(
    rf"(?P<left>.+?)\s+(?P<verb>grew|increased|rose|fell|declined|decreased)\s+"
    rf"(?P<comp>faster|slower)\s+than\s+(?P<right>.+)",
    re.IGNORECASE,
)
_CHANGE = re.compile(
    rf"(?P<left>.+?)\s+(?P<verb>increased|decreased|increase|decrease|rose|fell|grew|declined|dropped)\s+"
    rf"(?:by\s+)?\$?(?P<qty>{_NUM})\s*(?P<unit>{_UNIT})?"
    rf"\s*(?:\(\s*(?P<paren>{_NUM})\s*(?P<paren_unit>percentage points|%|percent)(?!\w)[^)]*\))?",
    re.IGNORECASE,
)
_HAD = re.compile(
    rf"(?P<left>.+?)\s+(?:had|has|have)\s+(?P<comp>more|fewer|less|greater|higher|lower)\s+"
    rf"(?P<measure>.+?)\s+than\s+(?P<right>.+)",
    re.IGNORECASE,
)
_THAN = re.compile(
    rf"(?P<left>.+?)\s+(?:was|were|is|are)\s+"
    rf"(?:(?P<qty>{_NUM})\s*(?P<unit>{_UNIT})?\s*)?"
    rf"(?:\(\s*(?P<paren>{_NUM})\s*(?P<paren_unit>percentage points|%|percent)(?!\w)[^)]*\)\s*)?"
    rf"(?P<comp>{_COMP})\s+than\s+(?P<right>.+)",
    re.IGNORECASE,
)
_QTY_THAN = re.compile(
    rf"(?P<left>.+?)\s+(?:about|nearly|around|approximately)?\s*(?P<qty>{_NUM})\s*"
    rf"(?P<unit>percentage points|cents per gallon|percent|%|points)\s+"
    rf"(?P<comp>{_COMP})\s+than\s+(?P<right>.+)",
    re.IGNORECASE,
)
_THRESHOLD = re.compile(
    rf"(?P<left>.+?)\s+(?P<comp>less|more|fewer|greater)\s+than\s+"
    rf"\$?(?P<qty>{_NUM})(?P<unit>\s*(?:percent|%))?",
    re.IGNORECASE,
)
_SENTENCE = re.compile(r"(?<=[a-z0-9])\.\s+(?=[A-Z])")
_AND_SPLIT = re.compile(r"\s+\band\b\s+", re.IGNORECASE)
_RIGHT_CUT = re.compile(r",|\band\b", re.IGNORECASE)
_FRAME = re.compile(
    r"\b(?:expects|forecasts|projects|estimates|expect|forecast|project|estimate)\s+"
    r"(?:the\s+)?(?P<object>.+?)\s+to\s+(?:average|reach|be|rise|fall)\b",
    re.IGNORECASE,
)
_TRAIL_VERB = re.compile(
    r"\s+(?:was|were|is|are|averages|averaged|average|scored|scores|score)\s*$",
    re.IGNORECASE,
)
_DET = re.compile(
    r"^(?:both\s+of\s+those|both\s+of\s+these|those|these|the|a|an|both)\s+",
    re.IGNORECASE,
)
_TEMPORAL_RIGHT = re.compile(
    r"^(?:in|during|for)\s+(?:the\s+)?(?:(?:first|second|third|fourth)\s+quarter\s+of\s+)?(?:19|20)\d{2}\b"
    r"|^(?:last|this|next)\s+(?:year|month|quarter)\b"
    r"|^(?:a|one)\s+year\s+ago\b"
    r"|^(?:the\s+)?(?:preceding|prior|previous|same)\s+(?:year|month|quarter)\b",
    re.IGNORECASE,
)
_SCOPE_YEAR = re.compile(
    r"\b(?:in|during|for)\s+(?:the\s+)?"
    r"(?:(?:first|second|third|fourth)\s+quarter\s+of\s+|(?:first|second)\s+half\s+of\s+)?"
    r"((?:19|20)\d{2})\b",
    re.IGNORECASE,
)
_SCOPE_MONTH = re.compile(
    r"\b(?:in|during|for)\s+(january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\b",
    re.IGNORECASE,
)
_SINCE_YEAR = re.compile(r"\bsince\s+(?:19|20)\d{2}\b", re.IGNORECASE)
_NUMERIC_RIGHT = re.compile(rf"^\$?{_NUM}\b")
_EQ_TO = re.compile(
    r"(?P<left>.+?)\s+(?:was|were|is|are)\s+equal\s+to\s+(?P<right>.+)",
    re.IGNORECASE,
)
_EQ_BARE = re.compile(
    r"(?P<left>.+?)\s+(?:was|were|is|are)\s+equal\b",
    re.IGNORECASE,
)
_UNCHANGED = re.compile(
    r"(?P<left>.+?)\s+(?:was|were|is|are|remained)\s+unchanged\b",
    re.IGNORECASE,
)

_GT = {"more", "higher", "greater"}
_LT = {"fewer", "lower", "less"}


def _covers(match: re.Match[str], text: str) -> bool:
    tail = text[match.end():]
    if re.fullmatch(r"[\s.,;:]*", tail):
        return True
    # A source or time adjunct may follow the relation. A second comparator may not.
    return _SECOND_CUE.search(tail) is None


def _norm_qty(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = raw.replace(",", "")
    if "." in cleaned:
        cleaned = cleaned.rstrip("0").rstrip(".")
    return cleaned or None


def _norm_unit(raw: str | None) -> str | None:
    if not raw:
        return None
    text = raw.casefold().strip()
    if text in {"%", "percent"}:
        return "percent"
    if text == "percentage points":
        return "percentage_point"
    return text


def _norm_entity(raw: str | None) -> str:
    if not raw:
        return ""
    text = raw.strip(" .,").casefold()
    text = re.sub(r"(?:'s|’s)$", "", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_measure(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = raw.casefold().strip(" .")
    cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return None
    parts = cleaned.split(" ")
    last = parts[-1]
    if len(last) > 3 and last.endswith("s") and not last.endswith("ss"):
        parts[-1] = last[:-1]
    return " ".join(parts)


def _aspect(measure: str | None, aspect: str | None) -> str | None:
    if not measure or not aspect:
        return measure
    suffix = " " + aspect
    if measure.endswith(suffix):
        return measure
    return measure + suffix


def year_list(text: str) -> list[str]:
    return _YEAR.findall(text)


def _blank(comparator: str = "NA") -> dict[str, Any]:
    return {
        "comparator": comparator,
        "left": None,
        "right": None,
        "measure": None,
        "qty": None,
        "unit": None,
        "paren_qty": None,
        "paren_unit": None,
        "y1": None,
        "y2": None,
        "verb": None,
        "years": [],
        "span": None,
        "ambiguity": comparator == "AMBIGUOUS",
    }


def _decompose_left(text: str) -> tuple[str, str | None]:
    raw = text.strip(" .")
    raw = re.sub(r"^(?:in|during)\s+(?:19|20)\d{2},?\s*", "", raw, flags=re.IGNORECASE)
    possessive = re.fullmatch(r"(.+?)(?:'s|’s)\s+(.+)", raw)
    if possessive:
        measure = _YEAR.sub(" ", possessive.group(2))
        measure = re.sub(r"\s+", " ", measure).strip()
        return _norm_entity(possessive.group(1)), normalize_measure(measure)
    pronoun = re.fullmatch(r"(their|his|her|its)\s+(.+)", raw, re.IGNORECASE)
    if pronoun:
        return pronoun.group(1).casefold(), normalize_measure(pronoun.group(2))
    return _norm_entity(raw), None


def _decompose_right(text: str) -> tuple[str, str | None]:
    raw = text.strip(" .")
    raw = _RIGHT_CUT.split(raw, maxsplit=1)[0]
    raw = re.sub(r"\s+in\s+(?:19|20)\d{2}\b", "", raw, flags=re.IGNORECASE).strip(" .")
    on_measure = re.fullmatch(r"(.+?)\s+on\s+(.+)", raw, re.IGNORECASE)
    if on_measure:
        return _norm_entity(on_measure.group(1)), normalize_measure(on_measure.group(2))
    return _norm_entity(raw), None


def _subject_measure(text: str) -> str | None:
    """Measure carried by a non-possessive subject. Time scenes are not part of it."""
    raw = text.strip(" .,")
    raw = _TIME_SCENE.sub("", raw)
    raw = re.sub(r"^(?:in|during)\s+(?:19|20)\d{2},?\s*", "", raw, flags=re.IGNORECASE)
    frame = _FRAME.search(raw)
    if frame:
        raw = frame.group("object")
    else:
        raw = _TRAIL_VERB.sub("", raw)
    raw = _TIME_WORD.sub(" ", raw)
    raw = re.sub(r"\s+", " ", raw).strip(" .,")
    while raw and _DET.match(raw):
        raw = _DET.sub("", raw, count=1)
    return normalize_measure(raw)


def _is_temporal(text: str) -> bool:
    raw = _RIGHT_CUT.split(text.strip(" .,"), maxsplit=1)[0].strip()
    return _TEMPORAL_RIGHT.match(raw) is not None


def _temporal_pole(text: str) -> str:
    raw = _RIGHT_CUT.split(text.strip(" .,"), maxsplit=1)[0].strip().casefold()
    year = re.search(r"(?:19|20)\d{2}", raw)
    if year and re.match(r"(?:in|during|for)\b", raw):
        return "year:" + year.group(0)
    if "last year" in raw:
        return "relative:last_year"
    if "year ago" in raw:
        return "relative:year_ago"
    if "last month" in raw:
        return "relative:last_month"
    return "relative:" + re.sub(r"\s+", " ", raw)


def _scope_years(text: str) -> list[str]:
    """Years and months that qualify this clause, excluding commentary after a dash."""
    cleaned = re.split(r"—|–", text, maxsplit=1)[0]
    cleaned = _SINCE_YEAR.sub(" ", cleaned)
    years = _SCOPE_YEAR.findall(cleaned)
    months = ["month:" + item.casefold() for item in _SCOPE_MONTH.findall(cleaned)]
    return years + months


def _split_pattern(text: str, pattern: re.Pattern[str]) -> list[tuple[int, str]]:
    parts: list[tuple[int, str]] = []
    start = 0
    for match in pattern.finditer(text):
        parts.append((start, text[start:match.start()]))
        start = match.end()
    parts.append((start, text[start:]))
    return [(offset, part) for offset, part in parts if part.strip()]


def _and_parts(text: str) -> list[tuple[int, str]]:
    pieces = _split_pattern(text, _AND_SPLIT)
    if len(pieces) > 1 and all(_SECOND_CUE.search(part) for _, part in pieces):
        return pieces
    return [(0, text)]


def _clauses(text: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for sent_off, sentence in _split_pattern(text, _SENTENCE):
        for clause_off, clause in _split_pattern(sentence, _SPLIT):
            base = sent_off + clause_off
            for and_off, part in _and_parts(clause):
                found.append((base + and_off, part))
    return found or [(0, text)]


def _finish(base: dict[str, Any], match: re.Match[str], offset: int) -> dict[str, Any]:
    base["span"] = [offset + match.start(), offset + match.end()]
    return base


def _relative(match: re.Match[str], comp_word: str, measure: str | None, offset: int) -> dict[str, Any]:
    row = _blank("GT" if comp_word.casefold() in _GT else "LT")
    left, left_measure = _decompose_left(match.group("left"))
    right_raw = match.group("right")
    if _SECOND_CUE.search(right_raw):
        return _finish(_blank("AMBIGUOUS"), match, offset)
    right, right_measure = _decompose_right(right_raw)
    if _is_temporal(right_raw):
        right = _temporal_pole(right_raw)
        if left_measure is None:
            subject = _subject_measure(match.group("left"))
            left = subject or left
            left_measure = subject
    row["left"] = left
    row["right"] = right
    row["measure"] = measure or right_measure or left_measure
    row["qty"] = _norm_qty(match.groupdict().get("qty"))
    row["unit"] = _norm_unit(match.groupdict().get("unit"))
    row["paren_qty"] = _norm_qty(match.groupdict().get("paren"))
    row["paren_unit"] = _norm_unit(match.groupdict().get("paren_unit"))
    if left_measure and right_measure and left_measure != right_measure:
        row["comparator"] = "AMBIGUOUS"
        row["ambiguity"] = True
    return _finish(row, match, offset)


def _from_match(kind: str, match: re.Match[str], offset: int) -> dict[str, Any]:
    if kind == "not_more":
        row = _blank("NOT_GT")
        row["left"] = _norm_entity(match.group("left"))
        row["right"] = _norm_entity(match.group("right"))
        row["measure"] = normalize_measure(match.group("measure"))
        return _finish(row, match, offset)
    if kind == "not_adj":
        word = match.group("word").casefold()
        row = _blank("NOT_GT" if word in _GT else "NOT_LT")
        row["left"] = _norm_entity(_decompose_left(match.group("left"))[0])
        right, right_measure = _decompose_right(match.group("right"))
        row["right"] = right
        row["measure"] = right_measure or _decompose_left(match.group("left"))[1]
        return _finish(row, match, offset)
    if kind == "rate_years":
        row = _blank("GT_RATE" if match.group("comp").casefold() == "faster" else "LT_RATE")
        left, measure = _decompose_left(match.group("left"))
        row["left"] = left
        row["measure"] = _aspect(measure, "growth")
        row["verb"] = match.group("verb").casefold()
        row["y1"] = match.group("y1")
        row["y2"] = match.group("y2")
        return _finish(row, match, offset)
    if kind == "rate_than":
        if _SECOND_CUE.search(match.group("right")):
            return _finish(_blank("AMBIGUOUS"), match, offset)
        row = _blank("GT_RATE" if match.group("comp").casefold() == "faster" else "LT_RATE")
        left, measure = _decompose_left(match.group("left"))
        row["left"] = left
        row["right"] = _norm_entity(match.group("right"))
        row["measure"] = _aspect(measure, "growth")
        row["verb"] = match.group("verb").casefold()
        return _finish(row, match, offset)
    if kind == "change":
        row = _blank("DECREASE" if match.group("verb").casefold().startswith(("decreas", "fell", "declin", "drop")) else "INCREASE")
        if match.group("verb").casefold() in {"fell", "declined", "dropped"}:
            row["comparator"] = "DECREASE"
        left, measure = _decompose_left(match.group("left"))
        if measure is None:
            measure = _subject_measure(match.group("left"))
            left = measure or left
        row["left"] = left
        row["measure"] = _aspect(measure, "change")
        row["verb"] = match.group("verb").casefold()
        row["qty"] = _norm_qty(match.group("qty"))
        row["unit"] = _norm_unit(match.group("unit"))
        row["paren_qty"] = _norm_qty(match.group("paren"))
        row["paren_unit"] = _norm_unit(match.group("paren_unit"))
        return _finish(row, match, offset)
    if kind == "had":
        return _relative(match, match.group("comp"), normalize_measure(match.group("measure")), offset)
    if kind in {"than", "qty_than"}:
        return _relative(match, match.group("comp"), None, offset)
    if kind == "threshold":
        word = match.group("comp").casefold()
        row = _blank("GT" if word in _GT else "LT")
        subject = _subject_measure(match.group("left"))
        row["left"] = subject
        row["right"] = "threshold"
        row["measure"] = subject
        row["qty"] = _norm_qty(match.group("qty"))
        row["unit"] = _norm_unit(match.group("unit"))
        return _finish(row, match, offset)
    if kind in {"eq_to", "eq_bare", "unchanged"}:
        row = _blank("EQ")
        left, measure = _decompose_left(match.group("left"))
        row["left"] = left
        row["measure"] = measure
        if kind == "eq_to":
            right, right_measure = _decompose_right(match.group("right"))
            row["right"] = right
            row["measure"] = measure or right_measure
        return _finish(row, match, offset)
    raise KeyError(kind)


_PATTERNS = (
    ("not_more", _NOT_MORE),
    ("not_adj", _NOT_ADJ),
    ("rate_years", _RATE_YEARS),
    ("rate_than", _RATE_THAN),
    ("change", _CHANGE),
    ("had", _HAD),
    ("qty_than", _QTY_THAN),
    ("threshold", _THRESHOLD),
    ("than", _THAN),
    ("eq_to", _EQ_TO),
    ("eq_bare", _EQ_BARE),
    ("unchanged", _UNCHANGED),
)


def _parse_clause(clause: str, offset: int) -> dict[str, Any] | None:
    text = clause.strip()
    if not text:
        return None
    pad = len(clause) - len(clause.lstrip())
    hits: list[dict[str, Any]] = []
    for kind, pattern in _PATTERNS:
        found = pattern.search(text)
        if found is None or not _covers(found, text):
            continue
        if kind == "than" and _NUMERIC_RIGHT.match(found.group("right").strip()):
            continue
        if kind in {"had", "than", "qty_than", "change", "rate_than"} and hits and hits[0]["comparator"] in {"NOT_GT", "NOT_LT"}:
            continue
        hits.append(_from_match(kind, found, offset + pad))
        if hits[-1]["comparator"] in {"NOT_GT", "NOT_LT"}:
            break
    if not hits:
        return None
    kinds = {item["comparator"] for item in hits}
    if "AMBIGUOUS" in kinds or len(kinds) > 1:
        row = _blank("AMBIGUOUS")
        row["span"] = [offset, offset + len(clause)]
        return row
    # A numeric threshold owns the clause when a copula pattern agrees with it.
    thresholds = [item for item in hits if item.get("right") == "threshold"]
    if thresholds and len(kinds) == 1:
        return max(thresholds, key=lambda item: item["span"][1] - item["span"][0])
    # Prefer the longest covering match when several patterns agree.
    return max(hits, key=lambda item: item["span"][1] - item["span"][0])


def parse_document(text: str) -> dict[str, Any]:
    parsed = []
    for offset, part in _clauses(text):
        item = _parse_clause(part, offset)
        if item is None:
            continue
        item["years"] = _scope_years(part)
        parsed.append(item)
    if not parsed:
        row = _blank("NA")
        row["years"] = _scope_years(text)
        return row
    if len(parsed) == 1:
        return parsed[0]
    return {
        "comparator": "MULTI",
        "clauses": parsed,
        "years": [],
        "span": [0, len(text)],
        "ambiguity": False,
        "measure": None,
        "left": None,
        "right": None,
        "qty": None,
        "unit": None,
        "paren_qty": None,
        "paren_unit": None,
        "y1": None,
        "y2": None,
        "verb": None,
    }


def _measure_key(measure: str | None) -> str | None:
    if not measure:
        return None
    text = _TIME_WORD.sub(" ", measure)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _measures_match(left: str | None, right: str | None) -> bool:
    """Equal measures only. A shorter name inside a qualified name is not the same measure."""
    key_left, key_right = _measure_key(left), _measure_key(right)
    return bool(key_left) and key_left == key_right


def _select_evidence(parsed: dict[str, Any], claim_measure: str | None) -> dict[str, Any]:
    if parsed["comparator"] != "MULTI":
        return parsed
    clauses = parsed["clauses"]
    for item in clauses:
        if item["comparator"] != "AMBIGUOUS":
            continue
        # An unbound ambiguous clause can still be the claim's relation. Fail closed.
        if item.get("measure") is None or _measures_match(item.get("measure"), claim_measure):
            row = _blank("AMBIGUOUS")
            row["years"] = item.get("years") or []
            row["span"] = item.get("span") or parsed["span"]
            row["measure"] = claim_measure
            return row
    matches = [item for item in clauses if _measures_match(item.get("measure"), claim_measure)]
    if len(matches) == 1:
        return dict(matches[0])
    row = _blank("AMBIGUOUS")
    row["years"] = []
    row["span"] = parsed["span"]
    row["measure"] = claim_measure if matches else None
    return row


def _units_conflict(claim: dict[str, Any], evidence: dict[str, Any]) -> bool:
    for key in ("unit", "paren_unit"):
        left, right = claim.get(key), evidence.get(key)
        if left and right and left != right:
            return True
    return False


def _magnitudes_match(claim: dict[str, Any], evidence: dict[str, Any]) -> bool:
    if bool(claim.get("paren_qty")) != bool(evidence.get("paren_qty")):
        return False
    if claim.get("paren_qty") and claim.get("paren_qty") != evidence.get("paren_qty"):
        return False
    if claim.get("qty") and evidence.get("qty") and claim.get("qty") != evidence.get("qty"):
        return False
    return True


def _inherit(claim: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    entities = {_norm_entity(evidence.get("left")), _norm_entity(evidence.get("right"))} - {""}
    if entities and entities <= _ANAPHOR:
        copied = dict(evidence)
        copied["left"] = claim.get("left")
        copied["right"] = claim.get("right")
        return copied
    return evidence


def _poles(row: dict[str, Any]) -> tuple[str, str] | None:
    left, right = _norm_entity(row.get("left")), _norm_entity(row.get("right"))
    if row["comparator"] == "GT":
        return (left, right)
    if row["comparator"] == "LT":
        return (right, left)
    return None


def _same_roles(claim: dict[str, Any], evidence: dict[str, Any]) -> bool:
    return _norm_entity(claim.get("left")) == _norm_entity(evidence.get("left")) and _norm_entity(
        claim.get("right")
    ) == _norm_entity(evidence.get("right"))


def _entity_set(row: dict[str, Any]) -> set[str]:
    return {_norm_entity(row.get("left")), _norm_entity(row.get("right"))} - {""}


def _decide_relative(claim: dict[str, Any], evidence: dict[str, Any]) -> tuple[str, str | None]:
    negated = {"NOT_GT", "NOT_LT"}
    if claim["comparator"] in negated or evidence["comparator"] in negated:
        if claim["comparator"] == evidence["comparator"] and _same_roles(claim, evidence) and _magnitudes_match(claim, evidence):
            return "supports", None
        if _same_roles(claim, evidence) and (
            (claim["comparator"] == "GT" and evidence["comparator"] == "NOT_GT")
            or (claim["comparator"] == "LT" and evidence["comparator"] == "NOT_LT")
        ):
            return "refutes", None
        return "unresolved", "negation_not_decisive"
    if claim["comparator"] == "EQ" or evidence["comparator"] == "EQ":
        if _entity_set(claim) != _entity_set(evidence):
            return "unresolved", "role_unbound"
        if claim["comparator"] == evidence["comparator"] and _magnitudes_match(claim, evidence):
            return "supports", None
        return "refutes", None
    claim_poles, evidence_poles = _poles(claim), _poles(evidence)
    if claim_poles is None or evidence_poles is None or "" in claim_poles or "" in evidence_poles:
        return "unresolved", "role_unbound"
    if claim_poles == evidence_poles:
        if _magnitudes_match(claim, evidence):
            return "supports", None
        return "unresolved", "magnitude_mismatch"
    if claim_poles == (evidence_poles[1], evidence_poles[0]):
        return "refutes", None
    return "unresolved", "role_unbound"


def _decide_rate(claim: dict[str, Any], evidence: dict[str, Any]) -> tuple[str, str | None]:
    if _norm_entity(claim.get("left")) != _norm_entity(evidence.get("left")):
        return "unresolved", "role_unbound"
    if (claim.get("verb") or "") != (evidence.get("verb") or ""):
        return "unresolved", "growth_verb_mismatch"
    claim_poles = (claim.get("y1"), claim.get("y2"))
    evidence_poles = (evidence.get("y1"), evidence.get("y2"))
    if claim["comparator"] == "LT_RATE":
        claim_poles = (claim_poles[1], claim_poles[0])
    if evidence["comparator"] == "LT_RATE":
        evidence_poles = (evidence_poles[1], evidence_poles[0])
    if None in claim_poles or None in evidence_poles:
        if claim["comparator"] == evidence["comparator"] and claim.get("right") and claim.get("right") == evidence.get("right"):
            return "supports", None
        if {claim["comparator"], evidence["comparator"]} == {"GT_RATE", "LT_RATE"} and claim.get("right") == evidence.get("right"):
            return "refutes", None
        return "unresolved", "role_unbound"
    if claim_poles == evidence_poles:
        return "supports", None
    if claim_poles == (evidence_poles[1], evidence_poles[0]):
        return "refutes", None
    return "unresolved", "time_mismatch"


def _decide_change(claim: dict[str, Any], evidence: dict[str, Any]) -> tuple[str, str | None]:
    if _norm_entity(claim.get("left")) != _norm_entity(evidence.get("left")):
        return "unresolved", "role_unbound"
    if claim["comparator"] == evidence["comparator"]:
        if _magnitudes_match(claim, evidence):
            return "supports", None
        return "unresolved", "magnitude_mismatch"
    return "refutes", None


def decide(claim: dict[str, Any], evidence: dict[str, Any]) -> tuple[str, str | None]:
    if claim["comparator"] == "NA":
        return "not_applicable", "unparsed_comparison"
    if evidence["comparator"] == "NA":
        return "unresolved", "evidence_not_a_quantity_relation"
    if claim["comparator"] == "AMBIGUOUS" or evidence["comparator"] == "AMBIGUOUS":
        return "unresolved", "competing_comparator_cues"
    if not _measures_match(claim.get("measure"), evidence.get("measure")):
        return "unresolved", "measure_mismatch"
    if set(claim.get("years") or []) != set(evidence.get("years") or []):
        return "unresolved", "time_mismatch"
    if _units_conflict(claim, evidence):
        return "unresolved", "unit_mismatch"
    evidence = _inherit(claim, evidence)
    families = (
        ({"GT", "LT", "EQ", "NOT_GT", "NOT_LT"}, _decide_relative),
        ({"GT_RATE", "LT_RATE"}, _decide_rate),
        ({"INCREASE", "DECREASE"}, _decide_change),
    )
    for members, function in families:
        if claim["comparator"] in members and evidence["comparator"] in members:
            return function(claim, evidence)
    return "unresolved", "relation_family_mismatch"


def _span(row: dict[str, Any], text: str) -> list[list[int]]:
    span = row.get("span") or [0, len(text)]
    if not span or span[0] >= span[1] or span[1] > len(text):
        return [[0, len(text)]] if text else []
    return [span]


def analyze(claim: str, evidence: str) -> dict[str, Any]:
    """Return the frozen development-contract record for one pair."""
    claim_row = parse_document(claim)
    if claim_row["comparator"] == "NA":
        return {
            "status": "not_applicable",
            "relation": "not_applicable",
            "claim_comparator": "NA",
            "evidence_comparator": "NA",
            "claim_measure": None,
            "evidence_measure": None,
            "claim_years": year_list(claim),
            "evidence_years": year_list(evidence),
            "ambiguity": False,
            "consumed_claim_spans": [],
            "consumed_evidence_spans": [],
            "abstention_cause": "unparsed_comparison",
            "instrument_id": INSTRUMENT_ID,
        }
    evidence_row = _select_evidence(parse_document(evidence), claim_row.get("measure"))
    relation, cause = decide(claim_row, evidence_row)
    status = "not_applicable" if relation == "not_applicable" else ("unresolved" if relation == "unresolved" else "claimed")
    return {
        "status": status,
        "relation": relation,
        "claim_comparator": claim_row["comparator"],
        "evidence_comparator": evidence_row["comparator"],
        "claim_measure": claim_row.get("measure"),
        "evidence_measure": evidence_row.get("measure"),
        "claim_roles": [claim_row.get("left"), claim_row.get("right")],
        "evidence_roles": [evidence_row.get("left"), evidence_row.get("right")],
        "claim_quantity": claim_row.get("qty"),
        "evidence_quantity": evidence_row.get("qty"),
        "claim_unit": claim_row.get("unit") or claim_row.get("paren_unit"),
        "evidence_unit": evidence_row.get("unit") or evidence_row.get("paren_unit"),
        "claim_years": year_list(claim),
        "evidence_years": year_list(evidence),
        "ambiguity": evidence_row["comparator"] == "AMBIGUOUS" or claim_row["comparator"] == "AMBIGUOUS",
        "consumed_claim_spans": _span(claim_row, claim),
        "consumed_evidence_spans": _span(evidence_row, evidence),
        "abstention_cause": cause,
        "instrument_id": INSTRUMENT_ID,
    }


def apply_quantity_receipt(receipt: dict[str, Any], envelope: dict[str, Any]) -> None:
    """Fill one isolated quantity-lane receipt. Other lanes are untouched."""
    claim = str(envelope["claim"])
    passages = [str(item["text"]) for item in envelope["evidence"]]
    claim_row = parse_document(claim)
    receipt["instrument_id"] = INSTRUMENT_ID
    receipt["binding"] = {"claim": _public(claim_row), "passages": []}
    if claim_row["comparator"] == "NA":
        receipt["abstention_cause"] = "unparsed_comparison"
        return
    receipt["applicability"] = "applicable"
    if not passages:
        receipt["conclusion"] = "unresolved"
        receipt["abstention_cause"] = "missing_evidence"
        return
    claim_years = set(year_list(claim))
    evidence_years: set[str] = set()
    for text in passages:
        evidence_years.update(year_list(text))
    if claim_years and not claim_years <= evidence_years:
        receipt["conclusion"] = "unresolved"
        receipt["abstention_cause"] = "time_mismatch"
        return
    opinions: list[str] = []
    causes: list[str | None] = []
    for text in passages:
        decision = analyze(claim, text)
        receipt["binding"]["passages"].append(decision)
        if decision["relation"] == "not_applicable":
            continue
        opinions.append(str(decision["relation"]))
        causes.append(decision.get("abstention_cause"))
    if "supports" in opinions and "refutes" in opinions:
        receipt["conclusion"] = "unresolved"
        receipt["abstention_cause"] = "material_conflict"
        receipt["local_material_conflict"] = True
        return
    if "supports" in opinions:
        receipt["conclusion"] = "supports"
        receipt["abstention_cause"] = None
        return
    if "refutes" in opinions:
        receipt["conclusion"] = "refutes"
        receipt["abstention_cause"] = None
        return
    receipt["conclusion"] = "unresolved"
    receipt["abstention_cause"] = next((item for item in causes if item), "no_matching_passage")


def _public(row: dict[str, Any]) -> dict[str, Any]:
    kept = (
        "comparator",
        "left",
        "right",
        "measure",
        "qty",
        "unit",
        "paren_qty",
        "paren_unit",
        "y1",
        "y2",
        "verb",
        "years",
        "span",
        "ambiguity",
    )
    return {key: row.get(key) for key in kept}
