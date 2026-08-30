from pathlib import Path

from research.nli_ensemble_disagreement_rc1.evaluate_ensemble import (
    load_frozen,
    r1_majority,
    r2_unanimity,
    r4_adverse_conservative,
    r5_aperture_route,
)

FROZEN = Path("research/nli_ensemble_disagreement_rc1/FROZEN_MEASUREMENTS.json")


def _row(case_id: str, variant: str):
    data = load_frozen(FROZEN)
    return next(
        row
        for row in data["rows"]
        if row["case_id"] == case_id and row["variant"] == variant
    )


def test_cg18_majority_is_adverse_but_conservative_rules_abstain() -> None:
    row = _row("CG-18", "short")
    assert row["target"] == "neutral"
    assert r1_majority(row) == "contradiction"
    assert r2_unanimity(row) == "unresolved"
    assert r4_adverse_conservative(row) == "unresolved"


def test_cg20_majority_recovers_but_conservative_rule_abstains() -> None:
    row = _row("CG-20", "short")
    assert row["target"] == "entailment"
    assert r1_majority(row) == "entailment"
    assert r4_adverse_conservative(row) == "unresolved"


def test_aperture_router_uses_long_model_only_when_512_models_truncate() -> None:
    short = _row("CG-03", "short")
    tail = _row("CG-03", "stress_tail")
    assert r5_aperture_route(short) == r4_adverse_conservative(short)
    assert tail["truncated"]["incumbent_base"] is True
    assert tail["truncated"]["same_family_large"] is True
    assert tail["truncated"]["long_context_base"] is False
    assert r5_aperture_route(tail) == tail["predictions"]["long_context_base"]
