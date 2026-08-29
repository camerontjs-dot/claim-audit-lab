"""Phase-2 comparison against the untouched frozen RC0 evaluator."""

from tests.research.rc0_candidate_adapters import (
    additive_epistemic_receipt_adapter,
    current_v050_trace_adapter,
    historical_v2_surface_adapter,
    internal_staged_ledger_adapter,
    terminal_reason_augmentation_adapter,
)
from tests.research.rc0_evaluator import GATES, evaluate


def _vector(*values: bool) -> dict[str, bool]:
    return dict(zip(GATES, values, strict=True))


def test_current_v050_observable_surface_gate_vector() -> None:
    assert evaluate(current_v050_trace_adapter) == _vector(
        True,   # A state distinguishability
        False,  # B fail-closed missing assessment state
        False,  # C final participation/deciding basis not first-class
        True,   # D measurement-policy separation
        True,   # E upstream-role invariance
        False,  # F source trust != explicit proposition eligibility assessment
        False,  # G causal multiplicity not represented
        False,  # H failed execution is not a v1 AuditTrace state
        True,   # I policy counterfactual leaves measurement fixed
        True,   # J replay surface is deterministic
    )


def test_terminal_reason_only_augmentation_is_insufficient() -> None:
    assert evaluate(terminal_reason_augmentation_adapter) == _vector(
        True,
        False,
        False,
        True,
        True,
        False,
        False,
        False,
        True,
        True,
    )


def test_additive_epistemic_receipt_clears_all_behavioral_gates() -> None:
    assert evaluate(additive_epistemic_receipt_adapter) == {gate: True for gate in GATES}


def test_historical_v2_surface_improves_participation_but_does_not_clear_required_state() -> None:
    assert evaluate(historical_v2_surface_adapter) == _vector(
        True,
        False,
        True,
        True,
        True,
        False,
        False,
        False,
        True,
        True,
    )


def test_full_internal_staging_is_not_discriminated_from_smaller_receipt() -> None:
    receipt = evaluate(additive_epistemic_receipt_adapter)
    staged = evaluate(internal_staged_ledger_adapter)
    assert receipt == staged == {gate: True for gate in GATES}
