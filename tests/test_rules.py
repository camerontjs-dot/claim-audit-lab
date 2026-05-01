"""Tests for deterministic rule checks and support assessment."""

from __future__ import annotations

from datetime import date as Date

from claim_audit_lab.models import (
    AuditConfig,
    Claim,
    ClaimAssessment,
    EvidenceBundle,
    EvidenceCandidate,
    EvidenceExcerpt,
    EvidenceSource,
)
from claim_audit_lab.rules import assess_claim_support


def _bundle(
    evidence_text: str,
    *,
    source_id: str = "source-001",
    excerpt_id: str = "excerpt-001",
    reliability: str = "high",
    source_date: Date | None = Date(2026, 1, 1),
    url: str | None = "https://example.com/source",
    notes: str | None = None,
) -> EvidenceBundle:
    return EvidenceBundle(
        sources=[
            EvidenceSource(
                id=source_id,
                title="Fictional source",
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
    source_url: str | None = "https://example.com/source",
) -> EvidenceCandidate:
    return EvidenceCandidate(
        source_id=source_id,
        excerpt_id=excerpt_id,
        score=score,
        source_reliability=reliability,
        source_date=source_date,
        source_url=source_url,
    )


def _claim(text: str, claim_type: str, claim_id: str = "claim-001") -> Claim:
    return Claim(id=claim_id, text=text, claim_type=claim_type)


def _codes(assessment: ClaimAssessment) -> set[str]:
    return {flag.code for flag in assessment.rule_flags}


def test_numeric_direct_support_is_supported() -> None:
    """A numeric claim with all claim numbers in evidence is supported."""
    claim = _claim("The test set included 52 workflow outputs.", "numeric")
    assessment = assess_claim_support(
        claim,
        _bundle("The test set included 52 workflow outputs."),
        [_candidate(score=1.0)],
    )

    assert assessment.support_label == "supported"
    assert assessment.risk_label == "low"
    assert assessment.rule_flags == []


def test_numeric_mismatch_is_unsupported_and_high_risk() -> None:
    """Related evidence with different numbers gets a numeric mismatch flag."""
    claim = _claim("The test set included 99 workflow outputs.", "numeric")
    assessment = assess_claim_support(
        claim,
        _bundle("The test set included 52 workflow outputs."),
        [_candidate(score=0.69)],
    )

    assert assessment.support_label == "unsupported"
    assert assessment.risk_label == "high"
    assert _codes(assessment) == {"numeric_mismatch"}


def test_causal_overreach_is_partially_supported() -> None:
    """A numeric change can be supported while causal framing remains limited."""
    claim = _claim(
        "Unsupported claims fell from 18 outputs to 11 outputs after the checklist was added.",
        "causal",
    )
    assessment = assess_claim_support(
        claim,
        _bundle("The intervention reduced unsupported claims in the test set from 18 to 11."),
        [_candidate(score=0.82)],
    )

    assert assessment.support_label == "partially_supported"
    assert assessment.risk_label == "medium"
    assert _codes(assessment) == {"causal_overreach"}


def test_comparative_claim_without_comparison_evidence_is_flagged() -> None:
    """Comparative claims need evidence that carries an actual comparison."""
    claim = _claim("The review screen is faster than a citation pass.", "comparative")
    assessment = assess_claim_support(
        claim,
        _bundle("The review screen completed a citation pass in 9 minutes."),
        [_candidate(score=0.55)],
    )

    assert assessment.support_label == "partially_supported"
    assert assessment.risk_label == "medium"
    assert _codes(assessment) == {"comparison_missing"}


def test_credential_claim_without_source_needs_source() -> None:
    """Credential claims need source support."""
    claim = _claim("The reviewer is a licensed sterile manufacturing specialist.", "credential")
    assessment = assess_claim_support(
        claim,
        _bundle("The reviewer works on audit notes."),
        [],
    )

    assert assessment.support_label == "needs_source"
    assert _codes(assessment) == {"credential_missing_source"}


def test_public_link_claim_without_source_url_needs_source() -> None:
    """Public-link claims need source URL metadata."""
    claim = _claim("The portfolio is published on GitHub.", "capability")
    assessment = assess_claim_support(
        claim,
        _bundle("The portfolio is published on GitHub.", url=None),
        [_candidate(source_url=None)],
    )

    assert assessment.support_label == "needs_source"
    assert _codes(assessment) == {"public_link_missing_source"}


def test_overconfident_wording_is_overstated() -> None:
    """Overstrong wording is flagged when evidence only supports a narrower claim."""
    claim = _claim("The tool clearly eliminates unsupported claims.", "scope")
    assessment = assess_claim_support(
        claim,
        _bundle("The tool reduced unsupported claims."),
        [_candidate(score=0.45)],
    )

    assert assessment.support_label == "overstated"
    assert assessment.risk_label == "high"
    assert "overconfident_wording" in _codes(assessment)


def test_low_reliability_only_support_lowers_assessment() -> None:
    """Low-reliability-only support stays visible as a limitation."""
    claim = _claim("The tool can generate audit summaries.", "capability")
    assessment = assess_claim_support(
        claim,
        _bundle(
            "The tool generated audit summaries.",
            reliability="low",
            url="https://example.com/low",
        ),
        [
            _candidate(
                score=0.8,
                reliability="low",
                source_url="https://example.com/low",
            )
        ],
    )

    assert assessment.support_label == "partially_supported"
    assert assessment.risk_label == "medium"
    assert _codes(assessment) == {"low_reliability_only"}


def test_stale_source_flag_is_opt_in_with_reference_date() -> None:
    """Freshness checks run only when a deterministic reference date is supplied."""
    claim = _claim("The tool can generate audit summaries.", "capability")
    bundle = _bundle(
        "The tool generated audit summaries.",
        source_date=Date(2024, 1, 1),
    )
    candidate = _candidate(score=0.8, source_date=Date(2024, 1, 1))

    assessment = assess_claim_support(
        claim,
        bundle,
        [candidate],
        AuditConfig(reference_date=Date(2026, 1, 2), freshness_days=365),
    )

    assert assessment.support_label == "partially_supported"
    assert _codes(assessment) == {"stale_source"}


def test_default_config_does_not_apply_stale_source_flag() -> None:
    """A dated source is not stale unless reference_date is set."""
    claim = _claim("The tool can generate audit summaries.", "capability")
    assessment = assess_claim_support(
        claim,
        _bundle("The tool generated audit summaries.", source_date=Date(2024, 1, 1)),
        [_candidate(score=0.8, source_date=Date(2024, 1, 1))],
    )

    assert assessment.support_label == "supported"
    assert "stale_source" not in _codes(assessment)


def test_date_or_deadline_claim_without_matching_evidence_needs_source() -> None:
    """Date and deadline claims need matching supplied evidence."""
    claim = _claim("The application deadline is approaching next month.", "prediction")
    assessment = assess_claim_support(
        claim,
        _bundle("The application page lists general eligibility."),
        [],
    )

    assert assessment.support_label == "needs_source"
    assert _codes(assessment) == {"date_missing_support"}


def test_future_certainty_and_overconfidence_cofire() -> None:
    """Future-certainty wording can produce multiple deterministic flags."""
    claim = _claim("The checklist will always prevent weak evidence.", "prediction")
    assessment = assess_claim_support(
        claim,
        _bundle("The checklist reduced weak-evidence issues in one review."),
        [],
    )

    assert assessment.support_label == "overstated"
    assert assessment.risk_label == "high"
    assert _codes(assessment) == {"future_certainty", "overconfident_wording"}


def test_scope_overreach_is_overstated() -> None:
    """Broad scope claims overreach when the supplied evidence names untested scope."""
    claim = _claim("The tool works across every regulated documentation workflow.", "scope")
    assessment = assess_claim_support(
        claim,
        _bundle(
            "The prototype was not tested on regulated documentation workflows.",
            notes="Known limitation for scope checks.",
        ),
        [_candidate(score=0.58)],
    )

    assert assessment.support_label == "overstated"
    assert assessment.risk_label == "high"
    assert _codes(assessment) == {"scope_overreach"}


def test_rule_flag_ids_are_deterministic() -> None:
    """Rule IDs derive from claim ID, rule code, and pinned trigger context."""
    claim = _claim("The checklist will always prevent weak evidence.", "prediction")
    bundle = _bundle("The checklist reduced weak-evidence issues in one review.")

    first = assess_claim_support(claim, bundle, [])
    second = assess_claim_support(claim, bundle, [])

    assert [flag.id for flag in first.rule_flags] == [flag.id for flag in second.rule_flags]
    assert all(flag.id.startswith("flag-") for flag in first.rule_flags)
