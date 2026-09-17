# ruff: noqa: I001, E501
from research.population_family_discriminator_rc0.candidate import relate
from research.population_family_discriminator_rc0.cohort import CASES, CASE_BY_ID, METAMORPHIC_PAIRS
from research.population_family_discriminator_rc0.evaluator import oracle_relation


def test_candidate_matches_population_oracle_on_all_core_cases() -> None:
    mismatches = []
    for case in CASES:
        observed = relate(case.authority, case.query)
        expected = oracle_relation(case.authority, case.query)
        if observed != expected:
            mismatches.append((case.case_id, observed, expected))
    assert mismatches == []


def test_candidate_replays_deterministically() -> None:
    first = tuple((case.case_id, relate(case.authority, case.query)) for case in CASES)
    second = tuple((case.case_id, relate(case.authority, case.query)) for case in CASES)
    assert first == second


def test_candidate_preserves_directed_subclass_boundary() -> None:
    for case_id in ("P07", "P09", "P11", "P12", "P13", "P15", "P17", "P19", "P20", "P21"):
        case = CASE_BY_ID[case_id]
        assert relate(case.authority, case.query) == oracle_relation(case.authority, case.query)


def test_candidate_preserves_unknown_and_identity_boundary() -> None:
    for case_id in ("P05", "P06", "P23", "P25", "P26"):
        case = CASE_BY_ID[case_id]
        assert relate(case.authority, case.query) == oracle_relation(case.authority, case.query)


def test_candidate_preserves_all_frozen_metamorphic_changes() -> None:
    for left_id, right_id in METAMORPHIC_PAIRS:
        left = CASE_BY_ID[left_id]
        right = CASE_BY_ID[right_id]
        assert relate(left.authority, left.query) != relate(right.authority, right.query), (
            left_id,
            right_id,
        )
