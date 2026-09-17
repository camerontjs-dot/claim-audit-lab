from research.attribute_state_contract_rc0.apparatus import CASES, oracle
from research.attribute_state_contract_rc0.candidate import relate


def test_candidate_matches_frozen_oracle() -> None:
    assert [case_id for case_id, source, query in CASES if relate(source, query) != oracle(source, query)] == []


def test_candidate_replays_exactly() -> None:
    first = tuple(relate(source, query) for _, source, query in CASES)
    assert first == tuple(relate(source, query) for _, source, query in CASES)
