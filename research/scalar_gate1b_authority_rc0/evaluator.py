"""Frozen evaluator for scalar Gate-1B authority RC0."""

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from fractions import Fraction

from research.scalar_measurement_machinery_rc0.candidate import (
    conservative_numeric_hybrid,
)
from research.scalar_measurement_machinery_rc0.cohort import (
    BATCH_YIELD,
    ScalarAtom,
    Status,
    Target,
)

from .cohort import CLEAN, CleanCase


AuthorityCandidate = Callable[[str, Target, ScalarAtom], object]


def _measured(case: CleanCase) -> ScalarAtom:
    observation = conservative_numeric_hybrid(case.text, case.target)
    if observation.status is not Status.CLAIMED or observation.atom is None:
        raise AssertionError(f"frozen clean measurement did not claim: {case.case_id}")
    return observation.atom


CLEAN_BY_ID = {case.case_id: case for case in CLEAN}


@dataclass(frozen=True, slots=True)
class MutationCase:
    case_id: str
    source_case_id: str
    mutated_atom: ScalarAtom


SW01 = _measured(CLEAN_BY_ID["SW01"])
SW03 = _measured(CLEAN_BY_ID["SW03"])
SW06 = _measured(CLEAN_BY_ID["SW06"])
SW09 = _measured(CLEAN_BY_ID["SW09"])

MUTATIONS: tuple[MutationCase, ...] = (
    MutationCase("SMUT01", "SW01", replace(SW01, entity="other_batch")),
    MutationCase("SMUT02", "SW01", replace(SW01, metric="count")),
    MutationCase("SMUT03", "SW01", replace(SW01, unit="fraction")),
    MutationCase(
        "SMUT04",
        "SW01",
        replace(SW01, low=Fraction(93), high=Fraction(93)),
    ),
    MutationCase(
        "SMUT05",
        "SW03",
        replace(SW03, low=Fraction(91)),
    ),
    MutationCase(
        "SMUT06",
        "SW03",
        replace(SW03, high=Fraction(95)),
    ),
    MutationCase(
        "SMUT07",
        "SW06",
        replace(SW06, exact=True),
    ),
    MutationCase(
        "SMUT08",
        "SW09",
        replace(SW09, exact=True),
    ),
    MutationCase(
        "SMUT09",
        "SW01",
        replace(
            SW01,
            entity=BATCH_YIELD.entity,
            metric=BATCH_YIELD.metric,
            unit=BATCH_YIELD.unit,
            low=Fraction(91),
            high=Fraction(93),
            exact=False,
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class Observation:
    case_id: str
    authority_status: str


def observe_clean(case: CleanCase, candidate: AuthorityCandidate) -> Observation:
    measured = _measured(case)
    try:
        candidate(case.text, case.target, measured)
    except Exception:
        status = "REFUSED"
    else:
        status = "WARRANTED"
    return Observation(case.case_id, status)


def observe_mutation(
    case: MutationCase,
    candidate: AuthorityCandidate,
) -> Observation:
    source = CLEAN_BY_ID[case.source_case_id]
    try:
        candidate(source.text, source.target, case.mutated_atom)
    except Exception:
        status = "REFUSED"
    else:
        status = "WARRANTED"
    return Observation(case.case_id, status)


def failures(candidate: AuthorityCandidate) -> tuple[str, ...]:
    result: list[str] = []
    for case in CLEAN:
        if observe_clean(case, candidate).authority_status != "WARRANTED":
            result.append(f"{case.case_id}:clean-refused")
    for case in MUTATIONS:
        if observe_mutation(case, candidate).authority_status != "REFUSED":
            result.append(f"{case.case_id}:mutation-warranted")
    return tuple(result)


def weak_trust_measurement(
    text: str,
    target: Target,
    measured: ScalarAtom,
) -> object:
    del text, target
    return measured
