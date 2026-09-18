from research.population_deontic_applicability_discriminator_rc0.candidate import (
    compose_applicability,
)
from research.population_deontic_applicability_discriminator_rc0.evaluator import (
    failures,
)


def test_candidate_matches_frozen_applicability_oracle() -> None:
    assert failures(compose_applicability) == ()
