"""Generic temporal-scope composition for attribute-state applicability RC0."""

from __future__ import annotations

from .apparatus import (
    Relation,
    StateContribution,
    TemporalScope,
    TemporalStateReceipt,
    TimedStateQuery,
    _stable,
    oracle_relation,
)


def compose_timed_state(
    state: StateContribution,
    scope: TemporalScope | None,
    query: TimedStateQuery,
) -> TemporalStateReceipt:
    relation = oracle_relation(state, scope, query)
    if relation is Relation.UNRESOLVED:
        return TemporalStateReceipt("", relation, "", None, None, None)

    assert scope is not None
    material = {
        "relation": relation.value,
        "authority_id": state.authority_id,
        "scope_start": scope.start_ordinal,
        "scope_end": scope.end_ordinal,
        "target_ordinal": query.target_ordinal,
        "query": {
            "entity": query.entity,
            "attribute": query.attribute,
            "domain": query.domain,
            "value": query.value,
        },
    }
    return TemporalStateReceipt(
        receipt_id=_stable(material),
        relation=relation,
        authority_id=state.authority_id,
        scope_start=scope.start_ordinal,
        scope_end=scope.end_ordinal,
        target_ordinal=query.target_ordinal,
    )
