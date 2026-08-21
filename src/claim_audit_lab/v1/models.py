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

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, SerializerFunctionWrapHandler, model_serializer

SupportVerdict = Literal[
    "supported",
    "partially_supported",
    "unsupported",
    "contradicted",
    "not_checkable",
]
"""Axis 1 — degree of support (ordinal, mutually exclusive). Produced by the
entailer + aggregator. See Decision A (C-B v2.0.0)."""

VerdictReason = Literal[
    "out_of_scope",
    "no_entail_signal",
    "no_evidence",
    # cal-rules-v1.9.0: two admitted passages take opposite positions on the
    # claim, both above threshold. Distinct from `no_entail_signal`, which
    # means nothing was established — here two things were, and they disagree.
    "conflicting_evidence",
    # cal-rules-v1.10.0: the claim denies that a *document* says something. Whether
    # that is true turns on whether the bundle is the whole source, which is
    # `source_boundary` — declared on the request, and read by no rule.
    "absence_not_decidable",
]
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


SourceBoundary = Literal["exhaustive", "bounded", "named_missing_material"]
"""How completely the supplied passages cover their source.

This is the parameter that decides whether an *absence* is informative. "The
guidance does not prescribe X" is settled by the bundle only when the bundle is
the whole source:

``exhaustive``
    The passages are the complete source. Absence in the bundle is absence in
    the source, so an absence claim is decidable from the bundle alone.
``bounded``
    The passages are an excerpt of a larger source. Absence in the bundle says
    nothing about the source, so an absence claim is not decidable here.
``named_missing_material``
    An excerpt that also names what is known to be missing.

Undeclared (``None``) means the caller has not said, and no absence reasoning is
licensed. Measured on PILOT-001, leaving this undeclared is not neutral: the
human coder supplied an implicit answer that tracked bundle size rather than a
rule, and that single ambiguity accounts for 7 of 34 CAL-gold disagreements
(absence-shaped claims, Fisher exact p = 0.0008).
"""


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
    p_entail: float | None = None
    """Softmax probability of the *entailment* class (2026-08-05 support-signal instrumentation).

    ``score`` is the probability of the **argmax** class, so on a neutral result
    it reports the model's confidence that the passage is *irrelevant* — not its
    support for the claim. Those are different quantities and only one of them
    answers the audit's question. This field carries the support probability
    unconditionally, whatever the label.

    It is derivable from ``raw_logits``, but only by a reader who knows the
    model's class order. Recording it makes the trace self-describing, and the
    number is never discarded regardless of whether it changed a verdict."""
    p_contradict: float | None = None
    """Softmax probability of the *contradiction* class. See :attr:`p_entail`."""

    _OPTIONAL_PROBABILITY_FIELDS = ("p_entail", "p_contradict")

    @model_serializer(mode="wrap")
    def _omit_absent_probabilities(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        """Drop the class probabilities when they were never measured.

        Same contract as ``AuditTrace._omit_absent_probe``: a key appears only
        when something recorded it. A stub entailer, or any trace written
        before 2026-08-05, round-trips byte-identically — which matters
        because preserved DEV suites embed whole traces and re-serialize them on
        replay. An absent measurement must never serialize as a measured null.
        """
        data: dict[str, Any] = handler(self)
        for key in self._OPTIONAL_PROBABILITY_FIELDS:
            if data.get(key) is None:
                data.pop(key, None)
        return data


class SupportSignal(_StrictModel):
    """Aggregated support signal across the candidate passages."""

    label: EntailLabel
    max_entailment_score: float
    contributing_passage_id: str | None = None
    best_entail: float | None = None
    """Highest ``p_entail`` over all candidate passages (2026-08-05 support-signal instrumentation).

    Independent of ``label``: it is populated on a neutral signal too, which is
    the whole point. The 128 claims that abstain with evidence admitted carry
    real entailment mass — up to 0.43 — that the argmax selection discards.

    **Reported, not acted on.** No rule reads this field; the verdict logic is
    byte-for-byte unchanged. Routing on it is a separate, gated decision."""
    best_contradict: float | None = None
    """Highest ``p_contradict`` over all candidate passages. See :attr:`best_entail`."""
    best_entail_passage_id: str | None = None
    """Passage carrying ``best_entail`` — not necessarily the contributing one."""
    best_contradict_passage_id: str | None = None
    """Passage carrying ``best_contradict``. See :attr:`best_entail_passage_id`."""

    _OPTIONAL_PROBABILITY_FIELDS = (
        "best_entail",
        "best_contradict",
        "best_entail_passage_id",
        "best_contradict_passage_id",
    )

    @model_serializer(mode="wrap")
    def _omit_absent_probabilities(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        """Drop the class probabilities when they were never measured.

        Same contract as ``AuditTrace._omit_absent_probe``: a key appears only
        when something recorded it. A stub entailer, or any trace written
        before 2026-08-05, round-trips byte-identically — which matters
        because preserved DEV suites embed whole traces and re-serialize them on
        replay. An absent measurement must never serialize as a measured null.
        """
        data: dict[str, Any] = handler(self)
        for key in self._OPTIONAL_PROBABILITY_FIELDS:
            if data.get(key) is None:
                data.pop(key, None)
        return data


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
    file ``cal-rules-v1.13.0.yaml`` by
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
    source_boundary: SourceBoundary | None = None
    """Declared coverage of ``passages`` over their source. See :data:`SourceBoundary`.

    Deliberately on the request rather than ``AuditConfig``: it is a property of
    the evidence supplied for this claim, not a run tunable, and putting it in
    the config would change ``audit_config_hash`` on every existing trace.
    """
    claimed_material_is_a_named_gap: bool = False
    """Caller-declared: under ``named_missing_material``, the denied material is
    among the named gaps, so the source is stipulated to address it.

    Not inferred from lexical overlap. Default False keeps every existing
    request byte-compatible.
    """


class NegationProbe(_StrictModel):
    """The recorded A4 negation-consistency probe (``cal-rules-v1.7.0``).

    Computed by the pipeline when the aggregated signal is a hard-contradiction
    candidate: the structurally negated claim is entailed against the same
    contributing premise, and the result is recorded here so the rules layer's
    confirmation stays deterministic and the trace replays without the model.
    ``abstained`` means the structural negator declined (compound or unhandled
    shape) — an abstention never demotes.
    """

    negated_claim: str | None
    abstained: bool
    result: EntailResult | None


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
    negation_probe: NegationProbe | None = None

    @model_serializer(mode="wrap")
    def _omit_absent_probe(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        """Serialize without ``negation_probe`` when no probe ran.

        The key appears only when the pipeline actually recorded a probe, so
        every pre-v1.7.0 trace byte-shape (goldens, preserved DEV suites)
        stays valid and unprobed traces round-trip unchanged.
        """
        data: dict[str, Any] = handler(self)
        if data.get("negation_probe") is None:
            data.pop("negation_probe", None)
        return data


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
    "NegationProbe",
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
