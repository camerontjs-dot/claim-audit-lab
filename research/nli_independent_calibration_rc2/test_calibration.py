import numpy as np

from research.nli_independent_calibration_rc2.run_calibration import (
    adverse_conservative,
    fit_temperature,
    multiclass_nll,
    probabilities_from_logits,
)


def test_adverse_conservative_preserves_conflict() -> None:
    assert (
        adverse_conservative(["contradiction", "contradiction", "entailment"])
        == "unresolved"
    )
    assert (
        adverse_conservative(["contradiction", "contradiction", "contradiction"])
        == "contradiction"
    )
    assert (
        adverse_conservative(["entailment", "entailment", "neutral"])
        == "entailment"
    )


def test_temperature_fit_is_positive_and_does_not_change_argmax() -> None:
    logits = np.array(
        [
            [4.0, 1.0, 0.0],
            [0.0, 3.0, 1.0],
            [0.0, 1.0, 4.0],
            [2.0, 1.8, 0.5],
        ],
        dtype=np.float64,
    )
    targets = np.array([0, 1, 2, 1], dtype=np.int64)
    temperature = fit_temperature(logits, targets)
    assert 0.05 <= temperature <= 20.0
    native = probabilities_from_logits(logits, 1.0).argmax(axis=1)
    calibrated = probabilities_from_logits(logits, temperature).argmax(axis=1)
    assert np.array_equal(native, calibrated)
    assert multiclass_nll(logits, targets, temperature) <= multiclass_nll(
        logits, targets, 1.0
    ) + 1e-10
