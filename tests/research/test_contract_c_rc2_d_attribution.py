"""Frozen assertions for the Contract C RC2-D attribution sweep."""

from __future__ import annotations

from pathlib import Path

from claim_audit_lab.policy import CAL_RULES_V1_2_0

from research_contract_c_rc2_d.sweep import (
    EXPECTED_POLICY_HASH,
    policy_hash,
    run_sweep,
)
from research_contract_c_rc2_d import validator


def _by_family(result: dict[str, object]) -> dict[str, dict[str, object]]:
    receipts = result["receipts"]
    assert isinstance(receipts, list)
    return {
        receipt["family_id"]: receipt
        for receipt in receipts
        if isinstance(receipt, dict) and isinstance(receipt.get("family_id"), str)
    }


def test_frozen_policy_hash_matches_preregistration() -> None:
    assert policy_hash(CAL_RULES_V1_2_0) == EXPECTED_POLICY_HASH


def test_all_preregistered_attribution_controls_pass() -> None:
    result = run_sweep()
    assert result["all_controls_passed"] is True
    assert all(result["controls"].values())


def test_multiplicity_and_residual_classifications_are_preserved() -> None:
    result = run_sweep()
    receipts = _by_family(result)

    assert receipts["tied_independent_support"]["causal_claim"]["classification"] == (
        "independent_sufficient_alternatives"
    )
    assert receipts["absolute_wording_joint"]["causal_claim"]["classification"] == (
        "jointly_sufficient"
    )
    assert receipts["low_reliability_residual"]["causal_claim"]["classification"] == (
        "redundant_non_deciding"
    )
    tied = receipts["tied_independent_support"]
    assert sorted(tied["co_maximal_support_refs"]) == sorted(
        tied["causal_claim"]["members"]
    )


def test_generic_rich_assessments_remain_not_performed() -> None:
    result = run_sweep()
    for receipt in result["receipts"]:
        assert all(
            item["state"] == "not_performed"
            for item in receipt["generic_assessments"].values()
        )


def test_independent_validator_imports_no_cal_production_module() -> None:
    source = Path(validator.__file__).read_text(encoding="utf-8")
    assert "from claim_audit_lab" not in source
    assert "import claim_audit_lab" not in source


def test_no_contract_or_production_promotion_is_claimed() -> None:
    result = run_sweep()
    assert result["bounds"] == {
        "production_change": False,
        "contract_c_version": False,
        "consumer_b_run": False,
        "decision_engine_change": False,
        "contract_b_change": False,
    }
