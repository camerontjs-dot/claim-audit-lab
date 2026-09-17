"""Frozen typed apparatus for Scalar Value Family Contract RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction


class Op(StrEnum):
    EQ = "EQ"
    GT = "GT"
    GE = "GE"
    LT = "LT"
    LE = "LE"


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class Authority:
    entity: str
    metric: str
    unit: str
    low: Fraction
    high: Fraction
    exact: bool = True


@dataclass(frozen=True, slots=True)
class Query:
    entity: str
    metric: str
    unit: str
    op: Op
    value: Fraction


def _truth(value: Fraction, query: Query) -> bool:
    if query.op is Op.EQ:
        return value == query.value
    if query.op is Op.GT:
        return value > query.value
    if query.op is Op.GE:
        return value >= query.value
    if query.op is Op.LT:
        return value < query.value
    if query.op is Op.LE:
        return value <= query.value
    raise AssertionError(query.op)


def oracle(authority: Authority, query: Query) -> Relation:
    if (authority.entity, authority.metric, authority.unit) != (
        query.entity,
        query.metric,
        query.unit,
    ):
        return Relation.UNRESOLVED
    if authority.low > authority.high:
        raise ValueError("invalid interval")
    if query.op is Op.EQ and not authority.exact:
        return Relation.UNRESOLVED
    endpoint_truth = {_truth(authority.low, query), _truth(authority.high, query)}
    if authority.low == authority.high:
        endpoint_truth = {_truth(authority.low, query)}
    if endpoint_truth == {True}:
        if query.op is Op.EQ and authority.low != authority.high:
            return Relation.UNRESOLVED
        return Relation.SUPPORTS
    if endpoint_truth == {False}:
        if query.op is Op.EQ and authority.low < query.value < authority.high:
            return Relation.UNRESOLVED
        return Relation.REFUTES
    return Relation.UNRESOLVED


def weak_midpoint(authority: Authority, query: Query) -> Relation:
    midpoint = (authority.low + authority.high) / 2
    fake = Authority(authority.entity, authority.metric, authority.unit, midpoint, midpoint, True)
    return oracle(fake, query)


def weak_ignore_unit(authority: Authority, query: Query) -> Relation:
    fake = Authority(authority.entity, authority.metric, query.unit, authority.low, authority.high, authority.exact)
    return oracle(fake, query)


def weak_approx_exact(authority: Authority, query: Query) -> Relation:
    fake = Authority(authority.entity, authority.metric, authority.unit, authority.low, authority.high, True)
    return oracle(fake, query)


F = Fraction
CASES: tuple[tuple[str, Authority, Query], ...] = (
    ("S01", Authority("batch", "yield", "%", F(92), F(92)), Query("batch", "yield", "%", Op.EQ, F(92))),
    ("S02", Authority("batch", "yield", "%", F(92), F(92)), Query("batch", "yield", "%", Op.GT, F(90))),
    ("S03", Authority("batch", "yield", "%", F(92), F(92)), Query("batch", "yield", "%", Op.LT, F(90))),
    ("S04", Authority("batch", "yield", "%", F(90), F(94)), Query("batch", "yield", "%", Op.GT, F(89))),
    ("S05", Authority("batch", "yield", "%", F(90), F(94)), Query("batch", "yield", "%", Op.GT, F(92))),
    ("S06", Authority("batch", "yield", "%", F(90), F(94)), Query("batch", "yield", "%", Op.LT, F(95))),
    ("S07", Authority("batch", "yield", "%", F(90), F(94)), Query("batch", "yield", "%", Op.EQ, F(92))),
    ("S08", Authority("batch", "yield", "%", F(92), F(92), False), Query("batch", "yield", "%", Op.EQ, F(92))),
    ("S09", Authority("batch", "yield", "%", F(92), F(92)), Query("batch", "yield", "fraction", Op.EQ, F(92))),
    ("S10", Authority("batch", "yield", "%", F(92), F(92)), Query("other", "yield", "%", Op.EQ, F(92))),
    ("S11", Authority("batch", "yield", "%", F(92), F(92)), Query("batch", "count", "%", Op.EQ, F(92))),
    ("S12", Authority("batch", "count", "count", F(17), F(17)), Query("batch", "count", "count", Op.GE, F(17))),
)


def disagreements(strategy) -> tuple[str, ...]:
    return tuple(case_id for case_id, authority, query in CASES if strategy(authority, query) != oracle(authority, query))
