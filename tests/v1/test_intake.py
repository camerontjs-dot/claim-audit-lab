"""Tests for the Phase 3 apparatus-intake normalizer (``v1.intake``).

Covers ``bundle_to_requests`` over the locked ``evidence-bundle-minimal``
fixture plus the ``retrieval_seed`` skip and the ``CBAuditConfig.pipeline``
selector default.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from shutil import copytree
from typing import Any

import pytest
import yaml

from claim_audit_lab.contracts.bundle_loader import (
    BundleContents,
    BundleIntegrityError,
    load_bundle,
)
from claim_audit_lab.contracts.cb_models import CBClaim, CBPassage
from claim_audit_lab.contracts.serialization import reseal_bundle
from claim_audit_lab.v1 import (
    AuditedBundleContents,
    AuditedBundleError,
    bundle_to_requests,
    load_audited,
)
from claim_audit_lab.v1.cb_writeback import write_audited_bundle_v1
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.models import (
    AuditRequest,
    AuditTrace,
    ExtractedFeatures,
    Passage,
    SupportSignal,
    Verdict,
)

FIXTURE_BUNDLE = Path(__file__).parents[1] / "fixtures" / "cb" / "evidence-bundle-minimal"


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return raw


def _load_minimal_bundle(tmp_path: Path) -> BundleContents:
    # deviations land in a scratch dir so a load failure never writes into the repo
    return load_bundle(FIXTURE_BUNDLE, deviations_dir=tmp_path / "deviations")


def _fixture_trace() -> AuditTrace:
    return AuditTrace(
        claim_id="clm-001",
        claim_text=(
            "Accelerated approval applications should include 30-day accelerated stability "
            "data in the submission package."
        ),
        retrieval=[],
        entailment=[],
        features=ExtractedFeatures(),
        support_signal=SupportSignal(
            label="entail",
            max_entailment_score=0.99,
            contributing_passage_id="src-001/pass-001",
        ),
        rules_fired=[],
        verdict=Verdict(support_verdict="supported"),
        audit_config_hash="sha256:" + "a" * 64,
        library_version="test",
    )


def _write_fixture_audited(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    copytree(FIXTURE_BUNDLE, source)
    contents = load_bundle(source, deviations_dir=tmp_path / "source-dev")
    return write_audited_bundle_v1(
        source,
        tmp_path / "audited",
        {"clm-001": _fixture_trace()},
        contents.claims,
        audit_run_id="typed-loader-test",
        audited_at_utc="2026-06-29T00:00:00Z",
    )


def test_minimal_bundle_normalizes_to_one_request_per_extracted_claim(tmp_path: Path) -> None:
    bundle = _load_minimal_bundle(tmp_path)
    config = load_default_audit_config()

    requests = bundle_to_requests(bundle, config)

    assert len(requests) == 1
    request = requests[0]
    assert isinstance(request, AuditRequest)
    assert request.claim_id == "clm-001"
    assert request.claim_text.startswith("Accelerated approval applications should include")
    assert request.audit_config == config


def test_request_carries_full_passage_set_with_preserved_provenance(tmp_path: Path) -> None:
    bundle = _load_minimal_bundle(tmp_path)

    (request,) = bundle_to_requests(bundle, load_default_audit_config())

    assert [p.passage_id for p in request.passages] == ["src-001/pass-001"]
    passage = request.passages[0]
    assert isinstance(passage, Passage)
    assert passage.text.startswith("For accelerated approval applications")
    assert passage.source_meta == {
        "source_id": "src-001",
        "passage_id": "pass-001",
        "passage_hash": "sha256:60d369c3c3befaef9a16bbf1f642ce3f5200256816f09fd91bdd277b1d5b8f55",
        "trust_level": "primary",
        "section": "Synthetic Guidance",
    }


def test_every_passage_carries_its_source_trust_level(tmp_path: Path) -> None:
    # D1 (Decision H / cal-rules-v1.5.0): the intake join stamps the source's
    # trust_level onto every passage's source_meta so the eligibility rules can
    # read provenance without re-loading the source profile.
    bundle = _load_minimal_bundle(tmp_path)

    (request,) = bundle_to_requests(bundle, load_default_audit_config())

    assert all(p.source_meta.get("trust_level") for p in request.passages)
    assert request.passages[0].source_meta["trust_level"] == "primary"


def test_background_source_trust_level_round_trips(tmp_path: Path) -> None:
    # A non-primary source round-trips its tier unchanged — this is the provenance
    # the P1 eligibility precondition reads to refuse a solo adverse decision.
    bundle = _load_minimal_bundle(tmp_path)
    background_profile = bundle.source_profiles["src-001"].model_copy(
        update={"trust_level": "background"}
    )
    bundle = replace(bundle, source_profiles={"src-001": background_profile})

    (request,) = bundle_to_requests(bundle, load_default_audit_config())

    assert request.passages[0].source_meta["trust_level"] == "background"


def test_normalization_is_deterministic(tmp_path: Path) -> None:
    bundle = _load_minimal_bundle(tmp_path)
    config = load_default_audit_config()

    assert bundle_to_requests(bundle, config) == bundle_to_requests(bundle, config)


def test_retrieval_seed_claims_are_skipped(tmp_path: Path) -> None:
    bundle = _load_minimal_bundle(tmp_path)
    seed_raw = _load_yaml(FIXTURE_BUNDLE / "claims" / "clm-001.yaml")
    seed_raw["claim_id"] = "seed-001"
    seed_raw["claim_type"] = "retrieval_seed"
    seeded = replace(bundle, claims=[*bundle.claims, CBClaim.model_validate(seed_raw)])

    requests = bundle_to_requests(seeded, load_default_audit_config())

    assert [r.claim_id for r in requests] == ["clm-001"]


def test_passage_without_section_omits_the_section_key(tmp_path: Path) -> None:
    bundle = _load_minimal_bundle(tmp_path)
    raw_passage = _load_yaml(FIXTURE_BUNDLE / "evidence" / "src-001" / "passages" / "pass-001.yaml")
    raw_passage["section"] = None
    sectionless = {"src-001": [CBPassage.model_validate(raw_passage)]}
    bundle = replace(bundle, passages=sectionless)

    (request,) = bundle_to_requests(bundle, load_default_audit_config())

    assert "section" not in request.passages[0].source_meta


def test_pipeline_selector_defaults_to_v0_2_lexical(tmp_path: Path) -> None:
    bundle = _load_minimal_bundle(tmp_path)
    # the fixture audit_config.yaml omits the field; the model default applies
    assert bundle.audit_config.pipeline == "v0.2-lexical"


def test_load_audited_returns_bundle_contents_with_typed_traces(tmp_path: Path) -> None:
    audited_dir = _write_fixture_audited(tmp_path)

    audited = load_audited(audited_dir, deviations_dir=tmp_path / "audited-dev")

    assert isinstance(audited, BundleContents)
    assert isinstance(audited, AuditedBundleContents)
    assert audited.manifest.bundle_id
    assert set(audited.traces) == {"clm-001"}
    assert isinstance(audited.traces["clm-001"], AuditTrace)
    assert audited.traces["clm-001"].verdict.support_verdict == "supported"


def test_load_audited_rejects_missing_trace(tmp_path: Path) -> None:
    with pytest.raises(AuditedBundleError, match="Missing v1 audit traces.*clm-001"):
        load_audited(FIXTURE_BUNDLE, deviations_dir=tmp_path / "deviations")


def test_load_audited_strictly_validates_trace_json(tmp_path: Path) -> None:
    audited_dir = _write_fixture_audited(tmp_path)
    trace_path = audited_dir / "claims" / "clm-001.audit-trace.json"
    trace_path.write_text("{}\n", encoding="utf-8")
    reseal_bundle(audited_dir)

    with pytest.raises(AuditedBundleError, match="Invalid v1 audit trace"):
        load_audited(audited_dir, deviations_dir=tmp_path / "audited-dev")


def test_load_audited_rejects_trace_claim_binding_mismatch(tmp_path: Path) -> None:
    audited_dir = _write_fixture_audited(tmp_path)
    trace_path = audited_dir / "claims" / "clm-001.audit-trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["claim_id"] = "clm-other"
    trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    reseal_bundle(audited_dir)

    with pytest.raises(AuditedBundleError, match="claim_id mismatch"):
        load_audited(audited_dir, deviations_dir=tmp_path / "audited-dev")


def test_load_audited_runs_bundle_integrity_checks_before_trace_parsing(tmp_path: Path) -> None:
    audited_dir = _write_fixture_audited(tmp_path)
    trace_path = audited_dir / "claims" / "clm-001.audit-trace.json"
    trace_path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(BundleIntegrityError, match="SHA256SUMS mismatch") as exc_info:
        load_audited(audited_dir, deviations_dir=tmp_path / "audited-dev")
    assert type(exc_info.value) is BundleIntegrityError
