from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8d import assess_authority
from .rc8e_cohort import build_rc8e_cases


def evaluate() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []

    for case in build_rc8e_cases():
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
    atom_binding_rows = [
        row for row in rows
        if row["mutation_axis"] in {
            "same_source_whole_atom_bundle_transplanted",
            "target_atom_identity_missing",
            "authority_subject_atom_identity_missing",
            "atom_mismatch_precedes_subreceipt_mismatch",
        }
    ]
    bank_invariance = {
        "warranted": by_id["E-BASE"]["observed_authority"] == by_id["E-BANK-WARRANTED"]["observed_authority"],
        "unresolved": by_id["E-BANK-UNRESOLVED"]["observed_authority"] == "UNRESOLVED",
    }

    result = {
        "experiment": "RC8E same-source whole-atom identity falsifier",
        "parent_candidate": "RC8D",
        "parent_candidate_git_blob": "f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "atom_binding_not_unsafe": sum(int(row["observed_authority"] != "WARRANTED") for row in atom_binding_rows),
        "atom_binding_case_count": len(atom_binding_rows),
        "bank_invariance": bank_invariance,
        "rows": rows,
    }
    result["scientific_state"] = (
        "WHOLE_ATOM_BINDING_SUPPORTED_BY_FROZEN_RC8D"
        if result["unsafe_warranted_atoms"] == 0
        and result["status_exact_count"] == result["case_count"]
        and result["reason_exact_count"] == result["case_count"]
        and all(bank_invariance.values())
        else "RC8D_WHOLE_ATOM_BINDING_FALSIFIED_OR_REGRESSED"
    )
    return result


def main() -> None:
    result = evaluate()
    Path("RC8E_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
