from research.spatial_composition_discriminator_rc1.candidate import compose_relation
from research.spatial_composition_discriminator_rc1.evaluator import failures


def test_candidate_matches_frozen_spatial_oracle() -> None:
    assert failures(compose_relation) == ()
