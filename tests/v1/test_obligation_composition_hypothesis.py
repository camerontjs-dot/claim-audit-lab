"""Preregistered CAL shadow experiment for evidence relations and obligations.

This suite is deliberately research-only.  A passing test can mean either:
* a control behaves as required, or
* a preregistered production limitation was successfully reproduced.

Nothing here changes the released ``run_audit`` path.  The experiment compares
the current max-winner aggregation with additive shadow machinery already
present on ``main``.
"""

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
    EvidenceDecisionTrace,
    StageReceipt,
    ValidityAssessment,
    evaluate_evidence,
)
from claim_audit_lab.v1.explicit_claims import aggregate_explicit_claim_verdicts
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.models import EntailResult, Verdict

_RECEIPT = "sha256:" + "1" * 64
_POLICY_RECEIPT = "sha256:" + "2" * 64


def _nli(
    passage_id: str,
    *,
    label: Literal["entail", "neutral", "contradict"],
    score: float,
    support: float,
    refutation: float,
) -> EntailResult:
    """Construct one deterministic NLI observation for aggregation probes."""
    return EntailResult(
        passage_id=passage_id,
        label=label,
        score=score,
        raw_logits=(0.0, 0.0, 0.0),
        p_entail=support,
        p_contradict=refutation,
    )


def _assessment(
    *,
    eligibility: Literal["eligible", "ineligible", "unknown"] = "eligible",
    validity: Literal["valid", "invalid", "unknown"] = "valid",
) -> tuple[EligibilityAssessment, ValidityAssessment]:
    return (
        EligibilityAssessment(
            status=eligibility,
            reason=f"constructed eligibility: {eligibility}",
            evidence_path="research fixture / eligibility",
            receipt_sha256=_RECEIPT,
        ),
        ValidityAssessment(
            status=validity,
            reason=f"constructed semantic validity: {validity}",
            evidence_path="research fixture / validity",
            receipt_sha256=_RECEIPT,
            operator="constructed_direct_relation",
        ),
    )


def _contribution(
    contribution_id: str,
    passage_id: str,
    *,
    channel: Literal["support", "refutation"],
    score: float,
    eligibility: Literal["eligible", "ineligible", "unknown"] = "eligible",
    validity: Literal["valid", "invalid", "unknown"] = "valid",
) -> EvidenceContribution:
    eligible, valid = _assessment(eligibility=eligibility, validity=validity)
    return EvidenceContribution(
        contribution_id=contribution_id,
        channel=channel,
        passage_ids=(passage_id,),
        score=score,
        score_method="direct_nli_probability",
        score_receipt_sha256=_RECEIPT,
        origin="direct_nli",
        eligibility=eligible,
        validity=valid,
    )


def _stage_receipts() -> tuple[StageReceipt, ...]:
    return tuple(
        StageReceipt(
            stage=stage,
            evidence_path=f"research fixture / {stage}",
            receipt_sha256="sha256:" + f"{index + 3:064x}",
        )
        for index, stage in enumerate(CANONICAL_STAGE_ORDER)
    )


def _apertures(
    *,
    support: Literal["complete", "incomplete", "unknown"] = "complete",
    refutation: Literal["complete", "incomplete", "unknown"] = "complete",
) -> tuple[ChannelApertureAssessment, ...]:
    return (
        ChannelApertureAssessment(
            channel="support",
            status=support,
            reason=f"constructed support aperture: {support}",
            evidence_path="research fixture / support aperture",
            receipt_sha256=_RECEIPT,
        ),
        ChannelApertureAssessment(
            channel="refutation",
            status=refutation,
            reason=f"constructed refutation aperture: {refutation}",
            evidence_path="research fixture / refutation aperture",
            receipt_sha256=_RECEIPT,
        ),
    )


def _decision(
    *contributions: EvidenceContribution,
    apertures: tuple[ChannelApertureAssessment, ...] | None = None,
) -> EvidenceDecisionTrace:
    passage_ids = tuple(sorted({item.passage_ids[0] for item in contributions}))
    channel_by_passage: dict[str, dict[str, float]] = {
        passage_id: {"support": 0.01, "refutation": 0.01} for passage_id in passage_ids
    }
    for contribution in contributions:
        channel_by_passage[contribution.passage_ids[0]][contribution.channel] = (
            contribution.score if contribution.score is not None else 0.01
        )
    measurements = tuple(
        ChannelMeasurement(
            passage_id=passage_id,
            support_score=scores["support"],
            refutation_score=scores["refutation"],
            evidence_path="research fixture / channel measurement",
            receipt_sha256=_RECEIPT,
        )
        for passage_id, scores in sorted(channel_by_passage.items())
    )
    return evaluate_evidence(
        EvidenceDecisionInput(
            claim_id="research-claim",
            scope_status="in_scope",
            stage_receipts=_stage_receipts(),
            admitted_passage_ids=passage_ids,
            measurements=measurements,
            apertures=_apertures() if apertures is None else apertures,
            signal_floor=0.20,
            support_threshold=0.70,
            refutation_threshold=0.70,
            policy_id="research-obligation-shadow-v1",
            policy_receipt_sha256=_POLICY_RECEIPT,
            contributions=tuple(contributions),
        )
    )


def _verdict(
    degree: Literal[
        "supported",
        "partially_supported",
        "unsupported",
        "contradicted",
        "not_checkable",
    ],
) -> Verdict:
    return Verdict(
        support_verdict=degree,
        support_verdict_reason=None,
        audit_flags=[],
        citation_status="correct",
        audit_confidence="high",
    )


# Stage A: relation preservation versus max-winner aggregation.


def test_a01_score_winner_swap_changes_current_label_but_not_shadow_conflict() -> None:
    first = [
        _nli("support", label="entail", score=0.90, support=0.90, refutation=0.04),
        _nli("refute", label="contradict", score=0.91, support=0.03, refutation=0.91),
    ]
    swapped = [
        _nli("support", label="entail", score=0.92, support=0.92, refutation=0.04),
        _nli("refute", label="contradict", score=0.91, support=0.03, refutation=0.91),
    ]

    current = MaxEntailmentAggregator()
    assert current.aggregate(first).label == "contradict"
    assert current.aggregate(swapped).label == "entail"

    first_shadow = _decision(
        _contribution("s", "support", channel="support", score=0.90),
        _contribution("r", "refute", channel="refutation", score=0.91),
    )
    swapped_shadow = _decision(
        _contribution("s", "support", channel="support", score=0.92),
        _contribution("r", "refute", channel="refutation", score=0.91),
    )
    assert first_shadow.valid.state == "mixed"
    assert swapped_shadow.valid.state == "mixed"
    assert first_shadow.decision.reason_code == "mixed_valid_evidence"
    assert swapped_shadow.decision.reason_code == "mixed_valid_evidence"


def test_a02_equal_score_passage_order_breaks_current_tie_but_not_shadow_state() -> None:
    support = _nli("p-support", label="entail", score=0.90, support=0.90, refutation=0.04)
    refute = _nli("p-refute", label="contradict", score=0.90, support=0.03, refutation=0.90)

    current = MaxEntailmentAggregator()
    assert current.aggregate([support, refute]).label == "entail"
    assert current.aggregate([refute, support]).label == "contradict"

    shadow_one = _decision(
        _contribution("s", "p-support", channel="support", score=0.90),
        _contribution("r", "p-refute", channel="refutation", score=0.90),
    )
    shadow_two = _decision(
        _contribution("r", "p-refute", channel="refutation", score=0.90),
        _contribution("s", "p-support", channel="support", score=0.90),
    )
    assert shadow_one.valid == shadow_two.valid
    assert shadow_one.decision == shadow_two.decision


def test_a03_ineligible_higher_refutation_cannot_launder_over_eligible_support() -> None:
    current = MaxEntailmentAggregator().aggregate(
        [
            _nli("eligible-support", label="entail", score=0.90, support=0.90, refutation=0.04),
            _nli(
                "wrong-scope-refute",
                label="contradict",
                score=0.99,
                support=0.01,
                refutation=0.99,
            ),
        ]
    )
    assert current.label == "contradict"

    shadow = _decision(
        _contribution("s", "eligible-support", channel="support", score=0.90),
        _contribution(
            "r",
            "wrong-scope-refute",
            channel="refutation",
            score=0.99,
            eligibility="ineligible",
        ),
    )
    assert shadow.raw.state == "mixed"
    assert shadow.eligible.state == "support_only"
    assert shadow.decision.disposition == "decided"
    assert shadow.decision.verdict == "supported"
    assert shadow.decision.basis_contribution_ids == ("s",)


def test_a04_unknown_eligibility_blocks_decision_instead_of_silently_falling_back() -> None:
    shadow = _decision(
        _contribution("s", "support", channel="support", score=0.90),
        _contribution(
            "r",
            "uncertain-refute",
            channel="refutation",
            score=0.99,
            eligibility="unknown",
        ),
    )
    assert shadow.decision.disposition == "abstained"
    assert shadow.decision.reason_code == "eligibility_unknown"


# Stage B: semantic validity remains separate from measured NLI strength.


@pytest.mark.parametrize("status", ["invalid", "unknown"])
def test_b01_high_scoring_semantically_nonvalid_refutation_does_not_decide(
    status: Literal["invalid", "unknown"],
) -> None:
    shadow = _decision(
        _contribution("s", "support", channel="support", score=0.91),
        _contribution(
            "r",
            "refute",
            channel="refutation",
            score=0.99,
            validity=status,
        ),
    )
    if status == "invalid":
        assert shadow.decision.verdict == "supported"
        assert shadow.decision.basis_contribution_ids == ("s",)
    else:
        assert shadow.decision.verdict is None
        assert shadow.decision.reason_code == "semantic_validity_unknown"


# Stage C: aperture/completeness is a decision dependency, not a confidence modifier.


@pytest.mark.parametrize(
    ("apertures", "reason"),
    [
        (_apertures(refutation="unknown"), "aperture_unknown"),
        (_apertures(support="incomplete"), "aperture_incomplete"),
    ],
)
def test_c01_strong_local_support_cannot_launder_unknown_or_incomplete_aperture(
    apertures: tuple[ChannelApertureAssessment, ...],
    reason: str,
) -> None:
    shadow = _decision(
        _contribution("s", "support", channel="support", score=0.99),
        apertures=apertures,
    )
    assert shadow.valid.state == "support_only"
    assert shadow.decision.disposition == "abstained"
    assert shadow.decision.reason_code == reason


# Stage D: explicit obligation composition.  These are manually declared on
# purpose; automatic decomposition is a separate hypothesis.


def test_d01_all_required_obligations_must_be_supported_for_full_support() -> None:
    complete = aggregate_explicit_claim_verdicts(
        "all_of",
        [_verdict("supported"), _verdict("supported"), _verdict("supported")],
    )
    unresolved = aggregate_explicit_claim_verdicts(
        "all_of",
        [_verdict("supported"), _verdict("supported"), _verdict("not_checkable")],
    )
    assert complete.verdict.support_verdict == "supported"
    assert unresolved.verdict.support_verdict != "supported"


def test_d02_strong_supported_obligations_do_not_launder_an_unsupported_dependency() -> None:
    parent = aggregate_explicit_claim_verdicts(
        "all_of",
        [
            _verdict("supported"),
            _verdict("supported"),
            _verdict("supported"),
            _verdict("supported"),
            _verdict("supported"),
            _verdict("supported"),
            _verdict("supported"),
            _verdict("not_checkable"),
            _verdict("unsupported"),
        ],
    )
    assert parent.verdict.support_verdict == "partially_supported"
    assert parent.rule_id == "ECA-ALLOF-PARTIAL"


def test_d03_any_required_conjunct_contradiction_blocks_parent_support() -> None:
    parent = aggregate_explicit_claim_verdicts(
        "all_of",
        [_verdict("supported"), _verdict("contradicted"), _verdict("supported")],
    )
    assert parent.verdict.support_verdict == "contradicted"
    assert parent.rule_id == "ECA-ALLOF-CONTRADICTED"


# Stage E: safety controls.  Easy single-channel cases should remain easy.


@pytest.mark.parametrize(
    ("channel", "expected"),
    [("support", "supported"), ("refutation", "contradicted")],
)
def test_e01_easy_valid_single_channel_controls_still_resolve(
    channel: Literal["support", "refutation"],
    expected: str,
) -> None:
    shadow = _decision(
        _contribution("only", "p1", channel=channel, score=0.95),
    )
    assert shadow.decision.disposition == "decided"
    assert shadow.decision.verdict == expected
