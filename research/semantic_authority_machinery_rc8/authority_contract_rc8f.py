from __future__ import annotations

from typing import Any

from .authority_contract_rc8d import assess_authority as assess_source_bound_receipt


def assess_authority(case: dict[str, Any]) -> dict[str, Any]:
    """Add whole-atom identity binding before the frozen RC8D/RC8B gate."""
    if case["execution_state"] != "completed":
        return assess_source_bound_receipt(case)

    if not case["evidence_admitted"]:
        return assess_source_bound_receipt(case)

    raw_source_id = case.get("raw_source_id")
    authority_subject_source_id = case.get("authority_subject_source_id")

    # Preserve frozen RC8D source-anchor semantics and precedence exactly.
    if raw_source_id is None or authority_subject_source_id is None:
        return assess_source_bound_receipt(case)
    if authority_subject_source_id != raw_source_id:
        return assess_source_bound_receipt(case)

    target_atom_id = case.get("target_atom_id")
    authority_subject_atom_id = case.get("authority_subject_atom_id")

    if target_atom_id is None or authority_subject_atom_id is None:
        return {
            "authority_status": "UNRESOLVED",
            "reason": "AUTHORITY_ATOM_IDENTITY_BINDING_UNRESOLVED",
        }

    if authority_subject_atom_id != target_atom_id:
        return {
            "authority_status": "REJECTED",
            "reason": "AUTHORITY_ATOM_IDENTITY_MISMATCH",
        }

    return assess_source_bound_receipt(case)
