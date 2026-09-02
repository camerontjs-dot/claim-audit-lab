from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rc8b_heldout_cohort import base_case


SOURCE_A = "source:rc8d:gamma"
SOURCE_B = "source:rc8d:delta"
SUBJECT_A = "authority-subject:rc8d:gamma:atom-402"
SUBJECT_B = "authority-subject:rc8d:gamma:atom-909"


def anchored_base() -> dict[str, Any]:
    case = deepcopy(base_case())
    case["case_id"] = "D-H-BASE"
    case["mutation_axis"] = "fresh_source_anchor_positive"
    case["expected_authority"] = "WARRANTED"
    case["expected_reason"] = "ALL_REQUIRED_WARRANT_ESTABLISHED"
    case["raw_source_id"] = SOURCE_A
    case["authority_subject_source_id"] = SOURCE_A
    case["authority_subject_id"] = SUBJECT_A
    case["proposal"]["authority_subject_id"] = SUBJECT_A
    case["assertion"]["authority_subject_id"] = SUBJECT_A
    case["operator"]["authority_subject_id"] = SUBJECT_A
    for receipt in case["field_warrants"].values():
        receipt["authority_subject_id"] = SUBJECT_A
    if case["composition"]["required"]:
        case["composition"]["authority_subject_id"] = SUBJECT_A
    if case["aperture"]["required"]:
        case["aperture"]["authority_subject_id"] = SUBJECT_A
    case["reader_agreement_count"] = 2
    case["instrument_ids"] = ["measurement:rc8d:gamma:1"]
    return case


def mutate(case_id: str, axis: str, expected: str, reason: str) -> dict[str, Any]:
    case = deepcopy(anchored_base())
    case["case_id"] = case_id
    case["mutation_axis"] = axis
    case["expected_authority"] = expected
    case["expected_reason"] = reason
    return case


def build_rc8d_heldout_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [anchored_base()]

    c = mutate("D-H-EXEC", "execution_precedes_missing_source_anchor", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    c.pop("raw_source_id")
    c.pop("authority_subject_source_id")
    cases.append(c)

    c = mutate("D-H-EVIDENCE", "evidence_rejection_precedes_missing_source_anchor", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    c.pop("raw_source_id")
    c.pop("authority_subject_source_id")
    cases.append(c)

    c = mutate("D-H-RAW-MISSING", "raw_source_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED")
    c.pop("raw_source_id")
    cases.append(c)

    c = mutate("D-H-ANCHOR-MISSING", "subject_source_anchor_missing", "UNRESOLVED", "AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED")
    c.pop("authority_subject_source_id")
    cases.append(c)

    c = mutate("D-H-MISMATCH-A-B", "source_anchor_a_raw_b", "REJECTED", "AUTHORITY_EVIDENCE_SOURCE_MISMATCH")
    c["raw_source_id"] = SOURCE_B
    cases.append(c)

    c = mutate("D-H-MISMATCH-B-A", "source_anchor_b_raw_a", "REJECTED", "AUTHORITY_EVIDENCE_SOURCE_MISMATCH")
    c["authority_subject_source_id"] = SOURCE_B
    cases.append(c)

    c = mutate("D-H-SOURCE-PRECEDENCE", "source_mismatch_precedes_subreceipt_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_SOURCE_MISMATCH")
    c["raw_source_id"] = SOURCE_B
    c["proposal"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("D-H-PROPOSAL-SUBJECT", "valid_source_anchor_with_proposal_subject_mismatch", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:proposal")
    c["proposal"]["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("D-H-SUBORDINATE-BUNDLE", "valid_source_anchor_with_all_subordinate_subjects_substituted", "REJECTED", "AUTHORITY_SUBJECT_MISMATCH:proposal")
    c["proposal"]["authority_subject_id"] = SUBJECT_B
    c["assertion"]["authority_subject_id"] = SUBJECT_B
    c["operator"]["authority_subject_id"] = SUBJECT_B
    for receipt in c["field_warrants"].values():
        receipt["authority_subject_id"] = SUBJECT_B
    cases.append(c)

    c = mutate("D-H-ASSERT-UNKNOWN", "anchored_source_assertion_unknown", "UNRESOLVED", "SOURCE_ASSERTION_UNRESOLVED")
    c["assertion"]["state"] = "unknown"
    cases.append(c)

    field = "comparison_direction"
    c = mutate("D-H-FIELD-EXTRACT", "anchored_field_extraction_unresolved", "UNRESOLVED", f"FIELD_EXTRACTION_UNRESOLVED:{field}")
    c["field_warrants"][field]["status"] = "extraction_unresolved"
    c["field_warrants"][field]["value"] = None
    cases.append(c)

    c = mutate("D-H-FIELD-MISMATCH", "anchored_field_value_mismatch", "REJECTED", f"FIELD_VALUE_MISMATCH:{field}")
    c["proposal"]["fields"][field] = "less_equal"
    cases.append(c)

    c = mutate("D-H-BANK-WARRANTED", "source_anchor_bank_growth_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["reader_agreement_count"] = 12
    c["instrument_ids"].extend([f"measurement:rc8d:irrelevant:{i}" for i in range(2, 13)])
    cases.append(c)

    c = mutate("D-H-BANK-UNRESOLVED", "source_anchor_bank_growth_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    c["reader_agreement_count"] = 12
    c["instrument_ids"].extend([f"measurement:rc8d:agree:{i}" for i in range(2, 13)])
    cases.append(c)

    return cases
