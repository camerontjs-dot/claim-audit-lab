"""Adapter tests for turning locked C-B bundles into CAL pipeline inputs."""

from __future__ import annotations

from dataclasses import replace
from datetime import date as Date
from pathlib import Path
from typing import Any

from claim_audit_lab.auditor import _build_assessments
from claim_audit_lab.contracts.adapter import adapt_bundle_to_pipeline
from claim_audit_lab.contracts.bundle_loader import BundleContents, load_bundle
from claim_audit_lab.contracts.cb_models import CBClaim
from claim_audit_lab.evidence_matching import match_claims_to_evidence

FIXTURE_BUNDLE = Path(__file__).parent / "fixtures" / "cb" / "evidence-bundle-minimal"


def _loaded_contents(tmp_path: Path) -> BundleContents:
    return load_bundle(FIXTURE_BUNDLE, deviations_dir=tmp_path / "deviations")


def _retrieval_seed_from_fixture_claim(contents: BundleContents) -> CBClaim:
    raw: dict[str, Any] = contents.claims[0].model_dump(mode="python")
    raw.update(
        {
            "claim_id": "seed-001",
            "claim_text": "What stability data belongs in an accelerated approval package?",
            "claim_type": "retrieval_seed",
            "evidence_passages": [],
            "counterevidence_passages": [],
        }
    )
    return CBClaim.model_validate(raw)


def test_adapter_skips_cb_retrieval_seed_claims(tmp_path: Path) -> None:
    """Only C-B extracted_claim records become CAL Claim objects."""
    contents = _loaded_contents(tmp_path)
    contents_with_seed = replace(
        contents,
        claims=[_retrieval_seed_from_fixture_claim(contents), *contents.claims],
    )

    claims, _evidence_bundle, _audit_config = adapt_bundle_to_pipeline(contents_with_seed)

    assert [claim.id for claim in claims] == ["clm-001"]


def test_adapter_derives_cal_semantic_claim_type_from_text(tmp_path: Path) -> None:
    """C-B claim_type values must not leak into CAL's semantic Claim.claim_type."""
    contents = _loaded_contents(tmp_path)

    claims, _evidence_bundle, _audit_config = adapt_bundle_to_pipeline(contents)

    assert claims[0].claim_type == "numeric"
    assert claims[0].claim_type not in {"retrieval_seed", "extracted_claim"}
    assert claims[0].location is not None
    assert "workflow_condition=full_scaffold" in claims[0].location
    assert "scaffold_support_status=sourced" in claims[0].location
    assert "scaffold_claim_strength=0.86" in claims[0].location
    assert "scaffold_extraction_fidelity=0.92" in claims[0].location


def test_adapter_preserves_cb_source_and_passage_traceability(tmp_path: Path) -> None:
    """Locked C-B source/profile fields become CAL evidence metadata."""
    contents = _loaded_contents(tmp_path)

    _claims, evidence_bundle, _audit_config = adapt_bundle_to_pipeline(contents)

    assert len(evidence_bundle.sources) == 1
    source = evidence_bundle.sources[0]
    assert source.id == "src-001"
    assert source.title == "Synthetic Regulatory Guidance Fixture"
    assert source.source_type == "report"
    assert source.reliability == "high"
    assert source.url == "https://example.test/synthetic-regulatory-guidance"
    assert source.date == Date(2026, 5, 8)

    assert len(source.excerpts) == 1
    excerpt = source.excerpts[0]
    assert excerpt.id == "src-001/pass-001"
    assert excerpt.text.startswith("For accelerated approval applications")
    assert excerpt.notes is not None
    assert "c_b_passage_id=pass-001" in excerpt.notes
    assert "section=Synthetic Guidance" in excerpt.notes
    assert "char_range=127-250" in excerpt.notes
    assert "passage_hash=sha256:60d369c3c3befaef" in excerpt.notes
    assert "scaffold_run_id=550e8400-e29b-41d4-a716-446655440000" in excerpt.notes


def test_adapter_maps_locked_cb_audit_config_to_current_cal_config(tmp_path: Path) -> None:
    """The adapter uses locked C-B audit_config blocks, not old draft fields."""
    contents = _loaded_contents(tmp_path)

    _claims, _evidence_bundle, audit_config = adapt_bundle_to_pipeline(contents)

    assert audit_config.strictness == "standard"
    assert audit_config.min_overlap_score == 0.4
    assert audit_config.max_candidate_evidence == 1
    assert audit_config.reference_date == Date(2026, 5, 10)
    assert audit_config.freshness_days == 365


def test_adapted_cb_fixture_runs_through_current_cal_assessment_path(tmp_path: Path) -> None:
    """Adapted C-B data is usable by CAL matching and rule assessment."""
    contents = _loaded_contents(tmp_path)
    claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(contents)

    candidate_map = match_claims_to_evidence(claims, evidence_bundle, audit_config)
    assessments = _build_assessments(claims, evidence_bundle, candidate_map, audit_config)

    assert [assessment.claim.id for assessment in assessments] == ["clm-001"]
    assert assessments[0].support_label == "supported"
    assert assessments[0].candidate_evidence[0].source_id == "src-001"
    assert assessments[0].candidate_evidence[0].excerpt_id == "src-001/pass-001"
