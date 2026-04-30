"""Tests for conservative claim extraction."""

from __future__ import annotations

from pathlib import Path

import pytest

from claim_audit_lab.claim_extraction import extract_claims
from claim_audit_lab.loader import load_draft
from claim_audit_lab.models import ClaimType, DraftDocument

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = PROJECT_ROOT / "examples"


def _document(content: str, document_id: str = "draft-001") -> DraftDocument:
    return DraftDocument(id=document_id, content=content)


def test_extracts_expected_claims_from_ai_research_note() -> None:
    """The first fictional fixture extracts predictable claim candidates."""
    draft = load_draft(EXAMPLES_ROOT / "drafts" / "ai-research-note.md")

    claims = extract_claims(draft)

    expected_claim_types = {
        (
            "The intervention clearly eliminates unsupported claims in multi-step AI "
            "research workflows."
        ): "scope",
        "The test set included 52 workflow outputs.": "numeric",
        (
            "Unsupported claims fell from 18 outputs to 11 outputs after the provenance "
            "checklist was added."
        ): "causal",
        (
            "The checklist will always prevent researchers from relying on weak evidence."
        ): "prediction",
    }
    claim_types_by_text = {claim.text: claim.claim_type for claim in claims}
    assert claim_types_by_text == expected_claim_types
    assert {claim.location for claim in claims} == {
        "paragraph:1:sentence:1",
        "paragraph:2:sentence:1",
        "paragraph:2:sentence:2",
        "paragraph:3:sentence:1",
    }


def test_claim_ids_are_stable_and_not_order_dependent() -> None:
    """Stable IDs are generated from document ID and normalized claim text."""
    first_document = _document(
        "The test set included 52 workflow outputs. The tool can detect unsupported claims.",
        document_id="stable-demo",
    )
    second_document = _document(
        "The tool can detect unsupported claims. The test set included 52 workflow outputs.",
        document_id="stable-demo",
    )

    first_ids = {claim.text: claim.id for claim in extract_claims(first_document)}
    second_ids = {claim.text: claim.id for claim in extract_claims(second_document)}

    assert first_ids == second_ids
    assert all(claim_id.startswith("claim-") for claim_id in first_ids.values())


@pytest.mark.parametrize(
    "sentence,expected_type",
    [
        pytest.param("The test set included 52 workflow outputs.", "numeric", id="numeric"),
        pytest.param(
            "The checklist reduced unsupported claims after review.",
            "causal",
            id="causal",
        ),
        pytest.param(
            "The revised prompt is better than the baseline prompt.",
            "comparative",
            id="comparative",
        ),
        pytest.param(
            "The reviewer has 8 years of experience in sterile manufacturing.",
            "credential",
            id="credential",
        ),
        pytest.param(
            "The checklist will always catch weak evidence.",
            "prediction",
            id="prediction",
        ),
        pytest.param(
            "The tool can detect unsupported claims in drafts.",
            "capability",
            id="capability",
        ),
        pytest.param(
            "The process works across all multi-step research workflows.",
            "scope",
            id="scope",
        ),
        pytest.param(
            "The report is credible and important for audit review.",
            "interpretive",
            id="interpretive",
        ),
    ],
)
def test_classifies_each_claim_type(sentence: str, expected_type: ClaimType) -> None:
    """Direct fixtures exercise every constrained claim type."""
    claims = extract_claims(_document(sentence))

    assert [claim.claim_type for claim in claims] == [expected_type]


def test_skips_vague_questions_headings_and_short_fragments() -> None:
    """Non-claim content should not become audit targets."""
    content = """# Claim Audit Draft

Maybe this is helpful.

Can the tool detect unsupported claims?

Strong.

This section discusses things.

## Notes
"""

    assert extract_claims(_document(content)) == []


def test_duplicate_and_near_duplicate_claims_do_not_inflate_count() -> None:
    """Repeated claims collapse to the first canonical candidate."""
    content = (
        "The tool can detect unsupported claims. "
        "The tool can detect unsupported claims. "
        "The tool detects unsupported claims."
    )

    claims = extract_claims(_document(content))

    assert len(claims) == 1
    assert claims[0].text == "The tool can detect unsupported claims."
    assert claims[0].location == "paragraph:1:sentence:1"
