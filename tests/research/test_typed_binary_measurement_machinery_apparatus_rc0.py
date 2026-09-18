from research.typed_binary_measurement_machinery_rc0.evaluator import (
    evaluate,
    metamorphic_failures,
    weak_all_spatial_transitive,
    weak_argument_erasure,
    weak_keyword_relation,
    weak_reporting_erasure,
    weak_unknown_predicate,
)


def test_keyword_relation_is_unsafe() -> None:
    assert evaluate(weak_keyword_relation).fail_closed_unsafe


def test_spatial_transitivity_shortcut_is_unsafe() -> None:
    assert "RF03" in evaluate(weak_all_spatial_transitive).fail_closed_unsafe


def test_unknown_predicate_is_unsafe() -> None:
    assert "RF01" in evaluate(weak_unknown_predicate).fail_closed_unsafe


def test_reporting_erasure_is_unsafe() -> None:
    assert "RF05" in evaluate(weak_reporting_erasure).fail_closed_unsafe


def test_argument_direction_erasure_is_detected() -> None:
    assert "RF11" in evaluate(weak_argument_erasure).fail_closed_unsafe


def test_metamorphic_controls_discriminate_weak_strategy() -> None:
    assert metamorphic_failures(weak_keyword_relation)
