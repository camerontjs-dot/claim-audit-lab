from __future__ import annotations

import hashlib
from collections.abc import Callable

import pytest

from claim_audit_lab.production_v1.semantic.authority import complete_and_warrant
from claim_audit_lab.production_v1.semantic.engine import audit
from claim_audit_lab.production_v1.semantic.measurements import (
    MeasurementReceipt,
    measure_direct_event_order,
    measure_strict_comparison,
)
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    Conclusion,
    EvidenceWorld,
    FailureCode,
    SemanticFamily,
    TypedProposition,
)
from claim_audit_lab.production_v1.semantic.plugins import (
    DEFAULT_FAMILY_REGISTRY,
    DIRECT_EVENT_ORDER_PLUGIN,
    STRICT_COMPARISON_PLUGIN,
    PluginConfigurationError,
    SemanticFamilyPlugin,
    SemanticFamilyRegistry,
)
from claim_audit_lab.production_v1.semantic.relations import derive_relation


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _context(
    family: SemanticFamily,
    fields: dict[str, str],
    text: str,
) -> AuditContext:
    passage = AdmittedPassage.create("p1", "source-1", text)
    world = EvidenceWorld.create(
        "1.2.0",
        "bundle-1",
        _tagged("bundle-1"),
        (passage,),
        {
            "search_scope": {"corpus": "plugin-rc0"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        "claim-1",
        family,
        fields,
        text_sha256=_hex("typed claim"),
    )
    return AuditContext("typed claim", proposition, world)


def _strict_context() -> AuditContext:
    return _context(
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        "Women had a higher rate than Men.",
    )


def _event_context() -> AuditContext:
    return _context(
        SemanticFamily.DIRECT_EVENT_ORDER,
        {
            "left_subject": "alice",
            "left_predicate": "review",
            "left_object": "dossier",
            "left_polarity": "positive",
            "temporal_relation": "BEFORE",
            "right_subject": "bob",
            "right_predicate": "archive",
            "right_object": "dossier",
            "right_polarity": "positive",
        },
        "Alice reviewed dossier before Bob archived dossier.",
    )


def test_default_registry_contains_exact_frozen_deciding_families() -> None:
    assert DEFAULT_FAMILY_REGISTRY.supported_families == (
        SemanticFamily.DIRECT_EVENT_ORDER,
        SemanticFamily.STRICT_COMPARISON,
    )
    assert DEFAULT_FAMILY_REGISTRY.get(SemanticFamily.STRICT_COMPARISON) is (
        STRICT_COMPARISON_PLUGIN
    )
    assert DEFAULT_FAMILY_REGISTRY.get(SemanticFamily.DIRECT_EVENT_ORDER) is (
        DIRECT_EVENT_ORDER_PLUGIN
    )
    assert DEFAULT_FAMILY_REGISTRY.get(SemanticFamily.PERMISSION_EXCEPTION) is None
    assert DEFAULT_FAMILY_REGISTRY.get(SemanticFamily.ASSERTION_SCOPE) is None


@pytest.mark.parametrize(
    ("context", "measure"),
    [
        (_strict_context(), measure_strict_comparison),
        (_event_context(), measure_direct_event_order),
    ],
)
def test_plugin_path_matches_existing_direct_semantic_stages(
    context: AuditContext,
    measure: Callable[[AuditContext, str], MeasurementReceipt],
) -> None:
    plugin = DEFAULT_FAMILY_REGISTRY.get(context.proposition.semantic_family)
    assert plugin is not None
    receipt = plugin.measure(context, "p1")
    expected_receipt = measure(context, "p1")
    assert receipt == expected_receipt
    authority = plugin.warrant(context, receipt, "p1")
    assert authority == complete_and_warrant(context, expected_receipt, "p1")
    relation = plugin.relate(context, authority)
    assert relation == derive_relation(context, authority)
    assert audit(context).conclusion is Conclusion.SUPPORTED


def test_missing_plugin_does_not_borrow_another_family() -> None:
    result = audit(_strict_context(), registry=SemanticFamilyRegistry())
    assert result.conclusion is Conclusion.NOT_CHECKABLE
    assert result.failure_code is FailureCode.UNSUPPORTED_SEMANTIC_FAMILY
    assert result.traces[0].measurement is None
    assert result.traces[0].authority is None
    assert result.traces[0].relation is None


def test_miswired_plugin_rejects_foreign_family_measurement() -> None:
    miswired = SemanticFamilyPlugin(
        semantic_family=SemanticFamily.STRICT_COMPARISON,
        measurement_fn=measure_direct_event_order,
        authority_fn=complete_and_warrant,
        relation_fn=derive_relation,
    )
    registry = SemanticFamilyRegistry((miswired,))
    with pytest.raises(
        PluginConfigurationError,
        match="plugin measurement semantic-family mismatch",
    ):
        audit(_strict_context(), registry=registry)


def test_registry_rejects_duplicate_family_plugins() -> None:
    with pytest.raises(
        PluginConfigurationError,
        match="duplicate semantic-family plugin: strict_comparison",
    ):
        SemanticFamilyRegistry((STRICT_COMPARISON_PLUGIN, STRICT_COMPARISON_PLUGIN))
