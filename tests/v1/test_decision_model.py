"""Deterministic controls for the additive contribution-ledger candidate."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

import pytest
from pydantic import ValidationError

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

_MODEL_RECEIPT = "sha256:" + "1" * 64
_POLICY_RECEIPT = "sha256:" + "2" * 64
_ELIGIBILITY_RECEIPT = "sha256:" + "3" * 64
_VALIDITY_RECEIPT = "sha256:" + "4" * 64
_APERTURE_RECEIPT = "sha256:" + "5" * 64


def _stage_receipts(
    stages: tuple[str, ...] = CANONICAL_STAGE_ORDER,
) -> tuple[StageReceipt, ...]:
    return tuple(
        StageReceipt(
            stage=stage,  # type: ignore[arg-type]
            evidence_path=f"fixture {stage} receipt",
            receipt_sha256="sha256:" + f"{index + 6:064x}",
        )
        for index, stage in enumerate(stages)
    )


def _contribution(
    contribution_id: str,
    *,
    channel: Literal["support", "refutation"] = "support",
    score: float | None = 0.90,
    passage_ids: tuple[str, ...] = ("p1",),
    eligibility: Literal["eligible", "ineligible", "unknown"] = "eligible",
    validity: Literal["valid", "invalid", "unknown"] = "valid",
    origin: Literal["direct_nli", "semantic_operator"] = "direct_nli",
    score_method: str | None = None,
) -> EvidenceContribution:
    if score_method is None and score is not None:
        score_method = "direct_nli_probability" if origin == "direct_nli" else "fixture_set_score"
    return EvidenceContribution(
        contribution_id=contribution_id,
        channel=channel,
        passage_ids=passage_ids,
        score=score,
        score_method=score_method,
        score_receipt_sha256=_MODEL_RECEIPT if score is not None else None,
        origin=origin,
        eligibility=EligibilityAssessment(
            status=eligibility,
            reason=f"eligibility is {eligibility}",
            evidence_path="fixture source metadata",
            receipt_sha256=_ELIGIBILITY_RECEIPT,
        ),
        validity=ValidityAssessment(
            status=validity,
            reason=f"semantic validity is {validity}",
            evidence_path="fixture operator receipt",
            receipt_sha256=_VALIDITY_RECEIPT,
            operator="fixture_operator",
        ),
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
            reason=f"support aperture is {support}",
            evidence_path="fixture aperture receipt",
            receipt_sha256=_APERTURE_RECEIPT,
        ),
        ChannelApertureAssessment(
            channel="refutation",
            status=refutation,
            reason=f"refutation aperture is {refutation}",
            evidence_path="fixture aperture receipt",
            receipt_sha256=_APERTURE_RECEIPT,
        ),
    )


def _measurements_for(
    admitted: tuple[str, ...], contributions: tuple[EvidenceContribution, ...]
) -> tuple[ChannelMeasurement, ...]:
    scores = {passage_id: {"support": 0.01, "refutation": 0.01} for passage_id in admitted}
    for contribution in contributions:
        if contribution.origin != "direct_nli":
            continue
        assert contribution.score is not None
        passage_id = contribution.passage_ids[0]
        if passage_id in scores:
            scores[passage_id][contribution.channel] = contribution.score
    return tuple(
        ChannelMeasurement(
            passage_id=passage_id,
            support_score=values["support"],
            refutation_score=values["refutation"],
            evidence_path="fixture channel receipt",
            receipt_sha256=_MODEL_RECEIPT,
        )
        for passage_id, values in scores.items()
    )


def _inputs(
    *contributions: EvidenceContribution,
    admitted: tuple[str, ...] = ("p1",),
    measurements: tuple[ChannelMeasurement, ...] | None = None,
    apertures: tuple[ChannelApertureAssessment, ...] | None = None,
    stage_receipts: tuple[StageReceipt, ...] | None = None,
    scope: Literal["in_scope", "out_of_scope", "unknown"] = "in_scope",
) -> EvidenceDecisionInput:
    contribution_tuple = tuple(contributions)
    if measurements is None:
        measurements = _measurements_for(admitted, contribution_tuple)
    return EvidenceDecisionInput(
        claim_id="c1",
        scope_status=scope,
        stage_receipts=_stage_receipts() if stage_receipts is None else stage_receipts,
        admitted_passage_ids=admitted,
        measurements=measurements,
        apertures=_apertures() if apertures is None else apertures,
        signal_floor=0.20,
        support_threshold=0.70,
        refutation_threshold=0.70,
        policy_id="fixture-decision-policy",
        policy_receipt_sha256=_POLICY_RECEIPT,
        contributions=contribution_tuple,
    )


@pytest.mark.parametrize(
    ("inputs", "state", "reason"),
    [
        (_inputs(admitted=()), "no_evidence", "no_evidence"),
        (_inputs(admitted=("p1",), measurements=()), "unmeasured", "channels_unmeasured"),
        (
            _inputs(
                admitted=("p1",),
                measurements=(
                    ChannelMeasurement(
                        passage_id="p1",
                        support_score=0.01,
                        refutation_score=None,
                        evidence_path="partial fixture",
                        receipt_sha256=_MODEL_RECEIPT,
                    ),
                ),
            ),
            "unmeasured",
            "channels_unmeasured",
        ),
        (_inputs(), "read_silent", "evidence_read_no_signal"),
    ],
)
def test_safe_abstention_states_are_explicit(
    inputs: EvidenceDecisionInput, state: str, reason: str
) -> None:
    trace = evaluate_evidence(inputs)
    assert trace.raw.state == state
    assert trace.eligible.state == state
    assert trace.valid.state == state
    assert trace.decision.disposition == "abstained"
    assert trace.decision.verdict is None
    assert trace.decision.reason_code == reason


@pytest.mark.parametrize(
    ("contribution", "state", "verdict", "reason"),
    [
        (_contribution("s-high"), "support_only", "supported", "support_above_threshold"),
        (
            _contribution("r-high", channel="refutation"),
            "refutation_only",
            "contradicted",
            "refutation_above_threshold",
        ),
    ],
)
def test_easy_high_valid_single_channel_cases_resolve(
    contribution: EvidenceContribution, state: str, verdict: str, reason: str
) -> None:
    trace = evaluate_evidence(_inputs(contribution))
    assert trace.raw.state == state
    assert trace.eligible.state == state
    assert trace.valid.state == state
    assert trace.decision.disposition == "decided"
    assert trace.decision.verdict == verdict
    assert trace.decision.reason_code == reason
    assert trace.decision.basis_contribution_ids == (contribution.contribution_id,)


@pytest.mark.parametrize(
    ("contribution", "reason"),
    [
        (_contribution("s-low", score=0.40), "support_below_decision_threshold"),
        (
            _contribution("r-low", channel="refutation", score=0.40),
            "refutation_below_decision_threshold",
        ),
    ],
)
def test_reporting_floor_signal_does_not_authorize_a_low_score_verdict(
    contribution: EvidenceContribution, reason: str
) -> None:
    decision = evaluate_evidence(_inputs(contribution)).decision
    assert decision.disposition == "abstained"
    assert decision.verdict is None
    assert decision.reason_code == reason
    assert decision.basis_contribution_ids == (contribution.contribution_id,)


def test_mixed_valid_evidence_abstains_with_both_channel_ids() -> None:
    trace = evaluate_evidence(
        _inputs(
            _contribution("support", score=0.99),
            _contribution("refute", channel="refutation", score=0.21),
        )
    )
    assert trace.valid.state == "mixed"
    assert trace.decision.reason_code == "mixed_valid_evidence"
    assert trace.decision.basis_contribution_ids == ("refute", "support")


@pytest.mark.parametrize(
    ("contribution", "eligible_state", "valid_state", "reason"),
    [
        (
            _contribution("eligibility-unknown", eligibility="unknown"),
            "read_silent",
            "read_silent",
            "eligibility_unknown",
        ),
        (
            _contribution("ineligible", eligibility="ineligible"),
            "read_silent",
            "read_silent",
            "no_eligible_contribution",
        ),
        (
            _contribution("validity-unknown", validity="unknown"),
            "support_only",
            "read_silent",
            "semantic_validity_unknown",
        ),
        (
            _contribution("invalid", validity="invalid"),
            "support_only",
            "read_silent",
            "no_valid_contribution",
        ),
    ],
)
def test_non_deciding_assessments_remain_auditable(
    contribution: EvidenceContribution,
    eligible_state: str,
    valid_state: str,
    reason: str,
) -> None:
    trace = evaluate_evidence(_inputs(contribution))
    assert trace.raw.state == "support_only"
    assert trace.eligible.state == eligible_state
    assert trace.valid.state == valid_state
    assert trace.decision.disposition == "abstained"
    assert trace.decision.reason_code == reason
    assert trace.decision.basis_contribution_ids == (contribution.contribution_id,)


def test_unknown_signal_blocks_otherwise_valid_opposite_channel() -> None:
    eligibility = evaluate_evidence(
        _inputs(
            _contribution("valid-support", passage_ids=("p1",)),
            _contribution(
                "unknown-refutation",
                channel="refutation",
                passage_ids=("p2",),
                eligibility="unknown",
            ),
            admitted=("p1", "p2"),
        )
    ).decision
    validity = evaluate_evidence(
        _inputs(
            _contribution("valid-refutation", channel="refutation", passage_ids=("p1",)),
            _contribution(
                "unknown-support",
                passage_ids=("p2",),
                validity="unknown",
            ),
            admitted=("p1", "p2"),
        )
    ).decision
    assert eligibility.reason_code == "eligibility_unknown"
    assert eligibility.verdict is None
    assert eligibility.basis_contribution_ids == ("unknown-refutation",)
    assert validity.reason_code == "semantic_validity_unknown"
    assert validity.verdict is None
    assert validity.basis_contribution_ids == ("unknown-support",)


def test_explicitly_invalid_opposite_channel_does_not_block_valid_support() -> None:
    decision = evaluate_evidence(
        _inputs(
            _contribution("valid-support", passage_ids=("p1",)),
            _contribution(
                "invalid-refutation",
                channel="refutation",
                passage_ids=("p2",),
                validity="invalid",
            ),
            admitted=("p1", "p2"),
        )
    ).decision
    assert decision.verdict == "supported"
    assert decision.basis_contribution_ids == ("valid-support",)


@pytest.mark.parametrize(
    ("apertures", "reason"),
    [
        (_apertures(refutation="unknown"), "aperture_unknown"),
        (_apertures(support="incomplete"), "aperture_incomplete"),
    ],
)
def test_incomplete_or_unknown_passage_aperture_blocks_resolution(
    apertures: tuple[ChannelApertureAssessment, ...], reason: str
) -> None:
    decision = evaluate_evidence(_inputs(_contribution("support"), apertures=apertures)).decision
    assert decision.disposition == "abstained"
    assert decision.reason_code == reason
    assert decision.basis_contribution_ids == ("support",)


def test_scope_gate_precedes_evidence_decision() -> None:
    out = evaluate_evidence(_inputs(_contribution("support"), scope="out_of_scope"))
    unknown = evaluate_evidence(_inputs(_contribution("support"), scope="unknown"))
    assert out.valid.state == "support_only"
    assert out.decision.reason_code == "out_of_scope"
    assert out.decision.verdict is None
    assert unknown.decision.reason_code == "scope_unknown"
    assert unknown.decision.verdict is None


def test_stage_contract_requires_the_canonical_receipt_order() -> None:
    with pytest.raises(ValidationError, match="canonical CAL order"):
        _inputs(
            _contribution("support"),
            stage_receipts=_stage_receipts(CANONICAL_STAGE_ORDER[:-1]),
        )

    with pytest.raises(ValidationError, match="canonical CAL order"):
        _inputs(
            _contribution("support"),
            stage_receipts=_stage_receipts(tuple(reversed(CANONICAL_STAGE_ORDER))),
        )


def test_ordered_stage_receipts_do_not_weaken_aperture_abstention() -> None:
    trace = evaluate_evidence(
        _inputs(
            _contribution("support"),
            apertures=_apertures(refutation="unknown"),
        )
    )
    assert tuple(item.stage for item in trace.inputs.stage_receipts) == CANONICAL_STAGE_ORDER
    assert trace.decision.disposition == "abstained"
    assert trace.decision.reason_code == "aperture_unknown"
    assert trace.decision.verdict is None


def test_passage_set_is_first_class_and_canonical() -> None:
    contribution = _contribution(
        "support-set",
        passage_ids=("p2", "p1"),
        origin="semantic_operator",
        score_method="minimum_atom_support",
    )
    trace = evaluate_evidence(_inputs(contribution, admitted=("p2", "p1")))
    assert contribution.passage_ids == ("p1", "p2")
    assert trace.valid.support_contribution_ids == ("support-set",)
    assert trace.decision.verdict == "supported"
    assert contribution.model_dump(mode="json")["passage_ids"] == ["p1", "p2"]


def test_valid_passage_set_without_score_method_abstains() -> None:
    contribution = _contribution(
        "unscored-set",
        passage_ids=("p1", "p2"),
        origin="semantic_operator",
        score=None,
    )
    decision = evaluate_evidence(_inputs(contribution, admitted=("p1", "p2"))).decision
    assert decision.reason_code == "contribution_score_unmeasured"
    assert decision.basis_contribution_ids == ("unscored-set",)


def test_equal_best_scores_retain_all_basis_ids_in_stable_order() -> None:
    trace = evaluate_evidence(
        _inputs(
            _contribution("z-last", passage_ids=("p1",)),
            _contribution("a-first", passage_ids=("p2",)),
            admitted=("p1", "p2"),
        )
    )
    assert trace.raw.contribution_ids == ("a-first", "z-last")
    assert trace.decision.basis_contribution_ids == ("a-first", "z-last")


@pytest.mark.parametrize(
    "bad_contribution",
    [
        lambda: _contribution("empty-set", passage_ids=()),
        lambda: _contribution("duplicate-set", passage_ids=("p1", "p1")),
        lambda: _contribution("bad-score", score=1.01),
        lambda: EvidenceContribution(
            contribution_id="partial-score-receipt",
            channel="support",
            passage_ids=("p1", "p2"),
            score=0.9,
            score_method=None,
            score_receipt_sha256=_MODEL_RECEIPT,
            origin="semantic_operator",
            eligibility=_contribution("template").eligibility,
            validity=_contribution("template").validity,
        ),
    ],
)
def test_invalid_contribution_receipts_are_rejected(
    bad_contribution: Callable[[], EvidenceContribution],
) -> None:
    with pytest.raises(ValidationError):
        bad_contribution()


def test_input_rejects_incoherent_direct_measurement_receipts() -> None:
    with pytest.raises(ValidationError, match="must be admitted"):
        _inputs(_contribution("missing", passage_ids=("p2",)))
    with pytest.raises(ValidationError, match="below the signal floor"):
        _inputs(_contribution("below", score=0.19))
    duplicate = _contribution("duplicate")
    with pytest.raises(ValidationError, match="must be unique"):
        _inputs(duplicate, duplicate)
    above_floor_without_contribution = (
        ChannelMeasurement(
            passage_id="p1",
            support_score=0.90,
            refutation_score=0.01,
            evidence_path="fixture channel receipt",
            receipt_sha256=_MODEL_RECEIPT,
        ),
    )
    with pytest.raises(ValidationError, match="exactly cover"):
        _inputs(measurements=above_floor_without_contribution)
