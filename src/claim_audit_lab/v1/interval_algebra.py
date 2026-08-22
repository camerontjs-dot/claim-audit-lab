"""Deterministic Interval Algebra Operator for Claim Audit Lab v2.

Evaluates mathematical containment of asserted numeric intervals against
evidence-permitted intervals without delegating arithmetic to language models.

Solves the D1 / D12 capability boundary:
- Replaces brittle heuristic overlap with exact interval subset containment.
- Distinguishes numeric measurements from entity identifiers.
- Normalizes physical units (time, temperature, mass, volume, percentage).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Literal

BoundKind = Literal[
    "exact", "at_least", "greater_than", "at_most", "less_than", "range", "tolerance", "unknown"
]
IntervalStatus = Literal["satisfied", "violated", "incomparable", "inconclusive"]

# Canonical unit normalization factors to base units:
# Base Time: seconds (s)
# Base Mass: grams (g)
# Base Volume: milliliters (mL)
# Base Ratio: fraction (1.0 = 100%)
_TIME_FACTORS: dict[str, float] = {
    "s": 1.0,
    "sec": 1.0,
    "second": 1.0,
    "seconds": 1.0,
    "min": 60.0,
    "minute": 60.0,
    "minutes": 60.0,
    "h": 3600.0,
    "hr": 3600.0,
    "hour": 3600.0,
    "hours": 3600.0,
    "d": 86400.0,
    "day": 86400.0,
    "days": 86400.0,
    "wk": 604800.0,
    "week": 604800.0,
    "weeks": 604800.0,
    # Standard regulatory/pharmaceutical month convention (30.4375 days or 30 days)
    "mo": 2592000.0,  # 30 days
    "month": 2592000.0,
    "months": 2592000.0,
    "yr": 31536000.0,  # 365 days
    "year": 31536000.0,
    "years": 31536000.0,
}

_MASS_FACTORS: dict[str, float] = {
    "ug": 1e-6,
    "mcg": 1e-6,
    "microgram": 1e-6,
    "micrograms": 1e-6,
    "mg": 1e-3,
    "milligram": 1e-3,
    "milligrams": 1e-3,
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
}

_VOLUME_FACTORS: dict[str, float] = {
    "ul": 1e-3,
    "microliter": 1e-3,
    "microliters": 1e-3,
    "ml": 1.0,
    "milliliter": 1.0,
    "milliliters": 1.0,
    "l": 1000.0,
    "liter": 1000.0,
    "liters": 1000.0,
}

_RATIO_FACTORS: dict[str, float] = {
    "%": 0.01,
    "percent": 0.01,
    "pct": 0.01,
    "ppm": 1e-6,
    "ppb": 1e-9,
}


def _normalize_unit_name(unit: str) -> str:
    cleaned = unit.strip().lower().replace("°", "").replace("deg ", "").replace("degrees ", "")
    return cleaned


def normalize_quantity_to_base(value: float, unit: str | None) -> tuple[float, str]:
    """Convert (value, unit) to a canonical base dimension."""
    if unit is None:
        return value, "scalar"
    u = _normalize_unit_name(unit)

    # Temperature (special non-multiplicative conversion)
    if u in ("c", "celsius", "centigrade"):
        return value, "temp_c"
    if u in ("f", "fahrenheit"):
        return (value - 32.0) * (5.0 / 9.0), "temp_c"
    if u in ("k", "kelvin"):
        return value - 273.15, "temp_c"

    # Multiplicative dimensions
    if u in _TIME_FACTORS:
        return value * _TIME_FACTORS[u], "time_s"
    if u in _MASS_FACTORS:
        return value * _MASS_FACTORS[u], "mass_g"
    if u in _VOLUME_FACTORS:
        return value * _VOLUME_FACTORS[u], "volume_ml"
    if u in _RATIO_FACTORS:
        return value * _RATIO_FACTORS[u], "ratio_unit"

    # Fallback to normalized verbatim unit
    return value, u


@dataclass(frozen=True)
class Interval:
    """Mathematical 1D continuous interval [lower, upper].

    Supports open and closed bounds, infinite endpoints, and set containment.
    """

    lower: float
    upper: float
    left_closed: bool = True
    right_closed: bool = True
    dimension: str = "scalar"

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError(f"Invalid interval: lower ({self.lower}) > upper ({self.upper})")

    @classmethod
    def at_least(cls, value: float, dimension: str = "scalar") -> Interval:
        return cls(
            lower=value, upper=math.inf, left_closed=True, right_closed=False, dimension=dimension
        )

    @classmethod
    def greater_than(cls, value: float, dimension: str = "scalar") -> Interval:
        return cls(
            lower=value, upper=math.inf, left_closed=False, right_closed=False, dimension=dimension
        )

    @classmethod
    def at_most(cls, value: float, dimension: str = "scalar") -> Interval:
        return cls(
            lower=-math.inf, upper=value, left_closed=False, right_closed=True, dimension=dimension
        )

    @classmethod
    def less_than(cls, value: float, dimension: str = "scalar") -> Interval:
        return cls(
            lower=-math.inf, upper=value, left_closed=False, right_closed=False, dimension=dimension
        )

    @classmethod
    def closed(cls, lower: float, upper: float, dimension: str = "scalar") -> Interval:
        return cls(
            lower=lower, upper=upper, left_closed=True, right_closed=True, dimension=dimension
        )

    @classmethod
    def point(cls, value: float, dimension: str = "scalar") -> Interval:
        return cls(
            lower=value, upper=value, left_closed=True, right_closed=True, dimension=dimension
        )

    def is_subset_of(self, other: Interval) -> bool:
        """Return True if self is a mathematical subset of other (self ⊆ other)."""
        if self.dimension != other.dimension:
            return False

        # Check lower bound
        if self.lower < other.lower:
            return False
        if self.lower == other.lower:
            if not self.left_closed and other.left_closed:
                pass  # (a, ...] is subset of [a, ...]
            elif self.left_closed and not other.left_closed:
                return False  # [a, ...] is NOT subset of (a, ...]

        # Check upper bound
        if self.upper > other.upper:
            return False
        if self.upper == other.upper:
            if not self.right_closed and other.right_closed:
                pass  # [..., b) is subset of [..., b]
            elif self.right_closed and not other.right_closed:
                return False  # [..., b] is NOT subset of [..., b)

        return True

    def is_disjoint_from(self, other: Interval) -> bool:
        """Return True if self and other do not intersect (self ∩ other = ∅)."""
        if self.dimension != other.dimension:
            return True

        if self.upper < other.lower or other.upper < self.lower:
            return True
        if self.upper == other.lower and (not self.right_closed or not other.left_closed):
            return True
        if other.upper == self.lower and (not other.right_closed or not self.left_closed):
            return True
        return False

    def __str__(self) -> str:
        left = "[" if self.left_closed else "("
        right = "]" if self.right_closed else ")"
        return f"{left}{self.lower}, {self.upper}{right} {self.dimension}"


# ---------------------------------------------------------------------------
# Regulatory Bound Parsing & Extraction
# ---------------------------------------------------------------------------

_LOWER_BOUND_PATTERNS = [
    re.compile(
        r"\b(?:at least|a minimum of|minimum of|minimum|not less than|no less than|"
        r"not fall below|not drop below|greater than or equal to|>=|≥)\s+"
        r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:greater than|more than|exceeding|above|>)\s+"
        r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?",
        re.IGNORECASE,
    ),
]

_UPPER_BOUND_PATTERNS = [
    re.compile(
        r"\b(?:at most|a maximum of|maximum of|maximum|not exceeding|not to exceed|"
        r"not exceed|no more than|no greater than|no higher than|less than or equal to|<=|≤)\s+"
        r"(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:within)\s+(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:less than|under|below|<)\s+(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?",
        re.IGNORECASE,
    ),
]

_RANGE_PATTERNS = [
    re.compile(
        r"\b(?:between)\s+(?P<val1>\d+(?:\.\d+)?)\s*(?:and|to)\s*"
        r"(?P<val2>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:from)\s+(?P<val1>\d+(?:\.\d+)?)\s*(?:to)\s*"
        r"(?P<val2>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?P<val1>\d+(?:\.\d+)?)\s*-\s*(?P<val2>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)",
        re.IGNORECASE,
    ),
]

_TOLERANCE_PATTERNS = [
    re.compile(
        r"\b(?P<val>\d+(?:\.\d+)?)\s*(?:±|\+/-)\s*(?P<tol>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?",
        re.IGNORECASE,
    ),
]


def extract_interval_from_text(text: str) -> Interval | None:
    """Extract a normalized mathematical Interval from natural language text."""
    # 1. Check Range Patterns (between A and B)
    for pat in _RANGE_PATTERNS:
        match = pat.search(text)
        if match:
            v1_raw = float(match.group("val1"))
            v2_raw = float(match.group("val2"))
            unit = match.group("unit")
            v1, dim1 = normalize_quantity_to_base(v1_raw, unit)
            v2, dim2 = normalize_quantity_to_base(v2_raw, unit)
            if dim1 == dim2:
                low = min(v1, v2)
                high = max(v1, v2)
                return Interval.closed(low, high, dimension=dim1)

    # 2. Check Tolerance Patterns (A ± T)
    for pat in _TOLERANCE_PATTERNS:
        match = pat.search(text)
        if match:
            v_raw = float(match.group("val"))
            t_raw = float(match.group("tol"))
            unit = match.group("unit")
            v, dim1 = normalize_quantity_to_base(v_raw, unit)
            t, _ = normalize_quantity_to_base(t_raw, unit)
            return Interval.closed(v - t, v + t, dimension=dim1)

    # 3. Check Lower Bound Patterns
    for pat in _LOWER_BOUND_PATTERNS:
        match = pat.search(text)
        if match:
            v_raw = float(match.group("val"))
            unit = match.group("unit")
            v, dim = normalize_quantity_to_base(v_raw, unit)
            strict = any(
                w in match.group(0).lower()
                for w in ("greater than", "more than", "exceeding", "above", ">")
            )
            if strict and not any(w in match.group(0).lower() for w in (">=", "≥", "equal")):
                return Interval.greater_than(v, dimension=dim)
            return Interval.at_least(v, dimension=dim)

    # 4. Check Upper Bound Patterns
    for pat in _UPPER_BOUND_PATTERNS:
        match = pat.search(text)
        if match:
            v_raw = float(match.group("val"))
            unit = match.group("unit")
            v, dim = normalize_quantity_to_base(v_raw, unit)
            if "within" in match.group(0).lower() and dim in ("time_s", "mass_g", "volume_ml"):
                # Within X is a non-negative range [0, X]
                return Interval.closed(0.0, v, dimension=dim)
            strict = any(w in match.group(0).lower() for w in ("less than", "under", "below", "<"))
            if strict and not any(w in match.group(0).lower() for w in ("<=", "≤", "equal")):
                return Interval.less_than(v, dimension=dim)
            return Interval.at_most(v, dimension=dim)

    # 5. Point Quantity Fallback
    point_match = re.search(r"\b(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?\b", text)
    if point_match:
        val_str = point_match.group("val")
        unit = point_match.group("unit")
        if unit and unit.lower() in ("cfr", "part", "annex", "ch", "suite", "lot", "line"):
            # Entity identifier or regulation citation, not a measurement
            return None
        v_raw = float(val_str)
        v, dim = normalize_quantity_to_base(v_raw, unit)
        return Interval.point(v, dimension=dim)

    return None


@dataclass(frozen=True)
class IntervalAssessment:
    """Deterministic result of evaluating claim interval against evidence interval."""

    status: IntervalStatus
    claim_interval: str | None
    evidence_interval: str | None
    reason: str
    verdict_impact: Literal["supported", "contradicted", "not_checkable"] | None


def evaluate_interval_containment(
    claim_text: str,
    evidence_text: str,
) -> IntervalAssessment:
    """Evaluate mathematical containment between claim quantity bounds and evidence bounds.

    For prescriptive / specification assertions:
    - If Evidence is a subset of Claim Interval (I_evidence ⊆ I_claim) -> Satisfied.
    - If Evidence is disjoint from Claim Interval (I_evidence ∩ I_claim = ∅) -> Violated.
    - Otherwise -> Incomparable / Inconclusive.
    """
    claim_iv = extract_interval_from_text(claim_text)
    if claim_iv is None:
        return IntervalAssessment(
            status="inconclusive",
            claim_interval=None,
            evidence_interval=None,
            reason="no quantitative bound extracted from claim",
            verdict_impact=None,
        )

    evidence_iv = extract_interval_from_text(evidence_text)
    if evidence_iv is None:
        return IntervalAssessment(
            status="inconclusive",
            claim_interval=str(claim_iv),
            evidence_interval=None,
            reason="claim specifies interval but no comparable interval found in evidence",
            verdict_impact=None,
        )

    if claim_iv.dimension != evidence_iv.dimension:
        return IntervalAssessment(
            status="incomparable",
            claim_interval=str(claim_iv),
            evidence_interval=str(evidence_iv),
            reason=(
                f"incompatible dimensions: claim ({claim_iv.dimension}) "
                f"vs evidence ({evidence_iv.dimension})"
            ),
            verdict_impact=None,
        )

    # 1. Check subset containment: Compliance with Evidence guarantees compliance with Claim
    if evidence_iv.is_subset_of(claim_iv):
        return IntervalAssessment(
            status="satisfied",
            claim_interval=str(claim_iv),
            evidence_interval=str(evidence_iv),
            reason=f"evidence interval {evidence_iv} satisfies asserted claim interval {claim_iv}",
            verdict_impact="supported",
        )

    # 2. Check disjointness: Evidence directly excludes the asserted interval
    if evidence_iv.is_disjoint_from(claim_iv):
        return IntervalAssessment(
            status="violated",
            claim_interval=str(claim_iv),
            evidence_interval=str(evidence_iv),
            reason=(
                f"evidence interval {evidence_iv} directly violates "
                f"asserted claim interval {claim_iv}"
            ),
            verdict_impact="contradicted",
        )

    # 3. Partial overlap or loose specification
    return IntervalAssessment(
        status="inconclusive",
        claim_interval=str(claim_iv),
        evidence_interval=str(evidence_iv),
        reason=(
            f"partial overlap between claim interval {claim_iv} "
            f"and evidence interval {evidence_iv}"
        ),
        verdict_impact="not_checkable",
    )


__all__ = [
    "Interval",
    "IntervalAssessment",
    "IntervalStatus",
    "evaluate_interval_containment",
    "extract_interval_from_text",
    "normalize_quantity_to_base",
]
