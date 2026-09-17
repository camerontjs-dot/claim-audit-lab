from research.event_occurrence_contract_rc0.apparatus import (
    CASES,
    Relation,
    disagreements,
    oracle,
    weak_erase_scope,
    weak_ignore_polarity,
    weak_ignore_roles,
    weak_mention_is_occurrence,
)


def test_oracle_is_deterministic_and_three_way() -> None:
    first = tuple((case_id, oracle(source, query)) for case_id, source, query in CASES)
    assert first == tuple((case_id, oracle(source, query)) for case_id, source, query in CASES)
    assert {relation for _, relation in first} == {Relation.SUPPORTS, Relation.REFUTES, Relation.UNRESOLVED}


def test_negation_erasure_is_killed() -> None:
    assert "E02" in disagreements(weak_ignore_polarity)


def test_role_bagging_is_killed() -> None:
    assert "E06" in disagreements(weak_ignore_roles)


def test_scope_erasure_is_killed() -> None:
    assert "E07" in disagreements(weak_erase_scope)


def test_order_mention_does_not_establish_occurrence() -> None:
    assert "E09" in disagreements(weak_mention_is_occurrence)
