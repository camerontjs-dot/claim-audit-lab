"""Contract C RC2-A1: diagnose the production semantic-boundary gap.

Research-only. These tests do not alter production semantics. They probe what
current v0.2 production actually computes and what can be reconstructed from
its legitimate result state.
"""

from __future__ import annotations

import inspect
from datetime import date as Date

import claim_audit_lab.rules as rules
from claim_audit_lab.contracts.output_writer import write_audited_bundle
from claim_audit_lab.models import (
    AuditConfig,
    Claim,
    ClaimAssessment,
    EvidenceBundle,
    EvidenceCandidate,
    EvidenceExcerpt,
    EvidenceSource,
)
from claim_audit_lab.rules import assess_claim_support
from claim_audit_lab.v1 import decision_model


def _claim(text: str = "The tool can generate audit summaries.") -> Claim:
    return Claim(id="claim-rc2-a1", text=text, claim_type="capability")


def _bundle(
    text: str = "The tool can generate audit summaries.",
    *,
    reliability: str = "high",
    source_date: Date | None = Date(2026, 1, 1),
    url: str | None = "https://example.test/source",
) -> EvidenceBundle:
    return EvidenceBundle(
        sources=[
            EvidenceSource(
                id="source-1",
                title="RC2-A1 source",
                reliability=reliability,
                date=source_date,
                url=url,
                excerpts=[EvidenceExcerpt(id="excerpt-1", text=text)],
            )
        ]
    )


def _candidate(
    *,
    excerpt_id: str = "excerpt-1",
    score: float = 0.9,
    reliability: str = "high",
    source_date: Date | None = Date(2026, 1, 1),
    url: str | None = "https://example.test/source",
) -> EvidenceCandidate:
    return EvidenceCandidate(
        source_id="source-1",
        excerpt_id=excerpt_id,
        score=score,
        source_reliability=reliability,
        source_date=source_date,
        source_url=url,
    )


def _codes(assessment: ClaimAssessment) -> set[str]:
    return {flag.code for flag in assessment.rule_flags}


def test_public_claim_assessment_has_no_generic_rich_assessment_receipts() -> None:
    """The legitimate v0.2 result object does not expose the RC1 shadow families."""
    fields = set(ClaimAssessment.model_fields)
    assert {
        "claim",
        "support_label",
        "risk_label",
        "candidate_evidence",
        "counterevidence",
        "support_signal",
        "rule_flags",
        "explanation",
        "rewrite_guidance",
        "limitations",
    } == fields
    assert not {
        "eligibility",
        "semantic_validity",
        "aperture",
        "temporal_applicability",
        "citation",
        "decision_basis",
        "supersedes",
    } & fields


def test_exact_v02_verdict_path_is_reconstructable_from_legitimate_result_state() -> None:
    """Recompute the exact production branch without a new epistemic assessment."""
    claim = _claim()
    bundle = _bundle()
    support = [_candidate(score=0.90)]
    counter = [_candidate(score=0.50)]
    assessment = assess_claim_support(claim, bundle, support, counterevidence=counter)

    support_contexts = rules._build_contexts(assessment.candidate_evidence, bundle)
    counter_contexts = rules._build_contexts(assessment.counterevidence, bundle)
    direct_contexts = [
        context for context in support_contexts if rules._is_direct_support(claim, context)
    ]
    signal = rules._support_signal(support_contexts, counter_contexts, rules.CAL_RULES_V1_2_0)
    flags = rules._build_rule_flags(
        claim,
        support_contexts,
        counter_contexts,
        direct_contexts,
        bundle,
        AuditConfig(),
        rules.CAL_RULES_V1_2_0,
    )
    verdict = rules._support_label(
        support_contexts,
        counter_contexts,
        flags,
        signal,
        rules.CAL_RULES_V1_2_0,
    )

    assert signal == assessment.support_signal == 0.75
    assert flags == assessment.rule_flags
    assert verdict == assessment.support_label == "partially_supported"
    assert max(c.score for c in assessment.candidate_evidence) == 0.90
    assert max(c.score for c in assessment.counterevidence) == 0.50
    assert _codes(assessment) == {"counterevidence_present"}


def test_low_reliability_is_a_rule_limitation_not_an_eligibility_gate() -> None:
    """Low reliability remains in the scalar; production does not exclude it as ineligible."""
    claim = _claim()
    bundle = _bundle(reliability="low")
    assessment = assess_claim_support(
        claim,
        bundle,
        [_candidate(score=0.80, reliability="low")],
    )

    assert assessment.support_signal == 0.80
    assert assessment.support_label == "partially_supported"
    assert _codes(assessment) == {"low_reliability_only"}
    assert assessment.candidate_evidence[0].source_reliability == "low"


def test_direct_support_predicate_is_not_a_generic_semantic_validity_gate() -> None:
    """A passage can fail the private direct-support predicate yet still drive the scalar."""
    claim = _claim()
    bundle = _bundle("The tool can generate audit summaries but is not tested.")
    candidate = _candidate(score=0.90)
    contexts = rules._build_contexts([candidate], bundle)

    assert rules._is_direct_support(claim, contexts[0]) is False

    assessment = assess_claim_support(claim, bundle, [candidate])
    assert assessment.support_signal == 0.90
    assert assessment.support_label == "supported"


def test_stale_source_is_narrow_freshness_not_general_temporal_applicability() -> None:
    """Production has an attributable freshness rule, but no applicability result field."""
    claim = _claim()
    old = Date(2024, 1, 1)
    bundle = _bundle(source_date=old)
    assessment = assess_claim_support(
        claim,
        bundle,
        [_candidate(score=0.80, source_date=old)],
        AuditConfig(reference_date=Date(2026, 1, 2), freshness_days=365),
    )

    assert assessment.support_signal == 0.80
    assert assessment.support_label == "partially_supported"
    assert _codes(assessment) == {"stale_source"}
    assert "temporal_applicability" not in ClaimAssessment.model_fields


def test_public_link_missing_source_is_not_a_generic_citation_assessment() -> None:
    """The URL rule is claim-specific and does not establish a citation-status axis."""
    claim = Claim(
        id="claim-public-link",
        text="The portfolio is published on GitHub.",
        claim_type="capability",
    )
    bundle = _bundle("The portfolio is published on GitHub.", url=None)
    assessment = assess_claim_support(
        claim,
        bundle,
        [_candidate(score=0.90, url=None)],
    )

    assert assessment.support_label == "needs_source"
    assert _codes(assessment) == {"public_link_missing_source"}
    assert "citation" not in ClaimAssessment.model_fields
    assert "citation_status" not in ClaimAssessment.model_fields


def test_shadow_assessment_and_basis_types_are_explicitly_additive() -> None:
    """Rich decision-state types exist, but their own module denies production authority."""
    doc = decision_model.__doc__ or ""
    assert "additive module" in doc
    assert "does not alter" in doc
    assert "production verdict path" in doc
    assert hasattr(decision_model, "EligibilityAssessment")
    assert hasattr(decision_model, "ValidityAssessment")
    assert hasattr(decision_model, "ChannelApertureAssessment")
    assert "basis_contribution_ids" in decision_model.DecisionOutcome.model_fields


def test_current_compatibility_writer_has_run_identity_but_no_result_lineage_relation() -> None:
    """A run ID is persisted; a supersession/prior-result relation is not."""
    source = inspect.getsource(write_audited_bundle)
    assert "audit_run_id" in source
    assert "supersed" not in source
    assert "prior_result" not in source
    assert "previous_result" not in source
