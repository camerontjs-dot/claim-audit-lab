"""Common non-authoritative RC7E instrument receipt contract."""
from __future__ import annotations

import hashlib
from typing import Any, Iterable

STATUSES = {"CLAIMED", "NOT_APPLICABLE", "UNRESOLVED"}


def source_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def proposal(
    dimension: str,
    atom: dict[str, Any] | None = None,
    *,
    scorable: bool = False,
    anchor_ids: Iterable[int] = (),
    note: str | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "dimension": dimension,
        "atom": atom,
        "scorable": bool(scorable and atom is not None),
        "anchor_ids": list(anchor_ids),
    }
    if note:
        row["note"] = note
    return row


def make_receipt(
    raw_source: str,
    *,
    instrument_id: str,
    instrument_identity: dict[str, Any],
    measurement_principle: str,
    status: str,
    proposed_dimensions: Iterable[str] = (),
    anchors: Iterable[dict[str, Any]] = (),
    candidate_atoms: Iterable[dict[str, Any]] = (),
    native_scores: Iterable[dict[str, Any]] = (),
    jurisdiction: Iterable[str] = (),
    limitations: Iterable[str] = (),
    residue: Iterable[str] = (),
    runtime: dict[str, Any] | None = None,
    native_output: Any = None,
) -> dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(f"invalid status: {status}")
    receipt = {
        "raw_source": raw_source,
        "raw_source_sha256": source_sha(raw_source),
        "instrument_id": instrument_id,
        "instrument_identity": instrument_identity,
        "measurement_principle": measurement_principle,
        "status": status,
        "proposed_dimensions": sorted(set(proposed_dimensions)),
        "anchors": list(anchors),
        "candidate_atoms": list(candidate_atoms),
        "native_scores": list(native_scores),
        "jurisdiction": list(jurisdiction),
        "limitations": list(limitations),
        "residue": list(residue),
        "runtime": runtime or {},
    }
    if native_output is not None:
        receipt["native_output"] = native_output
    validate_receipt(receipt)
    return receipt


def unavailable_receipt(raw_source: str, *, instrument_id: str, instrument_identity: dict[str, Any], measurement_principle: str, error: str, limitations: Iterable[str] = ()) -> dict[str, Any]:
    return make_receipt(
        raw_source,
        instrument_id=instrument_id,
        instrument_identity=instrument_identity,
        measurement_principle=measurement_principle,
        status="UNRESOLVED",
        limitations=[*limitations, "instrument_unavailable_or_failed"],
        residue=["no_measurement_due_to_runtime_failure"],
        runtime={"load_status": "FAILED", "error": error},
    )


def validate_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("status") not in STATUSES:
        raise AssertionError("invalid receipt status")
    raw = receipt.get("raw_source")
    if not isinstance(raw, str):
        raise AssertionError("raw_source must be str")
    if receipt.get("raw_source_sha256") != source_sha(raw):
        raise AssertionError("source hash mismatch")
    for key in ("instrument_id", "instrument_identity", "measurement_principle", "proposed_dimensions", "anchors", "candidate_atoms", "native_scores", "jurisdiction", "limitations", "residue", "runtime"):
        if key not in receipt:
            raise AssertionError(f"missing receipt field: {key}")
    dims = set(receipt["proposed_dimensions"])
    for row in receipt["candidate_atoms"]:
        if row.get("dimension") not in dims:
            raise AssertionError("candidate atom dimension must be proposed")
        if row.get("scorable") and not isinstance(row.get("atom"), dict):
            raise AssertionError("scorable proposal requires atom")
