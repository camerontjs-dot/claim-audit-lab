"""Strict contribution ledger and decide-or-abstain candidate for CAL v1.

The legacy production pipeline condenses all admitted passages to one
``SupportSignal``.  This additive module retains per-passage channel coverage,
keeps support and refutation independent, records eligibility and semantic
validity separately, and permits only explicitly eligible and valid contributions
to decide.  It does not alter ``AuditTrace`` or the production verdict path.
"""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from claim_audit_lab.v1.evidence_state import EvidenceState

EvidenceChannel = Literal["support", "refutation"]
ContributionOrigin = Literal["direct_nli", "semantic_operator"]
EligibilityStatus = Literal["eligible", "ineligible", "unknown"]
ValidityStatus = Literal["valid", "invalid", "unknown"]
ApertureStatus = Literal["complete", "incomplete", "unknown"]
ScopeStatus = Literal["in_scope", "out_of_scope", "unknown"]
StageName = Literal[
    "scope_identity",
    "decomposition",
    "retrieve_admit",
    "measure",
    "eligibility",
    "semantic_validity",
    "aperture",
    "aggregate",
    "resolve",
]
DecisionDisposition = Literal["decided", "abstained"]
ResolvedVerdict = Literal["supported", "contradicted"]
DecisionReasonCode = Literal[
    "support_above_threshold",
    "refutation_above_threshold",
    "out_of_scope",
    "scope_unknown",
    "no_evidence",
    "channels_unmeasured",
    "evidence_read_no_signal",
    "eligibility_unknown",
    "no_eligible_contribution",
    "semantic_validity_unknown",
    "no_valid_contribution",
    "aperture_unknown",
    "aperture_incomplete",
    "mixed_valid_evidence",
    "contribution_score_unmeasured",
    "support_below_decision_threshold",
    "refutation_below_decision_threshold",
]
Sha256Receipt = Annotated[str, StringConstraints(pattern=r"^sha256:[0-9a-f]{64}$")]


class _StrictModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class ChannelMeasurement(_StrictModel):
    """Independent channel coverage retained for one admitted passage."""

    passage_id: str = Field(min_length=1)
    support_score: float | None = Field(default=None, ge=0.0, le=1.0)
    refutation_score: float | None = Field(default=None, ge=0.0, le=1.0)
    receipt_sha256: Sha256Receipt
    evidence_path: str = Field(min_length=1)


class EligibilityAssessment(_StrictModel):
    """Source/policy eligibility for one contribution or passage set."""

    status: EligibilityStatus
    reason: str = Field(min_length=1)
    evidence_path: str = Field(min_length=1)
    receipt_sha256: Sha256Receipt


class ValidityAssessment(_StrictModel):
    """Semantic-operator validity for one contribution or passage set."""

    status: ValidityStatus
    reason: str = Field(min_length=1)
    evidence_path: str = Field(min_length=1)
    receipt_sha256: Sha256Receipt
    operator: str = Field(min_length=1)


class ChannelApertureAssessment(_StrictModel):
    """Whether the admitted passage set was completely assessed for one channel."""

    channel: EvidenceChannel
    status: ApertureStatus
    reason: str = Field(min_length=1)
    evidence_path: str = Field(min_length=1)
    receipt_sha256: Sha256Receipt


CANONICAL_STAGE_ORDER: tuple[StageName, ...] = (
    "scope_identity",
    "decomposition",
    "retrieve_admit",
    "measure",
    "eligibility",
    "semantic_validity",
    "aperture",
    "aggregate",
    "resolve",
)


class StageReceipt(_StrictModel):
    """Receipt for one ordered handoff in the shadow decision machine."""

    stage: StageName
    evidence_path: str = Field(min_length=1)
    receipt_sha256: Sha256Receipt


class EvidenceContribution(_StrictModel):
    """One independently auditable position taken by one passage or passage set."""

    contribution_id: str = Field(min_length=1)
    channel: EvidenceChannel
    passage_ids: tuple[str, ...]
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    score_method: str | None = Field(default=None, min_length=1)
    score_receipt_sha256: Sha256Receipt | None = None
    origin: ContributionOrigin
    eligibility: EligibilityAssessment
    validity: ValidityAssessment

    @field_validator("passage_ids")
    @classmethod
    def _canonical_passage_set(cls, passage_ids: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(passage_id.strip() for passage_id in passage_ids)
        if not normalized or any(not passage_id for passage_id in normalized):
            raise ValueError("a contribution requires at least one non-empty passage ID")
        if len(set(normalized)) != len(normalized):
            raise ValueError("a contribution passage set may not contain duplicate IDs")
        return tuple(sorted(normalized))

    @model_validator(mode="after")
    def _validate_score_receipt(self) -> Self:
        score_fields = (self.score, self.score_method, self.score_receipt_sha256)
        if any(value is None for value in score_fields) and any(
            value is not None for value in score_fields
        ):
            raise ValueError("score, score method, and score receipt must be present together")
        if self.origin == "direct_nli":
            if len(self.passage_ids) != 1:
                raise ValueError("a direct NLI contribution must name exactly one passage")
            if self.score is None or self.score_method != "direct_nli_probability":
                raise ValueError(
                    "a direct NLI contribution requires its recorded channel probability"
                )
        return self


class EvidenceDecisionInput(_StrictModel):
    """Receipt-bound inputs to the candidate state and decision sequence."""

    claim_id: str = Field(min_length=1)
    scope_status: ScopeStatus
    stage_receipts: tuple[StageReceipt, ...]
    admitted_passage_ids: tuple[str, ...]
    measurements: tuple[ChannelMeasurement, ...]
    apertures: tuple[ChannelApertureAssessment, ...]
    signal_floor: float = Field(ge=0.0, le=1.0)
    support_threshold: float = Field(ge=0.0, le=1.0)
    refutation_threshold: float = Field(ge=0.0, le=1.0)
    policy_id: str = Field(min_length=1)
    policy_receipt_sha256: Sha256Receipt
    contributions: tuple[EvidenceContribution, ...] = ()

    @field_validator("admitted_passage_ids")
    @classmethod
    def _canonical_admitted_passages(cls, passage_ids: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(passage_id.strip() for passage_id in passage_ids)
        if any(not passage_id for passage_id in normalized):
            raise ValueError("admitted passage IDs may not be empty")
        if len(set(normalized)) != len(normalized):
            raise ValueError("admitted passage IDs may not be duplicated")
        return tuple(sorted(normalized))

    @field_validator("measurements")
    @classmethod
    def _canonical_measurements(
        cls, measurements: tuple[ChannelMeasurement, ...]
    ) -> tuple[ChannelMeasurement, ...]:
        return tuple(sorted(measurements, key=lambda item: item.passage_id))

    @field_validator("apertures")
    @classmethod
    def _canonical_apertures(
        cls, apertures: tuple[ChannelApertureAssessment, ...]
    ) -> tuple[ChannelApertureAssessment, ...]:
        return tuple(sorted(apertures, key=lambda item: item.channel))

    @model_validator(mode="after")
    def _validate_receipt_coherence(self) -> Self:
        stage_order = tuple(item.stage for item in self.stage_receipts)
        if stage_order != CANONICAL_STAGE_ORDER:
            raise ValueError(
                "stage receipts must follow the canonical CAL order: "
                + " -> ".join(CANONICAL_STAGE_ORDER)
            )
        if self.support_threshold < self.signal_floor:
            raise ValueError("support threshold may not be below the signal floor")
        if self.refutation_threshold < self.signal_floor:
            raise ValueError("refutation threshold may not be below the signal floor")

        aperture_channels = [item.channel for item in self.apertures]
        if aperture_channels != ["refutation", "support"]:
            raise ValueError("exactly one support and one refutation aperture are required")

        admitted = set(self.admitted_passage_ids)
        measurement_ids = [item.passage_id for item in self.measurements]
        if len(set(measurement_ids)) != len(measurement_ids):
            raise ValueError("a passage may have at most one channel-measurement receipt")
        if not set(measurement_ids).issubset(admitted):
            raise ValueError("channel measurements may name only admitted passages")
        if not admitted and (self.measurements or self.contributions):
            raise ValueError("no-evidence inputs may not contain measurements or contributions")

        contribution_ids = [item.contribution_id for item in self.contributions]
        if len(set(contribution_ids)) != len(contribution_ids):
            raise ValueError("contribution IDs must be unique within one decision input")
        for contribution in self.contributions:
            missing = set(contribution.passage_ids) - admitted
            if missing:
                raise ValueError(
                    "contribution passage IDs must be admitted: " + ", ".join(sorted(missing))
                )
            if contribution.score is not None and contribution.score < self.signal_floor:
                raise ValueError("contribution score may not be below the signal floor")

        measurements_by_id = {item.passage_id: item for item in self.measurements}
        expected_direct: dict[tuple[EvidenceChannel, str], tuple[float, Sha256Receipt]] = {}
        for passage_id, measurement in measurements_by_id.items():
            channel_scores: tuple[tuple[EvidenceChannel, float | None], ...] = (
                ("support", measurement.support_score),
                ("refutation", measurement.refutation_score),
            )
            for channel, score in channel_scores:
                if score is not None and score >= self.signal_floor:
                    expected_direct[(channel, passage_id)] = (score, measurement.receipt_sha256)

        actual_direct: dict[tuple[EvidenceChannel, str], list[EvidenceContribution]] = {}
        for contribution in self.contributions:
            if contribution.origin == "direct_nli":
                key = (contribution.channel, contribution.passage_ids[0])
                actual_direct.setdefault(key, []).append(contribution)
        if set(actual_direct) != set(expected_direct):
            raise ValueError(
                "direct NLI contributions must exactly cover above-floor channel measurements"
            )
        for key, contributions in actual_direct.items():
            if len(contributions) != 1:
                raise ValueError("each above-floor channel measurement has one contribution")
            contribution = contributions[0]
            expected_score, expected_receipt = expected_direct[key]
            if (
                contribution.score != expected_score
                or contribution.score_receipt_sha256 != expected_receipt
            ):
                raise ValueError("direct NLI contribution must match its measurement receipt")
        return self


class AggregatedEvidence(_StrictModel):
    """One state snapshot over a named subset of the same contribution ledger."""

    state: EvidenceState
    contribution_ids: tuple[str, ...]
    support_contribution_ids: tuple[str, ...]
    refutation_contribution_ids: tuple[str, ...]
    best_support_score: float | None = Field(default=None, ge=0.0, le=1.0)
    best_refutation_score: float | None = Field(default=None, ge=0.0, le=1.0)


class DecisionOutcome(_StrictModel):
    """A resolved degree or explicit abstention with its exact basis ledger IDs."""

    disposition: DecisionDisposition
    verdict: ResolvedVerdict | None
    reason_code: DecisionReasonCode
    reason: str = Field(min_length=1)
    basis_contribution_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_pairing(self) -> Self:
        if self.disposition == "decided" and (
            self.verdict is None or not self.basis_contribution_ids
        ):
            raise ValueError("a decided outcome requires a verdict and contribution basis")
        if self.disposition == "abstained" and self.verdict is not None:
            raise ValueError("an abstention may not carry a verdict")
        return self


class EvidenceDecisionTrace(_StrictModel):
    """Receipt-bound input ledger, three state snapshots, and candidate decision."""

    inputs: EvidenceDecisionInput
    raw: AggregatedEvidence
    eligible: AggregatedEvidence
    valid: AggregatedEvidence
    decision: DecisionOutcome


def _channels_fully_measured(
    admitted_passage_ids: tuple[str, ...], measurements: tuple[ChannelMeasurement, ...]
) -> bool:
    by_id = {item.passage_id: item for item in measurements}
    return all(
        passage_id in by_id
        and by_id[passage_id].support_score is not None
        and by_id[passage_id].refutation_score is not None
        for passage_id in admitted_passage_ids
    )


def aggregate_evidence(
    *,
    admitted_passage_ids: tuple[str, ...],
    measurements: tuple[ChannelMeasurement, ...],
    contributions: tuple[EvidenceContribution, ...],
) -> AggregatedEvidence:
    """Compute one evidence state; all stages use this single implementation."""
    ordered = tuple(sorted(contributions, key=lambda item: item.contribution_id))
    support = tuple(item for item in ordered if item.channel == "support")
    refutation = tuple(item for item in ordered if item.channel == "refutation")

    if not admitted_passage_ids:
        state: EvidenceState = "no_evidence"
    elif not _channels_fully_measured(admitted_passage_ids, measurements):
        state = "unmeasured"
    elif support and refutation:
        state = "mixed"
    elif support:
        state = "support_only"
    elif refutation:
        state = "refutation_only"
    else:
        state = "read_silent"

    return AggregatedEvidence(
        state=state,
        contribution_ids=tuple(item.contribution_id for item in ordered),
        support_contribution_ids=tuple(item.contribution_id for item in support),
        refutation_contribution_ids=tuple(item.contribution_id for item in refutation),
        best_support_score=max(
            (item.score for item in support if item.score is not None), default=None
        ),
        best_refutation_score=max(
            (item.score for item in refutation if item.score is not None), default=None
        ),
    )


def _abstain(
    reason_code: DecisionReasonCode,
    reason: str,
    basis: tuple[str, ...] = (),
) -> DecisionOutcome:
    return DecisionOutcome(
        disposition="abstained",
        verdict=None,
        reason_code=reason_code,
        reason=reason,
        basis_contribution_ids=tuple(sorted(basis)),
    )


def _top_contributions(
    contributions: tuple[EvidenceContribution, ...], channel: EvidenceChannel
) -> tuple[float | None, tuple[str, ...]]:
    candidates = tuple(item for item in contributions if item.channel == channel)
    if any(item.score is None for item in candidates):
        return None, tuple(sorted(item.contribution_id for item in candidates))
    best = max(item.score for item in candidates if item.score is not None)
    basis = tuple(sorted(item.contribution_id for item in candidates if item.score == best))
    return best, basis


def _decide_from_valid(
    inputs: EvidenceDecisionInput,
    valid: tuple[EvidenceContribution, ...],
    state: EvidenceState,
) -> DecisionOutcome:
    if state == "mixed":
        return _abstain(
            "mixed_valid_evidence",
            "eligible, semantically valid support and refutation both remain",
            tuple(item.contribution_id for item in valid),
        )
    channel: EvidenceChannel = "support" if state == "support_only" else "refutation"
    score, basis = _top_contributions(valid, channel)
    if score is None:
        return _abstain(
            "contribution_score_unmeasured",
            "a valid contribution lacks a receipt-bound decision score",
            basis,
        )
    threshold = inputs.support_threshold if channel == "support" else inputs.refutation_threshold
    if score < threshold:
        code: DecisionReasonCode = (
            "support_below_decision_threshold"
            if channel == "support"
            else "refutation_below_decision_threshold"
        )
        return _abstain(
            code,
            f"best valid {channel} score {score:.4f} is below the receipt-bound "
            f"decision threshold {threshold:.4f}",
            basis,
        )
    verdict: ResolvedVerdict = "supported" if channel == "support" else "contradicted"
    code = "support_above_threshold" if channel == "support" else "refutation_above_threshold"
    return DecisionOutcome(
        disposition="decided",
        verdict=verdict,
        reason_code=code,
        reason=(
            f"best valid {channel} score {score:.4f} is at or above the receipt-bound "
            f"decision threshold {threshold:.4f}"
        ),
        basis_contribution_ids=basis,
    )


def evaluate_evidence(inputs: EvidenceDecisionInput) -> EvidenceDecisionTrace:
    """Run raw -> eligible -> semantically valid -> decide/abstain."""
    raw_contributions = tuple(item for item in inputs.contributions if item.origin == "direct_nli")
    eligible_contributions = tuple(
        item for item in raw_contributions if item.eligibility.status == "eligible"
    )
    all_eligible_contributions = tuple(
        item for item in inputs.contributions if item.eligibility.status == "eligible"
    )
    valid_contributions = tuple(
        item for item in all_eligible_contributions if item.validity.status == "valid"
    )
    raw = aggregate_evidence(
        admitted_passage_ids=inputs.admitted_passage_ids,
        measurements=inputs.measurements,
        contributions=raw_contributions,
    )
    eligible = aggregate_evidence(
        admitted_passage_ids=inputs.admitted_passage_ids,
        measurements=inputs.measurements,
        contributions=eligible_contributions,
    )
    valid = aggregate_evidence(
        admitted_passage_ids=inputs.admitted_passage_ids,
        measurements=inputs.measurements,
        contributions=valid_contributions,
    )

    eligibility_unknown = tuple(
        item.contribution_id
        for item in inputs.contributions
        if item.eligibility.status == "unknown"
    )
    validity_unknown = tuple(
        item.contribution_id
        for item in all_eligible_contributions
        if item.validity.status == "unknown"
    )
    aperture_incomplete = tuple(item for item in inputs.apertures if item.status == "incomplete")
    aperture_unknown = tuple(item for item in inputs.apertures if item.status == "unknown")

    if inputs.scope_status == "out_of_scope":
        decision = _abstain("out_of_scope", "claim is explicitly outside the audit scope")
    elif inputs.scope_status == "unknown":
        decision = _abstain("scope_unknown", "claim scope is unresolved")
    elif raw.state == "no_evidence":
        decision = _abstain("no_evidence", "no passage reached the measurement stage")
    elif raw.state == "unmeasured":
        decision = _abstain(
            "channels_unmeasured",
            "at least one admitted passage lacks an independent channel measurement",
            tuple(item.contribution_id for item in inputs.contributions),
        )
    elif eligibility_unknown:
        decision = _abstain(
            "eligibility_unknown",
            "at least one signal contribution has unresolved eligibility",
            eligibility_unknown,
        )
    elif validity_unknown:
        decision = _abstain(
            "semantic_validity_unknown",
            "at least one eligible contribution has unresolved semantic validity",
            validity_unknown,
        )
    elif aperture_incomplete:
        decision = _abstain(
            "aperture_incomplete",
            "at least one channel is known to have an incomplete passage assessment",
            tuple(item.contribution_id for item in inputs.contributions),
        )
    elif aperture_unknown:
        decision = _abstain(
            "aperture_unknown",
            "passage-set completeness is unresolved for at least one channel",
            tuple(item.contribution_id for item in inputs.contributions),
        )
    elif valid.state in {"support_only", "refutation_only", "mixed"}:
        decision = _decide_from_valid(inputs, valid_contributions, valid.state)
    elif raw.state == "read_silent" and not inputs.contributions:
        decision = _abstain(
            "evidence_read_no_signal",
            "all admitted evidence was measured below the stated signal floor",
        )
    elif not all_eligible_contributions:
        decision = _abstain(
            "no_eligible_contribution",
            "all measured signal contributions are explicitly ineligible",
            tuple(item.contribution_id for item in inputs.contributions),
        )
    else:
        decision = _abstain(
            "no_valid_contribution",
            "all eligible signal contributions are explicitly semantically invalid",
            tuple(item.contribution_id for item in all_eligible_contributions),
        )

    return EvidenceDecisionTrace(
        inputs=inputs,
        raw=raw,
        eligible=eligible,
        valid=valid,
        decision=decision,
    )


__all__ = [
    "AggregatedEvidence",
    "ApertureStatus",
    "CANONICAL_STAGE_ORDER",
    "ChannelApertureAssessment",
    "ChannelMeasurement",
    "ContributionOrigin",
    "DecisionDisposition",
    "DecisionOutcome",
    "DecisionReasonCode",
    "EligibilityAssessment",
    "EligibilityStatus",
    "EvidenceChannel",
    "EvidenceContribution",
    "EvidenceDecisionInput",
    "EvidenceDecisionTrace",
    "ResolvedVerdict",
    "ScopeStatus",
    "Sha256Receipt",
    "StageName",
    "StageReceipt",
    "ValidityAssessment",
    "ValidityStatus",
    "aggregate_evidence",
    "evaluate_evidence",
]
