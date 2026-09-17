# ruff: noqa: I001, E501
from research.population_family_discriminator_rc0.cohort import CASES, CASE_BY_ID, METAMORPHIC_PAIRS
from research.population_family_discriminator_rc0.evaluator import (
    disagreements,
    oracle_relation,
    oracle_vector,
    weak_negative_converse,
    weak_no_negative_inheritance,
    weak_positive_converse,
    weak_symmetric_subset,
    weak_unknown_as_negative,
)


def test_frozen_population_cohort_and_oracle_are_deterministic() -> None:
    assert len(CASES) == 26
    assert oracle_vector() == oracle_vector()


def test_positive_converse_is_killed() -> None:
    failed = set(disagreements(weak_positive_converse))
    assert {"P09", "P17"}.issubset(failed)


def test_negative_converse_is_killed() -> None:
    failed = set(disagreements(weak_negative_converse))
    assert {"P13", "P21"}.issubset(failed)


def test_rc5a_style_missing_negative_inheritance_is_killed() -> None:
    failed = set(disagreements(weak_no_negative_inheritance))
    assert {"P11", "P12", "P19", "P20"}.issubset(failed)


def test_symmetric_subset_strategy_is_killed() -> None:
    failed = set(disagreements(weak_symmetric_subset))
    assert {"P09", "P10", "P13", "P14", "P17", "P18", "P21", "P22"}.intersection(failed)


def test_unknown_as_negative_is_killed() -> None:
    failed = set(disagreements(weak_unknown_as_negative))
    assert {"P05", "P06"}.issubset(failed)


def test_every_population_metamorphic_pair_changes_oracle_relation() -> None:
    for left_id, right_id in METAMORPHIC_PAIRS:
        left = CASE_BY_ID[left_id]
        right = CASE_BY_ID[right_id]
        assert oracle_relation(left.authority, left.query) != oracle_relation(right.authority, right.query), (
            left_id,
            right_id,
        )
