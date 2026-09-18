from research.event_occurrence_measurement_machinery_rc0.evaluator import (
    evaluate,
    metamorphic_failures,
    weak_deontic_implies_occurrence,
    weak_event_words,
    weak_negation_erasure,
    weak_order_implies_occurrence,
    weak_reporting_erasure,
)


def test_word_bag_is_unsafe() -> None:
    assert evaluate(weak_event_words).fail_closed_unsafe


def test_negation_erasure_misses_required_polarity() -> None:
    assert "EM02" in evaluate(weak_negation_erasure).must_handle_failures


def test_reporting_erasure_is_unsafe() -> None:
    assert "EF01" in evaluate(weak_reporting_erasure).fail_closed_unsafe


def test_order_to_occurrence_shortcut_is_unsafe() -> None:
    assert "EF06" in evaluate(weak_order_implies_occurrence).fail_closed_unsafe


def test_deontic_to_occurrence_shortcut_is_unsafe() -> None:
    assert "EF04" in evaluate(weak_deontic_implies_occurrence).fail_closed_unsafe


def test_metamorphic_controls_discriminate_weak_strategy() -> None:
    assert metamorphic_failures(weak_event_words)
