"""Binding-preserving occurrence + order recombination candidate RC0."""

from __future__ import annotations

from .apparatus import (
    OccurrenceContribution,
    Order,
    OrderContribution,
    Polarity,
    Query,
    Relation,
)


def _normalize(
    left,
    relation: Order,
    right,
    left_binding_id: str | None,
    right_binding_id: str | None,
):
    if relation is Order.BEFORE:
        return left, right, left_binding_id, right_binding_id
    return right, left, right_binding_id, left_binding_id


def compose_occurrence_order(
    first: OccurrenceContribution,
    second: OccurrenceContribution,
    ordered: OrderContribution,
    query: Query,
) -> Relation:
    if not first.warranted or not second.warranted or not ordered.warranted:
        return Relation.UNRESOLVED

    if not first.authority_id or not second.authority_id or not ordered.authority_id:
        return Relation.UNRESOLVED
    if first.authority_id == second.authority_id:
        return Relation.UNRESOLVED

    if first.binding_id is None or second.binding_id is None:
        return Relation.UNRESOLVED
    if first.binding_id == second.binding_id:
        return Relation.UNRESOLVED

    if first.event.polarity is not Polarity.OCCURRED:
        return Relation.UNRESOLVED
    if second.event.polarity is not Polarity.OCCURRED:
        return Relation.UNRESOLVED

    order_left, order_right, order_left_binding, order_right_binding = _normalize(
        ordered.left,
        ordered.relation,
        ordered.right,
        ordered.left_binding_id,
        ordered.right_binding_id,
    )
    query_left, query_right, query_left_binding, query_right_binding = _normalize(
        query.left,
        query.relation,
        query.right,
        query.left_binding_id,
        query.right_binding_id,
    )

    if (
        order_left_binding is None
        or order_right_binding is None
        or query_left_binding is None
        or query_right_binding is None
    ):
        return Relation.UNRESOLVED
    if order_left_binding == order_right_binding:
        return Relation.UNRESOLVED
    if query_left_binding == query_right_binding:
        return Relation.UNRESOLVED

    if (
        order_left,
        order_right,
        order_left_binding,
        order_right_binding,
    ) != (
        query_left,
        query_right,
        query_left_binding,
        query_right_binding,
    ):
        return Relation.UNRESOLVED

    by_binding = {
        first.binding_id: first.event,
        second.binding_id: second.event,
    }
    if by_binding.get(query_left_binding) != query_left:
        return Relation.UNRESOLVED
    if by_binding.get(query_right_binding) != query_right:
        return Relation.UNRESOLVED

    return Relation.SUPPORTS
