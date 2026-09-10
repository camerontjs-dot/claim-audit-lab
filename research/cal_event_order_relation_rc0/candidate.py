"""Decisive CAL event-order relation RC0 candidate.

Adds exact proposition-projection identity at composition after the pre-science
seam recorded in DEVELOPMENT_NOTES.md. All other warrant, binding, relation and
scoreless-composition semantics remain in relation.py.
"""
from __future__ import annotations

from typing import Iterable

from . import relation as base

AUTHORITY_BINDING_FIELDS = base.AUTHORITY_BINDING_FIELDS
ATOM_WARRANT_SCHEMA = base.ATOM_WARRANT_SCHEMA
EVENT_FIELDS = base.EVENT_FIELDS
EVENT_FAMILY = base.EVENT_FAMILY
EventSemantics = base.EventSemantics
PROPOSITION_BINDING_SCHEMA = base.PROPOSITION_BINDING_SCHEMA
RelationRefusal = base.RelationRefusal
TemporalConclusion = base.TemporalConclusion
TemporalProposition = base.TemporalProposition
TemporalRelationRecord = base.TemporalRelationRecord
authority_binding_projection = base.authority_binding_projection
authority_subject_digest = base.authority_subject_digest
canonical_json_bytes = base.canonical_json_bytes
derive_temporal_relation = base.derive_temporal_relation
issue_event_atom_warrant = base.issue_event_atom_warrant
issue_proposition_binding = base.issue_proposition_binding
proposition_projection = base.proposition_projection
verify_event_atom_warrant = base.verify_event_atom_warrant
verify_proposition_binding = base.verify_proposition_binding
weak_claim_id_only_relation = base.weak_claim_id_only_relation


def compose_temporal_relations(
    *, proposition: TemporalProposition, relations: Iterable[TemporalRelationRecord]
) -> TemporalConclusion:
    rows = tuple(relations)
    exact_projection = proposition_projection(proposition)
    for row in rows:
        if row.proposition_projection != exact_projection:
            raise RelationRefusal(
                "COMPOSITION_PROPOSITION_MISMATCH",
                row.relation_id,
            )
    return base.compose_temporal_relations(proposition=proposition, relations=rows)


__all__ = [
    "AUTHORITY_BINDING_FIELDS",
    "ATOM_WARRANT_SCHEMA",
    "EVENT_FIELDS",
    "EVENT_FAMILY",
    "EventSemantics",
    "PROPOSITION_BINDING_SCHEMA",
    "RelationRefusal",
    "TemporalConclusion",
    "TemporalProposition",
    "TemporalRelationRecord",
    "authority_binding_projection",
    "authority_subject_digest",
    "canonical_json_bytes",
    "compose_temporal_relations",
    "derive_temporal_relation",
    "issue_event_atom_warrant",
    "issue_proposition_binding",
    "proposition_projection",
    "verify_event_atom_warrant",
    "verify_proposition_binding",
    "weak_claim_id_only_relation",
]
