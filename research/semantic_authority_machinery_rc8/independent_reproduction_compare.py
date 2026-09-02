from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
from typing import Any, Callable

from .authority_contract_rc8j import assess_authority as reference_assess
from .rc8j_qualification import qualification_cases
from .rc8j_heldout_cohort import build_rc8j_heldout_cases


def _load_assessor(path: Path) -> Callable[[dict[str, Any]], dict[str, Any]]:
    spec = importlib.util.spec_from_file_location("independent_authority_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load implementation: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assessor = getattr(module, "assess_authority", None)
    if not callable(assessor):
        raise RuntimeError("independent implementation must export assess_authority(case)")
    return assessor


def _cases() -> list[dict[str, Any]]:
    cases = list(qualification_cases())
    cases.extend(build_rc8j_heldout_cases())
    return cases


def evaluate(implementation_path: Path) -> dict[str, Any]:
    independent_assess = _load_assessor(implementation_path)
    rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []

    for index, case in enumerate(_cases()):
        independent = independent_assess(case)
        reference = reference_assess(case)
        expected_status = case["expected_authority"]
        expected_reason = case["expected_reason"]
        row = {
            "index": index,
            "case_id": case["case_id"],
            "mutation_axis": case["mutation_axis"],
            "expected_authority": expected_status,
            "expected_reason": expected_reason,
            "independent_authority": independent.get("authority_status"),
            "independent_reason": independent.get("reason"),
            "reference_authority": reference.get("authority_status"),
            "reference_reason": reference.get("reason"),
            "independent_status_exact": independent.get("authority_status") == expected_status,
            "independent_reason_exact": independent.get("reason") == expected_reason,
            "reference_status_exact": reference.get("authority_status") == expected_status,
            "reference_reason_exact": reference.get("reason") == expected_reason,
            "independent_reference_exact": independent == reference,
        }
        rows.append(row)
        if expected_status != "WARRANTED" and independent.get("authority_status") == "WARRANTED":
            unsafe_rows.append(row)

    return {
        "experiment": "Frozen Authority Gate Specification v1 fresh independent reproduction comparison",
        "case_count": len(rows),
        "independent_status_exact_count": sum(int(row["independent_status_exact"]) for row in rows),
        "independent_reason_exact_count": sum(int(row["independent_reason_exact"]) for row in rows),
        "reference_status_exact_count": sum(int(row["reference_status_exact"]) for row in rows),
        "reference_reason_exact_count": sum(int(row["reference_reason_exact"]) for row in rows),
        "independent_reference_exact_count": sum(int(row["independent_reference_exact"]) for row in rows),
        "unsafe_warranted_atoms": len(unsafe_rows),
        "unsafe_rows": unsafe_rows,
        "expected_state_counts": dict(Counter(row["expected_authority"] for row in rows)),
        "independent_state_counts": dict(Counter(row["independent_authority"] for row in rows)),
        "reference_state_counts": dict(Counter(row["reference_authority"] for row in rows)),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation", required=True, type=Path)
    parser.add_argument("--output", default=Path("INDEPENDENT_REPRODUCTION_COMPARISON.json"), type=Path)
    args = parser.parse_args()

    result = evaluate(args.implementation)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in {"rows", "unsafe_rows"}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
