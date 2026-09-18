from research.typed_binary_gate1b_authority_rc0.candidate import (
    complete_and_warrant_typed_binary,
)
from research.typed_binary_gate1b_authority_rc0.evaluator import failures


def test_candidate_satisfies_frozen_gate1b_contract() -> None:
    assert failures(complete_and_warrant_typed_binary) == ()
