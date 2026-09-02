from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8f import assess_authority
from .rc8g_cohort import build_rc8g_cases


def evaluate() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []

    for case in build_rc8g_cases():
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
    segment_rows = [
        row for row in rows
        if row["mutation_axis"] in {
            "raw_bundle_identity_missing",
            "authority_bundle_identity_missing",
            "contract_b_bundle_identity_mismatch",
            "raw_passage_identity_missing",
            "authority_passage_identity_missing",
            "same_bundle_source_passage_mismatch",
            "proposal_outside_admitted_passage_inside_operator",
            "field_support_outside_admitted_passage_inside_operator",
            "passage_mismatch_precedes_atom_mismatch",
        }
    ]
    bank_invariance = {
        "warranted": by_id["G-BASE"]["observed_authority"] == by_id["G-BANK-WARRANTED"]["observed_authority"],
        "unresolved": by_id["G-BANK-UNRESOLVED"]["observed_authority"] == "UNRESOLVED",
    }

    result = {
        "experiment": "RC8G Contract-B evidence segment binding falsifier",
        "parent_candidate": "RC8F",
        "parent_candidate_git_blob": "efc50481be3179332cecb449c3c9c91da7c3dfaa",
        "contract_b_authority_commit": "c314e53bd91c0736aa4370a364673b069aceb43e",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "segment_binding_not_unsafe": sum(int(row["observed_authority"] != "WARRANTED") for row in segment_rows),
        "segment_binding_case_count": len(segment_rows),
        "bank_invariance": bank_invariance,
        "rows": rows,
    }
    result["scientific_state"] = (
        "CONTRACT_B_SEGMENT_BINDING_SUPPORTED_BY_FROZEN_RC8F"
        if result["unsafe_warranted_atoms"] == 0
        and result["status_exact_count"] == result["case_count"]
        and result["reason_exact_count"] == result["case_count"]
        and all(bank_invariance.values())
        else "RC8F_CONTRACT_B_SEGMENT_BINDING_FALSIFIED_OR_REGRESSED"
    )
    return result


def main() -> None:
    result = evaluate()
    Path("RC8G_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
