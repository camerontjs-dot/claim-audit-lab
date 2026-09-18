"""Frozen evaluator for Typed Binary Relation Measurement Machinery RC1."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .cohort import Bucket,CASES,CASES_BY_ID,METAMORPHIC_PAIRS,Observation,RelationAtom,Status

Strategy=Callable[[str],Observation]


@dataclass(frozen=True,slots=True)
class Report:
    must_handle_failures:tuple[str,...]
    fail_closed_unsafe:tuple[str,...]
    diagnostic_wrong_claims:tuple[str,...]
    diagnostic_exact:tuple[str,...]
    diagnostic_unresolved:tuple[str,...]

    @property
    def qualifiable(self)->bool:
        return not self.must_handle_failures and not self.fail_closed_unsafe and not self.diagnostic_wrong_claims


def evaluate(strategy:Strategy)->Report:
    must=[]; unsafe=[]; wrong=[]; exact=[]; unresolved=[]
    for case in CASES:
        observed=strategy(case.text)
        if case.bucket is Bucket.MUST_HANDLE:
            if observed.status is not Status.CLAIMED or observed.atom!=case.expected:
                must.append(case.case_id)
        elif case.bucket is Bucket.FAIL_CLOSED:
            if observed.status is Status.CLAIMED:
                unsafe.append(case.case_id)
        elif observed.status is Status.CLAIMED:
            if observed.atom==case.expected:
                exact.append(case.case_id)
            else:
                wrong.append(case.case_id)
        else:
            unresolved.append(case.case_id)
    return Report(tuple(must),tuple(unsafe),tuple(wrong),tuple(exact),tuple(unresolved))


def metamorphic_failures(strategy:Strategy)->tuple[str,...]:
    failures=[]
    for left_id,right_id in METAMORPHIC_PAIRS:
        left=CASES_BY_ID[left_id]; right=CASES_BY_ID[right_id]
        left_obs=strategy(left.text); right_obs=strategy(right.text)
        if left_obs.status is not Status.CLAIMED or left_obs.atom!=left.expected:
            failures.append(f"{left_id}->{right_id}:left")
        elif right.bucket is Bucket.MUST_HANDLE:
            if right_obs.status is not Status.CLAIMED or right_obs.atom!=right.expected:
                failures.append(f"{left_id}->{right_id}:right")
        elif right.bucket is Bucket.DIAGNOSTIC:
            if right_obs.status is Status.CLAIMED and right_obs.atom!=right.expected:
                failures.append(f"{left_id}->{right_id}:wrong-right")
        elif right_obs.status is Status.CLAIMED:
            failures.append(f"{left_id}->{right_id}:unsafe-right")
    return tuple(failures)


def weak_argument_erasure(text:str)->Observation:
    low=text.casefold()
    if "owns" in low and "a" in low and "b" in low:
        return Observation.claimed(RelationAtom("a","OWNS","b"))
    return Observation.unresolved("weak")


def weak_open_predicate(text:str)->Observation:
    if "near" in text.casefold():
        return Observation.claimed(RelationAtom("a","NEAR","b"))
    return Observation.unresolved("weak")


def weak_spatial_transitivity(text:str)->Observation:
    if "north" in text.casefold() and "c" in text.casefold():
        return Observation.claimed(RelationAtom("a","NORTH_OF","c"))
    return Observation.unresolved("weak")


def weak_reporting_erasure(text:str)->Observation:
    if "owns" in text.casefold():
        return Observation.claimed(RelationAtom("a","OWNS","b"))
    return Observation.unresolved("weak")


def weak_metric_erasure(text:str)->Observation:
    if "north of" in text.casefold():
        return Observation.claimed(RelationAtom("a","NORTH_OF","b"))
    return Observation.unresolved("weak")
