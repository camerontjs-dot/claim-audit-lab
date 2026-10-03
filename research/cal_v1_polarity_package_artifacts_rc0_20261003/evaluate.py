from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any

SUBJECT = "64b6c7702696c851057c1cf0b2c105b1c81db543"
SEMANTIC = "caa0048f8f511ec3c4aa1ce713766f2219a04bc1"
FAMILIES = ["strict_comparison", "direct_event_order"]

SMOKE = r"""
import json
from claim_audit_lab.production_v1 import SEMANTIC_IMPLEMENTATION_SHA, SUPPORTED_SEMANTIC_FAMILIES
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)
from claim_audit_lab.production_v1.semantic.relations import _derive_comparison
from claim_audit_lab.production_v1.targeting import author_target

def context(claim):
    target = author_target("package-smoke", claim)
    proposition = TypedProposition.create(
        "package-smoke",
        SemanticFamily.STRICT_COMPARISON,
        target["proposition"]["fields"],
        text_sha256=target["proposition"]["text_sha256"],
    )
    passage = AdmittedPassage.create(
        "p0", "s0", claim, "sha256:" + "ab" * 32
    )
    world = EvidenceWorld.create(
        "1.2.0",
        "package-smoke",
        "sha256:" + "cd" * 32,
        (passage,),
        {"contract_b_factual_context_state": "present", "observation": {"scope": "package-smoke"}},
    )
    return AuditContext(claim, proposition, world)

negative_more = {
    "left": "alpha",
    "relation": "MORE_THAN",
    "right": "beta",
    "assertion_polarity": "negative",
}
higher = context("Alpha had a higher rate than Beta.")
lower = context("Alpha had a lower rate than Beta.")
print(json.dumps({
    "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
    "supported_semantic_families": list(SUPPORTED_SEMANTIC_FAMILIES),
    "negative_more_vs_higher": _derive_comparison(higher, negative_more).value,
    "negative_more_vs_lower": _derive_comparison(lower, negative_more).value,
}, sort_keys=True))
"""


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def run(command: list[str], *, cwd: Path) -> bytes:
    proc = subprocess.run(command, cwd=cwd, check=False, capture_output=True)
    if proc.returncode != 0:
        sys.stderr.buffer.write(proc.stdout)
        sys.stderr.buffer.write(proc.stderr)
        raise RuntimeError(f"command failed ({proc.returncode}): {command}")
    return proc.stdout


def smoke(python: Path, *, cwd: Path) -> dict[str, Any]:
    raw = run([str(python), "-c", SMOKE], cwd=cwd)
    value = json.loads(raw.decode("utf-8").strip())
    assert value["semantic_implementation_sha"] == SEMANTIC
    assert value["supported_semantic_families"] == FAMILIES
    assert value["negative_more_vs_higher"] == "REFUTES"
    assert value["negative_more_vs_lower"] == "UNRESOLVED"
    return value


def verify_wheel(wheel: Path, source_root: Path) -> int:
    checked = 0
    production = source_root / "src/claim_audit_lab/production_v1"
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        for path in production.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".json"}:
                relative = str(path.relative_to(source_root / "src"))
                assert relative in names, relative
                assert archive.read(relative) == path.read_bytes(), relative
                checked += 1
    return checked


def verify_sdist(sdist: Path, source_root: Path) -> int:
    checked = 0
    production = source_root / "src/claim_audit_lab/production_v1"
    with tarfile.open(sdist) as archive:
        members = archive.getmembers()
        for path in production.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".json"}:
                relative = str(path.relative_to(source_root))
                matches = [m for m in members if m.name.endswith("/" + relative)]
                assert len(matches) == 1, relative
                handle = archive.extractfile(matches[0])
                assert handle is not None
                assert handle.read() == path.read_bytes(), relative
                checked += 1
    return checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    out = Path(args.out).resolve()
    if out.exists():
        raise RuntimeError(f"refusing to overwrite output: {out}")
    out.mkdir(parents=True)

    product_diff = git(
        root,
        "diff",
        "--name-only",
        SUBJECT,
        "HEAD",
        "--",
        "src/claim_audit_lab",
        "pyproject.toml",
        "uv.lock",
        "MANIFEST.in",
    )
    assert product_diff == "", product_diff

    source_observation = smoke(Path(sys.executable), cwd=root)

    dist = out / "dist"
    run([sys.executable, "-m", "build", "--outdir", str(dist)], cwd=root)
    wheels = list(dist.glob("*.whl"))
    sdists = list(dist.glob("*.tar.gz"))
    assert len(wheels) == 1 and len(sdists) == 1
    wheel, sdist = wheels[0], sdists[0]

    wheel_members = verify_wheel(wheel, root)
    sdist_members = verify_sdist(sdist, root)
    assert wheel_members == sdist_members and wheel_members > 0

    observations: dict[str, dict[str, Any]] = {"source": source_observation}
    with tempfile.TemporaryDirectory(prefix="cal-package-qual-") as raw:
        temp = Path(raw)
        for kind, artifact in (("wheel", wheel), ("sdist", sdist)):
            venv = temp / kind
            run([sys.executable, "-m", "venv", str(venv)], cwd=root)
            python = venv / "bin/python"
            run([str(python), "-m", "pip", "install", str(artifact)], cwd=root)
            observations[kind] = smoke(python, cwd=root)

    assert observations["source"] == observations["wheel"] == observations["sdist"]

    receipt = {
        "schema": "cal-v1-polarity-successor-package-artifacts-rc0",
        "issue": 200,
        "product_subject": SUBJECT,
        "semantic_implementation_sha": SEMANTIC,
        "production_members_checked": wheel_members,
        "wheel": {"name": wheel.name, "sha256": sha256(wheel.read_bytes())},
        "sdist": {"name": sdist.name, "sha256": sha256(sdist.read_bytes())},
        "observations": observations,
        "status": "QUALIFIED_POLARITY_SUCCESSOR_PACKAGE_ARTIFACTS",
    }
    (out / "receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
