"""Contract C RC2-A2 decision-basis parity sweep.

Research-only. The candidate receipt is deliberately implemented in the test
surface so this experiment cannot alter CAL production verdict semantics.
"""

from __future__ import annotations

import copy
from dataclasses import replace
from datetime import date as Date
from typing import Any

import pytest

from claim_audit_lab.models import (
    AuditConfig,
    Claim,
    ClaimAssessment,
    EvidenceBundle,
    EvidenceCandidate,
    EvidenceExcerpt,
    EvidenceSource,
)
from claim_audit_lab.policy import CAL_RULES_V1_2_0, AuditPolicy
from claim_audit_lab.rules import assess_claim_support

_GENERIC_ASSESSMENTS = (
    "eligibility",
    "semantic_validity",
    "aperture_completeness",
    "temporal_applicability",
    "citation",
)
_NEEDS_SOURCE_CODES = {
    "credential_missing_source",
    "public_link_missing_source",
    "date_missing_support",
}
_OVERSTATED_CODES = {
    "future_certainty",
    "overconfident_wording",
    "scope_overreach",
}


def _claim(text: str, claim_type: str = "capability", *, claim_id: str = "claim-a2") -> Claim:
    return Claim(id=claim_id, text=text, claim_type=claim_type)


def _bundle(
    evidence_text: str,
    *,
    source_id: str = "source-001",
    excerpt_id: str = "excerpt-001",
    reliability: str = "high",
    source_date: Date | None = Date(2026, 1, 1),
    url: str | None = "https://example.test/source",
    notes: str | None = None,
) -> EvidenceBundle:
    return EvidenceBundle(
        sources=[
            EvidenceSource(
                id=source_id,
                title="RC2-A2 frozen-vector source",
                reliability=reliability,
                date=source_date,
                url=url,
                excerpts=[EvidenceExcerpt(id=excerpt_id, text=evidence_text, notes=notes)],
            )
        ]
    )


def _candidate(
    *,
    source_id: str = "source-001",
    excerpt_id: str = "excerpt-001",
    score: float = 0.8,
    reliability: str = "high",
    source_date: Date | None = Date(2026, 1, 1),
    source_url: str | None = "https://example.test/source",
) -> EvidenceCandidate:
    return EvidenceCandidate(
        source_id=source_id,
        excerpt_id=excerpt_id,
        score=score,
        source_reliability=reliability,
        source_date=source_date,
        source_url=source_url,
    )


def _evidence_id(candidate: EvidenceCandidate) -> str:
    return f"{candidate.source_id}:{candidate.excerpt_id}"


def _argmax_basis(candidates: list[EvidenceCandidate]) -> dict[str, Any]:
    if not candidates:
        return {"max_score": 0.0, "co_maximal_evidence_ids": []}
    maximum = max(candidate.score for candidate in candidates)
    return {
        "max_score": maximum,
        "co_maximal_evidence_ids": sorted(
            _evidence_id(candidate) for candidate in candidates if candidate.score == maximum
        ),
    }


def _policy_receipt(policy: AuditPolicy) -> dict[str, Any]:
    """Only behaviorally relevant support-label policy state, not a name alone."""
    return {
        "config_id": policy.config_id,
        "partial_support": policy.partial_support,
        "sourced_support": policy.sourced_support,
        "counterevidence_weight": policy.counterevidence_weight,
        "overstated_detection": policy.overstated_detection,
        "needs_source_detection": policy.needs_source_detection,
    }


def _classify_branch(
    claim: Claim,
    evidence_bundle: EvidenceBundle,
    assessment: ClaimAssessment,
    policy: AuditPolicy,
) -> tuple[str, set[str]]:
    """Classify the production control-flow branch from legitimate boundary state."""
    if claim.claim_type == "unclassified":
        return "unclassified", set()
    if not evidence_bundle.sources:
        return "no_sources", set()

    codes = {flag.code for flag in assessment.rule_flags}
    needs_source = _NEEDS_SOURCE_CODES & codes
    if policy.needs_source_detection and needs_source:
        return "needs_source_rule", needs_source
    if (
        policy.needs_source_detection
        and "comparison_missing" in codes
        and not assessment.candidate_evidence
    ):
        return "needs_source_comparison", {"comparison_missing"}

    overstated = _OVERSTATED_CODES & codes
    if policy.overstated_detection and overstated:
        return "overstated_rule", overstated
    if assessment.support_signal < policy.partial_support:
        return "below_partial_threshold", set()
    if assessment.support_signal < policy.sourced_support:
        return "below_sourced_threshold", set()
    if assessment.counterevidence or codes:
        # At this point any emitted rule code is independently sufficient for the
        # production `codes` truthiness predicate. Preserve all as co-sufficient
        # branch triggers rather than inventing one unique cause.
        return "post_sourced_residual_downgrade", codes
    return "clean_sourced_support", set()


def _materialize_receipt(
    claim: Claim,
    evidence_bundle: EvidenceBundle,
    assessment: ClaimAssessment,
    policy: AuditPolicy,
) -> dict[str, Any]:
    branch, deciding_codes = _classify_branch(claim, evidence_bundle, assessment, policy)
    deciding_rules = [
        {"rule_id": flag.id, "code": flag.code}
        for flag in assessment.rule_flags
        if flag.code in deciding_codes
    ]
    residual_rules = [
        {"rule_id": flag.id, "code": flag.code}
        for flag in assessment.rule_flags
        if flag.code not in deciding_codes
    ]
    signal_role = (
        "computed_nondeciding"
        if branch in {"unclassified", "no_sources", "needs_source_rule", "needs_source_comparison", "overstated_rule"}
        else "branch_input"
    )
    return {
        "receipt_profile": "rc2-a2-research-basis-receipt",
        "claim_type": claim.claim_type,
        "source_present": bool(evidence_bundle.sources),
        "support_candidate_count": len(assessment.candidate_evidence),
        "counterevidence_count": len(assessment.counterevidence),
        "policy": _policy_receipt(policy),
        "signal_basis": {
            "role": signal_role,
            "support": _argmax_basis(assessment.candidate_evidence),
            "counterevidence": _argmax_basis(assessment.counterevidence),
            "reported_signal": assessment.support_signal,
        },
        "rules": {
            "deciding": sorted(deciding_rules, key=lambda item: (item["code"], item["rule_id"])),
            "residual": sorted(residual_rules, key=lambda item: (item["code"], item["rule_id"])),
        },
        "assessment_families": {name: "not_performed" for name in _GENERIC_ASSESSMENTS},
        "branch": branch,
        "reported_verdict": assessment.support_label,
    }


def _require(receipt: dict[str, Any], key: str) -> Any:
    if key not in receipt:
        raise ValueError(f"missing receipt field: {key}")
    return receipt[key]


def _replay_receipt(receipt: dict[str, Any]) -> tuple[str, str]:
    """Replay without CAL implementation access or research-only semantic state."""
    claim_type = _require(receipt, "claim_type")
    source_present = _require(receipt, "source_present")
    support_candidate_count = _require(receipt, "support_candidate_count")
    counterevidence_count = _require(receipt, "counterevidence_count")
    policy = _require(receipt, "policy")
    signal_basis = _require(receipt, "signal_basis")
    rules = _require(receipt, "rules")

    required_policy = {
        "partial_support",
        "sourced_support",
        "counterevidence_weight",
        "overstated_detection",
        "needs_source_detection",
    }
    missing_policy = required_policy - set(policy)
    if missing_policy:
        raise ValueError(f"missing policy fields: {sorted(missing_policy)}")

    support = _require(signal_basis, "support")
    counter = _require(signal_basis, "counterevidence")
    if "max_score" not in support or "max_score" not in counter:
        raise ValueError("missing signal maximum")
    signal = round(
        min(
            max(
                float(support["max_score"])
                - (float(policy["counterevidence_weight"]) * float(counter["max_score"])),
                0.0,
            ),
            1.0,
        ),
        4,
    )
    if signal != _require(signal_basis, "reported_signal"):
        raise ValueError("signal basis does not reproduce reported signal")

    deciding = rules.get("deciding")
    residual = rules.get("residual")
    if deciding is None or residual is None:
        raise ValueError("missing rule partition")
    all_codes = {item["code"] for item in deciding + residual}

    if claim_type == "unclassified":
        return "unclassified", "not_checkable"
    if not source_present:
        verdict = "needs_source" if policy["needs_source_detection"] else "unsupported"
        return "no_sources", verdict

    needs_source = _NEEDS_SOURCE_CODES & all_codes
    if policy["needs_source_detection"] and needs_source:
        return "needs_source_rule", "needs_source"
    if (
        policy["needs_source_detection"]
        and "comparison_missing" in all_codes
        and support_candidate_count == 0
    ):
        return "needs_source_comparison", "needs_source"
    if policy["overstated_detection"] and (_OVERSTATED_CODES & all_codes):
        return "overstated_rule", "overstated"
    if signal < policy["partial_support"]:
        return "below_partial_threshold", "unsupported"
    if signal < policy["sourced_support"]:
        return "below_sourced_threshold", "partially_supported"
    if counterevidence_count or all_codes:
        return "post_sourced_residual_downgrade", "partially_supported"
    return "clean_sourced_support", "supported"


def _run(
    claim: Claim,
    bundle: EvidenceBundle,
    candidates: list[EvidenceCandidate],
    *,
    config: AuditConfig | None = None,
    counterevidence: list[EvidenceCandidate] | None = None,
    policy: AuditPolicy = CAL_RULES_V1_2_0,
) -> tuple[ClaimAssessment, dict[str, Any]]:
    assessment = assess_claim_support(
        claim,
        bundle,
        candidates,
        config,
        counterevidence=counterevidence,
        policy=policy,
    )
    return assessment, _materialize_receipt(claim, bundle, assessment, policy)


def _frozen_vectors() -> list[tuple[str, ClaimAssessment, dict[str, Any], str]]:
    vectors: list[tuple[str, ClaimAssessment, dict[str, Any], str]] = []

    def add(
        name: str,
        claim: Claim,
        bundle: EvidenceBundle,
        candidates: list[EvidenceCandidate],
        expected_branch: str,
        *,
        config: AuditConfig | None = None,
        counterevidence: list[EvidenceCandidate] | None = None,
        policy: AuditPolicy = CAL_RULES_V1_2_0,
    ) -> None:
        assessment, receipt = _run(
            claim,
            bundle,
            candidates,
            config=config,
            counterevidence=counterevidence,
            policy=policy,
        )
        vectors.append((name, assessment, receipt, expected_branch))

    add(
        "numeric-direct-support",
        _claim("The test set included 52 workflow outputs.", "numeric"),
        _bundle("The test set included 52 workflow outputs."),
        [_candidate(score=1.0)],
        "clean_sourced_support",
    )
    add(
        "unclassified",
        _claim("The report describes the pilot.", "unclassified"),
        EvidenceBundle(),
        [],
        "unclassified",
    )
    add(
        "classified-no-sources",
        _claim("The tool can generate audit summaries."),
        EvidenceBundle(),
        [],
        "no_sources",
    )
    add(
        "numeric-mismatch",
        _claim("The test set included 99 workflow outputs.", "numeric"),
        _bundle("The test set included 52 workflow outputs."),
        [_candidate(score=0.69)],
        "below_sourced_threshold",
    )
    for score, branch in (
        (0.40, "below_partial_threshold"),
        (0.5499, "below_partial_threshold"),
        (0.55, "below_sourced_threshold"),
        (0.7999, "below_sourced_threshold"),
        (0.80, "clean_sourced_support"),
    ):
        add(
            f"threshold-{score}",
            _claim("The tool can generate audit summaries."),
            _bundle("The tool can generate audit summaries."),
            [_candidate(score=score)],
            branch,
        )
    add(
        "counterevidence-scalar",
        _claim("The tool can generate audit summaries."),
        _bundle("The tool can generate audit summaries."),
        [_candidate(score=1.0)],
        "below_sourced_threshold",
        counterevidence=[_candidate(score=1.0)],
    )
    add(
        "absolute-wording-direct",
        _claim("The tool guarantees audit summaries.", "prediction"),
        _bundle("The tool guarantees audit summaries."),
        [_candidate(score=0.9)],
        "clean_sourced_support",
    )
    add(
        "absolute-wording-with-counterevidence",
        _claim("The tool guarantees audit summaries.", "prediction"),
        _bundle("The tool guarantees audit summaries."),
        [_candidate(score=1.0)],
        "overstated_rule",
        counterevidence=[_candidate(score=0.5)],
    )
    switched = replace(
        CAL_RULES_V1_2_0,
        overstated_detection=False,
        needs_source_detection=False,
    )
    add(
        "policy-switches-off",
        _claim("The reviewer guarantees licensed support.", "credential"),
        _bundle("The reviewer maintains audit notes."),
        [],
        "below_partial_threshold",
        policy=switched,
    )
    add(
        "causal-overreach",
        _claim(
            "Unsupported claims fell from 18 outputs to 11 outputs after the checklist was added.",
            "causal",
        ),
        _bundle("The intervention reduced unsupported claims in the test set from 18 to 11."),
        [_candidate(score=0.82)],
        "post_sourced_residual_downgrade",
    )
    add(
        "comparison-missing-with-candidate",
        _claim("The review screen is faster than a citation pass.", "comparative"),
        _bundle("The review screen completed a citation pass in 9 minutes."),
        [_candidate(score=0.55)],
        "below_sourced_threshold",
    )
    add(
        "credential-missing-source",
        _claim("The reviewer is a licensed sterile manufacturing specialist.", "credential"),
        _bundle("The reviewer works on audit notes."),
        [],
        "needs_source_rule",
    )
    add(
        "public-link-missing-source",
        _claim("The portfolio is published on GitHub."),
        _bundle("The portfolio is published on GitHub.", url=None),
        [_candidate(source_url=None)],
        "needs_source_rule",
    )
    add(
        "overconfident-wording",
        _claim("The tool clearly eliminates unsupported claims.", "scope"),
        _bundle("The tool reduced unsupported claims."),
        [_candidate(score=0.45)],
        "overstated_rule",
    )
    add(
        "low-reliability-only",
        _claim("The tool can generate audit summaries."),
        _bundle("The tool generated audit summaries.", reliability="low"),
        [_candidate(score=0.8, reliability="low")],
        "post_sourced_residual_downgrade",
    )
    old = Date(2024, 1, 1)
    add(
        "stale-source-opt-in",
        _claim("The tool can generate audit summaries."),
        _bundle("The tool generated audit summaries.", source_date=old),
        [_candidate(score=0.8, source_date=old)],
        "post_sourced_residual_downgrade",
        config=AuditConfig(reference_date=Date(2026, 1, 2), freshness_days=365),
    )
    add(
        "stale-source-default-invariance",
        _claim("The tool can generate audit summaries."),
        _bundle("The tool generated audit summaries.", source_date=old),
        [_candidate(score=0.8, source_date=old)],
        "clean_sourced_support",
    )
    add(
        "date-missing-support",
        _claim("The application deadline is approaching next month.", "prediction"),
        _bundle("The application page lists general eligibility."),
        [],
        "needs_source_rule",
    )
    add(
        "future-certainty",
        _claim("The checklist will always prevent weak evidence.", "prediction"),
        _bundle("The checklist reduced weak-evidence issues in one review."),
        [],
        "overstated_rule",
    )
    add(
        "scope-overreach",
        _claim("The tool works across every regulated documentation workflow.", "scope"),
        _bundle(
            "The prototype was not tested on regulated documentation workflows.",
            notes="Known limitation for scope checks.",
        ),
        [_candidate(score=0.58)],
        "overstated_rule",
    )
    return vectors


@pytest.mark.parametrize(
    ("name", "assessment", "receipt", "expected_branch"),
    _frozen_vectors(),
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_frozen_v02_vectors_replay_from_compact_basis_receipt(
    name: str,
    assessment: ClaimAssessment,
    receipt: dict[str, Any],
    expected_branch: str,
) -> None:
    del name
    replayed_branch, replayed_verdict = _replay_receipt(receipt)
    assert receipt["branch"] == replayed_branch == expected_branch
    assert receipt["reported_verdict"] == replayed_verdict == assessment.support_label
    assert receipt["assessment_families"] == {
        name: "not_performed" for name in _GENERIC_ASSESSMENTS
    }


def test_threshold_branch_keeps_numeric_mismatch_residual_to_headline() -> None:
    claim = _claim("The test set included 99 workflow outputs.", "numeric")
    assessment, receipt = _run(
        claim,
        _bundle("The test set included 52 workflow outputs."),
        [_candidate(score=0.69)],
    )
    assert assessment.support_label == "partially_supported"
    assert receipt["branch"] == "below_sourced_threshold"
    assert receipt["rules"]["deciding"] == []
    assert [item["code"] for item in receipt["rules"]["residual"]] == ["numeric_mismatch"]


def test_comparison_flag_is_residual_when_score_threshold_already_selects_partial() -> None:
    assessment, receipt = _run(
        _claim("The review screen is faster than a citation pass.", "comparative"),
        _bundle("The review screen completed a citation pass in 9 minutes."),
        [_candidate(score=0.55)],
    )
    assert assessment.support_label == "partially_supported"
    assert receipt["branch"] == "below_sourced_threshold"
    assert receipt["rules"]["deciding"] == []
    assert [item["code"] for item in receipt["rules"]["residual"]] == ["comparison_missing"]


@pytest.mark.parametrize("limiter", ["low_reliability", "stale_source"])
def test_high_score_limiting_rule_is_deciding_only_when_it_changes_sourced_branch(
    limiter: str,
) -> None:
    old = Date(2024, 1, 1)
    reliability = "low" if limiter == "low_reliability" else "high"
    source_date = old if limiter == "stale_source" else Date(2026, 1, 1)
    config = (
        AuditConfig(reference_date=Date(2026, 1, 2), freshness_days=365)
        if limiter == "stale_source"
        else None
    )
    assessment, receipt = _run(
        _claim("The tool can generate audit summaries."),
        _bundle(
            "The tool generated audit summaries.",
            reliability=reliability,
            source_date=source_date,
        ),
        [_candidate(score=0.8, reliability=reliability, source_date=source_date)],
        config=config,
    )
    assert assessment.support_label == "partially_supported"
    assert receipt["branch"] == "post_sourced_residual_downgrade"
    assert len(receipt["rules"]["deciding"]) == 1
    assert receipt["rules"]["residual"] == []


def test_counterevidence_maximum_not_all_counterevidence_is_scalar_basis() -> None:
    bundle = EvidenceBundle(
        sources=[
            EvidenceSource(
                id="source-001",
                title="support",
                reliability="high",
                date=Date(2026, 1, 1),
                url="https://example.test/support",
                excerpts=[EvidenceExcerpt(id="support", text="The tool can generate audit summaries.")],
            ),
            EvidenceSource(
                id="counter-a",
                title="counter A",
                reliability="high",
                date=Date(2026, 1, 1),
                url="https://example.test/a",
                excerpts=[EvidenceExcerpt(id="a", text="counter")],
            ),
            EvidenceSource(
                id="counter-b",
                title="counter B",
                reliability="high",
                date=Date(2026, 1, 1),
                url="https://example.test/b",
                excerpts=[EvidenceExcerpt(id="b", text="counter")],
            ),
        ]
    )
    support = [_candidate(excerpt_id="support", score=1.0)]
    counters = [
        _candidate(source_id="counter-a", excerpt_id="a", score=0.7),
        _candidate(source_id="counter-b", excerpt_id="b", score=0.2),
    ]
    assessment, receipt = _run(
        _claim("The tool can generate audit summaries."),
        bundle,
        support,
        counterevidence=counters,
    )
    assert assessment.support_signal == 0.79
    assert receipt["signal_basis"]["counterevidence"] == {
        "max_score": 0.7,
        "co_maximal_evidence_ids": ["counter-a:a"],
    }
    assert "counter-b:b" not in receipt["signal_basis"]["counterevidence"][
        "co_maximal_evidence_ids"
    ]


def test_tied_maxima_are_preserved_as_non_unique_co_maximal_basis() -> None:
    bundle = EvidenceBundle(
        sources=[
            EvidenceSource(
                id="source-a",
                title="A",
                reliability="high",
                date=Date(2026, 1, 1),
                url="https://example.test/a",
                excerpts=[EvidenceExcerpt(id="a", text="The tool can generate audit summaries.")],
            ),
            EvidenceSource(
                id="source-b",
                title="B",
                reliability="high",
                date=Date(2026, 1, 1),
                url="https://example.test/b",
                excerpts=[EvidenceExcerpt(id="b", text="The tool can generate audit summaries.")],
            ),
            EvidenceSource(
                id="source-c",
                title="C",
                reliability="high",
                date=Date(2026, 1, 1),
                url="https://example.test/c",
                excerpts=[EvidenceExcerpt(id="c", text="The tool can generate audit summaries.")],
            ),
        ]
    )
    candidates = [
        _candidate(source_id="source-a", excerpt_id="a", score=0.8),
        _candidate(source_id="source-b", excerpt_id="b", score=0.8),
        _candidate(source_id="source-c", excerpt_id="c", score=0.7),
    ]
    assessment, receipt = _run(
        _claim("The tool can generate audit summaries."),
        bundle,
        candidates,
    )
    assert assessment.support_label == "supported"
    assert receipt["signal_basis"]["support"] == {
        "max_score": 0.8,
        "co_maximal_evidence_ids": ["source-a:a", "source-b:b"],
    }
    assert "source-c:c" not in receipt["signal_basis"]["support"][
        "co_maximal_evidence_ids"
    ]


def test_config_id_alone_cannot_reproduce_behaviorally_relevant_policy_switches() -> None:
    switched = replace(
        CAL_RULES_V1_2_0,
        overstated_detection=False,
        needs_source_detection=False,
    )
    claim = _claim("The reviewer guarantees licensed support.", "credential")
    bundle = _bundle("The reviewer maintains audit notes.")
    baseline = assess_claim_support(claim, bundle, [], policy=CAL_RULES_V1_2_0)
    mutated = assess_claim_support(claim, bundle, [], policy=switched)

    assert CAL_RULES_V1_2_0.config_id == switched.config_id == "cal-rules-v1.2.0"
    assert baseline.support_label == "needs_source"
    assert mutated.support_label == "unsupported"

    _, receipt = _run(claim, bundle, [], policy=switched)
    replayed_branch, replayed_verdict = _replay_receipt(receipt)
    assert replayed_branch == "below_partial_threshold"
    assert replayed_verdict == "unsupported"
    assert receipt["policy"]["overstated_detection"] is False
    assert receipt["policy"]["needs_source_detection"] is False


def test_counterevidence_can_be_upstream_of_a_deciding_rule_even_when_its_own_flag_is_residual() -> None:
    claim = _claim("The tool guarantees audit summaries.", "prediction")
    bundle = _bundle("The tool guarantees audit summaries.")
    with_counter, receipt = _run(
        claim,
        bundle,
        [_candidate(score=1.0)],
        counterevidence=[_candidate(score=0.5)],
    )
    without_counter = assess_claim_support(claim, bundle, [_candidate(score=1.0)])

    assert with_counter.support_label == "overstated"
    assert without_counter.support_label == "supported"
    assert {item["code"] for item in receipt["rules"]["deciding"]} == {
        "future_certainty",
        "overconfident_wording",
    }
    assert {item["code"] for item in receipt["rules"]["residual"]} == {
        "counterevidence_present"
    }
    # This is a deliberate semantic warning for the result record: terminal
    # branch attribution alone does not encode the counterevidence -> rule
    # dependency that made the deciding rule fire.


def test_missing_required_receipt_state_fails_replay_closed() -> None:
    _, receipt = _run(
        _claim("The tool can generate audit summaries."),
        _bundle("The tool can generate audit summaries."),
        [_candidate(score=0.8)],
    )
    for field in ("policy", "signal_basis", "rules", "source_present"):
        mutated = copy.deepcopy(receipt)
        del mutated[field]
        with pytest.raises(ValueError):
            _replay_receipt(mutated)


def test_no_production_model_is_extended_by_the_research_receipt() -> None:
    assert "decision_basis" not in ClaimAssessment.model_fields
    assert "assessment_families" not in ClaimAssessment.model_fields
