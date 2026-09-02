from __future__ import annotations

from typing import Any

from .authority_contract_rc8b import assess_authority as assess_bound_receipt


def assess_authority(case: dict[str, Any]) -> dict[str, Any]:
    """Add admitted-evidence source anchoring before the frozen RC8B gate."""
    if case["execution_state"] != "completed":
        return assess_bound_receipt(case)

    if not case["evidence_admitted"]:
        return assess_bound_receipt(case)

    raw_source_id = case.get("raw_source_id")
    authority_subject_source_id = case.get("authority_subject_source_id")

    if raw_source_id is None or authority_subject_source_id is None:
        return {
            "authority_status": "UNRESOLVED",
            "reason": "AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED",
        }

    if authority_subject_source_id != raw_source_id:
        return {
            "authority_status": "REJECTED",
            "reason": "AUTHORITY_EVIDENCE_SOURCE_MISMATCH",
        }

    return assess_bound_receipt(case)
