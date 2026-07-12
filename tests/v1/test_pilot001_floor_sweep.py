"""Fast tests for the PILOT-001 floor-sweep diff tooling (no model loads)."""

from __future__ import annotations

from claim_audit_lab.v1.calibrate import CalibrationGold, GoldClaim
from claim_audit_lab.v1.models import (
    AuditTrace,
    ExtractedFeatures,
    SupportSignal,
    Verdict,
)
from scripts.pilot001_floor_sweep import build_diff_rows, classify_diff


def _trace(claim_id: str, verdict: str, *, admitted: tuple[str, ...] = ()) -> AuditTrace:
    from claim_audit_lab.v1.models import EntailResult

    return AuditTrace.model_validate(
        {
            "claim_id": claim_id,
            "claim_text": f"claim {claim_id}",
            "retrieval": [],
            "entailment": [
                EntailResult(
                    passage_id=passage_id,
                    label="neutral",
                    score=0.9,
                    raw_logits=(0.0, 1.0, 0.0),
                )
                for passage_id in admitted
            ],
            "features": ExtractedFeatures(),
            "support_signal": SupportSignal(label="neutral", max_entailment_score=0.0),
            "rules_fired": [],
            "verdict": Verdict(support_verdict=verdict),
            "audit_config_hash": "sha256:test",
            "library_version": "test",
        }
    )


def _gold() -> CalibrationGold:
    return CalibrationGold(
        gold_version="test",
        claims=[
            GoldClaim(claim_id="recovered", condition="c", model="m", gold_verdict="supported"),
            GoldClaim(claim_id="regressed", condition="c", model="m", gold_verdict="supported"),
            GoldClaim(claim_id="still-miss", condition="c", model="m", gold_verdict="supported"),
            GoldClaim(
                claim_id="unchanged-match",
                condition="c",
                model="m",
                gold_verdict="partially_supported",
            ),
            GoldClaim(
                claim_id="unchanged-miss",
                condition="c",
                model="m",
                gold_verdict="contradicted",
            ),
        ],
    )


def test_classify_diff_all_categories() -> None:
    assert classify_diff("supported", "not_checkable", "supported") == "recovered"
    assert classify_diff("supported", "supported", "contradicted") == "regressed"
    assert classify_diff("supported", "not_checkable", "contradicted") == "changed_but_still_miss"
    assert (
        classify_diff("partially_supported", "partially_supported", "partially_supported")
        == "unchanged_match"
    )
    assert classify_diff("contradicted", "unsupported", "unsupported") == "unchanged_miss"


def test_build_diff_rows_counts_recovery_regression_and_new_false_contradictions() -> None:
    baseline = {
        "recovered": _trace("recovered", "not_checkable"),
        "regressed": _trace("regressed", "supported", admitted=("p1",)),
        "still-miss": _trace("still-miss", "not_checkable"),
        "unchanged-match": _trace("unchanged-match", "partially_supported"),
        "unchanged-miss": _trace("unchanged-miss", "unsupported"),
    }
    candidate = {
        "recovered": _trace("recovered", "supported", admitted=("p2",)),
        "regressed": _trace("regressed", "contradicted", admitted=("p1", "p3")),
        "still-miss": _trace("still-miss", "contradicted"),
        "unchanged-match": _trace("unchanged-match", "partially_supported"),
        "unchanged-miss": _trace("unchanged-miss", "unsupported"),
    }

    rows, summary = build_diff_rows(_gold(), baseline, candidate)

    assert summary == {
        "claims": 5,
        "recovered": 1,
        "regressed": 1,
        "changed_but_still_miss": 1,
        "unchanged_match": 1,
        "unchanged_miss": 1,
        "verdict_changed": 3,
        "new_gold_supported_to_cal_contradicted": 2,
        "new_gold_supported_to_cal_contradicted_claim_ids": ["regressed", "still-miss"],
    }
    by_id = {row["claim_id"]: row for row in rows}
    assert by_id["recovered"]["newly_admitted_passage_ids"] == "p2"
    assert by_id["regressed"]["newly_admitted_passage_ids"] == "p3"
