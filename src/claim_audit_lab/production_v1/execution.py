"""Atomic deterministic execution for the CAL V1 integration candidate."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from claim_audit_lab.production_v1 import (
    CONTRACT_B_VERSION,
    DISTRIBUTION_VERSION,
    MANIFEST_SCHEMA_RESOURCE,
    PACKET_SCHEMA_RESOURCE,
    PROFILE,
    QUALIFIED_RC1_PARENT_SHA,
    RESULT_SCHEMA_RESOURCE,
    SEMANTIC_IMPLEMENTATION_SHA,
    SUPPORTED_SEMANTIC_FAMILIES,
    TARGET_SCHEMA_RESOURCE,
)
from claim_audit_lab.production_v1.bundle_input import prepare_contract_b_input
from claim_audit_lab.production_v1.packet import (
    context_from_packet,
    load_packet,
    packet_sha256,
)
from claim_audit_lab.production_v1.render import (
    audit_context_record,
    canonical_json_bytes,
    render_markdown,
    result_record,
)
from claim_audit_lab.production_v1.semantic.engine import audit
from claim_audit_lab.resources import read_package_bytes


class OutputSafetyError(ValueError):
    """Raised when a run would overwrite or partially replace an output."""


def _tagged_digest(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _destination_available(out_dir: Path) -> None:
    if out_dir.is_symlink():
        raise OutputSafetyError(f"output directory must not be a symlink: {out_dir}")
    if not out_dir.exists():
        return
    if not out_dir.is_dir():
        raise OutputSafetyError(f"output path is not a directory: {out_dir}")
    try:
        next(out_dir.iterdir())
    except StopIteration:
        return
    raise OutputSafetyError(f"refusing to overwrite non-empty output directory: {out_dir}")


def _schema_hash(resource: str) -> str:
    return _tagged_digest(read_package_bytes(resource))


def inspect_record() -> dict[str, Any]:
    """Return deterministic machine-readable runtime authority information."""
    return {
        "distribution_version": DISTRIBUTION_VERSION,
        "profile": PROFILE,
        "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
        "qualified_rc1_parent_sha": QUALIFIED_RC1_PARENT_SHA,
        "supported_semantic_families": list(SUPPORTED_SEMANTIC_FAMILIES),
        "contract_b": {
            "version": CONTRACT_B_VERSION,
            "compatibility": "released_input_authority",
            "canonical_execution_surface": "run-bundle",
            "intake": "load_contract_b_intake",
        },
        "compatibility_packet_surface": {
            "state": "preserved_noncanonical_input",
            "command": "run",
        },
        "packet_schema_sha256": _schema_hash(PACKET_SCHEMA_RESOURCE),
        "target_schema_sha256": _schema_hash(TARGET_SCHEMA_RESOURCE),
        "result_schema_sha256": _schema_hash(RESULT_SCHEMA_RESOURCE),
        "manifest_schema_sha256": _schema_hash(MANIFEST_SCHEMA_RESOURCE),
        "contract_c_handoff": {
            "owner": "apparatus-contracts",
            "state": "separate_compose_only_versioned_handoff",
        },
        "authorization": {
            "automatic_action_allowed": False,
        },
    }


def _manifest(
    *,
    input_mode: str,
    primary_input_sha256: str,
    input_schema_sha256: str,
    semantic_audit_context_sha256: str,
    artifact_bytes: Mapping[str, bytes],
) -> dict[str, Any]:
    file_hashes = {name: _tagged_digest(value) for name, value in sorted(artifact_bytes.items())}
    return {
        "schema": "cal-v1-manifest-v2",
        "distribution_version": DISTRIBUTION_VERSION,
        "profile": PROFILE,
        "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
        "qualified_rc1_parent_sha": QUALIFIED_RC1_PARENT_SHA,
        "input_mode": input_mode,
        "primary_input_sha256": primary_input_sha256,
        "input_schema_sha256": input_schema_sha256,
        "semantic_audit_context_sha256": semantic_audit_context_sha256,
        "result_schema_sha256": _schema_hash(RESULT_SCHEMA_RESOURCE),
        "manifest_schema_sha256": _schema_hash(MANIFEST_SCHEMA_RESOURCE),
        "files": file_hashes,
    }


def _finalize_run(
    out_dir: Path,
    *,
    artifact_bytes: Mapping[str, bytes],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        out_dir.parent.mkdir(parents=True, exist_ok=True)
        _destination_available(out_dir)
        temp_dir = Path(
            tempfile.mkdtemp(prefix=f".{out_dir.name or 'cal-run'}.tmp-", dir=out_dir.parent)
        )
    except OSError as exc:
        raise OutputSafetyError(f"cannot prepare output directory {out_dir}: {exc}") from exc

    try:
        for name, value in artifact_bytes.items():
            (temp_dir / name).write_bytes(value)
        (temp_dir / "manifest.json").write_bytes(canonical_json_bytes(dict(manifest)))
        if out_dir.exists():
            _destination_available(out_dir)
            out_dir.rmdir()
        os.replace(temp_dir, out_dir)
    except (OSError, OutputSafetyError) as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)
        if isinstance(exc, OutputSafetyError):
            raise
        raise OutputSafetyError(f"cannot finalize output directory {out_dir}: {exc}") from exc
    return dict(manifest)


def run_packet_file(packet_path: Path, out_dir: Path) -> dict[str, Any]:
    """Execute the preserved compatibility packet surface."""
    _destination_available(out_dir)
    packet, raw_bytes = load_packet(packet_path)
    context = context_from_packet(packet)
    result = audit(context)
    input_sha256 = packet_sha256(raw_bytes)
    audit_context_bytes = canonical_json_bytes(audit_context_record(context))
    audit_context_artifact_sha256 = _tagged_digest(audit_context_bytes)
    input_binding = {
        "mode": "compatibility_packet",
        "primary_input_sha256": input_sha256,
        "input_schema_sha256": _schema_hash(PACKET_SCHEMA_RESOURCE),
        "audit_context_artifact_sha256": audit_context_artifact_sha256,
        "contract_b": {
            "version": context.evidence_world.contract_b_version,
            "bundle_id": context.evidence_world.bundle_id,
            "bundle_hash": context.evidence_world.bundle_hash,
            "extension_state": "not_available_in_compatibility_packet",
            "intake_snapshot_sha256": None,
        },
    }
    record = result_record(context, result, input_binding=input_binding)
    artifact_bytes = {
        "input.packet.json": raw_bytes,
        "audit_context.json": audit_context_bytes,
        "result.json": canonical_json_bytes(record),
        "report.md": render_markdown(context, result).encode("utf-8"),
    }
    manifest = _manifest(
        input_mode="compatibility_packet",
        primary_input_sha256=input_sha256,
        input_schema_sha256=_schema_hash(PACKET_SCHEMA_RESOURCE),
        semantic_audit_context_sha256=context.context_sha256,
        artifact_bytes=artifact_bytes,
    )
    return _finalize_run(out_dir, artifact_bytes=artifact_bytes, manifest=manifest)


def validate_contract_b_bundle(bundle_dir: Path, target_path: Path) -> None:
    """Validate canonical Contract B intake and typed target without running CAL semantics."""
    prepare_contract_b_input(bundle_dir, target_path)


def run_contract_b_bundle(bundle_dir: Path, target_path: Path, out_dir: Path) -> dict[str, Any]:
    """Execute one typed target against one exact released Contract B 1.2 artifact."""
    _destination_available(out_dir)
    prepared = prepare_contract_b_input(bundle_dir, target_path)
    context = prepared.context
    result = audit(context)
    audit_context_bytes = canonical_json_bytes(audit_context_record(context))
    intake_snapshot_bytes = canonical_json_bytes(prepared.intake_snapshot)
    audit_context_artifact_sha256 = _tagged_digest(audit_context_bytes)
    intake_snapshot_sha256 = _tagged_digest(intake_snapshot_bytes)
    input_binding = {
        "mode": "contract_b_bundle",
        "primary_input_sha256": prepared.target_sha256,
        "input_schema_sha256": _schema_hash(TARGET_SCHEMA_RESOURCE),
        "audit_context_artifact_sha256": audit_context_artifact_sha256,
        "contract_b": {
            "version": context.evidence_world.contract_b_version,
            "bundle_id": context.evidence_world.bundle_id,
            "bundle_hash": context.evidence_world.bundle_hash,
            "extension_state": prepared.intake.extension_state,
            "intake_snapshot_sha256": intake_snapshot_sha256,
        },
    }
    record = result_record(context, result, input_binding=input_binding)
    artifact_bytes = {
        "input.target.json": prepared.target_bytes,
        "contract_b_intake.snapshot.json": intake_snapshot_bytes,
        "audit_context.json": audit_context_bytes,
        "result.json": canonical_json_bytes(record),
        "report.md": render_markdown(context, result).encode("utf-8"),
    }
    manifest = _manifest(
        input_mode="contract_b_bundle",
        primary_input_sha256=prepared.target_sha256,
        input_schema_sha256=_schema_hash(TARGET_SCHEMA_RESOURCE),
        semantic_audit_context_sha256=context.context_sha256,
        artifact_bytes=artifact_bytes,
    )
    return _finalize_run(out_dir, artifact_bytes=artifact_bytes, manifest=manifest)


__all__ = [
    "OutputSafetyError",
    "inspect_record",
    "run_contract_b_bundle",
    "run_packet_file",
    "validate_contract_b_bundle",
]
