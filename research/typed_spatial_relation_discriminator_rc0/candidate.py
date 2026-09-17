"""Generic typed-relation candidate for typed/spatial discriminator RC0."""

from __future__ import annotations

from .apparatus import SPECS, Atom, Relation


def _same_relation(source: Atom, query: Atom) -> bool:
    source_spec = SPECS.get(source.predicate)
    if source_spec is None or query.predicate not in SPECS:
        return False
    if (source.subject, source.predicate, source.object) == (
        query.subject,
        query.predicate,
        query.object,
    ):
        return True
    if source_spec.symmetric and source.predicate == query.predicate:
        return (source.subject, source.object) == (query.object, query.subject)
    if source_spec.inverse == query.predicate:
        return (source.subject, source.object) == (query.object, query.subject)
    return False


def relate(source: Atom, query: Atom) -> Relation:
    if not _same_relation(source, query):
        return Relation.UNRESOLVED
    return Relation.SUPPORTS if source.positive == query.positive else Relation.REFUTES
