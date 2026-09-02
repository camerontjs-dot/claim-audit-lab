from __future__ import annotations

from typing import Any

from .authority_contract_rc8h import _outside, _valid_span, assess_authority as assess_segment_atom_bound_receipt


def assess_authority(case: dict[str, Any]) -> dict[str, Any]:
    """Bind a validated Contract-B segment receipt to its referenced claim before atom authority."""
    if case["execution_state"] != "completed":
        return assess_segment_atom_bound_receipt(case)

    if not case["evidence_admitted"]:
        return assess_segment_atom_bound_receipt(case)

    raw_source_id = case.get("raw_source_id")
    authority_subject_source_id = case.get("authority_subject_source_id")
    if raw_source_id is None or authority_subject_source_id is None:
        return assess_segment_atom_bound_receipt(case)
    if authority_subject_source_id != raw_source_id:
        return assess_segment_atom_bound_receipt(case)

    raw_bundle_id = case.get("raw_bundle_id")
    authority_subject_bundle_id = case.get("authority_subject_bundle_id")
    raw_passage_id = case.get("raw_passage_id")
    authority_subject_passage_id = case.get("authority_subject_passage_id")

    if (
        raw_bundle_id is None
        or authority_subject_bundle_id is None
        or raw_passage_id is None
        or authority_subject_passage_id is None
    ):
        return {
            "authority_status": "UNRESOLVED",
            "reason": "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED",
        }

    if authority_subject_bundle_id != raw_bundle_id:
        return {
            "authority_status": "REJECTED",
            "reason": "AUTHORITY_EVIDENCE_BUNDLE_MISMATCH",
        }

    if authority_subject_passage_id != raw_passage_id:
        return {
            "authority_status": "REJECTED",
            "reason": "AUTHORITY_EVIDENCE_PASSAGE_MISMATCH",
        }

    admitted_span = case.get("admitted_passage_span")
    if not _valid_span(admitted_span):
        return {
            "authority_status": "UNRESOLVED",
            "reason": "ADMITTED_PASSAGE_SPAN_UNRESOLVED",
        }

    proposal_span = case["proposal"]["source_span"]
    if _outside(proposal_span, admitted_span):
        return {
            "authority_status": "REJECTED",
            "reason": "SOURCE_SPAN_OUTSIDE_ADMITTED_PASSAGE",
        }

    warrants = case["field_warrants"]
    for field in case["required_fields"]:
        receipt = warrants.get(field)
        if receipt is None:
            continue
        support_span = receipt.get("span")
        if not _valid_span(support_span):
            continue
        if _outside(support_span, admitted_span):
            return {
                "authority_status": "REJECTED",
                "reason": f"FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:{field}",
            }

    raw_claim_id = case.get("raw_claim_id")
    authority_subject_claim_id = case.get("authority_subject_claim_id")
    if raw_claim_id is None or authority_subject_claim_id is None:
        return {
            "authority_status": "UNRESOLVED",
            "reason": "AUTHORITY_CLAIM_BINDING_UNRESOLVED",
        }

    if authority_subject_claim_id != raw_claim_id:
        return {
            "authority_status": "REJECTED",
            "reason": "AUTHORITY_CLAIM_MISMATCH",
        }

    return assess_segment_atom_bound_receipt(case)
