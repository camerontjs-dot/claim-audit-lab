"""Fast tests for the premise-granularity DEV prototype (no model loads)."""

from __future__ import annotations

import spacy

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import (
    AuditRequest,
    AuditTrace,
    EntailResult,
    ExtractedFeatures,
    Passage,
    RetrievalResult,
    SupportSignal,
    Verdict,
)
from scripts.pilot001_premise_granularity_run04 import (
    build_premise_fragments,
    build_variant_trace,
    is_fallback_target,
)


def _nlp():
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    return nlp


def _baseline(config, *, reason: str | None = "no_entail_signal") -> AuditTrace:
    return AuditTrace(
        claim_id="c1",
        claim_text="The quality system supports CAPA.",
        retrieval=[RetrievalResult(passage_id="p1", score=0.8)],
        entailment=[
            EntailResult(
                passage_id="p1",
                label="neutral",
                score=0.9,
                raw_logits=(0.0, 1.0, 0.0),
            )
        ],
        features=ExtractedFeatures(claim_token_count=6),
        support_signal=SupportSignal(
            label="neutral",
            max_entailment_score=0.9,
            contributing_passage_id="p1",
        ),
        rules_fired=[],
        verdict=Verdict(
            support_verdict="not_checkable",
            support_verdict_reason=reason,
            audit_confidence="low",
        ),
        audit_config_hash="sha256:test",
        library_version="test",
    )


def test_build_premise_fragments_is_deterministic_and_inherits_parent_provenance() -> None:
    passage = Passage(
        passage_id="source/p1",
        text="1. CAPA is required. It prevents recurrence.",
        source_meta={"trust_level": "primary", "source_id": "source"},
    )

    fragments = build_premise_fragments(passage, _nlp(), window_sizes=(1, 2))

    assert [fragment.passage_id for fragment in fragments] == [
        "source/p1#s0002-0002",
        "source/p1#s0003-0003",
        "source/p1#s0002-0003",
    ]
    assert fragments[0].text == "CAPA is required."
    assert fragments[2].text == "CAPA is required. It prevents recurrence."
    assert fragments[2].source_meta == {
        "trust_level": "primary",
        "source_id": "source",
        "parent_passage_id": "source/p1",
        "premise_sentence_start": "2",
        "premise_sentence_end": "3",
        "premise_window_size": "2",
    }


def test_build_premise_fragments_rejects_invalid_window_sizes() -> None:
    passage = Passage(passage_id="p1", text="A sentence.")
    for widths in ((), (0,), (1, 1)):
        try:
            build_premise_fragments(passage, _nlp(), window_sizes=widths)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {widths}")


def test_is_fallback_target_requires_raw_neutral_no_entail_with_parent_results() -> None:
    config = load_default_audit_config()
    baseline = _baseline(config)
    assert is_fallback_target(baseline)
    assert not is_fallback_target(
        baseline.model_copy(
            update={
                "support_signal": SupportSignal(
                    label="entail",
                    max_entailment_score=0.8,
                    contributing_passage_id="p1",
                )
            }
        )
    )
    assert not is_fallback_target(_baseline(config, reason="no_evidence"))
    assert not is_fallback_target(baseline.model_copy(update={"entailment": []}))


def test_build_variant_trace_recovers_from_a_fragment_and_marks_prototype_rule() -> None:
    config = load_default_audit_config()
    baseline = _baseline(config)
    request = AuditRequest(
        claim_id="c1",
        claim_text=baseline.claim_text,
        passages=[
            Passage(
                passage_id="p1",
                text="CAPA is required. It prevents recurrence.",
                source_meta={"trust_level": "primary"},
            )
        ],
        audit_config=config,
    )
    fragments = build_premise_fragments(request.passages[0], _nlp(), window_sizes=(1, 2))
    fragment_results = [
        EntailResult(
            passage_id=fragment.passage_id,
            label=("entail" if fragment.passage_id.endswith("s0001-0001") else "neutral"),
            score=(0.95 if fragment.passage_id.endswith("s0001-0001") else 0.9),
            raw_logits=(
                (2.0, 0.0, -1.0) if fragment.passage_id.endswith("s0001-0001") else (0.0, 2.0, -1.0)
            ),
        )
        for fragment in fragments
    ]

    candidate = build_variant_trace(
        request,
        baseline,
        fragments,
        fragment_results,
        config,
        VerdictRules(rules_file_sha=config.rules_file_sha),
        variant="s1",
    )

    assert candidate.verdict.support_verdict == "supported"
    assert candidate.support_signal.contributing_passage_id == "p1#s0001-0001"
    assert candidate.rules_fired[0].rule_id == "PG_premise_fallback"
    assert len(candidate.entailment) == 3
    assert all("#s0001-0002" not in result.passage_id for result in candidate.entailment)
