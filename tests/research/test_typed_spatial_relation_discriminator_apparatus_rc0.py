from research.typed_spatial_relation_discriminator_rc0.apparatus import (
    CASES,
    Relation,
    disagreements,
    oracle,
    weak_all_symmetric,
    weak_ignore_inverse,
    weak_open_predicate,
)


def test_oracle_is_deterministic_and_three_way() -> None:
    first = tuple((case_id, oracle(source, query)) for case_id, source, query in CASES)
    assert first == tuple((case_id, oracle(source, query)) for case_id, source, query in CASES)
    assert {relation for _, relation in first} == {Relation.SUPPORTS, Relation.REFUTES, Relation.UNRESOLVED}


def test_open_predicate_acceptance_is_killed() -> None:
    assert "R09" in disagreements(weak_open_predicate)


def test_all_symmetric_is_killed() -> None:
    assert "R03" in disagreements(weak_all_symmetric)


def test_inverse_erasure_is_killed_on_generic_and_spatial_atoms() -> None:
    failed = set(disagreements(weak_ignore_inverse))
    assert {"R02", "R06", "R08"}.issubset(failed)
