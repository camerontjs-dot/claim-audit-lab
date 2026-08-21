"""Inference-free replay controls for the strict candidate adapter."""

from __future__ import annotations

from pathlib import Path

from scripts.decision_model_replay import build_report

_PROJECT = Path(__file__).resolve().parents[2]
_OUTPUTS = _PROJECT.parent / "outputs"


def _report(eligibility: Path, operator: Path) -> dict[str, object]:
    return build_report(
        eligibility,
        operator,
        support_threshold=0.70,
        refutation_threshold=0.70,
    )


def test_pinned_d5_replay_has_only_the_two_preregistered_changes() -> None:
    base = _OUTPUTS / "2026-08-07-negative-existential-packet" / "pinned-entailer-replay"
    report = _report(base / "eligibility-shadow.json", base / "operator-shadow.json")
    rows = {row["claim_id"]: row for row in report["rows"]}  # type: ignore[index]

    assert report["model_inference"] is False
    assert report["production_behavior_changed"] is False
    assert report["candidate_outcome_counts"] == {
        "abstain": 2,
        "contradicted": 2,
        "supported": 1,
    }
    assert rows["d5-supported"]["candidate_outcome"] == "supported"
    assert rows["d5-refuted"]["candidate_outcome"] == "contradicted"
    assert rows["d5-insufficient"]["candidate_outcome"] == "abstain"
    assert rows["ordinary-refuted"]["candidate_outcome"] == "contradicted"
    assert rows["d5-ambiguous"]["candidate_outcome"] == "abstain"
    assert rows["d5-ambiguous"]["candidate"]["decision"]["reason_code"] == (
        "semantic_validity_unknown"
    )


def test_scaled_and_pilot_replays_add_no_adverse_decision() -> None:
    base = _OUTPUTS / "2026-08-06-evidence-state-shadow"
    expected = {
        "scaled-30": {
            "n_claims": 210,
            "candidate_outcome_counts": {"abstain": 188, "contradicted": 1, "supported": 21},
            "n_changed": 53,
            "n_adapter_exclusions": 1,
        },
        "pilot-001": {
            "n_claims": 98,
            "candidate_outcome_counts": {"abstain": 74, "supported": 24},
            "n_changed": 48,
            "n_adapter_exclusions": 0,
        },
    }
    for name, wanted in expected.items():
        report = _report(
            base / f"{name}-eligibility-shadow.json",
            base / f"{name}-operator-shadow.json",
        )
        for key, value in wanted.items():
            assert report[key] == value
        assert report["n_new_contradicted"] == 0
        assert report["n_support_to_adverse"] == 0
        changed = [row for row in report["rows"] if row["changed"]]  # type: ignore[index]
        assert all(row["candidate_outcome"] == "abstain" for row in changed)


def test_scaled_replay_reproduces_corrected_abstention_strata() -> None:
    base = _OUTPUTS / "2026-08-06-evidence-state-shadow"
    report = _report(
        base / "scaled-30-eligibility-shadow.json",
        base / "scaled-30-operator-shadow.json",
    )
    assert report["legacy_stratum_counts"] == {
        "B1_no_evidence": 7,
        "B2a_read_silent": 112,
        "B2b_refutation_signal_on_legacy_abstention": 9,
        "B3_support_signal_discarded_by_legacy": 7,
    }


def test_policy_stage_receipts_name_the_inline_policy_and_hash_it() -> None:
    base = _OUTPUTS / "2026-08-07-negative-existential-packet" / "pinned-entailer-replay"
    report = _report(base / "eligibility-shadow.json", base / "operator-shadow.json")
    stage_receipts = report["rows"][0]["candidate"]["inputs"]["stage_receipts"]
    policy_stages = [item for item in stage_receipts if item["stage"] in {"aggregate", "resolve"}]

    assert [item["evidence_path"] for item in policy_stages] == [
        "policy:cal-decision-model-replay-v0.1",
        "policy:cal-decision-model-replay-v0.1",
    ]
    assert all(item["receipt_sha256"] == report["policy_receipt_sha256"] for item in policy_stages)
