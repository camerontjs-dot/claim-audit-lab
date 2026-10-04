"""One held-out run. Refuses to overwrite decisive-01 or a moved seal."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

_CANDIDATE = Path(__file__).resolve().parent
_ROOT = _CANDIDATE.parent
_REPO = _ROOT.parents[1]
sys.path.insert(0, str(_CANDIDATE))

from codec import canonical, digest  # noqa: E402
from evaluate import SUCCESSOR, evaluate_envelope  # noqa: E402

_OUT = _CANDIDATE / "execution" / "decisive-01"
_SEAL = _ROOT / "HELD_OUT_SEAL.json"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(_REPO), *args], text=True).strip()


def _source_dirty() -> str:
    allowed = "research/cal_v1_independent_judges_natural_rc1_20261004/candidate/execution/"
    bad: list[str] = []
    for line in _git("status", "--porcelain", "-uall").splitlines():
        if not line.strip():
            continue
        path = line[3:]
        if line.startswith("?? ") and (path == allowed[:-1] or path.startswith(allowed)):
            continue
        bad.append(line)
    return "\n".join(bad)


def _kind(conclusion: str, expected: str) -> str:
    deciding = {"supported", "contradicted"}
    if conclusion in deciding and conclusion != expected:
        return "false_support" if conclusion == "supported" else "false_refutation"
    if conclusion in deciding and conclusion == expected:
        return "correct_deciding"
    if conclusion == "not_checkable" and expected == "not_checkable":
        return "safe_abstention"
    if conclusion == "not_checkable":
        return "abstained"
    return "other"


def _years(text: str) -> list[str]:
    import re

    return re.findall(r"\b(?:19|20)\d{2}\b", text)


def _public(arm: dict[str, Any]) -> dict[str, Any]:
    synthesis = arm.get("synthesis") or {}
    return {
        "conclusion": arm.get("conclusion"),
        "blockers": synthesis.get("blockers", []),
        "scores": synthesis.get("scores"),
        "exclusions": synthesis.get("exclusions"),
        "authoring_status": arm.get("authoring_status"),
        "abstention_cause": arm.get("abstention_cause"),
        "router": arm.get("router"),
        "loss": arm.get("loss"),
        "dispatch_failure": arm.get("dispatch_failure"),
        "processes": [
            {
                "process_id": item["process_id"],
                "state": item["state"],
                "conclusion": item["receipt"].get("conclusion"),
                "applicability": item["receipt"].get("applicability"),
                "abstention_cause": item["receipt"].get("abstention_cause"),
                "execution": item["receipt"].get("execution"),
            }
            for item in arm.get("traces", [])
        ],
    }


def main() -> int:
    if _OUT.exists():
        raise SystemExit("decisive-01 already exists")
    if _source_dirty():
        raise SystemExit("candidate tree is dirty; freeze it before the held-out run")
    seal = json.loads(_SEAL.read_text(encoding="utf-8"))
    label_path = _ROOT / str(seal["relative_path"])
    raw_labels = label_path.read_bytes()
    if hashlib.sha256(raw_labels).hexdigest() != seal["sha256"]:
        raise SystemExit("held-out label seal does not match")
    policy = json.loads((_CANDIDATE / "POLICY.json").read_text(encoding="utf-8"))
    if policy["calibration_status"] != "CALIBRATED_ON_CALIBRATION_PARTITION_ONLY":
        raise SystemExit("policy is not the calibration-locked policy")
    labels = json.loads(raw_labels)
    if labels.get("partition") != "held_out":
        raise SystemExit("sealed file is not the held-out partition")
    _OUT.mkdir(parents=True)
    rows = []
    started = time.perf_counter()
    for claim in labels["claims"]:
        if claim.get("adjudication_status") != "agreed":
            status = "robustness_uncertain"
            expected = None
        else:
            status = "eligible"
            expected = claim.get("expected")
        raw = canonical({"claim": claim["claim"], "evidence": claim["evidence"]})
        result = evaluate_envelope(raw, policy)
        public = {arm: _public(result[arm]) for arm in ("K", "R", "B", "C")}
        kind = None if expected is None else _kind(str(public["C"]["conclusion"]), str(expected))
        c_relation = next(
            (
                item["receipt"].get("claim_interpretation")
                for item in result["C"]["traces"]
                if item["process_id"] == "quantity_relation"
            ),
            None,
        )
        years = _years(str(claim["claim"]))
        preserved = True
        if years and isinstance(c_relation, dict):
            preserved = set(years).issubset(set(c_relation.get("years") or []))
        row = {
            "claim_id": claim["claim_id"],
            "source_id": claim["source_id"],
            "status": status,
            "expected": expected,
            "families": claim.get("families", []),
            "arms": public,
            "arm_c_kind": kind,
            "scope_years_preserved_in_c_interpretation": preserved,
            "input_sha256": digest(raw),
        }
        rows.append(row)
        (_OUT / "cases").mkdir(exist_ok=True)
        (_OUT / "cases" / f"{claim['claim_id']}.json").write_text(
            json.dumps(row, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    elapsed = time.perf_counter() - started
    eligible = [row for row in rows if row["status"] == "eligible" and row["expected"] in {"supported", "contradicted", "not_checkable"}]
    matrix: dict[str, int] = {}
    for row in eligible:
        matrix[str(row["arm_c_kind"])] = matrix.get(str(row["arm_c_kind"]), 0) + 1
    differences = []
    for row in eligible:
        conclusions = {arm: row["arms"][arm]["conclusion"] for arm in ("R", "B", "C")}
        if len(set(conclusions.values())) > 1:
            differences.append({"claim_id": row["claim_id"], "conclusions": conclusions, "expected": row["expected"]})
    report = {
        "head": _git("rev-parse", "HEAD"),
        "elapsed_seconds": elapsed,
        "eligible": len(eligible),
        "robustness_uncertain": sum(1 for row in rows if row["status"] != "eligible"),
        "arm_c_matrix": matrix,
        "differences_rbc": differences,
        "successor_processes": list(SUCCESSOR),
        "cases": rows,
    }
    (_OUT / "REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"eligible": len(eligible), "arm_c_matrix": matrix, "differences": len(differences)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
