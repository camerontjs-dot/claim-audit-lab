"""Pydantic models for the CAL v1 input/output contract.

These are the JSON-shaped boundary types; everything else in v1 derives
from them. The contract is intentionally separate from the v0.2 YAML
models so the inference pipeline never touches YAML internally.

The audit verdict is a **two-axis record** (apparatus-contracts C-B v2.0.0,
see ``plans/proposal-v2.0.0-two-axis-audit-vocabulary.md``): a
``support_verdict`` degree plus non-exclusive ``audit_flags`` and an
orthogonal ``citation_status``. ``overstated`` / ``inferred`` are *flags on a
degree*, not degrees themselves.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SupportVerdict = Literal[
    "supported",
    "partially_supported",
    "unsupported",
    "contradicted",
    "not_checkable",
]
"""Axis 1 — degree of support (ordinal, mutually exclusive). Produced by the
entailer + aggregator. See Decision A (C-B v2.0.0)."""

VerdictReason = Literal["out_of_scope", "no_entail_signal", "no_evidence"]
"""Why a ``not_checkable`` verdict was returned. ``no_evidence`` absorbs the
retired ``needs_source``. See ``plans/adr-v1-input-contract.md``."""

AuditFlag = Literal[
    "overstated",
    "inferred",
    "source_scope_error",
    "false_caution",
    "missed_counterevidence",
    "coverage_loss",
]
"""Axis 2 — failure-mode modifiers (non-exclusive). Produced by the rules
layer. ``overstated`` = claim overshoots evidence; ``inferred`` = supported by
inference, not verbatim."""

CitationStatus = Literal[
    "correct",
    "partial",
    "wrong_source",
    "missing_needed",
    "not_cited",
    "not_applicable",
]
"""Axis 3 — provenance check, orthogonal to the support degree."""

AuditConfidence = Literal["high", "medium", "low"]
"""The auditor's confidence in its own verdict."""

EntailLabel = Literal["entail", "neutral", "contradict"]
"""NLI three-class label space, MNLI / FEVER / ANLI convention."""

ModalStrength = Literal["asserts", "hedges", "prescribes"]
"""Closed-set modal strength used by the deterministic feature layer."""

SentenceType = Literal["declarative", "question", "imperative", "opinion"]
"""Claim sentence type, for the input-contract / out_of_scope gate.
See ``plans/adr-v1-input-contract.md``."""

AggregationStrategy = Literal["max_entailment", "concat_premise", "matrix"]
"""Aggregation across retrieved passage candidates. v1 uses
``max_entailment``; the others are documented but deferred."""


class _StrictModel(BaseModel):
    """Base for v1 contract types: frozen, strict, no extras."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class Passage(_StrictModel):
    """A unit of evidence presented to CAL by the Evidence Bundler."""

    passage_id: str
    text: str
    source_meta: dict[str, str] = Field(default_factory=dict)


class Quantity(_StrictModel):
    """A numeric value extracted from a claim or passage."""

    value: float
    unit: str | None = None
    surface_text: str


class ExtractedFeatures(_StrictModel):
    """Linguistically grounded features computed from a claim.

    Replaces the v0.2 regex-driven ``ClaimType`` taxonomy. See
    DECISIONS.md § 2026-06-21 § 4. ``claim_token_count`` / ``compound_claim`` /
    ``sentence_type`` are the input-contract features (``adr-v1-input-contract.md``).
    """

    numerical_values: list[Quantity] = Field(default_factory=list)
    has_explicit_negation: bool = False
    has_universal_quantifier: bool = False
    modal_strength: ModalStrength = "asserts"
    claim_token_count: int = Field(ge=0, default=0)
    compound_claim: bool = False
    sentence_type: SentenceType = "declarative"


class RetrievalResult(_StrictModel):
    """A passage admitted by the Retriever, with its retrieval score."""

    passage_id: str
    score: float


class EntailResult(_StrictModel):
    """NLI output for a single (claim, premise) pair."""

    passage_id: str
    label: EntailLabel
    score: float
    raw_logits: tuple[float, float, float]


class SupportSignal(_StrictModel):
    """Aggregated support signal across the candidate passages."""

    label: EntailLabel
    max_entailment_score: float
    contributing_passage_id: str | None = None


class RuleFired(_StrictModel):
    """One deterministic rule application and the reason it fired."""

    rule_id: str
    reason: str


class Verdict(_StrictModel):
    """Final claim-level verdict — two-axis (C-B v2.0.0).

    ``support_verdict`` is the ordinal degree; ``audit_flags`` are
    non-exclusive failure-mode modifiers; ``citation_status`` is the
    orthogonal provenance check. ``support_verdict_reason`` is set only when
    ``support_verdict == 'not_checkable'`` (pairing is enforced by the rules
    layer, not the model).
    """

    support_verdict: SupportVerdict
    support_verdict_reason: VerdictReason | None = None
    audit_flags: list[AuditFlag] = Field(default_factory=list)
    citation_status: CitationStatus = "not_applicable"
    audit_confidence: AuditConfidence = "medium"


class ModelRevision(_StrictModel):
    """Pinned HF model identifier + revision SHA recorded in the trace."""

    model_id: str
    hf_revision_sha: str


class AuditConfig(_StrictModel):
    """Single source of run tunables, hashed into the trace per DECISIONS.md § 2026-06-21 § 6.

    The verdict thresholds (``retrieval_floor``, ``supported_threshold``,
    ``contradicted_threshold``, ``numeric_tolerance``,
    ``approx_numeric_tolerance``) are *materialized* from the versioned rules
    file ``cal-rules-v1.5.0.yaml`` by
    :func:`claim_audit_lab.v1.config.load_default_audit_config`, which pins that
    file as ``rules_file_sha``; they are not hand-authored here. See
    ``plans/adr-v1-rule-order.md``, ``plans/adr-v1-rules-v1.4.0-semantic-fixes.md``,
    ``plans/adr-v1-absence-route.md``, and ``…v1.config.verify_rules_consistency``.
    """

    top_k: int = Field(ge=1, default=5)
    retrieval_floor: float = Field(ge=0.0, le=1.0, default=0.40)
    supported_threshold: float = Field(ge=0.0, le=1.0, default=0.70)
    contradicted_threshold: float = Field(ge=0.0, le=1.0, default=0.70)
    numeric_tolerance: float = Field(ge=0.0, default=0.0)
    approx_numeric_tolerance: float = Field(ge=0.0, default=0.05)
    aggregation: AggregationStrategy = "max_entailment"
    rules_file_sha: str
    retriever: ModelRevision
    entailer: ModelRevision


class AuditRequest(_StrictModel):
    """Normalized JSON input to the v1 inference pipeline.

    Built once at C-B intake; downstream code does not touch YAML.
    """

    claim_id: str
    claim_text: str
    passages: list[Passage]
    audit_config: AuditConfig


class AuditTrace(_StrictModel):
    """The audit trace — sufficient to replay the verdict deterministically.

    See the reproducibility property in DECISIONS.md § 2026-06-21 § 3 and § 9.
    """

    claim_id: str
    claim_text: str
    retrieval: list[RetrievalResult]
    entailment: list[EntailResult]
    features: ExtractedFeatures
    support_signal: SupportSignal
    rules_fired: list[RuleFired]
    verdict: Verdict
    audit_config_hash: str
    library_version: str


__all__ = [
    "AggregationStrategy",
    "AuditConfidence",
    "AuditConfig",
    "AuditFlag",
    "AuditRequest",
    "AuditTrace",
    "CitationStatus",
    "EntailLabel",
    "EntailResult",
    "ExtractedFeatures",
    "ModalStrength",
    "ModelRevision",
    "Passage",
    "Quantity",
    "RetrievalResult",
    "RuleFired",
    "SentenceType",
    "SupportSignal",
    "SupportVerdict",
    "Verdict",
    "VerdictReason",
]
