from research.quantitative_change_warranted_composition_rc1.evaluator import weak_failures


def test_frozen_evaluator_discriminates_weak_strategies() -> None:
    observed = weak_failures()
    assert all(observed.values())
    assert any(item.startswith("QC07:") for item in observed["input_order"])
    assert any(item.startswith("QU01:") for item in observed["ignore_identity"])
    assert any(item.startswith("QU05:") for item in observed["midpoint"])
    assert any(item.startswith("QU08:") for item in observed["ignore_warrant"])
