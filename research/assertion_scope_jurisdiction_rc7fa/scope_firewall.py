"""RC7F-A bounded assertion/scope firewall.

Research-only. This module classifies the assertion status of an already-measured
local event observation. It does not discover events and it does not grant
production authority.
"""
from __future__ import annotations

import re
from typing import Iterable

CANDIDATE_VERSION = "rc7fa-scope-firewall-1"

STATUSES = {
    "ASSERTED",
    "ASSERTED_NEGATIVE",
    "ATTRIBUTED",
    "CONDITIONAL_ANTECEDENT",
    "CONDITIONAL_CONSEQUENT",
    "EPISTEMIC",
    "DEONTIC",
    "QUANTIFIED",
    "UNRESOLVED",
}

REPORTING_VERBS = (
    "said", "says", "reported", "reports", "claimed", "claims", "alleged",
    "alleges", "denied", "denies", "stated", "states", "announced", "announces",
    "believed", "believes", "argued", "argues", "asserted", "asserts",
    "confirmed", "confirms",
)

AMBIGUOUS_MARKERS = (
    "whether ", "it is disputed", "remains disputed", "according to ",
    "supposedly ", "purportedly ",
)

EPISTEMIC_PATTERNS = (
    r"\blikely\b", r"\bunlikely\b", r"\bprobably\b", r"\bpossibly\b", r"\bpossible\b",
    r"\bperhaps\b", r"\bmight\b", r"\bcould\b", r"\ba chance\b",
    r"\bappears? to\b", r"\bseems? to\b",
)

DEONTIC_PATTERNS = (
    r"\bonly\b.{0,80}\bmay\b",
    r"\bpermitted to\b", r"\ballowed to\b", r"\bauthorized to\b",
    r"\brequired to\b", r"\bmust\b", r"\bshall\b",
    r"\bprohibited from\b", r"\bforbidden to\b",
)

QUANTIFIER_PATTERNS = (
    r"^\s*all\b", r"^\s*every\b", r"^\s*some\b", r"^\s*no\b",
    r"^\s*not all\b", r"^\s*at least one\b", r"^\s*at most one\b",
    r"^\s*exactly\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
    r"^\s*\d+(?:\.\d+)?%\s+of\b", r"^\s*(?:a|the)\s+majority\s+of\b",
    r"^\s*few\b", r"^\s*many\b",
)

CONDITIONAL_PREFIXES = ("if ", "unless ", "provided that ", "provided ", "assuming that ")


def _quote_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    stack: int | None = None
    quote_chars = {'"', '“', '”'}
    for i, ch in enumerate(text):
        if ch not in quote_chars:
            continue
        if ch == '“':
            if stack is None:
                stack = i
        elif ch == '”':
            if stack is not None:
                ranges.append((stack, i + 1))
                stack = None
        else:
            if stack is None:
                stack = i
            else:
                ranges.append((stack, i + 1))
                stack = None
    return ranges


def _inside(start: int, end: int, span: tuple[int, int]) -> bool:
    return start >= span[0] and end <= span[1]


def classify(raw_source: str, observation: dict, *, disabled_rules: Iterable[str] = ()) -> dict:
    disabled = set(disabled_rules)
    start = observation.get("start")
    end = observation.get("end")
    if not isinstance(raw_source, str) or not isinstance(start, int) or not isinstance(end, int):
        return _result("UNRESOLVED", ["invalid_input"], ["raw source or anchor missing"])
    if start < 0 or end <= start or end > len(raw_source):
        return _result("UNRESOLVED", ["invalid_anchor"], ["anchor outside source"])
    anchor = raw_source[start:end]
    if not anchor.strip():
        return _result("UNRESOLVED", ["empty_anchor"], ["empty observation anchor"])

    lower = raw_source.lower()

    if "ambiguous" not in disabled:
        for marker in AMBIGUOUS_MARKERS:
            if marker in lower:
                return _result("UNRESOLVED", [f"ambiguous:{marker.strip()}"], ["unsupported evidential framing"])

    if "attribution" not in disabled:
        for qr in _quote_ranges(raw_source):
            if _inside(start, end, qr):
                return _result("ATTRIBUTED", ["anchor_inside_quote"], [])
        that_pos = lower.rfind(" that ", 0, start + 1)
        if that_pos >= 0:
            prefix = lower[:that_pos]
            if any(re.search(rf"\b{re.escape(v)}\b", prefix) for v in REPORTING_VERBS):
                return _result("ATTRIBUTED", ["reporting_verb+that_complement"], [])

    if "conditional" not in disabled:
        stripped = lower.lstrip()
        if any(stripped.startswith(p) for p in CONDITIONAL_PREFIXES):
            comma = raw_source.find(",")
            if comma >= 0:
                if end <= comma + 1:
                    return _result("CONDITIONAL_ANTECEDENT", ["conditional_prefix", "anchor_before_comma"], [])
                if start > comma:
                    return _result("CONDITIONAL_CONSEQUENT", ["conditional_prefix", "anchor_after_comma"], [])
            return _result("UNRESOLVED", ["conditional_prefix", "no_clause_boundary"], ["conditional clause boundary unresolved"])

    if "deontic" not in disabled:
        for pat in DEONTIC_PATTERNS:
            if re.search(pat, lower):
                return _result("DEONTIC", [f"deontic:{pat}"], [])

    if "epistemic" not in disabled:
        for pat in EPISTEMIC_PATTERNS:
            if re.search(pat, lower):
                return _result("EPISTEMIC", [f"epistemic:{pat}"], [])

    if "quantifier" not in disabled:
        for pat in QUANTIFIER_PATTERNS:
            if re.search(pat, lower):
                return _result("QUANTIFIED", [f"quantifier:{pat}"], [])

    if "ambiguous" not in disabled and re.search(r"\bmay\b", lower):
        return _result("UNRESOLVED", ["ambiguous:may"], ["may is not disambiguated by bounded rules"])

    polarity = str(observation.get("polarity", "positive")).lower()
    if polarity == "negative":
        return _result("ASSERTED_NEGATIVE", ["observation_polarity:negative"], [])
    if polarity != "positive":
        return _result("UNRESOLVED", [f"unknown_polarity:{polarity}"], ["unsupported polarity"])

    return _result("ASSERTED", ["no_outer_scope_detected"], [])


def _result(status: str, basis: list[str], limitations: list[str]) -> dict:
    assert status in STATUSES
    return {
        "scope_status": status,
        "authority_eligible": status in {"ASSERTED", "ASSERTED_NEGATIVE"},
        "basis": basis,
        "limitations": limitations,
    }
