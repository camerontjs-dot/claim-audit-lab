from __future__ import annotations

from typing import Any

from .authority_contract_rc8f import assess_authority as assess_source_atom_bound_receipt


def _valid_span(value: Any) -> bool:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return False
    start, end = value
    if not isinstance(start, int) or isinstance(start, bool):
        return False
    if not isinstance(end, int) or isinstance(end, bool):
        return False
    return start <= end


def _outside(inner: list[int] | tuple[int, int], outer: list[int] | tuple[int, int]) -> bool:
    return inner[0] < outer[0] or inner[1] > outer[1]


def assess_authority(case: dict[str, Any]) -> dict[str, Any]:
    """Bind a semantic authority receipt to a validated Contract-B evidence segment.

    RC8H assumes the raw Contract-B coordinate was already validated by Contract-B
    intake. It does not duplicate bundle/passage hashing or integrity validation.
    """
    if case["execution_state"] != "completed":
        return assess_source_atom_bound_receipt(case)

    if not case["evidence_admitted"]:
        return assess_source_atom_bound_receipt(case)

    # Preserve the frozen RC8F/RC8D source-anchor semantics and precedence.
    raw_source_id = case.get("raw_source_id")
    authority_subject_source_id = case.get("authority_subject_source_id")
    if raw_source_id is None or authority_subject_source_id is None:
        return assess_source_atom_bound_receipt(case)
    if authority_subject_source_id != raw_source_id:
        return assess_source_atom_bound_receipt(case)

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
            # Preserve the frozen RC8B missing/malformed field-span semantics.
            continue
        if _outside(support_span, admitted_span):
            return {
                "authority_status": "REJECTED",
                "reason": f"FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:{field}",
            }

    return assess_source_atom_bound_receipt(case)
