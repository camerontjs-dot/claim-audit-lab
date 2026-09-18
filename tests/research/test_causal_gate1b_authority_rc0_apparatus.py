from research.causal_gate1b_authority_rc0.evaluator import (
    failures,
    weak_trust_measurement,
)


def test_frozen_evaluator_rejects_measurement_trust() -> None:
    observed = failures(weak_trust_measurement)
    assert observed
    assert any(item.startswith("CMUT03:") for item in observed)
    assert any(item.startswith("CMUT05:") for item in observed)
