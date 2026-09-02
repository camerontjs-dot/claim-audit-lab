from __future__ import annotations

from copy import deepcopy

from .rc8a_cohort import SUBJECT_A, SUBJECT_B, build_rc8a_cases


def test_rc8a_cohort_is_exact_preregistered_shape_without_candidate_execution() -> None:
    cases = build_rc8a_cases()
    assert len(cases) == 7
    assert len({case["case_id"] for case in cases}) == 7

    bound = cases[0]
    assert bound["case_id"] == "RC8A-BOUND-POSITIVE"
    assert bound["expected_authority"] == "WARRANTED"
    assert bound["authority_subject_id"] == SUBJECT_A

    axes = {case["mutation_axis"] for case in cases[1:]}
    assert axes == {
        "assertion_authority_subject_substitution",
        "operator_authority_subject_substitution",
        "field_authority_subject_substitution",
        "field_support_span_outside_operator_governance",
        "composition_authority_subject_substitution",
        "aperture_authority_subject_substitution",
    }
    assert all(case["expected_authority"] == "REJECTED" for case in cases[1:])


def test_rc8a_mutations_hold_semantics_constant_and_change_only_preregistered_binding_surface() -> None:
    cases = build_rc8a_cases()
    bound = cases[0]

    for case in cases[1:]:
        assert case["raw_source_id"] == bound["raw_source_id"]
        assert case["proposal"]["family"] == bound["proposal"]["family"]
        assert case["proposal"]["source_span"] == bound["proposal"]["source_span"]
        assert case["proposal"]["fields"] == bound["proposal"]["fields"]
        assert case["proposal"]["extra_modifiers"] == []
        assert case["evidence_admitted"] is True
        assert case["execution_state"] == "completed"

    by_axis = {case["mutation_axis"]: case for case in cases[1:]}
    assert by_axis["assertion_authority_subject_substitution"]["assertion"]["authority_subject_id"] == SUBJECT_B
    assert by_axis["operator_authority_subject_substitution"]["operator"]["authority_subject_id"] == SUBJECT_B
    assert by_axis["field_authority_subject_substitution"]["field_warrants"]["comparison_direction"]["authority_subject_id"] == SUBJECT_B
    assert by_axis["field_support_span_outside_operator_governance"]["field_warrants"]["comparison_direction"]["span"] == [160, 170]
    assert by_axis["composition_authority_subject_substitution"]["composition"]["authority_subject_id"] == SUBJECT_B
    assert by_axis["aperture_authority_subject_substitution"]["aperture"]["authority_subject_id"] == SUBJECT_B

    reference = deepcopy(bound)
    reference.pop("case_id")
    reference.pop("mutation_axis")
    reference.pop("expected_authority")
    reference.pop("expected_reason")
    assert reference["authority_subject_id"] == SUBJECT_A
