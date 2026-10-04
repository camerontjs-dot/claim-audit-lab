"""Decisive original-input comparison. Refuses to overwrite an existing run."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_CANDIDATE = Path(__file__).resolve().parent
_REPO = _CANDIDATE.parents[1]
sys.path.insert(0, str(_CANDIDATE))

from adapter import synthesize
from codec import canonical, digest, parse_envelope
from dispatch import LANES, dispatch
from lossy import lossy_envelope

_OUT = _CANDIDATE / "execution" / "decisive-01"
_SEEDS = _REPO / "research" / "cal_v1_independent_judges_rc0_20261004" / "SEMANTIC_CASES.json"
_EXPECTATIONS = _CANDIDATE / "EXPECTATIONS.json"
_POLICY = _CANDIDATE / "POLICY.json"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(_REPO), *args], text=True).strip()


def _source_dirty() -> str:
    """Receipts under execution/ are outputs. Any other dirt means the freeze moved."""
    allowed = "research/cal_v1_independent_judges_candidate_rc0_20261004/execution/"
    bad: list[str] = []
    for line in _git("status", "--porcelain", "-uall").splitlines():
        if not line.strip():
            continue
        path = line[3:]
        if line.startswith("?? ") and (path == allowed[:-1] or path.startswith(allowed)):
            continue
        bad.append(line)
    return "\n".join(bad)


def _require_freeze() -> str:
    if _source_dirty():
        raise SystemExit("candidate tree is dirty; freeze the candidate before decisive execution")
    return _git("rev-parse", "HEAD")


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _scope_preserved(claim: str, interpretation: dict[str, Any] | None) -> bool:
    if not interpretation:
        return False
    years = re.findall(r"\b20\d{2}\b", claim)
    if years and interpretation.get("time") not in years:
        return False
    if " in all age groups" in claim and interpretation.get("quantifier") != "all":
        return False
    if " in some age groups" in claim and interpretation.get("quantifier") != "some":
        return False
    for token in ("COPD", "asthma"):
        if token in claim and token.casefold() not in str(interpretation.get("property", "")).casefold():
            return False
    return True


def _not_run(process_id: str, role: str) -> dict[str, Any]:
    return {
        "process_id": process_id,
        "execution": "not_run",
        "applicability": "not_run",
        "role": role,
        "conclusion": "not_run",
        "reason": "routed_kernel_baseline_does_not_dispatch_this_lane",
    }


def _kernel_arm(raw: bytes, traced: list[dict[str, Any]]) -> dict[str, Any]:
    kernel = traced[0]["receipt"]
    mapped = {
        "supports": "supported",
        "refutes": "contradicted",
        "unresolved": "not_checkable",
        "not_applicable": "not_checkable",
    }.get(kernel.get("conclusion"), "not_checkable")
    receipts = [_not_run(lane, role) for lane, role in LANES if lane != "kernel_legacy"]
    receipts.append(kernel)
    return {"conclusion": mapped, "receipts": receipts, "traces": traced, "synthesis": None}


def _synthesized(raw: bytes, traced: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    receipts = [item["receipt"] for item in traced]
    for item in traced:
        if item["state"] != "completed" or item["receipt"].get("forbidden_read"):
            return {
                "conclusion": "not_checkable",
                "receipts": receipts,
                "traces": traced,
                "synthesis": None,
                "dispatch_failure": item["process_id"],
            }
    return {
        "conclusion": synthesize(raw, receipts, policy)["conclusion"],
        "receipts": receipts,
        "traces": traced,
        "synthesis": synthesize(raw, receipts, policy),
    }


def _cause(arm: dict[str, Any], process_id: str) -> str | None:
    for receipt in arm["receipts"]:
        if receipt.get("process_id") == process_id:
            return receipt.get("abstention_cause")
    return None


def _relation(arm: dict[str, Any]) -> dict[str, Any]:
    for receipt in arm["receipts"]:
        if receipt.get("process_id") == "original_relation":
            return receipt
    return {}


def _check(case: dict[str, Any], expected: dict[str, Any], arms: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    original = case["claim"]
    for arm_name in ("arm_a", "arm_b", "arm_c"):
        if arms[arm_name]["conclusion"] != expected[arm_name]:
            failures.append(f"{arm_name} conclusion {arms[arm_name]['conclusion']} != {expected[arm_name]}")
    if expected.get("arm_a_cause") and _cause(arms["arm_a"], "kernel_legacy") != expected["arm_a_cause"]:
        failures.append("arm A cause")
    if expected.get("arm_c_cause") and _cause(arms["arm_c"], "original_relation") != expected["arm_c_cause"]:
        failures.append("arm C cause")
    relation = _relation(arms["arm_c"])
    preserved = _scope_preserved(original, relation.get("claim_interpretation"))
    if expected.get("scope_gain"):
        if arms["arm_c"]["conclusion"] != "supported" or not preserved:
            failures.append("scope-preserving gain missing")
        if _cause(arms["arm_c"], "kernel_legacy") != "authoring_refusal":
            failures.append("scope gain was not outside frozen authoring")
        required = expected.get("required_scope", {})
        interpretation = relation.get("claim_interpretation") or {}
        for key, value in required.items():
            if interpretation.get(key) != value:
                failures.append(f"required scope {key}")
    if "arm_b_scope_preserved" in expected:
        b_relation = _relation(arms["arm_b"])
        b_preserved = _scope_preserved(original, b_relation.get("claim_interpretation"))
        if b_preserved != expected["arm_b_scope_preserved"]:
            failures.append("arm B scope preservation")
    return failures


def _public_trace(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "process_id": item["process_id"],
        "state": item["state"],
        "supplied_sha256": item["supplied_sha256"],
        "returncode": item["returncode"],
        "binding_ok": item["binding_ok"],
        "open_classes": item.get("open_classes", []),
        "forbidden_read": item.get("forbidden_read", False),
        "stderr": item.get("stderr") or "",
    }


def main() -> int:
    if _OUT.exists():
        raise SystemExit("decisive-01 already exists; refusing to overwrite the first run")
    head = _require_freeze()
    expectations = json.loads(_EXPECTATIONS.read_text(encoding="utf-8"))
    seeds_bytes = _SEEDS.read_bytes()
    if digest(seeds_bytes) != expectations["seeds_sha256"]:
        raise SystemExit("semantic seed hash does not match the preregistered expectation")
    policy = json.loads(_POLICY.read_text(encoding="utf-8"))
    if policy["calibration_status"] != "UNCALIBRATED_TOY_RATIONALS_NOT_PRODUCTION_WEIGHTS":
        raise SystemExit("policy calibration label changed")
    seeds = json.loads(seeds_bytes)
    by_id = {item["id"]: item for item in expectations["cases"]}
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.mkdir(parents=False)
    rows = []
    first_failure = None
    for case in seeds["cases"]:
        raw = canonical({"claim": case["claim"], "evidence": case["evidence"]})
        lossy_raw, loss_record = lossy_envelope(parse_envelope(raw))
        arm_a_trace = dispatch(raw, order=("kernel_legacy",), trace_open=True)
        arm_b_trace = dispatch(lossy_raw, trace_open=True)
        arm_c_trace = dispatch(raw, trace_open=True)
        arms = {
            "arm_a": _kernel_arm(raw, arm_a_trace),
            "arm_b": _synthesized(lossy_raw, arm_b_trace, policy),
            "arm_c": _synthesized(raw, arm_c_trace, policy),
        }
        failures = _check(case, by_id[case["id"]], arms)
        if failures and first_failure is None:
            first_failure = {"id": case["id"], "failures": failures}
        relation = _relation(arms["arm_c"])
        summary = {
            "id": case["id"],
            "dimension": case["dimension"],
            "expected_seed": case["expected"],
            "arm_a": arms["arm_a"]["conclusion"],
            "arm_b": arms["arm_b"]["conclusion"],
            "arm_c": arms["arm_c"]["conclusion"],
            "arm_c_cause": _cause(arms["arm_c"], "original_relation"),
            "scope_preserved_against_original": _scope_preserved(
                case["claim"], relation.get("claim_interpretation")
            ),
            "lossy_bytes_differ": digest(lossy_raw) != digest(raw),
            "lossy_transform": loss_record["transform_id"],
            "attribution": (
                "confounded_instruments_and_routing"
                if arms["arm_a"]["conclusion"] != arms["arm_c"]["conclusion"]
                else "no_conclusion_difference"
            ),
            "loss_contrast": (
                "same_instruments_different_input"
                if arms["arm_b"]["conclusion"] != arms["arm_c"]["conclusion"]
                else "no_conclusion_difference"
            ),
            "failures": failures,
            "passed": not failures,
        }
        case_dir = _OUT / "cases" / case["id"]
        _write(case_dir / "summary.json", summary)
        for arm_name, arm in arms.items():
            _write(case_dir / arm_name / "result.json", {"conclusion": arm["conclusion"], "synthesis": arm["synthesis"]})
            for item in arm["traces"]:
                _write(case_dir / arm_name / f"{item['process_id']}.json", item["receipt"])
                _write(case_dir / arm_name / f"{item['process_id']}.trace.json", _public_trace(item))
        rows.append(summary)
    wrong = [row["id"] for row in rows if not row["passed"]]
    gains = [
        row["id"]
        for row in rows
        if row["passed"] and row["arm_c"] == "supported" and row["arm_a"] == "not_checkable" and row["scope_preserved_against_original"]
    ]
    report = {
        "evidence_class": "EXPOSED_SYNTHETIC_SEED_DISCRIMINATOR_NOT_NATURAL_USEFULNESS",
        "candidate_commit": head,
        "preparation_commit": "4f3eaadf39e2f8f9229298ce2e39dbeee8eea102",
        "control_commit": "64b6c7702696c851057c1cf0b2c105b1c81db543",
        "semantic_implementation": "caa0048f8f511ec3c4aa1ce713766f2219a04bc1",
        "models_used": False,
        "weights": policy["calibration_status"],
        "policy_sha256": digest(canonical(policy)),
        "expectations_sha256": digest(_EXPECTATIONS.read_bytes()),
        "case_count": len(rows),
        "failed_ids": wrong,
        "scope_preserving_gains_outside_authoring": gains,
        "first_failure": first_failure,
        "passed": not wrong and bool(gains),
        "cases": rows,
    }
    _write(_OUT / "REPORT.json", report)
    print(json.dumps({"passed": report["passed"], "failed_ids": wrong, "gains": gains}, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
