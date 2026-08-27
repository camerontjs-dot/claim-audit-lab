"""Rung 05: CAL-side Contract-B consumer seam experiments.

The tests characterize what crosses the verified C-B boundary versus what CAL
measures or judges downstream. Production paths remain unchanged.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Literal

import pytest

from claim_audit_lab.contracts.adapter import (
    adapt_bundle_to_pipeline,
    build_claim_evidence_scopes,
)
from claim_audit_lab.contracts.bundle_loader import BundleContents, load_bundle
from claim_audit_lab.contracts.cb_models import CBClaim
from claim_audit_lab.v1.config import load_default_audit_config
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
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.intake import bundle_to_requests
from claim_audit_lab.v1.models import AuditRequest, ExtractedFeatures
from claim_audit_lab.v1.pipeline import run_audit
from tests.v1.testing.stubs import StubEntailer, StubRetriever

_FIXTURE_BUNDLE = (
    Path(__file__).parents[1] / "fixtures" / "cb" / "evidence-bundle-minimal"
)
_RECEIPT = "sha256:" + "a" * 64
_POLICY_RECEIPT = "sha256:" + "b" * 64


class _StaticFeatures:
    """Freeze claim features so the seam tests vary no linguistic variable."""

    def extract(self, claim: str) -> ExtractedFeatures:
        del claim
        return ExtractedFeatures(sentence_type="declarative", claim_token_count=8)


def _loaded(tmp_path: Path) -> BundleContents:
    return load_bundle(_FIXTURE_BUNDLE, deviations_dir=tmp_path / "deviations")


def _move_nomination_lane(contents: BundleContents) -> BundleContents:
    raw = contents.claims[0].model_dump(mode="python")
    nominated = raw["evidence_passages"]
    raw["evidence_passages"] = []
    raw["counterevidence_passages"] = nominated
    return replace(contents, claims=[CBClaim.model_validate(raw)])


def _with_trust(contents: BundleContents, trust_level: str) -> BundleContents:
    source_id = next(iter(contents.source_profiles))
    profile = contents.source_profiles[source_id].model_copy(
        update={"trust_level": trust_level}
    )
    return replace(
        contents,
        source_profiles={**contents.source_profiles, source_id: profile},
    )


def _run_weak_refutation(request: AuditRequest):
    passage_id = request.passages[0].passage_id
    retriever = StubRetriever(scores={passage_id: 0.90})
    entailer = StubEntailer(
        responses={passage_id: ("contradict", 0.50, (0.0, 0.0, 0.0))}
    )
    rules = VerdictRules(rules_file_sha=request.audit_config.rules_file_sha)
    return run_audit(
        request,
        feature_extractor=_StaticFeatures(),
        retriever=retriever,
        entailer=entailer,
        aggregator=MaxEntailmentAggregator(),
        rules=rules,
    )


def test_h05_1_v1_passage_set_is_invariant_to_eb_nomination_lane(tmp_path: Path) -> None:
    contents = _loaded(tmp_path)
    swapped = _move_nomination_lane(contents)
    config = load_default_audit_config()

    original_request = bundle_to_requests(contents, config)[0]
    swapped_request = bundle_to_requests(swapped, config)[0]

    assert original_request.passages == swapped_request.passages
    assert original_request.claim_text == swapped_request.claim_text

    # Characterize the legacy seam separately: it does encode the EB lane into
    # support/counter search scopes. The v1 request deliberately does not.
    original_scope = build_claim_evidence_scopes(contents)[original_request.claim_id]
    swapped_scope = build_claim_evidence_scopes(swapped)[swapped_request.claim_id]
    assert original_scope.support_excerpt_ids == swapped_scope.counter_excerpt_ids
    assert original_scope.counter_excerpt_ids == swapped_scope.support_excerpt_ids


def test_h05_2_trust_tier_does_not_change_semantic_measurement(tmp_path: Path) -> None:
    contents = _loaded(tmp_path)
    config = load_default_audit_config()
    primary_request = bundle_to_requests(_with_trust(contents, "primary"), config)[0]
    secondary_request = bundle_to_requests(_with_trust(contents, "secondary"), config)[0]

    assert primary_request.passages[0].text == secondary_request.passages[0].text
    assert primary_request.passages[0].source_meta["trust_level"] == "primary"
    assert secondary_request.passages[0].source_meta["trust_level"] == "secondary"

    primary_trace = _run_weak_refutation(primary_request)
    secondary_trace = _run_weak_refutation(secondary_request)

    assert primary_trace.retrieval == secondary_trace.retrieval
    assert primary_trace.entailment == secondary_trace.entailment
    assert primary_trace.support_signal == secondary_trace.support_signal


def test_h05_3_current_p1_changes_verdict_only_at_cal_policy_layer(tmp_path: Path) -> None:
    contents = _loaded(tmp_path)
    config = load_default_audit_config()
    primary_trace = _run_weak_refutation(
        bundle_to_requests(_with_trust(contents, "primary"), config)[0]
    )
    secondary_trace = _run_weak_refutation(
        bundle_to_requests(_with_trust(contents, "secondary"), config)[0]
    )

    assert primary_trace.entailment == secondary_trace.entailment
    assert primary_trace.support_signal == secondary_trace.support_signal
    assert primary_trace.verdict.support_verdict == "unsupported"
    assert secondary_trace.verdict.support_verdict == "not_checkable"
    assert secondary_trace.verdict.support_verdict_reason == "no_entail_signal"
    assert "P1_eligibility_suppressed" in {
        fired.rule_id for fired in secondary_trace.rules_fired
    }
    assert "P1_eligibility_suppressed" not in {
        fired.rule_id for fired in primary_trace.rules_fired
    }


def test_h05_legacy_adapter_promotes_trust_tier_to_reliability(tmp_path: Path) -> None:
    contents = _loaded(tmp_path)
    _, primary_bundle, _ = adapt_bundle_to_pipeline(_with_trust(contents, "primary"))
    _, secondary_bundle, _ = adapt_bundle_to_pipeline(_with_trust(contents, "secondary"))

    assert primary_bundle.sources[0].reliability == "high"
    assert secondary_bundle.sources[0].reliability == "medium"


def _assessment_input(
    eligibility: Literal["eligible", "ineligible", "unknown"],
) -> EvidenceDecisionInput:
    passage_id = "secondary-source/pass-001"
    eligibility_receipt = EligibilityAssessment(
        status=eligibility,
        reason=f"explicit CAL eligibility assessment: {eligibility}",
        evidence_path="cal-assessment/eligibility",
        receipt_sha256=_RECEIPT,
    )
    validity = ValidityAssessment(
        status="valid",
        reason="the supplied passage directly addresses the proposition",
        evidence_path="cal-assessment/semantic-validity",
        receipt_sha256=_RECEIPT,
        operator="direct_proposition_relation",
    )
    contribution = EvidenceContribution(
        contribution_id="refutation:secondary-source/pass-001",
        channel="refutation",
        passage_ids=(passage_id,),
        score=0.90,
        score_method="direct_nli_probability",
        score_receipt_sha256=_RECEIPT,
        origin="direct_nli",
        eligibility=eligibility_receipt,
        validity=validity,
    )
    return EvidenceDecisionInput(
        claim_id="claim-001",
        scope_status="in_scope",
        stage_receipts=tuple(
            StageReceipt(
                stage=stage,
                evidence_path=f"cal-stage/{stage}",
                receipt_sha256=_RECEIPT,
            )
            for stage in CANONICAL_STAGE_ORDER
        ),
        admitted_passage_ids=(passage_id,),
        measurements=(
            ChannelMeasurement(
                passage_id=passage_id,
                support_score=0.01,
                refutation_score=0.90,
                evidence_path="cal-measurement/nli",
                receipt_sha256=_RECEIPT,
            ),
        ),
        apertures=(
            ChannelApertureAssessment(
                channel="support",
                status="complete",
                reason="constructed complete support aperture",
                evidence_path="cal-assessment/support-aperture",
                receipt_sha256=_RECEIPT,
            ),
            ChannelApertureAssessment(
                channel="refutation",
                status="complete",
                reason="constructed complete refutation aperture",
                evidence_path="cal-assessment/refutation-aperture",
                receipt_sha256=_RECEIPT,
            ),
        ),
        signal_floor=0.20,
        support_threshold=0.70,
        refutation_threshold=0.70,
        policy_id="rung05-explicit-eligibility-v1",
        policy_receipt_sha256=_POLICY_RECEIPT,
        contributions=(contribution,),
    )


@pytest.mark.parametrize(
    ("eligibility", "expected_disposition", "expected_verdict", "expected_reason"),
    [
        ("eligible", "decided", "contradicted", "refutation_above_threshold"),
        ("ineligible", "abstained", None, "no_eligible_contribution"),
        ("unknown", "abstained", None, "eligibility_unknown"),
    ],
)
def test_h05_4_shadow_requires_explicit_receipt_bound_eligibility(
    eligibility: Literal["eligible", "ineligible", "unknown"],
    expected_disposition: str,
    expected_verdict: str | None,
    expected_reason: str,
) -> None:
    trace = evaluate_evidence(_assessment_input(eligibility))

    assert trace.decision.disposition == expected_disposition
    assert trace.decision.verdict == expected_verdict
    assert trace.decision.reason_code == expected_reason
    assert trace.inputs.contributions[0].eligibility.status == eligibility
    assert trace.inputs.contributions[0].eligibility.receipt_sha256 == _RECEIPT


def test_h05_5_shadow_has_no_implicit_contract_trust_input() -> None:
    fields = set(EvidenceDecisionInput.model_fields)
    assert "trust_level" not in fields
    assert "source_reliability" not in fields
    assert "authority" not in fields

    # A source-looking passage ID does not change the outcome. Only the explicit
    # receipt-bound eligibility assessment does.
    trace = evaluate_evidence(_assessment_input("unknown"))
    assert trace.inputs.admitted_passage_ids == ("secondary-source/pass-001",)
    assert trace.decision.reason_code == "eligibility_unknown"
