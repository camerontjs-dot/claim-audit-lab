"""Atomic deterministic execution for the CAL V1 production CLI."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from claim_audit_lab.production_v1 import (
    CONTRACT_B_VERSION,
    DISTRIBUTION_VERSION,
    MANIFEST_SCHEMA_RESOURCE,
    PACKET_SCHEMA_RESOURCE,
    PROFILE,
    RESULT_SCHEMA_RESOURCE,
    SEMANTIC_IMPLEMENTATION_SHA,
    SUPPORTED_SEMANTIC_FAMILIES,
)
from claim_audit_lab.production_v1.packet import (
    context_from_packet,
    load_packet,
    packet_sha256,
)
from claim_audit_lab.production_v1.render import (
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
        "supported_semantic_families": list(SUPPORTED_SEMANTIC_FAMILIES),
        "contract_b": {
            "version": CONTRACT_B_VERSION,
            "compatibility": "exact_released_input_authority",
        },
        "packet_schema_sha256": _schema_hash(PACKET_SCHEMA_RESOURCE),
        "result_schema_sha256": _schema_hash(RESULT_SCHEMA_RESOURCE),
        "manifest_schema_sha256": _schema_hash(MANIFEST_SCHEMA_RESOURCE),
        "contract_c_handoff": {
            "owner": "apparatus-contracts",
            "state": "separate_versioned_handoff",
        },
        "authorization": {
            "automatic_action_allowed": False,
        },
    }


def _manifest(
    *,
    input_packet_sha256: str,
    result_bytes: bytes,
    report_bytes: bytes,
    packet_schema_sha256: str,
    result_schema_sha256: str,
) -> dict[str, Any]:
    result_sha256 = _tagged_digest(result_bytes)
    report_sha256 = _tagged_digest(report_bytes)
    return {
        "schema": "cal-v1-manifest-v1",
        "distribution_version": DISTRIBUTION_VERSION,
        "profile": PROFILE,
        "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
        "input_packet_sha256": input_packet_sha256,
        "result_sha256": result_sha256,
        "report_sha256": report_sha256,
        "packet_schema_sha256": packet_schema_sha256,
        "result_schema_sha256": result_schema_sha256,
        "files": {
            "input.packet.json": input_packet_sha256,
            "result.json": result_sha256,
            "report.md": report_sha256,
        },
    }


def run_packet_file(packet_path: Path, out_dir: Path) -> dict[str, Any]:
    """Execute one packet and atomically finalize the four-file run directory."""
    _destination_available(out_dir)
    packet, raw_bytes = load_packet(packet_path)
    context = context_from_packet(packet)
    result = audit(context)
    input_sha256 = packet_sha256(raw_bytes)
    record = result_record(context, result, input_packet_sha256=input_sha256)
    result_bytes = canonical_json_bytes(record)
    report_bytes = render_markdown(context, result).encode("utf-8")
    packet_schema_sha256 = _schema_hash(PACKET_SCHEMA_RESOURCE)
    result_schema_sha256 = _schema_hash(RESULT_SCHEMA_RESOURCE)
    manifest = _manifest(
        input_packet_sha256=input_sha256,
        result_bytes=result_bytes,
        report_bytes=report_bytes,
        packet_schema_sha256=packet_schema_sha256,
        result_schema_sha256=result_schema_sha256,
    )
    manifest_bytes = canonical_json_bytes(manifest)

    try:
        out_dir.parent.mkdir(parents=True, exist_ok=True)
        _destination_available(out_dir)
        temp_dir = Path(
            tempfile.mkdtemp(prefix=f".{out_dir.name or 'cal-run'}.tmp-", dir=out_dir.parent)
        )
    except OSError as exc:
        raise OutputSafetyError(f"cannot prepare output directory {out_dir}: {exc}") from exc

    try:
        (temp_dir / "input.packet.json").write_bytes(raw_bytes)
        (temp_dir / "result.json").write_bytes(result_bytes)
        (temp_dir / "report.md").write_bytes(report_bytes)
        (temp_dir / "manifest.json").write_bytes(manifest_bytes)
        if out_dir.exists():
            _destination_available(out_dir)
            out_dir.rmdir()
        os.replace(temp_dir, out_dir)
    except (OSError, OutputSafetyError) as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)
        if isinstance(exc, OutputSafetyError):
            raise
        raise OutputSafetyError(f"cannot finalize output directory {out_dir}: {exc}") from exc
    return manifest


__all__ = ["OutputSafetyError", "inspect_record", "run_packet_file"]
