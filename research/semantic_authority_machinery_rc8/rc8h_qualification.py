from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from .authority_contract_rc8h import assess_authority
from .rc8f_qualification import qualification_cases as rc8f_exposed_cases
from .rc8f_heldout_cohort import build_rc8f_heldout_cases
from .rc8g_cohort import build_rc8g_cases


NEUTRAL_BUNDLE = "bundle:rc8h:exposed:neutral"
NEUTRAL_PASSAGE = "passage:rc8h:exposed:neutral"
NEUTRAL_ADMITTED_SPAN = [0, 1_000_000]


def _valid_segment_binding(case: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(case)
    out["raw_bundle_id"] = NEUTRAL_BUNDLE
    out["authority_subject_bundle_id"] = NEUTRAL_BUNDLE
    out["raw_passage_id"] = NEUTRAL_PASSAGE
    out["authority_subject_passage_id"] = NEUTRAL_PASSAGE
    out["admitted_passage_span"] = list(NEUTRAL_ADMITTED_SPAN)
    return out


def qualification_cases() -> list[dict[str, Any]]:
    cases = [_valid_segment_binding(case) for case in rc8f_exposed_cases()]
    cases.extend(_valid_segment_binding(case) for case in build_rc8f_heldout_cases())
    # RC8G is the exposed causal evidence for this successor. Preserve its
    # segment mutations and expected labels exactly.
    cases.extend(deepcopy(case) for case in build_rc8g_cases())
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
        "experiment": "RC8H exposed Contract-B segment-bound qualification",
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
    Path("RC8H_QUALIFICATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    assert result["unsafe_warranted_atoms"] == 0, result["unsafe_rows"]
    assert result["status_exact_count"] == result["case_count"]
    assert result["reason_exact_count"] == result["case_count"]


if __name__ == "__main__":
    main()
