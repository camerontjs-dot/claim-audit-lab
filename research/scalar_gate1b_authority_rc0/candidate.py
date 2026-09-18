"""Independent source completion for bounded scalar Gate-1B RC0."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from fractions import Fraction

from research.scalar_measurement_machinery_rc0.cohort import (
    ScalarAtom,
    Target,
)


@dataclass(frozen=True, slots=True)
class ScalarAuthority:
    atom: ScalarAtom
    source_sha256: str
    status: str = "WARRANTED"


def _clean(text: str) -> str:
    compact = " ".join(text.strip().split())
    return compact[:-1] if compact.endswith(".") else compact


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def _point(
    target: Target,
    value: Fraction,
    *,
    exact: bool = True,
) -> ScalarAtom:
    return ScalarAtom(
        target.entity,
        target.metric,
        target.unit,
        value,
        value,
        exact,
    )


def _interval(
    target: Target,
    low: Fraction,
    high: Fraction,
    *,
    exact: bool = True,
) -> ScalarAtom:
    return ScalarAtom(
        target.entity,
        target.metric,
        target.unit,
        low,
        high,
        exact,
    )


def _source_atom(text: str, target: Target) -> ScalarAtom:
    compact = _clean(text)

    if target.entity != "batch":
        raise ValueError("unsupported scalar target entity")

    if target.metric == "yield" and target.unit == "%":
        exact_point = re.fullmatch(
            r"Batch yield was (?P<value>-?\d+(?:\.\d+)?)%",
            compact,
            re.IGNORECASE,
        )
        if exact_point is not None:
            return _point(target, _fraction(exact_point.group("value")))

        closed_range = re.fullmatch(
            r"Batch yield was between "
            r"(?P<low>-?\d+(?:\.\d+)?)% and "
            r"(?P<high>-?\d+(?:\.\d+)?)%",
            compact,
            re.IGNORECASE,
        )
        if closed_range is not None:
            return _interval(
                target,
                _fraction(closed_range.group("low")),
                _fraction(closed_range.group("high")),
            )

        approximate = re.fullmatch(
            r"Batch yield was approximately "
            r"(?P<value>-?\d+(?:\.\d+)?)%",
            compact,
            re.IGNORECASE,
        )
        if approximate is not None:
            return _point(
                target,
                _fraction(approximate.group("value")),
                exact=False,
            )

        terse = re.fullmatch(
            r"Batch yield:\s*(?P<value>-?\d+(?:\.\d+)?)%",
            compact,
            re.IGNORECASE,
        )
        if terse is not None:
            return _point(target, _fraction(terse.group("value")))

        plus_minus = re.fullmatch(
            r"Batch yield was "
            r"(?P<center>-?\d+(?:\.\d+)?)\s*±\s*"
            r"(?P<radius>\d+(?:\.\d+)?)%",
            compact,
            re.IGNORECASE,
        )
        if plus_minus is not None:
            center = _fraction(plus_minus.group("center"))
            radius = _fraction(plus_minus.group("radius"))
            return _interval(
                target,
                center - radius,
                center + radius,
                exact=False,
            )

    if target.metric == "count" and target.unit == "count":
        count = re.fullmatch(
            r"Batch count was (?P<value>-?\d+(?:\.\d+)?)",
            compact,
            re.IGNORECASE,
        )
        if count is not None:
            return _point(target, _fraction(count.group("value")))

    if target.metric == "temperature" and target.unit in {"degC", "degF"}:
        surface_unit = "°C" if target.unit == "degC" else "°F"
        temperature = re.fullmatch(
            rf"Batch temperature was "
            rf"(?P<value>-?\d+(?:\.\d+)?)\s*{re.escape(surface_unit)}",
            compact,
            re.IGNORECASE,
        )
        if temperature is not None:
            return _point(
                target,
                _fraction(temperature.group("value")),
            )

    raise ValueError("scalar source not independently reconstructable")


def complete_and_warrant_scalar(
    text: str,
    target: Target,
    measured: ScalarAtom,
) -> ScalarAuthority:
    completed = _source_atom(text, target)
    if completed != measured:
        raise ValueError("measurement/source semantic mismatch")
    return ScalarAuthority(
        atom=completed,
        source_sha256=hashlib.sha256(text.encode()).hexdigest(),
    )
