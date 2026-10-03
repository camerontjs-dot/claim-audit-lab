"""Qualify the CAL V1 strict-comparison polarity successor for bounded convergence.

Issue #192 is the preregistered task authority. This runner does not modify the
frozen #190 discriminator or the scientific polarity implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import traceback
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SUBJECT = "86b60022420a006358fde38b20a204ffe4df1a96"
PREDECESSOR = "6bb0d60f3e2286123f56de5657de4e97d6374c63"
SCIENTIFIC_IMPLEMENTATION = "caa0048f8f511ec3c4aa1ce713766f2219a04bc1"
FROZEN_EVALUATOR = "68d77aa621079d74be947de90c171a426e1b6890"
POLARITY_PATH = "research/cal_v1_strict_comparison_polarity_rc0_20261002/decisive"
EXTERNAL = {
    "frozen-cal": "e24e405f5336ee024674f39dba97255bb58a2dd9",
    "evidence-bundler": "4e1f6fe00e7c350b28f52bfea14f1f8988847884",
    "contract-c": "c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec",
    "rc2": "b42c827acb0a9fe65353354d709add0e27bab307",
    "resolver": "1d33e0612befcf8016816197c90c062373796df9",
}


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


class Qualification:
    def __init__(self, root: Path, external: Path, out: Path) -> None:
        self.root = root
        self.external = external
        self.out = out
        out.mkdir(parents=True, exist_ok=False)
        self.env = dict(os.environ)
        self.env.pop("PYTHONPATH", None)
        self.env.update(
            FROZEN_CAL_ROOT=str(external / "frozen-cal"),
            CAL_EB_INTEGRATION_REPO=str(external / "evidence-bundler"),
            EB_ROOT=str(external / "evidence-bundler"),
            CONTRACT_C_ROOT=str(external / "contract-c"),
            RC2_ROOT=str(external / "rc2"),
            RESOLVER_ROOT=str(external / "resolver"),
        )
        self.receipt: dict[str, Any] = {
            "schema": "cal-v1-polarity-successor-qualification-rc0",
            "issue": 192,
            "status": "RUNNING",
            "started_at": datetime.now(UTC).isoformat(),
            "head": git(root, "rev-parse", "HEAD"),
            "tree": git(root, "rev-parse", "HEAD^{tree}"),
            "qualification_subject": SUBJECT,
            "scientific_implementation": SCIENTIFIC_IMPLEMENTATION,
            "predecessor": PREDECESSOR,
            "steps": [],
        }
        self.save()

    def save(self) -> None:
        (self.out / "receipt.json").write_text(
            json.dumps(self.receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def run(
        self,
        name: str,
        command: list[str],
        *,
        expected: int = 0,
        env: dict[str, str] | None = None,
    ) -> bytes:
        index = len(self.receipt["steps"]) + 1
        stdout_path = self.out / f"{index:03d}-{name}.stdout.log"
        stderr_path = self.out / f"{index:03d}-{name}.stderr.log"
        started = datetime.now(UTC).isoformat()
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            proc = subprocess.run(
                command,
                cwd=self.root,
                env=env or self.env,
                stdout=stdout,
                stderr=stderr,
            )
        stdout_raw = stdout_path.read_bytes()
        stderr_raw = stderr_path.read_bytes()
        step = {
            "name": name,
            "command": command,
            "started_at": started,
            "exit_code": proc.returncode,
            "expected_exit": expected,
            "stdout_sha256": sha256(stdout_raw),
            "stderr_sha256": sha256(stderr_raw),
        }
        self.receipt["steps"].append(step)
        self.save()
        print(f"{name}: exit {proc.returncode} expected {expected}", flush=True)
        if proc.returncode != expected:
            raise RuntimeError(f"{name} exited {proc.returncode}, expected {expected}")
        return stdout_raw

    def identities(self) -> None:
        assert git(self.root, "status", "--porcelain") == "", "qualification checkout must be clean"
        assert git(self.root, "merge-base", SUBJECT, "HEAD") == SUBJECT
        protected_diff = git(
            self.root,
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
        assert protected_diff == "", f"qualification branch changed protected product files: {protected_diff}"

        semantic_paths = (
            "src/claim_audit_lab/production_v1/semantic/measurements.py",
            "src/claim_audit_lab/production_v1/semantic/authority.py",
            "src/claim_audit_lab/production_v1/semantic/relations.py",
        )
        semantic_blobs: dict[str, str] = {}
        for path in semantic_paths:
            actual = git(self.root, "hash-object", path)
            expected = git(self.root, "rev-parse", f"{SCIENTIFIC_IMPLEMENTATION}:{path}")
            assert actual == expected, path
            semantic_blobs[path] = actual

        protected_paths = (
            "src/claim_audit_lab/production_v1/targeting.py",
            "src/claim_audit_lab/production_v1/target_cli.py",
            "src/claim_audit_lab/production_v1/semantic/decomposition.py",
            "src/claim_audit_lab/production_v1/parent_bound.py",
            "src/claim_audit_lab/production_v1/schema/target.schema.json",
            "src/claim_audit_lab/production_v1/schema/result-v2.schema.json",
            "src/claim_audit_lab/production_v1/schema/manifest-v2.schema.json",
        )
        protected_blobs: dict[str, str] = {}
        for path in protected_paths:
            actual = git(self.root, "hash-object", path)
            expected = git(self.root, "rev-parse", f"{PREDECESSOR}:{path}")
            assert actual == expected, path
            protected_blobs[path] = actual

        evaluator_paths = (
            f"{POLARITY_PATH}/CASES.json",
            f"{POLARITY_PATH}/evaluate.py",
        )
        evaluator_blobs: dict[str, str] = {}
        for path in evaluator_paths:
            actual = git(self.root, "hash-object", path)
            expected = git(self.root, "rev-parse", f"{FROZEN_EVALUATOR}:{path}")
            assert actual == expected, path
            evaluator_blobs[path] = actual

        for name, expected in EXTERNAL.items():
            path = self.external / name
            assert git(path, "rev-parse", "HEAD") == expected, name
            assert git(path, "status", "--porcelain") == "", name

        from claim_audit_lab.production_v1 import SEMANTIC_IMPLEMENTATION_SHA

        assert SEMANTIC_IMPLEMENTATION_SHA == SCIENTIFIC_IMPLEMENTATION

        self.receipt["identity"] = {
            "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
            "semantic_blobs": semantic_blobs,
            "protected_predecessor_blobs": protected_blobs,
            "frozen_evaluator_blobs": evaluator_blobs,
            "external_authorities": EXTERNAL,
            "protected_product_diff_from_subject": [],
        }
        self.save()

    def polarity_replay(self) -> None:
        destination = self.out / "polarity-replay"
        raw = self.run(
            "frozen-polarity-discriminator",
            [
                sys.executable,
                f"{POLARITY_PATH}/evaluate.py",
                "--cases",
                f"{POLARITY_PATH}/CASES.json",
                "--out",
                str(destination),
            ],
        )
        result_path = destination / "decisive-result.json"
        result = json.loads(result_path.read_text(encoding="utf-8"))
        assert result["mechanical_disposition"] == "SUPPORTED_FOR_POLARITY_SUCCESSOR_QUALIFICATION"
        assert result["case_count"] == 33
        assert result["matched_count"] == 33
        assert result["failed_count"] == 0
        assert result["apparatus_errors"] == []
        boundary_mismatches = [
            mismatch
            for row in result["results"]
            for mismatch in row.get("mismatches", [])
            if mismatch.get("field") == "polarity_boundary"
        ]
        assert boundary_mismatches == []
        self.receipt["polarity_replay"] = {
            "stdout_sha256": sha256(raw),
            "result_sha256": sha256(result_path.read_bytes()),
            "matched": 33,
            "polarity_boundary_mismatches": 0,
        }
        self.save()

    def inherited_qualifications(self) -> None:
        target_result = self.out / "target-authoring-conformance.json"
        target_env = dict(
            self.env,
            QUALIFICATION_RESULT=str(target_result),
        )
        self.run(
            "target-authoring-conformance",
            [
                sys.executable,
                "tests/qualification/cal_v1_target_authoring_conformance_qualification.py",
            ],
            env=target_env,
        )
        target = json.loads(target_result.read_text(encoding="utf-8"))
        assert target["result"] == "PASS"
        assert target["weak_control_discrimination"]["existing_structural_validator_accepted"] == 8
        assert target["weak_control_discrimination"]["new_conformer_rejected"] == 8
        assert target["out_of_aperture_authoring_refusals"] == 5

        parent_result = self.out / "parent-contract-c.json"
        parent_env = dict(
            self.env,
            QUALIFICATION_RESULT=str(parent_result),
        )
        self.run(
            "parent-composition",
            [
                sys.executable,
                "tests/qualification/cal_v1_slice2_parent_contract_c_qualification.py",
            ],
            env=parent_env,
        )
        parent = json.loads(parent_result.read_text(encoding="utf-8"))
        assert parent["disposition"] == "QUALIFIED_FOR_CONTROLLED_LOCAL_PIPELINE_PARENT_BOUND_RUNS"
        assert parent["failures"] == []

        self.receipt["inherited_qualifications"] = {
            "target_authoring_conformance_sha256": sha256(target_result.read_bytes()),
            "parent_contract_c_sha256": sha256(parent_result.read_bytes()),
            "target_weak_controls": 8,
            "target_refusals": 5,
            "parent_failures": [],
        }
        self.save()

    def package_qualification(self) -> None:
        dist = self.out / "dist"
        self.run(
            "build-wheel-sdist",
            [sys.executable, "-m", "build", "--outdir", str(dist)],
        )
        wheels = list(dist.glob("*.whl"))
        sdists = list(dist.glob("*.tar.gz"))
        assert len(wheels) == 1 and len(sdists) == 1
        wheel, sdist = wheels[0], sdists[0]

        production = self.root / "src/claim_audit_lab/production_v1"
        with zipfile.ZipFile(wheel) as archive:
            for path in production.rglob("*"):
                if path.is_file() and path.suffix in {".py", ".json"}:
                    relative = str(path.relative_to(self.root / "src"))
                    assert archive.read(relative) == path.read_bytes(), relative
        with tarfile.open(sdist) as archive:
            for path in production.rglob("*"):
                if path.is_file() and path.suffix in {".py", ".json"}:
                    relative = str(path.relative_to(self.root))
                    member = next(m for m in archive.getmembers() if m.name.endswith("/" + relative))
                    handle = archive.extractfile(member)
                    assert handle is not None and handle.read() == path.read_bytes(), relative

        installed: dict[str, Any] = {}
        for kind, artifact in (("wheel", wheel), ("sdist", sdist)):
            venv = self.out / f"venv-{kind}"
            self.run(f"{kind}-venv", [sys.executable, "-m", "venv", str(venv)])
            python = venv / "bin/python"
            self.run(
                f"{kind}-install",
                [str(python), "-m", "pip", "install", str(artifact)],
            )
            raw = self.run(
                f"{kind}-inspect",
                [
                    str(python),
                    "-c",
                    (
                        "import json;"
                        "from claim_audit_lab.production_v1.execution import inspect_record;"
                        "print(json.dumps(inspect_record(),sort_keys=True))"
                    ),
                ],
            )
            record = json.loads(raw.decode().strip())
            assert record["semantic_implementation_sha"] == SCIENTIFIC_IMPLEMENTATION
            assert record["supported_semantic_families"] == [
                "strict_comparison",
                "direct_event_order",
            ]
            installed[kind] = record

        self.receipt["packages"] = {
            "wheel": {"name": wheel.name, "sha256": sha256(wheel.read_bytes())},
            "sdist": {"name": sdist.name, "sha256": sha256(sdist.read_bytes())},
            "installed_inspect": installed,
        }
        self.save()

    def regression(self) -> None:
        for name, command in (
            ("pytest-full", [sys.executable, "-m", "pytest", "-q"]),
            ("ruff-check", [sys.executable, "-m", "ruff", "check", "src", "tests"]),
            ("ruff-format", [sys.executable, "-m", "ruff", "format", "--check", "src"]),
            ("mypy", [sys.executable, "-m", "mypy"]),
        ):
            self.run(name, command)

    def execute(self) -> None:
        assert sys.version_info[:2] == (3, 11), "qualification requires Python 3.11"
        self.identities()
        self.polarity_replay()
        self.inherited_qualifications()
        self.package_qualification()
        self.regression()
        self.identities()
        self.receipt.update(
            status="QUALIFIED_POLARITY_SUCCESSOR_FOR_V1_CONVERGENCE",
            finished_at=datetime.now(UTC).isoformat(),
            downstream_equivalence="NOT_RUN",
            pressure_replay="NOT_RUN",
            release="NOT_RUN",
        )
        self.save()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    runner = Qualification(
        Path(__file__).resolve().parents[2],
        args.external.resolve(),
        args.out.resolve(),
    )
    try:
        runner.execute()
    except BaseException:
        failure = traceback.format_exc()
        (runner.out / "first-failure.txt").write_text(failure, encoding="utf-8")
        runner.receipt.update(
            status="FAILED_CLASSIFICATION_REQUIRED",
            first_failure_sha256=sha256(failure.encode()),
            finished_at=datetime.now(UTC).isoformat(),
        )
        runner.save()
        raise


if __name__ == "__main__":
    main()
