from research.strict_comparison_gate1b_authority_rc1.candidate import complete_and_warrant_strict
from research.strict_comparison_gate1b_authority_rc1.evaluator import failures


def test_candidate_satisfies_frozen_gate1b_contract() -> None:
    assert failures(complete_and_warrant_strict) == ()
