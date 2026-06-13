"""Fail-closed loader for locked C-B evidence-bundle directories."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal, TypeVar, cast

import yaml
from pydantic import BaseModel, ValidationError

from claim_audit_lab.contracts.cb_models import (
    CBAuditConfig,
    CBBundleManifest,
    CBClaim,
    CBPassage,
    CBSourceProfile,
    CBValidationSetRef,
)
from claim_audit_lab.resources import (
    PackageResourceError,
    read_package_bytes,
    read_package_text,
)

CONTRACT_VERSION = "1.1.0"
SUPPORTED_CONTRACT_VERSIONS: frozenset[str] = frozenset({"1.0.0", "1.1.0"})
PENDING_HASH = "sha256:pending"
SHA256_PREFIX = "sha256:"
DETECTED_BY = "claim_audit_lab"

DeviationType = Literal[
    "intake_hash_mismatch",
    "schema_validation_failure",
    "vocabulary_drift",
    "missing_required_field",
    "other",
]

TModel = TypeVar("TModel", bound=BaseModel)

_CONTRACT_VERSION_RESOURCE = "schema/.contract-version"
_VOCAB_RESOURCE = "schema/vocabulary.yaml"

_YAML_DUMP_KWARGS: dict[str, Any] = {
    "allow_unicode": True,
    "default_flow_style": False,
    "indent": 2,
    "sort_keys": False,
}


class BundleIntegrityError(Exception):
    """Raised when any bundle intake verification step fails."""


@dataclass(frozen=True)
class DeviationRecord:
    """Formal C-B intake deviation record."""

    deviation_id: str
    deviation_type: DeviationType
    artifact_id: str
    detected_at_utc: str
    detected_by: str
    description: str
    impact_assessment: str
    resolution: str = "pending"
    capa_notes: str = ""

    @classmethod
    def build(
        cls,
        *,
        deviation_type: DeviationType,
        artifact_id: str,
        description: str,
    ) -> DeviationRecord:
        digest = sha256(f"{artifact_id}:{deviation_type}:{description}".encode()).hexdigest()
        return cls(
            deviation_id=f"dev-{digest[:12]}",
            deviation_type=deviation_type,
            artifact_id=artifact_id,
            detected_at_utc=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            detected_by=DETECTED_BY,
            description=description,
            impact_assessment="Cannot proceed; C-B bundle intake halted.",
        )

    def to_dict(self) -> dict[str, str]:
        """Return a YAML-serializable mapping."""
        return {
            "deviation_id": self.deviation_id,
            "deviation_type": self.deviation_type,
            "artifact_id": self.artifact_id,
            "detected_at_utc": self.detected_at_utc,
            "detected_by": self.detected_by,
            "description": self.description,
            "impact_assessment": self.impact_assessment,
            "resolution": self.resolution,
            "capa_notes": self.capa_notes,
        }


@dataclass
class BundleContents:
    """Typed C-B bundle contents returned after successful intake verification."""

    manifest: CBBundleManifest
    audit_config: CBAuditConfig
    validation_set_ref: CBValidationSetRef
    claims: list[CBClaim]
    passages: dict[str, list[CBPassage]]
    source_profiles: dict[str, CBSourceProfile]


def load_bundle(
    bundle_dir: Path,
    *,
    deviations_dir: Path | None = None,
) -> BundleContents:
    """Verify and load a C-B bundle directory.

    Intake is halt-on-first-failure. Any failure writes a typed deviation record
    before raising ``BundleIntegrityError``.
    """
    bundle_dir = bundle_dir.resolve()
    active_deviations_dir = (deviations_dir or bundle_dir.parent / "deviations").resolve()
    artifact_id = bundle_dir.name

    def fail(deviation_type: DeviationType, description: str) -> None:
        deviation = DeviationRecord.build(
            deviation_type=deviation_type,
            artifact_id=artifact_id,
            description=description,
        )
        _write_deviation(active_deviations_dir, deviation)
        raise BundleIntegrityError(description)

    if not bundle_dir.is_dir():
        fail("missing_required_field", f"Bundle directory does not exist: {bundle_dir}")

    _verify_contract_version(bundle_dir, fail)

    manifest = _load_model(
        CBBundleManifest,
        bundle_dir / "bundle_manifest.yaml",
        "bundle_manifest.yaml",
        fail,
    )
    artifact_id = manifest.bundle_id

    audit_config = _load_model(
        CBAuditConfig,
        bundle_dir / "audit_config.yaml",
        "audit_config.yaml",
        fail,
    )
    validation_set_ref = _load_model(
        CBValidationSetRef,
        bundle_dir / "validation_set_ref.yaml",
        "validation_set_ref.yaml",
        fail,
    )

    _verify_audit_config_hash(bundle_dir, manifest, audit_config, fail)
    _verify_sha256sums(bundle_dir, fail)
    _verify_bundle_hash(bundle_dir, manifest, fail)
    _verify_optional_vocabulary(bundle_dir, fail)

    claims = _load_claims(bundle_dir, fail)
    source_profiles, passages = _load_evidence(bundle_dir, fail)
    _verify_loaded_consistency(manifest, claims, source_profiles, passages, fail)

    return BundleContents(
        manifest=manifest,
        audit_config=audit_config,
        validation_set_ref=validation_set_ref,
        claims=claims,
        passages=passages,
        source_profiles=source_profiles,
    )


def _verify_contract_version(
    bundle_dir: Path,
    fail: Callable[[DeviationType, str], None],
) -> None:
    contract_path = bundle_dir / "CONTRACT_VERSION"
    if not contract_path.exists():
        fail("missing_required_field", "CONTRACT_VERSION file missing")
    bundle_version = contract_path.read_text(encoding="utf-8").strip()
    try:
        consumer_version = read_package_text(_CONTRACT_VERSION_RESOURCE).strip()
    except PackageResourceError as exc:
        fail("missing_required_field", str(exc))
    if bundle_version not in SUPPORTED_CONTRACT_VERSIONS:
        fail(
            "vocabulary_drift",
            (
                "CONTRACT_VERSION mismatch: "
                f"bundle has {bundle_version!r}, CAL pins {consumer_version!r}"
            ),
        )


def _load_model(
    model_type: type[TModel],
    path: Path,
    rel_path: str,
    fail: Callable[[DeviationType, str], None],
) -> TModel:
    if not path.exists():
        fail("missing_required_field", f"{rel_path} missing")
    try:
        raw = _load_yaml(path)
        return model_type.model_validate(raw)
    except yaml.YAMLError as exc:
        fail("schema_validation_failure", f"{rel_path} is malformed YAML: {exc}")
    except (TypeError, ValueError, ValidationError) as exc:
        fail("schema_validation_failure", f"{rel_path} schema validation failed: {exc}")
    raise AssertionError("unreachable")


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("expected YAML mapping")
    return data


def _verify_audit_config_hash(
    bundle_dir: Path,
    manifest: CBBundleManifest,
    audit_config: CBAuditConfig,
    fail: Callable[[DeviationType, str], None],
) -> None:
    actual_hash = _hash_audit_config_file(bundle_dir / "audit_config.yaml")
    if audit_config.config_hash != actual_hash:
        fail(
            "intake_hash_mismatch",
            (
                "audit_config.config_hash does not match normalized "
                f"audit_config.yaml: expected {audit_config.config_hash}, got {actual_hash}"
            ),
        )
    if manifest.audit_config_hash != audit_config.config_hash:
        fail(
            "intake_hash_mismatch",
            "bundle_manifest.audit_config_hash does not match audit_config.config_hash",
        )


def _verify_sha256sums(
    bundle_dir: Path,
    fail: Callable[[DeviationType, str], None],
) -> None:
    sums_path = bundle_dir / "SHA256SUMS"
    if not sums_path.exists():
        fail("missing_required_field", "SHA256SUMS file missing")

    expected_paths: set[str] = set()
    for line_number, line in enumerate(
        sums_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            expected_hash, rel_path = line.split(maxsplit=1)
        except ValueError:
            fail("schema_validation_failure", f"SHA256SUMS line {line_number} is malformed")
        expected_paths.add(rel_path)
        target = _resolve_handoff_path(bundle_dir, rel_path, fail)
        if not target.exists():
            fail("intake_hash_mismatch", f"SHA256SUMS references missing file: {rel_path}")
        actual_hash = _hash_file_hex(target)
        if actual_hash != expected_hash:
            fail("intake_hash_mismatch", f"SHA256SUMS mismatch for {rel_path}")

    actual_paths = {
        path.relative_to(bundle_dir).as_posix() for path in _iter_handoff_files(bundle_dir)
    }
    missing_from_sums = sorted(actual_paths - expected_paths)
    if missing_from_sums:
        fail(
            "intake_hash_mismatch",
            f"SHA256SUMS missing entries: {', '.join(missing_from_sums)}",
        )


def _resolve_handoff_path(
    bundle_dir: Path,
    rel_path: str,
    fail: Callable[[DeviationType, str], None],
) -> Path:
    target = (bundle_dir / rel_path).resolve()
    try:
        target.relative_to(bundle_dir)
    except ValueError:
        fail("schema_validation_failure", f"SHA256SUMS path escapes bundle: {rel_path}")
    return target


def _verify_bundle_hash(
    bundle_dir: Path,
    manifest: CBBundleManifest,
    fail: Callable[[DeviationType, str], None],
) -> None:
    actual_hash = _compute_bundle_tree_hash(bundle_dir)
    if manifest.bundle.bundle_hash != actual_hash:
        fail(
            "intake_hash_mismatch",
            (
                "bundle.bundle_hash does not match recomputed bundle tree hash: "
                f"expected {manifest.bundle.bundle_hash}, got {actual_hash}"
            ),
        )


def _verify_optional_vocabulary(
    bundle_dir: Path,
    fail: Callable[[DeviationType, str], None],
) -> None:
    bundle_vocab = bundle_dir / "schema" / "vocabulary.yaml"
    if not bundle_vocab.exists():
        return
    try:
        pinned_vocabulary = read_package_bytes(_VOCAB_RESOURCE)
    except PackageResourceError as exc:
        fail("missing_required_field", str(exc))
    if bundle_vocab.read_bytes() != pinned_vocabulary:
        fail(
            "vocabulary_drift",
            "schema/vocabulary.yaml in bundle is not byte-identical to CAL's pinned copy",
        )


def _load_claims(
    bundle_dir: Path,
    fail: Callable[[DeviationType, str], None],
) -> list[CBClaim]:
    claims_dir = bundle_dir / "claims"
    if not claims_dir.is_dir():
        fail("missing_required_field", "claims/ directory missing")

    claims: list[CBClaim] = []
    for path in sorted(claims_dir.glob("*.yaml")):
        rel_path = path.relative_to(bundle_dir).as_posix()
        claims.append(_load_model(CBClaim, path, rel_path, fail))
    return claims


def _load_evidence(
    bundle_dir: Path,
    fail: Callable[[DeviationType, str], None],
) -> tuple[dict[str, CBSourceProfile], dict[str, list[CBPassage]]]:
    evidence_dir = bundle_dir / "evidence"
    if not evidence_dir.is_dir():
        fail("missing_required_field", "evidence/ directory missing")

    source_profiles: dict[str, CBSourceProfile] = {}
    passages: dict[str, list[CBPassage]] = {}
    for source_dir in sorted(path for path in evidence_dir.iterdir() if path.is_dir()):
        source_id = source_dir.name
        profile_path = source_dir / "source_profile.yaml"
        source_profiles[source_id] = _load_model(
            CBSourceProfile,
            profile_path,
            f"evidence/{source_id}/source_profile.yaml",
            fail,
        )

        passages_dir = source_dir / "passages"
        if not passages_dir.is_dir():
            fail("missing_required_field", f"evidence/{source_id}/passages/ directory missing")

        source_passages: list[CBPassage] = []
        for passage_path in sorted(passages_dir.glob("*.yaml")):
            rel_path = passage_path.relative_to(bundle_dir).as_posix()
            source_passages.append(_load_model(CBPassage, passage_path, rel_path, fail))
        passages[source_id] = source_passages

    return source_profiles, passages


def _verify_loaded_consistency(
    manifest: CBBundleManifest,
    claims: list[CBClaim],
    source_profiles: dict[str, CBSourceProfile],
    passages: dict[str, list[CBPassage]],
    fail: Callable[[DeviationType, str], None],
) -> None:
    if len(claims) != manifest.bundle.claims_included:
        fail(
            "schema_validation_failure",
            (
                "claims_included does not match loaded claim files: "
                f"manifest={manifest.bundle.claims_included}, loaded={len(claims)}"
            ),
        )

    total_passages = sum(len(source_passages) for source_passages in passages.values())
    if total_passages != manifest.bundle.total_evidence_passages:
        fail(
            "schema_validation_failure",
            (
                "total_evidence_passages does not match loaded passage files: "
                f"manifest={manifest.bundle.total_evidence_passages}, loaded={total_passages}"
            ),
        )

    if any(profile.source_id != source_id for source_id, profile in source_profiles.items()):
        fail("schema_validation_failure", "source_profile source_id does not match directory name")

    passage_lookup = {
        (passage.source_id, passage.passage_id)
        for source_passages in passages.values()
        for passage in source_passages
    }
    missing_refs = sorted(
        f"{claim.claim_id}:{embedded.source_id}/{embedded.passage_id}"
        for claim in claims
        for embedded in [*claim.evidence_passages, *claim.counterevidence_passages]
        if embedded.source_id not in source_profiles
        or (embedded.source_id, embedded.passage_id) not in passage_lookup
    )
    if missing_refs:
        fail(
            "schema_validation_failure",
            (
                "claim evidence_passages reference missing evidence records: "
                f"{', '.join(missing_refs)}"
            ),
        )


def _compute_bundle_tree_hash(bundle_dir: Path) -> str:
    hasher = sha256()
    for path in _iter_handoff_files(bundle_dir):
        rel_path = path.relative_to(bundle_dir).as_posix()
        if rel_path == "audit_config.yaml":
            digest = _strip_hash_prefix(_hash_audit_config_file(path))
        elif rel_path == "bundle_manifest.yaml":
            digest = _strip_hash_prefix(_hash_bundle_manifest_file(path))
        else:
            digest = _hash_file_hex(path)
        hasher.update(f"{rel_path}\0{digest}\n".encode())
    return f"{SHA256_PREFIX}{hasher.hexdigest()}"


def _hash_audit_config_file(path: Path) -> str:
    return _normalized_yaml_hash(path, lambda data: data.__setitem__("config_hash", PENDING_HASH))


def _hash_bundle_manifest_file(path: Path) -> str:
    def normalize(data: dict[str, Any]) -> None:
        bundle = data.get("bundle")
        if not isinstance(bundle, dict):
            raise ValueError("bundle_manifest.yaml missing bundle mapping")
        bundle["bundle_hash"] = PENDING_HASH

    return _normalized_yaml_hash(path, normalize)


def _normalized_yaml_hash(path: Path, normalizer: Callable[[dict[str, Any]], None]) -> str:
    data = _load_yaml(path)
    normalizer(data)
    return _hash_text(_yaml_to_string(data))


def _iter_handoff_files(
    root: Path,
    *,
    exclude_names: Iterable[str] = ("SHA256SUMS",),
) -> list[Path]:
    excluded = set(exclude_names)
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.name not in excluded and "deviations" not in path.parts
    )


def _hash_file_hex(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _hash_text(text: str) -> str:
    return f"{SHA256_PREFIX}{sha256(text.encode('utf-8')).hexdigest()}"


def _strip_hash_prefix(value: str) -> str:
    if not value.startswith(SHA256_PREFIX):
        raise ValueError(f"Expected sha256: hash value, got {value!r}")
    return value.removeprefix(SHA256_PREFIX)


def _yaml_to_string(data: dict[str, Any]) -> str:
    return cast(str, yaml.safe_dump(data, **_YAML_DUMP_KWARGS))


def _write_deviation(deviations_dir: Path, deviation: DeviationRecord) -> Path:
    deviations_dir.mkdir(parents=True, exist_ok=True)
    out_path = deviations_dir / f"intake-{_safe_filename(deviation.artifact_id)}.yaml"
    out_path.write_text(_yaml_to_string(deviation.to_dict()), encoding="utf-8")
    return out_path


def _safe_filename(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "-" for char in value) or "unknown"


__all__ = [
    "BundleContents",
    "BundleIntegrityError",
    "DeviationRecord",
    "DeviationType",
    "load_bundle",
]
