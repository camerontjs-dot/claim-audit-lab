from __future__ import annotations

from .rc8f_heldout_cohort import ATOM_A, ATOM_B, SOURCE_A, SOURCE_B, build_rc8f_heldout_cases


def test_rc8f_heldout_structure_is_candidate_blind() -> None:
    cases = build_rc8f_heldout_cases()
    assert len(cases) == 20
    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))

    states = {case["expected_authority"] for case in cases}
    assert {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"} <= states

    base = next(case for case in cases if case["case_id"] == "F-H-BASE")
    transplant = next(case for case in cases if case["case_id"] == "F-H-WHOLE-BUNDLE")
    source_mismatch = next(case for case in cases if case["case_id"] == "F-H-SOURCE-MISMATCH")

    assert base["raw_source_id"] == SOURCE_A
    assert base["authority_subject_source_id"] == SOURCE_A
    assert base["target_atom_id"] == ATOM_A
    assert base["authority_subject_atom_id"] == ATOM_A

    assert transplant["raw_source_id"] == SOURCE_A
    assert transplant["authority_subject_source_id"] == SOURCE_A
    assert transplant["target_atom_id"] == ATOM_A
    assert transplant["authority_subject_atom_id"] == ATOM_B
    assert transplant["proposal"]["fields"] == base["proposal"]["fields"]
    assert transplant["proposal"]["source_span"] == base["proposal"]["source_span"]

    assert source_mismatch["raw_source_id"] == SOURCE_B
    assert source_mismatch["authority_subject_source_id"] == SOURCE_A
    assert source_mismatch["authority_subject_atom_id"] == ATOM_B


def test_rc8f_bank_and_composition_controls() -> None:
    cases = {case["case_id"]: case for case in build_rc8f_heldout_cases()}
    base = cases["F-H-BASE"]
    bank = cases["F-H-BANK-WARRANTED"]
    assert bank["proposal"] == base["proposal"]
    assert bank["target_atom_id"] == base["target_atom_id"]
    assert bank["authority_subject_atom_id"] == base["authority_subject_atom_id"]
    assert bank["reader_agreement_count"] > base["reader_agreement_count"]
    assert len(bank["instrument_ids"]) > len(base["instrument_ids"])

    comp = cases["F-H-COMP-GOOD"]
    assert comp["composition"]["required"] is True
    assert comp["composition"]["state"] == "warranted"
    aperture = cases["F-H-APER-UNK"]
    assert aperture["aperture"]["required"] is True
    assert aperture["aperture"]["state"] == "unknown"
