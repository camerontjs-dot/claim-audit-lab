from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8b import assess_authority
from .cohort import build_cases
from .heldout_cohort import build_heldout_cases
from .rc8a_cohort import build_rc8a_cases


def bind_exposed_case(case: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(case)
    subject = f"authority-subject:qualified:{out['raw_source_id']}:{out['case_id']}"
    out["authority_subject_id"] = subject
    out["proposal"]["authority_subject_id"] = subject
    out["assertion"]["authority_subject_id"] = subject
    out["operator"]["authority_subject_id"] = subject
    for receipt in out["field_warrants"].values():
        receipt["authority_subject_id"] = subject
    if out["composition"]["required"]:
        out["composition"]["authority_subject_id"] = subject
    if out["aperture"]["required"]:
        out["aperture"]["authority_subject_id"] = subject
    return out


def qualification_cases() -> list[dict[str, Any]]:
    exposed = [bind_exposed_case(case) for case in build_cases()]
    exposed.extend(bind_exposed_case(case) for case in build_heldout_cases())
    exposed.extend(deepcopy(case) for case in build_rc8a_cases())
    return exposed


def evaluate() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []
    for case in qualification_cases():
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

    return {
        "experiment": "RC8B exposed qualification",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "rows": rows,
    }


def main() -> None:
    result = evaluate()
    Path("RC8B_QUALIFICATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result["unsafe_warranted_atoms"] == 0, result["unsafe_rows"]
    assert result["status_exact_count"] == result["case_count"], (
        result["status_exact_count"],
        result["case_count"],
    )
    assert result["reason_exact_count"] == result["case_count"], (
        result["reason_exact_count"],
        result["case_count"],
    )


if __name__ == "__main__":
    main()
