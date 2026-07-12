"""Tests for Phase 6 audit orchestration hardening."""

from __future__ import annotations

import re
from pathlib import Path

from claim_audit_lab.auditor import audit_document
from claim_audit_lab.claim_extraction import extract_claims
from claim_audit_lab.loader import load_draft, load_evidence_bundle
from claim_audit_lab.models import AuditConfig, AuditReport, DraftDocument, EvidenceBundle

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = PROJECT_ROOT / "examples"
ELIMINATES_CLAIM = (
    "The intervention clearly eliminates unsupported claims in multi-step AI research workflows."
)
REDUCTION_CLAIM = (
    "Unsupported claims fell from 18 outputs to 11 outputs after the provenance checklist "
    "was added."
)
FORBIDDEN_CAPABILITY_PATTERNS = (
    r"\bfact checked\b",
    r"\bverified\b",
    r"\bproven\b",
    r"\btrue\b",
    r"\bfalse\b",
)


def _ai_research_inputs() -> tuple[DraftDocument, EvidenceBundle]:
    draft = load_draft(EXAMPLES_ROOT / "drafts" / "ai-research-note.md")
    evidence_bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "ai-research-evidence.yml")
    return draft, evidence_bundle


def _ai_research_report(config: AuditConfig | None = None) -> AuditReport:
    draft, evidence_bundle = _ai_research_inputs()
    return audit_document(draft, evidence_bundle, config)


def _summary_counts(report: AuditReport) -> dict[str, int]:
    return {
        "total": report.summary.total_claims,
        "supported": report.summary.supported_claims,
        "partially_supported": report.summary.partially_supported_claims,
        "unsupported": report.summary.unsupported_claims,
        "overstated": report.summary.overstated_claims,
        "needs_source": report.summary.needs_source_claims,
        "not_checkable": report.summary.not_checkable_claims,
        "high_risk": report.summary.high_risk_claims,
    }


def test_audit_document_returns_typed_report_with_assessment_per_extracted_claim() -> None:
    """The coordinator returns typed traceable assessments in extraction order."""
    draft, evidence_bundle = _ai_research_inputs()
    extracted_claims = extract_claims(draft)
    report = audit_document(draft, evidence_bundle)

    assert isinstance(report, AuditReport)
    assert report.document_id == draft.id
    assert report.summary.total_claims == len(extracted_claims)
    assert [assessment.claim.id for assessment in report.claims] == [
        claim.id for claim in extracted_claims
    ]
    assert all(assessment.claim.text for assessment in report.claims)
    assert any(assessment.candidate_evidence for assessment in report.claims)
    assert report.limitations


def test_report_rule_flags_flatten_claim_flags_in_exact_claim_order() -> None:
    """Report-level flags preserve report.claims order and per-claim flag order."""
    report = _ai_research_report()
    expected_flags = [flag for assessment in report.claims for flag in assessment.rule_flags]

    assert report.rule_flags == expected_flags
    assert [flag.id for flag in report.rule_flags] == [flag.id for flag in expected_flags]


def test_every_report_rule_flag_points_to_assessed_claim_id() -> None:
    """Report-level flags keep claim IDs traceable to assessed claims."""
    report = _ai_research_report()
    assessed_claim_ids = {assessment.claim.id for assessment in report.claims}

    assert report.rule_flags
    assert all(flag.claim_id in assessed_claim_ids for flag in report.rule_flags)


def test_summary_counts_match_claim_assessments() -> None:
    """Summary values are derived from final claim assessments."""
    report = _ai_research_report()
    labels = [assessment.support_label for assessment in report.claims]
    risks = [assessment.risk_label for assessment in report.claims]

    assert _summary_counts(report) == {
        "total": len(report.claims),
        "supported": labels.count("supported"),
        "partially_supported": labels.count("partially_supported"),
        "unsupported": labels.count("unsupported"),
        "overstated": labels.count("overstated"),
        "needs_source": labels.count("needs_source"),
        "not_checkable": labels.count("not_checkable"),
        "high_risk": risks.count("high"),
    }


def test_ai_research_fixture_keeps_expected_labels_and_high_risk_count() -> None:
    """The governed rules produce the expected fixture labels."""
    report = _ai_research_report()

    assert [assessment.support_label for assessment in report.claims] == [
        "overstated",
        "supported",
        "partially_supported",
        "overstated",
    ]
    assert report.summary.high_risk_claims == 2
    assert {flag.code for flag in report.rule_flags} == {
        "causal_overreach",
        "future_certainty",
        "overconfident_wording",
        "scope_overreach",
    }


def test_empty_evidence_bundle_returns_needs_source_assessments_and_warning() -> None:
    """Empty evidence is an audit result, not a runtime failure."""
    draft, _ = _ai_research_inputs()
    report = audit_document(draft, EvidenceBundle(sources=[]))

    assert report.summary.total_claims == 4
    assert report.summary.needs_source_claims == 4
    assert report.summary.not_checkable_claims == 0
    assert report.evidence_bundle_warnings == [
        "No evidence sources were supplied; extracted claims are marked needs_source."
    ]
    assert all(assessment.support_label == "needs_source" for assessment in report.claims)
    assert all(assessment.risk_label == "medium" for assessment in report.claims)
    assert report.rule_flags == []


def test_high_risk_findings_return_successfully_and_are_counted() -> None:
    """High-risk claims stay in the completed audit report instead of raising."""
    report = _ai_research_report()
    high_risk_claims = [
        assessment for assessment in report.claims if assessment.risk_label == "high"
    ]

    assert len(high_risk_claims) == report.summary.high_risk_claims
    assert {assessment.claim.text for assessment in high_risk_claims} == {
        ELIMINATES_CLAIM,
        "The checklist will always prevent researchers from relying on weak evidence.",
    }


def test_no_claim_draft_returns_valid_zero_claim_report() -> None:
    """Drafts with no extracted claims still produce a valid empty report."""
    _, evidence_bundle = _ai_research_inputs()
    draft = DraftDocument(
        id="no-claim-note",
        content="Notes for later.\n\nQuestions to revisit? Plain background only.",
    )
    report = audit_document(draft, evidence_bundle)

    assert report.summary.total_claims == 0
    assert report.claims == []
    assert report.rule_flags == []
    assert report.evidence_bundle_warnings == []
    assert _summary_counts(report) == {
        "total": 0,
        "supported": 0,
        "partially_supported": 0,
        "unsupported": 0,
        "overstated": 0,
        "needs_source": 0,
        "not_checkable": 0,
        "high_risk": 0,
    }


def test_config_threshold_and_cap_flow_through_candidate_matching() -> None:
    """AuditConfig still controls candidate inclusion and capping in orchestration."""
    report = _ai_research_report(AuditConfig(min_overlap_score=0.95, max_candidate_evidence=1))

    candidate_counts = {
        assessment.claim.text: len(assessment.candidate_evidence) for assessment in report.claims
    }

    assert candidate_counts["The test set included 52 workflow outputs."] == 1
    assert candidate_counts[REDUCTION_CLAIM] == 0
    assert max(len(assessment.candidate_evidence) for assessment in report.claims) <= 1


def test_repeated_runs_produce_same_structured_report_data() -> None:
    """The structured audit report is deterministic for the same inputs."""
    first = _ai_research_report()
    second = _ai_research_report()

    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_report_limitations_preserve_boundaries_without_forbidden_language() -> None:
    """Report-level limitations preserve supplied-evidence and score boundaries."""
    limitations = _ai_research_report().limitations
    text = "\n".join(limitations)

    assert (
        "This report only audits support from the supplied evidence bundle; it does not "
        "assess the outside world."
    ) in limitations
    assert (
        "Match scores and support signals are deterministic supplied-evidence measures, "
        "not truth probabilities."
    ) in limitations
    assert "Phase " not in text
    for pattern in FORBIDDEN_CAPABILITY_PATTERNS:
        assert re.search(pattern, text.lower()) is None
