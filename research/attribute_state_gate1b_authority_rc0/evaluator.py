"""Frozen evaluator for attribute-state Gate-1B authority RC0."""

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from research.attribute_state_measurement_machinery_rc1.candidate import (
    conservative_state_hybrid,
)
from research.attribute_state_measurement_machinery_rc1.cohort import (
    StateAtom,
    Status,
)

from .cohort import CLEAN, CleanCase

AuthorityCandidate = Callable[[str, StateAtom], object]


def _measured(case: CleanCase) -> StateAtom:
    observed = conservative_state_hybrid(case.text)
    if observed.status is not Status.CLAIMED or observed.atom is None:
        raise AssertionError(case.case_id)
    return observed.atom


BY_ID = {case.case_id: case for case in CLEAN}


@dataclass(frozen=True, slots=True)
class MutationCase:
    case_id: str
    source_case_id: str
    mutated_atom: StateAtom


A1 = _measured(BY_ID["AW01"])
A3 = _measured(BY_ID["AW03"])
A4 = _measured(BY_ID["AW04"])
A11 = _measured(BY_ID["AW11"])

MUTATIONS: tuple[MutationCase, ...] = (
    MutationCase("AMUT01", "AW01", replace(A1, entity="other_batch")),
    MutationCase("AMUT02", "AW01", replace(A1, attribute="mode")),
    MutationCase("AMUT03", "AW01", replace(A1, domain="document_status")),
    MutationCase("AMUT04", "AW01", replace(A1, value="held")),
    MutationCase("AMUT05", "AW01", replace(A1, functional=False)),
    MutationCase("AMUT06", "AW03", replace(A3, value="active")),
    MutationCase("AMUT07", "AW04", replace(A4, functional=True)),
    MutationCase("AMUT08", "AW11", replace(A11, entity="batch")),
)


def _status(text: str, measured: StateAtom, candidate: AuthorityCandidate) -> str:
    try:
        candidate(text, measured)
    except Exception:
        return "REFUSED"
    return "WARRANTED"


def failures(candidate: AuthorityCandidate) -> tuple[str, ...]:
    result: list[str] = []
    for case in CLEAN:
        if _status(case.text, _measured(case), candidate) != "WARRANTED":
            result.append(f"{case.case_id}:clean-refused")
    for case in MUTATIONS:
        source = BY_ID[case.source_case_id]
        if _status(source.text, case.mutated_atom, candidate) != "REFUSED":
            result.append(f"{case.case_id}:mutation-warranted")
    return tuple(result)


def weak_trust_measurement(text: str, measured: StateAtom) -> object:
    del text
    return measured
