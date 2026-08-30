from __future__ import annotations

from research.nli_measurement_discrimination_rc0.run_experiment import (
    PRIMARY_TARGETS,
    _filler_block,
    build_primary_cases,
)


def test_primary_target_mapping_preserves_three_way_neutral() -> None:
    assert PRIMARY_TARGETS == {
        "restates": "entailment",
        "weakens": "entailment",
        "contradicts": "contradiction",
        "overgeneralizes": "neutral",
    }


def test_primary_slice_excludes_operator_owned_relations() -> None:
    cases = build_primary_cases()
    assert cases
    assert {case.target for case in cases} <= {"entailment", "neutral", "contradiction"}
    assert not {
        "absent_from",
        "instantiates_bound",
        "conjunction",
        "partial_conjunction",
        "chains",
    } & {case.relation for case in cases}


def test_aperture_filler_is_deterministic_and_does_not_embed_claim_terms() -> None:
    first = _filler_block(25)
    second = _filler_block(25)
    assert first == second
    assert "Quality Hold" not in first
    assert "requalification" not in first.lower()
