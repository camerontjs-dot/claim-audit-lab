from research.strict_comparison_gate1b_authority_rc2.evaluator import (
    failures,
    weak_trust_measurement,
)


def test_frozen_regression_evaluator_rejects_measurement_trust() -> None:
    observed = failures(weak_trust_measurement)
    assert observed
    assert any(item.startswith("S2R01:") for item in observed)
    assert any(item.startswith("S2R11:") for item in observed)
