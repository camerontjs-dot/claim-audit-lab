# ruff: noqa: I001, E501
from research.deontic_norm_contract_rc0.cohort import CASES, CASE_BY_ID, METAMORPHIC_PAIRS
from research.deontic_norm_contract_rc0.evaluator import (
    disagreements,
    oracle_relation,
    oracle_vector,
    weak_exact_mode_only,
    weak_ignore_modifiers,
    weak_ought_implies_may,
    weak_restriction_grants_permission,
)


def test_frozen_cohort_shape_and_oracle_determinism() -> None:
    assert len(CASES) == 36
    first = oracle_vector()
    second = oracle_vector()
    assert first == second
    assert len(first) == len(CASES)


def test_weak_ought_implies_may_is_killed_for_the_intended_reason() -> None:
    failed = disagreements(weak_ought_implies_may)
    assert "D09" in failed
    assert "D31" in failed


def test_weak_restriction_grants_permission_is_killed() -> None:
    failed = disagreements(weak_restriction_grants_permission)
    assert "D11" in failed
    assert "D32" in failed


def test_weak_modifier_erasure_is_killed_across_modifier_types() -> None:
    failed = set(disagreements(weak_ignore_modifiers))
    assert {"D16", "D17", "D19", "D20", "D22", "D23", "D24"}.issubset(failed)
    assert {"D26", "D27", "D28"}.issubset(failed)


def test_weak_exact_mode_only_is_killed_by_explicit_conflicts() -> None:
    failed = set(disagreements(weak_exact_mode_only))
    assert {"D05", "D06", "D07", "D08", "D29", "D30"}.issubset(failed)


def test_every_frozen_metamorphic_pair_changes_oracle_relation() -> None:
    assert len(METAMORPHIC_PAIRS) >= 8
    for left_id, right_id in METAMORPHIC_PAIRS:
        left = CASE_BY_ID[left_id]
        right = CASE_BY_ID[right_id]
        assert oracle_relation(left.source, left.query) != oracle_relation(right.source, right.query), (
            left_id,
            right_id,
        )
