"""Frozen apparatus for quantitative-change integration RC1."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from enum import StrEnum
from fractions import Fraction
from typing import Protocol


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
class WarrantedScalar:
    authority_id: str
    source_sha256: str
    entity: str
    metric: str
    unit: str
    low: Fraction
    high: Fraction
    exact: bool


@dataclass(frozen=True, slots=True)
class TemporalBinding:
    authority_id: str
    instant_id: str
    ordinal: int


@dataclass(frozen=True, slots=True)
class ChangeQuery:
    entity: str
    metric: str
    unit: str
    kind: Kind
    amount: Fraction | None = None


@dataclass(frozen=True, slots=True)
class ChangeReceipt:
    receipt_id: str
    relation: Relation
    old_authority_id: str
    new_authority_id: str
    old_instant_id: str
    new_instant_id: str
    delta: Fraction | None
    query: ChangeQuery


class Strategy(Protocol):
    def __call__(
        self,
        left: WarrantedScalar,
        right: WarrantedScalar,
        left_time: TemporalBinding,
        right_time: TemporalBinding,
        query: ChangeQuery,
    ) -> ChangeReceipt: ...


def _stable(material: dict[str, object]) -> str:
    payload = json.dumps(material, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def oracle_relation(
    left: WarrantedScalar,
    right: WarrantedScalar,
    left_time: TemporalBinding,
    right_time: TemporalBinding,
    query: ChangeQuery,
) -> Relation:
    if left_time.authority_id != left.authority_id:
        return Relation.UNRESOLVED
    if right_time.authority_id != right.authority_id:
        return Relation.UNRESOLVED
    if left_time.ordinal == right_time.ordinal:
        return Relation.UNRESOLVED
    if not left.exact or not right.exact:
        return Relation.UNRESOLVED
    if left.low != left.high or right.low != right.high:
        return Relation.UNRESOLVED
    if (left.entity, left.metric, left.unit) != (right.entity, right.metric, right.unit):
        return Relation.UNRESOLVED
    if (left.entity, left.metric, left.unit) != (query.entity, query.metric, query.unit):
        return Relation.UNRESOLVED

    old, new = (left, right) if left_time.ordinal < right_time.ordinal else (right, left)
    delta = new.low - old.low
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


def verify_receipt(
    receipt: ChangeReceipt,
    left: WarrantedScalar,
    right: WarrantedScalar,
    left_time: TemporalBinding,
    right_time: TemporalBinding,
    query: ChangeQuery,
) -> bool:
    expected_relation = oracle_relation(left, right, left_time, right_time, query)
    if receipt.relation is not expected_relation:
        return False

    if expected_relation is Relation.UNRESOLVED:
        return (
            receipt.old_authority_id == ""
            and receipt.new_authority_id == ""
            and receipt.old_instant_id == ""
            and receipt.new_instant_id == ""
            and receipt.delta is None
        )

    if left_time.ordinal < right_time.ordinal:
        old, new = left, right
        old_time, new_time = left_time, right_time
    else:
        old, new = right, left
        old_time, new_time = right_time, left_time

    if receipt.old_authority_id != old.authority_id:
        return False
    if receipt.new_authority_id != new.authority_id:
        return False
    if receipt.old_instant_id != old_time.instant_id:
        return False
    if receipt.new_instant_id != new_time.instant_id:
        return False
    if receipt.delta != new.low - old.low:
        return False
    if receipt.query != query:
        return False

    material = {
        "relation": receipt.relation.value,
        "old_authority_id": receipt.old_authority_id,
        "new_authority_id": receipt.new_authority_id,
        "old_instant_id": receipt.old_instant_id,
        "new_instant_id": receipt.new_instant_id,
        "delta": str(receipt.delta),
        "query": {
            "entity": query.entity,
            "metric": query.metric,
            "unit": query.unit,
            "kind": query.kind.value,
            "amount": None if query.amount is None else str(query.amount),
        },
    }
    return receipt.receipt_id == _stable(material)


def weak_relation_only(
    left: WarrantedScalar,
    right: WarrantedScalar,
    left_time: TemporalBinding,
    right_time: TemporalBinding,
    query: ChangeQuery,
) -> ChangeReceipt:
    return ChangeReceipt(
        receipt_id="",
        relation=oracle_relation(left, right, left_time, right_time, query),
        old_authority_id="",
        new_authority_id="",
        old_instant_id="",
        new_instant_id="",
        delta=None,
        query=query,
    )


def weak_input_order(
    left: WarrantedScalar,
    right: WarrantedScalar,
    left_time: TemporalBinding,
    right_time: TemporalBinding,
    query: ChangeQuery,
) -> ChangeReceipt:
    del left_time, right_time
    fake_l = TemporalBinding(left.authority_id, "input-left", 1)
    fake_r = TemporalBinding(right.authority_id, "input-right", 2)
    relation = oracle_relation(left, right, fake_l, fake_r, query)
    delta = right.low - left.low if relation is not Relation.UNRESOLVED else None
    return ChangeReceipt(
        receipt_id="weak",
        relation=relation,
        old_authority_id=left.authority_id,
        new_authority_id=right.authority_id,
        old_instant_id="input-left",
        new_instant_id="input-right",
        delta=delta,
        query=query,
    )


def weak_force_exact(
    left: WarrantedScalar,
    right: WarrantedScalar,
    left_time: TemporalBinding,
    right_time: TemporalBinding,
    query: ChangeQuery,
) -> ChangeReceipt:
    return weak_relation_only(
        replace(left, exact=True, low=left.low, high=left.low),
        replace(right, exact=True, low=right.low, high=right.low),
        left_time,
        right_time,
        query,
    )


F = Fraction
OLD = WarrantedScalar("auth-old", "sha-old", "batch", "yield", "%", F(92), F(92), True)
NEW = WarrantedScalar("auth-new", "sha-new", "batch", "yield", "%", F(95), F(95), True)
T1 = TemporalBinding("auth-old", "T1", 1)
T2 = TemporalBinding("auth-new", "T2", 2)

CASES: tuple[
    tuple[str, WarrantedScalar, WarrantedScalar, TemporalBinding, TemporalBinding, ChangeQuery],
    ...,
] = (
    ("Q1", OLD, NEW, T1, T2, ChangeQuery("batch", "yield", "%", Kind.INCREASED)),
    ("Q2", OLD, NEW, T1, T2, ChangeQuery("batch", "yield", "%", Kind.DECREASED)),
    ("Q3", OLD, NEW, T1, T2, ChangeQuery("batch", "yield", "%", Kind.DELTA, F(3))),
    ("Q4", OLD, replace(NEW, low=F(92), high=F(92)), T1, T2, ChangeQuery("batch", "yield", "%", Kind.UNCHANGED)),
    ("Q5", NEW, OLD, T2, T1, ChangeQuery("batch", "yield", "%", Kind.INCREASED)),
    ("Q6", replace(OLD, exact=False), NEW, T1, T2, ChangeQuery("batch", "yield", "%", Kind.INCREASED)),
    ("Q7", replace(OLD, low=F(90), high=F(94), exact=False), NEW, T1, T2, ChangeQuery("batch", "yield", "%", Kind.INCREASED)),
    ("Q8", OLD, replace(NEW, unit="fraction"), T1, T2, ChangeQuery("batch", "yield", "%", Kind.INCREASED)),
    ("Q9", OLD, NEW, T1, replace(T2, ordinal=1), ChangeQuery("batch", "yield", "%", Kind.INCREASED)),
    ("Q10", OLD, NEW, replace(T1, authority_id="wrong"), T2, ChangeQuery("batch", "yield", "%", Kind.INCREASED)),
)


def failures(strategy: Strategy) -> tuple[str, ...]:
    bad: list[str] = []
    for case_id, left, right, left_time, right_time, query in CASES:
        receipt = strategy(left, right, left_time, right_time, query)
        if not verify_receipt(receipt, left, right, left_time, right_time, query):
            bad.append(case_id)
    return tuple(bad)
