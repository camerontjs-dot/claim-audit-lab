from research.quantitative_change_composition_rc0.apparatus import CASES, oracle
from research.quantitative_change_composition_rc0.candidate import derive_relation


def test_composition_candidate_matches_frozen_oracle() -> None:
    assert [
        case_id
        for case_id, old, new, query in CASES
        if derive_relation(old, new, query) != oracle(old, new, query)
    ] == []


def test_composition_candidate_replays_exactly() -> None:
    first = tuple(derive_relation(old, new, query) for _, old, new, query in CASES)
    assert first == tuple(derive_relation(old, new, query) for _, old, new, query in CASES)
