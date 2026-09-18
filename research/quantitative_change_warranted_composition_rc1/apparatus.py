"""Frozen apparatus for warranted quantitative-change composition RC1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from research.scalar_measurement_machinery_rc0.cohort import ScalarAtom


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
class TemporalBinding:
    label: str
    rank: int | None
    established: bool = True


@dataclass(frozen=True, slots=True)
class Contribution:
    atom: ScalarAtom
    authority_id: str
    warranted: bool
    time: TemporalBinding


@dataclass(frozen=True, slots=True)
class Query:
    entity: str
    metric: str
    unit: str
    kind: Kind
    amount: Fraction | None = None


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    left: Contribution
    right: Contribution
    query: Query
    expected: Relation


F = Fraction


def point(
    value: Fraction,
    *,
    entity: str = "batch",
    metric: str = "yield",
    unit: str = "%",
    exact: bool = True,
) -> ScalarAtom:
    return ScalarAtom(entity, metric, unit, value, value, exact)


def interval(low: Fraction, high: Fraction) -> ScalarAtom:
    return ScalarAtom("batch", "yield", "%", low, high, True)


def c(
    value: Fraction | ScalarAtom,
    authority_id: str,
    rank: int | None,
    *,
    label: str | None = None,
    warranted: bool = True,
    established: bool = True,
) -> Contribution:
    atom = value if isinstance(value, ScalarAtom) else point(value)
    return Contribution(
        atom,
        authority_id,
        warranted,
        TemporalBinding(label or f"T{rank}", rank, established),
    )


def q(kind: Kind, amount: Fraction | None = None, **overrides: str) -> Query:
    return Query(
        overrides.get("entity", "batch"),
        overrides.get("metric", "yield"),
        overrides.get("unit", "%"),
        kind,
        amount,
    )


CASES: tuple[Case, ...] = (
    Case("QC01", c(F(80),"a1",1), c(F(90),"a2",2), q(Kind.INCREASED), Relation.SUPPORTS),
    Case("QC02", c(F(90),"a1",1), c(F(80),"a2",2), q(Kind.DECREASED), Relation.SUPPORTS),
    Case("QC03", c(F(90),"a1",1), c(F(90),"a2",2), q(Kind.UNCHANGED), Relation.SUPPORTS),
    Case("QC04", c(F(80),"a1",1), c(F(90),"a2",2), q(Kind.DELTA,F(10)), Relation.SUPPORTS),
    Case("QC05", c(F(80),"a1",1), c(F(90),"a2",2), q(Kind.DECREASED), Relation.REFUTES),
    Case("QC06", c(F(80),"a1",1), c(F(90),"a2",2), q(Kind.DELTA,F(9)), Relation.REFUTES),
    Case("QC07", c(F(90),"a2",2), c(F(80),"a1",1), q(Kind.INCREASED), Relation.SUPPORTS),
    Case("QC08", c(F(-5),"a1",1), c(F(-2),"a2",2), q(Kind.INCREASED), Relation.SUPPORTS),
    Case(
        "QU01",
        c(point(F(80),unit="%"),"a1",1),
        c(point(F(90),unit="fraction"),"a2",2),
        q(Kind.INCREASED),
        Relation.UNRESOLVED,
    ),
    Case(
        "QU02",
        c(point(F(80),metric="yield"),"a1",1),
        c(point(F(90),metric="count"),"a2",2),
        q(Kind.INCREASED),
        Relation.UNRESOLVED,
    ),
    Case(
        "QU03",
        c(point(F(80),entity="batch"),"a1",1),
        c(point(F(90),entity="other_batch"),"a2",2),
        q(Kind.INCREASED),
        Relation.UNRESOLVED,
    ),
    Case(
        "QU04",
        c(point(F(80),exact=False),"a1",1),
        c(F(90),"a2",2),
        q(Kind.INCREASED),
        Relation.UNRESOLVED,
    ),
    Case(
        "QU05",
        c(interval(F(80),F(82)),"a1",1),
        c(F(90),"a2",2),
        q(Kind.INCREASED),
        Relation.UNRESOLVED,
    ),
    Case("QU06", c(F(80),"a1",1), c(F(90),"a2",1), q(Kind.INCREASED), Relation.UNRESOLVED),
    Case(
        "QU07",
        c(F(80),"a1",1,established=False),
        c(F(90),"a2",2),
        q(Kind.INCREASED),
        Relation.UNRESOLVED,
    ),
    Case(
        "QU08",
        c(F(80),"a1",1,warranted=False),
        c(F(90),"a2",2),
        q(Kind.INCREASED),
        Relation.UNRESOLVED,
    ),
    Case("QU09", c(F(80),"same",1), c(F(90),"same",2), q(Kind.INCREASED), Relation.UNRESOLVED),
    Case(
        "QU10",
        c(F(80),"a1",1),
        c(F(90),"a2",2),
        q(Kind.INCREASED,unit="fraction"),
        Relation.UNRESOLVED,
    ),
    Case("QU11", c(F(80),"a1",1), c(F(90),"a2",2), q(Kind.DELTA), Relation.UNRESOLVED),
    Case(
        "QU12",
        c(F(80),"a1",1,label="T1"),
        c(F(90),"a2",2,label="T1"),
        q(Kind.INCREASED),
        Relation.UNRESOLVED,
    ),
)


def oracle(case: Case) -> Relation:
    return case.expected


def weak_input_order(left: Contribution, right: Contribution, query: Query) -> Relation:
    delta = right.atom.low - left.atom.low
    if query.kind is Kind.INCREASED:
        return Relation.SUPPORTS if delta > 0 else Relation.REFUTES
    if query.kind is Kind.DECREASED:
        return Relation.SUPPORTS if delta < 0 else Relation.REFUTES
    if query.kind is Kind.UNCHANGED:
        return Relation.SUPPORTS if delta == 0 else Relation.REFUTES
    if query.amount is None:
        return Relation.UNRESOLVED
    return Relation.SUPPORTS if delta == query.amount else Relation.REFUTES


def weak_ignore_identity(left: Contribution, right: Contribution, query: Query) -> Relation:
    return weak_input_order(left, right, query)


def weak_midpoint(left: Contribution, right: Contribution, query: Query) -> Relation:
    def midpoint(atom: ScalarAtom) -> Fraction:
        return (atom.low + atom.high) / 2

    delta = midpoint(right.atom) - midpoint(left.atom)
    if query.kind is Kind.INCREASED:
        return Relation.SUPPORTS if delta > 0 else Relation.REFUTES
    return Relation.UNRESOLVED


def weak_ignore_warrant(left: Contribution, right: Contribution, query: Query) -> Relation:
    return weak_input_order(left, right, query)
