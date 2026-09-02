from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8d import assess_authority
from .rc8b_qualification import qualification_cases as rc8b_exposed_cases
from .rc8b_heldout_cohort import build_rc8b_heldout_cases
from .rc8c_cohort import build_rc8c_cases


def _valid_anchor(case: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(case)
    if "raw_source_id" in out:
        out["authority_subject_source_id"] = out["raw_source_id"]
    return out


def qualification_cases() -> list[dict[str, Any]]:
    cases = [_valid_anchor(case) for case in rc8b_exposed_cases()]
    cases.extend(_valid_anchor(case) for case in build_rc8b_heldout_cases())

    # RC8C is exposed causal evidence. Its receipt bundle belongs to source alpha;
    # hold that subject-source anchor constant while raw_source_id is substituted or absent.
    for case in build_rc8c_cases():
        out = deepcopy(case)
        out["authority_subject_source_id"] = "source:prospective:alpha"
        cases.append(out)
    return cases


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

    result = {
        "experiment": "RC8D exposed admitted-evidence anchor qualification",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "rows": rows,
    }
    return result


def main() -> None:
    result = evaluate()
    Path("RC8D_QUALIFICATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result["unsafe_warranted_atoms"] == 0, result["unsafe_rows"]
    assert result["status_exact_count"] == result["case_count"]
    assert result["reason_exact_count"] == result["case_count"]


if __name__ == "__main__":
    main()
