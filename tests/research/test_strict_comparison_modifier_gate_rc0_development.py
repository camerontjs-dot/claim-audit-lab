from research.strict_comparison_modifier_gate_rc0.development_controls import (
    development_failures,
)


def test_revealed_parent_failures_are_closed_without_vacuous_positive_block() -> None:
    assert development_failures() == ()
