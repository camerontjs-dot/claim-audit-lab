from __future__ import annotations

from .rc8d_heldout_cohort import build_rc8d_heldout_cases


def test_rc8d_heldout_structure_is_frozen_and_candidate_blind() -> None:
    cases = build_rc8d_heldout_cases()
    assert len(cases) == 15

    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))

    states = {case["expected_authority"] for case in cases}
    assert {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"} <= states

    axes = {case["mutation_axis"] for case in cases}
    required_axes = {
        "fresh_source_anchor_positive",
        "execution_precedes_missing_source_anchor",
        "evidence_rejection_precedes_missing_source_anchor",
        "raw_source_missing",
        "subject_source_anchor_missing",
        "source_anchor_a_raw_b",
        "source_anchor_b_raw_a",
        "source_mismatch_precedes_subreceipt_mismatch",
        "valid_source_anchor_with_proposal_subject_mismatch",
        "valid_source_anchor_with_all_subordinate_subjects_substituted",
        "anchored_source_assertion_unknown",
        "anchored_field_extraction_unresolved",
        "anchored_field_value_mismatch",
        "source_anchor_bank_growth_warranted",
        "source_anchor_bank_growth_unresolved",
    }
    assert axes == required_axes

    positive = next(case for case in cases if case["case_id"] == "D-H-BASE")
    assert positive["raw_source_id"] == positive["authority_subject_source_id"]

    missing_raw = next(case for case in cases if case["case_id"] == "D-H-RAW-MISSING")
    assert "raw_source_id" not in missing_raw
    assert missing_raw["authority_subject_source_id"] == positive["authority_subject_source_id"]

    missing_anchor = next(case for case in cases if case["case_id"] == "D-H-ANCHOR-MISSING")
    assert "authority_subject_source_id" not in missing_anchor
    assert missing_anchor["raw_source_id"] == positive["raw_source_id"]

    mismatch = next(case for case in cases if case["case_id"] == "D-H-MISMATCH-A-B")
    assert mismatch["raw_source_id"] != mismatch["authority_subject_source_id"]

    bundle = next(case for case in cases if case["case_id"] == "D-H-SUBORDINATE-BUNDLE")
    assert bundle["raw_source_id"] == bundle["authority_subject_source_id"]
    assert bundle["proposal"]["authority_subject_id"] != bundle["authority_subject_id"]


def test_rc8d_bank_growth_does_not_change_the_semantic_mutation() -> None:
    cases = {case["case_id"]: case for case in build_rc8d_heldout_cases()}
    base = cases["D-H-BASE"]
    bank = cases["D-H-BANK-WARRANTED"]

    assert bank["raw_source_id"] == base["raw_source_id"]
    assert bank["authority_subject_source_id"] == base["authority_subject_source_id"]
    assert bank["proposal"] == base["proposal"]
    assert bank["assertion"] == base["assertion"]
    assert bank["operator"] == base["operator"]
    assert bank["field_warrants"] == base["field_warrants"]
    assert bank["reader_agreement_count"] > base["reader_agreement_count"]
    assert len(bank["instrument_ids"]) > len(base["instrument_ids"])
