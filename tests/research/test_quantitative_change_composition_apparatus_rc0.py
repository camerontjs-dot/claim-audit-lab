from research.quantitative_change_composition_rc0.apparatus import (
    CASES,
    Relation,
    disagreements,
    oracle,
    weak_approx_exact,
    weak_ignore_metric,
    weak_ignore_unit,
    weak_reverse_order,
)


def test_oracle_is_deterministic_and_three_way() -> None:
    first = tuple((case_id, oracle(old, new, query)) for case_id, old, new, query in CASES)
    assert first == tuple((case_id, oracle(old, new, query)) for case_id, old, new, query in CASES)
    assert {relation for _, relation in first} == {Relation.SUPPORTS, Relation.REFUTES, Relation.UNRESOLVED}


def test_unit_erasure_is_killed() -> None:
    assert "Q07" in disagreements(weak_ignore_unit)


def test_metric_erasure_is_killed() -> None:
    assert "Q06" in disagreements(weak_ignore_metric)


def test_approximate_states_do_not_authorize_exact_change() -> None:
    assert "Q08" in disagreements(weak_approx_exact)


def test_state_order_is_causal_to_change_direction() -> None:
    assert "Q01" in disagreements(weak_reverse_order)
