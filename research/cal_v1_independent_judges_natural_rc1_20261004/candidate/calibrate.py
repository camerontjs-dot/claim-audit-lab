"""Estimate weights from the calibration partition only.

This script refuses a held-out label file. It does not open one.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

_CANDIDATE = Path(__file__).resolve().parent
_ROOT = _CANDIDATE.parent
sys.path.insert(0, str(_CANDIDATE))

from codec import canonical  # noqa: E402
from evaluate import evaluate_envelope  # noqa: E402
from synthesize import synthesize  # noqa: E402

_CALIBRATION = _ROOT / "adjudication" / "reconciled" / "calibration.json"
_OUT = _CANDIDATE / "execution" / "calibration-01"


def _policy(weights: dict[str, str], minimum: str) -> dict[str, object]:
    return {
        "schema": "cal-independent-judges-natural-rc1-policy",
        "calibration_status": "CALIBRATED_ON_CALIBRATION_PARTITION_ONLY",
        "minimum": minimum,
        "lanes": {
            "quantity_relation": {
                "role": "relation",
                "weight": weights["quantity_relation"],
                "group": "quantity-text",
                "required": False,
            },
            "event_order": {
                "role": "relation",
                "weight": weights["event_order"],
                "group": "event-order-text",
                "required": False,
            },
            "scope_guard": {
                "role": "guard",
                "weight": "0",
                "group": "scope-guard",
                "required": True,
            },
            "attribution_guard": {
                "role": "guard",
                "weight": "0",
                "group": "attribution-guard",
                "required": True,
            },
        },
    }


def _eligible(claim: dict[str, object]) -> bool:
    return claim.get("expected") in {"supported", "contradicted", "not_checkable"} and claim.get(
        "adjudication_status"
    ) == "agreed"


def _class_of(conclusion: str, expected: str) -> str:
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


def _rescore(result: dict[str, object], policy: dict[str, object]) -> str:
    traces = result["C"]["traces"]  # type: ignore[index]
    raw_hash = traces[0]["receipt"]["input_sha256"]
    # Synthesis binds to the bytes the lanes received. Rebuild is unnecessary:
    # the stored receipts already carry that hash, and synthesize checks it
    # against the supplied raw. Recover the original raw from the case file
    # instead of trusting a reconstructed hash alone.
    del raw_hash
    raw = result["_raw"]  # type: ignore[index]
    receipts = [item["receipt"] for item in traces]
    return str(synthesize(raw, receipts, policy)["conclusion"])


def main() -> int:
    if len(sys.argv) > 1:
        raise SystemExit("calibrate.py takes no path arguments")
    document = json.loads(_CALIBRATION.read_text(encoding="utf-8"))
    if document.get("partition") != "calibration":
        raise SystemExit("calibration file is not the calibration partition")
    claims = [item for item in document["claims"] if _eligible(item)]
    weights = {"quantity_relation": "1", "event_order": "1"}
    policy = _policy(weights, "1")
    rows = []
    for claim in claims:
        raw = canonical({"claim": claim["claim"], "evidence": claim["evidence"]})
        result = evaluate_envelope(raw, policy)
        result["_raw"] = raw
        rows.append({"claim": claim, "result": result})
    changed = True
    while changed:
        changed = False
        policy = _policy(weights, "1")
        for row in rows:
            conclusion = _rescore(row["result"], policy)
            kind = _class_of(conclusion, str(row["claim"]["expected"]))
            if kind not in {"false_support", "false_refutation"}:
                continue
            direction = "supports" if kind == "false_support" else "refutes"
            synthesis = synthesize(
                row["result"]["_raw"],
                [item["receipt"] for item in row["result"]["C"]["traces"]],
                policy,
            )
            for receipt in synthesis["receipts"]:
                lane = policy["lanes"][receipt["process_id"]]
                if lane["role"] == "relation" and receipt.get("conclusion") == direction:
                    if weights[receipt["process_id"]] != "0":
                        weights[receipt["process_id"]] = "0"
                        changed = True
    best: tuple[int, int, str] | None = None
    observed = [Fraction(0)]
    for minimum in range(1, 5):
        policy = _policy(weights, str(minimum))
        correct = 0
        wrong = 0
        for row in rows:
            kind = _class_of(_rescore(row["result"], policy), str(row["claim"]["expected"]))
            if kind == "correct_deciding":
                correct += 1
            if kind in {"false_support", "false_refutation"}:
                wrong += 1
        if wrong == 0 and (best is None or (correct, -minimum) > (best[0], -best[1])):
            best = (correct, minimum, str(minimum))
        observed.append(Fraction(minimum))
    if best is None:
        minimum = "4"
    else:
        minimum = best[2]
    policy = _policy(weights, minimum)
    matrix: dict[str, int] = {}
    case_rows = []
    for row in rows:
        conclusion = _rescore(row["result"], policy)
        expected = str(row["claim"]["expected"])
        kind = _class_of(conclusion, expected)
        matrix[kind] = matrix.get(kind, 0) + 1
        local = {
            item["receipt"]["process_id"]: item["receipt"].get("conclusion")
            for item in row["result"]["C"]["traces"]
        }
        case_rows.append(
            {
                "claim_id": row["claim"]["claim_id"],
                "source_id": row["claim"]["source_id"],
                "expected": expected,
                "arm_c": conclusion,
                "kind": kind,
                "local": local,
            }
        )
    _OUT.mkdir(parents=True, exist_ok=True)
    (_CANDIDATE / "POLICY.json").write_text(
        json.dumps(policy, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = {
        "eligible_calibration_claims": len(rows),
        "weights": weights,
        "minimum": minimum,
        "matrix": matrix,
        "cases": case_rows,
        "uncertain_excluded": [
            item["claim_id"]
            for item in document["claims"]
            if item.get("adjudication_status") != "agreed"
        ],
    }
    (_OUT / "REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"eligible": len(rows), "matrix": matrix, "minimum": minimum, "weights": weights}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
