"""Controls for the shadow-only operator-validity projection."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.evidence_state_operator_shadow import OperatorJudgment, build_operator_report


def _trace_dir(tmp_path: Path) -> Path:
    trace_dir = tmp_path / "traces"
    trace_dir.mkdir()
    trace = {
        "claim_id": "c1",
        "claim_text": "The system does not archive records.",
        "retrieval": [],
        "entailment": [],
        "features": {"has_explicit_negation": True},
        "support_signal": {
            "label": "neutral",
            "max_entailment_score": 0.9,
            "contributing_passage_id": "p1",
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
    (trace_dir / "c1.json").write_text(json.dumps(trace), encoding="utf-8")
    return trace_dir


def _eligibility(trace_dir: Path) -> dict[str, object]:
    candidate = {"passage_id": "p1", "score": 0.9}
    return {
        "source": str(trace_dir),
        "signal_floor": 0.2,
        "rows": [
            {
                "claim_id": "c1",
                "current_verdict": "not_checkable",
                "before_state": "refutation_only",
                "after_state": "refutation_only",
                "raw_shadow_verdict": "contradicted",
                "eligible_shadow_verdict": "contradicted",
                "after_support_candidates": [],
                "after_refutation_candidates": [candidate],
            }
        ],
    }


def test_unknown_operator_contribution_is_explicit_and_non_deciding(tmp_path: Path) -> None:
    trace_dir = _trace_dir(tmp_path)
    judgment = OperatorJudgment(
        claim_id="c1",
        channel="refutation",
        passage_ids=("p1",),
        status="unknown",
        operator="negation_consistency",
        reason="structural negator abstained",
        evidence_path="fixture",
    )
    report = build_operator_report(_eligibility(trace_dir), [judgment])
    row = report["rows"][0]
    assert row["operator_state"] == "read_silent"
    assert row["operator_shadow_verdict"] == "unsupported"
    assert row["excluded_operator_contributions"][0]["judgments"][0]["status"] == "unknown"


def test_valid_affirmative_refutation_is_preserved(tmp_path: Path) -> None:
    trace_dir = _trace_dir(tmp_path)
    judgment = OperatorJudgment(
        claim_id="c1",
        channel="refutation",
        passage_ids=("p1",),
        status="valid",
        operator="negation_consistency",
        reason="same passage entails the structurally negated claim",
        evidence_path="fixture",
    )
    report = build_operator_report(_eligibility(trace_dir), [judgment])
    row = report["rows"][0]
    assert row["operator_state"] == "refutation_only"
    assert row["operator_shadow_verdict"] == "contradicted"


def test_invalid_derived_refutation_is_audited_without_entering_state(tmp_path: Path) -> None:
    trace_dir = _trace_dir(tmp_path)
    eligibility = _eligibility(trace_dir)
    eligibility["rows"][0]["after_state"] = "read_silent"  # type: ignore[index]
    eligibility["rows"][0]["eligible_shadow_verdict"] = "unsupported"  # type: ignore[index]
    eligibility["rows"][0]["after_refutation_candidates"] = []  # type: ignore[index]
    judgment = OperatorJudgment(
        claim_id="c1",
        channel="refutation",
        passage_ids=("p1",),
        status="invalid",
        operator="A3_partial_conjunct_mirror",
        reason="unary mirror is invalid over one negated conjunct",
        evidence_path="fixture",
        derived=True,
        score=0.9,
    )
    report = build_operator_report(eligibility, [judgment])
    row = report["rows"][0]
    assert row["operator_state"] == "read_silent"
    assert row["excluded_operator_contributions"][0]["derived"] is True


def test_manifest_operator_supersedes_recorded_operator_for_same_contribution(
    tmp_path: Path,
) -> None:
    trace_dir = _trace_dir(tmp_path)
    trace_path = trace_dir / "c1.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["negation_probe"] = {
        "negated_claim": "The system archives records.",
        "abstained": False,
        "result": {
            "passage_id": "p1",
            "label": "neutral",
            "score": 0.9,
            "raw_logits": [0.0, 1.0, 0.0],
        },
    }
    trace_path.write_text(json.dumps(trace), encoding="utf-8")
    replacement = OperatorJudgment(
        claim_id="c1",
        channel="refutation",
        passage_ids=("p1",),
        status="valid",
        operator="quantifier_aware_negation",
        reason="canonical complement is entailed",
        evidence_path="fixture receipt",
    )
    row = build_operator_report(_eligibility(trace_dir), [replacement])["rows"][0]
    assert row["operator_state"] == "refutation_only"
    assert row["operator_judgments"] == [replacement.model_dump()]
    assert row["superseded_operator_judgments"][0]["operator"] == "A4_negation_consistency"
