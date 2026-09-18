"""Frozen apparatus for attribute-state temporal applicability RC0."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class StateContribution:
    authority_id: str
    warranted: bool
    entity: str
    attribute: str
    domain: str
    value: str
    functional: bool


@dataclass(frozen=True, slots=True)
class TemporalScope:
    authority_id: str
    start_ordinal: int
    end_ordinal: int


@dataclass(frozen=True, slots=True)
class TimedStateQuery:
    entity: str
    attribute: str
    domain: str
    value: str
    target_ordinal: int


@dataclass(frozen=True, slots=True)
class TemporalStateReceipt:
    receipt_id: str
    relation: Relation
    authority_id: str
    scope_start: int | None
    scope_end: int | None
    target_ordinal: int | None


class Strategy(Protocol):
    def __call__(
        self,
        state: StateContribution,
        scope: TemporalScope | None,
        query: TimedStateQuery,
    ) -> TemporalStateReceipt: ...


def _stable(material: dict[str, object]) -> str:
    payload = json.dumps(material, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def oracle_relation(
    state: StateContribution,
    scope: TemporalScope | None,
    query: TimedStateQuery,
) -> Relation:
    if not state.warranted:
        return Relation.UNRESOLVED
    if scope is None:
        return Relation.UNRESOLVED
    if scope.authority_id != state.authority_id:
        return Relation.UNRESOLVED
    if scope.start_ordinal > scope.end_ordinal:
        return Relation.UNRESOLVED
    if not (scope.start_ordinal <= query.target_ordinal <= scope.end_ordinal):
        return Relation.UNRESOLVED
    if (state.entity, state.attribute, state.domain) != (
        query.entity,
        query.attribute,
        query.domain,
    ):
        return Relation.UNRESOLVED
    if state.value == query.value:
        return Relation.SUPPORTS
    if state.functional:
        return Relation.REFUTES
    return Relation.UNRESOLVED


def verify_receipt(
    receipt: TemporalStateReceipt,
    state: StateContribution,
    scope: TemporalScope | None,
    query: TimedStateQuery,
) -> bool:
    expected = oracle_relation(state, scope, query)
    if receipt.relation is not expected:
        return False

    if expected is Relation.UNRESOLVED:
        return (
            receipt.authority_id == ""
            and receipt.scope_start is None
            and receipt.scope_end is None
            and receipt.target_ordinal is None
        )

    assert scope is not None
    if receipt.authority_id != state.authority_id:
        return False
    if receipt.scope_start != scope.start_ordinal:
        return False
    if receipt.scope_end != scope.end_ordinal:
        return False
    if receipt.target_ordinal != query.target_ordinal:
        return False

    material = {
        "relation": receipt.relation.value,
        "authority_id": receipt.authority_id,
        "scope_start": receipt.scope_start,
        "scope_end": receipt.scope_end,
        "target_ordinal": receipt.target_ordinal,
        "query": {
            "entity": query.entity,
            "attribute": query.attribute,
            "domain": query.domain,
            "value": query.value,
        },
    }
    return receipt.receipt_id == _stable(material)


def _empty(relation: Relation) -> TemporalStateReceipt:
    return TemporalStateReceipt("", relation, "", None, None, None)


def weak_ignore_scope(
    state: StateContribution,
    scope: TemporalScope | None,
    query: TimedStateQuery,
) -> TemporalStateReceipt:
    del scope
    if not state.warranted:
        return _empty(Relation.UNRESOLVED)
    if (state.entity, state.attribute, state.domain) != (
        query.entity,
        query.attribute,
        query.domain,
    ):
        return _empty(Relation.UNRESOLVED)
    relation = (
        Relation.SUPPORTS
        if state.value == query.value
        else Relation.REFUTES if state.functional else Relation.UNRESOLVED
    )
    return _empty(relation)


def weak_latest_persists(
    state: StateContribution,
    scope: TemporalScope | None,
    query: TimedStateQuery,
) -> TemporalStateReceipt:
    if scope is None:
        return weak_ignore_scope(state, scope, query)
    if query.target_ordinal >= scope.start_ordinal:
        return weak_ignore_scope(state, scope, query)
    return _empty(Relation.UNRESOLVED)


def weak_ignore_scope_binding(
    state: StateContribution,
    scope: TemporalScope | None,
    query: TimedStateQuery,
) -> TemporalStateReceipt:
    if scope is None:
        return _empty(Relation.UNRESOLVED)
    rebound = TemporalScope(state.authority_id, scope.start_ordinal, scope.end_ordinal)
    relation = oracle_relation(state, rebound, query)
    return _empty(relation)


def weak_all_functional(
    state: StateContribution,
    scope: TemporalScope | None,
    query: TimedStateQuery,
) -> TemporalStateReceipt:
    forced = StateContribution(
        state.authority_id,
        state.warranted,
        state.entity,
        state.attribute,
        state.domain,
        state.value,
        True,
    )
    return _empty(oracle_relation(forced, scope, query))


def weak_ignore_warrant(
    state: StateContribution,
    scope: TemporalScope | None,
    query: TimedStateQuery,
) -> TemporalStateReceipt:
    forced = StateContribution(
        state.authority_id,
        True,
        state.entity,
        state.attribute,
        state.domain,
        state.value,
        state.functional,
    )
    return _empty(oracle_relation(forced, scope, query))


def weak_relation_only(
    state: StateContribution,
    scope: TemporalScope | None,
    query: TimedStateQuery,
) -> TemporalStateReceipt:
    return _empty(oracle_relation(state, scope, query))


STATUS = StateContribution(
    "state-status-1",
    True,
    "batch",
    "status",
    "batch_status",
    "released",
    True,
)
TAG = StateContribution(
    "state-tag-1",
    True,
    "record",
    "tag",
    "labels",
    "critical",
    False,
)
STATUS_SCOPE = TemporalScope("state-status-1", 10, 20)
TAG_SCOPE = TemporalScope("state-tag-1", 5, 15)


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    state: StateContribution
    scope: TemporalScope | None
    query: TimedStateQuery


CASES: tuple[Case, ...] = (
    Case("AT01", STATUS, STATUS_SCOPE, TimedStateQuery("batch", "status", "batch_status", "released", 15)),
    Case("AT02", STATUS, STATUS_SCOPE, TimedStateQuery("batch", "status", "batch_status", "held", 15)),
    Case("AT03", STATUS, STATUS_SCOPE, TimedStateQuery("batch", "status", "batch_status", "released", 10)),
    Case("AT04", STATUS, STATUS_SCOPE, TimedStateQuery("batch", "status", "batch_status", "released", 20)),
    Case("AT05", STATUS, STATUS_SCOPE, TimedStateQuery("batch", "status", "batch_status", "released", 21)),
    Case("AT06", STATUS, None, TimedStateQuery("batch", "status", "batch_status", "released", 15)),
    Case("AT07", STATUS, TemporalScope("wrong", 10, 20), TimedStateQuery("batch", "status", "batch_status", "released", 15)),
    Case("AT08", StateContribution("state-status-1", False, "batch", "status", "batch_status", "released", True), STATUS_SCOPE, TimedStateQuery("batch", "status", "batch_status", "released", 15)),
    Case("AT09", STATUS, STATUS_SCOPE, TimedStateQuery("other_batch", "status", "batch_status", "released", 15)),
    Case("AT10", TAG, TAG_SCOPE, TimedStateQuery("record", "tag", "labels", "critical", 10)),
    Case("AT11", TAG, TAG_SCOPE, TimedStateQuery("record", "tag", "labels", "urgent", 10)),
    Case("AT12", STATUS, TemporalScope("state-status-1", 20, 10), TimedStateQuery("batch", "status", "batch_status", "released", 15)),
)


def failures(strategy: Strategy) -> tuple[str, ...]:
    bad: list[str] = []
    for case in CASES:
        receipt = strategy(case.state, case.scope, case.query)
        if not verify_receipt(receipt, case.state, case.scope, case.query):
            bad.append(case.case_id)
    return tuple(bad)
