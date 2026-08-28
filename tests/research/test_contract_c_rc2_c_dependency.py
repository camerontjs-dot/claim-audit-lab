"""RC2-C research tests for the frozen evidence-to-rule dependency seam."""

from __future__ import annotations

from research_contract_c_rc2_c.dependency_probe import (
    CAL_RULES_V1_2_0,
    EXPECTED_POLICY_HASH,
    policy_hash,
    run_experiment,
)


def test_frozen_policy_hash_matches_preregistration() -> None:
    assert policy_hash(CAL_RULES_V1_2_0) == EXPECTED_POLICY_HASH


def test_all_preregistered_dependency_controls_pass() -> None:
    result = run_experiment()
    assert result["all_controls_passed"] is True
    assert all(result["controls"].values())


def test_no_contract_or_production_promotion_is_claimed() -> None:
    result = run_experiment()
    assert result["bounds"]["production_change"] is False
    assert result["bounds"]["rule_family_scope"] == (
        "absolute-wording/counterevidence seam only"
    )
