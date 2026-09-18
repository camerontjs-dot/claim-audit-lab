from research.attribute_state_temporal_applicability_rc0.evaluator import (
    weak_failures,
)


def test_each_weak_strategy_is_discriminated() -> None:
    observed = weak_failures()
    assert all(failures for failures in observed.values())


def test_timeless_persistence_fails_outside_scope() -> None:
    assert "AT05" in weak_failures()["latest_persists"]


def test_scope_must_bind_to_exact_authority() -> None:
    assert "AT07" in weak_failures()["ignore_scope_binding"]


def test_nonfunctional_attributes_do_not_refute_alternate_values() -> None:
    assert "AT11" in weak_failures()["all_functional"]
