"""Build a wheel and exercise its installed CLI outside the source checkout."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import venv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CB_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "cb" / "evidence-bundle-minimal"


def main() -> None:
    """Verify the user-facing wheel rather than the editable checkout."""
    with tempfile.TemporaryDirectory(prefix="claim-audit-install-") as temp:
        temp_dir = Path(temp)
        dist_dir = temp_dir / "dist"
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

        venv_dir = temp_dir / "venv"
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
        print(f"Installed wheel verified: {wheel.name}")


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
