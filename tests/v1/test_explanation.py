"""Explanation and abstention-classification contract.

The property under test is not "the wording is nice" — it is that an explanation
can never describe a verdict other than the one CAL returned, and that the
abstention classes reproduce the sealed 2026-08-05 decomposition.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claim_audit_lab.v1.explanation import (
    DEFAULT_SIGNAL_FLOOR,
    classify_abstention,
    explain,
    recover_logit_slots,
)
from claim_audit_lab.v1.models import AuditTrace

SCALED_TRACES = (
    Path(__file__).resolve().parents[2].parent
    / "outputs/2026-08-02-qms-claim-generation/scaled-30/cal-audit/traces"
)

# Sealed counts: outputs/2026-08-05-abstention-decomposition/FINDINGS.md,
# corrected by AMENDMENT-01 (9 of the 121 B2 claims carry a refutation signal).
SEALED_ABSTENTION_CLASSES = {
    "read_silent": 112,
    "refutation_stood_down": 9,
    "no_evidence_admitted": 7,
    "ambiguous_support": 7,
}


def _tuplify(obj):
    if isinstance(obj, dict):
        return {k: (tuple(v) if k == "raw_logits" else _tuplify(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_tuplify(x) for x in obj]
    return obj


def _load_scaled() -> list[AuditTrace]:
    return [
        AuditTrace.model_validate(_tuplify(json.loads(p.read_text())))
        for p in sorted(SCALED_TRACES.glob("*.json"))
    ]


requires_scaled = pytest.mark.skipif(
    not SCALED_TRACES.is_dir(), reason="sealed scaled-30 traces not present"
)


@requires_scaled
def test_abstention_classes_reproduce_sealed_decomposition() -> None:
    traces = _load_scaled()
    slots = recover_logit_slots(traces)
    assert slots is not None, "logit slots must be recoverable from the corpus"

    counts: dict[str, int] = {}
    for trace in traces:
        cls = classify_abstention(trace, DEFAULT_SIGNAL_FLOOR, slots)
        if cls:
            counts[cls] = counts.get(cls, 0) + 1

    assert counts == SEALED_ABSTENTION_CLASSES


@requires_scaled
def test_every_abstention_is_classified_and_nothing_else_is() -> None:
    traces = _load_scaled()
    slots = recover_logit_slots(traces)
    for trace in traces:
        cls = classify_abstention(trace, DEFAULT_SIGNAL_FLOOR, slots)
        if trace.verdict.support_verdict == "not_checkable":
            assert cls is not None
        else:
            assert cls is None


@requires_scaled
def test_explanation_never_contradicts_its_verdict() -> None:
    traces = _load_scaled()
    slots = recover_logit_slots(traces)
    for trace in traces:
        result = explain(trace, logit_slots=slots)
        assert result.verdict == trace.verdict.support_verdict
        assert result.claim_id == trace.claim_id
        # An abstention class may only accompany an abstention.
        assert (result.abstention_class is not None) == (
            trace.verdict.support_verdict == "not_checkable"
        )


@requires_scaled
def test_pre_instrumentation_traces_degrade_rather_than_guess() -> None:
    """Without corpus slots, an all-neutral trace must not be given a fine class."""
    traces = _load_scaled()
    coarse = {
        classify_abstention(t, DEFAULT_SIGNAL_FLOOR, None)
        for t in traces
        if t.verdict.support_verdict == "not_checkable"
    }
    assert coarse <= {"read_silent", "no_evidence_admitted", "out_of_scope"}


def _conflict_trace() -> AuditTrace:
    """An A5 abstention: two passages, opposite positions, both above threshold."""
    return AuditTrace.model_validate(
        {
            "claim_id": "conflict-01",
            "claim_text": "The platform validates submitted input records.",
            "retrieval": [
                {"passage_id": "p-1", "score": 0.91},
                {"passage_id": "p-2", "score": 0.89},
            ],
            "entailment": [
                {
                    "passage_id": "p-1",
                    "label": "entail",
                    "score": 0.948,
                    "raw_logits": (3.0, -1.0, -1.0),
                    "p_entail": 0.948,
                    "p_contradict": 0.01,
                },
                {
                    "passage_id": "p-2",
                    "label": "contradict",
                    "score": 0.964,
                    "raw_logits": (-1.0, -1.0, 3.0),
                    "p_entail": 0.01,
                    "p_contradict": 0.964,
                },
            ],
            "features": {
                "sentence_type": "declarative",
                "claim_token_count": 8,
                "has_explicit_negation": False,
                "has_universal_quantifier": False,
                "compound_claim": False,
                "modal_strength": "asserts",
                "numerical_values": [],
            },
            "support_signal": {
                "label": "contradict",
                "max_entailment_score": 0.964,
                "contributing_passage_id": "p-2",
                "best_entail": 0.948,
                "best_entail_passage_id": "p-1",
                "best_contradict": 0.964,
                "best_contradict_passage_id": "p-2",
            },
            "rules_fired": [{"rule_id": "A5_conflicting_evidence", "reason": "both clear"}],
            "verdict": {
                "support_verdict": "not_checkable",
                "support_verdict_reason": "conflicting_evidence",
                "audit_confidence": "low",
            },
            "audit_config_hash": "sha256:" + "0" * 64,
            "library_version": "0.3.0",
        }
    )


def test_a5_abstention_is_explained_as_a_conflict() -> None:
    """The recorded reason governs, so explain cannot disagree with the rule layer."""
    result = explain(_conflict_trace())
    assert result.verdict == "not_checkable"
    assert result.abstention_class == "conflicting_signal"


def test_a5_abstention_keeps_its_class_at_any_signal_floor() -> None:
    """A5 decides at the verdict thresholds; the reporting floor must not re-litigate it."""
    trace = _conflict_trace()
    for floor in (0.0, DEFAULT_SIGNAL_FLOOR, 0.99):
        assert classify_abstention(trace, floor, None) == "conflicting_signal"


def _read_silent_trace(*, n_admitted: int) -> AuditTrace:
    """A B5-neutral abstention with ``n_admitted`` silent passages."""
    entailment = [
        {
            "passage_id": f"p-{i}",
            "label": "neutral",
            "score": 0.99,
            "raw_logits": (-2.0, 4.0, -2.0),
            "p_entail": 0.01,
            "p_contradict": 0.01,
        }
        for i in range(1, n_admitted + 1)
    ]
    return AuditTrace.model_validate(
        {
            "claim_id": f"silent-{n_admitted}",
            "claim_text": "Cold-chain product held at 10 C for 7 hours goes on Quality Hold.",
            "retrieval": [
                {"passage_id": f"p-{i}", "score": 0.80} for i in range(1, n_admitted + 1)
            ],
            "entailment": entailment,
            "features": {
                "numerical_values": [],
                "has_explicit_negation": False,
                "has_universal_quantifier": False,
                "modal_strength": "asserts",
                "claim_token_count": 14,
                "compound_claim": False,
                "sentence_type": "declarative",
            },
            "support_signal": {
                "label": "neutral",
                "max_entailment_score": 0.99,
                "contributing_passage_id": "p-1",
                "best_entail": 0.01,
                "best_contradict": 0.01,
            },
            "rules_fired": [{"rule_id": "B5_degree", "reason": "neutral support signal"}],
            "verdict": {
                "support_verdict": "not_checkable",
                "support_verdict_reason": "no_entail_signal",
                "audit_flags": [],
                "citation_status": "not_applicable",
                "audit_confidence": "low",
            },
            "audit_config_hash": "sha256:" + "0" * 64,
            "library_version": "0.3.0",
        }
    )


def test_read_silent_next_step_does_not_send_reviewer_away_from_a_set() -> None:
    """D13: two admitted silent passages are a composition miss, not a missing source."""
    result = explain(_read_silent_trace(n_admitted=2))
    assert result.abstention_class == "read_silent"
    assert result.next_step is not None
    assert "as a set" in result.next_step
    assert "A different source is needed." not in result.next_step


def test_read_silent_single_passage_still_names_silence_not_absence_of_the_record() -> None:
    result = explain(_read_silent_trace(n_admitted=1))
    assert result.abstention_class == "read_silent"
    assert result.next_step is not None
    assert "No single admitted passage entails this claim" in result.next_step


def test_a7_next_step_asks_which_site() -> None:
    data = _tuplify(json.loads(_read_silent_trace(n_admitted=1).model_dump_json()))
    data["rules_fired"] = [{"rule_id": "A7_scope_mismatch", "reason": "sites differ"}]
    data["verdict"]["support_verdict_reason"] = "out_of_scope"
    result = explain(AuditTrace.model_validate(data))
    assert result.next_step is not None
    assert "Which one is the claim about?" in result.next_step


def test_numeric_silence_asks_about_the_bound() -> None:
    data = _tuplify(json.loads(_read_silent_trace(n_admitted=1).model_dump_json()))
    data["features"]["numerical_values"] = [
        {"value": 10.0, "unit": "degree Celsius", "surface_text": "10 C"}
    ]
    result = explain(AuditTrace.model_validate(data))
    assert result.next_step is not None
    assert "cannot instantiate numeric bounds" in result.next_step
