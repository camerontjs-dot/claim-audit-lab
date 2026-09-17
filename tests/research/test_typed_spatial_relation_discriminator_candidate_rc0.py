from research.typed_spatial_relation_discriminator_rc0.apparatus import CASES, oracle
from research.typed_spatial_relation_discriminator_rc0.candidate import relate


def test_generic_candidate_matches_every_frozen_case() -> None:
    assert [case_id for case_id, source, query in CASES if relate(source, query) != oracle(source, query)] == []


def test_spatial_subset_uses_same_generic_consumer() -> None:
    for case_id, source, query in CASES:
        if case_id in {"R05", "R06", "R07", "R08"}:
            assert relate(source, query) == oracle(source, query)
