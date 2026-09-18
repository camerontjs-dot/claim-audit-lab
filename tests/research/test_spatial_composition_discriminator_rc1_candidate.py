from research.spatial_composition_discriminator_rc1.apparatus import failures
from research.spatial_composition_discriminator_rc1.candidate import compose_relation_chain


def test_generic_declared_law_candidate_satisfies_frozen_contract() -> None:
    assert failures(compose_relation_chain) == ()
