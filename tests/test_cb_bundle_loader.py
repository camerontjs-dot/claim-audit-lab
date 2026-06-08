"""Fail-closed intake tests for C-B evidence-bundle loading."""

from __future__ import annotations

from pathlib import Path
from shutil import copytree
from typing import Any

import pytest
import yaml

from claim_audit_lab.contracts.bundle_loader import (
    BundleIntegrityError,
    _compute_bundle_tree_hash,
    _hash_file_hex,
    _iter_handoff_files,
    _yaml_to_string,
    load_bundle,
)

FIXTURE_BUNDLE = Path(__file__).parent / "fixtures" / "cb" / "evidence-bundle-minimal"
BAD_HASH = "sha256:0000000000000000000000000000000000000000000000000000000000000000"


@pytest.fixture()
def bundle_tmp(tmp_path: Path) -> Path:
    """Return a writable copy of the CAL-local C-B fixture."""
    destination = tmp_path / "evidence-bundle-minimal"
    copytree(FIXTURE_BUNDLE, destination)
    return destination


def test_load_bundle_accepts_valid_cb_fixture(bundle_tmp: Path, tmp_path: Path) -> None:
    """A sealed C-B fixture loads into typed contents without writing deviations."""
    deviations_dir = tmp_path / "deviations"

    contents = load_bundle(bundle_tmp, deviations_dir=deviations_dir)

    assert contents.manifest.schema_version == "1.0.0"
    assert contents.manifest.bundle.claims_included == 1
    assert [claim.claim_id for claim in contents.claims] == ["clm-001"]
    assert sorted(contents.source_profiles) == ["src-001"]
    assert [passage.passage_id for passage in contents.passages["src-001"]] == ["pass-001"]
    assert contents.audit_config.config_id == "cal-rules-v1.2.0"
    assert contents.validation_set_ref.validation_set_version == "valset-phase-0-fixture"
    assert not deviations_dir.exists()


def test_missing_contract_version_fails_closed_with_typed_deviation(
    bundle_tmp: Path,
    tmp_path: Path,
) -> None:
    """Missing required intake files stop processing and write a formal deviation."""
    (bundle_tmp / "CONTRACT_VERSION").unlink()

    with pytest.raises(BundleIntegrityError, match="CONTRACT_VERSION"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")

    deviation = _single_deviation(tmp_path / "deviations")
    assert deviation["deviation_type"] == "missing_required_field"
    assert deviation["artifact_id"] == bundle_tmp.name
    assert "CONTRACT_VERSION file missing" in deviation["description"]
    assert deviation["resolution"] == "pending"


def test_sha256sum_mismatch_fails_before_processing(bundle_tmp: Path, tmp_path: Path) -> None:
    """Post-seal file mutation is detected through SHA256SUMS."""
    claim_path = bundle_tmp / "claims" / "clm-001.yaml"
    claim_path.write_text(
        claim_path.read_text(encoding="utf-8").replace("Accelerated approval", "Changed approval"),
        encoding="utf-8",
    )

    with pytest.raises(BundleIntegrityError, match="SHA256SUMS mismatch"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")

    deviation = _single_deviation(tmp_path / "deviations")
    assert deviation["deviation_type"] == "intake_hash_mismatch"
    assert deviation["artifact_id"] == _bundle_id(bundle_tmp)
    assert "claims/clm-001.yaml" in deviation["description"]


def test_bundle_hash_mismatch_fails_when_sha256sums_were_rewritten(
    bundle_tmp: Path,
    tmp_path: Path,
) -> None:
    """SHA256SUMS alone is insufficient; bundle.bundle_hash must also verify."""
    claim_path = bundle_tmp / "claims" / "clm-001.yaml"
    claim_path.write_text(
        claim_path.read_text(encoding="utf-8").replace("submission package", "submission dossier"),
        encoding="utf-8",
    )
    _write_sha256sums(bundle_tmp)

    with pytest.raises(BundleIntegrityError, match="bundle\\.bundle_hash"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")

    deviation = _single_deviation(tmp_path / "deviations")
    assert deviation["deviation_type"] == "intake_hash_mismatch"
    assert "bundle.bundle_hash" in deviation["description"]


def test_audit_config_hash_mismatch_fails_even_when_bundle_is_resealed(
    bundle_tmp: Path,
    tmp_path: Path,
) -> None:
    """The manifest audit_config_hash must agree with the normalized audit config hash."""
    manifest_path = bundle_tmp / "bundle_manifest.yaml"
    manifest = _load_yaml(manifest_path)
    manifest["audit_config_hash"] = BAD_HASH
    _write_yaml(manifest_path, manifest)
    _reseal_bundle(bundle_tmp)

    with pytest.raises(BundleIntegrityError, match="audit_config_hash"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")

    deviation = _single_deviation(tmp_path / "deviations")
    assert deviation["deviation_type"] == "intake_hash_mismatch"
    assert "audit_config_hash" in deviation["description"]


def test_malformed_claim_schema_fails_closed_after_integrity_verifies(
    bundle_tmp: Path,
    tmp_path: Path,
) -> None:
    """Schema-invalid claim files are typed schema deviations, not partial loads."""
    claim_path = bundle_tmp / "claims" / "clm-001.yaml"
    claim = _load_yaml(claim_path)
    del claim["workflow_condition"]
    _write_yaml(claim_path, claim)
    _reseal_bundle(bundle_tmp)

    with pytest.raises(BundleIntegrityError, match="claims/clm-001.yaml"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")

    deviation = _single_deviation(tmp_path / "deviations")
    assert deviation["deviation_type"] == "schema_validation_failure"
    assert "workflow_condition" in deviation["description"]


def test_optional_bundled_vocabulary_drift_fails_closed(
    bundle_tmp: Path,
    tmp_path: Path,
) -> None:
    """A bundle schema/vocabulary.yaml copy is optional, but drift is fatal if present."""
    vocab_path = bundle_tmp / "schema" / "vocabulary.yaml"
    vocab_path.parent.mkdir(parents=True)
    vocab_path.write_text(
        "controlled_vocabularies:\n  audit_support_verdict: []\n",
        encoding="utf-8",
    )
    _reseal_bundle(bundle_tmp)

    with pytest.raises(BundleIntegrityError, match="vocabulary.yaml"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")

    deviation = _single_deviation(tmp_path / "deviations")
    assert deviation["deviation_type"] == "vocabulary_drift"
    assert "schema/vocabulary.yaml" in deviation["description"]


def _single_deviation(deviations_dir: Path) -> dict[str, Any]:
    paths = sorted(deviations_dir.glob("*.yaml"))
    assert len(paths) == 1
    return _load_yaml(paths[0])


def _bundle_id(bundle_dir: Path) -> str:
    return str(_load_yaml(bundle_dir / "bundle_manifest.yaml")["bundle_id"])


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(_yaml_to_string(data), encoding="utf-8")


def _reseal_bundle(bundle_dir: Path) -> None:
    manifest_path = bundle_dir / "bundle_manifest.yaml"
    manifest = _load_yaml(manifest_path)
    manifest["bundle"]["bundle_hash"] = "sha256:pending"
    _write_yaml(manifest_path, manifest)
    manifest["bundle"]["bundle_hash"] = _compute_bundle_tree_hash(bundle_dir)
    _write_yaml(manifest_path, manifest)
    _write_sha256sums(bundle_dir)


def _write_sha256sums(bundle_dir: Path) -> None:
    lines = [
        f"{_hash_file_hex(path)}  {path.relative_to(bundle_dir).as_posix()}"
        for path in _iter_handoff_files(bundle_dir)
    ]
    (bundle_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
