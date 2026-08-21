"""Focused contract tests for the bounded D6 aperture packet adapter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.d6_aperture_replay import build_packet

_PROJECT = Path(__file__).resolve().parents[2]
_OUTPUTS = _PROJECT.parent / "outputs"
_SHADOW = _OUTPUTS / "2026-08-06-evidence-state-shadow"
_SCALED = _OUTPUTS / "2026-08-02-qms-claim-generation" / "scaled-30"


def _build(*, probe_path: Path | None = None) -> dict[str, object]:
    return build_packet(
        _SHADOW / "scaled-30-eligibility-shadow.json",
        _SHADOW / "scaled-30-operator-shadow.json",
        claims_path=_SCALED / "claims.json",
        raw_dir=_SCALED / "raw",
        probe_path=probe_path,
    )


def test_frozen_target_universe_has_53_receipt_missing_alternatives() -> None:
    packet = _build()

    assert packet["model_inference"] is False
    assert packet["production_behavior_changed"] is False
    assert packet["target_count"] == 53
    assert packet["target_reason_counts"] == {
        "A4 recorded no semantic probe for this passage": 37,
        "the recorded structural negator abstained; unknown may not decide": 16,
    }
    assert packet["assessment_counts"] == {"unknown": 53}
    assert packet["blocking_target_count"] == 53
    assert all(item["trace"]["ordinary_entailment_receipt"] for item in packet["targets"])
    assert all(
        "missing_alternative_a4_probe_receipt" in item["blockers"] for item in packet["targets"]
    )


def test_ordinary_contradiction_receipt_does_not_become_a4_validity() -> None:
    packet = _build()
    ordinary_contradiction = next(
        item
        for item in packet["targets"]
        if item["trace"]["ordinary_entailment_receipt"]["label"] == "contradict"
    )

    assert ordinary_contradiction["assessment"]["status"] == "unknown"
    assert ordinary_contradiction["probe_receipt"] is None


def test_exact_probe_receipt_can_assess_one_target_without_inference(tmp_path: Path) -> None:
    baseline = _build()
    target = baseline["targets"][0]
    hypothesis = target["trace"]["negation_probe_state"]["negated_claim"]
    if hypothesis is None:
        hypothesis = "frozen future A4 hypothesis"
    probe_path = tmp_path / "probe-receipts.json"
    probe_path.write_text(
        json.dumps(
            {
                "schema_version": "cal-d6-probe-receipts-v1",
                "receipts": [
                    {
                        "claim_id": target["claim_id"],
                        "passage_id": target["passage_id"],
                        "hypothesis": hypothesis,
                        "label": "entail",
                        "score": 0.91,
                        "raw_logits": [2.0, -1.0, -2.0],
                        "model_id": "fixture-only-contract-test",
                        "model_revision": "fixture",
                        "config_hash": "sha256:" + "1" * 64,
                        "evidence_path": "fixture-only; not CAL evidence",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    packet = _build(probe_path=probe_path)
    assessed = next(
        item
        for item in packet["targets"]
        if item["claim_id"] == target["claim_id"] and item["passage_id"] == target["passage_id"]
    )
    assert assessed["assessment"]["status"] == "valid"
    assert assessed["assessment"]["receipt_sha256"].startswith("sha256:")
    assert packet["assessment_counts"] == {"unknown": 52, "valid": 1}


def test_probe_receipt_mismatch_fails_closed(tmp_path: Path) -> None:
    baseline = _build()
    target = baseline["targets"][0]
    probe_path = tmp_path / "probe-receipts.json"
    probe_path.write_text(
        json.dumps(
            {
                "schema_version": "cal-d6-probe-receipts-v1",
                "receipts": [
                    {
                        "claim_id": target["claim_id"],
                        "passage_id": "not-the-frozen-passage",
                        "hypothesis": "wrong",
                        "label": "entail",
                        "score": 0.91,
                        "raw_logits": [2.0, -1.0, -2.0],
                        "model_id": "fixture-only-contract-test",
                        "model_revision": "fixture",
                        "config_hash": "sha256:" + "1" * 64,
                        "evidence_path": "fixture-only; not CAL evidence",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="outside the frozen target universe"):
        _build(probe_path=probe_path)
