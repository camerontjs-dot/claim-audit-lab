from research.typed_binary_measurement_machinery_rc1.evaluator import (
    evaluate,
    metamorphic_failures,
    weak_argument_erasure,
    weak_metric_erasure,
    weak_open_predicate,
    weak_reporting_erasure,
    weak_spatial_transitivity,
)


def test_argument_erasure_is_wrong_diagnostic() -> None:
    assert "RD01" in evaluate(weak_argument_erasure).diagnostic_wrong_claims


def test_unknown_predicate_is_unsafe() -> None:
    assert "RF01" in evaluate(weak_open_predicate).fail_closed_unsafe


def test_spatial_transitivity_is_unsafe() -> None:
    report=evaluate(weak_spatial_transitivity)
    assert "RF02" in report.fail_closed_unsafe or "RF03" in report.fail_closed_unsafe


def test_reporting_erasure_is_unsafe() -> None:
    assert "RF05" in evaluate(weak_reporting_erasure).fail_closed_unsafe


def test_metric_erasure_is_unsafe() -> None:
    assert "RF04" in evaluate(weak_metric_erasure).fail_closed_unsafe


def test_metamorphics_discriminate_weakness() -> None:
    assert metamorphic_failures(weak_argument_erasure)
