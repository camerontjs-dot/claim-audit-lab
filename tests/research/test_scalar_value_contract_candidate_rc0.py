from research.scalar_value_contract_rc0.apparatus import CASES, oracle
from research.scalar_value_contract_rc0.candidate import relate


def test_candidate_matches_frozen_oracle() -> None:
    assert [
        case_id
        for case_id, authority, query in CASES
        if relate(authority, query) != oracle(authority, query)
    ] == []


def test_candidate_replays_exactly() -> None:
    first = tuple(relate(authority, query) for _, authority, query in CASES)
    second = tuple(relate(authority, query) for _, authority, query in CASES)
    assert first == second
