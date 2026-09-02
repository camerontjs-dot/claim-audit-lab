from __future__ import annotations

from .rc8b_heldout_cohort import SUBJECT_A, SUBJECT_B, build_rc8b_heldout_cases


def test_rc8b_heldout_is_fresh_structurally_complete_and_candidate_blind() -> None:
    cases = build_rc8b_heldout_cases()
    assert len(cases) == 50
    assert len({case["case_id"] for case in cases}) == 50

    statuses = {case["expected_authority"] for case in cases}
    assert statuses == {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"}

    axes = {case["mutation_axis"] for case in cases}
    required_axes = {
        "missing_assessment_subject",
        "missing_proposal_subject",
        "proposal_subject_mismatch",
        "missing_assertion_subject",
        "assertion_subject_mismatch",
        "missing_operator_subject",
        "operator_subject_mismatch",
        "required_field_missing_subject",
        "required_field_subject_mismatch",
        "required_field_missing_support_span",
        "required_field_malformed_support_span",
        "required_field_support_left_outside_governance",
        "required_field_support_right_outside_governance",
        "required_field_support_touches_operator_boundaries",
        "required_composition_missing_subject",
        "required_composition_subject_mismatch",
        "required_aperture_missing_subject",
        "required_aperture_subject_mismatch",
        "optional_composition_needs_no_binding",
        "optional_aperture_needs_no_binding",
        "precedence_proposal_before_assertion",
        "precedence_assertion_before_operator",
        "precedence_operator_before_field",
        "precedence_first_required_field_before_composition",
        "precedence_composition_before_aperture",
        "bound_source_semantic_unknown",
        "bound_extraction_unresolved",
        "irrelevant_bank_growth_on_warranted",
        "irrelevant_bank_growth_on_unresolved",
    }
    assert required_axes <= axes


def test_rc8b_heldout_mutations_preserve_preregistered_subject_and_span_controls() -> None:
    by_id = {case["case_id"]: case for case in build_rc8b_heldout_cases()}
    base = by_id["B-H-BASE"]
    assert base["authority_subject_id"] == SUBJECT_A
    assert base["proposal"]["authority_subject_id"] == SUBJECT_A
    assert base["assertion"]["authority_subject_id"] == SUBJECT_A
    assert base["operator"]["authority_subject_id"] == SUBJECT_A
    assert all(
        receipt["authority_subject_id"] == SUBJECT_A
        for receipt in base["field_warrants"].values()
    )

    assert by_id["B-H-MISMATCH-PROP"]["proposal"]["authority_subject_id"] == SUBJECT_B
    assert by_id["B-H-MISMATCH-ASSERT"]["assertion"]["authority_subject_id"] == SUBJECT_B
    assert by_id["B-H-MISMATCH-OP"]["operator"]["authority_subject_id"] == SUBJECT_B
    assert by_id["B-H-FIELD-MISMATCH-SUBJECT"]["field_warrants"]["unit"]["authority_subject_id"] == SUBJECT_B
    assert by_id["B-H-FIELD-SPAN-LEFT"]["field_warrants"]["unit"]["span"] == [49, 80]
    assert by_id["B-H-FIELD-SPAN-RIGHT"]["field_warrants"]["unit"]["span"] == [130, 161]
    assert by_id["B-H-FIELD-SPAN-BOUNDARY"]["field_warrants"]["unit"]["span"] == [50, 160]

    for case in build_rc8b_heldout_cases():
        if case["case_id"] in {"B-H-EXEC", "B-H-EVIDENCE", "B-H-MISS-ASSESS"}:
            continue
        assert case.get("authority_subject_id") == SUBJECT_A


def test_rc8b_heldout_agreement_bank_does_not_change_expected_authority() -> None:
    by_id = {case["case_id"]: case for case in build_rc8b_heldout_cases()}
    assert by_id["B-H-BASE"]["expected_authority"] == by_id["B-H-BANK-WARRANTED"]["expected_authority"] == "WARRANTED"
    assert by_id["B-H-APP-UNK"]["expected_authority"] == by_id["B-H-BANK-UNRESOLVED"]["expected_authority"] == "UNRESOLVED"
    assert by_id["B-H-BANK-WARRANTED"]["reader_agreement_count"] == 8
    assert by_id["B-H-BANK-UNRESOLVED"]["reader_agreement_count"] == 8
