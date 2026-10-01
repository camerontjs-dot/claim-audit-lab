"""Replay issue #185's preserved controls against a clean convergence candidate.

This runner executes real CAL/EB/Contract C paths and repository gates. It preserves
the first failure and never repairs source, evaluators, inputs, or expected results.
External checkouts and a prepared Python 3.11 all-extras environment are required.
"""

from __future__ import annotations

import argparse
import configparser
import hashlib
import importlib.util
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

BASE = "32275a239b68af383a56bca843e28cbc1e343976"
SLICE2 = "ddaf94551e38663920593cab89f9c60d43c1555f"
TARGET = "76b7c4dee6369cc6494486eb115a096e9da370b0"
SEMANTIC = "847cc970642bb648dc994b929c2053b5c9d4648c"
COMPOSER = "268d0dc4dd22ddde3848141d62b7d719e48d374d"
AUTHORITIES = {
    "frozen-cal": "e24e405f5336ee024674f39dba97255bb58a2dd9",
    "slice2": SLICE2,
    "evidence-bundler": "4e1f6fe00e7c350b28f52bfea14f1f8988847884",
    "contract-c": "c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec",
    "rc2": "b42c827acb0a9fe65353354d709add0e27bab307",
    "resolver": "1d33e0612befcf8016816197c90c062373796df9",
}


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def snapshot(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): digest(p.read_bytes())
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


class Qualification:
    def __init__(self, root: Path, external: Path, out: Path) -> None:
        self.root, self.external, self.out = root, external, out
        out.mkdir(parents=True, exist_ok=False)
        self.env = dict(os.environ)
        self.env.pop("PYTHONPATH", None)
        self.env.pop("PYTHONOPTIMIZE", None)
        self.env.update(
            FROZEN_CAL_ROOT=str(external / "frozen-cal"),
            CAL_EB_INTEGRATION_REPO=str(external / "evidence-bundler"),
            EB_ROOT=str(external / "evidence-bundler"),
            CONTRACT_C_ROOT=str(external / "contract-c"),
            RC2_ROOT=str(external / "rc2"),
            RESOLVER_ROOT=str(external / "resolver"),
        )
        self.receipt: dict[str, Any] = {
            "schema": "cal-v1-convergence-qualification-rc0",
            "started_at": datetime.now(UTC).isoformat(),
            "head": git(root, "rev-parse", "HEAD"),
            "tree": git(root, "rev-parse", "HEAD^{tree}"),
            "base": BASE,
            "status": "RUNNING",
            "candidate_metadata_version": "0.6.0",
            "release_version_decided": False,
            "steps": [],
        }
        self.save()

    def save(self) -> None:
        (self.out / "receipt.json").write_text(
            json.dumps(self.receipt, indent=2, sort_keys=True) + "\n"
        )

    def run(
        self, name: str, command: list[str], *, expected: int = 0, env: dict[str, str] | None = None
    ) -> bytes:
        log = self.out / f"{len(self.receipt['steps']) + 1:03d}-{name}.log"
        step: dict[str, Any] = {
            "name": name,
            "command": command,
            "started_at": datetime.now(UTC).isoformat(),
            "expected_exit": expected,
            "log": log.name,
        }
        stderr_log = log.with_suffix(".stderr.log")
        with log.open("wb") as stdout_stream, stderr_log.open("wb") as stderr_stream:
            result = subprocess.run(
                command,
                cwd=self.root,
                env=env or self.env,
                stdout=stdout_stream,
                stderr=stderr_stream,
            )
        raw = log.read_bytes()
        step.update(
            exit_code=result.returncode,
            log_sha256=digest(raw),
            stderr_log=stderr_log.name,
            stderr_sha256=digest(stderr_log.read_bytes()),
        )
        self.receipt["steps"].append(step)
        self.save()
        print(f"{name}: exit {result.returncode} (expected {expected})", flush=True)
        if result.returncode != expected:
            raise RuntimeError(f"first failed command: {name}; see {log.name}")
        return raw

    def identities(self) -> None:
        assert git(self.root, "status", "--porcelain") == "", "candidate must be clean"
        assert git(self.root, "merge-base", BASE, "HEAD") == BASE
        manifest_path = self.root / "CANDIDATE.json"
        manifest = json.loads(manifest_path.read_bytes())
        source = manifest["source_commit"]
        assert git(self.root, "rev-parse", f"{source}^{{tree}}") == manifest["source_tree"]
        assert git(self.root, "merge-base", source, "HEAD") == source
        assert git(self.root, "diff", "--name-only", source, "HEAD") == "CANDIDATE.json"
        assert manifest["state"] == "frozen_for_qualification"
        self.receipt["candidate_manifest"] = {
            "sha256": digest(manifest_path.read_bytes()),
            "source_commit": source,
            "source_tree": manifest["source_tree"],
            "freeze_commit": self.receipt["head"],
        }
        observed = {}
        for name, expected in AUTHORITIES.items():
            path = self.external / name
            assert git(path, "rev-parse", "HEAD") == expected, name
            assert git(path, "status", "--porcelain") == "", name
            observed[name] = {"commit": expected, "tree": git(path, "rev-parse", "HEAD^{tree}")}
        prefix = "src/claim_audit_lab/production_v1/"
        files = git(self.root, "ls-tree", "-r", "--name-only", SLICE2, "--", prefix).splitlines()
        files += [prefix + "targeting.py", prefix + "target_cli.py"]
        blobs = {}
        for path in files:
            source = TARGET if path.endswith(("/targeting.py", "/target_cli.py")) else SLICE2
            expected = git(self.root, "rev-parse", f"{source}:{path}")
            actual = git(self.root, "hash-object", path)
            assert actual == expected, path
            blobs[path] = {"blob": actual, "predecessor": source}
        assert blobs[prefix + "semantic/decomposition.py"]["blob"] == COMPOSER
        for path in ("pyproject.toml", "MANIFEST.in", "uv.lock", "src/claim_audit_lab/__init__.py"):
            assert git(self.root, "hash-object", path) == git(
                self.root, "rev-parse", f"{SLICE2}:{path}"
            ), path
        for source, name in (
            (SLICE2, "cal_v1_slice2_parent_contract_c_qualification.py"),
            (TARGET, "cal_v1_target_authoring_conformance_qualification.py"),
        ):
            assert git(self.root, "hash-object", f"tests/qualification/{name}") == git(
                self.root, "rev-parse", f"{source}:tests/research/{name}"
            ), name
        traces = git(
            self.root, "diff", "--name-only", BASE, "HEAD", "--", "tests/v1/fixtures/traces"
        ).splitlines()
        assert len(traces) == 30
        for path in traces:
            original = subprocess.check_output(
                ["git", "-C", str(self.root), "show", f"{BASE}:{path}"]
            )
            assert original.count(b'"library_version": "0.5.0"') == 1
            assert (self.root / path).read_bytes() == original.replace(
                b'"library_version": "0.5.0"', b'"library_version": "0.6.0"'
            ), path
        self.receipt["protected_identity"] = {
            "semantic_implementation": SEMANTIC,
            "decomposition_blob": COMPOSER,
            "exact_production_blobs": blobs,
            "trace_version_only_substitutions": len(traces),
            "external_authorities": observed,
            "decisive_evaluator_bytes_unchanged": True,
        }
        self.save()

    def frozen_tests(self) -> None:
        folder = self.out / "frozen-tests"
        folder.mkdir()
        tests = []
        hashes = {}
        for name in (
            "test_contract_b_integration_candidate.py",
            "test_contract_b_run_surface.py",
            "test_decomposition_composer_rc0.py",
        ):
            source = f"tests/production/{name}"
            raw = subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(self.root),
                    "show",
                    f"7cf0d2e50562ec4ce4082d1e1c058a11025b1a48:{source}",
                ]
            )
            path = folder / name
            path.write_bytes(raw)
            tests.append(str(path))
            hashes[source] = digest(raw)
        self.receipt["frozen_test_inputs"] = hashes
        self.run("frozen-contract-b-and-composer", [sys.executable, "-m", "pytest", "-q", *tests])

    def distribution(self) -> tuple[Path, Path]:
        dist = self.out / "dist"
        self.run("wheel-sdist-build", [sys.executable, "-m", "build", "--outdir", str(dist)])
        wheels, sdists = list(dist.glob("*.whl")), list(dist.glob("*.tar.gz"))
        assert len(wheels) == len(sdists) == 1
        wheel, sdist = wheels[0], sdists[0]
        production = self.root / "src/claim_audit_lab/production_v1"
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            for path in production.rglob("*"):
                if path.is_file() and path.suffix in (".py", ".json"):
                    relative = str(path.relative_to(self.root / "src"))
                    assert archive.read(relative) == path.read_bytes(), relative
            config = configparser.ConfigParser()
            entry = next(n for n in names if n.endswith(".dist-info/entry_points.txt"))
            config.read_string(archive.read(entry).decode())
            assert config["console_scripts"]["claim-audit-v1"] == (
                "claim_audit_lab.production_v1.bundle_cli:app"
            )
            assert config["console_scripts"]["claim-audit-v1-parent"] == (
                "claim_audit_lab.production_v1.parent_cli:app"
            )
        with tarfile.open(sdist) as archive:
            for path in production.rglob("*"):
                if path.is_file() and path.suffix in (".py", ".json"):
                    relative = str(path.relative_to(self.root))
                    member = next(
                        m for m in archive.getmembers() if m.name.endswith("/" + relative)
                    )
                    handle = archive.extractfile(member)
                    assert handle is not None and handle.read() == path.read_bytes(), relative
        self.receipt["artifacts"] = {
            "wheel": {"name": wheel.name, "sha256": digest(wheel.read_bytes())},
            "sdist": {"name": sdist.name, "sha256": digest(sdist.read_bytes())},
        }
        for kind, artifact in (("wheel", wheel), ("sdist", sdist)):
            venv = self.out / f"clean-{kind}"
            self.run(f"{kind}-venv", [sys.executable, "-m", "venv", str(venv)])
            self.run(
                f"{kind}-install", [str(venv / "bin/python"), "-m", "pip", "install", str(artifact)]
            )
        return self.out / "clean-wheel/bin", self.out / "clean-sdist/bin"

    def installed_paths(self, wheel_bin: Path, sdist_bin: Path) -> None:
        os.environ["CAL_EB_INTEGRATION_REPO"] = self.env["CAL_EB_INTEGRATION_REPO"]
        sys.path.insert(0, str(self.external / "slice2/src"))
        from claim_audit_lab.production_v1.parent_bound import run_parent_bound_pipeline

        fixture = (
            self.external
            / "frozen-cal/tests/research/test_cal_v1_a2_eb_b_parent_integration_rc0.py"
        )
        spec = importlib.util.spec_from_file_location("convergence_frozen_fixture", fixture)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        rows = {}
        authority = [
            "--contract-c-root",
            str(self.external / "contract-c"),
            "--rc2-root",
            str(self.external / "rc2"),
            "--resolver-root",
            str(self.external / "resolver"),
        ]
        inspect = json.loads(
            self.run("installed-inspect", [str(wheel_bin / "claim-audit-v1"), "inspect", "--json"])
        )
        assert inspect["semantic_implementation_sha"] == SEMANTIC
        assert inspect["supported_semantic_families"] == ["strict_comparison", "direct_event_order"]
        for case in module.CASES:
            reference = module._execute_case(case, self.out / "predecessor-fixtures")
            fixture_root = self.out / "predecessor-fixtures" / case.case_id
            bundle = fixture_root / "eb/contract_b"
            contract_a = fixture_root / "contract-a.json"
            contract_a.write_text(json.dumps(reference["contract_a"], sort_keys=True) + "\n")
            targets = {child: fixture_root / f"{child}.target.json" for child in ("C1", "C2")}
            expected = fixture_root / "predecessor-parent"
            run_parent_bound_pipeline(
                contract_a_path=contract_a,
                bundle_dir=bundle,
                child_targets=targets,
                out_dir=expected,
                contract_c_root=self.external / "contract-c",
                rc2_root=self.external / "rc2",
                resolver_root=self.external / "resolver",
            )
            bindings = []
            for child in ("C1", "C2"):
                authored = fixture_root / f"{child}.installed-authored.json"
                self.run(
                    f"{case.case_id}-{child}-author",
                    [
                        str(wheel_bin / "python"),
                        "-m",
                        "claim_audit_lab.production_v1.target_cli",
                        "author",
                        str(bundle),
                        child,
                        "--out",
                        str(authored),
                    ],
                )
                assert authored.read_bytes() == targets[child].read_bytes()
                self.run(
                    f"{case.case_id}-{child}-conform",
                    [
                        str(wheel_bin / "python"),
                        "-m",
                        "claim_audit_lab.production_v1.target_cli",
                        "conform",
                        str(bundle),
                        str(authored),
                    ],
                )
                actual = fixture_root / f"{child}.installed-child"
                self.run(
                    f"{case.case_id}-{child}-run-bundle",
                    [
                        str(wheel_bin / "claim-audit-v1"),
                        "run-bundle",
                        str(bundle),
                        str(authored),
                        "--out-dir",
                        str(actual),
                    ],
                )
                assert snapshot(actual) == snapshot(fixture_root / f"{child}.cal")
                bindings += ["--target", f"{child}={authored}"]
            for repeat in (1, 2):
                actual = fixture_root / f"installed-parent-{repeat}"
                self.run(
                    f"{case.case_id}-parent-{repeat}",
                    [
                        str(wheel_bin / "claim-audit-v1-parent"),
                        "run",
                        str(contract_a),
                        str(bundle),
                        *bindings,
                        "--out-dir",
                        str(actual),
                        *authority,
                    ],
                )
                assert snapshot(actual) == snapshot(expected), case.case_id
            record = json.loads((expected / "parent-result.json").read_bytes())
            assert record["parent_conclusion"] == case.expected_parent.value
            rows[case.case_id] = {
                "parent": record["parent_conclusion"],
                "all_artifacts_identical_to_slice2": True,
                "installed_replay_identical": True,
            }
        bundle = self.out / "predecessor-fixtures/PIPE01/eb/contract_b"
        target = self.out / "predecessor-fixtures/PIPE01/C1.target.json"
        self.run(
            "sdist-conform",
            [
                str(sdist_bin / "python"),
                "-m",
                "claim_audit_lab.production_v1.target_cli",
                "conform",
                str(bundle),
                str(target),
            ],
        )
        self.run(
            "sdist-child",
            [
                str(sdist_bin / "claim-audit-v1"),
                "run-bundle",
                str(bundle),
                str(target),
                "--out-dir",
                str(self.out / "sdist-child"),
            ],
        )
        assert snapshot(self.out / "sdist-child") == snapshot(
            self.out / "predecessor-fixtures/PIPE01/C1.cal"
        )
        invalid = self.out / "invalid.target.json"
        invalid.write_bytes(b"{invalid json\n")
        for name, path in (("missing", self.out / "missing.target.json"), ("invalid", invalid)):
            self.run(
                f"{name}-target-conformance-refusal",
                [
                    str(wheel_bin / "python"),
                    "-m",
                    "claim_audit_lab.production_v1.target_cli",
                    "conform",
                    str(bundle),
                    str(path),
                ],
                expected=2,
            )
            destination = self.out / f"{name}-rejected-run"
            self.run(
                f"{name}-target-execution-refusal",
                [
                    str(wheel_bin / "claim-audit-v1"),
                    "run-bundle",
                    str(bundle),
                    str(path),
                    "--out-dir",
                    str(destination),
                ],
                expected=2,
            )
            assert not (destination / "result.json").exists()
        self.receipt["installed_paths"] = rows
        self.save()

    def execute(self) -> None:
        assert sys.version_info[:2] == (3, 11), "maintained qualification requires Python 3.11"
        self.identities()
        self.run(
            "target-unit-controls",
            [sys.executable, "-m", "pytest", "-q", "tests/test_production_v1_targeting.py"],
        )
        self.frozen_tests()
        for name, script in (
            ("target-seam", "cal_v1_target_authoring_conformance_qualification.py"),
            ("slice2-parent", "cal_v1_slice2_parent_contract_c_qualification.py"),
        ):
            env = dict(self.env, QUALIFICATION_RESULT=str(self.out / f"{name}.json"))
            self.run(
                name, [sys.executable, str(self.root / "tests/qualification" / script)], env=env
            )
            self.receipt[f"{name}_result_sha256"] = digest((self.out / f"{name}.json").read_bytes())
        self.installed_paths(*self.distribution())
        for name, command in (
            ("pytest-full", ["pytest", "-q"]),
            ("ruff-check", ["ruff", "check", "src", "tests"]),
            ("ruff-format", ["ruff", "format", "--check", "src"]),
            ("mypy-strict", ["mypy"]),
        ):
            self.run(name, [sys.executable, "-m", *command])
        self.identities()
        self.receipt.update(
            status="SUPPORTED_BOUNDED_CONVERGENCE_LOCAL",
            finished_at=datetime.now(UTC).isoformat(),
            fresh_blind_acceptance="NOT_RUN",
            release="NOT_RUN",
        )
        self.save()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    runner = Qualification(
        Path(__file__).resolve().parents[1], args.external.resolve(), args.out.resolve()
    )
    try:
        runner.execute()
    except BaseException:
        failure = traceback.format_exc()
        (runner.out / "first-failure.txt").write_text(failure)
        runner.receipt.update(
            status="FAILED_CLASSIFICATION_REQUIRED", first_failure_sha256=digest(failure.encode())
        )
        runner.save()
        raise


if __name__ == "__main__":
    main()
