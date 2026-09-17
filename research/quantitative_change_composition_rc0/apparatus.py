"""Frozen composition apparatus for Quantitative Change RC0."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from fractions import Fraction


class Kind(StrEnum):
    INCREASED = "INCREASED"
    DECREASED = "DECREASED"
    UNCHANGED = "UNCHANGED"
    DELTA = "DELTA"


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class State:
    entity: str
    metric: str
    unit: str
    time: str
    value: Fraction
    exact: bool = True


@dataclass(frozen=True, slots=True)
class Query:
    entity: str
    metric: str
    unit: str
    kind: Kind
    amount: Fraction | None = None


def oracle(old: State, new: State, query: Query) -> Relation:
    if not old.exact or not new.exact:
        return Relation.UNRESOLVED
    if old.time == new.time:
        return Relation.UNRESOLVED
    if (old.entity, old.metric, old.unit) != (new.entity, new.metric, new.unit):
        return Relation.UNRESOLVED
    if (old.entity, old.metric, old.unit) != (query.entity, query.metric, query.unit):
        return Relation.UNRESOLVED
    delta = new.value - old.value
    truth = {
        Kind.INCREASED: delta > 0,
        Kind.DECREASED: delta < 0,
        Kind.UNCHANGED: delta == 0,
        Kind.DELTA: query.amount is not None and delta == query.amount,
    }[query.kind]
    return Relation.SUPPORTS if truth else Relation.REFUTES


def weak_ignore_unit(old: State, new: State, query: Query) -> Relation:
    return oracle(replace(old, unit=query.unit), replace(new, unit=query.unit), query)


def weak_ignore_metric(old: State, new: State, query: Query) -> Relation:
    return oracle(replace(old, metric=query.metric), replace(new, metric=query.metric), query)


def weak_approx_exact(old: State, new: State, query: Query) -> Relation:
    return oracle(replace(old, exact=True), replace(new, exact=True), query)


def weak_reverse_order(old: State, new: State, query: Query) -> Relation:
    return oracle(new, old, query)


F = Fraction
BASE_OLD = State("batch", "yield", "%", "T1", F(80))
BASE_NEW = State("batch", "yield", "%", "T2", F(90))
CASES: tuple[tuple[str, State, State, Query], ...] = (
    ("Q01", BASE_OLD, BASE_NEW, Query("batch", "yield", "%", Kind.INCREASED)),
    ("Q02", BASE_OLD, BASE_NEW, Query("batch", "yield", "%", Kind.DECREASED)),
    ("Q03", BASE_OLD, BASE_NEW, Query("batch", "yield", "%", Kind.DELTA, F(10))),
    ("Q04", BASE_OLD, BASE_NEW, Query("batch", "yield", "%", Kind.UNCHANGED)),
    ("Q05", BASE_OLD, replace(BASE_NEW, value=F(80)), Query("batch", "yield", "%", Kind.UNCHANGED)),
    ("Q06", BASE_OLD, replace(BASE_NEW, metric="count"), Query("batch", "yield", "%", Kind.INCREASED)),
    ("Q07", BASE_OLD, replace(BASE_NEW, unit="fraction"), Query("batch", "yield", "%", Kind.INCREASED)),
    ("Q08", replace(BASE_OLD, exact=False), BASE_NEW, Query("batch", "yield", "%", Kind.INCREASED)),
    ("Q09", BASE_OLD, BASE_NEW, Query("other", "yield", "%", Kind.INCREASED)),
)


def disagreements(strategy) -> tuple[str, ...]:
    return tuple(case_id for case_id, old, new, query in CASES if strategy(old, new, query) != oracle(old, new, query))
