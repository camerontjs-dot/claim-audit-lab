"""Canonical Contract B 1.2 intake for the CAL V1 integration candidate."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from claim_audit_lab.contracts.cb_models import CBClaim, CBPassage
from claim_audit_lab.contracts.factual_context import ContractBIntakeView, load_contract_b_intake
from claim_audit_lab.production_v1 import CONTRACT_B_VERSION
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)


class BundleTargetValidationError(ValueError):
    """Raised when the typed CAL target cannot be bound to canonical Contract B intake."""


@dataclass(frozen=True, slots=True)
class PreparedContractBInput:
    context: AuditContext
    intake: ContractBIntakeView
    target: dict[str, Any]
    target_bytes: bytes
    target_sha256: str
    intake_snapshot: dict[str, Any]


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BundleTargetValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BundleTargetValidationError(f"{label} must be an object")
    return cast(dict[str, Any], value)


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BundleTargetValidationError(f"{label} must be a non-empty string")
    return value


def _validate_target(target: Mapping[str, Any]) -> None:
    if set(target) != {"claim_id", "proposition"}:
        unexpected = sorted(set(target) - {"claim_id", "proposition"})
        missing = sorted({"claim_id", "proposition"} - set(target))
        if unexpected:
            raise BundleTargetValidationError(
                f"target has unknown field(s): {', '.join(unexpected)}"
            )
        raise BundleTargetValidationError(f"target is missing field(s): {', '.join(missing)}")
    _string(target.get("claim_id"), "claim_id")
    proposition = _object(target.get("proposition"), "proposition")
    required = {"proposition_id", "text_sha256", "semantic_family", "fields"}
    if set(proposition) != required:
        unexpected = sorted(set(proposition) - required)
        missing = sorted(required - set(proposition))
        if unexpected:
            raise BundleTargetValidationError(
                f"proposition has unknown field(s): {', '.join(unexpected)}"
            )
        raise BundleTargetValidationError(
            f"proposition is missing field(s): {', '.join(missing)}"
        )
    proposition_id = _string(proposition.get("proposition_id"), "proposition.proposition_id")
    text_sha256 = _string(proposition.get("text_sha256"), "proposition.text_sha256")
    family_value = _string(proposition.get("semantic_family"), "proposition.semantic_family")
    try:
        family = SemanticFamily(family_value)
    except ValueError as exc:
        raise BundleTargetValidationError(
            f"proposition.semantic_family is not supported: {family_value}"
        ) from exc
    fields = _object(proposition.get("fields"), "proposition.fields")
    normalized_fields: dict[str, str] = {}
    for key, value in fields.items():
        if not isinstance(key, str) or not key.strip():
            raise BundleTargetValidationError("proposition.fields keys must be non-empty strings")
        normalized_fields[key] = _string(value, f"proposition.fields.{key}")
    try:
        TypedProposition.create(
            proposition_id,
            family,
            normalized_fields,
            text_sha256=text_sha256,
        )
    except ValueError as exc:
        raise BundleTargetValidationError(str(exc)) from exc


def load_target(path: Path) -> tuple[dict[str, Any], bytes]:
    """Load and strictly validate one typed proposition target file."""
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        raise BundleTargetValidationError(f"cannot read target {path}: {exc}") from exc
    try:
        decoded = raw_bytes.decode("utf-8")
        value: Any = json.loads(decoded, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, BundleTargetValidationError) as exc:
        raise BundleTargetValidationError(f"invalid target JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise BundleTargetValidationError("target root must be an object")
    target = cast(dict[str, Any], value)
    _validate_target(target)
    return target, raw_bytes


def target_sha256(raw_bytes: bytes) -> str:
    return f"sha256:{hashlib.sha256(raw_bytes).hexdigest()}"


def _claim_for_target(intake: ContractBIntakeView, claim_id: str) -> CBClaim:
    matches = [claim for claim in intake.bundle.claims if claim.claim_id == claim_id]
    if len(matches) != 1:
        raise BundleTargetValidationError(
            f"claim_id must resolve exactly once in Contract B bundle: {claim_id}"
        )
    return matches[0]


def _canonical_passages(intake: ContractBIntakeView) -> dict[str, CBPassage]:
    result: dict[str, CBPassage] = {}
    for rows in intake.bundle.passages.values():
        for passage in rows:
            if passage.passage_id in result:
                raise BundleTargetValidationError(
                    f"passage_id is not globally unique in Contract B bundle: {passage.passage_id}"
                )
            result[passage.passage_id] = passage
    return result


def _extension_admitted_ids(intake: ContractBIntakeView, claim_id: str) -> tuple[str, ...] | None:
    if intake.extension_state != "present" or intake.semantic_context is None:
        return None
    claims = intake.semantic_context.get("claims")
    if not isinstance(claims, list):
        raise BundleTargetValidationError("Contract B semantic context claims must be an array")
    matching = [row for row in claims if isinstance(row, dict) and row.get("claim_id") == claim_id]
    if len(matching) > 1:
        raise BundleTargetValidationError(
            f"claim_id occurs more than once in Contract B semantic context: {claim_id}"
        )
    if not matching:
        return ()
    admitted = matching[0].get("admitted_passages")
    if not isinstance(admitted, list):
        raise BundleTargetValidationError("Contract B admitted_passages must be an array")
    ids: list[str] = []
    for row in admitted:
        if not isinstance(row, dict):
            raise BundleTargetValidationError("Contract B admitted passage row must be an object")
        ids.append(_string(row.get("passage_id"), "admitted_passages[].passage_id"))
    return tuple(ids)


def _base_admitted_ids(claim: CBClaim) -> tuple[str, ...]:
    # Extension-absent fallback preserves canonical claim evidence links.
    # Absence is still carried explicitly in the aperture record and never means
    # a closed evidence world.
    ordered: list[str] = []
    seen: set[str] = set()
    for row in (*claim.evidence_passages, *claim.counterevidence_passages):
        if row.passage_id not in seen:
            ordered.append(row.passage_id)
            seen.add(row.passage_id)
    return tuple(ordered)


def _aperture_binding(intake: ContractBIntakeView, claim_id: str) -> dict[str, Any]:
    observation: dict[str, Any] | None = None
    if intake.intake_ledger is not None:
        rows = intake.intake_ledger.get("aperture")
        if isinstance(rows, list):
            matching = [row for row in rows if isinstance(row, dict) and row.get("claim_id") == claim_id]
            if len(matching) > 1:
                raise BundleTargetValidationError(
                    f"claim_id occurs more than once in Contract B aperture ledger: {claim_id}"
                )
            if matching:
                observation = cast(dict[str, Any], matching[0])
    return {
        "contract_b_factual_context_state": intake.extension_state,
        "observation": observation,
    }


def _intake_snapshot(intake: ContractBIntakeView) -> dict[str, Any]:
    bundle = intake.bundle
    return {
        "schema": "cal-v1-contract-b-intake-snapshot-v1",
        "contract_b_version": bundle.manifest.schema_version,
        "extension_state": intake.extension_state,
        "bundle_manifest": bundle.manifest.model_dump(mode="json"),
        "audit_config": bundle.audit_config.model_dump(mode="json"),
        "validation_set_ref": bundle.validation_set_ref.model_dump(mode="json"),
        "claims": [
            claim.model_dump(mode="json")
            for claim in sorted(bundle.claims, key=lambda row: row.claim_id)
        ],
        "source_profiles": [
            bundle.source_profiles[source_id].model_dump(mode="json")
            for source_id in sorted(bundle.source_profiles)
        ],
        "passages": [
            passage.model_dump(mode="json")
            for source_id in sorted(bundle.passages)
            for passage in sorted(bundle.passages[source_id], key=lambda row: row.passage_id)
        ],
        "factual_context_intake_ledger": intake.intake_ledger,
        "semantic_context": intake.semantic_context,
    }


def prepare_contract_b_input(bundle_dir: Path, target_path: Path) -> PreparedContractBInput:
    """Bind one typed target to one exact validated Contract B evidence world."""
    target, raw_target = load_target(target_path)
    intake = load_contract_b_intake(bundle_dir)
    if intake.bundle.manifest.schema_version != CONTRACT_B_VERSION:
        raise BundleTargetValidationError(
            "canonical CAL V1 bundle execution requires released Contract B "
            f"{CONTRACT_B_VERSION}, got {intake.bundle.manifest.schema_version}"
        )
    claim_id = cast(str, target["claim_id"])
    claim = _claim_for_target(intake, claim_id)
    proposition_raw = _object(target["proposition"], "proposition")
    expected_text_sha256 = hashlib.sha256(claim.claim_text.encode("utf-8")).hexdigest()
    if proposition_raw["text_sha256"] != expected_text_sha256:
        raise BundleTargetValidationError(
            "proposition.text_sha256 does not bind the exact Contract B claim text"
        )
    fields_raw = _object(proposition_raw["fields"], "proposition.fields")
    proposition = TypedProposition.create(
        cast(str, proposition_raw["proposition_id"]),
        SemanticFamily(cast(str, proposition_raw["semantic_family"])),
        {key: cast(str, value) for key, value in fields_raw.items()},
        text_sha256=cast(str, proposition_raw["text_sha256"]),
    )

    canonical_passages = _canonical_passages(intake)
    admitted_ids = _extension_admitted_ids(intake, claim_id)
    if admitted_ids is None:
        admitted_ids = _base_admitted_ids(claim)
    admitted: list[AdmittedPassage] = []
    for passage_id in admitted_ids:
        canonical = canonical_passages.get(passage_id)
        if canonical is None:
            raise BundleTargetValidationError(
                f"admitted passage is missing from canonical Contract B evidence: {passage_id}"
            )
        source = intake.bundle.source_profiles.get(canonical.source_id)
        if source is None:
            raise BundleTargetValidationError(
                f"admitted passage source is missing from Contract B bundle: {canonical.source_id}"
            )
        admitted.append(
            AdmittedPassage(
                passage_id=canonical.passage_id,
                source_id=canonical.source_id,
                text=canonical.passage_text,
                text_sha256=canonical.passage_hash,
                source_sha256=source.content_hash,
            )
        )

    world = EvidenceWorld.create(
        contract_b_version=CONTRACT_B_VERSION,
        bundle_id=intake.bundle.manifest.bundle_id,
        bundle_hash=intake.bundle.manifest.bundle.bundle_hash,
        admitted_passages=tuple(admitted),
        aperture_observation=_aperture_binding(intake, claim_id),
    )
    context = AuditContext(
        original_claim=claim.claim_text,
        proposition=proposition,
        evidence_world=world,
    )
    try:
        context.verify()
    except ValueError as exc:
        raise BundleTargetValidationError(str(exc)) from exc
    return PreparedContractBInput(
        context=context,
        intake=intake,
        target=target,
        target_bytes=raw_target,
        target_sha256=target_sha256(raw_target),
        intake_snapshot=_intake_snapshot(intake),
    )


__all__ = [
    "BundleTargetValidationError",
    "PreparedContractBInput",
    "load_target",
    "prepare_contract_b_input",
    "target_sha256",
]
