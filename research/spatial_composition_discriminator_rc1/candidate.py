"""Metadata-bounded spatial composition candidate RC1."""

from __future__ import annotations

from research.typed_binary_measurement_machinery_rc1.cohort import RelationAtom

from .apparatus import Contribution, Relation


def _normalize(atom: RelationAtom) -> tuple[str, str, str] | None:
    if atom.predicate == "IN":
        return ("IN", atom.subject, atom.object)
    if atom.predicate == "CONTAINS":
        return ("IN", atom.object, atom.subject)
    if atom.predicate == "NORTH_OF":
        return ("NORTH_OF", atom.subject, atom.object)
    if atom.predicate == "SOUTH_OF":
        return ("NORTH_OF", atom.object, atom.subject)
    return None


def _chain(
    first: tuple[str, str, str],
    second: tuple[str, str, str],
) -> tuple[str, str, str] | None:
    if first[0] != second[0]:
        return None
    if first[2] == second[1]:
        return (first[0], first[1], second[2])
    if second[2] == first[1]:
        return (first[0], second[1], first[2])
    return None


def compose_relation(
    left: Contribution,
    right: Contribution,
    query: RelationAtom,
) -> Relation:
    if not left.warranted or not right.warranted:
        return Relation.UNRESOLVED
    if not left.authority_id or not right.authority_id:
        return Relation.UNRESOLVED
    if left.authority_id == right.authority_id:
        return Relation.UNRESOLVED
    if not left.atom.positive or not right.atom.positive:
        return Relation.UNRESOLVED

    first = _normalize(left.atom)
    second = _normalize(right.atom)
    target = _normalize(query)
    if first is None or second is None or target is None:
        return Relation.UNRESOLVED

    if first[0] != second[0] or first[0] != target[0]:
        return Relation.UNRESOLVED

    if first[0] == "NORTH_OF":
        if not left.frame_established or not right.frame_established:
            return Relation.UNRESOLVED
        if left.frame_id is None or right.frame_id is None:
            return Relation.UNRESOLVED
        if left.frame_id != right.frame_id:
            return Relation.UNRESOLVED

    derived = _chain(first, second)
    if derived is None:
        return Relation.UNRESOLVED
    if derived[1] == derived[2]:
        return Relation.UNRESOLVED
    if derived != target:
        return Relation.UNRESOLVED

    return Relation.SUPPORTS if query.positive else Relation.REFUTES
