from research.attribute_state_temporal_applicability_rc0.apparatus import failures
from research.attribute_state_temporal_applicability_rc0.candidate import (
    compose_timed_state,
)


def test_candidate_satisfies_frozen_contract() -> None:
    assert failures(compose_timed_state) == ()
