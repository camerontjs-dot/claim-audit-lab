from __future__ import annotations

import json
from pathlib import Path

from .authority_contract_rc8b import assess_authority
from .rc8c_cohort import build_rc8c_cases


def evaluate() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    unsafe_rows: list[dict[str, object]] = []
    for case in build_rc8c_cases():
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

    result: dict[str, object] = {
        "experiment": "RC8C admitted-evidence source anchor falsifier",
        "candidate_freeze_commit": "e52f70b77ed0395e33afa9b193cae47475abf892",
        "candidate_git_blob": "edf84bb5aae0dd217e3f780e7a49767440b7c1e5",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "rows": rows,
        "scientific_state": (
            "RC8B_SURVIVES_EVIDENCE_SOURCE_ANCHOR_FALSIFIER"
            if not unsafe_rows and all(row["status_exact"] for row in rows)
            else "RC8B_FALSIFIED_BY_MISSING_EVIDENCE_SOURCE_ANCHOR"
        ),
    }
    return result


def main() -> None:
    result = evaluate()
    Path("RC8C_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
