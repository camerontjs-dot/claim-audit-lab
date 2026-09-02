from __future__ import annotations

from copy import deepcopy
from typing import Any

from .rc8h_heldout_cohort import ATOM_A, ATOM_B, BUNDLE_A, BUNDLE_B, PASSAGE_A, PASSAGE_B, SOURCE_A, SOURCE_B, heldout_base


CLAIM_A = "claim:rc8i:contract-b:alpha"
CLAIM_B = "claim:rc8i:contract-b:beta"


def claim_base() -> dict[str, Any]:
    case = deepcopy(heldout_base())
    case["case_id"] = "I-BASE"
    case["mutation_axis"] = "contract_b_claim_bound_positive"
    case["expected_authority"] = "WARRANTED"
    case["expected_reason"] = "ALL_REQUIRED_WARRANT_ESTABLISHED"
    case["raw_claim_id"] = CLAIM_A
    case["authority_subject_claim_id"] = CLAIM_A
    return case


def mutate(case_id: str, axis: str, expected: str, reason: str) -> dict[str, Any]:
    case = deepcopy(claim_base())
    case["case_id"] = case_id
    case["mutation_axis"] = axis
    case["expected_authority"] = expected
    case["expected_reason"] = reason
    return case


def build_rc8i_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [claim_base()]

    c = mutate("I-EXEC", "execution_precedes_claim_binding", "NO_ASSESSMENT", "EXECUTION_FAILED")
    c["execution_state"] = "failed"
    c.pop("raw_claim_id")
    c.pop("authority_subject_claim_id")
    cases.append(c)

    c = mutate("I-EVIDENCE", "evidence_rejection_precedes_claim_binding", "REJECTED", "EVIDENCE_NOT_ADMITTED")
    c["evidence_admitted"] = False
    c.pop("raw_claim_id")
    c.pop("authority_subject_claim_id")
    cases.append(c)

    c = mutate("I-RAW-CLAIM-MISSING", "raw_claim_identity_missing", "UNRESOLVED", "AUTHORITY_CLAIM_BINDING_UNRESOLVED")
    c.pop("raw_claim_id")
    cases.append(c)

    c = mutate("I-SUBJECT-CLAIM-MISSING", "authority_claim_identity_missing", "UNRESOLVED", "AUTHORITY_CLAIM_BINDING_UNRESOLVED")
    c.pop("authority_subject_claim_id")
    cases.append(c)

    c = mutate("I-CLAIM-MISMATCH", "same_segment_atom_claim_mismatch", "REJECTED", "AUTHORITY_CLAIM_MISMATCH")
    c["authority_subject_claim_id"] = CLAIM_B
    cases.append(c)

    c = mutate("I-WHOLE-RECEIPT-TRANSPLANT", "whole_receipt_transplant_between_claims_same_semantics", "REJECTED", "AUTHORITY_CLAIM_MISMATCH")
    c["authority_subject_claim_id"] = CLAIM_B
    c["reader_agreement_count"] = 9
    c["instrument_ids"] = ["measurement:rc8i:transplanted"]
    cases.append(c)

    c = mutate("I-SOURCE-PREC", "source_mismatch_precedes_claim_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_SOURCE_MISMATCH")
    c["authority_subject_source_id"] = SOURCE_B
    c["authority_subject_claim_id"] = CLAIM_B
    cases.append(c)

    c = mutate("I-BUNDLE-PREC", "bundle_mismatch_precedes_claim_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_BUNDLE_MISMATCH")
    c["authority_subject_bundle_id"] = BUNDLE_B
    c["authority_subject_claim_id"] = CLAIM_B
    cases.append(c)

    c = mutate("I-PASSAGE-PREC", "passage_mismatch_precedes_claim_mismatch", "REJECTED", "AUTHORITY_EVIDENCE_PASSAGE_MISMATCH")
    c["authority_subject_passage_id"] = PASSAGE_B
    c["authority_subject_claim_id"] = CLAIM_B
    cases.append(c)

    c = mutate("I-CLAIM-ATOM-PREC", "claim_mismatch_precedes_atom_mismatch", "REJECTED", "AUTHORITY_CLAIM_MISMATCH")
    c["authority_subject_claim_id"] = CLAIM_B
    c["authority_subject_atom_id"] = ATOM_B
    cases.append(c)

    c = mutate("I-SEMANTIC-UNRESOLVED", "valid_claim_binding_preserves_semantic_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    cases.append(c)

    c = mutate("I-BANK-WARRANTED", "claim_binding_bank_growth_warranted", "WARRANTED", "ALL_REQUIRED_WARRANT_ESTABLISHED")
    c["reader_agreement_count"] = 40
    c["instrument_ids"].extend([f"measurement:rc8i:irrelevant:{i}" for i in range(2, 41)])
    cases.append(c)

    c = mutate("I-BANK-UNRESOLVED", "claim_binding_bank_growth_unresolved", "UNRESOLVED", "OPERATOR_APPLICABILITY_UNKNOWN")
    c["operator"]["applicability"] = "unknown"
    c["reader_agreement_count"] = 40
    c["instrument_ids"].extend([f"measurement:rc8i:agree:{i}" for i in range(2, 41)])
    cases.append(c)

    return cases
