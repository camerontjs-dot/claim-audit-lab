"""Competing proposal instruments for CAL Scalar Measurement Machinery RC0."""

from __future__ import annotations

import re
from fractions import Fraction

from .cohort import Observation, ScalarAtom, Status, Target


def _clean(text: str) -> str:
    return " ".join(text.strip().split()).removesuffix(".")


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def _surface_unit(unit: str) -> str:
    return {
        "%": "%",
        "count": "",
        "degC": "°C",
        "degF": "°F",
        "mg": "mg",
        "min": "min",
    }[unit]


def _metric_surface(metric: str) -> str:
    return {
        "yield": "yield",
        "count": "count",
        "temperature": "temperature",
        "mass": "mass",
        "duration": "duration",
    }[metric]


def _hard_hazard(text: str) -> str | None:
    low = text.casefold()
    if re.search(r"\b(report|study|article)\b.*\b(says?|said|states?|reported|claims?)\b", low):
        return "reporting scope"
    if " may be " in f" {low} ":
        return "epistemic modality"
    if " or " in f" {low} ":
        return "disjunction"
    if " at t1 " in f" {low} " or " at t2 " in f" {low} ":
        return "multiple temporal states"
    if re.search(r"\b(increased|decreased|changed|rose|fell)\b", low):
        return "quantitative change"
    if "more than" in low or "less than" in low or "at least" in low or "at most" in low:
        return "open inequality"
    if re.search(r"\bversion\b", low):
        return "version number"
    return None


def _point(target: Target, value: Fraction, *, exact: bool = True) -> Observation:
    return Observation.claimed(
        ScalarAtom(target.entity, target.metric, target.unit, value, value, exact)
    )


def _interval(
    target: Target,
    low: Fraction,
    high: Fraction,
    *,
    exact: bool = True,
) -> Observation:
    return Observation.claimed(
        ScalarAtom(target.entity, target.metric, target.unit, low, high, exact)
    )


def _target_prefix(target: Target) -> str:
    if target.entity != "batch":
        return ""
    return f"Batch {_metric_surface(target.metric)}"


def direct_numeric_grammar(text: str, target: Target) -> Observation:
    """Bounded target-aware numeric parser for exact points and closed intervals."""

    compact = _clean(text)
    hazard = _hard_hazard(compact)
    if hazard is not None:
        return Observation.unresolved(hazard)

    prefix = _target_prefix(target)
    if not prefix:
        return Observation.unresolved("unsupported target entity")

    unit = re.escape(_surface_unit(target.unit))
    value = r"(?P<value>-?\d+(?:\.\d+)?)"

    if target.unit == "count":
        point_pattern = rf"{re.escape(prefix)} was {value}"
    else:
        point_pattern = rf"{re.escape(prefix)} was {value}\s*{unit}"

    match = re.fullmatch(point_pattern, compact, re.IGNORECASE)
    if match is not None:
        return _point(target, _fraction(match.group("value")))

    if target.unit == "%":
        measured = re.fullmatch(
            rf"The batch yield measured {value}%",
            compact,
            re.IGNORECASE,
        )
        if measured is not None and target.metric == "yield":
            return _point(target, _fraction(measured.group("value")))

    low_high = r"(?P<low>-?\d+(?:\.\d+)?)"
    high = r"(?P<high>-?\d+(?:\.\d+)?)"
    between = re.fullmatch(
        rf"{re.escape(prefix)} was between {low_high}\s*{unit} and {high}\s*{unit}",
        compact,
        re.IGNORECASE,
    )
    if between is not None:
        return _interval(
            target,
            _fraction(between.group("low")),
            _fraction(between.group("high")),
        )

    ranged = re.fullmatch(
        rf"{re.escape(prefix)} ranged from {low_high}\s*{unit} to {high}\s*{unit}",
        compact,
        re.IGNORECASE,
    )
    if ranged is not None:
        return _interval(
            target,
            _fraction(ranged.group("low")),
            _fraction(ranged.group("high")),
        )

    # A numeric statement about another target is unresolved, never rebound.
    if re.search(r"-?\d+(?:\.\d+)?", compact):
        return Observation.unresolved("numeric surface does not bind exact target")
    return Observation.not_applicable("no scalar surface")


def broad_number_grabber(text: str, target: Target) -> Observation:
    """Deliberately broad numeric extractor used as a weak competing instrument."""

    values = re.findall(r"-?\d+(?:\.\d+)?", text)
    if not values:
        return Observation.not_applicable("no number")
    value = _fraction(values[0])
    return _point(target, value)


def _diagnostic_extension(text: str, target: Target) -> Observation:
    compact = _clean(text)

    if target == Target("batch", "yield", "%"):
        approx = re.fullmatch(
            r"Batch yield was approximately (?P<value>\d+(?:\.\d+)?)%",
            compact,
            re.IGNORECASE,
        )
        if approx is not None:
            return _point(target, _fraction(approx.group("value")), exact=False)

        about = re.fullmatch(
            r"Batch yield was about (?P<value>\d+(?:\.\d+)?) percent",
            compact,
            re.IGNORECASE,
        )
        if about is not None:
            return _point(target, _fraction(about.group("value")), exact=False)

        terse = re.fullmatch(
            r"Batch yield:\s*(?P<value>\d+(?:\.\d+)?)%",
            compact,
            re.IGNORECASE,
        )
        if terse is not None:
            return _point(target, _fraction(terse.group("value")))

        alternate = re.fullmatch(
            r"The yield of the batch was (?P<value>\d+(?:\.\d+)?)%",
            compact,
            re.IGNORECASE,
        )
        if alternate is not None:
            return _point(target, _fraction(alternate.group("value")))

        plus_minus = re.fullmatch(
            r"Batch yield was (?P<center>\d+(?:\.\d+)?) ± "
            r"(?P<radius>\d+(?:\.\d+)?)%",
            compact,
            re.IGNORECASE,
        )
        if plus_minus is not None:
            center = _fraction(plus_minus.group("center"))
            radius = _fraction(plus_minus.group("radius"))
            return _interval(target, center - radius, center + radius, exact=False)

    if target == Target("batch", "temperature", "degF"):
        fahrenheit = re.fullmatch(
            r"Batch temperature was (?P<value>-?\d+(?:\.\d+)?)\s*°F",
            compact,
            re.IGNORECASE,
        )
        if fahrenheit is not None:
            return _point(target, _fraction(fahrenheit.group("value")))

    return Observation.unresolved("outside bounded diagnostic extensions")


def conservative_numeric_hybrid(text: str, target: Target) -> Observation:
    """Use exact grammar first, then only preregistered safe numeric extensions."""

    direct = direct_numeric_grammar(text, target)
    if direct.status is Status.CLAIMED:
        return direct
    if _hard_hazard(_clean(text)) is not None:
        return direct
    return _diagnostic_extension(text, target)


INSTRUMENTS = {
    "direct_numeric_grammar": direct_numeric_grammar,
    "broad_number_grabber": broad_number_grabber,
    "conservative_numeric_hybrid": conservative_numeric_hybrid,
}
