#!/usr/bin/env python3
"""Evaluate preregistered ensemble/disagreement rules on frozen RC0 measurements."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

EXPECTED_MEASUREMENTS_SHA256 = "a575966ca1089d43d7fdf162e01d15bfa2f06b8ab8afec95a826aa121dc132b7"
MODELS = ("incumbent_base", "same_family_large", "long_context_base")
LABELS = {"entailment", "neutral", "contradiction"}


def load_frozen(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_MEASUREMENTS_SHA256:
        raise RuntimeError(f"frozen measurement SHA mismatch: {actual}")
    data = json.loads(raw)
    rows = data["rows"]
    if len(rows) != 42:
        raise RuntimeError(f"expected 42 frozen rows, got {len(rows)}")
    for row in rows:
        if set(row["predictions"]) != set(MODELS):
            raise RuntimeError(f"{row['case_id']}/{row['variant']}: model set changed")
        if row["target"] not in LABELS:
            raise RuntimeError(f"{row['case_id']}: invalid target")
        if any(v not in LABELS for v in row["predictions"].values()):
            raise RuntimeError(f"{row['case_id']}: invalid frozen prediction")
    return data


def r0_incumbent(row: dict[str, Any]) -> str:
    return row["predictions"]["incumbent_base"]


def r1_majority(row: dict[str, Any]) -> str:
    counts = Counter(row["predictions"].values())
    label, count = counts.most_common(1)[0]
    return label if count >= 2 else "unresolved"


def r2_unanimity(row: dict[str, Any]) -> str:
    values = tuple(row["predictions"].values())
    return values[0] if len(set(values)) == 1 else "unresolved"


def r3_polar_abstain(row: dict[str, Any]) -> str:
    values = set(row["predictions"].values())
    if {"entailment", "contradiction"} <= values:
        return "unresolved"
    return r1_majority(row)


def r4_adverse_conservative(row: dict[str, Any]) -> str:
    counts = Counter(row["predictions"].values())
    if counts["contradiction"] == 3:
        return "contradiction"
    if counts["entailment"] >= 2 and counts["contradiction"] == 0:
        return "entailment"
    if counts["neutral"] >= 2 and counts["contradiction"] == 0:
        return "neutral"
    return "unresolved"


def r5_aperture_route(row: dict[str, Any]) -> str:
    trunc = row["truncated"]
    if (
        (trunc["incumbent_base"] or trunc["same_family_large"])
        and not trunc["long_context_base"]
    ):
        return row["predictions"]["long_context_base"]
    return r4_adverse_conservative(row)


RULES: dict[str, Callable[[dict[str, Any]], str]] = {
    "R0_incumbent": r0_incumbent,
    "R1_majority": r1_majority,
    "R2_unanimity": r2_unanimity,
    "R3_polar_abstain": r3_polar_abstain,
    "R4_adverse_conservative": r4_adverse_conservative,
    "R5_aperture_route": r5_aperture_route,
}


def summarize(rows: list[dict[str, Any]], rule: Callable[[dict[str, Any]], str]) -> dict[str, Any]:
    evaluated = []
    for row in rows:
        output = rule(row)
        target = row["target"]
        decided = output != "unresolved"
        evaluated.append((row, target, output, decided))

    decided_rows = [x for x in evaluated if x[3]]
    correct = [x for x in decided_rows if x[1] == x[2]]
    per_target = {}
    for target in sorted(LABELS):
        subset = [x for x in evaluated if x[1] == target]
        decided_subset = [x for x in subset if x[3]]
        per_target[target] = {
            "n": len(subset),
            "decided": len(decided_subset),
            "correct": sum(x[1] == x[2] for x in decided_subset),
        }

    return {
        "n": len(evaluated),
        "decided": len(decided_rows),
        "coverage": len(decided_rows) / len(evaluated),
        "exact_all": sum(x[1] == x[2] for x in evaluated),
        "selective_accuracy": len(correct) / len(decided_rows) if decided_rows else None,
        "wrong_decided": sum(x[1] != x[2] for x in decided_rows),
        "false_adverse": sum(
            x[1] != "contradiction" and x[2] == "contradiction" for x in decided_rows
        ),
        "neutral_to_contradiction": sum(
            x[1] == "neutral" and x[2] == "contradiction" for x in decided_rows
        ),
        "contradiction_to_neutral": sum(
            x[1] == "contradiction" and x[2] == "neutral" for x in decided_rows
        ),
        "contradiction_to_entailment": sum(
            x[1] == "contradiction" and x[2] == "entailment" for x in decided_rows
        ),
        "entailment_to_contradiction": sum(
            x[1] == "entailment" and x[2] == "contradiction" for x in decided_rows
        ),
        "unresolved": sum(not x[3] for x in evaluated),
        "per_target": per_target,
    }


def diagnostics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        values = list(row["predictions"].values())
        majority = r1_majority(row)
        correct_present = row["target"] in values
        incumbent_correct = row["predictions"]["incumbent_base"] == row["target"]
        out.append(
            {
                "case_id": row["case_id"],
                "variant": row["variant"],
                "target": row["target"],
                "predictions": row["predictions"],
                "distinct_labels": len(set(values)),
                "unanimous": len(set(values)) == 1,
                "polar_conflict": (
                    "entailment" in values and "contradiction" in values
                ),
                "majority_output": majority,
                "majority_correct": majority == row["target"],
                "correct_label_present_in_votes": correct_present,
                "incumbent_correct": incumbent_correct,
                "R2_unanimity": r2_unanimity(row),
                "R3_polar_abstain": r3_polar_abstain(row),
                "R4_adverse_conservative": r4_adverse_conservative(row),
                "R5_aperture_route": r5_aperture_route(row),
            }
        )
    return out


def run(frozen_path: Path, output_path: Path) -> dict[str, Any]:
    data = load_frozen(frozen_path)
    rows = data["rows"]
    by_variant = {
        variant: [r for r in rows if r["variant"] == variant]
        for variant in ("short", "stress_head", "stress_tail")
    }
    result = {
        "schema_version": "cal-nli-ensemble-disagreement-rc1-result-v0.1",
        "frozen_measurements_sha256": "sha256:" + EXPECTED_MEASUREMENTS_SHA256,
        "score_normalization_performed": False,
        "learned_weights_performed": False,
        "threshold_tuning_performed": False,
        "results": {
            variant: {
                rule_name: summarize(vrows, rule)
                for rule_name, rule in RULES.items()
            }
            for variant, vrows in by_variant.items()
        },
        "diagnostics": diagnostics(rows),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.frozen, args.output)
    print(json.dumps(result["results"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
