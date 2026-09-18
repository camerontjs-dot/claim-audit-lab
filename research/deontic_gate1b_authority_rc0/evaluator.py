"""Frozen evaluator for deontic Gate-1B authority RC0."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from research.deontic_measurement_machinery_rc0.candidate import direct_grammar
from research.deontic_measurement_machinery_rc0.cohort import (
    APPROVE_RECORD,
    ARCHIVE_RECORD,
    QA,
    RELEASE_BATCH,
    TECH,
    Mode,
    Norm,
    Status,
)

from .cohort import CLEAN, CleanCase


AuthorityCandidate = Callable[[str, Norm], object]


@dataclass(frozen=True, slots=True)
class Observation:
    case_id: str
    measurement_claimed: bool
    authority_status: str


@dataclass(frozen=True, slots=True)
class MutationCase:
    case_id: str
    source_case_id: str
    mutated_norm: Norm


def _measured(case: CleanCase) -> Norm:
    observation = direct_grammar(case.text)
    if observation.status is not Status.CLAIMED or observation.norm is None:
        raise AssertionError(f"frozen clean measurement did not claim: {case.case_id}")
    return observation.norm


CLEAN_BY_ID = {case.case_id: case for case in CLEAN}

MUTATIONS: tuple[MutationCase, ...] = (
    MutationCase(
        "DMUT01",
        "DW01",
        replace(_measured(CLEAN_BY_ID["DW01"]), mode=Mode.OBLIGATORY),
    ),
    MutationCase(
        "DMUT02",
        "DW08",
        replace(_measured(CLEAN_BY_ID["DW08"]), subject=TECH),
    ),
    MutationCase(
        "DMUT03",
        "DW09",
        replace(_measured(CLEAN_BY_ID["DW09"]), action=RELEASE_BATCH),
    ),
    MutationCase(
        "DMUT04",
        "DW10",
        replace(_measured(CLEAN_BY_ID["DW10"]), condition=None),
    ),
    MutationCase(
        "DMUT05",
        "DW11",
        replace(
            _measured(CLEAN_BY_ID["DW11"]),
            temporal_relation=None,
            temporal_reference=None,
        ),
    ),
    MutationCase(
        "DMUT06",
        "DW13",
        replace(_measured(CLEAN_BY_ID["DW13"]), exceptions=()),
    ),
    MutationCase(
        "DMUT07",
        "DW14",
        replace(_measured(CLEAN_BY_ID["DW14"]), mode=Mode.PERMITTED),
    ),
    MutationCase(
        "DMUT08",
        "DW08",
        replace(_measured(CLEAN_BY_ID["DW08"]), action=ARCHIVE_RECORD),
    ),
    MutationCase(
        "DMUT09",
        "DW01",
        replace(_measured(CLEAN_BY_ID["DW01"]), subject=QA),
    ),
    MutationCase(
        "DMUT10",
        "DW08",
        replace(_measured(CLEAN_BY_ID["DW08"]), action=APPROVE_RECORD, subject=TECH),
    ),
)


def observe_clean(case: CleanCase, candidate: AuthorityCandidate) -> Observation:
    measured = _measured(case)
    try:
        candidate(case.text, measured)
    except Exception:
        status = "REFUSED"
    else:
        status = "WARRANTED"
    return Observation(case.case_id, True, status)


def observe_mutation(case: MutationCase, candidate: AuthorityCandidate) -> Observation:
    source = CLEAN_BY_ID[case.source_case_id]
    try:
        candidate(source.text, case.mutated_norm)
    except Exception:
        status = "REFUSED"
    else:
        status = "WARRANTED"
    return Observation(case.case_id, True, status)


def failures(candidate: AuthorityCandidate) -> tuple[str, ...]:
    result: list[str] = []
    for case in CLEAN:
        observed = observe_clean(case, candidate)
        if observed.authority_status != "WARRANTED":
            result.append(f"{case.case_id}:clean-refused")
    for case in MUTATIONS:
        observed = observe_mutation(case, candidate)
        if observed.authority_status != "REFUSED":
            result.append(f"{case.case_id}:mutation-warranted")
    return tuple(result)


def weak_trust_measurement(text: str, measured: Norm) -> object:
    del text
    return measured
