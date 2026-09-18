from __future__ import annotations

from dataclasses import replace

import pytest

from claim_audit_lab.production_v1.semantic.composition import (
    DEFAULT_COMPOSITION_REGISTRY,
    QUANTITATIVE_CHANGE_EXACT_MODULE,
    CompositionAuthority,
    CompositionConfigurationError,
    CompositionRegistry,
    CompositionRefusal,
    QuantitativeChangeKind,
    QuantitativeChangeQuery,
    QuantitativeChangeRequest,
    TemporalBinding,
    compose_registered,
    verify_composition_receipt,
)
from claim_audit_lab.production_v1.semantic.models import CategoricalRelation

CTX = "a" * 64
WORLD = "b" * 64


def _authority(
    authority_id: str,
    value: str,
    *,
    entity: str = "batch",
    metric: str = "yield",
    unit: str = "%",
    low: str | None = None,
    high: str | None = None,
    exact: str = "true",
    semantic_family: str = "scalar_value",
    status: str = "WARRANTED",
    context: str = CTX,
    world: str = WORLD,
) -> CompositionAuthority:
    return CompositionAuthority.create(
        authority_id=authority_id,
        semantic_family=semantic_family,
        audit_context_sha256=context,
        evidence_world_sha256=world,
        status=status,
        fields={
            "entity": entity,
            "metric": metric,
            "unit": unit,
            "low": low or value,
            "high": high or value,
            "exact": exact,
        },
    )


def _request(
    left: CompositionAuthority | None = None,
    right: CompositionAuthority | None = None,
    *,
    left_rank: int | None = 1,
    right_rank: int | None = 2,
    left_label: str = "T1",
    right_label: str = "T2",
    left_established: bool = True,
    right_established: bool = True,
    kind: QuantitativeChangeKind = QuantitativeChangeKind.INCREASED,
    amount: str | None = None,
    query_entity: str = "batch",
    query_metric: str = "yield",
    query_unit: str = "%",
) -> QuantitativeChangeRequest:
    left = left or _authority("scalar-auth-t1", "92")
    right = right or _authority("scalar-auth-t2", "95")
    return QuantitativeChangeRequest(
        authorities=(left, right),
        temporal_bindings=(
            TemporalBinding(left.authority_id, left_label, left_rank, left_established),
            TemporalBinding(right.authority_id, right_label, right_rank, right_established),
        ),
        query=QuantitativeChangeQuery(
            query_entity,
            query_metric,
            query_unit,
            kind,
            amount,
        ),
    )


def _compose(request: QuantitativeChangeRequest):
    return compose_registered(
        "quantitative_change_exact_v1",
        request,
        registry=DEFAULT_COMPOSITION_REGISTRY,
    )


def test_default_composition_registry_is_separate_and_bounded() -> None:
    assert DEFAULT_COMPOSITION_REGISTRY.supported_modules == (
        "quantitative_change_exact_v1",
    )
    assert DEFAULT_COMPOSITION_REGISTRY.get("quantitative_change_exact_v1") is (
        QUANTITATIVE_CHANGE_EXACT_MODULE
    )
    assert DEFAULT_COMPOSITION_REGISTRY.get("strict_comparison") is None


def test_registry_rejects_duplicate_module() -> None:
    with pytest.raises(
        CompositionConfigurationError,
        match="duplicate composition module",
    ):
        CompositionRegistry(
            (QUANTITATIVE_CHANGE_EXACT_MODULE, QUANTITATIVE_CHANGE_EXACT_MODULE)
        )


def test_unknown_module_fails_closed() -> None:
    with pytest.raises(CompositionRefusal, match="UNSUPPORTED_COMPOSITION_MODULE"):
        compose_registered(
            "unknown-module",
            _request(),
            registry=DEFAULT_COMPOSITION_REGISTRY,
        )


@pytest.mark.parametrize(
    ("request", "expected"),
    [
        (_request(), CategoricalRelation.SUPPORTS),
        (
            _request(kind=QuantitativeChangeKind.DECREASED),
            CategoricalRelation.REFUTES,
        ),
        (
            _request(
                _authority("scalar-auth-t1", "95"),
                _authority("scalar-auth-t2", "92"),
                kind=QuantitativeChangeKind.DECREASED,
            ),
            CategoricalRelation.SUPPORTS,
        ),
        (
            _request(
                _authority("scalar-auth-t1", "95"),
                _authority("scalar-auth-t2", "95"),
                kind=QuantitativeChangeKind.UNCHANGED,
            ),
            CategoricalRelation.SUPPORTS,
        ),
        (
            _request(kind=QuantitativeChangeKind.DELTA, amount="3"),
            CategoricalRelation.SUPPORTS,
        ),
        (
            _request(kind=QuantitativeChangeKind.DELTA, amount="2"),
            CategoricalRelation.REFUTES,
        ),
    ],
)
def test_exact_quantitative_change_relations(
    request: QuantitativeChangeRequest,
    expected: CategoricalRelation,
) -> None:
    assert _compose(request).relation is expected


def test_call_order_does_not_replace_temporal_authority() -> None:
    forward = _request()
    reversed_request = QuantitativeChangeRequest(
        authorities=tuple(reversed(forward.authorities)),
        temporal_bindings=tuple(reversed(forward.temporal_bindings)),
        query=forward.query,
    )
    assert _compose(forward) == _compose(reversed_request)


def test_temporal_rank_reversal_changes_semantics() -> None:
    request = _request(left_rank=2, right_rank=1)
    assert _compose(request).relation is CategoricalRelation.REFUTES


@pytest.mark.parametrize(
    "request",
    [
        _request(right=_authority("scalar-auth-t2", "95", entity="other")),
        _request(right=_authority("scalar-auth-t2", "95", metric="count")),
        _request(right=_authority("scalar-auth-t2", "95", unit="fraction")),
        _request(query_unit="fraction"),
        _request(right=_authority("scalar-auth-t2", "95", exact="false")),
        _request(right=_authority("scalar-auth-t2", "95", low="94", high="96")),
        _request(left_rank=1, right_rank=1),
        _request(left_label="T1", right_label="T1"),
        _request(left_established=False),
        _request(kind=QuantitativeChangeKind.DELTA, amount=None),
    ],
)
def test_semantic_insufficiency_is_unresolved(
    request: QuantitativeChangeRequest,
) -> None:
    result = _compose(request)
    assert result.relation is CategoricalRelation.UNRESOLVED
    assert result.receipt.relation is CategoricalRelation.UNRESOLVED


@pytest.mark.parametrize(
    "request",
    [
        _request(left=_authority("a1", "92", semantic_family="event_occurrence")),
        _request(left=_authority("a1", "92", status="CLAIMED")),
        _request(
            left=_authority("a1", "92", context="c" * 64),
            right=_authority("a2", "95", context="d" * 64),
        ),
        _request(
            left=_authority("a1", "92", world="c" * 64),
            right=_authority("a2", "95", world="d" * 64),
        ),
    ],
)
def test_authority_firewall_rejects_invalid_inputs(
    request: QuantitativeChangeRequest,
) -> None:
    with pytest.raises(CompositionRefusal):
        _compose(request)


def test_duplicate_authority_identity_is_rejected() -> None:
    left = _authority("same", "92")
    right = _authority("same", "95")
    request = QuantitativeChangeRequest(
        authorities=(left, right),
        temporal_bindings=(
            TemporalBinding("same", "T1", 1),
            TemporalBinding("same", "T2", 2),
        ),
        query=QuantitativeChangeQuery(
            "batch",
            "yield",
            "%",
            QuantitativeChangeKind.INCREASED,
        ),
    )
    with pytest.raises(CompositionRefusal, match="INVALID_AUTHORITY_IDENTITY"):
        _compose(request)


def test_portable_vector_cpv01_is_reproduced_exactly() -> None:
    result = _compose(_request())
    assert result.receipt.input_authority_ids == (
        "scalar-auth-t1",
        "scalar-auth-t2",
    )
    assert result.receipt.semantic_input_sha256 == (
        "91f38b39ae4f668ee50ab0a62ea3285f46634cf4276be4646c4e5d2ccf645e2d"
    )
    assert result.receipt.modifier_state_sha256 == (
        "996ada96c1098112af8d241bfeecee23a909828e4d07299f21d94009b9c5c6ff"
    )
    assert result.receipt.query_sha256 == (
        "164ccaa22d5ad46a0b76f890bff9f4111d17f5c6188b2325fdb00473cb3172ac"
    )
    assert result.receipt.receipt_id == (
        "0eb02674f563771a4b585f9b00a9c2d6816491d15214d796aca62ad70b7f4591"
    )


def test_every_bound_receipt_field_is_verified() -> None:
    request = _request()
    result = _compose(request)
    receipt = result.receipt
    semantic_input = {
        "entity": "batch",
        "metric": "yield",
        "new": "95",
        "old": "92",
        "unit": "%",
    }
    modifier_state = {
        "temporal_bindings": [
            {"authority_id": "scalar-auth-t1", "label": "T1", "rank": 1},
            {"authority_id": "scalar-auth-t2", "label": "T2", "rank": 2},
        ]
    }
    query = {
        "entity": "batch",
        "kind": "INCREASED",
        "metric": "yield",
        "unit": "%",
    }

    assert verify_composition_receipt(
        receipt,
        module_id="quantitative_change_exact_v1",
        relation=CategoricalRelation.SUPPORTS,
        input_authority_ids=("scalar-auth-t1", "scalar-auth-t2"),
        semantic_input=semantic_input,
        modifier_state=modifier_state,
        query=query,
    )

    mutations = (
        replace(receipt, module_id="mutated"),
        replace(receipt, relation=CategoricalRelation.REFUTES),
        replace(receipt, input_authority_ids=("scalar-auth-t1",)),
        replace(receipt, semantic_input_sha256="0" * 64),
        replace(receipt, modifier_state_sha256="1" * 64),
        replace(receipt, query_sha256="2" * 64),
        replace(receipt, receipt_id="3" * 64),
    )
    for mutated in mutations:
        assert not verify_composition_receipt(
            mutated,
            module_id="quantitative_change_exact_v1",
            relation=CategoricalRelation.SUPPORTS,
            input_authority_ids=("scalar-auth-t1", "scalar-auth-t2"),
            semantic_input=semantic_input,
            modifier_state=modifier_state,
            query=query,
        )
