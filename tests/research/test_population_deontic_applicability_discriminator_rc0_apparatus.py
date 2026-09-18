from research.population_deontic_applicability_discriminator_rc0.evaluator import (
    weak_failures,
)


def test_frozen_evaluator_discriminates_weak_applicability_strategies() -> None:
    observed = weak_failures()
    assert all(observed.values())
    assert any(
        item.startswith("NU01:") or item.startswith("NU07:")
        for item in observed["string_only"]
    )
    assert any(
        item.startswith("NU01:") or item.startswith("NU02:")
        for item in observed["ignore_status"]
    )
    assert any(item.startswith("NU07:") for item in observed["ignore_subject_kind"])
    assert any(
        item.startswith("NU08:")
        or item.startswith("NU09:")
        or item.startswith("NU10:")
        for item in observed["drop_modifiers"]
    )
    assert any(
        item.startswith("NU05:") or item.startswith("NU06:")
        for item in observed["ignore_warrant"]
    )
