"""Strict CAL V1 production packet intake."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from claim_audit_lab.production_v1 import CONTRACT_B_VERSION
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_TAGGED_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


class PacketValidationError(ValueError):
    """Raised when a packet is not valid CAL V1 intake."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PacketValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PacketValidationError(f"{label} must be an object")
    return cast(dict[str, Any], value)


def _keys(
    value: Mapping[str, Any],
    *,
    label: str,
    required: frozenset[str],
    optional: frozenset[str] = frozenset(),
) -> None:
    actual = set(value)
    allowed = required | optional
    unexpected = sorted(actual - allowed)
    missing = sorted(required - actual)
    if unexpected:
        raise PacketValidationError(f"{label} has unknown field(s): {', '.join(unexpected)}")
    if missing:
        raise PacketValidationError(f"{label} is missing field(s): {', '.join(missing)}")


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PacketValidationError(f"{label} must be a non-empty string")
    return value


def _hex_hash(value: Any, label: str) -> str:
    text = _string(value, label)
    if _HEX64.fullmatch(text) is None:
        raise PacketValidationError(f"{label} must be 64 lowercase hexadecimal characters")
    return text


def _tagged_hash(value: Any, label: str) -> str:
    text = _string(value, label)
    if _TAGGED_SHA256.fullmatch(text) is None:
        raise PacketValidationError(f"{label} must be sha256:<64 lowercase hexadecimal characters>")
    return text


def _optional_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _string(value, label)


def validate_packet(packet: Mapping[str, Any]) -> None:
    """Validate packet shape and evidence integrity without running CAL semantics."""
    _keys(
        packet,
        label="packet",
        required=frozenset({"original_claim", "proposition", "evidence_world"}),
    )
    _string(packet.get("original_claim"), "original_claim")

    proposition = _object(packet.get("proposition"), "proposition")
    _keys(
        proposition,
        label="proposition",
        required=frozenset({"proposition_id", "text_sha256", "semantic_family", "fields"}),
    )
    _string(proposition.get("proposition_id"), "proposition.proposition_id")
    _hex_hash(proposition.get("text_sha256"), "proposition.text_sha256")
    family_value = _string(proposition.get("semantic_family"), "proposition.semantic_family")
    try:
        SemanticFamily(family_value)
    except ValueError as exc:
        raise PacketValidationError(
            f"proposition.semantic_family is not supported: {family_value}"
        ) from exc
    fields = _object(proposition.get("fields"), "proposition.fields")
    for key, value in fields.items():
        if not isinstance(key, str) or not key.strip():
            raise PacketValidationError("proposition.fields keys must be non-empty strings")
        _string(value, f"proposition.fields.{key}")

    world = _object(packet.get("evidence_world"), "evidence_world")
    _keys(
        world,
        label="evidence_world",
        required=frozenset(
            {
                "contract_b_version",
                "bundle_id",
                "bundle_hash",
                "aperture_observation",
                "admitted_passages",
            }
        ),
        optional=frozenset({"root_id", "child_id"}),
    )
    contract_b_version = _string(
        world.get("contract_b_version"), "evidence_world.contract_b_version"
    )
    if contract_b_version != CONTRACT_B_VERSION:
        raise PacketValidationError(
            "evidence_world.contract_b_version must equal "
            f"the released CAL input authority {CONTRACT_B_VERSION}"
        )
    _string(world.get("bundle_id"), "evidence_world.bundle_id")
    _tagged_hash(world.get("bundle_hash"), "evidence_world.bundle_hash")
    if not isinstance(world.get("aperture_observation"), dict):
        raise PacketValidationError("evidence_world.aperture_observation must be an object")
    _optional_string(world.get("root_id"), "evidence_world.root_id")
    _optional_string(world.get("child_id"), "evidence_world.child_id")

    passages = world.get("admitted_passages")
    if not isinstance(passages, list):
        raise PacketValidationError("evidence_world.admitted_passages must be an array")
    seen_ids: set[str] = set()
    for index, value in enumerate(passages):
        passage = _object(value, f"evidence_world.admitted_passages[{index}]")
        _keys(
            passage,
            label=f"evidence_world.admitted_passages[{index}]",
            required=frozenset({"passage_id", "source_id", "text", "text_sha256", "source_sha256"}),
        )
        passage_id = _string(
            passage.get("passage_id"),
            f"evidence_world.admitted_passages[{index}].passage_id",
        )
        if passage_id in seen_ids:
            raise PacketValidationError(f"duplicate passage_id: {passage_id}")
        seen_ids.add(passage_id)
        _string(
            passage.get("source_id"),
            f"evidence_world.admitted_passages[{index}].source_id",
        )
        _string(passage.get("text"), f"evidence_world.admitted_passages[{index}].text")
        _tagged_hash(
            passage.get("text_sha256"),
            f"evidence_world.admitted_passages[{index}].text_sha256",
        )
        _tagged_hash(
            passage.get("source_sha256"),
            f"evidence_world.admitted_passages[{index}].source_sha256",
        )


def load_packet(path: Path) -> tuple[dict[str, Any], bytes]:
    """Read, parse and validate one packet, preserving its original bytes."""
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        raise PacketValidationError(f"cannot read packet {path}: {exc}") from exc
    try:
        decoded = raw_bytes.decode("utf-8")
        raw: Any = json.loads(decoded, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, PacketValidationError) as exc:
        raise PacketValidationError(f"invalid packet JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise PacketValidationError("packet root must be an object")
    packet = cast(dict[str, Any], raw)
    validate_packet(packet)
    context_from_packet(packet)
    return packet, raw_bytes


def packet_sha256(raw_bytes: bytes) -> str:
    """Return the tagged SHA-256 identity of the exact packet bytes."""
    return f"sha256:{hashlib.sha256(raw_bytes).hexdigest()}"


def context_from_packet(packet: Mapping[str, Any]) -> AuditContext:
    """Convert an already validated packet into the qualified semantic context."""
    validate_packet(packet)
    proposition_raw = _object(packet["proposition"], "proposition")
    family = SemanticFamily(proposition_raw["semantic_family"])
    fields_raw = _object(proposition_raw["fields"], "proposition.fields")
    fields = {key: cast(str, value) for key, value in fields_raw.items()}
    proposition = TypedProposition.create(
        cast(str, proposition_raw["proposition_id"]),
        family,
        fields,
        text_sha256=cast(str, proposition_raw["text_sha256"]),
    )

    world_raw = _object(packet["evidence_world"], "evidence_world")
    passages_raw = cast(list[Any], world_raw["admitted_passages"])
    passages = tuple(
        AdmittedPassage(
            passage_id=cast(str, _object(row, "passage")["passage_id"]),
            source_id=cast(str, _object(row, "passage")["source_id"]),
            text=cast(str, _object(row, "passage")["text"]),
            text_sha256=cast(str, _object(row, "passage")["text_sha256"]),
            source_sha256=cast(str, _object(row, "passage")["source_sha256"]),
        )
        for row in passages_raw
    )
    world = EvidenceWorld.create(
        contract_b_version=cast(str, world_raw["contract_b_version"]),
        bundle_id=cast(str, world_raw["bundle_id"]),
        bundle_hash=cast(str, world_raw["bundle_hash"]),
        admitted_passages=passages,
        aperture_observation=cast(Mapping[str, Any], world_raw["aperture_observation"]),
        root_id=_optional_string(world_raw.get("root_id"), "evidence_world.root_id"),
        child_id=_optional_string(world_raw.get("child_id"), "evidence_world.child_id"),
    )
    context = AuditContext(
        original_claim=cast(str, packet["original_claim"]),
        proposition=proposition,
        evidence_world=world,
    )
    try:
        context.verify()
    except ValueError as exc:
        raise PacketValidationError(str(exc)) from exc
    return context


__all__ = [
    "PacketValidationError",
    "context_from_packet",
    "load_packet",
    "packet_sha256",
    "validate_packet",
]
