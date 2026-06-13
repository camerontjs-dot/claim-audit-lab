"""Fail-closed intake tests for C-B evidence-bundle loading."""

from __future__ import annotations

from pathlib import Path
from shutil import copytree
from typing import Any

import pytest
import yaml

from claim_audit_lab.contracts.bundle_loader import (
    BundleIntegrityError,
    load_bundle,
)
from claim_audit_lab.contracts.serialization import (
    compute_bundle_tree_hash,
    hash_audit_config_file,
    hash_file_hex,
    iter_handoff_files,
    yaml_to_string,
)
from claim_audit_lab.resources import read_package_bytes, read_package_text

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


def test_packaged_contract_resources_match_repository_pins() -> None:
    """The wheel's runtime copies stay byte-identical to governed root resources."""
    project_root = Path(__file__).resolve().parents[1]

    assert read_package_text("schema/.contract-version") == (
        project_root / "schema" / ".contract-version"
    ).read_text(encoding="utf-8")
    assert (
        read_package_bytes("schema/vocabulary.yaml")
        == (project_root / "schema" / "vocabulary.yaml").read_bytes()
    )


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


def test_missing_bundle_directory_fails_closed(tmp_path: Path) -> None:
    missing = tmp_path / "missing-bundle"

    with pytest.raises(BundleIntegrityError, match="does not exist"):
        load_bundle(missing, deviations_dir=tmp_path / "deviations")


def test_unsupported_contract_version_fails_closed(bundle_tmp: Path, tmp_path: Path) -> None:
    (bundle_tmp / "CONTRACT_VERSION").write_text("9.9.9\n", encoding="utf-8")

    with pytest.raises(BundleIntegrityError, match="CONTRACT_VERSION mismatch"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


def test_missing_audit_config_fails_closed(bundle_tmp: Path, tmp_path: Path) -> None:
    (bundle_tmp / "audit_config.yaml").unlink()

    with pytest.raises(BundleIntegrityError, match="audit_config.yaml missing"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


def test_malformed_manifest_yaml_fails_closed(bundle_tmp: Path, tmp_path: Path) -> None:
    (bundle_tmp / "bundle_manifest.yaml").write_text("bundle: [\n", encoding="utf-8")

    with pytest.raises(BundleIntegrityError, match="malformed YAML"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


def test_audit_config_self_hash_mismatch_fails_closed(
    bundle_tmp: Path,
    tmp_path: Path,
) -> None:
    config_path = bundle_tmp / "audit_config.yaml"
    config = _load_yaml(config_path)
    config["config_hash"] = BAD_HASH
    _write_yaml(config_path, config)

    with pytest.raises(BundleIntegrityError, match="audit_config.config_hash"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


@pytest.mark.parametrize(
    ("contents", "message"),
    [
        pytest.param("malformed\n", "line 1 is malformed", id="malformed-line"),
        pytest.param(
            f"{'0' * 64}  ../escape.yaml\n",
            "path escapes bundle",
            id="path-traversal",
        ),
        pytest.param(
            f"{'0' * 64}  missing.yaml\n",
            "references missing file",
            id="missing-file",
        ),
    ],
)
def test_invalid_sha256sums_fail_closed(
    bundle_tmp: Path,
    tmp_path: Path,
    contents: str,
    message: str,
) -> None:
    (bundle_tmp / "SHA256SUMS").write_text(contents, encoding="utf-8")

    with pytest.raises(BundleIntegrityError, match=message):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


def test_sha256sums_missing_entry_fails_closed(bundle_tmp: Path, tmp_path: Path) -> None:
    sums_path = bundle_tmp / "SHA256SUMS"
    lines = sums_path.read_text(encoding="utf-8").splitlines()
    sums_path.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")

    with pytest.raises(BundleIntegrityError, match="missing entries"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


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


@pytest.mark.parametrize(
    ("field_path", "value"),
    [
        pytest.param(("config_id",), "cal-rules-v1.2.1", id="changed-id"),
        pytest.param(
            ("scoring", "support_threshold_sourced"),
            0.81,
            id="changed-threshold",
        ),
        pytest.param(
            ("rule_policies", "overstated_detection"),
            False,
            id="changed-switch",
        ),
    ],
)
def test_unsupported_audit_policy_fails_closed_after_hash_verification(
    bundle_tmp: Path,
    tmp_path: Path,
    field_path: tuple[str, ...],
    value: object,
) -> None:
    """Hash-valid policy drift is still rejected as a typed intake deviation."""
    _rewrite_audit_policy(bundle_tmp, field_path, value)

    with pytest.raises(BundleIntegrityError, match="Unsupported C-B audit policy"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")

    deviation = _single_deviation(tmp_path / "deviations")
    assert deviation["deviation_type"] == "vocabulary_drift"
    assert ".".join(field_path) in deviation["description"]


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


@pytest.mark.parametrize(
    ("target", "message"),
    [
        pytest.param("claims", "claims/ directory missing", id="claims"),
        pytest.param("evidence", "evidence/ directory missing", id="evidence"),
        pytest.param(
            "evidence/src-001/passages",
            "passages/ directory missing",
            id="passages",
        ),
    ],
)
def test_missing_bundle_structure_fails_closed(
    bundle_tmp: Path,
    tmp_path: Path,
    target: str,
    message: str,
) -> None:
    from shutil import rmtree

    rmtree(bundle_tmp / target)
    _reseal_bundle(bundle_tmp)

    with pytest.raises(BundleIntegrityError, match=message):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        pytest.param("claims_included", 2, "claims_included", id="claim-count"),
        pytest.param(
            "total_evidence_passages",
            2,
            "total_evidence_passages",
            id="passage-count",
        ),
    ],
)
def test_manifest_count_inconsistency_fails_closed(
    bundle_tmp: Path,
    tmp_path: Path,
    field: str,
    value: int,
    message: str,
) -> None:
    manifest_path = bundle_tmp / "bundle_manifest.yaml"
    manifest = _load_yaml(manifest_path)
    manifest["bundle"][field] = value
    _write_yaml(manifest_path, manifest)
    _reseal_bundle(bundle_tmp)

    with pytest.raises(BundleIntegrityError, match=message):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


def test_source_profile_directory_mismatch_fails_closed(
    bundle_tmp: Path,
    tmp_path: Path,
) -> None:
    profile_path = bundle_tmp / "evidence" / "src-001" / "source_profile.yaml"
    profile = _load_yaml(profile_path)
    profile["source_id"] = "src-other"
    _write_yaml(profile_path, profile)
    _reseal_bundle(bundle_tmp)

    with pytest.raises(BundleIntegrityError, match="source_id does not match"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


def test_claim_reference_to_missing_passage_fails_closed(
    bundle_tmp: Path,
    tmp_path: Path,
) -> None:
    claim_path = bundle_tmp / "claims" / "clm-001.yaml"
    claim = _load_yaml(claim_path)
    claim["evidence_passages"][0]["passage_id"] = "pass-missing"
    _write_yaml(claim_path, claim)
    _reseal_bundle(bundle_tmp)

    with pytest.raises(BundleIntegrityError, match="reference missing evidence"):
        load_bundle(bundle_tmp, deviations_dir=tmp_path / "deviations")


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
    path.write_text(yaml_to_string(data), encoding="utf-8")


def _rewrite_audit_policy(
    bundle_dir: Path,
    field_path: tuple[str, ...],
    value: object,
) -> None:
    config_path = bundle_dir / "audit_config.yaml"
    config = _load_yaml(config_path)
    target: dict[str, Any] = config
    for field in field_path[:-1]:
        nested = target[field]
        assert isinstance(nested, dict)
        target = nested
    target[field_path[-1]] = value
    config["config_hash"] = "sha256:pending"
    _write_yaml(config_path, config)
    config["config_hash"] = hash_audit_config_file(config_path)
    _write_yaml(config_path, config)

    manifest_path = bundle_dir / "bundle_manifest.yaml"
    manifest = _load_yaml(manifest_path)
    manifest["audit_config_hash"] = config["config_hash"]
    if field_path == ("config_id",):
        manifest["audit_config_version"] = value
    _write_yaml(manifest_path, manifest)
    _reseal_bundle(bundle_dir)


def _reseal_bundle(bundle_dir: Path) -> None:
    manifest_path = bundle_dir / "bundle_manifest.yaml"
    manifest = _load_yaml(manifest_path)
    manifest["bundle"]["bundle_hash"] = "sha256:pending"
    _write_yaml(manifest_path, manifest)
    manifest["bundle"]["bundle_hash"] = compute_bundle_tree_hash(bundle_dir)
    _write_yaml(manifest_path, manifest)
    _write_sha256sums(bundle_dir)


def _write_sha256sums(bundle_dir: Path) -> None:
    lines = [
        f"{hash_file_hex(path)}  {path.relative_to(bundle_dir).as_posix()}"
        for path in iter_handoff_files(bundle_dir)
    ]
    (bundle_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
