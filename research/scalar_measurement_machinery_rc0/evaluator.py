"""Frozen evaluator for CAL Scalar Measurement Machinery RC0."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction

from .cohort import (
    BATCH_YIELD,
    Bucket,
    CASES,
    CASES_BY_ID,
    METAMORPHIC_PAIRS,
    Observation,
    ScalarAtom,
    Status,
    Target,
)

Strategy = Callable[[str, Target], Observation]


@dataclass(frozen=True, slots=True)
class Report:
    must_handle_failures: tuple[str, ...]
    fail_closed_unsafe: tuple[str, ...]
    diagnostic_wrong_claims: tuple[str, ...]
    diagnostic_exact: tuple[str, ...]
    diagnostic_unresolved: tuple[str, ...]
    diagnostic_not_applicable: tuple[str, ...]

    @property
    def qualifiable(self) -> bool:
        return (
            not self.must_handle_failures
            and not self.fail_closed_unsafe
            and not self.diagnostic_wrong_claims
        )


def evaluate(strategy: Strategy) -> Report:
    must: list[str] = []
    unsafe: list[str] = []
    wrong: list[str] = []
    exact: list[str] = []
    unresolved: list[str] = []
    not_applicable: list[str] = []

    for case in CASES:
        observed = strategy(case.text, case.target)
        if case.bucket is Bucket.MUST_HANDLE:
            if observed.status is not Status.CLAIMED or observed.atom != case.expected:
                must.append(case.case_id)
        elif case.bucket is Bucket.FAIL_CLOSED:
            if observed.status is Status.CLAIMED:
                unsafe.append(case.case_id)
        elif observed.status is Status.CLAIMED:
            if observed.atom == case.expected:
                exact.append(case.case_id)
            else:
                wrong.append(case.case_id)
        elif observed.status is Status.UNRESOLVED:
            unresolved.append(case.case_id)
        else:
            not_applicable.append(case.case_id)

    return Report(
        tuple(must),
        tuple(unsafe),
        tuple(wrong),
        tuple(exact),
        tuple(unresolved),
        tuple(not_applicable),
    )


def metamorphic_failures(strategy: Strategy) -> tuple[str, ...]:
    failures: list[str] = []
    for left_id, right_id in METAMORPHIC_PAIRS:
        left = CASES_BY_ID[left_id]
        right = CASES_BY_ID[right_id]
        left_obs = strategy(left.text, left.target)
        right_obs = strategy(right.text, right.target)
        if left_obs.status is not Status.CLAIMED or left_obs.atom != left.expected:
            failures.append(f"{left_id}->{right_id}:left")
        elif right.bucket is Bucket.DIAGNOSTIC:
            if right_obs.status is Status.CLAIMED and right_obs.atom != right.expected:
                failures.append(f"{left_id}->{right_id}:wrong-right")
        elif right_obs.status is Status.CLAIMED:
            failures.append(f"{left_id}->{right_id}:unsafe-right")
    return tuple(failures)


def _first_number(text: str) -> Fraction | None:
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if match is None:
        return None
    return Fraction(match.group(0))


def weak_first_number(text: str, target: Target) -> Observation:
    value = _first_number(text)
    if value is None:
        return Observation.not_applicable("weak")
    return Observation.claimed(
        ScalarAtom(target.entity, target.metric, target.unit, value, value, True)
    )


def weak_ignore_unit(text: str, target: Target) -> Observation:
    value = _first_number(text)
    if value is None or "yield" not in text.casefold():
        return Observation.unresolved("weak")
    return Observation.claimed(
        ScalarAtom(target.entity, target.metric, target.unit, value, value, True)
    )


def weak_ignore_target_binding(text: str, target: Target) -> Observation:
    value = _first_number(text)
    if value is None:
        return Observation.unresolved("weak")
    return Observation.claimed(
        ScalarAtom(target.entity, target.metric, target.unit, value, value, True)
    )


def weak_approx_exact(text: str, target: Target) -> Observation:
    if "approximately" not in text.casefold() and "about" not in text.casefold():
        return Observation.unresolved("weak")
    value = _first_number(text)
    assert value is not None
    return Observation.claimed(
        ScalarAtom(target.entity, target.metric, target.unit, value, value, True)
    )


def weak_range_midpoint(text: str, target: Target) -> Observation:
    values = [Fraction(value) for value in re.findall(r"\d+(?:\.\d+)?", text)]
    if len(values) != 2:
        return Observation.unresolved("weak")
    midpoint = (values[0] + values[1]) / 2
    return Observation.claimed(
        ScalarAtom(target.entity, target.metric, target.unit, midpoint, midpoint, True)
    )


assert BATCH_YIELD.unit == "%"
