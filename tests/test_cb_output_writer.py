"""Tests for writing CAL audit results into a copied C-B bundle."""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path
from shutil import copytree
from typing import Any

import yaml

from claim_audit_lab.auditor import _build_assessments
from claim_audit_lab.contracts.adapter import adapt_bundle_to_pipeline
from claim_audit_lab.contracts.audit_flags import compute_flags
from claim_audit_lab.contracts.bundle_loader import BundleContents, load_bundle
from claim_audit_lab.contracts.cb_models import CBClaim
from claim_audit_lab.contracts.output_writer import write_audited_bundle
from claim_audit_lab.evidence_matching import match_claims_to_evidence
from claim_audit_lab.models import Claim, ClaimAssessment, EvidenceCandidate

FIXTURE_BUNDLE = Path(__file__).parent / "fixtures" / "cb" / "evidence-bundle-minimal"
AUDIT_RUN_ID = "cal-audit-run-unit-5"
AUDITED_AT_UTC = "2026-05-10T18:30:00Z"


def test_write_audited_bundle_populates_audit_fields_without_mutating_source(
    tmp_path: Path,
) -> None:
    """Audit results are written to a fresh copy and the sealed input stays byte-stable."""
    source_dir = _copy_fixture(tmp_path)
    contents = load_bundle(source_dir, deviations_dir=tmp_path / "source-deviations")
    assessments = _fixture_assessments(contents)
    source_before = _file_snapshot(source_dir)
    out_dir = tmp_path / "audited-bundle"

    result = write_audited_bundle(
        source_dir,
        out_dir,
        contents.claims,
        assessments,
        audit_run_id=AUDIT_RUN_ID,
        audited_at_utc=AUDITED_AT_UTC,
        audit_config=contents.audit_config,
    )

    assert result == out_dir.resolve()
    assert _file_snapshot(source_dir) == source_before
    assert _load_yaml(source_dir / "claims" / "clm-001.yaml")["audit"] == {
        "audit_run_id": None,
        "audited_at_utc": None,
        "audit_support_verdict": None,
        "audit_confidence": None,
        "audit_notes": None,
        "false_caution_flag": None,
        "deviation_flag": None,
        "deviation_notes": None,
    }

    output_claim = _load_yaml(out_dir / "claims" / "clm-001.yaml")
    assert output_claim["audit"]["audit_run_id"] == AUDIT_RUN_ID
    assert output_claim["audit"]["audited_at_utc"] == AUDITED_AT_UTC
    assert output_claim["audit"]["audit_support_verdict"] == "supported"
    assert output_claim["audit"]["audit_confidence"] > 0.85
    assert output_claim["audit"]["audit_notes"]
    assert output_claim["audit"]["false_caution_flag"] is False
    assert output_claim["audit"]["deviation_flag"] is False
    assert "No material disagreement" in output_claim["audit"]["deviation_notes"]

    reloaded = load_bundle(out_dir, deviations_dir=tmp_path / "output-deviations")
    assert reloaded.claims[0].audit.audit_run_id == AUDIT_RUN_ID
    assert reloaded.claims[0].audit.audit_support_verdict == "supported"


def test_write_audited_bundle_leaves_unassessed_retrieval_seed_untouched(
    tmp_path: Path,
) -> None:
    """Retrieval seeds are copied through unchanged when no assessment is supplied."""
    source_dir = _copy_fixture(tmp_path)
    contents = load_bundle(source_dir, deviations_dir=tmp_path / "source-deviations")
    seed_claim = _retrieval_seed_from_fixture_claim(contents)
    seed_path = source_dir / "claims" / "seed-001.yaml"
    _write_yaml(seed_path, seed_claim.model_dump(mode="json"))
    seed_before = seed_path.read_text(encoding="utf-8")
    out_dir = tmp_path / "audited-with-seed"

    write_audited_bundle(
        source_dir,
        out_dir,
        [seed_claim, *contents.claims],
        _fixture_assessments(contents),
        audit_run_id=AUDIT_RUN_ID,
        audited_at_utc=AUDITED_AT_UTC,
        audit_config=contents.audit_config,
    )

    assert seed_path.read_text(encoding="utf-8") == seed_before
    assert (out_dir / "claims" / "seed-001.yaml").read_text(encoding="utf-8") == seed_before


def test_compute_flags_marks_false_caution_when_cautious_scaffold_is_later_supported(
    tmp_path: Path,
) -> None:
    """Over-cautious scaffold labels become both false-caution and deviation signals."""
    contents = load_bundle(FIXTURE_BUNDLE, deviations_dir=tmp_path / "deviations")
    cautious_claim = _claim_with_scaffold_status(contents.claims[0], "uncertain")
    assessment = _assessment(cautious_claim, support_label="supported", score=0.91)

    flags = compute_flags(
        cautious_claim,
        assessment,
        false_caution_detection=True,
        false_caution_threshold=0.85,
    )

    assert flags.false_caution_flag is True
    assert flags.deviation_flag is True
    assert flags.audit_confidence == 0.91
    assert "false_caution_flag=true" in flags.deviation_notes


def test_compute_flags_marks_material_scaffold_audit_disagreement(tmp_path: Path) -> None:
    """A scaffold-sourced claim later judged unsupported is a formal disagreement."""
    contents = load_bundle(FIXTURE_BUNDLE, deviations_dir=tmp_path / "deviations")
    assessment = _assessment(contents.claims[0], support_label="unsupported", score=None)

    flags = compute_flags(contents.claims[0], assessment)

    assert flags.false_caution_flag is False
    assert flags.deviation_flag is True
    assert flags.audit_confidence == 0.1
    assert "scaffold_support_status=sourced" in flags.deviation_notes
    assert "audit_support_verdict=unsupported" in flags.deviation_notes


def _copy_fixture(tmp_path: Path) -> Path:
    destination = tmp_path / "evidence-bundle-minimal"
    copytree(FIXTURE_BUNDLE, destination)
    return destination


def _fixture_assessments(contents: BundleContents) -> dict[str, ClaimAssessment]:
    claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(contents)
    candidate_map = match_claims_to_evidence(claims, evidence_bundle, audit_config)
    assessments = _build_assessments(claims, evidence_bundle, candidate_map, audit_config)
    return {assessment.claim.id: assessment for assessment in assessments}


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


def _claim_with_scaffold_status(cb_claim: CBClaim, status: str) -> CBClaim:
    raw = cb_claim.model_dump(mode="python")
    raw["scaffold_support_status"] = status
    return CBClaim.model_validate(raw)


def _assessment(
    cb_claim: CBClaim,
    *,
    support_label: str,
    score: float | None,
) -> ClaimAssessment:
    candidates = []
    if score is not None:
        candidates.append(
            EvidenceCandidate(
                source_id="src-001",
                excerpt_id="src-001/pass-001",
                score=score,
                source_reliability="high",
            )
        )
    return ClaimAssessment(
        claim=Claim(id=cb_claim.claim_id, text=cb_claim.claim_text, claim_type="numeric"),
        support_label=support_label,  # type: ignore[arg-type]
        risk_label="low",
        candidate_evidence=candidates,
        explanation="Synthetic assessment for output-writer tests.",
    )


def _file_snapshot(root: Path) -> Mapping[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
