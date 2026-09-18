from research.attribute_state_gate1b_authority_rc0.candidate import (
    complete_and_warrant_attribute_state,
)
from research.attribute_state_gate1b_authority_rc0.evaluator import failures


def test_candidate_satisfies_frozen_gate1b_contract() -> None:
    assert failures(complete_and_warrant_attribute_state) == ()
