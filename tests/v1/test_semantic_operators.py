"""Guarded D5 operator controls through the shared validity contract."""

from __future__ import annotations

from typing import Literal

import pytest

from claim_audit_lab.v1.decision_model import (
    CANONICAL_STAGE_ORDER,
    ChannelApertureAssessment,
    ChannelMeasurement,
    EligibilityAssessment,
    EvidenceContribution,
    EvidenceDecisionInput,
    StageReceipt,
    ValidityAssessment,
    evaluate_evidence,
)
from claim_audit_lab.v1.features import negate_claim
from claim_audit_lab.v1.semantic_operators import (
    SemanticProbeReceipt,
    assess_negation_probe,
    project_negation,
)

_MODEL_RECEIPT = "sha256:" + "a" * 64
_POLICY_RECEIPT = "sha256:" + "b" * 64
_SOURCE_RECEIPT = "sha256:" + "c" * 64
_PROBE_RECEIPT = "sha256:" + "d" * 64
_APERTURE_RECEIPT = "sha256:" + "e" * 64


def _eligibility() -> EligibilityAssessment:
    return EligibilityAssessment(
        status="eligible",
        reason="frozen D5 fixture uses one admitted primary passage",
        evidence_path="2026-08-07 D5 packet",
        receipt_sha256=_SOURCE_RECEIPT,
    )


def _apertures() -> tuple[ChannelApertureAssessment, ...]:
    return tuple(
        ChannelApertureAssessment(
            channel=channel,
            status="complete",
            reason="the preregistered D5 packet admits exactly one authored passage",
            evidence_path="D5 PREREGISTRATION.md",
            receipt_sha256=_APERTURE_RECEIPT,
        )
        for channel in ("support", "refutation")
    )


def _stage_receipts() -> tuple[StageReceipt, ...]:
    return tuple(
        StageReceipt(
            stage=stage,  # type: ignore[arg-type]
            evidence_path=f"D5 {stage} receipt",
            receipt_sha256="sha256:" + f"{index + 6:064x}",
        )
        for index, stage in enumerate(CANONICAL_STAGE_ORDER)
    )


def _input(
    *,
    claim_id: str,
    contribution: EvidenceContribution | None,
) -> EvidenceDecisionInput:
    support_score = 0.01
    refutation_score = 0.01
    if contribution is not None:
        assert contribution.score is not None
        if contribution.channel == "support":
            support_score = contribution.score
        else:
            refutation_score = contribution.score
    return EvidenceDecisionInput(
        claim_id=claim_id,
        scope_status="in_scope",
        stage_receipts=_stage_receipts(),
        admitted_passage_ids=("p1",),
        measurements=(
            ChannelMeasurement(
                passage_id="p1",
                support_score=support_score,
                refutation_score=refutation_score,
                evidence_path="frozen pinned direct NLI receipt",
                receipt_sha256=_MODEL_RECEIPT,
            ),
        ),
        apertures=_apertures(),
        signal_floor=0.20,
        support_threshold=0.70,
        refutation_threshold=0.70,
        policy_id="frozen current-threshold fixture",
        policy_receipt_sha256=_POLICY_RECEIPT,
        contributions=() if contribution is None else (contribution,),
    )


def _direct(
    *,
    claim_id: str,
    channel: Literal["support", "refutation"],
    validity: ValidityAssessment,
    score: float = 0.95,
) -> EvidenceContribution:
    return EvidenceContribution(
        contribution_id=f"{claim_id}:{channel}",
        channel=channel,
        passage_ids=("p1",),
        score=score,
        score_method="direct_nli_probability",
        score_receipt_sha256=_MODEL_RECEIPT,
        origin="direct_nli",
        eligibility=_eligibility(),
        validity=validity,
    )


def _direct_validity() -> ValidityAssessment:
    return ValidityAssessment(
        status="valid",
        reason="direct support needs no polarity-changing operator",
        evidence_path="frozen direct NLI receipt",
        receipt_sha256=_MODEL_RECEIPT,
        operator="direct_claim_identity",
    )


def _probe(
    *,
    hypothesis: str | None,
    label: Literal["entail", "neutral", "contradict"] | None,
    passage_ids: tuple[str, ...] = ("p1",),
) -> SemanticProbeReceipt:
    return SemanticProbeReceipt(
        passage_ids=passage_ids,
        hypothesis=hypothesis,
        label=label,
        abstained=hypothesis is None,
        evidence_path="frozen pinned probe receipt",
        receipt_sha256=_PROBE_RECEIPT,
    )


def test_pinned_negative_existential_has_exact_canonical_complement() -> None:
    projection = project_negation("No leak was reported during the shift.")
    assert projection.kind == "negative_existential"
    assert projection.complement == "At least one leak was reported during the shift."


@pytest.mark.parametrize(
    ("claim", "reason_fragment"),
    [
        ("No more than one leak was reported.", "bounded"),
        ("No leak was not reported.", "already contains negation"),
        ("No leak was never reported.", "already contains negation"),
        ("No deviations were reported.", "plural agreement"),
        ("No one was notified.", "different quantifier scope"),
        ("No leak was reported or investigated.", "compound"),
        ("None of the leaks was reported.", "outside the pinned"),
        ("No leak can be reported.", "outside the pinned"),
    ],
)
def test_unpinned_or_ambiguous_negative_existential_scope_is_unknown(
    claim: str, reason_fragment: str
) -> None:
    projection = project_negation(claim)
    assert projection.kind == "unknown"
    assert projection.complement is None
    assert reason_fragment in projection.reason


def test_ordinary_negation_delegates_without_change() -> None:
    claim = "The leak was reported."
    projection = project_negation(claim)
    assert projection.kind == "ordinary"
    assert projection.complement == negate_claim(claim)


@pytest.mark.parametrize("label", ["neutral", "contradict"])
def test_matching_probe_that_does_not_entail_complement_is_invalid(
    label: Literal["neutral", "contradict"],
) -> None:
    assessment = assess_negation_probe(
        claim="No leak was reported during the shift.",
        contribution_passage_ids=("p1",),
        receipt=_probe(hypothesis="At least one leak was reported during the shift.", label=label),
    )
    assert assessment.status == "invalid"


def test_passage_or_hypothesis_mismatch_and_operator_abstention_are_unknown() -> None:
    passage_mismatch = assess_negation_probe(
        claim="No leak was reported during the shift.",
        contribution_passage_ids=("p2",),
        receipt=_probe(
            hypothesis="At least one leak was reported during the shift.", label="entail"
        ),
    )
    hypothesis_mismatch = assess_negation_probe(
        claim="No leak was reported during the shift.",
        contribution_passage_ids=("p1",),
        receipt=_probe(hypothesis="No leak was not reported.", label="entail"),
    )
    bounded = assess_negation_probe(
        claim="No more than one leak was reported during the shift.",
        contribution_passage_ids=("p1",),
        receipt=_probe(hypothesis=None, label=None),
    )
    assert passage_mismatch.status == "unknown"
    assert hypothesis_mismatch.status == "unknown"
    assert bounded.status == "unknown"


def test_frozen_five_case_outcome_matrix() -> None:
    canonical = assess_negation_probe(
        claim="No leak was reported during the shift.",
        contribution_passage_ids=("p1",),
        receipt=_probe(
            hypothesis="At least one leak was reported during the shift.", label="entail"
        ),
    )
    ordinary_claim = "The system did not archive records."
    ordinary_complement = negate_claim(ordinary_claim)
    assert ordinary_complement is not None
    ordinary = assess_negation_probe(
        claim=ordinary_claim,
        contribution_passage_ids=("p1",),
        receipt=_probe(hypothesis=ordinary_complement, label="entail"),
    )
    ambiguous = assess_negation_probe(
        claim="No more than one leak was reported during the shift.",
        contribution_passage_ids=("p1",),
        receipt=_probe(hypothesis=None, label=None),
    )
    cases = {
        "d5-supported": _input(
            claim_id="d5-supported",
            contribution=_direct(
                claim_id="d5-supported",
                channel="support",
                validity=_direct_validity(),
            ),
        ),
        "d5-refuted": _input(
            claim_id="d5-refuted",
            contribution=_direct(
                claim_id="d5-refuted",
                channel="refutation",
                validity=canonical,
            ),
        ),
        "d5-insufficient": _input(claim_id="d5-insufficient", contribution=None),
        "ordinary-refuted": _input(
            claim_id="ordinary-refuted",
            contribution=_direct(
                claim_id="ordinary-refuted",
                channel="refutation",
                validity=ordinary,
            ),
        ),
        "d5-ambiguous": _input(
            claim_id="d5-ambiguous",
            contribution=_direct(
                claim_id="d5-ambiguous",
                channel="refutation",
                validity=ambiguous,
            ),
        ),
    }
    outcomes = {case_id: evaluate_evidence(inputs).decision for case_id, inputs in cases.items()}
    assert outcomes["d5-supported"].verdict == "supported"
    assert outcomes["d5-refuted"].verdict == "contradicted"
    assert outcomes["d5-insufficient"].reason_code == "evidence_read_no_signal"
    assert outcomes["ordinary-refuted"].verdict == "contradicted"
    assert outcomes["d5-ambiguous"].reason_code == "semantic_validity_unknown"
    assert outcomes["d5-ambiguous"].basis_contribution_ids == ("d5-ambiguous:refutation",)
