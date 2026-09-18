"""Frozen evaluator for event-occurrence Gate-1B authority RC0."""

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from research.event_occurrence_measurement_machinery_rc0.candidate import (
    conservative_event_hybrid,
)
from research.event_occurrence_measurement_machinery_rc0.cohort import (
    EventAtom,
    Polarity,
    Status,
)

from .cohort import CLEAN, CleanCase


AuthorityCandidate = Callable[[str, EventAtom], object]


def _measured(case: CleanCase) -> EventAtom:
    observation = conservative_event_hybrid(case.text)
    if observation.status is not Status.CLAIMED or observation.atom is None:
        raise AssertionError(f"frozen clean measurement did not claim: {case.case_id}")
    return observation.atom


CLEAN_BY_ID = {case.case_id: case for case in CLEAN}


@dataclass(frozen=True, slots=True)
class MutationCase:
    case_id: str
    source_case_id: str
    mutated_atom: EventAtom


EW01 = _measured(CLEAN_BY_ID["EW01"])
EW02 = _measured(CLEAN_BY_ID["EW02"])
EW06 = _measured(CLEAN_BY_ID["EW06"])

MUTATIONS: tuple[MutationCase, ...] = (
    MutationCase("EMUT01", "EW01", replace(EW01, actor="ops")),
    MutationCase("EMUT02", "EW01", replace(EW01, action="release")),
    MutationCase("EMUT03", "EW01", replace(EW01, object="record")),
    MutationCase(
        "EMUT04",
        "EW01",
        replace(EW01, polarity=Polarity.DID_NOT_OCCUR),
    ),
    MutationCase(
        "EMUT05",
        "EW02",
        replace(EW02, polarity=Polarity.OCCURRED),
    ),
    MutationCase("EMUT06", "EW06", replace(EW06, time=None)),
    MutationCase("EMUT07", "EW01", replace(EW01, time="T1")),
    MutationCase("EMUT08", "EW01", replace(EW01, scope="REPORTED")),
)


@dataclass(frozen=True, slots=True)
class Observation:
    case_id: str
    authority_status: str


def observe_clean(case: CleanCase, candidate: AuthorityCandidate) -> Observation:
    measured = _measured(case)
    try:
        candidate(case.text, measured)
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
        candidate(source.text, case.mutated_atom)
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


def weak_trust_measurement(text: str, measured: EventAtom) -> object:
    del text
    return measured
