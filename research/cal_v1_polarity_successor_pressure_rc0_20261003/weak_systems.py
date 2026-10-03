"""Plausible weak auditors. They are not the candidate and must not be repaired into it."""

from __future__ import annotations

import re
from typing import Any


def ignore_assertion_polarity(claim: str, evidence: list[str]) -> str:
    """Treat any higher/lower cue as a positive comparison and ignore `did not`."""
    text = " ".join(evidence)
    higher = re.search(r"\b(higher|greater|larger|more|exceeded)\b", text, re.I)
    lower = re.search(r"\b(lower|smaller|fewer|less|trailed)\b", text, re.I)
    claim_higher = re.search(r"\b(higher|greater|larger|more)\b", claim, re.I)
    if higher and claim_higher:
        return "supported"
    if lower and not claim_higher:
        return "supported"
    if higher or lower:
        return "contradicted"
    return "not_checkable"


def collapse_scoped_comparison(claim: str) -> dict[str, str] | None:
    """Keep only a bare lhs/rhs/direction and drop population, time, and condition."""
    match = re.search(
        r"(?P<lhs>[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?)"
        r".*?\b(?P<rel>higher|lower|greater|smaller|larger|more|fewer|less)\b"
        r".*?\bthan\s+(?P<rhs>[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?)",
        claim,
    )
    if match is None:
        return None
    relation = match.group("rel").casefold()
    direction = "LESS_THAN" if relation in {"lower", "smaller", "fewer", "less"} else "MORE_THAN"
    return {
        "lhs_entity": match.group("lhs"),
        "rhs_entity": match.group("rhs"),
        "comparison_direction": direction,
    }


def structural_target_ok(target: dict[str, Any]) -> bool:
    """Accept any string-to-string field map. Do not compare it with authored claim text."""
    proposition = target.get("proposition")
    if not isinstance(proposition, dict):
        return False
    fields = proposition.get("fields")
    if not isinstance(fields, dict) or not fields:
        return False
    return all(isinstance(key, str) and isinstance(value, str) for key, value in fields.items())


def resolver_identity_wildcard(observed_sha: str, pinned_sha: str) -> bool:
    """Accept any non-empty producer identity."""
    del pinned_sha
    return bool(observed_sha.strip())
