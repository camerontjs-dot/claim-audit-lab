#!/usr/bin/env python3
"""Replay frozen Cohort A with an A4 authority firewall and monotonicity guard."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.decision_model_replay import build_report
from scripts.evidence_state_operator_shadow import OperatorJudgment, build_operator_report


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _firewall_judgments(operator_row: dict[str, Any]) -> list[OperatorJudgment]:
    judgments: list[OperatorJudgment] = []
    for raw in operator_row["operator_judgments"]:
        if raw["operator"] != "A4_negation_consistency":
            continue
        status = raw["status"]
        reason = raw["reason"]
        if status == "invalid":
            status = "unknown"
            reason = (
                "RC1 authority firewall: A4 non-entailment does not prove the "
                "original refutation contribution semantically invalid"
            )
        judgments.append(
            OperatorJudgment.model_validate(
                {**raw, "status": status, "reason": reason}, strict=False
            )
        )
    return judgments


def run(predecessor_root: Path, output: Path) -> dict[str, Any]:
    predecessor_results = json.loads(
        (predecessor_root / "RESULTS.json").read_text(encoding="utf-8")
    )
    rows: list[dict[str, Any]] = []

    for frozen in predecessor_results["rows"]:
        claim_id = frozen["claim_id"]
        case_dir = predecessor_root / "cases" / claim_id
        eligibility_path = case_dir / "eligibility-shadow.json"
        frozen_operator = json.loads(
            (case_dir / "operator-shadow.json").read_text(encoding="utf-8")
        )
        eligibility = json.loads(eligibility_path.read_text(encoding="utf-8"))
        judgments = _firewall_judgments(frozen_operator["rows"][0])
        counterfactual_operator = build_operator_report(eligibility, judgments)
        operator_path = output.parent / "cases" / claim_id / "operator-rc1.json"
        _write(operator_path, counterfactual_operator)

        replay = build_report(
            eligibility_path,
            operator_path,
            support_threshold=0.70,
            refutation_threshold=0.70,
        )
        row = replay["rows"][0]
        unguarded = row["candidate_outcome"]
        eligible_state = counterfactual_operator["rows"][0]["eligible_state"]
        unknown_channels = {
            j.channel for j in judgments if j.status == "unknown"
        }

        guarded = unguarded
        guard_reason = None
        if eligible_state == "mixed" and unguarded in {"supported", "contradicted"}:
            decided_channel = "support" if unguarded == "supported" else "refutation"
            opposite = "refutation" if decided_channel == "support" else "support"
            if opposite in unknown_channels:
                guarded = "abstain"
                guard_reason = "unresolved_mixed_evidence"

        rows.append(
            {
                "case_id": frozen["case_id"],
                "claim_id": claim_id,
                "relation": frozen["relation"],
                "source_boundary": frozen["source_boundary"],
                "frozen_candidate_outcome": frozen["candidate_outcome"],
                "eligible_state": eligible_state,
                "rc1_valid_state": row["candidate"]["valid"]["state"],
                "rc1_unguarded_outcome": unguarded,
                "rc1_guarded_outcome": guarded,
                "guard_reason": guard_reason,
                "a4_judgments": [j.model_dump(mode="json") for j in judgments],
            }
        )

    cg23b = next(r for r in rows if r["case_id"] == "CG-23b")
    targeted = {
        cid: next(r for r in rows if r["case_id"] == cid)
        for cid in ("CG-12a", "CG-12b", "CG-24", "CG-08a", "CG-08b", "CG-21",
                    "CG-09a", "CG-09b", "CG-22")
    }
    result = {
        "schema_version": "cal-operator-applicability-monotonicity-rc1-v0.1",
        "authority": "non_authoritative_research",
        "predecessor_results_sha256": (\n            "sha256:38cd6f29eab0ea6e0f50e737814b993aaf45a3919cacb5e02296289516e112d7"\n        ),
        "new_model_execution": False,
        "threshold_tuning_performed": False,
        "production_behavior_changed": False,
        "summary": {
            "n_cases": len(rows),
            "a4_invalid_to_unknown": sum(
                j["status"] == "unknown"
                and "non-entailment" in j["reason"]
                for r in rows for j in r["a4_judgments"]
            ),
            "guarded_outcome_counts": dict(\n                sorted(Counter(r["rc1_guarded_outcome"] for r in rows).items())\n            ),
            "monotonicity_guards_fired": sum(r["guard_reason"] is not None for r in rows),
            "cg23b_strengthening_blocked": cg23b["rc1_guarded_outcome"] == "abstain",
            "support_to_adverse_created": sum(
                r["frozen_candidate_outcome"] == "supported"
                and r["rc1_guarded_outcome"] == "contradicted" for r in rows
            ),
            "adverse_to_support_created": sum(
                r["frozen_candidate_outcome"] == "contradicted"
                and r["rc1_guarded_outcome"] == "supported" for r in rows
            ),
        },
        "cg23b": cg23b,
        "targeted_cases": targeted,
        "rows": rows,
    }
    _write(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predecessor-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.predecessor_root, args.output)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    if not result["summary"]["cg23b_strengthening_blocked"]:
        raise SystemExit("CG-23b strengthening falsifier failed")
    if (\n        result["summary"]["support_to_adverse_created"]\n        or result["summary"]["adverse_to_support_created"]\n    ):
        raise SystemExit("RC1 created a forbidden support/adverse polarity transition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
