"""Frozen apparatus for spatial composition discriminator RC1."""

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
class WarrantedRelation:
    authority_id: str
    source_sha256: str
    subject: str
    predicate: str
    object: str
    positive: bool = True


@dataclass(frozen=True, slots=True)
class RelationQuery:
    subject: str
    predicate: str
    object: str
    positive: bool = True


@dataclass(frozen=True, slots=True)
class CompositionReceipt:
    receipt_id: str
    relation: Relation
    left_authority_id: str
    right_authority_id: str
    derived_subject: str
    derived_predicate: str
    derived_object: str
    derived_positive: bool


@dataclass(frozen=True, slots=True)
class Spec:
    inverse: str | None = None
    symmetric: bool = False
    transitive: bool = False


SPECS = {
    "OWNS": Spec(inverse="OWNED_BY"),
    "OWNED_BY": Spec(inverse="OWNS"),
    "ADJACENT_TO": Spec(symmetric=True),
    "NORTH_OF": Spec(inverse="SOUTH_OF"),
    "SOUTH_OF": Spec(inverse="NORTH_OF"),
    "IN": Spec(inverse="CONTAINS", transitive=True),
    "CONTAINS": Spec(inverse="IN", transitive=True),
}


class Strategy(Protocol):
    def __call__(
        self,
        left: WarrantedRelation,
        right: WarrantedRelation,
        query: RelationQuery,
    ) -> CompositionReceipt: ...


def _stable(material: dict[str, object]) -> str:
    payload = json.dumps(material, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _normalize(atom: WarrantedRelation) -> tuple[str, str, str, bool] | None:
    spec = SPECS.get(atom.predicate)
    if spec is None:
        return None
    if atom.predicate == "CONTAINS":
        return (atom.object, "IN", atom.subject, atom.positive)
    return (atom.subject, atom.predicate, atom.object, atom.positive)


def oracle(
    left: WarrantedRelation,
    right: WarrantedRelation,
    query: RelationQuery,
) -> tuple[Relation, tuple[str, str, str, bool] | None]:
    l = _normalize(left)
    r = _normalize(right)
    if l is None or r is None:
        return Relation.UNRESOLVED, None
    if not l[3] or not r[3]:
        return Relation.UNRESOLVED, None

    lspec = SPECS[l[1]]
    rspec = SPECS[r[1]]
    if l[1] != r[1] or not lspec.transitive or not rspec.transitive:
        return Relation.UNRESOLVED, None
    if l[2] != r[0]:
        return Relation.UNRESOLVED, None

    derived = (l[0], l[1], r[2], True)
    q = (query.subject, query.predicate, query.object, query.positive)

    if query.predicate == "CONTAINS":
        qnorm = (query.object, "IN", query.subject, query.positive)
    else:
        qnorm = q

    if derived[:3] != qnorm[:3]:
        return Relation.UNRESOLVED, derived
    return (
        Relation.SUPPORTS if derived[3] == qnorm[3] else Relation.REFUTES,
        derived,
    )


def verify_receipt(
    receipt: CompositionReceipt,
    left: WarrantedRelation,
    right: WarrantedRelation,
    query: RelationQuery,
) -> bool:
    relation, derived = oracle(left, right, query)
    if receipt.relation is not relation:
        return False

    if relation is Relation.UNRESOLVED:
        return (
            receipt.left_authority_id == ""
            and receipt.right_authority_id == ""
            and receipt.derived_subject == ""
            and receipt.derived_predicate == ""
            and receipt.derived_object == ""
        )

    assert derived is not None
    if receipt.left_authority_id != left.authority_id:
        return False
    if receipt.right_authority_id != right.authority_id:
        return False
    if (
        receipt.derived_subject,
        receipt.derived_predicate,
        receipt.derived_object,
        receipt.derived_positive,
    ) != derived:
        return False

    material = {
        "relation": receipt.relation.value,
        "left_authority_id": receipt.left_authority_id,
        "right_authority_id": receipt.right_authority_id,
        "derived_subject": receipt.derived_subject,
        "derived_predicate": receipt.derived_predicate,
        "derived_object": receipt.derived_object,
        "derived_positive": receipt.derived_positive,
    }
    return receipt.receipt_id == _stable(material)


def weak_relation_only(
    left: WarrantedRelation,
    right: WarrantedRelation,
    query: RelationQuery,
) -> CompositionReceipt:
    relation, _ = oracle(left, right, query)
    return CompositionReceipt("", relation, "", "", "", "", "", True)


def weak_all_transitive(
    left: WarrantedRelation,
    right: WarrantedRelation,
    query: RelationQuery,
) -> CompositionReceipt:
    if left.predicate == right.predicate and left.object == right.subject:
        derived = (left.subject, left.predicate, right.object, left.positive and right.positive)
        relation = (
            Relation.SUPPORTS
            if derived[:3] == (query.subject, query.predicate, query.object)
            and derived[3] == query.positive
            else Relation.UNRESOLVED
        )
        return CompositionReceipt("weak", relation, left.authority_id, right.authority_id, *derived)
    return weak_relation_only(left, right, query)


def weak_no_transitivity(
    left: WarrantedRelation,
    right: WarrantedRelation,
    query: RelationQuery,
) -> CompositionReceipt:
    del left, right, query
    return CompositionReceipt("", Relation.UNRESOLVED, "", "", "", "", "", True)


def weak_container_inherits_direction(
    left: WarrantedRelation,
    right: WarrantedRelation,
    query: RelationQuery,
) -> CompositionReceipt:
    if (
        left.predicate == "IN"
        and right.predicate in {"NORTH_OF", "SOUTH_OF"}
        and left.object == right.subject
        and (left.subject, right.predicate, right.object)
        == (query.subject, query.predicate, query.object)
    ):
        return CompositionReceipt(
            "weak",
            Relation.SUPPORTS,
            left.authority_id,
            right.authority_id,
            left.subject,
            right.predicate,
            right.object,
            True,
        )
    return weak_relation_only(left, right, query)


def W(a: str, s: str, p: str, o: str, positive: bool = True) -> WarrantedRelation:
    return WarrantedRelation(a, f"sha-{a}", s, p, o, positive)


CASES: tuple[tuple[str, WarrantedRelation, WarrantedRelation, RelationQuery], ...] = (
    ("S1", W("a1", "room", "IN", "zone"), W("a2", "zone", "IN", "building"), RelationQuery("room", "IN", "building")),
    ("S2", W("a3", "building", "CONTAINS", "zone"), W("a4", "zone", "CONTAINS", "room"), RelationQuery("building", "CONTAINS", "room")),
    ("S3", W("a5", "room", "IN", "zone"), W("a6", "building", "CONTAINS", "zone"), RelationQuery("building", "CONTAINS", "room")),
    ("S4", W("a7", "room", "IN", "zone"), W("a8", "zone", "IN", "building"), RelationQuery("room", "IN", "building", False)),
    ("S5", W("a9", "a", "ADJACENT_TO", "b"), W("a10", "b", "ADJACENT_TO", "c"), RelationQuery("a", "ADJACENT_TO", "c")),
    ("S6", W("a11", "a", "NORTH_OF", "b"), W("a12", "b", "NORTH_OF", "c"), RelationQuery("a", "NORTH_OF", "c")),
    ("S7", W("a13", "a", "OWNS", "b"), W("a14", "b", "OWNS", "c"), RelationQuery("a", "OWNS", "c")),
    ("S8", W("a15", "room", "IN", "zone_a"), W("a16", "zone_a", "NORTH_OF", "zone_b"), RelationQuery("room", "NORTH_OF", "zone_b")),
    ("S9", W("a17", "room", "IN", "zone"), W("a18", "other", "IN", "building"), RelationQuery("room", "IN", "building")),
    ("S10", W("a19", "a", "CUSTOM", "b"), W("a20", "b", "CUSTOM", "c"), RelationQuery("a", "CUSTOM", "c")),
)


def failures(strategy: Strategy) -> tuple[str, ...]:
    bad: list[str] = []
    for case_id, left, right, query in CASES:
        receipt = strategy(left, right, query)
        if not verify_receipt(receipt, left, right, query):
            bad.append(case_id)
    return tuple(bad)
