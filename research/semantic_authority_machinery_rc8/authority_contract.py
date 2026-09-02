from __future__ import annotations

from typing import Any


UNRESOLVED_FIELD_STATES = {
    "extraction_unresolved": "FIELD_EXTRACTION_UNRESOLVED",
    "insufficient_authority": "FIELD_INSUFFICIENT_AUTHORITY",
}


def assess_authority(case: dict[str, Any]) -> dict[str, Any]:
    """Assess epistemic warrant for one already-proposed semantic atom.

    This gate consumes frozen interpretation/jurisdiction receipts. It does not parse
    language and it does not treat reader count, confidence, or instrument count as
    authority-bearing inputs.
    """
    if case["execution_state"] != "completed":
        return {"authority_status": "NO_ASSESSMENT", "reason": "EXECUTION_FAILED"}

    if not case["evidence_admitted"]:
        return {"authority_status": "REJECTED", "reason": "EVIDENCE_NOT_ADMITTED"}

    proposal = case["proposal"]
    assertion = case["assertion"]
    operator = case["operator"]

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
        if receipt is None or receipt["status"] == "absent_not_applicable":
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
        if composition["state"] == "rejected":
            return {"authority_status": "REJECTED", "reason": "COMPOSITION_REJECTED"}
        if composition["state"] != "warranted":
            return {"authority_status": "UNRESOLVED", "reason": "COMPOSITION_UNRESOLVED"}

    aperture = case["aperture"]
    if aperture["required"] and aperture["state"] != "sufficient":
        return {"authority_status": "UNRESOLVED", "reason": "APERTURE_UNRESOLVED"}

    return {"authority_status": "WARRANTED", "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED"}
