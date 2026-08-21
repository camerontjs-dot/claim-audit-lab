"""Tests for analysis-only production-P1 state recomputation."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.evidence_state_eligibility_shadow import build_eligibility_report


def test_non_primary_refutation_is_removed_but_support_is_retained(tmp_path: Path) -> None:
    trace = {
        "claim_id": "c1",
        "claim_text": "The system records each review outcome.",
        "retrieval": [],
        "entailment": [
            {
                "passage_id": "background/p1",
                "label": "neutral",
                "score": 0.8,
                "raw_logits": [0.0, 0.0, 0.0],
                "p_entail": 0.7,
                "p_contradict": 0.8,
            }
        ],
        "features": {},
        "support_signal": {
            "label": "neutral",
            "max_entailment_score": 0.8,
            "contributing_passage_id": "background/p1",
        },
        "rules_fired": [],
        "verdict": {
            "support_verdict": "not_checkable",
            "support_verdict_reason": "no_entail_signal",
            "audit_flags": [],
            "citation_status": "not_applicable",
            "audit_confidence": "low",
        },
        "audit_config_hash": "sha256:test",
        "library_version": "test",
    }
    trace_dir = tmp_path / "traces"
    trace_dir.mkdir()
    (trace_dir / "c1.json").write_text(json.dumps(trace), encoding="utf-8")
    report = build_eligibility_report(
        trace_dir, signal_floor=0.20, trust_by_source={"background": "background"}
    )
    row = report["rows"][0]
    assert row["before_state"] == "mixed"
    assert row["after_state"] == "support_only"
    assert row["after_support_candidates"]
    assert row["after_refutation_candidates"] == []
    assert row["excluded_contributions"][0]["trust_level"] == "background"


def test_absent_trust_remains_eligible_like_production(tmp_path: Path) -> None:
    trace = {
        "claim_id": "c1",
        "claim_text": "The system records each review outcome.",
        "retrieval": [],
        "entailment": [
            {
                "passage_id": "direct/p1",
                "label": "neutral",
                "score": 0.8,
                "raw_logits": [0.0, 0.0, 0.0],
                "p_entail": 0.1,
                "p_contradict": 0.8,
            }
        ],
        "features": {},
        "support_signal": {
            "label": "neutral",
            "max_entailment_score": 0.8,
            "contributing_passage_id": "direct/p1",
        },
        "rules_fired": [],
        "verdict": {
            "support_verdict": "not_checkable",
            "support_verdict_reason": "no_entail_signal",
            "audit_flags": [],
            "citation_status": "not_applicable",
            "audit_confidence": "low",
        },
        "audit_config_hash": "sha256:test",
        "library_version": "test",
    }
    trace_dir = tmp_path / "traces"
    trace_dir.mkdir()
    (trace_dir / "c1.json").write_text(json.dumps(trace), encoding="utf-8")
    report = build_eligibility_report(trace_dir, signal_floor=0.20, trust_by_source={})
    row = report["rows"][0]
    assert row["before_state"] == "refutation_only"
    assert row["after_state"] == "refutation_only"
    assert row["excluded_contributions"] == []
