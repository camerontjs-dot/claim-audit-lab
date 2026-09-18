from research.spatial_composition_discriminator_rc1.apparatus import (
    failures,
    weak_all_transitive,
    weak_container_inherits_direction,
    weak_no_transitivity,
    weak_relation_only,
)


def test_provenance_free_output_is_insufficient() -> None:
    assert failures(weak_relation_only)


def test_all_predicates_transitive_is_unsafe() -> None:
    observed = failures(weak_all_transitive)
    assert "S5" in observed or "S6" in observed or "S7" in observed


def test_no_transitivity_loses_containment_composition() -> None:
    observed = failures(weak_no_transitivity)
    assert "S1" in observed


def test_container_direction_inheritance_is_unsafe() -> None:
    assert "S8" in failures(weak_container_inherits_direction)
