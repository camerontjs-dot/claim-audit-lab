"""Direct consumer candidate for Event Occurrence Family Contract RC0."""

from __future__ import annotations

from .apparatus import Event, Relation, SourceKind


def relate(source: Event, query: Event) -> Relation:
    if source.source_kind is not SourceKind.DIRECT:
        return Relation.UNRESOLVED
    if (
        source.actor,
        source.action,
        source.object,
        source.scope,
        source.time,
    ) != (
        query.actor,
        query.action,
        query.object,
        query.scope,
        query.time,
    ):
        return Relation.UNRESOLVED
    return Relation.SUPPORTS if source.polarity is query.polarity else Relation.REFUTES
