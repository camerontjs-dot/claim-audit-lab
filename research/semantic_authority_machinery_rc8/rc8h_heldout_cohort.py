from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rc8f_heldout_cohort import fresh_base


SOURCE_A = "source:rc8h:prospective:omega"
SOURCE_B = "source:rc8h:prospective:sigma"
BUNDLE_A = "bundle:rc8h:prospective:omega"
BUNDLE_B = "bundle:rc8h:prospective:sigma"
PASSAGE_A = "passage:rc8h:omega:117"
PASSAGE_B = "passage:rc8h:omega:118"
ATOM_A = "atom:rc8h:omega:comparison-117"
ATOM_B = "atom:rc8h:omega:comparison-118"
ADMITTED_SPAN = [75, 135]


def heldout_base() -> dict[str, Any]:
    case = deepcopy(fresh_base())
    case["case_id"] = "H-H-BASE"
    case["mutation_axis"] = "fresh_contract_b_segment_bound_positive"
    case["expected_authority"] = "WARRANTED"
    case["expected_reason"] = "ALL_REQUIRED_WARRANT_ESTABLISHED"
    case["raw_source_id"] = SOURCE_A
    case["authority_subject_source_id"] = SOURCE_A
    case["raw_bundle_id"] = BUNDLE_A
    case["authority_subject_bundle_id"] = BUNDLE_A
    case["raw_passage_id"] = PASSAGE_A
    case["authority_subject_passage_id"] = PASSAGE_A
    case["admitted_passage_span"] = list(ADMITTED_SPAN)
    case["target_atom_id"] = ATOM_A
    case["authority_subject_atom_id"] = ATOM_A
    case["reader_agreement_count"] = 3
    case["instrument_ids"] = ["measurement:rc8h:prospective:1"]
    return case


def mutate(case_id: str, axis: str, expected: str, reason: str) -> dict[str, Any]:
    case = deepcopy(heldout_base())
    case["case_id"] = case_id
    case["mutation_axis"] = axis
    case["expected_authority"] = expected
    case["expected_reason"] = reason
    return case


def build_rc8h_heldout_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [heldout_base()]

    c = mutate("H-H-EXEC", "execution_precedes_all_bindings", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    for key in ("authority_subject_source_id", "raw_bundle_id", "authority_subject_bundle_id", "raw_passage_id", "authority_subject_passage_id", "admitted_passage_span", "target_atom_id", "authority_subject_atom_id"):
        c.pop(key, None)
    cases.append(c)

    c = mutate("H-H-EVIDENCE", "evidence_rejection_precedes_all_bindings", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    for key in ("authority_subject_source_id", "raw_bundle_id", "authority_subject_bundle_id", "raw_passage_id", "authority_subject_passage_id", "admitted_passage_span", "target_atom_id", "authority_subject_atom_id"):
        c.pop(key, None)
    cases.append(c)

    c = mutate("H-H-SOURCE-MISSING", "source_binding_missing_precedes_segment", "UNRESOLVED", "AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED")
    c.pop("authority_subject_source_id")
    c.pop("authority_subject_bundle_id")
    cases.append(c)

    c = mutate("H-H-SOURCE-MISMATCH", "source_mismatch_precedes_segment_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_SOURCE_MISMATCH")
    c["authority_subject_source_id"] = SOURCE_B
    c["authority_subject_bundle_id"] = BUNDLE_B
    c["authority_subject_passage_id"] = PASSAGE_B
    cases.append(c)

    c = mutate("H-H-BUNDLE-MISSING", "bundle_binding_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED")
    c.pop("authority_subject_bundle_id")
    cases.append(c)

    c = mutate("H-H-BUNDLE-MISMATCH", "bundle_mismatch_precedes_passage_and_atom", "REJECTED", "AUTHORITY_EVIDENCE_BUNDLE_MISMATCH")
    c["authority_subject_bundle_id"] = BUNDLE_B
    c["authority_subject_passage_id"] = PASSAGE_B
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("H-H-PASSAGE-MISSING", "passage_binding_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED")
    c.pop("raw_passage_id")
    cases.append(c)

    c = mutate("H-H-PASSAGE-MISMATCH", "passage_mismatch_precedes_atom", "REJECTED", "AUTHORITY_EVIDENCE_PASSAGE_MISMATCH")
    c["authority_subject_passage_id"] = PASSAGE_B
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("H-H-SPAN-MISSING", "admitted_passage_span_missing", "UNRESOLVED", "ADMITTED_PASSAGE_SPAN_UNRESOLVED")
    c.pop("admitted_passage_span")
    cases.append(c)

    c = mutate("H-H-SPAN-REVERSED", "admitted_passage_span_reversed", "UNRESOLVED", "ADMITTED_PASSAGE_SPAN_UNRESOLVED")
    c["admitted_passage_span"] = [135, 75]
    cases.append(c)

    c = mutate("H-H-SPAN-NONINT", "admitted_passage_span_non_integer", "UNRESOLVED", "ADMITTED_PASSAGE_SPAN_UNRESOLVED")
    c["admitted_passage_span"] = [75, "135"]
    cases.append(c)

    c = mutate("H-H-PROPOSAL-BOUNDARY", "proposal_exact_admitted_passage_boundary", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["proposal"]["source_span"] = list(ADMITTED_SPAN)
    cases.append(c)

    c = mutate("H-H-PROPOSAL-LEFT", "proposal_left_outside_passage_inside_operator", "REJECTED", "SOURCE_SPAN_OUTSIDE_ADMITTED_PASSAGE")
    c["proposal"]["source_span"] = [70, 100]
    cases.append(c)

    c = mutate("H-H-PROPOSAL-RIGHT", "proposal_right_outside_passage_inside_operator", "REJECTED", "SOURCE_SPAN_OUTSIDE_ADMITTED_PASSAGE")
    c["proposal"]["source_span"] = [110, 140]
    cases.append(c)

    field = "comparison_direction"
    c = mutate("H-H-FIELD-BOUNDARY", "required_field_exact_admitted_passage_boundary", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["field_warrants"][field]["span"] = list(ADMITTED_SPAN)
    cases.append(c)

    c = mutate("H-H-FIELD-LEFT", "required_field_left_outside_passage_inside_operator", "REJECTED", f"FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:{field}")
    c["field_warrants"][field]["span"] = [70, 80]
    cases.append(c)

    c = mutate("H-H-FIELD-RIGHT", "required_field_right_outside_passage_inside_operator", "REJECTED", f"FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:{field}")
    c["field_warrants"][field]["span"] = [130, 140]
    cases.append(c)

    c = mutate("H-H-FIELD-SPAN-MISSING", "invalid_field_span_delegates_to_parent", "UNRESOLVED", f"FIELD_SUPPORT_SPAN_UNRESOLVED:{field}")
    c["field_warrants"][field].pop("span")
    cases.append(c)

    c = mutate("H-H-FIELD-ABSENT", "missing_required_field_delegates_to_parent", "REJECTED", f"FIELD_REQUIRED_ABSENT:{field}")
    c["field_warrants"].pop(field)
    cases.append(c)

    c = mutate("H-H-ATOM", "valid_segment_preserves_atom_mismatch", "REJECTED", "AUTHORITY_ATOM_IDENTITY_MISMATCH")
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("H-H-EXTRACT", "valid_segment_preserves_extraction_unresolved", "UNRESOLVED", f"FIELD_EXTRACTION_UNRESOLVED:{field}")
    c["field_warrants"][field]["status"] = "extraction_unresolved"
    c["field_warrants"][field]["value"] = None
    cases.append(c)

    c = mutate("H-H-COMP", "valid_segment_required_composition_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    subject = c["authority_subject_id"]
    c["composition"] = {
        "required": True,
        "state": "warranted",
        "basis": [ATOM_A, "atom:rc8h:omega:temporal-117"],
        "authority_subject_id": subject,
    }
    cases.append(c)

    c = mutate("H-H-APER", "valid_segment_preserves_aperture_unresolved", "UNRESOLVED", "APERTURE_UNRESOLVED")
    c["aperture"] = {"required": True, "state": "unknown", "authority_subject_id": c["authority_subject_id"]}
    cases.append(c)

    c = mutate("H-H-BANK-WARRANTED", "irrelevant_bank_growth_segment_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["reader_agreement_count"] = 31
    c["instrument_ids"].extend([f"measurement:rc8h:irrelevant:{i}" for i in range(2, 32)])
    cases.append(c)

    c = mutate("H-H-BANK-UNRESOLVED", "irrelevant_bank_growth_segment_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    c["reader_agreement_count"] = 31
    c["instrument_ids"].extend([f"measurement:rc8h:agree:{i}" for i in range(2, 32)])
    cases.append(c)

    return cases
