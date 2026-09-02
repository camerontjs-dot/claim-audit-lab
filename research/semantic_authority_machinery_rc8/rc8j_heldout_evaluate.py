from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8j import assess_authority
from .rc8j_heldout_cohort import build_rc8j_heldout_cases


CLAIM_BINDING_AXES = {
    "raw_claim_identity_missing",
    "authority_claim_identity_missing",
    "same_segment_atom_claim_mismatch",
    "whole_receipt_cross_claim_transplant_same_material",
    "claim_mismatch_precedes_atom_mismatch",
}


def evaluate() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []

    for case in build_rc8j_heldout_cases():
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
    claim_rows = [row for row in rows if row["mutation_axis"] in CLAIM_BINDING_AXES]
    bank_invariance = {
        "warranted": by_id["J-H-BANK-WARRANTED"]["observed_authority"] == by_id["J-H-BASE"]["observed_authority"],
        "unresolved": by_id["J-H-BANK-UNRESOLVED"]["observed_authority"] == "UNRESOLVED",
    }

    return {
        "experiment": "RC8J prospective claim-bound Contract-B authority heldout",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "claim_binding_case_count": len(claim_rows),
        "claim_binding_not_unsafe": sum(int(row["observed_authority"] != "WARRANTED") for row in claim_rows),
        "bank_invariance": bank_invariance,
        "rows": rows,
    }


def main() -> None:
    result = evaluate()
    Path("RC8J_HELDOUT_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
