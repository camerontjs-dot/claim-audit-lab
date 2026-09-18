from research.occurrence_order_binding_discriminator_rc0.candidate import (
    compose_occurrence_order,
)
from research.occurrence_order_binding_discriminator_rc0.evaluator import failures


def test_candidate_matches_frozen_recombination_oracle() -> None:
    assert failures(compose_occurrence_order) == ()
