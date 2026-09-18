from research.strict_comparison_structural_gate_rc1.development_controls import failures


def test_revealed_failures_closed_and_bounded_positives_retained() -> None:
    assert failures() == ()
