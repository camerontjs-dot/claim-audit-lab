"""C-B bundle preparation helpers shared by v1 integration tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from shutil import copytree, rmtree
from typing import Any

from claim_audit_lab.contracts.serialization import (
    hash_audit_config_file,
    hash_text,
    load_yaml_mapping,
    reseal_bundle,
    yaml_to_string,
)

_MINIMAL_FIXTURE = Path(__file__).parents[2] / "fixtures" / "cb" / "evidence-bundle-minimal"


def opt_bundle_into_v1(bundle_dir: Path) -> Path:
    """Select the v1 pipeline and correctly reseal a writable C-B bundle."""
    audit_config_path = bundle_dir / "audit_config.yaml"
    audit_config = load_yaml_mapping(audit_config_path)
    audit_config["pipeline"] = "v1-retrieve-entail"
    audit_config_path.write_text(yaml_to_string(audit_config), encoding="utf-8")

    config_hash = hash_audit_config_file(audit_config_path)
    audit_config["config_hash"] = config_hash
    audit_config_path.write_text(yaml_to_string(audit_config), encoding="utf-8")

    manifest_path = bundle_dir / "bundle_manifest.yaml"
    manifest = load_yaml_mapping(manifest_path)
    manifest["audit_config_hash"] = config_hash
    manifest_path.write_text(yaml_to_string(manifest), encoding="utf-8")

    reseal_bundle(bundle_dir)
    return bundle_dir


@dataclass(frozen=True)
class CalibrationCase:
    """One synthetic calibration claim and its candidate passages."""

    claim_id: str
    claim_text: str
    passages: tuple[str, ...]


# Five base contents whose committed inference goldens (tests/v1/fixtures/traces/
# inference/) fix CAL's real verdict — encryption→supported, logging→contradicted,
# uptime→contradicted, opinion→not_checkable, no_evidence→not_checkable. Each is a
# (claim_text, passages) pair; the calibration packet below reuses them.
_Content = tuple[str, tuple[str, ...]]

_ENCRYPTION: _Content = (
    "Customer data is encrypted at rest.",
    (
        "All stored customer data is encrypted at rest using AES-256.",
        "The service maintained 99.95 percent uptime over the last quarter.",
        "The local weather forecast predicts rain on Thursday afternoon.",
    ),
)
_LOGGING: _Content = (
    "The platform does not log administrator actions.",
    (
        "Every administrator action is recorded in an immutable audit log.",
        "The platform logs all administrator actions for compliance.",
        "This recipe calls for two cups of flour and a pinch of salt.",
    ),
)
_UPTIME: _Content = (
    "The service meets 99 percent uptime.",
    (
        "The service meets 95 percent uptime under normal load.",
        "Availability is monitored continuously by the operations team.",
        "The local weather forecast predicts rain on Thursday afternoon.",
    ),
)
_OPINION: _Content = (
    "In my opinion the dashboard is the best feature.",
    (
        "The dashboard shows live operational metrics.",
        "Users can configure the dashboard layout.",
        "This recipe calls for two cups of flour and a pinch of salt.",
    ),
)
_NO_EVIDENCE: _Content = (
    "The compound reduces infection risk in clinical trials.",
    (
        "This recipe calls for two cups of flour and a pinch of salt.",
        "The local weather forecast predicts rain on Thursday afternoon.",
        "The cafeteria menu changes every week.",
    ),
)

# Phase-4 Unit-2 calibration packet: 12 claims = 4 conditions x 3, 2 models. It
# deliberately REUSES the five base contents above under twelve claim_ids so every
# CAL verdict stays deterministic and hand-checkable without inventing new claims
# or re-deriving goldens. The honest cost: CAL's emitted columns are confined to
# {supported, contradicted, not_checkable} (no unsupported / partially_supported on
# the CAL side). The hand-authored gold (calibration-synthetic/gold.yaml) spans all
# five degrees, so the 5x5 confusion + on-scale weighted/AC2 path are still fully
# exercised. The per-condition / per-model layout lives in gold.yaml; this builder
# only fixes claim content. See DECISIONS.md § 2026-06-30 (Phase 4 Unit 2).
CALIBRATION_CASES: tuple[CalibrationCase, ...] = (
    CalibrationCase("syn-01", *_ENCRYPTION),
    CalibrationCase("syn-02", *_LOGGING),
    CalibrationCase("syn-03", *_UPTIME),
    CalibrationCase("syn-04", *_ENCRYPTION),
    CalibrationCase("syn-05", *_OPINION),
    CalibrationCase("syn-06", *_NO_EVIDENCE),
    CalibrationCase("syn-07", *_ENCRYPTION),
    CalibrationCase("syn-08", *_LOGGING),
    CalibrationCase("syn-09", *_UPTIME),
    CalibrationCase("syn-10", *_OPINION),
    CalibrationCase("syn-11", *_ENCRYPTION),
    CalibrationCase("syn-12", *_LOGGING),
)


def build_calibration_packet(dest: Path) -> Path:
    """Build the 12-bundle v1 calibration packet under ``dest`` from the cases.

    Each :class:`CalibrationCase` becomes its own single-claim C-B bundle (copied
    from the minimal fixture, content swapped, opted into v1, resealed). Because the
    cases reuse the five committed-golden contents, each bundle's real verdict
    reproduces the ``inf-01..05`` spread deterministically. Returns ``dest``.
    """
    dest.mkdir(parents=True, exist_ok=True)
    for case in CALIBRATION_CASES:
        bundle_dir = dest / f"bundle-{case.claim_id}"
        if bundle_dir.exists():
            rmtree(bundle_dir)
        copytree(_MINIMAL_FIXTURE, bundle_dir)
        _rewrite_single_claim_bundle(bundle_dir, case)
        opt_bundle_into_v1(bundle_dir)
    return dest


def _rewrite_single_claim_bundle(bundle_dir: Path, case: CalibrationCase) -> None:
    """Swap the minimal fixture's single claim + passage for ``case`` content."""
    claims_dir = bundle_dir / "claims"
    passages_dir = bundle_dir / "evidence" / "src-001" / "passages"
    claim_tmpl = load_yaml_mapping(claims_dir / "clm-001.yaml")
    passage_tmpl = load_yaml_mapping(passages_dir / "pass-001.yaml")
    ref_tmpl: dict[str, Any] = dict(claim_tmpl["evidence_passages"][0])

    for path in passages_dir.glob("*.yaml"):
        path.unlink()
    embedded: list[dict[str, Any]] = []
    for index, text in enumerate(case.passages, start=1):
        passage_id = f"pass-{index:03d}"
        passage_hash = hash_text(text)
        doc = dict(passage_tmpl)
        doc.update(
            passage_id=passage_id,
            passage_text=text,
            passage_hash=passage_hash,
            cited_by_claims=[case.claim_id],
            char_start=0,
            char_end=len(text),
        )
        (passages_dir / f"{passage_id}.yaml").write_text(yaml_to_string(doc), encoding="utf-8")
        ref = dict(ref_tmpl)
        ref.update(
            passage_id=passage_id,
            source_id="src-001",
            passage_text=text,
            passage_hash=passage_hash,
            char_start=0,
            char_end=len(text),
        )
        embedded.append(ref)

    for path in claims_dir.glob("*.yaml"):
        path.unlink()
    claim = dict(claim_tmpl)
    claim.update(
        claim_id=case.claim_id,
        claim_text=case.claim_text,
        evidence_passages=embedded,
        counterevidence_passages=[],
    )
    (claims_dir / f"{case.claim_id}.yaml").write_text(yaml_to_string(claim), encoding="utf-8")

    manifest_path = bundle_dir / "bundle_manifest.yaml"
    manifest = load_yaml_mapping(manifest_path)
    bundle = manifest["bundle"]
    bundle.update(
        total_claims_in_source=1,
        claims_included=1,
        claims_excluded=0,
        total_evidence_passages=len(case.passages),
        exclusion_rationale="Synthetic calibration fixture; single extracted_claim.",
    )
    manifest["transformations"][0]["claims_affected"] = [case.claim_id]
    manifest_path.write_text(yaml_to_string(manifest), encoding="utf-8")


__all__ = [
    "CALIBRATION_CASES",
    "CalibrationCase",
    "build_calibration_packet",
    "opt_bundle_into_v1",
]
