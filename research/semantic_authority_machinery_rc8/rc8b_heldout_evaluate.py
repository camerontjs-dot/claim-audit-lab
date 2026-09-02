from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8b import assess_authority
from .rc8b_heldout_cohort import build_rc8b_heldout_cases


def evaluate() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []

    for case in build_rc8b_heldout_cases():
        observed = assess_authority(case)
        row = {
            "case_id": case["case_id"],
            "mutation_axis": case["mutation_axis"],
            "expected_authority": case["expected_authority"],
            "expected_reason": case["expected_reason"],
            "observed_authority": observed["authority_status"],
            "observed_reason": observed["reason"],
            "status_exact": observed["authority_status"] == case["expected_authority"],
            "reason_exact": observed["reason"] == case["expected_reason"],
        }
        rows.append(row)
        if case["expected_authority"] != "WARRANTED" and observed["authority_status"] == "WARRANTED":
            unsafe_rows.append(row)

    by_id = {row["case_id"]: row for row in rows}
    bank_invariance = {
        "warranted": (
            by_id["B-H-BASE"]["observed_authority"]
            == by_id["B-H-BANK-WARRANTED"]["observed_authority"]
        ),
        "unresolved": (
            by_id["B-H-APP-UNK"]["observed_authority"]
            == by_id["B-H-BANK-UNRESOLVED"]["observed_authority"]
        ),
    }

    mismatch_rows = [row for row in rows if "subject_mismatch" in row["mutation_axis"] or row["mutation_axis"].startswith("precedence_")]
    missing_binding_rows = [row for row in rows if "missing_" in row["mutation_axis"] and "subject" in row["mutation_axis"]]
    span_rows = [row for row in rows if "support_" in row["mutation_axis"] and "span" in row["mutation_axis"]]

    result = {
        "experiment": "RC8B prospective bound-receipt held-out",
        "candidate_freeze_commit": "e52f70b77ed0395e33afa9b193cae47475abf892",
        "candidate_git_blob": "edf84bb5aae0dd217e3f780e7a49767440b7c1e5",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "explicit_mismatch_exact_rejections": sum(
            int(row["observed_authority"] == "REJECTED") for row in mismatch_rows
        ),
        "explicit_mismatch_case_count": len(mismatch_rows),
        "missing_binding_not_warranted": sum(
            int(row["observed_authority"] != "WARRANTED") for row in missing_binding_rows
        ),
        "missing_binding_case_count": len(missing_binding_rows),
        "support_span_not_unsafe": sum(
            int(
                row["expected_authority"] == "WARRANTED"
                or row["observed_authority"] != "WARRANTED"
            )
            for row in span_rows
        ),
        "support_span_case_count": len(span_rows),
        "bank_invariance": bank_invariance,
        "rows": rows,
    }
    result["scientific_state"] = (
        "BOUND_RECEIPT_GATE_SUPPORTED_WITHIN_PROSPECTIVE_ENVELOPE"
        if result["unsafe_warranted_atoms"] == 0
        and result["status_exact_count"] == result["case_count"]
        and result["reason_exact_count"] == result["case_count"]
        and all(bank_invariance.values())
        else "BOUND_RECEIPT_GATE_FALSIFIED_OR_REGRESSED"
    )
    return result


def main() -> None:
    result = evaluate()
    Path("RC8B_HELDOUT_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
