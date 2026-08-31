"""Separate RC7E authority layer over non-authoritative instrument receipts."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from research.semantic_operator_jurisdiction_rc7d_d import validator_v3_final
from research.language_instrument_ablation_rc7e.contract import source_sha

LEGACY_DIMENSIONS = {"permission", "role_binding", "quantifier", "exception", "temporal", "subclass", "probability", "quantitative"}


def _span_from_anchor(raw: str, anchor: dict[str, Any]) -> dict[str, Any] | None:
    start = anchor.get("start")
    end = anchor.get("end")
    if isinstance(start, int) and isinstance(end, int) and 0 <= start <= end <= len(raw):
        return {"start": start, "end": end, "text": raw[start:end]}
    return None


def validate_common_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    raw = receipt["raw_source"]
    if receipt["raw_source_sha256"] != source_sha(raw):
        raise AssertionError("authority received altered source")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in receipt.get("candidate_atoms", []):
        if isinstance(row.get("atom"), dict):
            grouped[row["dimension"]].append(row)

    authorized: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rejected: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    validation_receipts: list[dict[str, Any]] = []

    spans = [s for a in receipt.get("anchors", []) if (s := _span_from_anchor(raw, a)) is not None]
    for dimension, rows in grouped.items():
        if dimension not in LEGACY_DIMENSIONS:
            for row in rows:
                unresolved.append({"instrument_id": receipt["instrument_id"], "dimension": dimension, "atom": row["atom"], "reason": "outside_rc7d_d_validator_jurisdiction"})
            continue
        legacy = {
            "operator_id": f"rc7e::{receipt['instrument_id']}",
            "version": "rc7e-common-adapter-v1",
            "dimension": dimension,
            "status": "CLAIMED",
            "raw_source": raw,
            "raw_source_sha256": source_sha(raw),
            "spans": spans,
            "atoms": [r["atom"] for r in rows],
            "warrants": [f"measurement_proposal::{receipt['instrument_id']}"] * len(rows),
            "composition_requirements": [],
        }
        try:
            vr = validator_v3_final.validate_receipt(raw, legacy)
            validation_receipts.append(vr)
            for av in vr.get("atom_validations", []):
                item = {"instrument_id": receipt["instrument_id"], "dimension": dimension, **av}
                if av.get("status") == "AUTHORIZED":
                    authorized[dimension].append(av["atom"])
                elif av.get("status") == "REJECTED":
                    rejected.append(item)
                else:
                    unresolved.append(item)
        except Exception as exc:
            for row in rows:
                unresolved.append({"instrument_id": receipt["instrument_id"], "dimension": dimension, "atom": row["atom"], "reason": f"validator_exception:{type(exc).__name__}:{exc}"})

    atom_dims = set(grouped)
    for dimension in receipt.get("proposed_dimensions", []):
        if dimension not in atom_dims:
            unresolved.append({"instrument_id": receipt["instrument_id"], "dimension": dimension, "atom": None, "reason": "dimension_observed_without_authorizable_typed_atom"})

    return {
        "raw_source": raw,
        "raw_source_sha256": source_sha(raw),
        "instrument_id": receipt["instrument_id"],
        "authorized_atoms": dict(authorized),
        "authorized_dimensions": sorted(authorized),
        "rejected_proposals": rejected,
        "unresolved_proposals": unresolved,
        "validation_receipts": validation_receipts,
    }


def validate_union(raw: str, receipts: list[dict[str, Any]]) -> dict[str, Any]:
    combined = {
        "raw_source": raw,
        "raw_source_sha256": source_sha(raw),
        "instrument_id": "portfolio_union",
        "instrument_identity": {"version": "rc7e-union-v1"},
        "measurement_principle": "proposal_union",
        "status": "CLAIMED" if any(r.get("proposed_dimensions") for r in receipts) else "NOT_APPLICABLE",
        "proposed_dimensions": sorted({d for r in receipts for d in r.get("proposed_dimensions", [])}),
        "anchors": [a for r in receipts for a in r.get("anchors", [])],
        "candidate_atoms": [a for r in receipts for a in r.get("candidate_atoms", [])],
        "native_scores": [], "jurisdiction": [], "limitations": [], "residue": [], "runtime": {},
    }
    return validate_common_receipt(combined)
