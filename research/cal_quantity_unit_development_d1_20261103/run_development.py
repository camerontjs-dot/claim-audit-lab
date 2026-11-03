"""Reproduce exposed development evidence; never opens source/calibration gold."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
REL = HERE.relative_to(REPO).as_posix()
S1 = "research/cal_v1_quantity_unit_source_evaluator_s1_20261013"
RC3 = "research/cal_v1_quantity_unit_boundary_rc3_20261004"
RC2 = "research/cal_v1_quantity_comparator_binding_rc2_20261004/candidate"
PINS = {
    f"{RC2}/quantity_binding.py": "05b1e7616cac8401656c8e777a6395f88d705a8c",
    f"{RC2}/candidate_adapter.py": "559306c69b56ad1f9725193a6188f2e986cf3a3b",
    f"{RC3}/DEVELOPMENT_CASES.json": "ac467ee96b879612ad686caa741afcfdcc4f7c00",
    f"{RC3}/unit_contract_tests.py": "3cd87c389af76fd46225324050ce132279a83800",
    f"{S1}/receipt_contract_tests_v2.py": "85ddcabfa24d371d9905ed98c8eba7f6dd84aa6e",
    f"{S1}/receipt_basis_tests_v3.py": "6ff72d0576e3366ed94efa9a1113ad2c681d0d78",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def run(args: list[str]) -> dict:
    result = subprocess.run([sys.executable, *args], cwd=REPO, capture_output=True, check=False)
    out, err = result.stdout.decode(), result.stderr.decode()
    try:
        parsed = json.loads(out)
    except ValueError:
        parsed = None
    return {
        "command": ["python3", *args], "exit_code": result.returncode,
        "stdout_sha256": sha(result.stdout), "stderr_sha256": sha(result.stderr),
        "stdout": out.replace(str(REPO), "$CHECKOUT"),
        "stderr": err.replace(str(REPO), "$CHECKOUT"),
        "public_path_normalization": "checkout prefix only; raw stream hashes retained",
        "result": parsed,
    }


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("refuse to overwrite an existing development receipt")
    pinned = {}
    for path, expected in PINS.items():
        data = (REPO / path).read_bytes()
        actual = git_blob(data)
        if actual != expected:
            raise SystemExit("pinned input mismatch: " + path)
        pinned[path] = {"git_blob": actual, "sha256": sha(data)}
    commands = {}
    for label, evaluator in (("v1", f"{RC3}/unit_contract_tests.py"), ("v2", f"{S1}/receipt_contract_tests_v2.py"), ("v3", f"{S1}/receipt_basis_tests_v3.py")):
        commands[label + "_selftest"] = run([evaluator, "--selftest"])
        commands[label + "_candidate"] = run([evaluator, "--adapter", f"{REL}/candidate_adapter.py"])
    reviewer = HERE / "test_review_controls.py"
    if reviewer.exists():
        commands["review_controls"] = run([f"{REL}/test_review_controls.py"])
    baseline = load(REPO / RC2 / "candidate_adapter.py", "d1_exposed_rc2_baseline")
    candidate = load(HERE / "candidate_adapter.py", "d1_candidate_comparison")
    cases = json.loads((REPO / RC3 / "DEVELOPMENT_CASES.json").read_text())["cases"]
    comparisons, receipts = {}, {}
    for label, module in (("baseline", baseline), ("candidate", candidate)):
        rows = []
        for case in cases:
            result = module.analyze(case["claim"], case["evidence"])
            rows.append({"id": case["id"], "expected_relation": case["expected_relation"], "actual_relation": result["relation"]})
            if label == "candidate":
                receipts[case["id"]] = result
        comparisons[label] = {
            "cases": len(rows),
            "exact_relation_match": sum(x["actual_relation"] == x["expected_relation"] for x in rows),
            "false_support": sum(x["actual_relation"] == "supports" and x["expected_relation"] != "supports" for x in rows),
            "false_refutation": sum(x["actual_relation"] == "refutes" and x["expected_relation"] != "refutes" for x in rows),
            "missed_warranted_decisions": sum(x["expected_relation"] in {"supports", "refutes"} and x["actual_relation"] not in {"supports", "refutes"} for x in rows),
            "rows": rows,
        }
    candidate_files = {p.name: sha(p.read_bytes()) for p in sorted(HERE.glob("*.py"))}
    passed = all(c["exit_code"] == 0 for c in commands.values()) and "review_controls" in commands
    report = {
        "schema": "cal-quantity-unit-d1-exposed-development-v1",
        "evidence_class": "INFORMED_EXPOSED_DEVELOPMENT_ONLY",
        "scientific_qualification": "NOT_RUN", "runtime_qualification": "NOT_RUN",
        "fresh_generalization": "NOT_ESTABLISHED", "blind_implementation": False,
        "python": platform.python_version(), "implementation": platform.python_implementation(),
        "pinned_inputs": pinned, "candidate_file_sha256": candidate_files,
        "commands": commands, "relation_comparison": comparisons,
        "review_controls_present": "review_controls" in commands,
        "all_development_checks_passed": passed,
    }
    args.out.mkdir(parents=True)
    (args.out / "RESULT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (args.out / "CANDIDATE_RECEIPTS.json").write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"all_development_checks_passed": passed, "commands": {k: v["exit_code"] for k, v in commands.items()}, "relations": {k: {a: b for a, b in v.items() if a != "rows"} for k, v in comparisons.items()}}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
