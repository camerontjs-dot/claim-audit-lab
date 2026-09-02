from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .authority_contract import assess_authority
from .heldout_cohort import build_heldout_cases


def evaluate() -> dict:
    rows = []
    for case in build_heldout_cases():
        got = assess_authority(case)
        rows.append({
            "case_id": case["case_id"],
            "family": case["family"],
            "axis": case["mutation_axis"],
            "expected": case["expected_authority"],
            "observed": got["authority_status"],
            "expected_reason": case["expected_reason"],
            "observed_reason": got["reason"],
            "status_exact": got["authority_status"] == case["expected_authority"],
            "reason_exact": got["reason"] == case["expected_reason"],
        })

    unsafe = [r for r in rows if r["observed"] == "WARRANTED" and r["expected"] != "WARRANTED"]
    warranted_expected = [r for r in rows if r["expected"] == "WARRANTED"]
    warranted_observed = [r for r in rows if r["observed"] == "WARRANTED"]
    true_warranted = [r for r in rows if r["observed"] == r["expected"] == "WARRANTED"]
    false_dimensions = sorted({r["axis"] for r in unsafe})

    pair_ids = []
    for family in ("population_membership", "comparison", "event_ordering", "permission_composition"):
        base = f"H-{family}-BASE"
        bank = f"{base}-BANK8"
        app = f"{base}-APPUNK"
        app_bank = f"{base}-APPUNK-BANK8"
        pair_ids.extend([(base, bank), (app, app_bank)])
    by_id = {r["case_id"]: r for r in rows}
    monotonic_violations = sum(by_id[a]["observed"] != by_id[b]["observed"] for a, b in pair_ids)

    payload = {
        "case_count": len(rows),
        "family_counts": dict(Counter(r["family"] for r in rows)),
        "expected_state_counts": dict(Counter(r["expected"] for r in rows)),
        "status_exact_count": sum(r["status_exact"] for r in rows),
        "reason_exact_count": sum(r["reason_exact"] for r in rows),
        "unsafe_warranted_atoms": len(unsafe),
        "unsafe_rows": unsafe,
        "false_warranted_semantic_dimensions": false_dimensions,
        "warranted_precision": len(true_warranted) / len(warranted_observed) if warranted_observed else 1.0,
        "warranted_recall": len(true_warranted) / len(warranted_expected) if warranted_expected else 1.0,
        "unresolved_rate": sum(r["observed"] == "UNRESOLVED" for r in rows) / len(rows),
        "incorrect_rejection_rate": sum(r["observed"] == "REJECTED" and r["expected"] == "WARRANTED" for r in rows) / len(warranted_expected),
        "field_level_failure_localization": sum(r["reason_exact"] for r in rows) / len(rows),
        "applicability_errors": sum("applicability" in r["axis"] and not r["status_exact"] for r in rows),
        "composition_errors": sum(r["axis"].startswith("composition_") and not r["status_exact"] for r in rows),
        "authority_monotonicity_violations": monotonic_violations,
        "rows": rows,
    }
    payload["scientific_state"] = (
        "FORMAL_AUTHORITY_GATE_SUPPORTED_WITH_BOUNDS"
        if payload["unsafe_warranted_atoms"] == 0
        and payload["status_exact_count"] == payload["case_count"]
        and payload["reason_exact_count"] == payload["case_count"]
        and payload["authority_monotonicity_violations"] == 0
        else "AUTHORITY_GATE_FALSIFIED"
    )
    return payload


def main() -> None:
    payload = evaluate()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    Path("HELDOUT_RESULTS.json").write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
