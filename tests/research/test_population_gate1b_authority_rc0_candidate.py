from research.population_gate1b_authority_rc0.candidate import (
    complete_and_warrant_population,
)
from research.population_gate1b_authority_rc0.evaluator import failures


def test_candidate_satisfies_frozen_gate1b_contract() -> None:
    assert failures(complete_and_warrant_population) == ()
