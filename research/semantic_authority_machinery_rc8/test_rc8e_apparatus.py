from __future__ import annotations

from .rc8e_cohort import ATOM_A, ATOM_B, SOURCE, build_rc8e_cases


def test_rc8e_structure_is_frozen_and_candidate_blind() -> None:
    cases = build_rc8e_cases()
    assert len(cases) == 10
    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))

    states = {case["expected_authority"] for case in cases}
    assert {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"} <= states

    base = next(case for case in cases if case["case_id"] == "E-BASE")
    transplant = next(case for case in cases if case["case_id"] == "E-TRANSPLANT")

    assert base["raw_source_id"] == SOURCE
    assert base["authority_subject_source_id"] == SOURCE
    assert base["target_atom_id"] == ATOM_A
    assert base["authority_subject_atom_id"] == ATOM_A

    assert transplant["raw_source_id"] == SOURCE
    assert transplant["authority_subject_source_id"] == SOURCE
    assert transplant["target_atom_id"] == ATOM_A
    assert transplant["authority_subject_atom_id"] == ATOM_B

    # The transplantation case must not be detectable by semantic value differences.
    assert transplant["proposal"]["fields"] == base["proposal"]["fields"]
    assert transplant["proposal"]["source_span"] == base["proposal"]["source_span"]
    assert transplant["operator"]["domain"] == base["operator"]["domain"]
    assert transplant["operator"]["governed_span"] == base["operator"]["governed_span"]
    assert {
        key: (receipt["status"], receipt["value"], receipt["span"])
        for key, receipt in transplant["field_warrants"].items()
    } == {
        key: (receipt["status"], receipt["value"], receipt["span"])
        for key, receipt in base["field_warrants"].items()
    }


def test_rc8e_missing_bindings_and_bank_controls() -> None:
    cases = {case["case_id"]: case for case in build_rc8e_cases()}
    assert "target_atom_id" not in cases["E-TARGET-MISSING"]
    assert "authority_subject_atom_id" not in cases["E-SUBJECT-ATOM-MISSING"]

    base = cases["E-BASE"]
    bank = cases["E-BANK-WARRANTED"]
    assert bank["target_atom_id"] == base["target_atom_id"]
    assert bank["authority_subject_atom_id"] == base["authority_subject_atom_id"]
    assert bank["proposal"] == base["proposal"]
    assert bank["reader_agreement_count"] > base["reader_agreement_count"]
    assert len(bank["instrument_ids"]) > len(base["instrument_ids"])
