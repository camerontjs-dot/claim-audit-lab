from research.typed_binary_gate1b_authority_rc1.evaluator import (
    failures,
    weak_trust_measurement,
)


def test_frozen_evaluator_rejects_measurement_trust() -> None:
    observed = failures(weak_trust_measurement)
    assert observed
    assert any(item.startswith("TMUT01:") for item in observed)
    assert any(item.startswith("TMUT04:") for item in observed)
