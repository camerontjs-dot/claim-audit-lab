from research.direct_event_order_gate1b_authority_rc3.candidate import (
    complete_and_warrant_event_order_rc3,
)
from research.direct_event_order_gate1b_authority_rc3.evaluator import failures


def test_candidate_closes_frozen_regressions() -> None:
    assert failures(complete_and_warrant_event_order_rc3) == ()
