from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rc8h_heldout_cohort import heldout_base


SOURCE_A = "source:rc8j:prospective:kappa"
SOURCE_B = "source:rc8j:prospective:lambda"
BUNDLE_A = "bundle:rc8j:prospective:kappa"
BUNDLE_B = "bundle:rc8j:prospective:lambda"
PASSAGE_A = "passage:rc8j:kappa:207"
PASSAGE_B = "passage:rc8j:kappa:208"
CLAIM_A = "claim:rc8j:kappa:207"
CLAIM_B = "claim:rc8j:kappa:208"
ATOM_A = "atom:rc8j:kappa:comparison-207"
ATOM_B = "atom:rc8j:kappa:comparison-208"
ADMITTED_SPAN = [72, 138]


def prospective_base() -> dict[str, Any]:
    case = deepcopy(heldout_base())
    case["case_id"] = "J-H-BASE"
    case["mutation_axis"] = "fresh_full_claim_bound_positive"
    case["expected_authority"] = "WARRANTED"
    case["expected_reason"] = "ALL_REQUIRED_WARRANT_ESTABLISHED"
    case["raw_source_id"] = SOURCE_A
    case["authority_subject_source_id"] = SOURCE_A
    case["raw_bundle_id"] = BUNDLE_A
    case["authority_subject_bundle_id"] = BUNDLE_A
    case["raw_passage_id"] = PASSAGE_A
    case["authority_subject_passage_id"] = PASSAGE_A
    case["admitted_passage_span"] = list(ADMITTED_SPAN)
    case["raw_claim_id"] = CLAIM_A
    case["authority_subject_claim_id"] = CLAIM_A
    case["target_atom_id"] = ATOM_A
    case["authority_subject_atom_id"] = ATOM_A
    case["reader_agreement_count"] = 2
    case["instrument_ids"] = ["measurement:rc8j:prospective:1"]
    return case


def mutate(case_id: str, axis: str, expected: str, reason: str) -> dict[str, Any]:
    case = deepcopy(prospective_base())
    case["case_id"] = case_id
    case["mutation_axis"] = axis
    case["expected_authority"] = expected
    case["expected_reason"] = reason
    return case


def build_rc8j_heldout_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [prospective_base()]

    c = mutate("J-H-EXEC", "execution_precedes_full_identity_chain", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    for key in ("authority_subject_source_id", "raw_bundle_id", "authority_subject_bundle_id", "raw_passage_id", "authority_subject_passage_id", "admitted_passage_span", "raw_claim_id", "authority_subject_claim_id", "target_atom_id", "authority_subject_atom_id"):
        c.pop(key, None)
    cases.append(c)

    c = mutate("J-H-EVIDENCE", "evidence_precedes_full_identity_chain", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    for key in ("authority_subject_source_id", "raw_bundle_id", "authority_subject_bundle_id", "raw_passage_id", "authority_subject_passage_id", "admitted_passage_span", "raw_claim_id", "authority_subject_claim_id", "target_atom_id", "authority_subject_atom_id"):
        c.pop(key, None)
    cases.append(c)

    c = mutate("J-H-SOURCE-MISSING", "source_binding_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED")
    c.pop("authority_subject_source_id")
    cases.append(c)

    c = mutate("J-H-SOURCE-MISMATCH", "source_mismatch_precedes_bundle_passage_claim_atom", "REJECTED", "AUTHORITY_EVIDENCE_SOURCE_MISMATCH")
    c["authority_subject_source_id"] = SOURCE_B
    c["authority_subject_bundle_id"] = BUNDLE_B
    c["authority_subject_passage_id"] = PASSAGE_B
    c["authority_subject_claim_id"] = CLAIM_B
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("J-H-BUNDLE-MISSING", "bundle_binding_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED")
    c.pop("authority_subject_bundle_id")
    cases.append(c)

    c = mutate("J-H-BUNDLE-MISMATCH", "bundle_mismatch_precedes_passage_claim_atom", "REJECTED", "AUTHORITY_EVIDENCE_BUNDLE_MISMATCH")
    c["authority_subject_bundle_id"] = BUNDLE_B
    c["authority_subject_passage_id"] = PASSAGE_B
    c["authority_subject_claim_id"] = CLAIM_B
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("J-H-PASSAGE-MISSING", "passage_binding_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED")
    c.pop("authority_subject_passage_id")
    cases.append(c)

    c = mutate("J-H-PASSAGE-MISMATCH", "passage_mismatch_precedes_claim_atom", "REJECTED", "AUTHORITY_EVIDENCE_PASSAGE_MISMATCH")
    c["authority_subject_passage_id"] = PASSAGE_B
    c["authority_subject_claim_id"] = CLAIM_B
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("J-H-SPAN-MISSING", "admitted_passage_span_missing", "UNRESOLVED", "ADMITTED_PASSAGE_SPAN_UNRESOLVED")
    c.pop("admitted_passage_span")
    cases.append(c)

    c = mutate("J-H-SPAN-MALFORMED", "admitted_passage_span_malformed", "UNRESOLVED", "ADMITTED_PASSAGE_SPAN_UNRESOLVED")
    c["admitted_passage_span"] = [138, 72]
    cases.append(c)

    c = mutate("J-H-RAW-CLAIM-MISSING", "raw_claim_identity_missing", "UNRESOLVED", "AUTHORITY_CLAIM_BINDING_UNRESOLVED")
    c.pop("raw_claim_id")
    cases.append(c)

    c = mutate("J-H-SUBJECT-CLAIM-MISSING", "authority_claim_identity_missing", "UNRESOLVED", "AUTHORITY_CLAIM_BINDING_UNRESOLVED")
    c.pop("authority_subject_claim_id")
    cases.append(c)

    c = mutate("J-H-CLAIM-MISMATCH", "same_segment_atom_claim_mismatch", "REJECTED", "AUTHORITY_CLAIM_MISMATCH")
    c["authority_subject_claim_id"] = CLAIM_B
    cases.append(c)

    c = mutate("J-H-WHOLE-RECEIPT-TRANSPLANT", "whole_receipt_cross_claim_transplant_same_material", "REJECTED", "AUTHORITY_CLAIM_MISMATCH")
    c["authority_subject_claim_id"] = CLAIM_B
    c["reader_agreement_count"] = 11
    c["instrument_ids"] = ["measurement:rc8j:transplanted"]
    cases.append(c)

    c = mutate("J-H-CLAIM-ATOM-PREC", "claim_mismatch_precedes_atom_mismatch", "REJECTED", "AUTHORITY_CLAIM_MISMATCH")
    c["authority_subject_claim_id"] = CLAIM_B
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("J-H-ATOM", "valid_claim_binding_preserves_atom_mismatch", "REJECTED", "AUTHORITY_ATOM_IDENTITY_MISMATCH")
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("J-H-PROPOSAL-LEFT", "proposal_outside_admitted_passage_inside_operator", "REJECTED", "SOURCE_SPAN_OUTSIDE_ADMITTED_PASSAGE")
    c["proposal"]["source_span"] = [68, 100]
    cases.append(c)

    field = "comparison_direction"
    c = mutate("J-H-FIELD-RIGHT", "field_support_outside_admitted_passage_inside_operator", "REJECTED", f"FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:{field}")
    c["field_warrants"][field]["span"] = [130, 142]
    cases.append(c)

    c = mutate("J-H-FIELD-SPAN-MISSING", "missing_field_span_delegates_to_parent", "UNRESOLVED", f"FIELD_SUPPORT_SPAN_UNRESOLVED:{field}")
    c["field_warrants"][field].pop("span")
    cases.append(c)

    c = mutate("J-H-FIELD-ABSENT", "missing_required_field_delegates_to_parent", "REJECTED", f"FIELD_REQUIRED_ABSENT:{field}")
    c["field_warrants"].pop(field)
    cases.append(c)

    c = mutate("J-H-FIELD-EXTRACT", "field_extraction_unresolved", "UNRESOLVED", f"FIELD_EXTRACTION_UNRESOLVED:{field}")
    c["field_warrants"][field]["status"] = "extraction_unresolved"
    c["field_warrants"][field]["value"] = None
    cases.append(c)

    c = mutate("J-H-FIELD-VALUE", "field_value_mismatch", "REJECTED", f"FIELD_VALUE_MISMATCH:{field}")
    c["proposal"]["fields"][field] = "less_equal"
    cases.append(c)

    c = mutate("J-H-COMP", "required_composition_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["composition"] = {
        "required": True,
        "state": "warranted",
        "basis": [ATOM_A, "atom:rc8j:kappa:temporal-207"],
        "authority_subject_id": c["authority_subject_id"],
    }
    cases.append(c)

    c = mutate("J-H-APER", "required_aperture_unresolved", "UNRESOLVED", "APERTURE_UNRESOLVED")
    c["aperture"] = {"required": True, "state": "unknown", "authority_subject_id": c["authority_subject_id"]}
    cases.append(c)

    c = mutate("J-H-SEMANTIC", "valid_identity_chain_semantic_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    cases.append(c)

    c = mutate("J-H-BANK-WARRANTED", "irrelevant_bank_growth_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["reader_agreement_count"] = 48
    c["instrument_ids"].extend([f"measurement:rc8j:irrelevant:{i}" for i in range(2, 49)])
    cases.append(c)

    c = mutate("J-H-BANK-UNRESOLVED", "irrelevant_bank_growth_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    c["reader_agreement_count"] = 48
    c["instrument_ids"].extend([f"measurement:rc8j:agree:{i}" for i in range(2, 49)])
    cases.append(c)

    return cases
