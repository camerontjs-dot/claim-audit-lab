from __future__ import annotations

from typing import Any


UNRESOLVED_FIELD_STATES = {
    "extraction_unresolved": "FIELD_EXTRACTION_UNRESOLVED",
    "insufficient_authority": "FIELD_INSUFFICIENT_AUTHORITY",
}


def _binding_result(receipt: dict[str, Any], subject: str, component: str) -> dict[str, str] | None:
    receipt_subject = receipt.get("authority_subject_id")
    if receipt_subject is None:
        return {
            "authority_status": "UNRESOLVED",
            "reason": f"AUTHORITY_SUBJECT_BINDING_UNRESOLVED:{component}",
        }
    if receipt_subject != subject:
        return {
            "authority_status": "REJECTED",
            "reason": f"AUTHORITY_SUBJECT_MISMATCH:{component}",
        }
    return None


def _field_span_result(receipt: dict[str, Any], governed_span: list[int], field: str) -> dict[str, str] | None:
    span = receipt.get("span")
    if not isinstance(span, (list, tuple)) or len(span) != 2:
        return {
            "authority_status": "UNRESOLVED",
            "reason": f"FIELD_SUPPORT_SPAN_UNRESOLVED:{field}",
        }
    start, end = span
    governed_start, governed_end = governed_span
    if not isinstance(start, int) or not isinstance(end, int) or start > end:
        return {
            "authority_status": "UNRESOLVED",
            "reason": f"FIELD_SUPPORT_SPAN_UNRESOLVED:{field}",
        }
    if start < governed_start or end > governed_end:
        return {
            "authority_status": "REJECTED",
            "reason": f"FIELD_SUPPORT_OUTSIDE_OPERATOR_GOVERNANCE:{field}",
        }
    return None


def assess_authority(case: dict[str, Any]) -> dict[str, Any]:
    """Assess authority for an already-proposed semantic atom with bound receipts.

    RC8B adds only explicit authority-subject consistency and required-field support
    span governance to the frozen RC8 transition. It does not parse source language,
    authenticate receipt producers, or treat reader/instrument counts as authority.
    """
    if case["execution_state"] != "completed":
        return {"authority_status": "NO_ASSESSMENT", "reason": "EXECUTION_FAILED"}

    if not case["evidence_admitted"]:
        return {"authority_status": "REJECTED", "reason": "EVIDENCE_NOT_ADMITTED"}

    subject = case.get("authority_subject_id")
    if subject is None:
        return {
            "authority_status": "UNRESOLVED",
            "reason": "AUTHORITY_SUBJECT_BINDING_UNRESOLVED:assessment",
        }

    proposal = case["proposal"]
    assertion = case["assertion"]
    operator = case["operator"]

    binding = _binding_result(proposal, subject, "proposal")
    if binding:
        return binding
    binding = _binding_result(assertion, subject, "assertion")
    if binding:
        return binding
    binding = _binding_result(operator, subject, "operator")
    if binding:
        return binding

    if assertion["state"] == "not_asserted":
        return {"authority_status": "REJECTED", "reason": "SOURCE_ASSERTION_NOT_ESTABLISHED"}
    if assertion["state"] == "unknown":
        return {"authority_status": "UNRESOLVED", "reason": "SOURCE_ASSERTION_UNRESOLVED"}

    if operator["domain"] != proposal["family"]:
        return {"authority_status": "REJECTED", "reason": "OPERATOR_DOMAIN_MISMATCH"}
    if operator["applicability"] == "inapplicable":
        return {"authority_status": "REJECTED", "reason": "OPERATOR_INAPPLICABLE"}
    if operator["applicability"] == "unknown":
        return {"authority_status": "UNRESOLVED", "reason": "OPERATOR_APPLICABILITY_UNKNOWN"}

    start, end = proposal["source_span"]
    governed_start, governed_end = operator["governed_span"]
    if start < governed_start or end > governed_end:
        return {"authority_status": "REJECTED", "reason": "SOURCE_SPAN_OUTSIDE_OPERATOR_GOVERNANCE"}

    if proposal["extra_modifiers"]:
        return {"authority_status": "REJECTED", "reason": "UNSUPPORTED_EXTRA_MODIFIER"}

    jurisdiction = set(operator["jurisdiction_fields"])
    warrants = case["field_warrants"]
    for field in case["required_fields"]:
        if field not in jurisdiction:
            return {"authority_status": "REJECTED", "reason": f"FIELD_OUTSIDE_OPERATOR_JURISDICTION:{field}"}
        receipt = warrants.get(field)
        if receipt is None:
            return {"authority_status": "REJECTED", "reason": f"FIELD_REQUIRED_ABSENT:{field}"}

        binding = _binding_result(receipt, subject, f"field:{field}")
        if binding:
            return binding
        span_result = _field_span_result(receipt, operator["governed_span"], field)
        if span_result:
            return span_result

        if receipt["status"] == "absent_not_applicable":
            return {"authority_status": "REJECTED", "reason": f"FIELD_REQUIRED_ABSENT:{field}"}
        if receipt["status"] in UNRESOLVED_FIELD_STATES:
            return {
                "authority_status": "UNRESOLVED",
                "reason": f"{UNRESOLVED_FIELD_STATES[receipt['status']]}:{field}",
            }
        if receipt["status"] not in {"established", "semantic_unknown"}:
            return {"authority_status": "UNRESOLVED", "reason": f"FIELD_STATUS_UNRECOGNIZED:{field}"}
        if proposal["fields"].get(field) != receipt["value"]:
            return {"authority_status": "REJECTED", "reason": f"FIELD_VALUE_MISMATCH:{field}"}

    composition = case["composition"]
    if composition["required"]:
        binding = _binding_result(composition, subject, "composition")
        if binding:
            return binding
        if composition["state"] == "rejected":
            return {"authority_status": "REJECTED", "reason": "COMPOSITION_REJECTED"}
        if composition["state"] != "warranted":
            return {"authority_status": "UNRESOLVED", "reason": "COMPOSITION_UNRESOLVED"}

    aperture = case["aperture"]
    if aperture["required"]:
        binding = _binding_result(aperture, subject, "aperture")
        if binding:
            return binding
        if aperture["state"] != "sufficient":
            return {"authority_status": "UNRESOLVED", "reason": "APERTURE_UNRESOLVED"}

    return {"authority_status": "WARRANTED", "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED"}
