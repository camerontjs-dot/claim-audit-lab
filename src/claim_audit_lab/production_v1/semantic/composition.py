"""Bounded CAL V1 composition registry and quantitative-change module RC0."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from types import MappingProxyType
from typing import Any, TypeAlias

from .models import CategoricalRelation, canonical_json_bytes


class CompositionConfigurationError(ValueError):
    """Raised when composition-registry wiring violates a frozen invariant."""


class CompositionRefusal(ValueError):
    """Raised before module semantics when authority or dispatch is invalid."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True, slots=True)
class CompositionAuthority:
    """Normalized, authority-only input boundary for composition."""

    authority_id: str
    semantic_family: str
    audit_context_sha256: str
    evidence_world_sha256: str
    fields: tuple[tuple[str, str], ...]
    status: str = "WARRANTED"

    @classmethod
    def create(
        cls,
        *,
        authority_id: str,
        semantic_family: str,
        audit_context_sha256: str,
        evidence_world_sha256: str,
        fields: Mapping[str, str],
        status: str = "WARRANTED",
    ) -> CompositionAuthority:
        return cls(
            authority_id=authority_id,
            semantic_family=semantic_family,
            audit_context_sha256=audit_context_sha256,
            evidence_world_sha256=evidence_world_sha256,
            fields=tuple(sorted((str(key), str(value)) for key, value in fields.items())),
            status=status,
        )

    def field_map(self) -> dict[str, str]:
        return dict(self.fields)


@dataclass(frozen=True, slots=True)
class CompositionReceipt:
    receipt_id: str
    module_id: str
    relation: CategoricalRelation
    input_authority_ids: tuple[str, ...]
    semantic_input_sha256: str
    modifier_state_sha256: str
    query_sha256: str


@dataclass(frozen=True, slots=True)
class CompositionResult:
    relation: CategoricalRelation
    receipt: CompositionReceipt


def _sha(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _receipt_material(
    *,
    module_id: str,
    relation: CategoricalRelation,
    input_authority_ids: tuple[str, ...],
    semantic_input: object,
    modifier_state: object,
    query: object,
) -> dict[str, object]:
    return {
        "module_id": module_id,
        "relation": relation.value,
        "input_authority_ids": list(input_authority_ids),
        "semantic_input_sha256": _sha(semantic_input),
        "modifier_state_sha256": _sha(modifier_state),
        "query_sha256": _sha(query),
    }


def bind_composition_receipt(
    *,
    module_id: str,
    relation: CategoricalRelation,
    input_authority_ids: tuple[str, ...],
    semantic_input: object,
    modifier_state: object,
    query: object,
) -> CompositionReceipt:
    material = _receipt_material(
        module_id=module_id,
        relation=relation,
        input_authority_ids=input_authority_ids,
        semantic_input=semantic_input,
        modifier_state=modifier_state,
        query=query,
    )
    return CompositionReceipt(
        receipt_id=_sha(material),
        module_id=module_id,
        relation=relation,
        input_authority_ids=input_authority_ids,
        semantic_input_sha256=str(material["semantic_input_sha256"]),
        modifier_state_sha256=str(material["modifier_state_sha256"]),
        query_sha256=str(material["query_sha256"]),
    )


def verify_composition_receipt(
    receipt: CompositionReceipt,
    *,
    module_id: str,
    relation: CategoricalRelation,
    input_authority_ids: tuple[str, ...],
    semantic_input: object,
    modifier_state: object,
    query: object,
) -> bool:
    return receipt == bind_composition_receipt(
        module_id=module_id,
        relation=relation,
        input_authority_ids=input_authority_ids,
        semantic_input=semantic_input,
        modifier_state=modifier_state,
        query=query,
    )


CompositionFn: TypeAlias = Callable[[object], CompositionResult]


@dataclass(frozen=True, slots=True)
class CompositionModule:
    module_id: str
    compose_fn: CompositionFn

    def compose(self, request: object) -> CompositionResult:
        return self.compose_fn(request)


class CompositionRegistry:
    """Immutable lookup table for composition modules."""

    def __init__(self, modules: Iterable[CompositionModule] = ()) -> None:
        indexed: dict[str, CompositionModule] = {}
        for module in modules:
            if not module.module_id.strip():
                raise CompositionConfigurationError("composition module_id must be non-empty")
            if module.module_id in indexed:
                raise CompositionConfigurationError(
                    f"duplicate composition module: {module.module_id}"
                )
            indexed[module.module_id] = module
        self._modules: Mapping[str, CompositionModule] = MappingProxyType(indexed)

    def get(self, module_id: str) -> CompositionModule | None:
        return self._modules.get(module_id)

    @property
    def supported_modules(self) -> tuple[str, ...]:
        return tuple(sorted(self._modules))


def compose_registered(
    module_id: str,
    request: object,
    *,
    registry: CompositionRegistry,
) -> CompositionResult:
    module = registry.get(module_id)
    if module is None:
        raise CompositionRefusal("UNSUPPORTED_COMPOSITION_MODULE", module_id)
    return module.compose(request)


class QuantitativeChangeKind(str, Enum):  # noqa: UP042
    INCREASED = "INCREASED"
    DECREASED = "DECREASED"
    UNCHANGED = "UNCHANGED"
    DELTA = "DELTA"


@dataclass(frozen=True, slots=True)
class TemporalBinding:
    authority_id: str
    label: str
    rank: int | None
    established: bool = True


@dataclass(frozen=True, slots=True)
class QuantitativeChangeQuery:
    entity: str
    metric: str
    unit: str
    kind: QuantitativeChangeKind
    amount: str | None = None


@dataclass(frozen=True, slots=True)
class QuantitativeChangeRequest:
    authorities: tuple[CompositionAuthority, ...]
    temporal_bindings: tuple[TemporalBinding, ...]
    query: QuantitativeChangeQuery


_QUANTITATIVE_MODULE_ID = "quantitative_change_exact_v1"
_SCALAR_FAMILY = "scalar_value"


def _require_authority_firewall(
    authorities: tuple[CompositionAuthority, ...],
) -> None:
    if len(authorities) != 2:
        raise CompositionRefusal("INVALID_AUTHORITY_CARDINALITY", "exactly two required")
    ids = tuple(authority.authority_id for authority in authorities)
    if any(not authority_id for authority_id in ids) or len(set(ids)) != 2:
        raise CompositionRefusal("INVALID_AUTHORITY_IDENTITY", "distinct non-empty ids required")
    for authority in authorities:
        if authority.status != "WARRANTED":
            raise CompositionRefusal("AUTHORITY_NOT_WARRANTED", authority.authority_id)
        if authority.semantic_family != _SCALAR_FAMILY:
            raise CompositionRefusal(
                "FOREIGN_AUTHORITY_FAMILY",
                f"{authority.authority_id}:{authority.semantic_family}",
            )
    contexts = {authority.audit_context_sha256 for authority in authorities}
    worlds = {authority.evidence_world_sha256 for authority in authorities}
    if len(contexts) != 1:
        raise CompositionRefusal("AUTHORITY_CONTEXT_MISMATCH", "cross-context composition")
    if len(worlds) != 1:
        raise CompositionRefusal("AUTHORITY_EVIDENCE_WORLD_MISMATCH", "cross-world composition")


def _scalar_payload(authority: CompositionAuthority) -> dict[str, str]:
    fields = authority.field_map()
    required = {"entity", "metric", "unit", "low", "high", "exact"}
    if set(fields) != required:
        raise CompositionRefusal(
            "AUTHORITY_PAYLOAD_INVALID",
            f"{authority.authority_id}: scalar payload shape",
        )
    try:
        Fraction(fields["low"])
        Fraction(fields["high"])
    except (ValueError, ZeroDivisionError) as exc:
        raise CompositionRefusal(
            "AUTHORITY_PAYLOAD_INVALID",
            f"{authority.authority_id}: scalar values",
        ) from exc
    if fields["exact"] not in {"true", "false"}:
        raise CompositionRefusal(
            "AUTHORITY_PAYLOAD_INVALID",
            f"{authority.authority_id}: exact flag",
        )
    return fields


def _binding_map(
    request: QuantitativeChangeRequest,
) -> dict[str, TemporalBinding] | None:
    if len(request.temporal_bindings) != 2:
        return None
    indexed: dict[str, TemporalBinding] = {}
    for binding in request.temporal_bindings:
        if binding.authority_id in indexed:
            return None
        indexed[binding.authority_id] = binding
    if set(indexed) != {authority.authority_id for authority in request.authorities}:
        return None
    return indexed


def _query_material(query: QuantitativeChangeQuery) -> dict[str, object]:
    material: dict[str, object] = {
        "entity": query.entity,
        "kind": query.kind.value,
        "metric": query.metric,
        "unit": query.unit,
    }
    if query.amount is not None:
        material["amount"] = query.amount
    return material


def _fallback_semantic_material(
    authorities: tuple[CompositionAuthority, ...],
) -> dict[str, object]:
    return {
        "authorities": [
            {
                "authority_id": authority.authority_id,
                "fields": authority.field_map(),
            }
            for authority in sorted(authorities, key=lambda value: value.authority_id)
        ]
    }


def _fallback_modifier_material(
    bindings: tuple[TemporalBinding, ...],
) -> dict[str, object]:
    return {
        "temporal_bindings": [
            {
                "authority_id": binding.authority_id,
                "established": binding.established,
                "label": binding.label,
                "rank": binding.rank,
            }
            for binding in sorted(bindings, key=lambda value: value.authority_id)
        ]
    }


def _unresolved_result(
    request: QuantitativeChangeRequest,
    *,
    semantic_input: object | None = None,
    modifier_state: object | None = None,
) -> CompositionResult:
    authority_ids = tuple(sorted(authority.authority_id for authority in request.authorities))
    semantic = semantic_input or _fallback_semantic_material(request.authorities)
    modifiers = modifier_state or _fallback_modifier_material(request.temporal_bindings)
    query = _query_material(request.query)
    relation = CategoricalRelation.UNRESOLVED
    receipt = bind_composition_receipt(
        module_id=_QUANTITATIVE_MODULE_ID,
        relation=relation,
        input_authority_ids=authority_ids,
        semantic_input=semantic,
        modifier_state=modifiers,
        query=query,
    )
    return CompositionResult(relation, receipt)


def compose_quantitative_change(request: object) -> CompositionResult:
    if not isinstance(request, QuantitativeChangeRequest):
        raise CompositionRefusal("INVALID_COMPOSITION_REQUEST", type(request).__name__)

    _require_authority_firewall(request.authorities)
    payloads = {
        authority.authority_id: _scalar_payload(authority)
        for authority in request.authorities
    }
    bindings = _binding_map(request)
    if bindings is None:
        return _unresolved_result(request)

    if any(
        not binding.established or binding.rank is None
        for binding in bindings.values()
    ):
        return _unresolved_result(request)
    ranks = [binding.rank for binding in bindings.values()]
    labels = [binding.label for binding in bindings.values()]
    if len(set(ranks)) != 2 or any(not label for label in labels) or len(set(labels)) != 2:
        return _unresolved_result(request)

    ordered = tuple(
        sorted(
            request.authorities,
            key=lambda authority: int(bindings[authority.authority_id].rank or 0),
        )
    )
    earlier, later = ordered
    earlier_fields = payloads[earlier.authority_id]
    later_fields = payloads[later.authority_id]

    identity = (
        earlier_fields["entity"],
        earlier_fields["metric"],
        earlier_fields["unit"],
    )
    later_identity = (
        later_fields["entity"],
        later_fields["metric"],
        later_fields["unit"],
    )
    query_identity = (
        request.query.entity,
        request.query.metric,
        request.query.unit,
    )

    semantic_input = {
        "entity": earlier_fields["entity"],
        "metric": earlier_fields["metric"],
        "new": later_fields["low"],
        "old": earlier_fields["low"],
        "unit": earlier_fields["unit"],
    }
    modifier_state = {
        "temporal_bindings": [
            {
                "authority_id": authority.authority_id,
                "label": bindings[authority.authority_id].label,
                "rank": bindings[authority.authority_id].rank,
            }
            for authority in ordered
        ]
    }
    query_material = _query_material(request.query)
    authority_ids = tuple(authority.authority_id for authority in ordered)

    if identity != later_identity or identity != query_identity:
        return _unresolved_result(
            request,
            semantic_input=semantic_input,
            modifier_state=modifier_state,
        )

    usable_points = (
        earlier_fields["exact"] == "true"
        and later_fields["exact"] == "true"
        and earlier_fields["low"] == earlier_fields["high"]
        and later_fields["low"] == later_fields["high"]
    )
    if not usable_points:
        return _unresolved_result(
            request,
            semantic_input=semantic_input,
            modifier_state=modifier_state,
        )

    old_value = Fraction(earlier_fields["low"])
    new_value = Fraction(later_fields["low"])
    delta = new_value - old_value

    if request.query.kind is QuantitativeChangeKind.INCREASED:
        truth = delta > 0
    elif request.query.kind is QuantitativeChangeKind.DECREASED:
        truth = delta < 0
    elif request.query.kind is QuantitativeChangeKind.UNCHANGED:
        truth = delta == 0
    elif request.query.kind is QuantitativeChangeKind.DELTA:
        if request.query.amount is None:
            return _unresolved_result(
                request,
                semantic_input=semantic_input,
                modifier_state=modifier_state,
            )
        try:
            amount = Fraction(request.query.amount)
        except (ValueError, ZeroDivisionError):
            return _unresolved_result(
                request,
                semantic_input=semantic_input,
                modifier_state=modifier_state,
            )
        truth = delta == amount
    else:
        return _unresolved_result(
            request,
            semantic_input=semantic_input,
            modifier_state=modifier_state,
        )

    relation = (
        CategoricalRelation.SUPPORTS if truth else CategoricalRelation.REFUTES
    )
    receipt = bind_composition_receipt(
        module_id=_QUANTITATIVE_MODULE_ID,
        relation=relation,
        input_authority_ids=authority_ids,
        semantic_input=semantic_input,
        modifier_state=modifier_state,
        query=query_material,
    )
    return CompositionResult(relation, receipt)


QUANTITATIVE_CHANGE_EXACT_MODULE = CompositionModule(
    module_id=_QUANTITATIVE_MODULE_ID,
    compose_fn=compose_quantitative_change,
)

DEFAULT_COMPOSITION_REGISTRY = CompositionRegistry(
    (QUANTITATIVE_CHANGE_EXACT_MODULE,)
)


__all__ = [
    "CompositionAuthority",
    "CompositionConfigurationError",
    "CompositionModule",
    "CompositionReceipt",
    "CompositionRefusal",
    "CompositionRegistry",
    "CompositionResult",
    "DEFAULT_COMPOSITION_REGISTRY",
    "QUANTITATIVE_CHANGE_EXACT_MODULE",
    "QuantitativeChangeKind",
    "QuantitativeChangeQuery",
    "QuantitativeChangeRequest",
    "TemporalBinding",
    "bind_composition_receipt",
    "compose_quantitative_change",
    "compose_registered",
    "verify_composition_receipt",
]
