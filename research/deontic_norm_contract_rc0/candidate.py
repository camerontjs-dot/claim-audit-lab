"""Direct consumer candidate for CAL Deontic Norm Family Contract RC0."""

from __future__ import annotations

from .cohort import Mode, Norm, Relation


def _same_scope(source: Norm, query: Norm) -> bool:
    return (
        source.subject == query.subject
        and source.action == query.action
        and source.exceptions == query.exceptions
        and source.condition == query.condition
        and source.temporal_relation == query.temporal_relation
        and source.temporal_reference == query.temporal_reference
    )


def relate(source: Norm, query: Norm) -> Relation:
    """Derive the bounded direct relation without stronger deontic implication."""
    if not _same_scope(source, query):
        return Relation.UNRESOLVED

    if source.mode is query.mode:
        return Relation.SUPPORTS

    if {source.mode, query.mode} == {Mode.PERMITTED, Mode.PROHIBITED}:
        return Relation.REFUTES

    if {source.mode, query.mode} == {Mode.OBLIGATORY, Mode.PROHIBITED}:
        return Relation.REFUTES

    return Relation.UNRESOLVED
