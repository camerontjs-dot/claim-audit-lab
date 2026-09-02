from __future__ import annotations

from .rc8h_heldout_cohort import ADMITTED_SPAN, ATOM_A, ATOM_B, BUNDLE_A, BUNDLE_B, PASSAGE_A, PASSAGE_B, SOURCE_A, SOURCE_B, build_rc8h_heldout_cases


def test_rc8h_heldout_structure_is_candidate_blind() -> None:
    cases = build_rc8h_heldout_cases()
    assert len(cases) == 26
    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))
    assert {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"} <= {case["expected_authority"] for case in cases}

    base = next(case for case in cases if case["case_id"] == "H-H-BASE")
    assert base["raw_source_id"] == SOURCE_A
    assert base["authority_subject_source_id"] == SOURCE_A
    assert base["raw_bundle_id"] == BUNDLE_A
    assert base["authority_subject_bundle_id"] == BUNDLE_A
    assert base["raw_passage_id"] == PASSAGE_A
    assert base["authority_subject_passage_id"] == PASSAGE_A
    assert base["target_atom_id"] == ATOM_A
    assert base["authority_subject_atom_id"] == ATOM_A
    assert base["admitted_passage_span"] == ADMITTED_SPAN

    source = next(case for case in cases if case["case_id"] == "H-H-SOURCE-MISMATCH")
    assert source["authority_subject_source_id"] == SOURCE_B
    assert source["authority_subject_bundle_id"] == BUNDLE_B
    assert source["authority_subject_passage_id"] == PASSAGE_B

    bundle = next(case for case in cases if case["case_id"] == "H-H-BUNDLE-MISMATCH")
    assert bundle["raw_bundle_id"] == BUNDLE_A
    assert bundle["authority_subject_bundle_id"] == BUNDLE_B
    assert bundle["authority_subject_passage_id"] == PASSAGE_B
    assert bundle["authority_subject_atom_id"] == ATOM_B

    passage = next(case for case in cases if case["case_id"] == "H-H-PASSAGE-MISMATCH")
    assert passage["raw_passage_id"] == PASSAGE_A
    assert passage["authority_subject_passage_id"] == PASSAGE_B
    assert passage["authority_subject_atom_id"] == ATOM_B


def test_rc8h_passage_boundary_mutations_are_discriminating() -> None:
    cases = {case["case_id"]: case for case in build_rc8h_heldout_cases()}
    op_span = cases["H-H-BASE"]["operator"]["governed_span"]

    assert cases["H-H-PROPOSAL-BOUNDARY"]["proposal"]["source_span"] == ADMITTED_SPAN
    assert cases["H-H-FIELD-BOUNDARY"]["field_warrants"]["comparison_direction"]["span"] == ADMITTED_SPAN

    for case_id in ("H-H-PROPOSAL-LEFT", "H-H-PROPOSAL-RIGHT"):
        span = cases[case_id]["proposal"]["source_span"]
        assert span[0] >= op_span[0] and span[1] <= op_span[1]
        assert span[0] < ADMITTED_SPAN[0] or span[1] > ADMITTED_SPAN[1]

    for case_id in ("H-H-FIELD-LEFT", "H-H-FIELD-RIGHT"):
        span = cases[case_id]["field_warrants"]["comparison_direction"]["span"]
        assert span[0] >= op_span[0] and span[1] <= op_span[1]
        assert span[0] < ADMITTED_SPAN[0] or span[1] > ADMITTED_SPAN[1]

    assert "span" not in cases["H-H-FIELD-SPAN-MISSING"]["field_warrants"]["comparison_direction"]
    assert "comparison_direction" not in cases["H-H-FIELD-ABSENT"]["field_warrants"]


def test_rc8h_bank_controls_do_not_change_authority_inputs() -> None:
    cases = {case["case_id"]: case for case in build_rc8h_heldout_cases()}
    base = cases["H-H-BASE"]
    bank = cases["H-H-BANK-WARRANTED"]
    assert bank["proposal"] == base["proposal"]
    assert bank["raw_bundle_id"] == base["raw_bundle_id"]
    assert bank["raw_passage_id"] == base["raw_passage_id"]
    assert bank["target_atom_id"] == base["target_atom_id"]
    assert bank["reader_agreement_count"] > base["reader_agreement_count"]
    assert len(bank["instrument_ids"]) > len(base["instrument_ids"])
