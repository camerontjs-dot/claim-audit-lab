from research.population_measurement_machinery_rc0.evaluator import (
    evaluate,
    metamorphic_failures,
    weak_any_copula,
    weak_negation_erasure,
    weak_past_membership,
    weak_plural_subset,
    weak_reporting_erasure,
)


def test_any_copula_is_rejected() -> None:
    assert evaluate(weak_any_copula).fail_closed_unsafe


def test_quantifier_blind_subset_is_rejected() -> None:
    report = evaluate(weak_plural_subset)
    assert "PF01" in report.fail_closed_unsafe
    assert "PF02" in report.fail_closed_unsafe


def test_negation_erasure_is_rejected() -> None:
    assert "PM02" in evaluate(weak_negation_erasure).must_handle_failures


def test_past_membership_is_rejected() -> None:
    assert "PF06" in evaluate(weak_past_membership).fail_closed_unsafe


def test_reporting_erasure_is_rejected() -> None:
    assert "PF08" in evaluate(weak_reporting_erasure).fail_closed_unsafe


def test_metamorphic_controls_discriminate_weak_strategy() -> None:
    assert metamorphic_failures(weak_any_copula)
