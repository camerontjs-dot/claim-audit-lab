"""B16 apparatus round trip against Evidence Bundler's real synthetic fixture."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from claim_audit_lab.cli import app
from claim_audit_lab.contracts.bundle_loader import BundleContents, load_bundle
from claim_audit_lab.v1 import AuditedBundleContents, load_audited
from tests.v1.testing.bundles import opt_bundle_into_v1

CAL_WORKBENCH = Path(__file__).resolve().parents[2]
runner = CliRunner()


def _evidence_bundler_workbench() -> Path:
    configured = os.environ.get("EVIDENCE_BUNDLER_WORKBENCH")
    candidate = (
        Path(configured).expanduser()
        if configured
        else CAL_WORKBENCH.parent.parent / "evidence-bundler" / "workbench"
    )
    if not candidate.is_dir():
        pytest.skip(
            "Evidence Bundler sibling not found; set EVIDENCE_BUNDLER_WORKBENCH "
            "to run the apparatus integration test"
        )
    return candidate.resolve()


def _build_evidence_bundle(tmp_path: Path) -> tuple[Path, Path]:
    workbench = _evidence_bundler_workbench()
    fixture = workbench / "tests" / "fixtures" / "scaffold-run-minimal"
    python = workbench / ".venv" / "bin" / "python"
    if not python.is_file():
        pytest.skip(f"Evidence Bundler test interpreter not found under {workbench}")

    bundle_dir = tmp_path / "evidence-bundle-b16"
    result = subprocess.run(
        [
            str(python),
            "-m",
            "evidence_bundler.cli",
            "build-fixture-bundle",
            str(fixture),
            "--output",
            str(bundle_dir),
        ],
        cwd=workbench,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return fixture, opt_bundle_into_v1(bundle_dir)


def test_evidence_bundler_to_cal_v1_round_trip(tmp_path: Path) -> None:
    fixture, bundle_dir = _build_evidence_bundle(tmp_path)

    # The fixture contains no expected-outputs artifact. B16 therefore locks the
    # deterministic expectation grounded in its claim + directly stating passage:
    # C-B `supported`, v1 `supported`, and no not-checkable reason sub-label.
    assert not list(fixture.rglob("*expected*"))

    out_dir = tmp_path / "cal-output"
    result = runner.invoke(
        app,
        [
            "audit-bundle",
            str(bundle_dir),
            "--out-dir",
            str(out_dir),
            "--audit-run-id",
            "b16-round-trip",
            "--audited-at",
            "2026-06-29T00:00:00Z",
        ],
    )
    assert result.exit_code == 0, result.output

    audited_dir = out_dir / f"{bundle_dir.name}-audited"
    cb_loaded = load_bundle(audited_dir, deviations_dir=tmp_path / "cb-deviations")
    v1_loaded = load_audited(audited_dir, deviations_dir=tmp_path / "v1-deviations")

    assert isinstance(cb_loaded, BundleContents)
    assert isinstance(v1_loaded, AuditedBundleContents)
    assert cb_loaded.claims[0].claim_id == "clm-001"
    assert cb_loaded.claims[0].audit.audit_support_verdict == "supported"

    trace = v1_loaded.traces["clm-001"]
    assert trace.verdict.support_verdict == "supported"
    assert trace.verdict.support_verdict_reason is None
    assert trace.support_signal.label == "entail"
