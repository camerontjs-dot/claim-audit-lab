from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeAlias

from .authority import AuthorityReceipt, complete_and_warrant
from .measurements import (
    MeasurementReceipt,
    measure_direct_event_order,
    measure_strict_comparison,
)
from .models import AuditContext, SemanticFamily
from .relations import BoundRelation, derive_relation

MeasurementFn: TypeAlias = Callable[[AuditContext, str], MeasurementReceipt]
AuthorityFn: TypeAlias = Callable[[AuditContext, MeasurementReceipt, str], AuthorityReceipt]
RelationFn: TypeAlias = Callable[[AuditContext, AuthorityReceipt], BoundRelation]


class PluginConfigurationError(ValueError):
    """Raised when semantic-family plugin wiring violates a kernel invariant."""


@dataclass(frozen=True, slots=True)
class SemanticFamilyPlugin:
    semantic_family: SemanticFamily
    measurement_fn: MeasurementFn
    authority_fn: AuthorityFn
    relation_fn: RelationFn

    def _verify_context(self, context: AuditContext) -> None:
        if context.proposition.semantic_family is not self.semantic_family:
            raise PluginConfigurationError(
                "plugin/context semantic-family mismatch: "
                f"plugin={self.semantic_family.value} "
                f"context={context.proposition.semantic_family.value}"
            )

    def measure(self, context: AuditContext, passage_id: str) -> MeasurementReceipt:
        self._verify_context(context)
        receipt = self.measurement_fn(context, passage_id)
        if receipt.semantic_family is not self.semantic_family:
            raise PluginConfigurationError(
                "plugin measurement semantic-family mismatch: "
                f"plugin={self.semantic_family.value} "
                f"measurement={receipt.semantic_family.value}"
            )
        return receipt

    def warrant(
        self,
        context: AuditContext,
        receipt: MeasurementReceipt,
        passage_id: str,
    ) -> AuthorityReceipt:
        self._verify_context(context)
        if receipt.semantic_family is not self.semantic_family:
            raise PluginConfigurationError(
                "plugin received foreign-family measurement: "
                f"plugin={self.semantic_family.value} "
                f"measurement={receipt.semantic_family.value}"
            )
        authority = self.authority_fn(context, receipt, passage_id)
        if authority.atom.semantic_family is not self.semantic_family:
            raise PluginConfigurationError(
                "plugin authority semantic-family mismatch: "
                f"plugin={self.semantic_family.value} "
                f"authority={authority.atom.semantic_family.value}"
            )
        return authority

    def relate(self, context: AuditContext, authority: AuthorityReceipt) -> BoundRelation:
        self._verify_context(context)
        if authority.atom.semantic_family is not self.semantic_family:
            raise PluginConfigurationError(
                "plugin received foreign-family authority: "
                f"plugin={self.semantic_family.value} "
                f"authority={authority.atom.semantic_family.value}"
            )
        return self.relation_fn(context, authority)


class SemanticFamilyRegistry:
    """Immutable lookup table for semantic-family execution plugins."""

    def __init__(self, plugins: Iterable[SemanticFamilyPlugin] = ()) -> None:
        indexed: dict[SemanticFamily, SemanticFamilyPlugin] = {}
        for plugin in plugins:
            if plugin.semantic_family in indexed:
                raise PluginConfigurationError(
                    f"duplicate semantic-family plugin: {plugin.semantic_family.value}"
                )
            indexed[plugin.semantic_family] = plugin
        self._plugins: Mapping[SemanticFamily, SemanticFamilyPlugin] = MappingProxyType(indexed)

    def get(self, family: SemanticFamily) -> SemanticFamilyPlugin | None:
        return self._plugins.get(family)

    @property
    def supported_families(self) -> tuple[SemanticFamily, ...]:
        return tuple(sorted(self._plugins, key=lambda family: family.value))


STRICT_COMPARISON_PLUGIN = SemanticFamilyPlugin(
    semantic_family=SemanticFamily.STRICT_COMPARISON,
    measurement_fn=measure_strict_comparison,
    authority_fn=complete_and_warrant,
    relation_fn=derive_relation,
)

DIRECT_EVENT_ORDER_PLUGIN = SemanticFamilyPlugin(
    semantic_family=SemanticFamily.DIRECT_EVENT_ORDER,
    measurement_fn=measure_direct_event_order,
    authority_fn=complete_and_warrant,
    relation_fn=derive_relation,
)

DEFAULT_FAMILY_REGISTRY = SemanticFamilyRegistry(
    (
        STRICT_COMPARISON_PLUGIN,
        DIRECT_EVENT_ORDER_PLUGIN,
    )
)
