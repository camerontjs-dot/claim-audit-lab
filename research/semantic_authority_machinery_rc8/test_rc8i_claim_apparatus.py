from __future__ import annotations

from .rc8i_claim_cohort import CLAIM_A, CLAIM_B, build_rc8i_cases


def test_rc8i_claim_falsifier_is_candidate_blind_and_discriminating() -> None:
    cases = build_rc8i_cases()
    assert len(cases) == 14
    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))

    by_id = {case["case_id"]: case for case in cases}
    base = by_id["I-BASE"]
    transplant = by_id["I-WHOLE-RECEIPT-TRANSPLANT"]

    assert base["raw_claim_id"] == CLAIM_A
    assert base["authority_subject_claim_id"] == CLAIM_A
    assert transplant["raw_claim_id"] == CLAIM_A
    assert transplant["authority_subject_claim_id"] == CLAIM_B

    for key in (
        "raw_source_id",
        "authority_subject_source_id",
        "raw_bundle_id",
        "authority_subject_bundle_id",
        "raw_passage_id",
        "authority_subject_passage_id",
        "admitted_passage_span",
        "target_atom_id",
        "authority_subject_atom_id",
        "proposal",
        "assertion",
        "operator",
        "field_warrants",
        "required_fields",
        "composition",
        "aperture",
    ):
        assert transplant[key] == base[key]

    assert by_id["I-CLAIM-MISMATCH"]["authority_subject_claim_id"] == CLAIM_B
    assert by_id["I-CLAIM-ATOM-PREC"]["authority_subject_claim_id"] == CLAIM_B
    assert by_id["I-CLAIM-ATOM-PREC"]["authority_subject_atom_id"] != base["authority_subject_atom_id"]


def test_rc8i_bank_controls_change_only_irrelevant_bank_inputs() -> None:
    cases = {case["case_id"]: case for case in build_rc8i_cases()}
    base = cases["I-BASE"]
    bank = cases["I-BANK-WARRANTED"]
    assert bank["raw_claim_id"] == base["raw_claim_id"]
    assert bank["authority_subject_claim_id"] == base["authority_subject_claim_id"]
    assert bank["proposal"] == base["proposal"]
    assert bank["reader_agreement_count"] > base["reader_agreement_count"]
    assert len(bank["instrument_ids"]) > len(base["instrument_ids"])
