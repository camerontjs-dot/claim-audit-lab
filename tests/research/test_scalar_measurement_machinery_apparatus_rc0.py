from research.scalar_measurement_machinery_rc0.evaluator import (
    evaluate,
    metamorphic_failures,
    weak_approx_exact,
    weak_first_number,
    weak_ignore_target_binding,
    weak_ignore_unit,
    weak_range_midpoint,
)


def test_first_number_strategy_is_unsafe() -> None:
    report = evaluate(weak_first_number)
    assert report.fail_closed_unsafe


def test_unit_erasure_is_unsafe() -> None:
    report = evaluate(weak_ignore_unit)
    assert "SF11" in report.fail_closed_unsafe


def test_target_binding_erasure_is_unsafe() -> None:
    report = evaluate(weak_ignore_target_binding)
    assert "SF09" in report.fail_closed_unsafe
    assert "SF10" in report.fail_closed_unsafe


def test_approximation_laundering_is_detected() -> None:
    report = evaluate(weak_approx_exact)
    assert "SD01" in report.diagnostic_wrong_claims


def test_range_midpoint_loses_required_interval() -> None:
    report = evaluate(weak_range_midpoint)
    assert "SM03" in report.must_handle_failures


def test_metamorphic_controls_discriminate_weak_strategy() -> None:
    assert metamorphic_failures(weak_first_number)
