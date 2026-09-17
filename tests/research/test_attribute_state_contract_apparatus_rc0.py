from research.attribute_state_contract_rc0.apparatus import (
    CASES,
    Relation,
    disagreements,
    oracle,
    weak_generic_spo,
    weak_ignore_domain,
    weak_ignore_entity,
    weak_nonfunctional_as_functional,
)


def test_oracle_is_deterministic_and_three_way() -> None:
    first = tuple((case_id, oracle(source, query)) for case_id, source, query in CASES)
    assert first == tuple((case_id, oracle(source, query)) for case_id, source, query in CASES)
    assert {relation for _, relation in first} == {Relation.SUPPORTS, Relation.REFUTES, Relation.UNRESOLVED}


def test_generic_spo_overreach_is_killed() -> None:
    assert "A06" in disagreements(weak_generic_spo)


def test_domain_erasure_is_killed() -> None:
    assert "A04" in disagreements(weak_ignore_domain)


def test_entity_erasure_is_killed() -> None:
    assert "A03" in disagreements(weak_ignore_entity)


def test_nonfunctional_predicate_is_not_closed_attribute() -> None:
    assert "A06" in disagreements(weak_nonfunctional_as_functional)
