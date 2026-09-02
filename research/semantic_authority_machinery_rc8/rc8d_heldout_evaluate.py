from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8d import assess_authority
from .rc8d_heldout_cohort import build_rc8d_heldout_cases


def evaluate() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []

    for case in build_rc8d_heldout_cases():
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
    source_anchor_rows = [
        row for row in rows
        if row["mutation_axis"] in {
            "raw_source_missing",
            "subject_source_anchor_missing",
            "source_anchor_a_raw_b",
            "source_anchor_b_raw_a",
            "source_mismatch_precedes_subreceipt_mismatch",
        }
    ]
    subordinate_rows = [
        row for row in rows
        if row["mutation_axis"] in {
            "valid_source_anchor_with_proposal_subject_mismatch",
            "valid_source_anchor_with_all_subordinate_subjects_substituted",
        }
    ]
    bank_invariance = {
        "warranted": (
            by_id["D-H-BASE"]["observed_authority"]
            == by_id["D-H-BANK-WARRANTED"]["observed_authority"]
        ),
        "unresolved": (
            by_id["D-H-BANK-UNRESOLVED"]["observed_authority"] == "UNRESOLVED"
        ),
    }

    result = {
        "experiment": "RC8D prospective admitted-evidence anchored authority held-out",
        "candidate_freeze": "RC8D_CANDIDATE_FREEZE.json",
        "candidate_git_blob": "f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1",
        "dependency_rc8b_git_blob": "edf84bb5aae0dd217e3f780e7a49767440b7c1e5",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "source_anchor_not_unsafe": sum(int(row["observed_authority"] != "WARRANTED") for row in source_anchor_rows),
        "source_anchor_case_count": len(source_anchor_rows),
        "subordinate_binding_not_unsafe": sum(int(row["observed_authority"] != "WARRANTED") for row in subordinate_rows),
        "subordinate_binding_case_count": len(subordinate_rows),
        "bank_invariance": bank_invariance,
        "rows": rows,
    }
    result["scientific_state"] = (
        "ADMITTED_EVIDENCE_ANCHORED_GATE_SUPPORTED_WITHIN_PROSPECTIVE_ENVELOPE"
        if result["unsafe_warranted_atoms"] == 0
        and result["status_exact_count"] == result["case_count"]
        and result["reason_exact_count"] == result["case_count"]
        and result["source_anchor_not_unsafe"] == result["source_anchor_case_count"]
        and result["subordinate_binding_not_unsafe"] == result["subordinate_binding_case_count"]
        and all(bank_invariance.values())
        else "ADMITTED_EVIDENCE_ANCHORED_GATE_FALSIFIED_OR_REGRESSED"
    )
    return result


def main() -> None:
    result = evaluate()
    Path("RC8D_HELDOUT_RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
