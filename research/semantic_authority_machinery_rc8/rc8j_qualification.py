from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8j import assess_authority
from .rc8h_qualification import qualification_cases as rc8h_exposed_cases
from .rc8h_heldout_cohort import build_rc8h_heldout_cases
from .rc8i_claim_cohort import build_rc8i_cases


NEUTRAL_CLAIM = "claim:rc8j:exposed:neutral"


def _valid_claim_binding(case: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(case)
    out["raw_claim_id"] = NEUTRAL_CLAIM
    out["authority_subject_claim_id"] = NEUTRAL_CLAIM
    return out


def qualification_cases() -> list[dict[str, Any]]:
    cases = [_valid_claim_binding(case) for case in rc8h_exposed_cases()]
    cases.extend(_valid_claim_binding(case) for case in build_rc8h_heldout_cases())
    cases.extend(deepcopy(case) for case in build_rc8i_cases())
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

    return {
        "experiment": "RC8J exposed claim-bound Contract-B authority qualification",
        "case_count": len(rows),
        "status_exact_count": sum(int(row["status_exact"]) for row in rows),
        "reason_exact_count": sum(int(row["reason_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "rows": rows,
    }


def main() -> None:
    result = evaluate()
    Path("RC8J_QUALIFICATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result["unsafe_warranted_atoms"] == 0, result["unsafe_rows"]
    assert result["status_exact_count"] == result["case_count"]
    assert result["reason_exact_count"] == result["case_count"]


if __name__ == "__main__":
    main()
