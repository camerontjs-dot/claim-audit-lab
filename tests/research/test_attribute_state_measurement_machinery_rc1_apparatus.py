from research.attribute_state_measurement_machinery_rc1.evaluator import (
    evaluate,
    metamorphic_failures,
    weak_any_copula,
    weak_change_as_state,
    weak_ignore_domain,
    weak_ignore_entity,
    weak_reporting_erasure,
)


def test_generic_copula_is_unsafe() -> None:
    assert evaluate(weak_any_copula).fail_closed_unsafe


def test_entity_erasure_is_wrong_diagnostic() -> None:
    assert "AD06" in evaluate(weak_ignore_entity).diagnostic_wrong_claims


def test_domain_erasure_is_wrong_diagnostic() -> None:
    assert "AD07" in evaluate(weak_ignore_domain).diagnostic_wrong_claims


def test_change_event_is_unsafe() -> None:
    assert "AF02" in evaluate(weak_change_as_state).fail_closed_unsafe


def test_reporting_erasure_is_unsafe() -> None:
    assert "AF06" in evaluate(weak_reporting_erasure).fail_closed_unsafe


def test_metamorphic_controls_detect_weakness() -> None:
    assert metamorphic_failures(weak_any_copula)
