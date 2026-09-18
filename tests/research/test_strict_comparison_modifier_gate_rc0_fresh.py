from research.strict_comparison_modifier_gate_rc0.fresh_evaluator import (
    positive_failures,
    unsafe_cases,
)


def test_fresh_direct_positive_controls_survive() -> None:
    assert positive_failures() == ()


def test_fresh_modifier_scope_cases_fail_closed() -> None:
    assert unsafe_cases() == ()
