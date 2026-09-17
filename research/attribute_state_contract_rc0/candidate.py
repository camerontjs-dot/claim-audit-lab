"""Direct consumer candidate for Attribute State Family Contract RC0."""

from __future__ import annotations

from .apparatus import Relation, State


def relate(source: State, query: State) -> Relation:
    if (source.entity, source.attribute, source.domain) != (
        query.entity,
        query.attribute,
        query.domain,
    ):
        return Relation.UNRESOLVED
    if source.value == query.value:
        return Relation.SUPPORTS
    if source.functional and query.functional:
        return Relation.REFUTES
    return Relation.UNRESOLVED
