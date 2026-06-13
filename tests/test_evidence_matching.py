"""Tests for deterministic evidence matching."""

from __future__ import annotations

from pathlib import Path

from claim_audit_lab.claim_extraction import extract_claims
from claim_audit_lab.evidence_matching import match_claims_to_evidence, match_evidence
from claim_audit_lab.loader import load_draft, load_evidence_bundle
from claim_audit_lab.models import (
    AuditConfig,
    Claim,
    EvidenceBundle,
    EvidenceExcerpt,
    EvidenceSource,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = PROJECT_ROOT / "examples"


def _ai_research_claims() -> list[Claim]:
    draft = load_draft(EXAMPLES_ROOT / "drafts" / "ai-research-note.md")
    return extract_claims(draft)


def _product_claims() -> list[Claim]:
    draft = load_draft(EXAMPLES_ROOT / "drafts" / "product-readme-note.md")
    return extract_claims(draft)


def _claim_with_text(claims: list[Claim], text: str) -> Claim:
    for claim in claims:
        if claim.text == text:
            return claim
    raise AssertionError(f"Missing claim: {text}")


def test_numeric_match_links_workflow_count_to_matching_excerpt() -> None:
    """Matching numbers produce a high-scoring candidate evidence link."""
    claim = _claim_with_text(
        _ai_research_claims(),
        "The test set included 52 workflow outputs.",
    )
    bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "ai-research-evidence.yml")

    candidates = match_evidence(claim, bundle, AuditConfig(min_overlap_score=0.2))

    assert candidates[0].source_id == "source-001"
    assert candidates[0].excerpt_id == "excerpt-002"
    assert candidates[0].score >= 0.7
    assert candidates[0].score <= 1.0
    assert candidates[0].source_reliability == "medium"
    assert candidates[0].source_date is not None
    assert candidates[0].source_date.isoformat() == "2026-04-01"
    assert (
        candidates[0].source_url == "https://example.com/fictional-provenance-checklist-evaluation"
    )
    assert candidates[0].rationale is not None
    assert "matched numbers: 52" in candidates[0].rationale


def test_numeric_mismatch_does_not_receive_high_score() -> None:
    """Related evidence without the claim's number stays below high-score territory."""
    claim = Claim(
        id="claim-mismatch",
        text="The test set included 99 workflow outputs.",
        claim_type="numeric",
    )
    bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "ai-research-evidence.yml")

    candidates = match_evidence(claim, bundle, AuditConfig(min_overlap_score=0.2))

    assert candidates[0].source_id == "source-001"
    assert candidates[0].excerpt_id == "excerpt-002"
    assert 0.2 <= candidates[0].score < 0.7
    assert candidates[0].rationale is not None
    assert "claim numbers not found in excerpt: 99" in candidates[0].rationale


def test_reduction_numbers_link_to_reduction_excerpt() -> None:
    """The 18-to-11 reduction claim links to the matching reduction evidence."""
    claim = _claim_with_text(
        _ai_research_claims(),
        (
            "Unsupported claims fell from 18 outputs to 11 outputs after the provenance "
            "checklist was added."
        ),
    )
    bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "ai-research-evidence.yml")

    candidates = match_evidence(claim, bundle)

    assert candidates[0].source_id == "source-001"
    assert candidates[0].excerpt_id == "excerpt-001"
    assert candidates[0].score >= 0.7
    assert candidates[0].rationale is not None
    assert "matched numbers: 11, 18" in candidates[0].rationale


def test_product_capability_claim_links_to_capability_excerpt() -> None:
    """Product capability wording links to the narrow prototype capability evidence."""
    claim = _claim_with_text(
        _product_claims(),
        "Meridian Notes can generate traceable audit summaries from uploaded research notes.",
    )
    bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "product-readme-evidence.yml")

    candidates = match_evidence(claim, bundle, AuditConfig(min_overlap_score=0.2))

    assert candidates[0].source_id == "source-product-001"
    assert candidates[0].excerpt_id == "excerpt-product-001"
    assert candidates[0].score >= 0.2


def test_product_comparison_claim_links_to_timed_walkthrough_excerpt() -> None:
    """Comparative wording links to the timed walkthrough comparison evidence."""
    claim = _claim_with_text(
        _product_claims(),
        "The review screen is faster than a manual citation pass.",
    )
    bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "product-readme-evidence.yml")

    candidates = match_evidence(claim, bundle)

    assert candidates[0].source_id == "source-product-001"
    assert candidates[0].excerpt_id == "excerpt-product-002"
    assert candidates[0].score >= 0.2


def test_scope_limitation_claim_can_find_limitation_candidate() -> None:
    """Scope claims can link to limitation evidence without deciding final support."""
    claim = _claim_with_text(
        _product_claims(),
        "Meridian Notes works across every regulated documentation workflow.",
    )
    bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "product-readme-evidence.yml")

    candidates = match_evidence(claim, bundle)

    assert candidates[0].source_id == "source-product-002"
    assert candidates[0].excerpt_id == "excerpt-product-003"
    assert candidates[0].source_reliability == "high"


def test_prediction_limitation_claim_can_find_limitation_candidate() -> None:
    """Prediction claims can link to limitation evidence without assigning a label."""
    claim = _claim_with_text(
        _product_claims(),
        "Meridian Notes will always prevent teams from shipping unsupported release notes.",
    )
    bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "product-readme-evidence.yml")

    candidates = match_evidence(claim, bundle, AuditConfig(min_overlap_score=0.2))

    assert candidates[0].source_id == "source-product-002"
    assert candidates[0].excerpt_id == "excerpt-product-004"
    assert candidates[0].score >= 0.2


def test_multiple_candidates_are_sorted_and_capped_deterministically() -> None:
    """Equal-scoring candidates sort by source and excerpt IDs before capping."""
    claim = Claim(
        id="claim-sorted",
        text="The test set included 52 workflow outputs.",
        claim_type="numeric",
    )
    bundle = EvidenceBundle(
        sources=[
            EvidenceSource(
                id="source-b",
                title="Second source",
                excerpts=[
                    EvidenceExcerpt(
                        id="excerpt-b",
                        text="The test set included 52 workflow outputs.",
                    )
                ],
            ),
            EvidenceSource(
                id="source-a",
                title="First source",
                excerpts=[
                    EvidenceExcerpt(
                        id="excerpt-c",
                        text="The test set included 52 workflow outputs.",
                    ),
                    EvidenceExcerpt(
                        id="excerpt-a",
                        text="The test set included 52 workflow outputs.",
                    ),
                ],
            ),
        ]
    )

    candidates = match_evidence(
        claim,
        bundle,
        AuditConfig(max_candidate_evidence=2),
    )

    assert [(candidate.source_id, candidate.excerpt_id) for candidate in candidates] == [
        ("source-a", "excerpt-a"),
        ("source-a", "excerpt-c"),
    ]


def test_empty_evidence_bundle_returns_no_candidates() -> None:
    """Empty evidence bundles are valid and produce no candidate links."""
    claim = Claim(
        id="claim-empty",
        text="The test set included 52 workflow outputs.",
        claim_type="numeric",
    )

    assert match_evidence(claim, EvidenceBundle(sources=[])) == []


def test_candidate_scores_are_bounded_for_fixture_claims() -> None:
    """All generated candidates stay inside the model's score bounds."""
    bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "product-readme-evidence.yml")
    candidates = [
        candidate for claim in _product_claims() for candidate in match_evidence(claim, bundle)
    ]

    assert candidates
    assert all(0.0 <= candidate.score <= 1.0 for candidate in candidates)


def test_match_claims_to_evidence_returns_claim_id_mapping() -> None:
    """Batch matching returns a dictionary keyed by stable claim IDs."""
    claims = _ai_research_claims()
    bundle = load_evidence_bundle(EXAMPLES_ROOT / "evidence" / "ai-research-evidence.yml")

    matches = match_claims_to_evidence(claims, bundle)

    assert set(matches) == {claim.id for claim in claims}
    count_claim = _claim_with_text(claims, "The test set included 52 workflow outputs.")
    assert matches[count_claim.id][0].excerpt_id == "excerpt-002"
