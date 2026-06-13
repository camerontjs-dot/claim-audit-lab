"""Audit pipeline coordination."""

from __future__ import annotations

from claim_audit_lab.claim_extraction import extract_claims
from claim_audit_lab.evidence_matching import (
    ClaimEvidenceScope,
    match_claims_to_evidence,
    match_scoped_evidence,
)
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

_SUPPORT_SIGNAL_LIMITATION = (
    "Match scores and support signals are deterministic supplied-evidence measures, "
    "not truth probabilities."
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
    assessments = audit_claims(claims, evidence_bundle, active_config)

    return build_audit_report(draft.id, assessments, evidence_bundle)


def build_audit_report(
    document_id: str,
    assessments: list[ClaimAssessment],
    evidence_bundle: EvidenceBundle,
) -> AuditReport:
    """Build a structured report from completed claim assessments."""
    return AuditReport(
        document_id=document_id,
        summary=_build_summary(assessments),
        claims=assessments,
        rule_flags=_collect_rule_flags(assessments),
        evidence_bundle_warnings=_build_evidence_bundle_warnings(evidence_bundle),
        limitations=_build_report_limitations(),
    )


def audit_claims(
    claims: list[Claim],
    evidence_bundle: EvidenceBundle,
    config: AuditConfig | None = None,
    *,
    evidence_scopes: dict[str, ClaimEvidenceScope] | None = None,
) -> list[ClaimAssessment]:
    """Audit a supplied claim list against supplied evidence."""
    active_config = config or AuditConfig()
    if evidence_scopes is None:
        candidate_map = match_claims_to_evidence(claims, evidence_bundle, active_config)
        return _build_assessments(
            claims,
            evidence_bundle,
            candidate_map,
            active_config,
        )

    assessments: list[ClaimAssessment] = []
    for claim in claims:
        matches = match_scoped_evidence(
            claim,
            evidence_bundle,
            evidence_scopes.get(claim.id, ClaimEvidenceScope()),
            active_config,
        )
        assessments.append(
            assess_claim_support(
                claim,
                evidence_bundle,
                list(matches.support),
                active_config,
                counterevidence=list(matches.counterevidence),
            )
        )
    return assessments


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
        _SUPPORT_SIGNAL_LIMITATION,
        _SUPPLIED_EVIDENCE_LIMITATION,
    ]


__all__ = ["audit_claims", "audit_document", "build_audit_report"]
