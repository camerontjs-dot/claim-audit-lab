from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rc8f_heldout_cohort import ATOM_A, ATOM_B, SOURCE_A, SOURCE_B, fresh_base


BUNDLE_A = "bundle:rc8g:contract-b:A"
BUNDLE_B = "bundle:rc8g:contract-b:B"
PASSAGE_A = "passage:rc8g:A:042"
PASSAGE_B = "passage:rc8g:A:043"
ADMITTED_SPAN = [75, 135]


def segment_base() -> dict[str, Any]:
    case = deepcopy(fresh_base())
    case["case_id"] = "G-BASE"
    case["mutation_axis"] = "contract_b_segment_bound_positive"
    case["expected_authority"] = "WARRANTED"
    case["expected_reason"] = "ALL_REQUIRED_WARRANT_ESTABLISHED"
    case["raw_bundle_id"] = BUNDLE_A
    case["authority_subject_bundle_id"] = BUNDLE_A
    case["raw_passage_id"] = PASSAGE_A
    case["authority_subject_passage_id"] = PASSAGE_A
    case["admitted_passage_span"] = list(ADMITTED_SPAN)
    case["reader_agreement_count"] = 4
    case["instrument_ids"] = ["measurement:rc8g:segment:1"]
    return case


def mutate(case_id: str, axis: str, expected: str, reason: str) -> dict[str, Any]:
    case = deepcopy(segment_base())
    case["case_id"] = case_id
    case["mutation_axis"] = axis
    case["expected_authority"] = expected
    case["expected_reason"] = reason
    return case


def build_rc8g_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [segment_base()]

    c = mutate("G-EXEC", "execution_precedes_segment_binding", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    c.pop("raw_bundle_id")
    c.pop("authority_subject_bundle_id")
    c.pop("raw_passage_id")
    c.pop("authority_subject_passage_id")
    cases.append(c)

    c = mutate("G-EVIDENCE", "evidence_rejection_precedes_segment_binding", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    c.pop("raw_bundle_id")
    c.pop("authority_subject_bundle_id")
    c.pop("raw_passage_id")
    c.pop("authority_subject_passage_id")
    cases.append(c)

    c = mutate("G-RAW-BUNDLE-MISSING", "raw_bundle_identity_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED")
    c.pop("raw_bundle_id")
    cases.append(c)

    c = mutate("G-SUBJECT-BUNDLE-MISSING", "authority_bundle_identity_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED")
    c.pop("authority_subject_bundle_id")
    cases.append(c)

    c = mutate("G-BUNDLE-MISMATCH", "contract_b_bundle_identity_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_BUNDLE_MISMATCH")
    c["authority_subject_bundle_id"] = BUNDLE_B
    cases.append(c)

    c = mutate("G-RAW-PASSAGE-MISSING", "raw_passage_identity_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED")
    c.pop("raw_passage_id")
    cases.append(c)

    c = mutate("G-SUBJECT-PASSAGE-MISSING", "authority_passage_identity_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED")
    c.pop("authority_subject_passage_id")
    cases.append(c)

    c = mutate("G-PASSAGE-MISMATCH", "same_bundle_source_passage_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_PASSAGE_MISMATCH")
    c["authority_subject_passage_id"] = PASSAGE_B
    cases.append(c)

    c = mutate("G-PROPOSAL-SPAN", "proposal_outside_admitted_passage_inside_operator", "REJECTED", "SOURCE_SPAN_OUTSIDE_ADMITTED_PASSAGE")
    c["proposal"]["source_span"] = [136, 150]
    cases.append(c)

    field = "comparison_direction"
    c = mutate("G-FIELD-SPAN", "field_support_outside_admitted_passage_inside_operator", "REJECTED", f"FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:{field}")
    c["field_warrants"][field]["span"] = [60, 70]
    cases.append(c)

    c = mutate("G-SOURCE-PREC", "source_mismatch_precedes_passage_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_SOURCE_MISMATCH")
    c["raw_source_id"] = SOURCE_B
    c["authority_subject_passage_id"] = PASSAGE_B
    cases.append(c)

    c = mutate("G-PASSAGE-PREC", "passage_mismatch_precedes_atom_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_PASSAGE_MISMATCH")
    c["authority_subject_passage_id"] = PASSAGE_B
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("G-ATOM-CONTROL", "valid_segment_preserves_atom_mismatch", "REJECTED", "AUTHORITY_ATOM_IDENTITY_MISMATCH")
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("G-SEMANTIC-UNRESOLVED", "valid_segment_preserves_semantic_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    cases.append(c)

    c = mutate("G-BANK-WARRANTED", "segment_binding_bank_growth_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["reader_agreement_count"] = 24
    c["instrument_ids"].extend([f"measurement:rc8g:irrelevant:{i}" for i in range(2, 25)])
    cases.append(c)

    c = mutate("G-BANK-UNRESOLVED", "segment_binding_bank_growth_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    c["reader_agreement_count"] = 24
    c["instrument_ids"].extend([f"measurement:rc8g:agree:{i}" for i in range(2, 25)])
    cases.append(c)

    return cases
