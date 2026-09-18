from research.causal_measurement_machinery_rc0.evaluator import (
    evaluate,
    metamorphic_failures,
    weak_association_is_correlation,
    weak_composition_collapse,
    weak_everything_causes,
    weak_ignore_endpoints,
    weak_reporting_erasure,
    weak_risk_factor_contribution,
)


def test_kind_laundering_is_detected() -> None:
    report = evaluate(weak_everything_causes)
    assert {"CM02", "CM04", "CM05"}.intersection(report.must_handle_failures)


def test_endpoint_erasure_is_detected() -> None:
    assert "CM07" in evaluate(weak_ignore_endpoints).must_handle_failures


def test_reporting_erasure_is_unsafe() -> None:
    assert "CF01" in evaluate(weak_reporting_erasure).fail_closed_unsafe


def test_association_is_not_frozen_correlation() -> None:
    assert "CF08" in evaluate(weak_association_is_correlation).fail_closed_unsafe


def test_risk_factor_is_not_auto_contribution() -> None:
    assert "CF03" in evaluate(weak_risk_factor_contribution).fail_closed_unsafe


def test_composition_collapse_is_unsafe() -> None:
    assert "CF05" in evaluate(weak_composition_collapse).fail_closed_unsafe


def test_metamorphic_controls_discriminate_weak_strategy() -> None:
    assert metamorphic_failures(weak_everything_causes)
