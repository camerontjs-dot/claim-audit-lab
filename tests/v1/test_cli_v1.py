"""End-to-end CLI tests for the v1 ``audit-bundle`` routing path (B15).

A v1-selecting C-B bundle is built by adding ``pipeline: v1-retrieve-entail`` to
the minimal fixture's ``audit_config.yaml`` and resealing every hash. These tests
load the real retriever + entailer, so they are slower than the writeback unit
tests; model weights are process-cached, so the two-run reproducibility check is
cheap after the first load.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from shutil import copytree

from typer.testing import CliRunner

from claim_audit_lab.cli import app
from claim_audit_lab.contracts.bundle_loader import load_bundle
from tests.v1.testing.bundles import opt_bundle_into_v1

CB_FIXTURE = Path(__file__).parents[1] / "fixtures" / "cb" / "evidence-bundle-minimal"
runner = CliRunner()


def _make_v1_bundle(dest: Path) -> Path:
    """Copy the minimal fixture, opt it into v1, and reseal all hashes."""
    copytree(CB_FIXTURE, dest)
    return opt_bundle_into_v1(dest)


def _tree_snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_v1_bundle_fixture_is_well_sealed(tmp_path: Path) -> None:
    """Sanity: the hand-built v1 bundle passes the fail-closed loader unchanged."""
    bundle = _make_v1_bundle(tmp_path / "evidence-bundle-minimal")
    contents = load_bundle(bundle, deviations_dir=tmp_path / "dev")
    assert contents.audit_config.pipeline == "v1-retrieve-entail"


def test_audit_bundle_routes_to_v1_and_writes_trace(tmp_path: Path) -> None:
    bundle = _make_v1_bundle(tmp_path / "evidence-bundle-minimal")
    out_dir = tmp_path / "out"

    result = runner.invoke(app, ["audit-bundle", str(bundle), "--out-dir", str(out_dir)])

    assert result.exit_code == 0, result.output
    assert "v1 retrieve-entail" in result.stdout
    audited = out_dir / f"{bundle.name}-audited"
    assert (audited / "claims" / "clm-001.audit-trace.json").exists()
    # no markdown report on the v1 path — the trace is the report
    assert not (out_dir / f"{bundle.name}-audit-report.md").exists()

    reloaded = load_bundle(audited, deviations_dir=tmp_path / "out-dev")
    audit = reloaded.claims[0].audit
    assert audit.audit_run_id is not None
    assert audit.audit_support_verdict is not None


def test_v1_audit_bundle_is_byte_identical_with_pinned_metadata(tmp_path: Path) -> None:
    bundle = _make_v1_bundle(tmp_path / "evidence-bundle-minimal")
    roots = [tmp_path / "first", tmp_path / "second"]

    for out_dir in roots:
        result = runner.invoke(
            app,
            [
                "audit-bundle",
                str(bundle),
                "--out-dir",
                str(out_dir),
                "--audit-run-id",
                "cal-v1-pinned",
                "--audited-at",
                "2026-06-29T00:00:00Z",
            ],
        )
        assert result.exit_code == 0, result.output

    first = roots[0] / f"{bundle.name}-audited"
    second = roots[1] / f"{bundle.name}-audited"
    assert _tree_snapshot(first) == _tree_snapshot(second)
