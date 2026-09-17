from research.scalar_value_contract_rc0.apparatus import (
    CASES,
    Relation,
    disagreements,
    oracle,
    weak_approx_exact,
    weak_ignore_unit,
    weak_midpoint,
)


def test_oracle_is_deterministic_and_three_way() -> None:
    first = tuple((case_id, oracle(authority, query)) for case_id, authority, query in CASES)
    second = tuple((case_id, oracle(authority, query)) for case_id, authority, query in CASES)
    assert first == second
    assert {relation for _, relation in first} == {Relation.SUPPORTS, Relation.REFUTES, Relation.UNRESOLVED}


def test_midpoint_shortcut_is_killed() -> None:
    assert "S05" in disagreements(weak_midpoint)


def test_unit_erasure_is_killed() -> None:
    assert "S09" in disagreements(weak_ignore_unit)


def test_approximate_point_is_not_exact_equality_authority() -> None:
    assert "S08" in disagreements(weak_approx_exact)


def test_range_equality_remains_unresolved() -> None:
    case = next(item for item in CASES if item[0] == "S07")
    assert oracle(case[1], case[2]) is Relation.UNRESOLVED
