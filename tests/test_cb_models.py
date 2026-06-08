"""Model-only tests for locked C-B v1.0.0 bundle read models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from claim_audit_lab.contracts.cb_models import (
    CBAuditConfig,
    CBBundleManifest,
    CBClaim,
    CBPassage,
    CBSourceProfile,
    CBValidationSetRef,
)

FIXTURE_BUNDLE = Path(__file__).parent / "fixtures" / "cb" / "evidence-bundle-minimal"


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return raw


def test_cb_manifest_model_matches_locked_v1_bundle_shape() -> None:
    """bundle_manifest.yaml uses nested locked C-B blocks, not the old draft shape."""
    manifest = CBBundleManifest.model_validate(_load_yaml(FIXTURE_BUNDLE / "bundle_manifest.yaml"))

    assert manifest.schema_version == "1.0.0"
    assert manifest.source_run_id == "550e8400-e29b-41d4-a716-446655440000"
    assert manifest.evidence_builder.operator == "cameron"
    assert manifest.bundle.claims_included == 1
    assert manifest.bundle.claims_excluded == 1
    assert manifest.quality_gates.every_passage_links_to_source_profile is True
    assert manifest.reviewer_sign_off.required is False
    assert manifest.reviewer_sign_off.signed_by is None


def test_cb_claim_model_carries_scaffold_fields_embedded_passages_and_null_audit() -> None:
    """claims/{claim_id}.yaml is a self-contained audit unit at handoff."""
    claim = CBClaim.model_validate(_load_yaml(FIXTURE_BUNDLE / "claims" / "clm-001.yaml"))

    assert claim.schema_version == "1.0.0"
    assert claim.claim_type == "extracted_claim"
    assert claim.workflow_condition == "full_scaffold"
    assert claim.task_id == "pharma-reg-submission-task-03"
    assert claim.scaffold_support_status == "sourced"
    assert claim.scaffold_claim_strength == 0.86
    assert claim.scaffold_extraction_fidelity == 0.92
    assert claim.scaffold_counterevidence_found is False
    assert claim.scaffold_downgraded is False
    assert len(claim.evidence_passages) == 1
    assert claim.evidence_passages[0].source_trust_level == "primary"
    assert claim.counterevidence_passages == []
    assert all(value is None for value in claim.audit.model_dump(mode="json").values())


def test_cb_source_profile_passage_config_and_validation_ref_models_load_fixture() -> None:
    """The remaining C-B files validate as independent locked read models."""
    source_profile = CBSourceProfile.model_validate(
        _load_yaml(FIXTURE_BUNDLE / "evidence" / "src-001" / "source_profile.yaml")
    )
    passage = CBPassage.model_validate(
        _load_yaml(FIXTURE_BUNDLE / "evidence" / "src-001" / "passages" / "pass-001.yaml")
    )
    audit_config = CBAuditConfig.model_validate(_load_yaml(FIXTURE_BUNDLE / "audit_config.yaml"))
    validation_ref = CBValidationSetRef.model_validate(
        _load_yaml(FIXTURE_BUNDLE / "validation_set_ref.yaml")
    )

    assert source_profile.bibliographic.source_type == "regulatory_guidance"
    assert source_profile.bibliographic.title == "Synthetic Regulatory Guidance Fixture"
    assert source_profile.trust_level == "primary"
    assert source_profile.retrieved_for == ["seed-001", "clm-001"]
    assert passage.provenance.scaffold_run_id == "550e8400-e29b-41d4-a716-446655440000"
    assert passage.extraction_method == "scaffold_cited"
    assert audit_config.scoring.support_threshold_sourced == 0.8
    assert audit_config.rule_policies.needs_source_detection is True
    assert validation_ref.validation_set_version == "valset-phase-0-fixture"


def test_cb_models_reject_simplified_draft_shapes() -> None:
    """The partial generated guide's simplified fields are not accepted as locked C-B."""
    with pytest.raises(ValidationError):
        CBBundleManifest.model_validate(
            {
                "bundle_id": "bundle-001",
                "scaffold_run_id": "run-001",
                "bundle_format_version": "draft",
                "created_at_utc": "2026-05-10T00:00:00Z",
                "claim_count": 1,
                "source_count": 1,
            }
        )

    with pytest.raises(ValidationError):
        CBClaim.model_validate(
            {
                "claim_id": "clm-001",
                "claim_text": "The claim has old draft fields.",
                "claim_type": "extracted_claim",
                "support_status": "sourced",
                "source_ids": ["src-001"],
                "passage_ids": ["pass-001"],
            }
        )


def test_cb_vocabularies_do_not_accept_cal_or_legacy_label_values() -> None:
    """C-B role and verdict fields stay on the locked contract vocabularies."""
    claim_data = _load_yaml(FIXTURE_BUNDLE / "claims" / "clm-001.yaml")

    claim_data["claim_type"] = "numeric"
    with pytest.raises(ValidationError):
        CBClaim.model_validate(claim_data)

    claim_data = _load_yaml(FIXTURE_BUNDLE / "claims" / "clm-001.yaml")
    claim_data["audit"]["audit_support_verdict"] = "not_audit_ready"
    with pytest.raises(ValidationError):
        CBClaim.model_validate(claim_data)

