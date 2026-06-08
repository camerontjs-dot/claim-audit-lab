"""Read-only Pydantic models for C-B evidence-bundle artifacts.

These models mirror the locked Apparatus Contracts v1.0.0 C-B tree locally
inside Claim Audit Lab. CAL consumes the on-disk bundle contract; it does not
import the Evidence Bundler package that produces the bundle.

Type boundary
-------------
C-B ``claim_type`` is the handoff-contract role field:
``retrieval_seed`` | ``extracted_claim``.

CAL ``Claim.claim_type`` is the semantic pipeline field:
``numeric`` | ``causal`` | ``comparative`` | ...

Never copy a C-B ``claim_type`` value into a CAL semantic ``Claim.claim_type``.
"""

from __future__ import annotations

from typing import Annotated, Literal, Self, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

NonBlankStr: TypeAlias = Annotated[str, Field(min_length=1)]
ContractVersion: TypeAlias = Literal["1.0.0", "1.1.0"]
HashValue: TypeAlias = Annotated[str, Field(pattern=r"^sha256:([a-f0-9]{64}|pending)$")]

WorkflowCondition: TypeAlias = Literal[
    "baseline",
    "format_only",
    "provenance_scaffold",
    "full_scaffold",
]
CBClaimType: TypeAlias = Literal["retrieval_seed", "extracted_claim"]
ScaffoldSupportStatus: TypeAlias = Literal["sourced", "inferred", "uncertain", "unsupported"]
AuditSupportVerdict: TypeAlias = Literal[
    "supported",
    "partially_supported",
    "unsupported",
    "overstated",
    "needs_source",
    "not_checkable",
]
CBSourceType: TypeAlias = Literal[
    "journal_article",
    "regulatory_guidance",
    "preprint",
    "web_page",
    "book",
    "other",
]
TrustLevel: TypeAlias = Literal["primary", "secondary", "background"]
ExtractionMethod: TypeAlias = Literal["scaffold_cited", "scaffold_inferred", "auto_retrieved"]


class _CBBase(BaseModel):
    """Base model for contract read models: strict and whitespace-normalizing."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CBEvidenceBuilderInfo(_CBBase):
    """Bundler runtime state recorded in bundle_manifest.yaml."""

    version: NonBlankStr
    config_hash: HashValue
    operator: NonBlankStr
    build_timestamp_utc: NonBlankStr


class CBBundleStats(_CBBase):
    """Bundle claim and passage counts."""

    total_claims_in_source: int = Field(ge=0)
    claims_included: int = Field(ge=0)
    claims_excluded: int = Field(ge=0)
    exclusion_rationale: str
    total_evidence_passages: int = Field(ge=0)
    bundle_hash: HashValue


class CBTransformationRecord(_CBBase):
    """Transformation applied while preparing the C-B bundle."""

    type: NonBlankStr
    description: NonBlankStr
    claims_affected: list[NonBlankStr] = Field(default_factory=list)


class CBQualityGates(_CBBase):
    """Seal-time quality gate outcomes."""

    every_claim_has_at_least_one_passage: bool
    every_passage_links_to_source_profile: bool
    source_hashes_verified: bool
    bundle_integrity_verified: bool


class CBReviewerSignOff(_CBBase):
    """Deferred 21 CFR Part 11 sign-off surface."""

    required: bool = False
    signed_by: NonBlankStr | None = None
    signature_timestamp_utc: NonBlankStr | None = None
    signature_notes: str | None = None


class CBBundleManifest(_CBBase):
    """C-B bundle_manifest.yaml certificate of analysis."""

    bundle_id: NonBlankStr
    schema_version: ContractVersion
    generated_at_utc: NonBlankStr
    source_run_id: NonBlankStr
    source_contract_version: ContractVersion
    source_corpus_hash: HashValue
    evidence_builder: CBEvidenceBuilderInfo
    bundle: CBBundleStats
    transformations: list[CBTransformationRecord] = Field(default_factory=list)
    quality_gates: CBQualityGates
    audit_config_version: NonBlankStr
    audit_config_hash: HashValue
    validation_set_version: NonBlankStr
    validation_set_hash: HashValue
    reviewer_sign_off: CBReviewerSignOff


class CBClaimEvidencePassage(_CBBase):
    """Passage embedded into a self-contained claim audit unit."""

    passage_id: NonBlankStr
    source_id: NonBlankStr
    passage_text: NonBlankStr
    section: NonBlankStr | None = None
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    source_trust_level: TrustLevel
    passage_hash: HashValue

    @model_validator(mode="after")
    def validate_offsets(self) -> Self:
        """Reject inverted character offsets."""
        if self.char_end <= self.char_start:
            raise ValueError("char_end must be greater than char_start")
        return self


class CBAuditFields(_CBBase):
    """Claim Audit Lab target fields; null at Evidence Bundler handoff."""

    audit_run_id: NonBlankStr | None = None
    audited_at_utc: NonBlankStr | None = None
    audit_support_verdict: AuditSupportVerdict | None = None
    audit_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    audit_notes: str | None = None
    false_caution_flag: bool | None = None
    deviation_flag: bool | None = None
    deviation_notes: str | None = None


class CBClaim(_CBBase):
    """C-B claims/{claim_id}.yaml self-contained audit unit."""

    claim_id: NonBlankStr
    bundle_id: NonBlankStr
    schema_version: ContractVersion
    claim_text: NonBlankStr
    claim_type: CBClaimType
    workflow_condition: WorkflowCondition
    task_id: NonBlankStr
    scaffold_support_status: ScaffoldSupportStatus
    scaffold_claim_strength: float = Field(ge=0.0, le=1.0)
    scaffold_extraction_fidelity: float = Field(ge=0.0, le=1.0)
    scaffold_counterevidence_found: bool
    scaffold_downgraded: bool
    evidence_passages: list[CBClaimEvidencePassage] = Field(default_factory=list)
    counterevidence_passages: list[CBClaimEvidencePassage] = Field(default_factory=list)
    audit: CBAuditFields = Field(default_factory=CBAuditFields)


class CBPassageProvenance(_CBBase):
    """Full C-A to C-B lineage for a passage record."""

    source_url: NonBlankStr
    source_access_date_utc: NonBlankStr
    source_content_hash: HashValue
    scaffold_run_id: NonBlankStr
    evidence_builder_version: NonBlankStr
    bundle_created_at_utc: NonBlankStr


class CBPassage(_CBBase):
    """C-B evidence/{source_id}/passages/{passage_id}.yaml passage record."""

    passage_id: NonBlankStr
    source_id: NonBlankStr
    bundle_id: NonBlankStr
    schema_version: ContractVersion
    passage_text: NonBlankStr
    section: NonBlankStr | None = None
    paragraph_index: int = Field(ge=0)
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    passage_hash: HashValue
    cited_by_claims: list[NonBlankStr] = Field(default_factory=list)
    extraction_method: ExtractionMethod
    provenance: CBPassageProvenance

    @model_validator(mode="after")
    def validate_offsets(self) -> Self:
        """Reject inverted character offsets."""
        if self.char_end <= self.char_start:
            raise ValueError("char_end must be greater than char_start")
        return self


class CBSourceBibliographic(_CBBase):
    """Bibliographic identity copied from C-A source metadata."""

    source_type: CBSourceType
    title: NonBlankStr
    authors: list[NonBlankStr] = Field(default_factory=list)
    publication_date: NonBlankStr | None = None
    pmid: NonBlankStr | None = None
    doi: NonBlankStr | None = None
    url: NonBlankStr
    access_date_utc: NonBlankStr


class CBSourceProfile(_CBBase):
    """C-B evidence/{source_id}/source_profile.yaml source identity."""

    source_id: NonBlankStr
    schema_version: ContractVersion
    bibliographic: CBSourceBibliographic
    trust_level: TrustLevel
    content_hash: HashValue
    retrieved_for: list[NonBlankStr] = Field(default_factory=list)
    retrieval_query: NonBlankStr
    retrieval_rank: int = Field(ge=1)
    notes: str = ""


class CBAuditScoringConfig(_CBBase):
    """Frozen audit scoring thresholds."""

    support_threshold_sourced: float = Field(ge=0.0, le=1.0)
    support_threshold_partial: float = Field(ge=0.0, le=1.0)
    counterevidence_weight: float = Field(ge=0.0, le=1.0)


class CBAuditRulePolicies(_CBBase):
    """Frozen audit rule switches."""

    require_passage_level_match: bool
    flag_unsupported_threshold: float = Field(ge=0.0, le=1.0)
    false_caution_detection: bool
    false_caution_threshold: float = Field(ge=0.0, le=1.0)
    overstated_detection: bool
    needs_source_detection: bool


class CBAuditConfigChange(_CBBase):
    """Audit config change-log entry."""

    version: NonBlankStr
    date: NonBlankStr
    changes: NonBlankStr
    rationale: NonBlankStr


class CBAuditConfig(_CBBase):
    """C-B audit_config.yaml frozen audit rules."""

    config_id: NonBlankStr
    config_hash: HashValue
    schema_version: ContractVersion
    frozen_at_utc: NonBlankStr
    scoring: CBAuditScoringConfig
    rule_policies: CBAuditRulePolicies
    known_limitations: list[NonBlankStr] = Field(default_factory=list)
    change_log: list[CBAuditConfigChange] = Field(default_factory=list)


class CBValidationSetRef(_CBBase):
    """C-B validation_set_ref.yaml pointer."""

    schema_version: ContractVersion
    validation_set_version: NonBlankStr
    validation_set_hash: HashValue
    frozen_at_utc: NonBlankStr
    description: NonBlankStr
    notes: str = ""


# Short aliases are convenient in tests and future loader work; the CB-prefixed
# names remain exported for compatibility with the existing draft modules.
AuditConfig = CBAuditConfig
AuditConfigChange = CBAuditConfigChange
AuditFields = CBAuditFields
AuditRulePolicies = CBAuditRulePolicies
AuditScoringConfig = CBAuditScoringConfig
BundleManifest = CBBundleManifest
BundleStats = CBBundleStats
ClaimAuditUnit = CBClaim
ClaimEvidencePassage = CBClaimEvidencePassage
EvidenceBuilderInfo = CBEvidenceBuilderInfo
PassageProvenance = CBPassageProvenance
PassageRecord = CBPassage
QualityGates = CBQualityGates
ReviewerSignOff = CBReviewerSignOff
SourceBibliographic = CBSourceBibliographic
SourceProfile = CBSourceProfile
TransformationRecord = CBTransformationRecord
ValidationSetRef = CBValidationSetRef


__all__ = [
    "AuditConfig",
    "AuditConfigChange",
    "AuditFields",
    "AuditRulePolicies",
    "AuditScoringConfig",
    "AuditSupportVerdict",
    "BundleManifest",
    "BundleStats",
    "CBClaim",
    "CBClaimEvidencePassage",
    "CBClaimType",
    "CBAuditConfig",
    "CBAuditConfigChange",
    "CBAuditFields",
    "CBAuditRulePolicies",
    "CBAuditScoringConfig",
    "CBBundleManifest",
    "CBBundleStats",
    "CBEvidenceBuilderInfo",
    "CBPassage",
    "CBPassageProvenance",
    "CBQualityGates",
    "CBReviewerSignOff",
    "CBSourceBibliographic",
    "CBSourceProfile",
    "CBSourceType",
    "CBTransformationRecord",
    "CBValidationSetRef",
    "ClaimAuditUnit",
    "ClaimEvidencePassage",
    "ContractVersion",
    "EvidenceBuilderInfo",
    "ExtractionMethod",
    "HashValue",
    "NonBlankStr",
    "PassageProvenance",
    "PassageRecord",
    "QualityGates",
    "ReviewerSignOff",
    "ScaffoldSupportStatus",
    "SourceBibliographic",
    "SourceProfile",
    "TransformationRecord",
    "TrustLevel",
    "ValidationSetRef",
    "WorkflowCondition",
]
