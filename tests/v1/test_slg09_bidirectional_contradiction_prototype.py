"""Pure contract tests for the non-landing SLG-09 prototype guard."""

from __future__ import annotations

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.models import (
    AuditTrace,
    EntailResult,
    ExtractedFeatures,
    RetrievalResult,
    RuleFired,
    SupportSignal,
    Verdict,
)
from scripts.slg09_bidirectional_contradiction_prototype import (
    _a4_contradiction,
    _candidate_verdict,
    _trace_from_json_payload,
    _tree_sha256,
)


def _trace() -> AuditTrace:
    return AuditTrace(
        claim_id="case",
        claim_text="The parcel was sealed.",
        retrieval=[RetrievalResult(passage_id="p", score=0.8)],
        entailment=[
            EntailResult(
                passage_id="p",
                label="contradict",
                score=0.97,
                raw_logits=(0.0, 0.0, 1.0),
            )
        ],
        features=ExtractedFeatures(claim_token_count=5),
        support_signal=SupportSignal(
            label="contradict", max_entailment_score=0.97, contributing_passage_id="p"
        ),
        rules_fired=[RuleFired(rule_id="A4_hard_contradiction", reason="fixture")],
        verdict=Verdict(support_verdict="contradicted", audit_confidence="high"),
        audit_config_hash="sha256:fixture",
        library_version="fixture",
    )


def test_candidate_keeps_bidirectionally_high_contradiction() -> None:
    trace = _trace()
    threshold = load_default_audit_config().contradicted_threshold
    assert _a4_contradiction(trace) is True
    assert _candidate_verdict(trace, "contradict", threshold, threshold) == trace.verdict


def test_candidate_only_simulates_safe_demote_for_directional_inconsistency() -> None:
    threshold = load_default_audit_config().contradicted_threshold
    verdict = _candidate_verdict(_trace(), "neutral", 0.99, threshold)
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "no_entail_signal"


def test_json_mode_trace_restores_strict_logits_tuple() -> None:
    trace = _trace()
    restored = _trace_from_json_payload(trace.model_dump(mode="json"))
    assert restored == trace


def test_candidate_uses_supplied_threshold_not_a_hard_coded_value() -> None:
    threshold = load_default_audit_config().contradicted_threshold
    above_threshold = min(1.0, threshold + 0.05)
    assert (
        _candidate_verdict(_trace(), "contradict", above_threshold, threshold).support_verdict
        == "contradicted"
    )
    assert (
        _candidate_verdict(
            _trace(), "contradict", above_threshold, min(1.0, threshold + 0.10)
        ).support_verdict
        == "not_checkable"
    )


def test_tree_hash_binds_relative_paths_and_raw_bytes(tmp_path) -> None:
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "a.txt").write_bytes(b"same")
    first = _tree_sha256(tree)
    (tree / "nested").mkdir()
    (tree / "nested" / "b.txt").write_bytes(b"same")
    assert _tree_sha256(tree) != first
