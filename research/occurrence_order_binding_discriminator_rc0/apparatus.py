"""Frozen apparatus for occurrence + order binding discriminator RC0."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Polarity(StrEnum):
    OCCURRED = "OCCURRED"
    DID_NOT_OCCUR = "DID_NOT_OCCUR"


class Order(StrEnum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class EventKey:
    actor: str
    action: str
    object: str
    polarity: Polarity = Polarity.OCCURRED


@dataclass(frozen=True, slots=True)
class OccurrenceContribution:
    event: EventKey
    authority_id: str
    warranted: bool
    binding_id: str | None


@dataclass(frozen=True, slots=True)
class OrderContribution:
    left: EventKey
    relation: Order
    right: EventKey
    authority_id: str
    warranted: bool
    left_binding_id: str | None
    right_binding_id: str | None


@dataclass(frozen=True, slots=True)
class Query:
    left: EventKey
    relation: Order
    right: EventKey
    left_binding_id: str | None
    right_binding_id: str | None


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    first_occurrence: OccurrenceContribution
    second_occurrence: OccurrenceContribution
    order: OrderContribution
    query: Query
    expected: Relation


def e(
    actor: str,
    action: str,
    obj: str,
    polarity: Polarity = Polarity.OCCURRED,
) -> EventKey:
    return EventKey(actor, action, obj, polarity)


A = e("qa", "approve", "batch")
B = e("ops", "release", "batch")
C = e("qa", "sign", "record")
NEG_A = e("qa", "approve", "batch", Polarity.DID_NOT_OCCUR)


def occ(
    event: EventKey,
    authority_id: str,
    binding_id: str | None,
    *,
    warranted: bool = True,
) -> OccurrenceContribution:
    return OccurrenceContribution(event, authority_id, warranted, binding_id)


def order(
    left: EventKey,
    relation: Order,
    right: EventKey,
    authority_id: str,
    left_binding_id: str | None,
    right_binding_id: str | None,
    *,
    warranted: bool = True,
) -> OrderContribution:
    return OrderContribution(
        left,
        relation,
        right,
        authority_id,
        warranted,
        left_binding_id,
        right_binding_id,
    )


def q(
    left: EventKey,
    relation: Order,
    right: EventKey,
    left_binding_id: str | None,
    right_binding_id: str | None,
) -> Query:
    return Query(left, relation, right, left_binding_id, right_binding_id)


CASES: tuple[Case, ...] = (
    Case(
        "OB01",
        occ(A, "oa", "event-a"),
        occ(B, "ob", "event-b"),
        order(A, Order.BEFORE, B, "oo", "event-a", "event-b"),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.SUPPORTS,
    ),
    Case(
        "OB02",
        occ(A, "oa", "event-a"),
        occ(B, "ob", "event-b"),
        order(B, Order.AFTER, A, "oo", "event-b", "event-a"),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.SUPPORTS,
    ),
    Case(
        "OB03",
        occ(B, "ob", "event-b"),
        occ(A, "oa", "event-a"),
        order(A, Order.BEFORE, B, "oo", "event-a", "event-b"),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.SUPPORTS,
    ),
    Case(
        "OU01",
        occ(A, "oa2", "event-a-2"),
        occ(B, "ob", "event-b"),
        order(A, Order.BEFORE, B, "oo", "event-a-1", "event-b"),
        q(A, Order.BEFORE, B, "event-a-2", "event-b"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU02",
        occ(A, "oa", "event-a", warranted=False),
        occ(B, "ob", "event-b"),
        order(A, Order.BEFORE, B, "oo", "event-a", "event-b"),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU03",
        occ(A, "oa", "event-a"),
        occ(B, "ob", "event-b"),
        order(
            A,
            Order.BEFORE,
            B,
            "oo",
            "event-a",
            "event-b",
            warranted=False,
        ),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU04",
        occ(A, "oa", "event-a"),
        occ(B, "ob", "event-b"),
        order(C, Order.BEFORE, B, "oo", "event-a", "event-b"),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU05",
        occ(A, "oa", "event-a"),
        occ(B, "ob", "event-b"),
        order(A, Order.BEFORE, B, "oo", "event-a", "event-b"),
        q(C, Order.BEFORE, B, "event-a", "event-b"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU06",
        occ(A, "oa", None),
        occ(B, "ob", "event-b"),
        order(A, Order.BEFORE, B, "oo", "event-a", "event-b"),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU07",
        occ(A, "oa", "event-a"),
        occ(B, "ob", "event-b"),
        order(A, Order.BEFORE, B, "oo", None, "event-b"),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU08",
        occ(A, "oa", "same-event"),
        occ(B, "ob", "same-event"),
        order(A, Order.BEFORE, B, "oo", "same-event", "same-event"),
        q(A, Order.BEFORE, B, "same-event", "same-event"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU09",
        occ(NEG_A, "oa", "event-a"),
        occ(B, "ob", "event-b"),
        order(A, Order.BEFORE, B, "oo", "event-a", "event-b"),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU10",
        occ(A, "oa", "event-a"),
        occ(B, "ob", "event-b"),
        order(A, Order.BEFORE, B, "oo", "event-a", "event-b"),
        q(A, Order.BEFORE, B, None, "event-b"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU11",
        occ(A, "oa", "event-a"),
        occ(A, "ob", "event-a"),
        order(A, Order.BEFORE, A, "oo", "event-a", "event-a"),
        q(A, Order.BEFORE, A, "event-a", "event-a"),
        Relation.UNRESOLVED,
    ),
    Case(
        "OU12",
        occ(A, "same-authority", "event-a"),
        occ(B, "same-authority", "event-b"),
        order(A, Order.BEFORE, B, "oo", "event-a", "event-b"),
        q(A, Order.BEFORE, B, "event-a", "event-b"),
        Relation.UNRESOLVED,
    ),
)


def _normalized_order(
    left: EventKey,
    relation: Order,
    right: EventKey,
    left_binding_id: str | None,
    right_binding_id: str | None,
) -> tuple[EventKey, EventKey, str | None, str | None]:
    if relation is Order.BEFORE:
        return left, right, left_binding_id, right_binding_id
    return right, left, right_binding_id, left_binding_id


def _has_event_by_fields(
    first: OccurrenceContribution,
    second: OccurrenceContribution,
    event: EventKey,
) -> bool:
    return first.event == event or second.event == event


def _has_event_by_binding(
    first: OccurrenceContribution,
    second: OccurrenceContribution,
    binding_id: str | None,
) -> bool:
    return first.binding_id == binding_id or second.binding_id == binding_id


def weak_field_only(
    first: OccurrenceContribution,
    second: OccurrenceContribution,
    ordered: OrderContribution,
    query: Query,
) -> Relation:
    ql, qr, _, _ = _normalized_order(
        query.left,
        query.relation,
        query.right,
        query.left_binding_id,
        query.right_binding_id,
    )
    ol, or_, _, _ = _normalized_order(
        ordered.left,
        ordered.relation,
        ordered.right,
        ordered.left_binding_id,
        ordered.right_binding_id,
    )
    if (
        _has_event_by_fields(first, second, ql)
        and _has_event_by_fields(first, second, qr)
        and ol == ql
        and or_ == qr
    ):
        return Relation.SUPPORTS
    return Relation.UNRESOLVED


def weak_binding_only(
    first: OccurrenceContribution,
    second: OccurrenceContribution,
    ordered: OrderContribution,
    query: Query,
) -> Relation:
    _, _, qlb, qrb = _normalized_order(
        query.left,
        query.relation,
        query.right,
        query.left_binding_id,
        query.right_binding_id,
    )
    _, _, olb, orb = _normalized_order(
        ordered.left,
        ordered.relation,
        ordered.right,
        ordered.left_binding_id,
        ordered.right_binding_id,
    )
    if (
        _has_event_by_binding(first, second, qlb)
        and _has_event_by_binding(first, second, qrb)
        and olb == qlb
        and orb == qrb
    ):
        return Relation.SUPPORTS
    return Relation.UNRESOLVED


def weak_ignore_warrant(
    first: OccurrenceContribution,
    second: OccurrenceContribution,
    ordered: OrderContribution,
    query: Query,
) -> Relation:
    ql, qr, qlb, qrb = _normalized_order(
        query.left,
        query.relation,
        query.right,
        query.left_binding_id,
        query.right_binding_id,
    )
    ol, or_, olb, orb = _normalized_order(
        ordered.left,
        ordered.relation,
        ordered.right,
        ordered.left_binding_id,
        ordered.right_binding_id,
    )
    events = {
        (first.event, first.binding_id),
        (second.event, second.binding_id),
    }
    if (
        (ql, qlb) in events
        and (qr, qrb) in events
        and (ol, olb) == (ql, qlb)
        and (or_, orb) == (qr, qrb)
    ):
        return Relation.SUPPORTS
    return Relation.UNRESOLVED


def weak_call_order(
    first: OccurrenceContribution,
    second: OccurrenceContribution,
    ordered: OrderContribution,
    query: Query,
) -> Relation:
    del ordered
    ql, qr, qlb, qrb = _normalized_order(
        query.left,
        query.relation,
        query.right,
        query.left_binding_id,
        query.right_binding_id,
    )
    if (
        (first.event, first.binding_id) == (ql, qlb)
        and (second.event, second.binding_id) == (qr, qrb)
    ):
        return Relation.SUPPORTS
    return Relation.UNRESOLVED
