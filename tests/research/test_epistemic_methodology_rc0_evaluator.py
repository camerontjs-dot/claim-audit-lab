"""Assurance controls for the frozen CAL Epistemic Methodology RC0 evaluator."""

from tests.research.rc0_evaluator import (
    GATES,
    evaluate,
    generic_abstention_weak_control,
    reference_observability_control,
    terminal_reason_only_weak_control,
)


def test_positive_observability_control_clears_all_frozen_gates() -> None:
    results = evaluate(reference_observability_control)
    assert results == {gate: True for gate in GATES}


def test_generic_abstention_control_is_rejected() -> None:
    results = evaluate(generic_abstention_weak_control)
    assert not all(results.values())
    assert results["A_state_distinguishability"] is False
    assert results["C_evidence_retention"] is False
    assert results["H_execution_state_separation"] is False


def test_terminal_reason_only_control_does_not_fake_a_state_ledger() -> None:
    results = evaluate(terminal_reason_only_weak_control)
    assert results["A_state_distinguishability"] is True
    assert results["C_evidence_retention"] is False
    assert results["F_trust_eligibility_separation"] is False
    assert results["G_causal_basis_reconstruction"] is False


def test_frozen_gate_set_is_exact() -> None:
    assert GATES == (
        "A_state_distinguishability",
        "B_fail_closed_missing_state",
        "C_evidence_retention",
        "D_measurement_policy_separation",
        "E_upstream_role_invariance",
        "F_trust_eligibility_separation",
        "G_causal_basis_reconstruction",
        "H_execution_state_separation",
        "I_policy_counterfactual_stability",
        "J_replayability",
    )
