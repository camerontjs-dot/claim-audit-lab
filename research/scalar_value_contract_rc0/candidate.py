"""Direct consumer candidate for Scalar Value Family Contract RC0."""

from __future__ import annotations

from fractions import Fraction

from .apparatus import Authority, Op, Query, Relation


def _satisfies(value: Fraction, query: Query) -> bool:
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


def relate(authority: Authority, query: Query) -> Relation:
    if (authority.entity, authority.metric, authority.unit) != (
        query.entity,
        query.metric,
        query.unit,
    ):
        return Relation.UNRESOLVED
    if authority.low > authority.high:
        raise ValueError("invalid interval")
    if query.op is Op.EQ:
        if not authority.exact or authority.low != authority.high:
            return Relation.UNRESOLVED
        return Relation.SUPPORTS if authority.low == query.value else Relation.REFUTES

    low_truth = _satisfies(authority.low, query)
    high_truth = _satisfies(authority.high, query)
    if low_truth and high_truth:
        return Relation.SUPPORTS
    if not low_truth and not high_truth:
        return Relation.REFUTES
    return Relation.UNRESOLVED
