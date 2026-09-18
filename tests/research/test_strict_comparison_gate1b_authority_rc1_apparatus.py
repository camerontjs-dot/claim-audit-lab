from research.strict_comparison_gate1b_authority_rc1.evaluator import (
    failures,
    weak_permissive_authority,
)


def test_frozen_evaluator_rejects_permissive_authority() -> None:
    observed = failures(weak_permissive_authority)
    assert observed
    assert any(item.startswith("SCR01:") for item in observed)
    assert any(item.startswith("SCR07:") for item in observed)
