from research.quantitative_change_integration_rc1.apparatus import (
    failures,
    weak_force_exact,
    weak_input_order,
    weak_relation_only,
)


def test_relation_only_is_not_sufficient_evidence() -> None:
    assert failures(weak_relation_only)


def test_input_order_is_not_temporal_authority() -> None:
    assert "Q5" in failures(weak_input_order)


def test_approximate_scalar_must_not_be_upgraded() -> None:
    assert failures(weak_force_exact)
