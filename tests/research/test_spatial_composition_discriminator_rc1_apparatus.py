from research.spatial_composition_discriminator_rc1.evaluator import weak_failures


def test_frozen_evaluator_discriminates_weak_strategies() -> None:
    observed = weak_failures()
    assert all(observed.values())
    assert any(item.startswith("SU01:") for item in observed["all_transitive"])
    assert any(item.startswith("SU03:") for item in observed["ignore_frame"])
    assert any(item.startswith("SU10:") for item in observed["ignore_warrant"])
    assert any(
        item.startswith("SC02:") or item.startswith("SC06:")
        for item in observed["no_inverse"]
    )
