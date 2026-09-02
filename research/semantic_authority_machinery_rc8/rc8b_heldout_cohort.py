from __future__ import annotations

from copy import deepcopy
from typing import Any


SUBJECT_A = "authority-subject:prospective:alpha:comparison-77"
SUBJECT_B = "authority-subject:prospective:beta:comparison-77"

VALUES: dict[str, Any] = {
    "lhs_entity": "lot_17",
    "rhs_entity": "lot_23",
    "property": "sterility_hold",
    "numeric_value": 6,
    "unit": "hour",
    "comparison_direction": "greater_equal",
    "temporal_attachment": "after_sampling",
}


def _w(
    value: Any,
    *,
    status: str = "established",
    subject: str = SUBJECT_A,
    span: tuple[int, int] = (82, 128),
) -> dict[str, Any]:
    return {
        "status": status,
        "value": value,
        "span": list(span),
        "authority_subject_id": subject,
    }


def base_case() -> dict[str, Any]:
    return {
        "case_id": "B-H-BASE",
        "mutation_axis": "fully_bound_positive",
        "expected_authority": "WARRANTED",
        "expected_reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
        "raw_source_id": "source:prospective:alpha",
        "authority_subject_id": SUBJECT_A,
        "evidence_admitted": True,
        "proposal": {
            "family": "comparison",
            "source_span": [80, 130],
            "fields": deepcopy(VALUES),
            "extra_modifiers": [],
            "authority_subject_id": SUBJECT_A,
        },
        "assertion": {
            "state": "asserted",
            "scope_path": ["reporter", "main_clause"],
            "authority_subject_id": SUBJECT_A,
        },
        "operator": {
            "operator_id": "operator:comparison:prospective-rc8b-v1",
            "domain": "comparison",
            "applicability": "applicable",
            "governed_span": [50, 160],
            "jurisdiction_fields": sorted(VALUES),
            "authority_subject_id": SUBJECT_A,
        },
        "field_warrants": {name: _w(value) for name, value in VALUES.items()},
        "required_fields": sorted(VALUES),
        "composition": {
            "required": False,
            "state": "not_applicable",
            "basis": [],
        },
        "aperture": {
            "required": False,
            "state": "not_applicable",
        },
        "execution_state": "completed",
        "measurement": {
            "instrument": "measurement:comparison:prospective-v1",
            "value": "candidate-blind",
        },
        "instrument_ids": ["measurement:comparison:prospective-v1"],
        "reader_agreement_count": 1,
    }


def mutate(case_id: str, axis: str, expected: str, reason: str) -> dict[str, Any]:
    case = deepcopy(base_case())
    case["case_id"] = case_id
    case["mutation_axis"] = axis
    case["expected_authority"] = expected
    case["expected_reason"] = reason
    return case


def build_rc8b_heldout_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [base_case()]

    c = mutate("B-H-EXEC", "execution_failure_without_binding", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    c.pop("authority_subject_id")
    cases.append(c)

    c = mutate("B-H-EVIDENCE", "evidence_not_admitted_without_binding", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    c.pop("authority_subject_id")
    cases.append(c)

    c = mutate("B-H-MISS-ASSESS", "missing_assessment_subject", "UNRESOLVED", "AUTHORITY_SUBJECT_BINDING_UNRESOLVED:assessment")
    c.pop("authority_subject_id")
    cases.append(c)

    c = mutate("B-H-MISS-PROP", "missing_proposal_subject", "UNRESOLVED", "AUTHORITY_SUBJECT_BINDING_UNRESOLVED:proposal")
    c["proposal"].pop("authority_subject_id")
    cases.append(c)

    c = mutate("B-H-MISMATCH-PROP", "proposal_subject_mismatch", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:proposal")
    c["proposal"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("B-H-MISS-ASSERT", "missing_assertion_subject", "UNRESOLVED", "AUTHORITY_SUBJECT_BINDING_UNRESOLVED:assertion")
    c["assertion"].pop("authority_subject_id")
    cases.append(c)

    c = mutate("B-H-MISMATCH-ASSERT", "assertion_subject_mismatch", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:assertion")
    c["assertion"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("B-H-MISS-OP", "missing_operator_subject", "UNRESOLVED", "AUTHORITY_SUBJECT_BINDING_UNRESOLVED:operator")
    c["operator"].pop("authority_subject_id")
    cases.append(c)

    c = mutate("B-H-MISMATCH-OP", "operator_subject_mismatch", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:operator")
    c["operator"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("B-H-ASSERT-NO", "bound_not_asserted", "REJECTED", "SOURCE_ASSERTION_NOT_ESTABLISHED")
    c["assertion"]["state"] = "not_asserted"
    c["assertion"]["scope_path"] = ["quoted", "embedded"]
    cases.append(c)

    c = mutate("B-H-ASSERT-UNK", "bound_assertion_unknown", "UNRESOLVED", "SOURCE_ASSERTION_UNRESOLVED")
    c["assertion"]["state"] = "unknown"
    c["assertion"]["scope_path"] = ["wrapper", "unresolved"]
    cases.append(c)

    c = mutate("B-H-DOMAIN", "bound_domain_mismatch", "REJECTED", "OPERATOR_DOMAIN_MISMATCH")
    c["operator"]["domain"] = "event_ordering"
    cases.append(c)

    c = mutate("B-H-APP-UNK", "bound_applicability_unknown", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    cases.append(c)

    c = mutate("B-H-APP-NO", "bound_operator_inapplicable", "REJECTED", "OPERATOR_INAPPLICABLE")
    c["operator"]["applicability"] = "inapplicable"
    cases.append(c)

    c = mutate("B-H-PROP-SPAN", "bound_proposal_span_outside_governance", "REJECTED", "SOURCE_SPAN_OUTSIDE_OPERATOR_GOVERNANCE")
    c["proposal"]["source_span"] = [161, 180]
    cases.append(c)

    c = mutate("B-H-EXTRA", "bound_unsupported_modifier", "REJECTED", "UNSUPPORTED_EXTRA_MODIFIER")
    c["proposal"]["extra_modifiers"] = ["only_when_shift_b"]
    cases.append(c)

    field = "unit"
    c = mutate("B-H-FIELD-ABSENT", "required_field_receipt_absent", "REJECTED", f"FIELD_REQUIRED_ABSENT:{field}")
    c["field_warrants"].pop(field)
    cases.append(c)

    c = mutate("B-H-FIELD-MISS-SUBJECT", "required_field_missing_subject", "UNRESOLVED", f"AUTHORITY_SUBJECT_BINDING_UNRESOLVED:field:{field}")
    c["field_warrants"][field].pop("authority_subject_id")
    cases.append(c)

    c = mutate("B-H-FIELD-MISMATCH-SUBJECT", "required_field_subject_mismatch", "REJECTED", f"AUTHORITY_SUBJECT_MISMATCH:field:{field}")
    c["field_warrants"][field]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("B-H-FIELD-MISS-SPAN", "required_field_missing_support_span", "UNRESOLVED", f"FIELD_SUPPORT_SPAN_UNRESOLVED:{field}")
    c["field_warrants"][field].pop("span")
    cases.append(c)

    c = mutate("B-H-FIELD-BAD-SPAN", "required_field_malformed_support_span", "UNRESOLVED", f"FIELD_SUPPORT_SPAN_UNRESOLVED:{field}")
    c["field_warrants"][field]["span"] = [120, 110]
    cases.append(c)

    c = mutate("B-H-FIELD-SPAN-LEFT", "required_field_support_left_outside_governance", "REJECTED", f"FIELD_SUPPORT_OUTSIDE_OPERATOR_GOVERNANCE:{field}")
    c["field_warrants"][field]["span"] = [49, 80]
    cases.append(c)

    c = mutate("B-H-FIELD-SPAN-RIGHT", "required_field_support_right_outside_governance", "REJECTED", f"FIELD_SUPPORT_OUTSIDE_OPERATOR_GOVERNANCE:{field}")
    c["field_warrants"][field]["span"] = [130, 161]
    cases.append(c)

    c = mutate("B-H-FIELD-SPAN-BOUNDARY", "required_field_support_touches_operator_boundaries", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["field_warrants"][field]["span"] = [50, 160]
    cases.append(c)

    c = mutate("B-H-FIELD-VALUE", "bound_field_value_mismatch", "REJECTED", f"FIELD_VALUE_MISMATCH:{field}")
    c["proposal"]["fields"][field] = "minute"
    cases.append(c)

    c = mutate("B-H-FIELD-EXTRACT", "bound_extraction_unresolved", "UNRESOLVED", f"FIELD_EXTRACTION_UNRESOLVED:{field}")
    c["field_warrants"][field]["status"] = "extraction_unresolved"
    c["field_warrants"][field]["value"] = None
    cases.append(c)

    c = mutate("B-H-FIELD-INSUFF", "bound_insufficient_authority", "UNRESOLVED", f"FIELD_INSUFFICIENT_AUTHORITY:{field}")
    c["field_warrants"][field]["status"] = "insufficient_authority"
    c["field_warrants"][field]["value"] = None
    cases.append(c)

    c = mutate("B-H-SEMUNK", "bound_source_semantic_unknown", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["field_warrants"][field]["status"] = "semantic_unknown"
    c["field_warrants"][field]["value"] = "unknown"
    c["proposal"]["fields"][field] = "unknown"
    cases.append(c)

    c = mutate("B-H-SEMUNK-LAUNDER", "bound_semantic_unknown_launder", "REJECTED", f"FIELD_VALUE_MISMATCH:{field}")
    c["field_warrants"][field]["status"] = "semantic_unknown"
    c["field_warrants"][field]["value"] = "unknown"
    cases.append(c)

    c = mutate("B-H-FIELD-STATUS-ABSENT", "bound_required_field_not_applicable", "REJECTED", f"FIELD_REQUIRED_ABSENT:{field}")
    c["field_warrants"][field]["status"] = "absent_not_applicable"
    c["field_warrants"][field]["value"] = None
    cases.append(c)

    c = mutate("B-H-JURIS", "bound_field_outside_jurisdiction", "REJECTED", f"FIELD_OUTSIDE_OPERATOR_JURISDICTION:{field}")
    c["operator"]["jurisdiction_fields"].remove(field)
    cases.append(c)

    c = mutate("B-H-COMP-GOOD", "required_composition_bound_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["composition"] = {
        "required": True,
        "state": "warranted",
        "basis": ["atom:comparison", "atom:temporal"],
        "authority_subject_id": SUBJECT_A,
    }
    cases.append(c)

    c = mutate("B-H-COMP-MISS", "required_composition_missing_subject", "UNRESOLVED", "AUTHORITY_SUBJECT_BINDING_UNRESOLVED:composition")
    c["composition"] = {
        "required": True,
        "state": "warranted",
        "basis": ["atom:comparison", "atom:temporal"],
    }
    cases.append(c)

    c = mutate("B-H-COMP-MISMATCH", "required_composition_subject_mismatch", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:composition")
    c["composition"] = {
        "required": True,
        "state": "warranted",
        "basis": ["atom:comparison", "atom:temporal"],
        "authority_subject_id": SUBJECT_B,
    }
    cases.append(c)

    c = mutate("B-H-COMP-UNK", "bound_composition_unresolved", "UNRESOLVED", "COMPOSITION_UNRESOLVED")
    c["composition"] = {
        "required": True,
        "state": "unresolved",
        "basis": ["atom:comparison", "atom:temporal"],
        "authority_subject_id": SUBJECT_A,
    }
    cases.append(c)

    c = mutate("B-H-COMP-REJ", "bound_composition_rejected", "REJECTED", "COMPOSITION_REJECTED")
    c["composition"] = {
        "required": True,
        "state": "rejected",
        "basis": ["atom:comparison", "atom:temporal"],
        "authority_subject_id": SUBJECT_A,
    }
    cases.append(c)

    c = mutate("B-H-COMP-OPTIONAL", "optional_composition_needs_no_binding", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["composition"] = {"required": False, "state": "not_applicable", "basis": []}
    cases.append(c)

    c = mutate("B-H-APER-GOOD", "required_aperture_bound_sufficient", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["aperture"] = {"required": True, "state": "sufficient", "authority_subject_id": SUBJECT_A}
    cases.append(c)

    c = mutate("B-H-APER-MISS", "required_aperture_missing_subject", "UNRESOLVED", "AUTHORITY_SUBJECT_BINDING_UNRESOLVED:aperture")
    c["aperture"] = {"required": True, "state": "sufficient"}
    cases.append(c)

    c = mutate("B-H-APER-MISMATCH", "required_aperture_subject_mismatch", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:aperture")
    c["aperture"] = {"required": True, "state": "sufficient", "authority_subject_id": SUBJECT_B}
    cases.append(c)

    c = mutate("B-H-APER-UNK", "bound_aperture_unresolved", "UNRESOLVED", "APERTURE_UNRESOLVED")
    c["aperture"] = {"required": True, "state": "unknown", "authority_subject_id": SUBJECT_A}
    cases.append(c)

    c = mutate("B-H-APER-OPTIONAL", "optional_aperture_needs_no_binding", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["aperture"] = {"required": False, "state": "not_applicable"}
    cases.append(c)

    c = mutate("B-H-PREC-PROP", "precedence_proposal_before_assertion", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:proposal")
    c["proposal"]["authority_subject_id"] = SUBJECT_B
    c["assertion"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("B-H-PREC-ASSERT", "precedence_assertion_before_operator", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:assertion")
    c["assertion"]["authority_subject_id"] = SUBJECT_B
    c["operator"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("B-H-PREC-OP", "precedence_operator_before_field", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:operator")
    c["operator"]["authority_subject_id"] = SUBJECT_B
    c["field_warrants"]["comparison_direction"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("B-H-PREC-FIELD", "precedence_first_required_field_before_composition", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:field:comparison_direction")
    c["field_warrants"]["comparison_direction"]["authority_subject_id"] = SUBJECT_B
    c["composition"] = {
        "required": True,
        "state": "warranted",
        "basis": ["atom:a"],
        "authority_subject_id": SUBJECT_B,
    }
    cases.append(c)

    c = mutate("B-H-PREC-COMP", "precedence_composition_before_aperture", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:composition")
    c["composition"] = {
        "required": True,
        "state": "warranted",
        "basis": ["atom:a"],
        "authority_subject_id": SUBJECT_B,
    }
    c["aperture"] = {"required": True, "state": "sufficient", "authority_subject_id": SUBJECT_B}
    cases.append(c)

    c = mutate("B-H-BANK-WARRANTED", "irrelevant_bank_growth_on_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["instrument_ids"].extend([f"measurement:irrelevant:prospective:{i}" for i in range(1, 8)])
    c["reader_agreement_count"] = 8
    cases.append(c)

    c = mutate("B-H-BANK-UNRESOLVED", "irrelevant_bank_growth_on_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    c["instrument_ids"].extend([f"measurement:agree:prospective:{i}" for i in range(1, 8)])
    c["reader_agreement_count"] = 8
    cases.append(c)

    return cases
