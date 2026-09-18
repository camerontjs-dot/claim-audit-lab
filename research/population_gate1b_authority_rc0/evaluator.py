"""Frozen evaluator for population/membership Gate-1B authority RC0."""

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from research.population_measurement_machinery_rc0.candidate import (
    conservative_hybrid,
)
from research.population_measurement_machinery_rc0.cohort import (
    ALICE,
    BOB,
    QUALIFIED_PERSONNEL,
    QUALIFIED_TECHNICIANS,
    REVIEWERS,
    STERILE_TECHNICIANS,
    TRAINED_PERSONNEL,
    Atom,
    MembershipAtom,
    MembershipStatus,
    Status,
    SubsetAtom,
)

from .cohort import CLEAN, CleanCase


AuthorityCandidate = Callable[[str, Atom], object]


def _measured(case: CleanCase) -> Atom:
    observation = conservative_hybrid(case.text)
    if observation.status is not Status.CLAIMED or observation.atom is None:
        raise AssertionError(f"frozen clean measurement did not claim: {case.case_id}")
    return observation.atom


CLEAN_BY_ID = {case.case_id: case for case in CLEAN}


@dataclass(frozen=True, slots=True)
class MutationCase:
    case_id: str
    source_case_id: str
    mutated_atom: Atom


PW01 = _measured(CLEAN_BY_ID["PW01"])
PW02 = _measured(CLEAN_BY_ID["PW02"])
PW04 = _measured(CLEAN_BY_ID["PW04"])
PW07 = _measured(CLEAN_BY_ID["PW07"])
PW08 = _measured(CLEAN_BY_ID["PW08"])

assert isinstance(PW01, MembershipAtom)
assert isinstance(PW02, MembershipAtom)
assert isinstance(PW04, SubsetAtom)
assert isinstance(PW07, MembershipAtom)
assert isinstance(PW08, MembershipAtom)

MUTATIONS: tuple[MutationCase, ...] = (
    MutationCase(
        "PMUT01",
        "PW01",
        replace(PW01, status=MembershipStatus.NON_MEMBER),
    ),
    MutationCase(
        "PMUT02",
        "PW02",
        replace(PW02, status=MembershipStatus.MEMBER),
    ),
    MutationCase("PMUT03", "PW01", replace(PW01, entity=BOB)),
    MutationCase(
        "PMUT04",
        "PW01",
        replace(PW01, population=REVIEWERS),
    ),
    MutationCase(
        "PMUT05",
        "PW04",
        replace(
            PW04,
            child=TRAINED_PERSONNEL,
            parent=STERILE_TECHNICIANS,
        ),
    ),
    MutationCase(
        "PMUT06",
        "PW04",
        replace(PW04, parent=QUALIFIED_PERSONNEL),
    ),
    MutationCase("PMUT07", "PW07", replace(PW07, entity=ALICE)),
    MutationCase(
        "PMUT08",
        "PW08",
        replace(PW08, population=QUALIFIED_TECHNICIANS),
    ),
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


def weak_trust_measurement(text: str, measured: Atom) -> object:
    del text
    return measured
