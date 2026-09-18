from research.composition_provenance_carrier_rc0.apparatus import (
    CASES,
    failures,
    mutation_failures,
    verify_receipt,
)
from research.composition_provenance_carrier_rc0.candidate import bind_composition


def test_candidate_satisfies_all_module_shapes() -> None:
    assert failures(bind_composition) == ()


def test_candidate_receipts_verify_for_every_case() -> None:
    for request in CASES:
        assert verify_receipt(bind_composition(request), request)


def test_any_bound_field_mutation_invalidates_receipt() -> None:
    assert mutation_failures(bind_composition) == ()
