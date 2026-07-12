"""Build a wheel and exercise its installed CLI outside the source checkout.

Two checks run by default:

1. v0.2 surface — install the wheel, run ``claim-audit --help``, ``claim-audit demo``,
   and ``claim-audit audit-bundle``; assert output files exist.
2. v1 surface — install the wheel with the ``[v1]`` extra in a separate clean venv
   and import ``claim_audit_lab.v1``. Verifies the v1 inference-stack declaration
   in ``pyproject.toml`` resolves cleanly and the v1 modules load without error.

Skip the heavier v1 check with ``--skip-v1`` for a fast turnaround during work that
does not touch the v1 dependency surface.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CB_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "cb" / "evidence-bundle-minimal"


def main() -> None:
    """Verify the user-facing wheel rather than the editable checkout."""
    skip_v1 = "--skip-v1" in sys.argv[1:]
    with tempfile.TemporaryDirectory(prefix="claim-audit-install-") as temp:
        temp_dir = Path(temp)
        dist_dir = temp_dir / "dist"
        _clean_build_tree()
        _run(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--outdir",
                str(dist_dir),
            ],
            cwd=PROJECT_ROOT,
        )
        wheel = _single_wheel(dist_dir)

        _verify_v02_surface(wheel, temp_dir)
        if not skip_v1:
            _verify_v1_surface(wheel, temp_dir)

        print(f"Installed wheel verified: {wheel.name}")


def _verify_v02_surface(wheel: Path, temp_dir: Path) -> None:
    """Install the wheel and exercise the v0.2 CLI surface."""
    venv_dir = temp_dir / "venv-v02"
    venv.EnvBuilder(with_pip=True).create(venv_dir)
    python = venv_dir / "bin" / "python"
    claim_audit = venv_dir / "bin" / "claim-audit"
    _run([str(python), "-m", "pip", "install", str(wheel)], cwd=temp_dir)

    _run([str(claim_audit), "--help"], cwd=temp_dir)
    _run(
        [str(claim_audit), "demo", "--out-dir", str(temp_dir / "demo")],
        cwd=temp_dir,
    )
    _run(
        [
            str(claim_audit),
            "audit-bundle",
            str(CB_FIXTURE),
            "--out-dir",
            str(temp_dir / "bundle"),
        ],
        cwd=temp_dir,
    )

    _require(temp_dir / "demo" / "ai-research-note.cli.md")
    _require(temp_dir / "bundle" / f"{CB_FIXTURE.name}-audited" / "bundle_manifest.yaml")
    _require(temp_dir / "bundle" / f"{CB_FIXTURE.name}-audit-report.md")
    print("v0.2 surface verified.")


def _verify_v1_surface(wheel: Path, temp_dir: Path) -> None:
    """Install the wheel with [v1] in a clean venv and import v1 modules."""
    venv_dir = temp_dir / "venv-v1"
    venv.EnvBuilder(with_pip=True).create(venv_dir)
    python = venv_dir / "bin" / "python"
    _run([str(python), "-m", "pip", "install", f"{wheel}[v1]"], cwd=temp_dir)
    _run(
        [
            str(python),
            "-c",
            (
                "from importlib.resources import files; "
                "from claim_audit_lab.v1 import features, models, protocols, "
                "load_default_audit_config; "
                "from claim_audit_lab.v1.impl import "
                "BiEncoderRetriever, DeBERTaEntailer, "
                "MaxEntailmentAggregator, VerdictRules; "
                "cfg = load_default_audit_config(); "
                "assert cfg.retriever.hf_revision_sha == "
                "'1110a243fdf4706b3f48f1d95db1a4f5529b4d41', cfg.retriever; "
                "assert cfg.entailer.hf_revision_sha == "
                "'6f5cf0a2b59cabb106aca4c287eed12e357e90eb', cfg.entailer; "
                "rules = sorted(p.name for p in "
                "files('claim_audit_lab.v1.configs').iterdir() "
                "if p.name.startswith('cal-rules-')); "
                "assert rules == ['cal-rules-v1.5.0.yaml'], rules"
            ),
        ],
        cwd=temp_dir,
    )
    print("v1 surface verified.")


def _clean_build_tree() -> None:
    """Remove setuptools' reusable build tree before creating the verification wheel.

    ``python -m build`` reuses ``build/lib`` when it exists, including package-data
    files deleted from ``src`` since the prior build. A verifier that calls its wheel
    clean must remove that generated cache first or it can silently ship retired rules.
    """
    shutil.rmtree(PROJECT_ROOT / "build", ignore_errors=True)


def _run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def _single_wheel(dist_dir: Path) -> Path:
    wheels = sorted(dist_dir.glob("*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected one wheel in {dist_dir}, found {len(wheels)}")
    return wheels[0]


def _require(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"Expected installed-artifact output is missing: {path}")


if __name__ == "__main__":
    main()
