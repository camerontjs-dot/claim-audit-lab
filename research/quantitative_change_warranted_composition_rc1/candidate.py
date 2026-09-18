"""Candidate for warranted quantitative-change composition RC1."""

from __future__ import annotations

from .apparatus import Contribution, Kind, Query, Relation


def _point_is_usable(contribution: Contribution) -> bool:
    atom = contribution.atom
    return (
        contribution.warranted
        and bool(contribution.authority_id)
        and contribution.time.established
        and contribution.time.rank is not None
        and atom.exact
        and atom.low == atom.high
    )


def compose_change(
    left: Contribution,
    right: Contribution,
    query: Query,
) -> Relation:
    if not _point_is_usable(left) or not _point_is_usable(right):
        return Relation.UNRESOLVED

    if left.authority_id == right.authority_id:
        return Relation.UNRESOLVED

    if left.time.rank == right.time.rank:
        return Relation.UNRESOLVED

    if left.time.label == right.time.label:
        return Relation.UNRESOLVED

    left_key = (left.atom.entity, left.atom.metric, left.atom.unit)
    right_key = (right.atom.entity, right.atom.metric, right.atom.unit)
    query_key = (query.entity, query.metric, query.unit)
    if left_key != right_key or left_key != query_key:
        return Relation.UNRESOLVED

    earlier, later = (
        (left, right)
        if left.time.rank < right.time.rank
        else (right, left)
    )
    delta = later.atom.low - earlier.atom.low

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
        return Relation.UNRESOLVED

    return Relation.SUPPORTS if truth else Relation.REFUTES
