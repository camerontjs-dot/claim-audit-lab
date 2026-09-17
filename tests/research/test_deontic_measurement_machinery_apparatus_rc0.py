from research.deontic_measurement_machinery_rc0.evaluator import (
    evaluate,
    metamorphic_failures,
    weak_exact_modal_only,
    weak_may_not_prohibition,
    weak_modal_cue,
    weak_modifier_erasure,
    weak_reporting_erasure,
)


def test_frozen_modal_cue_weakness_is_detected() -> None:
    report = evaluate(weak_modal_cue)
    assert report.fail_closed_unsafe


def test_frozen_modifier_erasure_is_detected() -> None:
    report = evaluate(weak_modifier_erasure)
    assert "DM10" in report.must_handle_failures
    assert "DM11" in report.must_handle_failures
    assert "DM13" in report.must_handle_failures


def test_frozen_may_not_coercion_is_detected() -> None:
    report = evaluate(weak_may_not_prohibition)
    assert "DF03" in report.fail_closed_unsafe


def test_frozen_reporting_erasure_is_detected() -> None:
    report = evaluate(weak_reporting_erasure)
    assert "DF05" in report.fail_closed_unsafe


def test_frozen_exact_modal_only_is_incomplete() -> None:
    report = evaluate(weak_exact_modal_only)
    assert {"DM05", "DM06", "DM07"}.intersection(report.must_handle_failures)


def test_frozen_metamorphic_controls_are_nonempty() -> None:
    assert metamorphic_failures(weak_modal_cue)
