from research.attribute_state_gate1b_authority_rc0.evaluator import (
    failures,
    weak_trust_measurement,
)


def test_frozen_evaluator_rejects_measurement_trust() -> None:
    observed = failures(weak_trust_measurement)
    assert observed
    assert any(item.startswith("AMUT01:") for item in observed)
    assert any(item.startswith("AMUT05:") for item in observed)
