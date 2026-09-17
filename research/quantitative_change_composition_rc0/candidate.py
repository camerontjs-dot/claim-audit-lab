"""Composition candidate for Quantitative Change RC0."""

from __future__ import annotations

from .apparatus import Kind, Query, Relation, State


def derive_relation(old: State, new: State, query: Query) -> Relation:
    if not old.exact or not new.exact:
        return Relation.UNRESOLVED
    if old.time == new.time:
        return Relation.UNRESOLVED
    if (old.entity, old.metric, old.unit) != (new.entity, new.metric, new.unit):
        return Relation.UNRESOLVED
    if (old.entity, old.metric, old.unit) != (query.entity, query.metric, query.unit):
        return Relation.UNRESOLVED

    delta = new.value - old.value
    if query.kind is Kind.INCREASED:
        truth = delta > 0
    elif query.kind is Kind.DECREASED:
        truth = delta < 0
    elif query.kind is Kind.UNCHANGED:
        truth = delta == 0
    elif query.kind is Kind.DELTA:
        if query.amount is None:
            return Relation.UNRESOLVED
        truth = delta == query.amount
    else:
        raise AssertionError(query.kind)
    return Relation.SUPPORTS if truth else Relation.REFUTES
