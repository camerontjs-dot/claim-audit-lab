from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8h import assess_authority
from .rc8h_heldout_cohort import build_rc8h_heldout_cases


BINDING_PREFIXES = (
    "source_binding_",
    "source_mismatch_",
    "bundle_binding_",
    "bundle_mismatch_",
    "passage_binding_",
    "passage_mismatch_",
    "admitted_passage_span_",
    "proposal_",
    "required_field_left_",
    "required_field_right_",
)


def evaluate() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []

    for case in build_rc8h_heldout_cases():
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
    binding_rows = [
        row for row in rows
        if row["mutation_axis"].startswith(BINDING_PREFIXES)
        and row["expected_authority"] != "WARRANTED"
    ]
    bank_invariance = {
        "warranted": by_id["H-H-BANK-WARRANTED"]["observed_authority"] == by_id["H-H-BASE"]["observed_authority"],
        "unresolved": by_id["H-H-BANK-UNRESOLVED"]["observed_authority"] == "UNRESOLVED",
    }

    return {
        "experiment": "RC8H prospective Contract-B segment-bound authority heldout",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "binding_case_count": len(binding_rows),
        "binding_not_unsafe": sum(int(row["observed_authority"] != "WARRANTED") for row in binding_rows),
        "bank_invariance": bank_invariance,
        "rows": rows,
    }


def main() -> None:
    result = evaluate()
    Path("RC8H_HELDOUT_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result["unsafe_warranted_atoms"] == 0, result["unsafe_rows"]
    assert result["status_exact_count"] == result["case_count"]
    assert result["reason_exact_count"] == result["case_count"]
    assert result["binding_not_unsafe"] == result["binding_case_count"]
    assert all(result["bank_invariance"].values())


if __name__ == "__main__":
    main()
