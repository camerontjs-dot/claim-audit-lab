from research.direct_event_order_gate1b_authority_rc1.evaluator import (
    failures,
    weak_permissive_authority,
)


def test_frozen_evaluator_rejects_permissive_authority() -> None:
    observed = failures(weak_permissive_authority)
    assert observed
    assert any(item.startswith("EOR01:") for item in observed)
    assert any(item.startswith("EOR06:") for item in observed)
