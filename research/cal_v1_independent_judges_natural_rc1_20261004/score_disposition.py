"""Score the one decisive run against the preregistered acceptance rule.

Critical false decisions are counted on arm C. Arm B is the lossy control,
and P1 requires B to be wrong on a claim where the shared reduction removes
a year, quantifier, or attribution hedge. That B outcome is not an arm-C
error-rule failure.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CANDIDATE = ROOT / "candidate"
FREEZE_FILES = (
    "candidate/judges.py",
    "candidate/views.py",
    "candidate/router.py",
    "candidate/lossy.py",
    "candidate/synthesize.py",
    "candidate/evaluate.py",
    "candidate/dispatch.py",
    "candidate/worker.py",
    "candidate/kernel_worker.py",
    "candidate/codec.py",
    "candidate/calibrate.py",
    "candidate/decisive.py",
    "candidate/mechanical_checks.py",
    "candidate/POLICY.json",
    "candidate/CATALOGUE.json",
    "score_disposition.py",
    "HELD_OUT_SEAL.json",
    "PROTOCOL.md",
)

ADVANTAGE = "SUPPORTED_SOURCE_DISJOINT_NATURAL_CLAIM_USEFULNESS_WITH_BOUNDED_INDEPENDENT_JUDGE_ADVANTAGE"
USEFULNESS = "SUPPORTED_NATURAL_CLAIM_USEFULNESS_ARCHITECTURE_ADVANTAGE_UNESTABLISHED"
MECHANICS = "MECHANICS_SUPPORTED_NATURAL_USEFULNESS_UNESTABLISHED"
FALSIFIED = "FALSIFIED_UNSAFE_FALSE_DECISION_RATE"
INCONCLUSIVE = "INCONCLUSIVE_EVALUATOR_OR_COHORT_INVALID"
BLOCKED = "BLOCKED_REQUIRED_JUDGE_OR_ENVIRONMENT_UNAVAILABLE"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _freeze_ok() -> bool:
    freeze = json.loads((ROOT / "FREEZE.json").read_text(encoding="utf-8"))
    recorded = freeze["files"]
    return all(_sha256(ROOT / name) == recorded[name] for name in FREEZE_FILES)


def _p1(row: dict) -> bool:
    loss = (row["arms"]["B"].get("loss") or {})
    if loss.get("material_tokens_removed") is not True:
        return False
    expected = row["expected"]
    got_c = row["arms"]["C"]["conclusion"]
    got_b = row["arms"]["B"]["conclusion"]
    return got_c == expected and got_b in {"supported", "contradicted"} and got_b != expected


def _p2(row: dict) -> bool:
    if row.get("arm_c_kind") != "correct_deciding":
        return False
    by_arm = {
        arm: {item["process_id"]: item for item in row["arms"][arm]["processes"]}
        for arm in ("R", "C")
    }
    skipped = [
        process_id
        for process_id, item in by_arm["C"].items()
        if item.get("execution") != "not_run" and by_arm["R"][process_id].get("execution") == "not_run"
    ]
    if not skipped:
        return False
    return row["arms"]["R"]["conclusion"] != row["arms"]["C"]["conclusion"]


def main() -> None:
    report = json.loads((CANDIDATE / "execution" / "decisive-01" / "REPORT.json").read_text(encoding="utf-8"))
    mechanical = json.loads((CANDIDATE / "execution" / "mechanical-01" / "REPORT.json").read_text(encoding="utf-8"))
    eligible = [
        row
        for row in report["cases"]
        if row["status"] == "eligible" and row["expected"] in {"supported", "contradicted", "not_checkable"}
    ]
    false_rows = [row for row in eligible if row["arm_c_kind"] in {"false_support", "false_refutation"}]
    deciding = [row for row in eligible if row["expected"] in {"supported", "contradicted"}]
    unresolved = [row for row in eligible if row["expected"] == "not_checkable"]
    correct = [row for row in eligible if row["arm_c_kind"] == "correct_deciding"]
    safe = [row for row in unresolved if row["arm_c_kind"] == "safe_abstention"]
    p1_rows = [row["claim_id"] for row in eligible if _p1(row)]
    p2_rows = [row["claim_id"] for row in eligible if _p2(row)]
    controls_passed = bool(mechanical.get("passed"))
    freeze_ok = _freeze_ok()
    successor_ran = any(
        item.get("execution") == "completed"
        for row in eligible
        for item in row["arms"]["C"]["processes"]
    )
    if not successor_ran:
        disposition = BLOCKED
    elif not freeze_ok:
        disposition = INCONCLUSIVE
    elif false_rows:
        disposition = FALSIFIED
    elif len(eligible) < 4 or len(deciding) < 2:
        disposition = MECHANICS
    elif len(correct) < 2:
        disposition = MECHANICS
    elif not unresolved or len(safe) != len(unresolved) or not controls_passed:
        disposition = INCONCLUSIVE
    elif p1_rows or p2_rows:
        disposition = ADVANTAGE
    else:
        disposition = USEFULNESS
    decisions = len(correct) + len(false_rows)
    summary = {
        "disposition": disposition,
        "eligible": len(eligible),
        "deciding_class_claims": len(deciding),
        "correct_deciding": len(correct),
        "false_support": sum(1 for row in false_rows if row["arm_c_kind"] == "false_support"),
        "false_refutation": sum(1 for row in false_rows if row["arm_c_kind"] == "false_refutation"),
        "conditional_accuracy": None if decisions == 0 else len(correct) / decisions,
        "safe_abstentions": len(safe),
        "p1": p1_rows,
        "p2": p2_rows,
        "controls_passed": controls_passed,
        "freeze_ok": freeze_ok,
        "false_claim_ids": [row["claim_id"] for row in false_rows],
        "elapsed_seconds": report.get("elapsed_seconds"),
        "head": report.get("head"),
    }
    out = CANDIDATE / "execution" / "decisive-01" / "DISPOSITION.json"
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
