from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rc8b_heldout_cohort import base_case


SOURCE_A = "source:rc8f:fresh:zeta"
SOURCE_B = "source:rc8f:fresh:eta"
ATOM_A = "atom:rc8f:fresh:zeta:A-314"
ATOM_B = "atom:rc8f:fresh:zeta:B-271"
SUBJECT_A = "authority-subject:rc8f:fresh:zeta:A-314"
SUBJECT_B = "authority-subject:rc8f:fresh:zeta:B-271"


def _bind_internal_subject(case: dict[str, Any], subject: str) -> None:
    case["authority_subject_id"] = subject
    case["proposal"]["authority_subject_id"] = subject
    case["assertion"]["authority_subject_id"] = subject
    case["operator"]["authority_subject_id"] = subject
    for receipt in case["field_warrants"].values():
        receipt["authority_subject_id"] = subject
    if case["composition"]["required"]:
        case["composition"]["authority_subject_id"] = subject
    if case["aperture"]["required"]:
        case["aperture"]["authority_subject_id"] = subject


def fresh_base() -> dict[str, Any]:
    case = deepcopy(base_case())
    case["case_id"] = "F-H-BASE"
    case["mutation_axis"] = "fresh_source_atom_bound_positive"
    case["expected_authority"] = "WARRANTED"
    case["expected_reason"] = "ALL_REQUIRED_WARRANT_ESTABLISHED"
    case["raw_source_id"] = SOURCE_A
    case["authority_subject_source_id"] = SOURCE_A
    case["target_atom_id"] = ATOM_A
    case["authority_subject_atom_id"] = ATOM_A
    _bind_internal_subject(case, SUBJECT_A)
    case["reader_agreement_count"] = 3
    case["instrument_ids"] = ["measurement:rc8f:fresh:1"]
    return case


def mutate(case_id: str, axis: str, expected: str, reason: str) -> dict[str, Any]:
    case = deepcopy(fresh_base())
    case["case_id"] = case_id
    case["mutation_axis"] = axis
    case["expected_authority"] = expected
    case["expected_reason"] = reason
    return case


def build_rc8f_heldout_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [fresh_base()]

    c = mutate("F-H-EXEC", "execution_precedes_source_and_atom_binding", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    c.pop("authority_subject_source_id")
    c.pop("target_atom_id")
    c.pop("authority_subject_atom_id")
    cases.append(c)

    c = mutate("F-H-EVIDENCE", "evidence_rejection_precedes_source_and_atom_binding", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    c.pop("authority_subject_source_id")
    c.pop("target_atom_id")
    c.pop("authority_subject_atom_id")
    cases.append(c)

    c = mutate("F-H-SOURCE-MISSING", "source_anchor_missing_before_atom_binding", "UNRESOLVED", "AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED")
    c.pop("authority_subject_source_id")
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("F-H-SOURCE-MISMATCH", "source_mismatch_precedes_atom_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_SOURCE_MISMATCH")
    c["raw_source_id"] = SOURCE_B
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("F-H-TARGET-MISSING", "fresh_target_atom_identity_missing", "UNRESOLVED", "AUTHORITY_ATOM_IDENTITY_BINDING_UNRESOLVED")
    c.pop("target_atom_id")
    cases.append(c)

    c = mutate("F-H-SUBJECT-ATOM-MISSING", "fresh_authority_atom_identity_missing", "UNRESOLVED", "AUTHORITY_ATOM_IDENTITY_BINDING_UNRESOLVED")
    c.pop("authority_subject_atom_id")
    cases.append(c)

    c = mutate("F-H-ATOM-MISMATCH", "fresh_same_source_atom_mismatch", "REJECTED", "AUTHORITY_ATOM_IDENTITY_MISMATCH")
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("F-H-WHOLE-BUNDLE", "fresh_same_source_whole_bundle_transplant", "REJECTED", "AUTHORITY_ATOM_IDENTITY_MISMATCH")
    c["authority_subject_atom_id"] = ATOM_B
    _bind_internal_subject(c, SUBJECT_B)
    cases.append(c)

    c = mutate("F-H-ATOM-PREC", "atom_mismatch_precedes_proposal_subject_mismatch", "REJECTED", "AUTHORITY_ATOM_IDENTITY_MISMATCH")
    c["authority_subject_atom_id"] = ATOM_B
    c["proposal"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("F-H-PROPOSAL", "valid_atom_binding_preserves_proposal_subject_rejection", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:proposal")
    c["proposal"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("F-H-ASSERT-UNK", "valid_atom_binding_preserves_assertion_unknown", "UNRESOLVED", "SOURCE_ASSERTION_UNRESOLVED")
    c["assertion"]["state"] = "unknown"
    cases.append(c)

    field = "comparison_direction"
    c = mutate("F-H-FIELD-EXTRACT", "valid_atom_binding_preserves_field_extraction_unresolved", "UNRESOLVED", f"FIELD_EXTRACTION_UNRESOLVED:{field}")
    c["field_warrants"][field]["status"] = "extraction_unresolved"
    c["field_warrants"][field]["value"] = None
    cases.append(c)

    c = mutate("F-H-FIELD-MISMATCH", "valid_atom_binding_preserves_field_value_mismatch", "REJECTED", f"FIELD_VALUE_MISMATCH:{field}")
    c["proposal"]["fields"][field] = "less_equal"
    cases.append(c)

    c = mutate("F-H-FIELD-SPAN", "valid_atom_binding_preserves_field_support_governance", "REJECTED", f"FIELD_SUPPORT_OUTSIDE_OPERATOR_GOVERNANCE:{field}")
    c["field_warrants"][field]["span"] = [161, 170]
    cases.append(c)

    c = mutate("F-H-COMP-GOOD", "valid_atom_binding_with_required_composition", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["composition"] = {
        "required": True,
        "state": "warranted",
        "basis": ["atom:rc8f:fresh:component-1", "atom:rc8f:fresh:component-2"],
        "authority_subject_id": SUBJECT_A,
    }
    cases.append(c)

    c = mutate("F-H-COMP-MISMATCH", "valid_atom_binding_preserves_composition_subject_mismatch", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:composition")
    c["composition"] = {
        "required": True,
        "state": "warranted",
        "basis": ["atom:rc8f:fresh:component-1"],
        "authority_subject_id": SUBJECT_B,
    }
    cases.append(c)

    c = mutate("F-H-APER-UNK", "valid_atom_binding_preserves_aperture_unresolved", "UNRESOLVED", "APERTURE_UNRESOLVED")
    c["aperture"] = {"required": True, "state": "unknown", "authority_subject_id": SUBJECT_A}
    cases.append(c)

    c = mutate("F-H-INAPPLICABLE", "valid_atom_binding_preserves_operator_inapplicable", "REJECTED", "OPERATOR_INAPPLICABLE")
    c["operator"]["applicability"] = "inapplicable"
    cases.append(c)

    c = mutate("F-H-BANK-WARRANTED", "fresh_atom_binding_bank_growth_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["reader_agreement_count"] = 20
    c["instrument_ids"].extend([f"measurement:rc8f:fresh:irrelevant:{i}" for i in range(2, 21)])
    cases.append(c)

    c = mutate("F-H-BANK-UNRESOLVED", "fresh_atom_binding_bank_growth_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    c["reader_agreement_count"] = 20
    c["instrument_ids"].extend([f"measurement:rc8f:fresh:agree:{i}" for i in range(2, 21)])
    cases.append(c)

    return cases
