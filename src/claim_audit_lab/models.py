"""Typed data models for claim audits."""

from __future__ import annotations

from datetime import date as Date
from typing import Annotated, Literal, Self, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

NonBlankStr: TypeAlias = Annotated[str, Field(min_length=1)]

SupportLabel: TypeAlias = Literal[
    "supported",
    "partially_supported",
    "unsupported",
    "overstated",
    "needs_source",
    "not_audit_ready",
]
RiskLabel: TypeAlias = Literal["low", "medium", "high"]
ClaimType: TypeAlias = Literal[
    "numeric",
    "causal",
    "comparative",
    "credential",
    "prediction",
    "capability",
    "scope",
    "interpretive",
]
SourceReliability: TypeAlias = Literal["low", "medium", "high", "unknown"]
SourceType: TypeAlias = Literal[
    "report",
    "article",
    "documentation",
    "test_output",
    "local_note",
    "public_profile",
    "unknown",
]
Strictness: TypeAlias = Literal["low", "standard", "high"]


class StrictBaseModel(BaseModel):
    """Base model that rejects schema drift and strips string whitespace."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class EvidenceExcerpt(StrictBaseModel):
    """Quoted or summarized evidence from a source."""

    id: NonBlankStr
    text: NonBlankStr
    notes: NonBlankStr | None = None


class EvidenceSource(StrictBaseModel):
    """Evidence source with one or more auditable excerpts."""

    id: NonBlankStr
    title: NonBlankStr
    source_type: SourceType = "unknown"
    reliability: SourceReliability = "unknown"
    excerpts: list[EvidenceExcerpt] = Field(default_factory=list)
    url: NonBlankStr | None = None
    date: Date | None = None


class EvidenceBundle(StrictBaseModel):
    """Collection of supplied evidence sources."""

    sources: list[EvidenceSource] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> Self:
        """Reject duplicate source IDs and excerpt IDs."""
        source_ids: set[str] = set()
        excerpt_ids: set[str] = set()

        for source in self.sources:
            if source.id in source_ids:
                raise ValueError(f"Duplicate evidence source id: {source.id}")
            source_ids.add(source.id)

            for excerpt in source.excerpts:
                if excerpt.id in excerpt_ids:
                    raise ValueError(f"Duplicate evidence excerpt id: {excerpt.id}")
                excerpt_ids.add(excerpt.id)

        return self


class DraftDocument(StrictBaseModel):
    """Draft document submitted for claim audit."""

    id: NonBlankStr
    content: NonBlankStr
    title: NonBlankStr | None = None
    path: NonBlankStr | None = None


class AuditConfig(StrictBaseModel):
    """Configuration for deterministic audit behavior."""

    strictness: Strictness = "standard"
    freshness_days: int = Field(default=365, gt=0)
    reference_date: Date | None = None
    min_overlap_score: float = Field(default=0.2, ge=0.0, le=1.0)
    max_candidate_evidence: int = Field(default=3, ge=1)


class Claim(StrictBaseModel):
    """Extracted claim from a draft document."""

    id: NonBlankStr
    text: NonBlankStr
    claim_type: ClaimType
    location: NonBlankStr | None = None


class EvidenceCandidate(StrictBaseModel):
    """Candidate evidence link for an extracted claim."""

    source_id: NonBlankStr
    excerpt_id: NonBlankStr
    score: float = Field(ge=0.0, le=1.0)
    rationale: NonBlankStr | None = None
    source_reliability: SourceReliability = "unknown"
    source_date: Date | None = None
    source_url: NonBlankStr | None = None


class RuleFlag(StrictBaseModel):
    """Rule-based warning attached to a claim assessment."""

    id: NonBlankStr
    claim_id: NonBlankStr
    code: NonBlankStr
    message: NonBlankStr
    risk: RiskLabel


class ClaimAssessment(StrictBaseModel):
    """Support assessment for a single claim."""

    claim: Claim
    support_label: SupportLabel
    risk_label: RiskLabel
    candidate_evidence: list[EvidenceCandidate] = Field(default_factory=list)
    rule_flags: list[RuleFlag] = Field(default_factory=list)
    explanation: NonBlankStr | None = None
    suggested_rewrite: NonBlankStr | None = None
    limitations: list[NonBlankStr] = Field(default_factory=list)


class AuditSummary(StrictBaseModel):
    """Aggregate counts for an audit report."""

    total_claims: int = Field(ge=0)
    supported_claims: int = Field(default=0, ge=0)
    partially_supported_claims: int = Field(default=0, ge=0)
    unsupported_claims: int = Field(default=0, ge=0)
    overstated_claims: int = Field(default=0, ge=0)
    needs_source_claims: int = Field(default=0, ge=0)
    not_audit_ready_claims: int = Field(default=0, ge=0)
    high_risk_claims: int = Field(default=0, ge=0)


class AuditReport(StrictBaseModel):
    """Structured result returned by the audit pipeline."""

    document_id: NonBlankStr
    summary: AuditSummary
    claims: list[ClaimAssessment] = Field(default_factory=list)
    rule_flags: list[RuleFlag] = Field(default_factory=list)
    evidence_bundle_warnings: list[NonBlankStr] = Field(default_factory=list)
    limitations: list[NonBlankStr] = Field(default_factory=list)


__all__ = [
    "AuditConfig",
    "AuditReport",
    "AuditSummary",
    "Claim",
    "ClaimAssessment",
    "ClaimType",
    "DraftDocument",
    "EvidenceBundle",
    "EvidenceCandidate",
    "EvidenceExcerpt",
    "EvidenceSource",
    "RiskLabel",
    "RuleFlag",
    "SourceReliability",
    "SourceType",
    "StrictBaseModel",
    "Strictness",
    "SupportLabel",
]
