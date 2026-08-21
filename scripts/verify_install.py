"""Build a wheel and exercise its installed CLI outside the source checkout.

Two checks run by default:

1. v0.2 surface — install the wheel, run ``claim-audit --help``,
   ``claim-audit demo --engine v0.2-lexical``, and ``claim-audit audit-bundle``;
   assert output files exist. The lexical engine is explicit so this venv does
   not need torch.
2. v1 surface — install the wheel with the ``[v1]`` extra in a separate clean
   venv, import the inference modules, and run ``claim-audit demo`` (the
   ordinary path). The written report must name ``v1-retrieve-entail``.

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
            _verify_ui_surface(wheel, temp_dir)

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
        [
            str(claim_audit),
            "demo",
            "--engine",
            "v0.2-lexical",
            "--out-dir",
            str(temp_dir / "demo"),
        ],
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
    """Install the wheel with [v1] and run a real ``claim-audit demo``."""
    venv_dir = temp_dir / "venv-v1"
    venv.EnvBuilder(with_pip=True).create(venv_dir)
    python = venv_dir / "bin" / "python"
    claim_audit = venv_dir / "bin" / "claim-audit"
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
                "assert rules == ['cal-rules-v1.13.0.yaml'], rules"
            ),
        ],
        cwd=temp_dir,
    )
    # The v1 feature extractor needs the spaCy pipeline, which is a post-install
    # step rather than a wheel dependency (see pyproject `[v1]` and the README
    # install block). `demo` defaults to the v1 engine, so a verifier that skips
    # this step is checking an install no README instruction produces.
    _install_spacy_model(python, temp_dir)

    demo_dir = temp_dir / "demo-v1"
    _run(
        [str(claim_audit), "demo", "--out-dir", str(demo_dir)],
        cwd=temp_dir,
    )
    markdown = _require(demo_dir / "ai-research-note.cli.md").read_text(encoding="utf-8")
    payload = _require(demo_dir / "ai-research-note.cli.json").read_text(encoding="utf-8")
    if "v1-retrieve-entail" not in markdown or "v1-retrieve-entail" not in payload:
        raise RuntimeError("Installed [v1] claim-audit demo did not name engine v1-retrieve-entail")
    if "cal-rules-v1.13.0" not in markdown or "cal-rules-v1.13.0" not in payload:
        raise RuntimeError("Installed [v1] claim-audit demo did not name rules cal-rules-v1.13.0")
    print("v1 surface verified (claim-audit demo named v1-retrieve-entail).")


def _verify_ui_surface(wheel: Path, temp_dir: Path) -> None:
    """Install the wheel with [ui] only and import both UI modules.

    ``claim_audit_lab.ui.server`` is stdlib-only; ``claim_audit_lab.ui.app`` is the
    FastAPI variant and pulls the whole inference stack through the extra. Both are
    packaged, so the extra is what makes the FastAPI module importable after a clean
    install — which is the thing worth checking, and it is checked with only [ui]
    declared so a missing dependency cannot be masked by [v1] being present too.
    """
    venv_dir = temp_dir / "venv-ui"
    venv.EnvBuilder(with_pip=True).create(venv_dir)
    python = venv_dir / "bin" / "python"
    _run([str(python), "-m", "pip", "install", f"{wheel}[ui]"], cwd=temp_dir)
    _run(
        [
            str(python),
            "-c",
            (
                "import claim_audit_lab.ui.server as server; "
                "import claim_audit_lab.ui.app as app; "
                "assert hasattr(app, 'app'), 'ui.app does not expose an ASGI app'; "
                "import sys; "
                "assert server.__name__ in sys.modules"
            ),
        ],
        cwd=temp_dir,
    )
    print("ui surface verified (ui.server and ui.app import from a [ui]-only install).")


def _install_spacy_model(python: Path, cwd: Path) -> None:
    """Put ``en_core_web_sm`` into the verification venv, offline where possible.

    Prefers the copy already resolved in this interpreter's environment by copying
    the package and its dist-info into the fresh venv, so a machine that has run
    the suite once can verify an install without network. Falls back to the
    documented ``python -m spacy download en_core_web_sm``.
    """
    source = _local_spacy_model()
    if source is not None:
        package, dist_info = source
        target = Path(
            subprocess.run(
                [str(python), "-c", "import site; print(site.getsitepackages()[0])"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )
        shutil.copytree(package, target / package.name, dirs_exist_ok=True)
        shutil.copytree(dist_info, target / dist_info.name, dirs_exist_ok=True)
        return
    _run([str(python), "-m", "spacy", "download", "en_core_web_sm"], cwd=cwd)


def _local_spacy_model() -> tuple[Path, Path] | None:
    """Locate an installed ``en_core_web_sm`` package plus its dist-info, if present."""
    try:
        import en_core_web_sm  # noqa: PLC0415
    except ImportError:
        return None
    package = Path(en_core_web_sm.__file__).resolve().parent
    dist_infos = sorted(package.parent.glob("en_core_web_sm-*.dist-info"))
    if not dist_infos:
        return None
    return package, dist_infos[-1]


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


def _require(path: Path) -> Path:
    if not path.is_file():
        raise RuntimeError(f"Expected installed-artifact output is missing: {path}")
    return path


if __name__ == "__main__":
    main()
