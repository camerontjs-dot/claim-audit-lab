"""Tests for Claim Audit Lab data models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from claim_audit_lab.models import (
    AuditConfig,
    AuditReport,
    AuditSummary,
    Claim,
    ClaimAssessment,
    EvidenceBundle,
    EvidenceCandidate,
    EvidenceExcerpt,
    EvidenceSource,
    RuleFlag,
)

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "examples" / "evidence"


@pytest.fixture
def evidence_bundle_data() -> dict[str, Any]:
    """Load the first fictional evidence fixture."""
    fixture_path = FIXTURE_ROOT / "ai-research-evidence.yml"
    return yaml.safe_load(fixture_path.read_text(encoding="utf-8"))


def test_valid_evidence_fixture_loads(evidence_bundle_data: dict[str, Any]) -> None:
    """Valid evidence fixture loads into an EvidenceBundle."""
    bundle = EvidenceBundle.model_validate(evidence_bundle_data)

    assert len(bundle.sources) == 1
    assert bundle.sources[0].id == "source-001"
    assert bundle.sources[0].reliability == "medium"
    assert [excerpt.id for excerpt in bundle.sources[0].excerpts] == [
        "excerpt-001",
        "excerpt-002",
    ]


def test_unknown_fields_are_rejected() -> None:
    """Models reject fields outside the schema."""
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        EvidenceExcerpt(id="excerpt-001", text="Supported detail.", unexpected=True)


@pytest.mark.parametrize(
    "model_data",
    [
        pytest.param({"id": " ", "text": "Supported detail."}, id="blank_excerpt_id"),
        pytest.param({"id": "excerpt-001", "text": " "}, id="blank_excerpt_text"),
        pytest.param({"id": "source-001", "title": " "}, id="blank_source_title"),
    ],
)
def test_blank_required_text_fields_are_rejected(model_data: dict[str, str]) -> None:
    """Required IDs and text fields cannot be blank."""
    model = EvidenceSource if "title" in model_data else EvidenceExcerpt

    with pytest.raises(ValidationError):
        model.model_validate(model_data)


def test_invalid_reliability_label_is_rejected(evidence_bundle_data: dict[str, Any]) -> None:
    """Source reliability must be one of the constrained labels."""
    evidence_bundle_data["sources"][0]["reliability"] = "certain"

    with pytest.raises(ValidationError, match="Input should be"):
        EvidenceBundle.model_validate(evidence_bundle_data)


def test_duplicate_source_ids_fail(evidence_bundle_data: dict[str, Any]) -> None:
    """EvidenceBundle rejects duplicate source IDs."""
    duplicate_source = dict(evidence_bundle_data["sources"][0])
    duplicate_source["title"] = "Duplicate source"
    evidence_bundle_data["sources"].append(duplicate_source)

    with pytest.raises(ValidationError, match="Duplicate evidence source id"):
        EvidenceBundle.model_validate(evidence_bundle_data)


def test_duplicate_excerpt_ids_fail(evidence_bundle_data: dict[str, Any]) -> None:
    """EvidenceBundle rejects duplicate excerpt IDs across all sources."""
    second_source = dict(evidence_bundle_data["sources"][0])
    second_source["id"] = "source-002"
    second_source["title"] = "Second source"
    evidence_bundle_data["sources"].append(second_source)

    with pytest.raises(ValidationError, match="Duplicate evidence excerpt id"):
        EvidenceBundle.model_validate(evidence_bundle_data)


def test_empty_evidence_bundle_is_accepted() -> None:
    """An empty evidence bundle is valid for the model layer."""
    bundle = EvidenceBundle(sources=[])

    assert bundle.sources == []


@pytest.mark.parametrize(
    "field,value",
    [
        pytest.param("freshness_days", 0, id="zero_freshness_days"),
        pytest.param("min_overlap_score", -0.1, id="negative_overlap_score"),
        pytest.param("min_overlap_score", 1.1, id="over_one_overlap_score"),
        pytest.param("max_candidate_evidence", 0, id="zero_candidate_count"),
    ],
)
def test_audit_config_rejects_impossible_values(field: str, value: float | int) -> None:
    """AuditConfig rejects thresholds and counts outside useful bounds."""
    with pytest.raises(ValidationError):
        AuditConfig.model_validate({field: value})


@pytest.mark.parametrize(
    "score",
    [
        pytest.param(-0.1, id="negative_score"),
        pytest.param(1.1, id="over_one_score"),
    ],
)
def test_evidence_candidate_score_is_bounded(score: float) -> None:
    """Evidence candidate scores must stay between zero and one."""
    with pytest.raises(ValidationError):
        EvidenceCandidate(source_id="source-001", excerpt_id="excerpt-001", score=score)


def test_audit_report_serializes_to_json_shaped_dict() -> None:
    """AuditReport serializes to a JSON-shaped dictionary."""
    flag = RuleFlag(
        id="flag-001",
        claim_id="claim-001",
        code="overconfident_wording",
        message="The claim is stronger than the supplied evidence supports.",
        risk="medium",
    )
    assessment = ClaimAssessment(
        claim=Claim(
            id="claim-001",
            text="The checklist eliminates unsupported claims.",
            claim_type="causal",
        ),
        support_label="overstated",
        risk_label="medium",
        candidate_evidence=[
            EvidenceCandidate(
                source_id="source-001",
                excerpt_id="excerpt-001",
                score=0.82,
                rationale="Shares intervention and unsupported-claims terms.",
            )
        ],
        rule_flags=[flag],
        explanation="The evidence supports reduction, not elimination.",
        suggested_rewrite="The checklist reduced unsupported claims in the test set.",
        limitations=["The tool cannot verify the source itself."],
    )
    report = AuditReport(
        document_id="draft-001",
        summary=AuditSummary(total_claims=1, overstated_claims=1),
        claims=[assessment],
        rule_flags=[flag],
        limitations=["Audits supplied evidence only."],
    )

    data = report.model_dump(mode="json")

    assert data["document_id"] == "draft-001"
    assert data["summary"]["total_claims"] == 1
    assert data["claims"][0]["support_label"] == "overstated"
    assert data["claims"][0]["candidate_evidence"][0]["score"] == 0.82
