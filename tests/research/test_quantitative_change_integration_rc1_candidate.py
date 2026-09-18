from research.quantitative_change_integration_rc1.apparatus import failures
from research.quantitative_change_integration_rc1.candidate import compose_change


def test_candidate_satisfies_frozen_integration_contract() -> None:
    assert failures(compose_change) == ()
