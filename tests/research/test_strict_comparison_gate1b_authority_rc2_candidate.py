from research.strict_comparison_gate1b_authority_rc2.candidate import (
    complete_and_warrant_strict_rc2,
)
from research.strict_comparison_gate1b_authority_rc2.evaluator import failures


def test_candidate_closes_frozen_regressions() -> None:
    assert failures(complete_and_warrant_strict_rc2) == ()
