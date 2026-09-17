from research.causal_relation_contract_rc0.apparatus import (
    CASES,
    Relation,
    disagreements,
    oracle,
    weak_cause_contributes,
    weak_contribution_causes,
    weak_correlation_causes,
    weak_precedence_causes,
)


def test_oracle_is_deterministic_and_three_way() -> None:
    first = tuple((case_id, oracle(source, query)) for case_id, source, query in CASES)
    assert first == tuple((case_id, oracle(source, query)) for case_id, source, query in CASES)
    assert {relation for _, relation in first} == {Relation.SUPPORTS, Relation.REFUTES, Relation.UNRESOLVED}


def test_precedence_is_not_causation() -> None:
    assert "C07" in disagreements(weak_precedence_causes)


def test_correlation_is_not_causation() -> None:
    assert "C06" in disagreements(weak_correlation_causes)


def test_contribution_is_not_promoted_to_cause() -> None:
    assert "C04" in disagreements(weak_contribution_causes)


def test_cause_is_not_silently_rewritten_as_contribution() -> None:
    assert "C05" in disagreements(weak_cause_contributes)
