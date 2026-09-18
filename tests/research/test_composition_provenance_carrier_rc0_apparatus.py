from research.composition_provenance_carrier_rc0.evaluator import weak_failures


def test_all_weak_carriers_are_discriminated() -> None:
    observed = weak_failures()
    assert all(failures for failures in observed.values())


def test_relation_only_is_insufficient() -> None:
    assert weak_failures()["relation_only"]


def test_modifier_state_is_auditable_state() -> None:
    assert weak_failures()["drop_modifiers"]


def test_module_identity_is_bound() -> None:
    assert weak_failures()["module_agnostic"]
