from __future__ import annotations

from dataclasses import dataclass

from .authority import AuthorityReceipt
from .models import AuditContext, CategoricalRelation, SemanticFamily, stable_id


@dataclass(frozen=True, slots=True)
class BoundRelation:
    relation_id: str
    categorical_relation: CategoricalRelation
    audit_context_sha256: str
    evidence_world_sha256: str
    proposition_sha256: str
    authority_id: str
    passage_id: str


class RelationRefusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _comparison_sign(value: str) -> int | None:
    mapping = {
        "MORE_THAN": 1,
        "GREATER_THAN": 1,
        "LESS_THAN": -1,
        "FEWER_THAN": -1,
    }
    return mapping.get(value.upper())


def _derive_comparison(context: AuditContext, fields: dict[str, str]) -> CategoricalRelation:
    target = context.proposition.field_map()
    required = {"lhs_entity", "rhs_entity", "comparison_direction"}
    if not required.issubset(target):
        raise RelationRefusal(
            "PROPOSITION_BINDING_FAILED", "strict comparison target fields missing"
        )
    lhs = target["lhs_entity"].casefold().strip()
    rhs = target["rhs_entity"].casefold().strip()
    expected = _comparison_sign(target["comparison_direction"])
    observed = _comparison_sign(fields.get("relation", ""))
    if expected is None:
        raise RelationRefusal("PROPOSITION_BINDING_FAILED", "unsupported comparison direction")
    if observed is None:
        return CategoricalRelation.UNRESOLVED
    left = fields.get("left", "").casefold().strip()
    right = fields.get("right", "").casefold().strip()
    if (left, right) == (lhs, rhs):
        normalized = observed
    elif (left, right) == (rhs, lhs):
        normalized = -observed
    else:
        return CategoricalRelation.IRRELEVANT
    return CategoricalRelation.SUPPORTS if normalized == expected else CategoricalRelation.REFUTES


def _event_tuple(fields: dict[str, str], side: str) -> tuple[str, str, str, str]:
    return (
        fields.get(f"{side}_subject", ""),
        fields.get(f"{side}_predicate", ""),
        fields.get(f"{side}_object", ""),
        fields.get(f"{side}_polarity", ""),
    )


def _derive_event(context: AuditContext, fields: dict[str, str]) -> CategoricalRelation:
    target = context.proposition.field_map()
    required = {
        "left_subject",
        "left_predicate",
        "left_object",
        "left_polarity",
        "temporal_relation",
        "right_subject",
        "right_predicate",
        "right_object",
        "right_polarity",
    }
    if not required.issubset(target):
        raise RelationRefusal(
            "PROPOSITION_BINDING_FAILED", "direct event-order target fields missing"
        )
    target_left = _event_tuple(target, "left")
    target_right = _event_tuple(target, "right")
    atom_left = _event_tuple(fields, "left")
    atom_right = _event_tuple(fields, "right")
    target_relation = target["temporal_relation"].upper()
    atom_relation = fields.get("temporal_relation", "").upper()
    if target_relation not in {"BEFORE", "AFTER"} or atom_relation not in {
        "BEFORE",
        "AFTER",
    }:
        raise RelationRefusal("PROPOSITION_BINDING_FAILED", "unsupported temporal relation")
    if (atom_left, atom_right) == (target_left, target_right):
        normalized = atom_relation
    elif (atom_left, atom_right) == (target_right, target_left):
        normalized = "AFTER" if atom_relation == "BEFORE" else "BEFORE"
    else:
        return CategoricalRelation.IRRELEVANT
    return (
        CategoricalRelation.SUPPORTS
        if normalized == target_relation
        else CategoricalRelation.REFUTES
    )  # noqa: E501


def derive_relation(context: AuditContext, authority: AuthorityReceipt) -> BoundRelation:
    if authority.status != "WARRANTED":
        raise RelationRefusal("SEMANTIC_AUTHORITY_UNRESOLVED", authority.status)
    if authority.audit_context_sha256 != context.context_sha256:
        raise RelationRefusal("PROPOSITION_BINDING_FAILED", "authority/context mismatch")
    if authority.evidence_world_sha256 != context.evidence_world.evidence_world_sha256:
        raise RelationRefusal("COMMON_EVIDENCE_WORLD_MISMATCH", "authority/world mismatch")
    atom = authority.atom
    if atom.audit_context_sha256 != context.context_sha256:
        raise RelationRefusal("PROPOSITION_BINDING_FAILED", "atom/context mismatch")
    fields = atom.field_map()
    if context.proposition.semantic_family is SemanticFamily.STRICT_COMPARISON:
        relation = _derive_comparison(context, fields)
    elif context.proposition.semantic_family is SemanticFamily.DIRECT_EVENT_ORDER:
        relation = _derive_event(context, fields)
    else:
        raise RelationRefusal("PROPOSITION_BINDING_FAILED", "unsupported proposition family")
    material = {
        "categorical_relation": relation.value,
        "audit_context_sha256": context.context_sha256,
        "evidence_world_sha256": context.evidence_world.evidence_world_sha256,
        "proposition_sha256": context.proposition.sha256,
        "authority_id": authority.authority_id,
        "passage_id": atom.passage_id,
    }
    return BoundRelation(
        relation_id=stable_id("bound-relation", material),
        categorical_relation=relation,
        audit_context_sha256=context.context_sha256,
        evidence_world_sha256=context.evidence_world.evidence_world_sha256,
        proposition_sha256=context.proposition.sha256,
        authority_id=authority.authority_id,
        passage_id=atom.passage_id,
    )
