from __future__ import annotations

from .rc8j_heldout_cohort import ADMITTED_SPAN, ATOM_A, ATOM_B, BUNDLE_A, BUNDLE_B, CLAIM_A, CLAIM_B, PASSAGE_A, PASSAGE_B, SOURCE_A, SOURCE_B, build_rc8j_heldout_cases


def test_rc8j_heldout_is_candidate_blind_and_complete() -> None:
    cases = build_rc8j_heldout_cases()
    assert len(cases) == 28
    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))
    assert {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"} <= {case["expected_authority"] for case in cases}

    by_id = {case["case_id"]: case for case in cases}
    base = by_id["J-H-BASE"]
    assert base["raw_source_id"] == SOURCE_A
    assert base["authority_subject_source_id"] == SOURCE_A
    assert base["raw_bundle_id"] == BUNDLE_A
    assert base["authority_subject_bundle_id"] == BUNDLE_A
    assert base["raw_passage_id"] == PASSAGE_A
    assert base["authority_subject_passage_id"] == PASSAGE_A
    assert base["raw_claim_id"] == CLAIM_A
    assert base["authority_subject_claim_id"] == CLAIM_A
    assert base["target_atom_id"] == ATOM_A
    assert base["authority_subject_atom_id"] == ATOM_A
    assert base["admitted_passage_span"] == ADMITTED_SPAN

    source = by_id["J-H-SOURCE-MISMATCH"]
    assert source["authority_subject_source_id"] == SOURCE_B
    assert source["authority_subject_bundle_id"] == BUNDLE_B
    assert source["authority_subject_passage_id"] == PASSAGE_B
    assert source["authority_subject_claim_id"] == CLAIM_B
    assert source["authority_subject_atom_id"] == ATOM_B

    bundle = by_id["J-H-BUNDLE-MISMATCH"]
    assert bundle["authority_subject_bundle_id"] == BUNDLE_B
    assert bundle["authority_subject_passage_id"] == PASSAGE_B
    assert bundle["authority_subject_claim_id"] == CLAIM_B
    assert bundle["authority_subject_atom_id"] == ATOM_B

    passage = by_id["J-H-PASSAGE-MISMATCH"]
    assert passage["authority_subject_passage_id"] == PASSAGE_B
    assert passage["authority_subject_claim_id"] == CLAIM_B
    assert passage["authority_subject_atom_id"] == ATOM_B


def test_rc8j_cross_claim_transplant_preserves_authority_material() -> None:
    cases = {case["case_id"]: case for case in build_rc8j_heldout_cases()}
    base = cases["J-H-BASE"]
    transplant = cases["J-H-WHOLE-RECEIPT-TRANSPLANT"]

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

    claim_atom = cases["J-H-CLAIM-ATOM-PREC"]
    assert claim_atom["authority_subject_claim_id"] == CLAIM_B
    assert claim_atom["authority_subject_atom_id"] == ATOM_B


def test_rc8j_boundary_and_bank_controls_are_discriminating() -> None:
    cases = {case["case_id"]: case for case in build_rc8j_heldout_cases()}
    base = cases["J-H-BASE"]
    op_span = base["operator"]["governed_span"]

    proposal = cases["J-H-PROPOSAL-LEFT"]["proposal"]["source_span"]
    assert proposal[0] >= op_span[0] and proposal[1] <= op_span[1]
    assert proposal[0] < ADMITTED_SPAN[0]

    field_span = cases["J-H-FIELD-RIGHT"]["field_warrants"]["comparison_direction"]["span"]
    assert field_span[0] >= op_span[0] and field_span[1] <= op_span[1]
    assert field_span[1] > ADMITTED_SPAN[1]

    bank = cases["J-H-BANK-WARRANTED"]
    assert bank["proposal"] == base["proposal"]
    assert bank["raw_claim_id"] == base["raw_claim_id"]
    assert bank["authority_subject_claim_id"] == base["authority_subject_claim_id"]
    assert bank["reader_agreement_count"] > base["reader_agreement_count"]
    assert len(bank["instrument_ids"]) > len(base["instrument_ids"])
