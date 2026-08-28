from __future__ import annotations

import copy

from contract_c_rc2_research.experiment import (
    PROFILE_ID,
    ablation_matrix,
    canonical_bytes,
    producer_gate,
    render_derived_report,
    semantic_firewall_receipts,
    stable_id,
    validate_candidate,
)


def _candidate() -> dict:
    body = {
        "candidate_profile": PROFILE_ID,
        "input": {
            "contract_b": {
                "contract_version": "1.2.0",
                "bundle_id": "bundle-1",
                "bundle_hash": "sha256:" + "a" * 64,
                "artifact_sha256": "sha256:" + "b" * 64,
                "sha256sums_sha256": "sha256:" + "c" * 64,
            }
        },
        "producer": {
            "name": "claim-audit-lab",
            "code_sha": "3" * 40,
            "library_version": "0.4.0",
            "engine": {"id": "v0.2-lexical", "selection_origin": "cal_compatibility_default"},
            "policy": {"id": "cal-rules-v1.2.0", "contract_b_audit_config_hash": "sha256:" + "d" * 64},
            "operator": {"state": "not_recorded_at_boundary"},
            "model": {"state": "not_applicable", "reason_code": "deterministic_v0_2_engine"},
        },
        "contract_b_context": {"factual_context_state": "absent"},
        "execution": {"status": "completed", "audit_run_id": "run-1", "failures": [], "deviations": []},
        "propositions": [
            {
                "proposition": {"proposition_id": "p1", "text_sha256": "sha256:" + "e" * 64},
                "contributions": [
                    {
                        "contribution_id": "contribution:one",
                        "channel": "support_candidate",
                        "evidence_ref": {
                            "source_id": "s1",
                            "passage_id": "e1",
                            "passage_sha256": "sha256:" + "f" * 64,
                        },
                    }
                ],
                "measurements": [
                    {
                        "measurement_id": "measurement:one",
                        "kind": "cal_v0_2_aggregate_support_signal",
                        "value": 0.8,
                        "operator_id": "claim_audit_lab.rules.assess_claim_support",
                    }
                ],
                "assessments": {
                    "eligibility": {"state": "not_exposed", "reason_code": "no_typed_receipt"},
                    "semantic_validity": {"state": "not_exposed", "reason_code": "no_typed_receipt"},
                    "aperture": {"state": "not_exposed", "reason_code": "no_typed_receipt"},
                    "temporal_applicability": {"state": "not_exposed", "reason_code": "no_typed_receipt"},
                    "citation": {"state": "not_exposed", "reason_code": "no_typed_receipt"},
                },
                "conclusion": {
                    "reported_verdict": "supported",
                    "basis": {
                        "state": "unavailable",
                        "reason_code": "no_deciding_contribution_receipt_at_production_boundary",
                        "available_contribution_ids": ["contribution:one"],
                        "available_rule_receipt_ids": [],
                    },
                    "residual": {"counterevidence_contribution_ids": []},
                    "blockers": [],
                },
                "execution": {"status": "completed", "failures": []},
            }
        ],
    }
    candidate = copy.deepcopy(body)
    candidate["result_set_id"] = stable_id("result-set", body)
    return candidate


def _reidentify(candidate: dict) -> dict:
    body = copy.deepcopy(candidate)
    body.pop("result_set_id", None)
    body["result_set_id"] = stable_id("result-set", body)
    return body


def test_candidate_is_structurally_valid_but_producer_gate_fails_on_real_boundary_gaps() -> None:
    candidate = _candidate()
    assert validate_candidate(candidate) == []
    gate, blockers = producer_gate(candidate)
    assert gate == "FAILED"
    assert any("exact decision basis" in blocker for blocker in blockers)
    assert any("required assessment attribution" in blocker for blocker in blockers)


def test_absent_not_performed_performed_unknown_failed_and_not_applicable_are_not_collapsed() -> None:
    base = _candidate()
    variants = []

    absent = copy.deepcopy(base)
    del absent["propositions"][0]["assessments"]["semantic_validity"]
    variants.append(canonical_bytes(_reidentify(absent)))

    for value in (
        {"state": "not_performed"},
        {"state": "performed", "value": "unknown"},
        {"state": "failed", "failure": {"code": "operator_failure"}},
        {"state": "not_applicable"},
        {"state": "performed", "value": "invalid"},
    ):
        item = copy.deepcopy(base)
        item["propositions"][0]["assessments"]["semantic_validity"] = value
        variants.append(canonical_bytes(_reidentify(item)))

    assert len(set(variants)) == len(variants)


def test_same_verdict_with_different_counterevidence_or_basis_changes_canonical_state() -> None:
    base = _candidate()

    counter = copy.deepcopy(base)
    counter["propositions"][0]["contributions"].append(
        {
            "contribution_id": "contribution:counter",
            "channel": "counterevidence",
            "evidence_ref": {
                "source_id": "s2",
                "passage_id": "e2",
                "passage_sha256": "sha256:" + "1" * 64,
            },
        }
    )
    counter["propositions"][0]["conclusion"]["residual"]["counterevidence_contribution_ids"] = ["contribution:counter"]
    counter = _reidentify(counter)

    basis = copy.deepcopy(base)
    basis["propositions"][0]["conclusion"]["basis"] = {
        "state": "known",
        "contribution_ids": ["contribution:one"],
        "rule_receipt_ids": [],
    }
    basis = _reidentify(basis)

    assert base["propositions"][0]["conclusion"]["reported_verdict"] == "supported"
    assert counter["propositions"][0]["conclusion"]["reported_verdict"] == "supported"
    assert basis["propositions"][0]["conclusion"]["reported_verdict"] == "supported"
    assert canonical_bytes(base) != canonical_bytes(counter)
    assert canonical_bytes(base) != canonical_bytes(basis)


def test_measurement_outcome_is_semantic_but_private_debug_telemetry_is_not_a_public_field() -> None:
    base = _candidate()
    changed = copy.deepcopy(base)
    changed["propositions"][0]["measurements"][0]["value"] = 0.31
    changed = _reidentify(changed)
    assert canonical_bytes(changed) != canonical_bytes(base)

    public_keys = canonical_bytes(base).decode("utf-8")
    for forbidden in ("raw_logits", "retrieval_score", "rationale", "risk_label", "rewrite_guidance"):
        assert forbidden not in public_keys


def test_partial_or_failed_execution_does_not_rewrite_epistemic_conclusion() -> None:
    base = _candidate()
    failed = copy.deepcopy(base)
    failed["propositions"][0]["execution"] = {
        "status": "failed",
        "failures": [{"code": "operator_failure"}],
    }
    failed = _reidentify(failed)
    assert failed["propositions"][0]["conclusion"]["reported_verdict"] == "supported"
    assert canonical_bytes(failed) != canonical_bytes(base)


def test_authority_and_prediction_firewalls_leave_contract_c_bytes_identical() -> None:
    receipt = semantic_firewall_receipts(_candidate())
    assert receipt["identical"] is True
    assert receipt["contract_c_sha256_before"] == receipt["contract_c_sha256_after"]


def test_destination_policy_leakage_is_rejected() -> None:
    leaked = _candidate()
    leaked["propositions"][0]["conclusion"]["risk_tolerance"] = "low"
    leaked = _reidentify(leaked)
    assert any("destination-policy leakage" in error for error in validate_candidate(leaked))


def test_report_derivation_is_deterministic_and_contains_no_destination_authority() -> None:
    candidate = _candidate()
    report_a = render_derived_report(candidate)
    report_b = render_derived_report(candidate)
    assert report_a == report_b
    assert candidate["result_set_id"] in report_a
    assert "authority_profile" not in report_a
    assert "forecast_probability" not in report_a


def test_ablation_matrix_records_semantic_consequences_not_only_need_field_assertions() -> None:
    rows = ablation_matrix(_candidate())
    assert rows
    assert all(row["hard_coded_harness_only"] is False for row in rows)
    assert any(row["removed_structure"] == "input.contract_b" for row in rows)
    assert any(row["removed_structure"] == "propositions[].measurements" for row in rows)
    assert any(row["classification"] == "implementation telemetry" for row in rows)
