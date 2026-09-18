"""Frozen evaluator for typed-binary Gate-1B authority RC1."""

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from research.typed_binary_measurement_machinery_rc1.candidate import (
    conservative_relation_hybrid,
)
from research.typed_binary_measurement_machinery_rc1.cohort import (
    RelationAtom,
    Status,
)

from .cohort import CLEAN, CleanCase

AuthorityCandidate = Callable[[str, RelationAtom], object]


def _measured(case: CleanCase) -> RelationAtom:
    observed = conservative_relation_hybrid(case.text)
    if observed.status is not Status.CLAIMED or observed.atom is None:
        raise AssertionError(case.case_id)
    return observed.atom


BY_ID = {case.case_id: case for case in CLEAN}


@dataclass(frozen=True, slots=True)
class MutationCase:
    case_id: str
    source_case_id: str
    atom: RelationAtom


T1 = _measured(BY_ID["TW01"])
T3 = _measured(BY_ID["TW03"])
T4 = _measured(BY_ID["TW04"])
T6 = _measured(BY_ID["TW06"])

MUTATIONS: tuple[MutationCase, ...] = (
    MutationCase("TMUT01", "TW01", replace(T1, subject="b")),
    MutationCase("TMUT02", "TW01", replace(T1, object="a")),
    MutationCase("TMUT03", "TW01", replace(T1, predicate="OWNED_BY")),
    MutationCase("TMUT04", "TW01", replace(T1, positive=False)),
    MutationCase("TMUT05", "TW03", replace(T3, predicate="NORTH_OF")),
    MutationCase("TMUT06", "TW04", replace(T4, predicate="SOUTH_OF")),
    MutationCase("TMUT07", "TW06", replace(T6, predicate="CONTAINS")),
    MutationCase("TMUT08", "TW06", replace(T6, subject="zone", object="room")),
)


def _status(text: str, atom: RelationAtom, candidate: AuthorityCandidate) -> str:
    try:
        candidate(text, atom)
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
        if _status(source.text, case.atom, candidate) != "REFUSED":
            result.append(f"{case.case_id}:mutation-warranted")
    return tuple(result)


def weak_trust_measurement(text: str, measured: RelationAtom) -> object:
    del text
    return measured
