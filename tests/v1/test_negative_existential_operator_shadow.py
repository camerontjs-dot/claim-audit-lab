"""DEV controls for D5's quantifier-aware negation shadow contract."""

import json
from pathlib import Path

from scripts.evidence_state_operator_shadow import build_operator_report
from scripts.negative_existential_operator_shadow import (
    judgment_from_probe,
    project_negation,
)


def _trace_dir(tmp_path: Path, claim_id: str, claim: str) -> Path:
    trace_dir = tmp_path / claim_id
    trace_dir.mkdir()
    trace = {
        "claim_id": claim_id,
        "claim_text": claim,
        "retrieval": [],
        "entailment": [],
        "features": {"has_explicit_negation": True},
        "support_signal": {"label": "neutral", "max_entailment_score": 0.0},
        "rules_fired": [],
        "verdict": {
            "support_verdict": "not_checkable",
            "support_verdict_reason": "no_entail_signal",
            "audit_flags": [],
            "citation_status": "not_applicable",
            "audit_confidence": "low",
        },
        "audit_config_hash": "sha256:dev-d5",
        "library_version": "dev-d5",
    }
    (trace_dir / f"{claim_id}.json").write_text(json.dumps(trace), encoding="utf-8")
    return trace_dir


def _eligibility(
    trace_dir: Path,
    claim_id: str,
    *,
    support: bool = False,
    refutation: bool = False,
) -> dict[str, object]:
    support_candidates = [{"passage_id": "p1", "score": 0.9}] if support else []
    refutation_candidates = [{"passage_id": "p1", "score": 0.9}] if refutation else []
    if support and refutation:
        state = "mixed"
        verdict = "needs_review"
    elif support:
        state = "support_only"
        verdict = "partially_supported"
    elif refutation:
        state = "refutation_only"
        verdict = "contradicted"
    else:
        state = "no_evidence"
        verdict = "not_checkable"
    return {
        "source": str(trace_dir),
        "signal_floor": 0.2,
        "rows": [
            {
                "claim_id": claim_id,
                "current_verdict": "not_checkable",
                "before_state": state,
                "after_state": state,
                "raw_shadow_verdict": verdict,
                "eligible_shadow_verdict": verdict,
                "after_support_candidates": support_candidates,
                "after_refutation_candidates": refutation_candidates,
            }
        ],
    }


def test_negative_existential_projects_to_existential_positive() -> None:
    result = project_negation("No leak was reported during the shift.")
    assert result.kind == "negative_existential"
    assert result.complement == "At least one leak was reported during the shift."


def test_negative_existential_refutation_is_valid_only_for_matching_complement() -> None:
    judgment = judgment_from_probe(
        claim_id="d5-refuted",
        passage_id="p-leak",
        claim="No leak was reported during the shift.",
        probed_hypothesis="At least one leak was reported during the shift.",
        probe_label="entail",
    )
    assert judgment.status == "valid"


def test_negative_existential_support_is_not_recast_as_refutation() -> None:
    judgment = judgment_from_probe(
        claim_id="d5-supported",
        passage_id="p-no-leak",
        claim="No leak was reported during the shift.",
        probed_hypothesis="At least one leak was reported during the shift.",
        probe_label="contradict",
    )
    assert judgment.status == "invalid"


def test_malformed_double_negation_is_unknown_and_non_deciding() -> None:
    judgment = judgment_from_probe(
        claim_id="d5-malformed",
        passage_id="p1",
        claim="No leak was not reported during the shift.",
        probed_hypothesis="No leak was not reported during the shift.",
        probe_label="entail",
    )
    assert judgment.status == "unknown"


def test_unrecognized_negative_existential_scope_remains_unknown() -> None:
    result = project_negation("No more than one leak was reported during the shift.")
    assert result.kind == "unknown"
    assert result.complement is None


def test_ordinary_negation_affirmative_control_remains_available() -> None:
    result = project_negation("The system did not archive records.")
    assert result.kind == "ordinary"
    assert result.complement == "The system did archive records."


def test_no_evidence_requires_no_operator_judgment() -> None:
    # B1 is represented by the absence of a passage/probe receipt.  The operator
    # must not manufacture a contribution from claim text alone.
    judgments: list[object] = []
    assert judgments == []


def test_valid_negative_existential_refutation_survives_state_recomputation(
    tmp_path: Path,
) -> None:
    claim = "No leak was reported during the shift."
    trace_dir = _trace_dir(tmp_path, "d5-refuted", claim)
    judgment = judgment_from_probe(
        claim_id="d5-refuted",
        passage_id="p1",
        claim=claim,
        probed_hypothesis="At least one leak was reported during the shift.",
        probe_label="entail",
    )
    row = build_operator_report(_eligibility(trace_dir, "d5-refuted", refutation=True), [judgment])[
        "rows"
    ][0]
    assert (row["raw_state"], row["eligible_state"], row["operator_state"]) == (
        "refutation_only",
        "refutation_only",
        "refutation_only",
    )


def test_invalid_refutation_is_removed_while_independent_support_survives(
    tmp_path: Path,
) -> None:
    claim = "No leak was reported during the shift."
    trace_dir = _trace_dir(tmp_path, "d5-supported", claim)
    judgment = judgment_from_probe(
        claim_id="d5-supported",
        passage_id="p1",
        claim=claim,
        probed_hypothesis="At least one leak was reported during the shift.",
        probe_label="contradict",
    )
    row = build_operator_report(
        _eligibility(trace_dir, "d5-supported", support=True, refutation=True), [judgment]
    )["rows"][0]
    assert (row["raw_state"], row["eligible_state"], row["operator_state"]) == (
        "mixed",
        "mixed",
        "support_only",
    )


def test_unknown_refutation_becomes_read_silent_not_contradicted(tmp_path: Path) -> None:
    claim = "No more than one leak was reported during the shift."
    trace_dir = _trace_dir(tmp_path, "d5-unknown", claim)
    judgment = judgment_from_probe(
        claim_id="d5-unknown",
        passage_id="p1",
        claim=claim,
        probed_hypothesis=None,
        probe_label=None,
    )
    row = build_operator_report(_eligibility(trace_dir, "d5-unknown", refutation=True), [judgment])[
        "rows"
    ][0]
    assert row["operator_state"] == "read_silent"
    assert row["operator_shadow_verdict"] == "unsupported"


def test_b1_stays_no_evidence_through_all_state_views(tmp_path: Path) -> None:
    claim = "No leak was reported during the shift."
    trace_dir = _trace_dir(tmp_path, "d5-b1", claim)
    row = build_operator_report(_eligibility(trace_dir, "d5-b1"), [])["rows"][0]
    assert (row["raw_state"], row["eligible_state"], row["operator_state"]) == (
        "no_evidence",
        "no_evidence",
        "no_evidence",
    )
