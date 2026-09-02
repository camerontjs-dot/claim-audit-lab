from __future__ import annotations

import json
from pathlib import Path

from .authority_contract import assess_authority
from .rc8a_cohort import build_rc8a_cases


def evaluate() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    unsafe_rows: list[dict[str, object]] = []
    status_exact_count = 0
    reason_exact_count = 0

    for case in build_rc8a_cases():
        observed = assess_authority(case)
        status_exact = observed["authority_status"] == case["expected_authority"]
        reason_exact = observed["reason"] == case["expected_reason"]
        status_exact_count += int(status_exact)
        reason_exact_count += int(reason_exact)

        row = {
            "case_id": case["case_id"],
            "mutation_axis": case["mutation_axis"],
            "expected_authority": case["expected_authority"],
            "expected_reason": case["expected_reason"],
            "observed_authority": observed["authority_status"],
            "observed_reason": observed["reason"],
            "status_exact": status_exact,
            "reason_exact": reason_exact,
        }
        rows.append(row)

        if case["expected_authority"] != "WARRANTED" and observed["authority_status"] == "WARRANTED":
            unsafe_rows.append(row)

    result: dict[str, object] = {
        "experiment": "RC8A authority-subject binding falsifier",
        "candidate_freeze_commit": "61d605902cd79ddfd9f6da4e3f1e93173a8d4257",
        "case_count": len(rows),
        "status_exact_count": status_exact_count,
        "reason_exact_count": reason_exact_count,
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "rows": rows,
        "scientific_state": (
            "RC8_RECEIPT_SURVIVES_SOURCE_BINDING_FALSIFIER"
            if not unsafe_rows and status_exact_count == len(rows)
            else "RC8_RECEIPT_FALSIFIED_BY_SOURCE_BINDING"
        ),
    }
    return result


def main() -> None:
    result = evaluate()
    Path("RC8A_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
