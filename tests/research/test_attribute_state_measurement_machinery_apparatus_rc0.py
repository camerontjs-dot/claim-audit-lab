from research.attribute_state_measurement_machinery_rc0.evaluator import (
    evaluate,
    metamorphic_failures,
    weak_any_copula,
    weak_change_as_state,
    weak_membership_as_state,
    weak_nonfunctional_singleton,
    weak_reporting_erasure,
)


def test_generic_copula_is_unsafe() -> None:
    assert evaluate(weak_any_copula).fail_closed_unsafe


def test_membership_cannot_be_recast_as_state() -> None:
    assert "AF01" in evaluate(weak_membership_as_state).fail_closed_unsafe


def test_change_event_cannot_be_recast_as_state() -> None:
    assert "AF02" in evaluate(weak_change_as_state).fail_closed_unsafe


def test_reporting_erasure_is_unsafe() -> None:
    assert "AF06" in evaluate(weak_reporting_erasure).fail_closed_unsafe


def test_multi_label_cannot_be_collapsed() -> None:
    assert "AF08" in evaluate(weak_nonfunctional_singleton).fail_closed_unsafe


def test_metamorphic_controls_discriminate_weak_strategy() -> None:
    assert metamorphic_failures(weak_any_copula)
