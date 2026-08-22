"""Deterministic Interval Algebra Operator for Claim Audit Lab v2.

Evaluates mathematical containment of asserted numeric intervals against
evidence-permitted intervals without delegating arithmetic to language models.

Addresses part of the D1 / D12 capability boundary:

- Replaces brittle heuristic overlap with interval subset containment.
- Distinguishes numeric measurements from entity identifiers.
- Normalizes physical units (time, temperature, mass, volume, percentage).

## What this operator cannot do, and why it abstains

It has **no measurand binding**: nothing here decides whether a bound found in a
passage is a bound *on the thing the claim is about*. A passage reading
"Ambient lab temperature must not exceed 22 °C. The product excursion reached
40 °C." carries two temperature bounds, and a bare first-match extractor reports
the first one and calls a 25 °C storage claim satisfied — a false *supported* on
evidence that in fact records a violation.

Until a measurand is bound, the only sound behaviour is to abstain whenever a
side carries more than one bound in the claim's dimension. That is what
``ambiguous`` is. It is a real abstention with a specific question attached, not
a failure, and it is why the pipeline treats this operator's output as advisory
rather than as a role veto (see ``pipeline_rules._q4_interval_containment``).

## Comparisons are tolerance-aware, not bit-exact

Unit normalization is multiplicative, so two spellings of one physical quantity
need not land on the same double: ``2.5 percent`` normalizes to ``0.025`` and
``25000 ppm`` to ``0.024999999999999998``. Comparing those with ``==`` made
containment depend on which spelling was the claim and which the evidence.
Endpoint comparisons therefore go through :func:`_eq` / :func:`_lt`, which are
relative-tolerance comparisons at :data:`_REL_TOL`.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

BoundKind = Literal[
    "exact", "at_least", "greater_than", "at_most", "less_than", "range", "tolerance", "unknown"
]
IntervalStatus = Literal["satisfied", "violated", "incomparable", "ambiguous", "inconclusive"]

#: Relative tolerance for endpoint comparison. Unit normalization is
#: multiplicative and therefore lossy in binary floating point; two spellings of
#: the same physical quantity can differ in the last ulp. Endpoints are compared
#: at this relative tolerance so containment does not depend on spelling.
_REL_TOL = 1e-9

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

_CELSIUS_NAMES = ("c", "celsius", "centigrade")
_FAHRENHEIT_NAMES = ("f", "fahrenheit")
_KELVIN_NAMES = ("k", "kelvin")

#: Dimensions this module recognizes as physical measurements. A point quantity
#: whose unit does not land in one of these is not treated as a measurement at
#: all; see :func:`_point_candidate`.
MEASUREMENT_DIMENSIONS = frozenset({"time_s", "mass_g", "volume_ml", "ratio_unit", "temp_c"})

#: Dimensions on which a bare "within X" denotes the range [0, X]. Time, mass and
#: volume are non-negative and "within 30 days" means "somewhere in the first 30
#: days". On a signed or anchored dimension "within 5 %" means "within ±5 % of a
#: target" and the target is not in the text, so no interval is emitted.
_WITHIN_NON_NEGATIVE_DIMENSIONS = frozenset({"time_s", "mass_g", "volume_ml"})


def _eq(a: float, b: float) -> bool:
    """Endpoint equality at the module's relative tolerance.

    ``math.isclose`` handles the infinite endpoints correctly: ``inf`` is close
    to ``inf`` and not to ``-inf``.
    """
    return math.isclose(a, b, rel_tol=_REL_TOL, abs_tol=0.0)


def _lt(a: float, b: float) -> bool:
    """True when ``a`` is below ``b`` by more than the module's tolerance."""
    return a < b and not _eq(a, b)


def _normalize_unit_name(unit: str) -> str:
    cleaned = unit.strip().lower().replace("°", "").replace("deg ", "").replace("degrees ", "")
    return cleaned


def normalize_quantity_to_base(value: float, unit: str | None) -> tuple[float, str]:
    """Convert a *point on a scale* to a canonical base dimension.

    For a difference on a scale — a tolerance, a span — use
    :func:`normalize_delta_to_base` instead. The two differ on temperature,
    where the conversion is affine rather than multiplicative.
    """
    if unit is None:
        return value, "scalar"
    u = _normalize_unit_name(unit)

    # Temperature (special non-multiplicative conversion)
    if u in _CELSIUS_NAMES:
        return value, "temp_c"
    if u in _FAHRENHEIT_NAMES:
        return (value - 32.0) * (5.0 / 9.0), "temp_c"
    if u in _KELVIN_NAMES:
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


def normalize_delta_to_base(value: float, unit: str | None) -> tuple[float, str]:
    """Convert a *difference* on a scale to a canonical base dimension.

    A tolerance is a width, not a position, so the affine temperature offsets
    must not be applied to it. ``±2 °F`` is a 1.11 °C-wide tolerance; running it
    through :func:`normalize_quantity_to_base` yields ``−16.67``, and
    ``98 ± 2 °F`` then constructs the inverted interval ``[53.33, 20.0]`` and
    raises. Every other dimension is multiplicative, where a difference and a
    position convert identically.
    """
    if unit is None:
        return value, "scalar"
    u = _normalize_unit_name(unit)
    if u in _CELSIUS_NAMES or u in _KELVIN_NAMES:
        return value, "temp_c"
    if u in _FAHRENHEIT_NAMES:
        return value * (5.0 / 9.0), "temp_c"
    return normalize_quantity_to_base(value, unit)


@dataclass(frozen=True)
class Interval:
    """Mathematical 1D continuous interval [lower, upper].

    Supports open and closed bounds, infinite endpoints, and set containment.

    Endpoint comparisons are tolerance-aware (see :data:`_REL_TOL`), so the
    containment relations below are decidable *to that tolerance* rather than
    bit-exact.
    """

    lower: float
    upper: float
    left_closed: bool = True
    right_closed: bool = True
    dimension: str = "scalar"

    def __post_init__(self) -> None:
        # Tolerance-aware so a last-ulp artefact of unit conversion is not fatal,
        # while a genuinely inverted interval still is.
        if _lt(self.upper, self.lower):
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

    def is_comparable_with(self, other: Interval) -> bool:
        """Return True when both intervals live on the same dimension.

        :meth:`is_subset_of` and :meth:`is_disjoint_from` are only meaningful for
        comparable intervals. Check this first; both relations answer ``False``
        for incomparable ones, which means "not established", not "established
        false".
        """
        return self.dimension == other.dimension

    def is_subset_of(self, other: Interval) -> bool:
        """Return True if self is a subset of other (self ⊆ other).

        False for incomparable dimensions: a mass is not a subset of a duration,
        but neither is it provably outside one.
        """
        if not self.is_comparable_with(other):
            return False

        if _lt(self.lower, other.lower):
            return False
        if _eq(self.lower, other.lower) and self.left_closed and not other.left_closed:
            return False  # [a, ...] is NOT a subset of (a, ...]

        if _lt(other.upper, self.upper):
            return False
        if _eq(self.upper, other.upper) and self.right_closed and not other.right_closed:
            return False  # [..., b] is NOT a subset of [..., b)

        return True

    def is_disjoint_from(self, other: Interval) -> bool:
        """Return True if self and other provably do not intersect.

        **False for incomparable dimensions.** Disjointness is a positive claim,
        and two intervals on different dimensions do not establish it — they are
        not comparable at all. Returning True here would let the natural caller
        idiom (``not subset and disjoint -> contradiction``) turn a unit mismatch
        into a contradiction.
        """
        if not self.is_comparable_with(other):
            return False

        if _lt(self.upper, other.lower) or _lt(other.upper, self.lower):
            return True
        if _eq(self.upper, other.lower) and (not self.right_closed or not other.left_closed):
            return True
        if _eq(other.upper, self.lower) and (not other.right_closed or not self.left_closed):
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

_POINT_PATTERNS = [re.compile(r"\b(?P<val>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%°]+)?\b")]

_STRICT_LOWER_WORDS = ("greater than", "more than", "exceeding", "above", ">")
_STRICT_UPPER_WORDS = ("less than", "under", "below", "<")
_INCLUSIVE_MARKERS = (">=", "≥", "<=", "≤", "equal")


def _range_candidate(match: re.Match[str]) -> Interval | None:
    # Both endpoints normalize through the pattern's single `unit` group, so they
    # always land on the same dimension; there is no mismatch branch to take.
    v1_raw = float(match.group("val1"))
    v2_raw = float(match.group("val2"))
    unit = match.group("unit")
    v1, dim = normalize_quantity_to_base(v1_raw, unit)
    v2, _ = normalize_quantity_to_base(v2_raw, unit)
    return Interval.closed(min(v1, v2), max(v1, v2), dimension=dim)


def _tolerance_candidate(match: re.Match[str]) -> Interval | None:
    v_raw = float(match.group("val"))
    t_raw = float(match.group("tol"))
    unit = match.group("unit")
    v, dim = normalize_quantity_to_base(v_raw, unit)
    # A tolerance is a width on the scale, not a position on it.
    t, _ = normalize_delta_to_base(t_raw, unit)
    return Interval.closed(v - abs(t), v + abs(t), dimension=dim)


def _lower_bound_candidate(match: re.Match[str]) -> Interval | None:
    v_raw = float(match.group("val"))
    unit = match.group("unit")
    v, dim = normalize_quantity_to_base(v_raw, unit)
    phrase = match.group(0).lower()
    strict = any(w in phrase for w in _STRICT_LOWER_WORDS)
    if strict and not any(w in phrase for w in _INCLUSIVE_MARKERS):
        return Interval.greater_than(v, dimension=dim)
    return Interval.at_least(v, dimension=dim)


def _upper_bound_candidate(match: re.Match[str]) -> Interval | None:
    v_raw = float(match.group("val"))
    unit = match.group("unit")
    v, dim = normalize_quantity_to_base(v_raw, unit)
    phrase = match.group(0).lower()
    if "within" in phrase:
        if dim not in _WITHIN_NON_NEGATIVE_DIMENSIONS:
            # "within 5 %" is a tolerance around a target the text does not name.
            return None
        return Interval.closed(0.0, v, dimension=dim)
    strict = any(w in phrase for w in _STRICT_UPPER_WORDS)
    if strict and not any(w in phrase for w in _INCLUSIVE_MARKERS):
        return Interval.less_than(v, dimension=dim)
    return Interval.at_most(v, dimension=dim)


def _point_candidate(match: re.Match[str]) -> Interval | None:
    """A bare quantity is a measurement only when its unit names a dimension.

    This is what separates ``37 °C`` from ``Part 11``, ``Suite S-12`` and
    ``Building 4``. An earlier denylist of identifier words (``cfr``, ``part``,
    ``annex``…) inspected only the token *following* the number, so it caught
    ``21 CFR`` and missed ``Part 11``, and any unrecognized following word
    became a bogus dimension: ``Batch 12 was held`` extracted
    ``[12.0, 12.0] was``. Requiring a recognized unit is the same guard stated
    positively, and it is total.
    """
    unit = match.group("unit")
    if unit is None:
        return None
    value, dim = normalize_quantity_to_base(float(match.group("val")), unit)
    if dim not in MEASUREMENT_DIMENSIONS:
        return None
    return Interval.point(value, dimension=dim)


#: Builds an interval from one regex match, or declines by returning None.
_CandidateBuilder = Callable[[re.Match[str]], "Interval | None"]

#: Extraction families in precedence order. A span consumed by a higher-priority
#: family is not offered to a lower one, so ``between 2 and 8 °C`` yields one
#: range rather than a range plus two points.
_EXTRACTORS: tuple[tuple[list[re.Pattern[str]], _CandidateBuilder], ...] = (
    (_RANGE_PATTERNS, _range_candidate),
    (_TOLERANCE_PATTERNS, _tolerance_candidate),
    (_LOWER_BOUND_PATTERNS, _lower_bound_candidate),
    (_UPPER_BOUND_PATTERNS, _upper_bound_candidate),
    (_POINT_PATTERNS, _point_candidate),
)


def _overlaps(span: tuple[int, int], consumed: list[tuple[int, int]]) -> bool:
    return any(span[0] < end and start < span[1] for start, end in consumed)


def extract_intervals_from_text(text: str) -> list[Interval]:
    """Extract **every** normalized interval the text carries, in text order.

    Precedence is by extraction family, but the returned order is the order the
    bounds appear in the sentence. The distinction matters: the previous
    first-match-wins extractor returned whichever family sat earliest in the
    pattern table, so ``less than 5 mg of reagent, completed within 30 days``
    returned the *duration*, because ``within`` preceded ``less than`` in the
    table rather than in the text.

    Total: never raises.
    """
    consumed: list[tuple[int, int]] = []
    found: list[tuple[int, Interval]] = []

    for patterns, build in _EXTRACTORS:
        for pattern in patterns:
            for match in pattern.finditer(text):
                span = match.span()
                if _overlaps(span, consumed):
                    continue
                # The span is claimed by this family whether or not it yields an
                # interval. Declining is a decision — "within 5 %" names no
                # usable bound — and a lower-priority family must not reinterpret
                # the same characters and override it.
                consumed.append(span)
                try:
                    candidate = build(match)
                except ValueError:
                    # A malformed interval is not a candidate. Recorded as absent
                    # rather than raised: extraction is total.
                    continue
                if candidate is None:
                    continue
                found.append((span[0], candidate))

    return [interval for _, interval in sorted(found, key=lambda pair: pair[0])]


def extract_interval_from_text(text: str) -> Interval | None:
    """Extract the first normalized interval the text carries, or None."""
    intervals = extract_intervals_from_text(text)
    return intervals[0] if intervals else None


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
    """Evaluate containment between claim quantity bounds and evidence bounds.

    For prescriptive / specification assertions:

    - Evidence is a subset of the claim interval (I_e ⊆ I_c) -> satisfied.
    - Evidence is disjoint from the claim interval (I_e ∩ I_c = ∅) -> violated.
    - More than one comparable bound on either side -> **ambiguous**, because
      nothing here binds a bound to a measurand.
    - Otherwise -> incomparable / inconclusive.

    Total: never raises. Every failure to decide is a status.
    """
    claim_intervals = extract_intervals_from_text(claim_text)
    if not claim_intervals:
        return IntervalAssessment(
            status="inconclusive",
            claim_interval=None,
            evidence_interval=None,
            reason="no quantitative bound extracted from claim",
            verdict_impact=None,
        )
    if len(claim_intervals) > 1:
        return IntervalAssessment(
            status="ambiguous",
            claim_interval="; ".join(str(i) for i in claim_intervals),
            evidence_interval=None,
            reason=(
                f"claim carries {len(claim_intervals)} bounds and nothing binds one to a "
                f"measurand; which bound is under audit is undetermined"
            ),
            verdict_impact=None,
        )

    claim_iv = claim_intervals[0]
    evidence_intervals = extract_intervals_from_text(evidence_text)
    comparable = [i for i in evidence_intervals if i.is_comparable_with(claim_iv)]

    if not comparable:
        if evidence_intervals:
            dims = ", ".join(sorted({i.dimension for i in evidence_intervals}))
            return IntervalAssessment(
                status="incomparable",
                claim_interval=str(claim_iv),
                evidence_interval="; ".join(str(i) for i in evidence_intervals),
                reason=(
                    f"incompatible dimensions: claim ({claim_iv.dimension}) vs evidence ({dims})"
                ),
                verdict_impact=None,
            )
        return IntervalAssessment(
            status="inconclusive",
            claim_interval=str(claim_iv),
            evidence_interval=None,
            reason="claim specifies interval but no comparable interval found in evidence",
            verdict_impact=None,
        )

    if len(comparable) > 1:
        # The false-supported case. Two bounds on the claim's dimension and no
        # way to tell which one is a bound on the claim's subject.
        return IntervalAssessment(
            status="ambiguous",
            claim_interval=str(claim_iv),
            evidence_interval="; ".join(str(i) for i in comparable),
            reason=(
                f"evidence carries {len(comparable)} bounds on the claim's dimension "
                f"({claim_iv.dimension}) and nothing binds one to the claim's measurand; "
                f"confirm which bound is the one under audit"
            ),
            verdict_impact=None,
        )

    evidence_iv = comparable[0]

    # 1. Subset containment: compliance with the evidence guarantees compliance
    #    with the claim.
    if evidence_iv.is_subset_of(claim_iv):
        return IntervalAssessment(
            status="satisfied",
            claim_interval=str(claim_iv),
            evidence_interval=str(evidence_iv),
            reason=f"evidence interval {evidence_iv} satisfies asserted claim interval {claim_iv}",
            verdict_impact="supported",
        )

    # 2. Disjointness: the evidence directly excludes the asserted interval.
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

    # 3. Partial overlap or loose specification.
    return IntervalAssessment(
        status="inconclusive",
        claim_interval=str(claim_iv),
        evidence_interval=str(evidence_iv),
        reason=(
            f"partial overlap between claim interval {claim_iv} and evidence interval {evidence_iv}"
        ),
        verdict_impact="not_checkable",
    )


__all__ = [
    "MEASUREMENT_DIMENSIONS",
    "Interval",
    "IntervalAssessment",
    "IntervalStatus",
    "evaluate_interval_containment",
    "extract_interval_from_text",
    "extract_intervals_from_text",
    "normalize_delta_to_base",
    "normalize_quantity_to_base",
]
