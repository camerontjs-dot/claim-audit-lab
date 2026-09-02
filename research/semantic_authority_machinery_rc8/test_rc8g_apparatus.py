from __future__ import annotations

from .rc8g_cohort import ADMITTED_SPAN, ATOM_A, BUNDLE_A, BUNDLE_B, PASSAGE_A, PASSAGE_B, SOURCE_A, build_rc8g_cases


def test_rc8g_structure_is_candidate_blind_and_contract_b_shaped() -> None:
    cases = build_rc8g_cases()
    assert len(cases) == 17
    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))

    states = {case["expected_authority"] for case in cases}
    assert {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"} <= states

    base = next(case for case in cases if case["case_id"] == "G-BASE")
    assert base["raw_bundle_id"] == BUNDLE_A
    assert base["authority_subject_bundle_id"] == BUNDLE_A
    assert base["raw_source_id"] == SOURCE_A
    assert base["raw_passage_id"] == PASSAGE_A
    assert base["authority_subject_passage_id"] == PASSAGE_A
    assert base["target_atom_id"] == ATOM_A
    assert base["admitted_passage_span"] == ADMITTED_SPAN

    bundle_mismatch = next(case for case in cases if case["case_id"] == "G-BUNDLE-MISMATCH")
    assert bundle_mismatch["raw_bundle_id"] == BUNDLE_A
    assert bundle_mismatch["authority_subject_bundle_id"] == BUNDLE_B
    assert bundle_mismatch["raw_passage_id"] == PASSAGE_A

    passage_mismatch = next(case for case in cases if case["case_id"] == "G-PASSAGE-MISMATCH")
    assert passage_mismatch["raw_bundle_id"] == BUNDLE_A
    assert passage_mismatch["raw_passage_id"] == PASSAGE_A
    assert passage_mismatch["authority_subject_passage_id"] == PASSAGE_B
    assert passage_mismatch["proposal"]["fields"] == base["proposal"]["fields"]


def test_rc8g_span_mutations_isolate_admitted_passage_boundary() -> None:
    cases = {case["case_id"]: case for case in build_rc8g_cases()}
    base = cases["G-BASE"]
    proposal = cases["G-PROPOSAL-SPAN"]
    field = cases["G-FIELD-SPAN"]

    governed_start, governed_end = base["operator"]["governed_span"]
    admitted_start, admitted_end = base["admitted_passage_span"]

    p_start, p_end = proposal["proposal"]["source_span"]
    assert governed_start <= p_start <= p_end <= governed_end
    assert p_start > admitted_end or p_end > admitted_end

    f_start, f_end = field["field_warrants"]["comparison_direction"]["span"]
    assert governed_start <= f_start <= f_end <= governed_end
    assert f_start < admitted_start or f_end > admitted_end


def test_rc8g_bank_growth_changes_only_non_authority_diagnostics() -> None:
    cases = {case["case_id"]: case for case in build_rc8g_cases()}
    base = cases["G-BASE"]
    bank = cases["G-BANK-WARRANTED"]
    assert bank["raw_bundle_id"] == base["raw_bundle_id"]
    assert bank["raw_passage_id"] == base["raw_passage_id"]
    assert bank["proposal"] == base["proposal"]
    assert bank["reader_agreement_count"] > base["reader_agreement_count"]
    assert len(bank["instrument_ids"]) > len(base["instrument_ids"])
