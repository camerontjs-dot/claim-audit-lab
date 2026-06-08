"""Audit pipeline coordination."""

from __future__ import annotations

from claim_audit_lab.claim_extraction import extract_claims
from claim_audit_lab.evidence_matching import match_claims_to_evidence
from claim_audit_lab.models import (
    AuditConfig,
    AuditReport,
    AuditSummary,
    Claim,
    ClaimAssessment,
    DraftDocument,
    EvidenceBundle,
    EvidenceCandidate,
    RuleFlag,
)
from claim_audit_lab.rules import assess_claim_support

_PIPELINE_STATUS_LIMITATION = (
    "Audit orchestration has been hardened through Phase 6; deterministic rule checks "
    "and Phase 7 report rendering are enabled; Phase 8 CLI workflow is available."
)
_CANDIDATE_SCORE_LIMITATION = (
    "Candidate scores rank deterministic text and number overlap only; they are not support scores."
)
_SUPPLIED_EVIDENCE_LIMITATION = (
    "This report only audits support from the supplied evidence bundle; it does not "
    "assess the outside world."
)


def audit_document(
    draft: DraftDocument,
    evidence_bundle: EvidenceBundle,
    config: AuditConfig | None = None,
) -> AuditReport:
    """Run the deterministic audit pipeline for a draft and supplied evidence bundle."""
    active_config = config or AuditConfig()
    claims = extract_claims(draft)
    candidate_map = match_claims_to_evidence(claims, evidence_bundle, active_config)
    assessments = _build_assessments(claims, evidence_bundle, candidate_map, active_config)

    return AuditReport(
        document_id=draft.id,
        summary=_build_summary(assessments),
        claims=assessments,
        rule_flags=_collect_rule_flags(assessments),
        evidence_bundle_warnings=_build_evidence_bundle_warnings(evidence_bundle),
        limitations=_build_report_limitations(),
    )


def _build_assessments(
    claims: list[Claim],
    evidence_bundle: EvidenceBundle,
    candidate_map: dict[str, list[EvidenceCandidate]],
    config: AuditConfig,
) -> list[ClaimAssessment]:
    return [
        assess_claim_support(
            claim,
            evidence_bundle,
            candidate_map.get(claim.id, []),
            config,
        )
        for claim in claims
    ]


def _collect_rule_flags(assessments: list[ClaimAssessment]) -> list[RuleFlag]:
    return [flag for assessment in assessments for flag in assessment.rule_flags]


def _build_summary(assessments: list[ClaimAssessment]) -> AuditSummary:
    return AuditSummary(
        total_claims=len(assessments),
        supported_claims=sum(assessment.support_label == "supported" for assessment in assessments),
        partially_supported_claims=sum(
            assessment.support_label == "partially_supported" for assessment in assessments
        ),
        unsupported_claims=sum(
            assessment.support_label == "unsupported" for assessment in assessments
        ),
        overstated_claims=sum(
            assessment.support_label == "overstated" for assessment in assessments
        ),
        needs_source_claims=sum(
            assessment.support_label == "needs_source" for assessment in assessments
        ),
        not_checkable_claims=sum(
            assessment.support_label == "not_checkable" for assessment in assessments
        ),
        high_risk_claims=sum(assessment.risk_label == "high" for assessment in assessments),
    )


def _build_evidence_bundle_warnings(evidence_bundle: EvidenceBundle) -> list[str]:
    if evidence_bundle.sources:
        return []
    return ["No evidence sources were supplied; extracted claims are marked needs_source."]


def _build_report_limitations() -> list[str]:
    return [
        _PIPELINE_STATUS_LIMITATION,
        _CANDIDATE_SCORE_LIMITATION,
        _SUPPLIED_EVIDENCE_LIMITATION,
    ]


__all__ = ["audit_document", "_build_assessments"]
