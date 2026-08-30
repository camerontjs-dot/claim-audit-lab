from __future__ import annotations

import hashlib
import json
from itertools import product
from typing import Any

SCHEMA_VERSION = "population-semantics-contract-rc5.0"


def case(case_id: str, dimension: str, authority: dict[str, Any], query: dict[str, Any]) -> dict[str, Any]:
    return {"case_id": case_id, "dimension": dimension, "authority": authority, "query": query}


def build_cases() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    idx = 0
    for target_entity, membership, modality, polarity, query_kind in product(
        ("e0", "e1"), ("member", "non_member", "unknown"), ("fact", "obligation"),
        ("positive", "negative"), ("membership", "rule_applies", "behavior_positive", "behavior_negative"),
    ):
        idx += 1
        out.append(case(f"M-{idx:03d}", "membership_rule",
            {"entity": "e0", "population": "C", "membership": membership,
             "rule": {"population": "C", "predicate": "P", "modality": modality, "polarity": polarity}},
            {"kind": query_kind, "entity": target_entity, "population": "C", "predicate": "P"}))

    idx = 0
    for edge, membership_class, membership_status, query_class in product(
        ("A_sub_B", "B_sub_A", "none"), ("A", "B"), ("member", "non_member", "unknown"), ("A", "B")
    ):
        idx += 1
        out.append(case(f"S-{idx:03d}", "subclass",
            {"entity": "e0", "membership_population": membership_class, "membership": membership_status, "subclass_edge": edge},
            {"kind": "membership", "entity": "e0", "population": query_class}))

    idx = 0
    for entity, membership, explicit_permission, query_kind in product(
        ("e0", "e1"), ("member", "non_member", "unknown"),
        ("permitted", "not_permitted", "unknown"), ("membership", "permission")
    ):
        idx += 1
        out.append(case(f"O-{idx:03d}", "only_permission",
            {"entity": "e0", "population": "C", "membership": membership, "predicate": "P",
             "only_population_may": True, "explicit_permission": explicit_permission},
            {"kind": query_kind, "entity": entity, "population": "C", "predicate": "P"}))

    idx = 0
    for authority_q, query_q, predicate in product(
        ("every", "none", "some", "not_every"), ("every", "none", "some", "not_every"), ("P", "Q")
    ):
        idx += 1
        out.append(case(f"Q-{idx:03d}", "quantifier",
            {"population": "C", "members": ["e0", "e1"], "predicate": "P", "quantifier": authority_q, "polarity": "positive"},
            {"kind": "quantified", "population": "C", "predicate": predicate, "quantifier": query_q, "polarity": "positive"}))

    idx = 0
    for authority_scope, authority_pred, query_scope, query_pred in product(
        ("group", "member:e0"), ("P", "Q"), ("group", "member:e0", "member:e1"), ("P", "Q")
    ):
        idx += 1
        out.append(case(f"G-{idx:03d}", "group_scope",
            {"group": "G", "members": ["e0", "e1"], "event_scope": authority_scope, "predicate": authority_pred, "polarity": "positive"},
            {"kind": "event", "group": "G", "event_scope": query_scope, "predicate": query_pred, "polarity": "positive"}))

    idx = 0
    for predicate, subject, obj, polarity, q_predicate, q_subject, q_object, q_polarity in product(
        ("reviews", "approves"), ("e0", "e1"), ("e0", "e1"), ("positive", "negative"),
        ("reviews", "approves"), ("e0", "e1"), ("e0", "e1"), ("positive", "negative"),
    ):
        if subject == obj or q_subject == q_object:
            continue
        idx += 1
        out.append(case(f"R-{idx:03d}", "role_binding",
            {"event": {"predicate": predicate, "roles": {"subject": subject, "object": obj}, "polarity": polarity}},
            {"kind": "event", "predicate": q_predicate, "roles": {"subject": q_subject, "object": q_object}, "polarity": q_polarity}))

    idx = 0
    for window, query_time, modality, polarity, query_kind in product(
        ("before_only", "after_only", "always", "never", "unknown"), ("before", "after"),
        ("fact", "obligation"), ("positive", "negative"),
        ("membership", "rule_applies", "behavior_positive", "behavior_negative"),
    ):
        idx += 1
        out.append(case(f"T-{idx:03d}", "temporal_membership",
            {"entity": "e0", "population": "C", "membership_window": window, "boundary": "cutoff",
             "rule": {"population": "C", "predicate": "P", "modality": modality, "polarity": polarity}},
            {"kind": query_kind, "entity": "e0", "population": "C", "predicate": "P", "time": query_time}))
    return out


def build_ablation_witnesses() -> list[dict[str, Any]]:
    return [
        {"field": "entity_identity", "field_path": ["authority", "entity"],
         "left": case("A-entity-L", "membership_rule", {"entity": "e0", "population": "C", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"}),
         "right": case("A-entity-R", "membership_rule", {"entity": "e1", "population": "C", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"})},
        {"field": "population_identity", "field_path": ["authority", "population"],
         "left": case("A-pop-L", "membership_rule", {"entity": "e0", "population": "C", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"}),
         "right": case("A-pop-R", "membership_rule", {"entity": "e0", "population": "D", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"})},
        {"field": "membership_status", "field_path": ["authority", "membership"],
         "left": case("A-mem-L", "membership_rule", {"entity": "e0", "population": "C", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"}),
         "right": case("A-mem-R", "membership_rule", {"entity": "e0", "population": "C", "membership": "non_member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"})},
        {"field": "directed_subclass_edge", "field_path": ["authority", "subclass_edge"],
         "left": case("A-sub-L", "subclass", {"entity": "e0", "membership_population": "A", "membership": "member", "subclass_edge": "A_sub_B"}, {"kind": "membership", "entity": "e0", "population": "B"}),
         "right": case("A-sub-R", "subclass", {"entity": "e0", "membership_population": "A", "membership": "member", "subclass_edge": "B_sub_A"}, {"kind": "membership", "entity": "e0", "population": "B"})},
        {"field": "predicate_identity", "field_path": ["authority", "predicate"],
         "left": case("A-pred-L", "group_scope", {"group": "G", "members": ["e0", "e1"], "event_scope": "group", "predicate": "P", "polarity": "positive"}, {"kind": "event", "group": "G", "event_scope": "group", "predicate": "P", "polarity": "positive"}),
         "right": case("A-pred-R", "group_scope", {"group": "G", "members": ["e0", "e1"], "event_scope": "group", "predicate": "Q", "polarity": "positive"}, {"kind": "event", "group": "G", "event_scope": "group", "predicate": "P", "polarity": "positive"})},
        {"field": "modality", "field_path": ["authority", "rule", "modality"],
         "left": case("A-mod-L", "membership_rule", {"entity": "e0", "population": "C", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "fact", "polarity": "positive"}}, {"kind": "behavior_positive", "entity": "e0", "population": "C", "predicate": "P"}),
         "right": case("A-mod-R", "membership_rule", {"entity": "e0", "population": "C", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "behavior_positive", "entity": "e0", "population": "C", "predicate": "P"})},
        {"field": "population_quantifier", "field_path": ["authority", "quantifier"],
         "left": case("A-quant-L", "quantifier", {"population": "C", "members": ["e0", "e1"], "predicate": "P", "quantifier": "every", "polarity": "positive"}, {"kind": "quantified", "population": "C", "predicate": "P", "quantifier": "some", "polarity": "positive"}),
         "right": case("A-quant-R", "quantifier", {"population": "C", "members": ["e0", "e1"], "predicate": "P", "quantifier": "none", "polarity": "positive"}, {"kind": "quantified", "population": "C", "predicate": "P", "quantifier": "some", "polarity": "positive"})},
        {"field": "only_semantics", "field_path": ["authority", "only_population_may"],
         "left": case("A-only-L", "only_permission", {"entity": "e0", "population": "C", "membership": "non_member", "predicate": "P", "only_population_may": True, "explicit_permission": "unknown"}, {"kind": "permission", "entity": "e0", "population": "C", "predicate": "P"}),
         "right": case("A-only-R", "only_permission", {"entity": "e0", "population": "C", "membership": "non_member", "predicate": "P", "only_population_may": False, "explicit_permission": "unknown"}, {"kind": "permission", "entity": "e0", "population": "C", "predicate": "P"})},
        {"field": "group_member_scope", "field_path": ["authority", "event_scope"],
         "left": case("A-scope-L", "group_scope", {"group": "G", "members": ["e0", "e1"], "event_scope": "group", "predicate": "P", "polarity": "positive"}, {"kind": "event", "group": "G", "event_scope": "group", "predicate": "P", "polarity": "positive"}),
         "right": case("A-scope-R", "group_scope", {"group": "G", "members": ["e0", "e1"], "event_scope": "member:e0", "predicate": "P", "polarity": "positive"}, {"kind": "event", "group": "G", "event_scope": "group", "predicate": "P", "polarity": "positive"})},
        {"field": "ordered_roles", "field_path": ["authority", "event", "roles"],
         "left": case("A-role-L", "role_binding", {"event": {"predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"}}, {"kind": "event", "predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"}),
         "right": case("A-role-R", "role_binding", {"event": {"predicate": "reviews", "roles": {"subject": "e1", "object": "e0"}, "polarity": "positive"}}, {"kind": "event", "predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"})},
        {"field": "temporal_boundary_direction", "field_path": ["authority", "membership_window"],
         "left": case("A-time-L", "temporal_membership", {"entity": "e0", "population": "C", "membership_window": "before_only", "boundary": "cutoff", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P", "time": "before"}),
         "right": case("A-time-R", "temporal_membership", {"entity": "e0", "population": "C", "membership_window": "after_only", "boundary": "cutoff", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P", "time": "before"})},
        {"field": "polarity", "field_path": ["authority", "event", "polarity"],
         "left": case("A-pol-L", "role_binding", {"event": {"predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"}}, {"kind": "event", "predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"}),
         "right": case("A-pol-R", "role_binding", {"event": {"predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "negative"}}, {"kind": "event", "predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"})},
        {"field": "explicit_unknown", "field_path": ["authority", "membership"],
         "left": case("A-unk-L", "membership_rule", {"entity": "e0", "population": "C", "membership": "unknown", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"}),
         "right": case("A-unk-R", "membership_rule", {"entity": "e0", "population": "C", "membership": "non_member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"})},
    ]


def build_metamorphic_pairs() -> list[dict[str, Any]]:
    return [
        {"name": "entity_rename_invariance", "left_case_id": "META-rename-L", "right_case_id": "META-rename-R", "relation": "same"},
        {"name": "irrelevant_entity_addition", "left_case_id": "META-irrel-L", "right_case_id": "META-irrel-R", "relation": "same"},
        {"name": "membership_flip", "left_case_id": "META-mem-L", "right_case_id": "META-mem-R", "relation": "different"},
        {"name": "subclass_reversal", "left_case_id": "META-sub-L", "right_case_id": "META-sub-R", "relation": "different"},
        {"name": "quantifier_strength", "left_case_id": "META-quant-L", "right_case_id": "META-quant-R", "relation": "different"},
        {"name": "role_swap", "left_case_id": "META-role-L", "right_case_id": "META-role-R", "relation": "different"},
        {"name": "group_member_scope_change", "left_case_id": "META-scope-L", "right_case_id": "META-scope-R", "relation": "different"},
        {"name": "temporal_boundary_cross", "left_case_id": "META-time-L", "right_case_id": "META-time-R", "relation": "different"},
    ]


def build_metamorphic_cases() -> list[dict[str, Any]]:
    return [
        case("META-rename-L", "membership_rule", {"entity": "e0", "population": "C", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"}),
        case("META-rename-R", "membership_rule", {"entity": "z9", "population": "C", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "z9", "population": "C", "predicate": "P"}),
        case("META-irrel-L", "quantifier", {"population": "C", "members": ["e0", "e1"], "predicate": "P", "quantifier": "every", "polarity": "positive"}, {"kind": "quantified", "population": "C", "predicate": "P", "quantifier": "some", "polarity": "positive"}),
        case("META-irrel-R", "quantifier", {"population": "C", "members": ["e0", "e1"], "irrelevant_entities": ["z9"], "predicate": "P", "quantifier": "every", "polarity": "positive"}, {"kind": "quantified", "population": "C", "predicate": "P", "quantifier": "some", "polarity": "positive"}),
        case("META-mem-L", "membership_rule", {"entity": "e0", "population": "C", "membership": "member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"}),
        case("META-mem-R", "membership_rule", {"entity": "e0", "population": "C", "membership": "non_member", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P"}),
        case("META-sub-L", "subclass", {"entity": "e0", "membership_population": "A", "membership": "member", "subclass_edge": "A_sub_B"}, {"kind": "membership", "entity": "e0", "population": "B"}),
        case("META-sub-R", "subclass", {"entity": "e0", "membership_population": "A", "membership": "member", "subclass_edge": "B_sub_A"}, {"kind": "membership", "entity": "e0", "population": "B"}),
        case("META-quant-L", "quantifier", {"population": "C", "members": ["e0", "e1"], "predicate": "P", "quantifier": "every", "polarity": "positive"}, {"kind": "quantified", "population": "C", "predicate": "P", "quantifier": "every", "polarity": "positive"}),
        case("META-quant-R", "quantifier", {"population": "C", "members": ["e0", "e1"], "predicate": "P", "quantifier": "some", "polarity": "positive"}, {"kind": "quantified", "population": "C", "predicate": "P", "quantifier": "every", "polarity": "positive"}),
        case("META-role-L", "role_binding", {"event": {"predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"}}, {"kind": "event", "predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"}),
        case("META-role-R", "role_binding", {"event": {"predicate": "reviews", "roles": {"subject": "e1", "object": "e0"}, "polarity": "positive"}}, {"kind": "event", "predicate": "reviews", "roles": {"subject": "e0", "object": "e1"}, "polarity": "positive"}),
        case("META-scope-L", "group_scope", {"group": "G", "members": ["e0", "e1"], "event_scope": "group", "predicate": "P", "polarity": "positive"}, {"kind": "event", "group": "G", "event_scope": "group", "predicate": "P", "polarity": "positive"}),
        case("META-scope-R", "group_scope", {"group": "G", "members": ["e0", "e1"], "event_scope": "member:e0", "predicate": "P", "polarity": "positive"}, {"kind": "event", "group": "G", "event_scope": "group", "predicate": "P", "polarity": "positive"}),
        case("META-time-L", "temporal_membership", {"entity": "e0", "population": "C", "membership_window": "before_only", "boundary": "cutoff", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P", "time": "before"}),
        case("META-time-R", "temporal_membership", {"entity": "e0", "population": "C", "membership_window": "before_only", "boundary": "cutoff", "rule": {"population": "C", "predicate": "P", "modality": "obligation", "polarity": "positive"}}, {"kind": "membership", "entity": "e0", "population": "C", "predicate": "P", "time": "after"}),
    ]


def build() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "cases": build_cases() + build_metamorphic_cases(),
            "ablation_witnesses": build_ablation_witnesses(), "metamorphic_pairs": build_metamorphic_pairs()}


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256() -> str:
    return hashlib.sha256(canonical_bytes(build())).hexdigest()


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
    print(sha256())
