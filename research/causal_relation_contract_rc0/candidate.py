"""Direct conservative candidate for Causal Relation Family Contract RC0."""

from __future__ import annotations

from .apparatus import Claim, Kind, Relation


def relate(source: Claim, query: Claim) -> Relation:
    if (source.cause, source.effect) != (query.cause, query.effect):
        return Relation.UNRESOLVED
    if source.kind is query.kind:
        return Relation.SUPPORTS
    if {source.kind, query.kind} == {Kind.CAUSES, Kind.PREVENTS}:
        return Relation.REFUTES
    return Relation.UNRESOLVED
