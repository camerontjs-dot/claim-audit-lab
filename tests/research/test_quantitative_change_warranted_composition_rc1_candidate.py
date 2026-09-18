from research.quantitative_change_warranted_composition_rc1.candidate import compose_change
from research.quantitative_change_warranted_composition_rc1.evaluator import failures


def test_candidate_matches_frozen_composition_oracle() -> None:
    assert failures(compose_change) == ()
