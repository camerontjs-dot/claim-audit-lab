from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8f import assess_authority
from .rc8f_heldout_cohort import build_rc8f_heldout_cases


def evaluate() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []

    for case in build_rc8f_heldout_cases():
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
    source_atom_rows = [
        row for row in rows
        if row["mutation_axis"] in {
            "source_anchor_missing_before_atom_binding",
            "source_mismatch_precedes_atom_mismatch",
            "fresh_target_atom_identity_missing",
            "fresh_authority_atom_identity_missing",
            "fresh_same_source_atom_mismatch",
            "fresh_same_source_whole_bundle_transplant",
            "atom_mismatch_precedes_proposal_subject_mismatch",
        }
    ]
    bank_invariance = {
        "warranted": by_id["F-H-BASE"]["observed_authority"] == by_id["F-H-BANK-WARRANTED"]["observed_authority"],
        "unresolved": by_id["F-H-BANK-UNRESOLVED"]["observed_authority"] == "UNRESOLVED",
    }

    result = {
        "experiment": "RC8F prospective source-and-whole-atom anchored authority heldout",
        "candidate_git_blob": "efc50481be3179332cecb449c3c9c91da7c3dfaa",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "source_atom_binding_not_unsafe": sum(int(row["observed_authority"] != "WARRANTED") for row in source_atom_rows),
        "source_atom_binding_case_count": len(source_atom_rows),
        "bank_invariance": bank_invariance,
        "rows": rows,
    }
    result["scientific_state"] = (
        "SOURCE_AND_ATOM_ANCHORED_GATE_SUPPORTED_WITHIN_PROSPECTIVE_ENVELOPE"
        if result["unsafe_warranted_atoms"] == 0
        and result["status_exact_count"] == result["case_count"]
        and result["reason_exact_count"] == result["case_count"]
        and result["source_atom_binding_not_unsafe"] == result["source_atom_binding_case_count"]
        and all(bank_invariance.values())
        else "SOURCE_AND_ATOM_ANCHORED_GATE_FALSIFIED_OR_REGRESSED"
    )
    return result


def main() -> None:
    result = evaluate()
    Path("RC8F_HELDOUT_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
