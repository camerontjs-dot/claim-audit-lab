"""Write audited claim files to an output copy of the bundle.

Design constraint
-----------------
The received C-B bundle is hash-sealed.  Mutating ``claims/{claim_id}.yaml``
in-place would break the original ``bundle_hash`` and ``SHA256SUMS``.
This writer therefore ALWAYS produces a fresh output copy in ``out_dir``;
the source bundle at ``source_bundle_dir`` is never touched.

If in-place mutation is ever desired (e.g. for downstream tooling), it must
be an explicit, documented, separately invoked operation — never a default.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

from claim_audit_lab.contracts.audit_flags import compute_flags
from claim_audit_lab.contracts.cb_models import CBAuditConfig, CBClaim
from claim_audit_lab.contracts.serialization import (
    PENDING_HASH,
    compute_bundle_tree_hash,
    hash_file_hex,
    iter_handoff_files,
    yaml_to_string,
)
from claim_audit_lab.models import ClaimAssessment


def write_audited_bundle(
    source_bundle_dir: Path,
    out_dir: Path,
    cb_claims: list[CBClaim],
    assessments: dict[str, ClaimAssessment],
    *,
    audit_run_id: str,
    audited_at_utc: str,
    audit_config: CBAuditConfig | None = None,
) -> Path:
    """Copy ``source_bundle_dir`` to ``out_dir`` and populate audit fields.

    Parameters
    ----------
    source_bundle_dir:
        The original, unmodified C-B bundle directory.
    out_dir:
        Destination for the audited copy.  Recreated from scratch if it
        already exists, so the output is always a clean copy.
    cb_claims:
        All C-B claims (including retrieval_seeds, which are left untouched).
    assessments:
        ``{claim_id: ClaimAssessment}`` mapping from the CAL auditor.
        Claims absent from this dict (e.g. retrieval_seeds that were not
        adapted) are copied as-is without audit population.
    audit_run_id:
        Stable ID for this CAL audit run.
    audited_at_utc:
        ISO-like UTC timestamp recorded into each audited claim.
    audit_config:
        Optional locked C-B audit config, used for false-caution thresholding.
    """
    _require_non_blank("audit_run_id", audit_run_id)
    _require_non_blank("audited_at_utc", audited_at_utc)

    source_bundle_dir = source_bundle_dir.resolve()
    out_dir = out_dir.resolve()
    _guard_output_location(source_bundle_dir, out_dir)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(source_bundle_dir, out_dir)

    claims_out_dir = out_dir / "claims"

    for cb_claim in cb_claims:
        assessment = assessments.get(cb_claim.claim_id)
        if assessment is None:
            continue  # retrieval_seed or unadapted claim — leave file as-is

        claim_path = claims_out_dir / f"{cb_claim.claim_id}.yaml"
        if not claim_path.exists():
            raise FileNotFoundError(f"Missing copied C-B claim file: {claim_path}")

        flags = compute_flags(
            cb_claim,
            assessment,
            false_caution_detection=_false_caution_detection(audit_config),
            false_caution_threshold=_false_caution_threshold(audit_config),
        )

        raw = _load_yaml(claim_path)
        raw.setdefault("audit", {})
        raw["audit"]["audit_run_id"] = audit_run_id
        raw["audit"]["audited_at_utc"] = audited_at_utc
        raw["audit"]["audit_support_verdict"] = assessment.support_label
        raw["audit"]["audit_confidence"] = flags.audit_confidence
        raw["audit"]["audit_notes"] = assessment.explanation or "No explanation recorded."
        raw["audit"]["false_caution_flag"] = flags.false_caution_flag
        raw["audit"]["deviation_flag"] = flags.deviation_flag
        raw["audit"]["deviation_notes"] = flags.deviation_notes

        claim_path.write_text(yaml_to_string(raw), encoding="utf-8")

    _reseal_output_bundle(out_dir)
    return out_dir


def _require_non_blank(field_name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must be non-blank")


def _guard_output_location(source_bundle_dir: Path, out_dir: Path) -> None:
    if out_dir == source_bundle_dir or out_dir.is_relative_to(source_bundle_dir):
        raise ValueError("out_dir must not be the source bundle or inside it")


def _false_caution_detection(audit_config: CBAuditConfig | None) -> bool:
    if audit_config is None:
        return True
    return audit_config.rule_policies.false_caution_detection


def _false_caution_threshold(audit_config: CBAuditConfig | None) -> float:
    if audit_config is None:
        return 0.85
    return audit_config.rule_policies.false_caution_threshold


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return raw


def _reseal_output_bundle(out_dir: Path) -> None:
    manifest_path = out_dir / "bundle_manifest.yaml"
    manifest = _load_yaml(manifest_path)
    bundle = manifest.get("bundle")
    if not isinstance(bundle, dict):
        raise ValueError("bundle_manifest.yaml missing bundle mapping")

    bundle["bundle_hash"] = PENDING_HASH
    manifest_path.write_text(yaml_to_string(manifest), encoding="utf-8")

    bundle["bundle_hash"] = compute_bundle_tree_hash(out_dir)
    manifest_path.write_text(yaml_to_string(manifest), encoding="utf-8")
    _write_sha256sums(out_dir)


def _write_sha256sums(out_dir: Path) -> None:
    lines = [
        f"{hash_file_hex(path)}  {path.relative_to(out_dir).as_posix()}"
        for path in iter_handoff_files(out_dir)
    ]
    (out_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


__all__ = ["write_audited_bundle"]
