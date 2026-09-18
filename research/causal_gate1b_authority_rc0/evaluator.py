"""Frozen evaluator for explicit-causal-assertion Gate-1B authority RC0."""

# ruff: noqa: I001

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from research.causal_measurement_machinery_rc0.candidate import (
    conservative_assertion_hybrid,
)
from research.causal_measurement_machinery_rc0.cohort import (
    CausalAtom,
    Kind,
    Status,
)

from .cohort import CLEAN, CleanCase

AuthorityCandidate = Callable[[str, CausalAtom], object]


def _measured(case: CleanCase) -> CausalAtom:
    observed = conservative_assertion_hybrid(case.text)
    if observed.status is not Status.CLAIMED or observed.atom is None:
        raise AssertionError(case.case_id)
    return observed.atom


BY_ID = {case.case_id: case for case in CLEAN}


@dataclass(frozen=True, slots=True)
class MutationCase:
    case_id: str
    source_case_id: str
    atom: CausalAtom


C1 = _measured(BY_ID["CW01"])
C2 = _measured(BY_ID["CW02"])
C4 = _measured(BY_ID["CW04"])
C5 = _measured(BY_ID["CW05"])

MUTATIONS: tuple[MutationCase, ...] = (
    MutationCase("CMUT01", "CW01", replace(C1, cause="b")),
    MutationCase("CMUT02", "CW01", replace(C1, effect="a")),
    MutationCase("CMUT03", "CW01", replace(C1, kind=Kind.CONTRIBUTES_TO)),
    MutationCase("CMUT04", "CW02", replace(C2, kind=Kind.CAUSES)),
    MutationCase("CMUT05", "CW04", replace(C4, kind=Kind.CAUSES)),
    MutationCase("CMUT06", "CW05", replace(C5, kind=Kind.CAUSES)),
    MutationCase("CMUT07", "CW01", replace(C1, kind=Kind.PREVENTS)),
    MutationCase("CMUT08", "CW01", replace(C1, cause="x", effect="y")),
)


def _status(text: str, atom: CausalAtom, candidate: AuthorityCandidate) -> str:
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


def weak_trust_measurement(text: str, measured: CausalAtom) -> object:
    del text
    return measured
