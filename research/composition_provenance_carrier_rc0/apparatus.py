"""Frozen apparatus for composition provenance carrier RC0."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Protocol


class Relation(StrEnum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, slots=True)
class CompositionRequest:
    module_id: str
    relation: Relation
    input_authority_ids: tuple[str, ...]
    semantic_input: dict[str, object]
    modifier_state: dict[str, object]
    query: dict[str, object]


@dataclass(frozen=True, slots=True)
class CompositionReceipt:
    receipt_id: str
    module_id: str
    relation: Relation
    input_authority_ids: tuple[str, ...]
    semantic_input_sha256: str
    modifier_state_sha256: str
    query_sha256: str


class Strategy(Protocol):
    def __call__(self, request: CompositionRequest) -> CompositionReceipt: ...


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def expected_material(request: CompositionRequest) -> dict[str, object]:
    return {
        "module_id": request.module_id,
        "relation": request.relation.value,
        "input_authority_ids": list(request.input_authority_ids),
        "semantic_input_sha256": _sha(request.semantic_input),
        "modifier_state_sha256": _sha(request.modifier_state),
        "query_sha256": _sha(request.query),
    }


def expected_receipt_id(request: CompositionRequest) -> str:
    return _sha(expected_material(request))


def verify_receipt(
    receipt: CompositionReceipt,
    request: CompositionRequest,
) -> bool:
    expected = expected_material(request)
    if receipt.receipt_id != expected_receipt_id(request):
        return False
    if receipt.module_id != expected["module_id"]:
        return False
    if receipt.relation.value != expected["relation"]:
        return False
    if list(receipt.input_authority_ids) != expected["input_authority_ids"]:
        return False
    if receipt.semantic_input_sha256 != expected["semantic_input_sha256"]:
        return False
    if receipt.modifier_state_sha256 != expected["modifier_state_sha256"]:
        return False
    if receipt.query_sha256 != expected["query_sha256"]:
        return False
    return True


def weak_relation_only(request: CompositionRequest) -> CompositionReceipt:
    return CompositionReceipt(
        "",
        "",
        request.relation,
        (),
        "",
        "",
        "",
    )


def weak_drop_inputs(request: CompositionRequest) -> CompositionReceipt:
    material = expected_material(request)
    return CompositionReceipt(
        _sha({**material, "input_authority_ids": []}),
        request.module_id,
        request.relation,
        (),
        str(material["semantic_input_sha256"]),
        str(material["modifier_state_sha256"]),
        str(material["query_sha256"]),
    )


def weak_drop_modifiers(request: CompositionRequest) -> CompositionReceipt:
    material = expected_material(request)
    empty_modifier = _sha({})
    return CompositionReceipt(
        _sha({**material, "modifier_state_sha256": empty_modifier}),
        request.module_id,
        request.relation,
        request.input_authority_ids,
        str(material["semantic_input_sha256"]),
        empty_modifier,
        str(material["query_sha256"]),
    )


def weak_drop_query(request: CompositionRequest) -> CompositionReceipt:
    material = expected_material(request)
    empty_query = _sha({})
    return CompositionReceipt(
        _sha({**material, "query_sha256": empty_query}),
        request.module_id,
        request.relation,
        request.input_authority_ids,
        str(material["semantic_input_sha256"]),
        str(material["modifier_state_sha256"]),
        empty_query,
    )


def weak_module_agnostic(request: CompositionRequest) -> CompositionReceipt:
    material = expected_material(request)
    return CompositionReceipt(
        _sha({**material, "module_id": ""}),
        "",
        request.relation,
        request.input_authority_ids,
        str(material["semantic_input_sha256"]),
        str(material["modifier_state_sha256"]),
        str(material["query_sha256"]),
    )


CASES: tuple[CompositionRequest, ...] = (
    CompositionRequest(
        "quantitative_change_exact_v1",
        Relation.SUPPORTS,
        ("scalar-auth-t1", "scalar-auth-t2"),
        {
            "entity": "batch",
            "metric": "yield",
            "unit": "%",
            "old": "92",
            "new": "95",
        },
        {
            "temporal_bindings": [
                {"authority_id": "scalar-auth-t1", "rank": 1, "label": "T1"},
                {"authority_id": "scalar-auth-t2", "rank": 2, "label": "T2"},
            ]
        },
        {"kind": "INCREASED", "entity": "batch", "metric": "yield", "unit": "%"},
    ),
    CompositionRequest(
        "typed_relation_chain_v1",
        Relation.SUPPORTS,
        ("relation-auth-1", "relation-auth-2"),
        {
            "left": {"subject": "a", "predicate": "NORTH_OF", "object": "b"},
            "right": {"subject": "b", "predicate": "NORTH_OF", "object": "c"},
        },
        {"frame_id": "frame-7", "frame_established": True},
        {"subject": "a", "predicate": "NORTH_OF", "object": "c"},
    ),
    CompositionRequest(
        "occurrence_order_binding_v1",
        Relation.SUPPORTS,
        ("occ-auth-1", "occ-auth-2", "order-auth-1"),
        {
            "first_event": "qa|approve|batch|positive",
            "second_event": "ops|release|batch|positive",
            "order": "BEFORE",
        },
        {
            "first_binding_id": "event-17",
            "second_binding_id": "event-18",
            "order_left_binding_id": "event-17",
            "order_right_binding_id": "event-18",
        },
        {"left_binding_id": "event-17", "relation": "BEFORE", "right_binding_id": "event-18"},
    ),
    CompositionRequest(
        "population_deontic_applicability_v1",
        Relation.SUPPORTS,
        ("norm-auth-1", "membership-auth-1"),
        {
            "norm_subject": "qualified_technicians",
            "member_entity": "alice",
            "member_population": "qualified_technicians",
            "mode": "PERMITTED",
            "action": "release_batch",
        },
        {"subject_kind": "POPULATION", "membership_status": "MEMBER"},
        {"entity": "alice", "mode": "PERMITTED", "action": "release_batch"},
    ),
    CompositionRequest(
        "attribute_temporal_applicability_v1",
        Relation.REFUTES,
        ("state-auth-1",),
        {
            "entity": "batch",
            "attribute": "status",
            "domain": "batch_status",
            "value": "released",
            "functional": True,
        },
        {"scope_start": 10, "scope_end": 20, "target": 15},
        {"entity": "batch", "attribute": "status", "domain": "batch_status", "value": "held"},
    ),
    CompositionRequest(
        "attribute_temporal_applicability_v1",
        Relation.UNRESOLVED,
        ("state-auth-2",),
        {
            "entity": "record",
            "attribute": "tag",
            "domain": "labels",
            "value": "critical",
            "functional": False,
        },
        {"scope_start": 5, "scope_end": 15, "target": 10},
        {"entity": "record", "attribute": "tag", "domain": "labels", "value": "urgent"},
    ),
)


WEAKS: tuple[tuple[str, Strategy], ...] = (
    ("relation_only", weak_relation_only),
    ("drop_inputs", weak_drop_inputs),
    ("drop_modifiers", weak_drop_modifiers),
    ("drop_query", weak_drop_query),
    ("module_agnostic", weak_module_agnostic),
)


def failures(strategy: Strategy) -> tuple[int, ...]:
    bad: list[int] = []
    for index, request in enumerate(CASES):
        if not verify_receipt(strategy(request), request):
            bad.append(index)
    return tuple(bad)


def mutation_failures(strategy: Strategy) -> tuple[str, ...]:
    failures_found: list[str] = []
    for index, request in enumerate(CASES):
        receipt = strategy(request)
        if not verify_receipt(receipt, request):
            failures_found.append(f"{index}:baseline")
            continue

        mutations = (
            ("module", replace(receipt, module_id=receipt.module_id + "-mutated")),
            ("relation", replace(
                receipt,
                relation=(
                    Relation.REFUTES
                    if receipt.relation is Relation.SUPPORTS
                    else Relation.SUPPORTS
                ),
            )),
            ("inputs", replace(receipt, input_authority_ids=receipt.input_authority_ids + ("extra",))),
            ("semantic", replace(receipt, semantic_input_sha256="0" * 64)),
            ("modifier", replace(receipt, modifier_state_sha256="1" * 64)),
            ("query", replace(receipt, query_sha256="2" * 64)),
            ("receipt", replace(receipt, receipt_id="3" * 64)),
        )
        for name, mutated in mutations:
            if verify_receipt(mutated, request):
                failures_found.append(f"{index}:{name}")
    return tuple(failures_found)
