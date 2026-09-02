from __future__ import annotations

import argparse
import importlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from .cohort import build_cases


def weak_allow_all(case: dict[str, Any]) -> dict[str, Any]:
    if case["execution_state"] != "completed":
        return {"authority_status": "NO_ASSESSMENT", "reason": "EXECUTION_FAILED"}
    return {"authority_status": "WARRANTED", "reason": "ALLOW_ALL"}


def weak_family_only(case: dict[str, Any]) -> dict[str, Any]:
    if case["execution_state"] != "completed":
        return {"authority_status": "NO_ASSESSMENT", "reason": "EXECUTION_FAILED"}
    ok = case["operator"]["domain"] == case["proposal"]["family"]
    return {"authority_status": "WARRANTED" if ok else "REJECTED", "reason": "FAMILY_ONLY"}


def weak_collapse_unknown(case: dict[str, Any]) -> dict[str, Any]:
    if case["execution_state"] != "completed":
        return {"authority_status": "NO_ASSESSMENT", "reason": "EXECUTION_FAILED"}
    if not case["evidence_admitted"]:
        return {"authority_status": "REJECTED", "reason": "EVIDENCE"}
    if case["operator"]["applicability"] == "inapplicable":
        return {"authority_status": "REJECTED", "reason": "INAPPLICABLE"}
    return {"authority_status": "WARRANTED", "reason": "COLLAPSED_UNKNOWN"}


def weak_agreement_boost(case: dict[str, Any]) -> dict[str, Any]:
    if case["execution_state"] != "completed":
        return {"authority_status": "NO_ASSESSMENT", "reason": "EXECUTION_FAILED"}
    if case["reader_agreement_count"] >= 2:
        return {"authority_status": "WARRANTED", "reason": "AGREEMENT_BOOST"}
    return weak_family_only(case)


def score(name: str, fn: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
    cases = build_cases()
    rows = []
    unsafe = 0
    incorrect_rejection = 0
    unresolved_wrong = 0
    exact = 0
    for case in cases:
        got = fn(case)
        expected = case["expected_authority"]
        observed = got["authority_status"]
        ok = observed == expected
        exact += int(ok)
        if observed == "WARRANTED" and expected != "WARRANTED":
            unsafe += 1
        if observed == "REJECTED" and expected == "WARRANTED":
            incorrect_rejection += 1
        if observed == "UNRESOLVED" and expected != "UNRESOLVED":
            unresolved_wrong += 1
        rows.append({
            "case_id": case["case_id"],
            "axis": case["mutation_axis"],
            "expected": expected,
            "observed": observed,
            "expected_reason": case["expected_reason"],
            "observed_reason": got.get("reason"),
            "exact": ok,
        })
    return {
        "name": name,
        "case_count": len(cases),
        "exact": exact,
        "unsafe_warranted_atoms": unsafe,
        "incorrect_rejection_count": incorrect_rejection,
        "unresolved_misclassification_count": unresolved_wrong,
        "rows": rows,
    }


def qualification() -> dict[str, Any]:
    cases = build_cases()
    ids = [c["case_id"] for c in cases]
    assert len(ids) == len(set(ids))
    required_axes = {
        "source_span", "narrator_assertion_scope", "entity", "population", "predicate",
        "polarity", "role_direction", "subclass_direction", "quantifier", "permission_status",
        "exception_attachment", "temporal_attachment", "numeric_value", "unit",
        "comparison_direction", "necessity_direction", "unsupported_extra_modifier",
        "out_of_jurisdiction_semantic_family", "composition_unresolved",
    }
    observed_axes = {c["mutation_axis"] for c in cases}
    assert required_axes <= observed_axes

    controls = {
        "allow_all": score("allow_all", weak_allow_all),
        "family_only": score("family_only", weak_family_only),
        "collapse_unknown": score("collapse_unknown", weak_collapse_unknown),
        "agreement_boost": score("agreement_boost", weak_agreement_boost),
    }
    assert all(v["unsafe_warranted_atoms"] > 0 for v in controls.values())

    monotonic_pairs = [("BASE", "BANK-2"), ("BASE", "BANK-8"), ("BANK-UNK-1", "BANK-UNK-8")]
    return {
        "state": "QUALIFIED",
        "case_count": len(cases),
        "expected_counts": dict(Counter(c["expected_authority"] for c in cases)),
        "weak_controls": {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in controls.items()},
        "monotonic_pairs": monotonic_pairs,
    }


def science(module: str) -> dict[str, Any]:
    candidate = importlib.import_module(module)
    result = score(module, candidate.assess_authority)
    rows = result["rows"]
    reason_exact = sum(r["observed_reason"] == r["expected_reason"] for r in rows)

    row_by_id = {r["case_id"]: r for r in rows}
    monotonic_pairs = [("BASE", "BANK-2"), ("BASE", "BANK-8"), ("BANK-UNK-1", "BANK-UNK-8")]
    monotonic_violations = sum(
        row_by_id[a]["observed"] != row_by_id[b]["observed"] for a, b in monotonic_pairs
    )

    positives = sum(r["expected"] == "WARRANTED" for r in rows)
    warranted = sum(r["observed"] == "WARRANTED" for r in rows)
    true_warranted = sum(r["expected"] == r["observed"] == "WARRANTED" for r in rows)
    rejected_positive = sum(r["expected"] == "WARRANTED" and r["observed"] == "REJECTED" for r in rows)
    false_dimensions = sorted({r["axis"] for r in rows if r["observed"] == "WARRANTED" and r["expected"] != "WARRANTED"})

    result.update({
        "warranted_precision": true_warranted / warranted if warranted else 1.0,
        "warranted_recall": true_warranted / positives if positives else 1.0,
        "false_warranted_semantic_dimensions": false_dimensions,
        "unresolved_rate": sum(r["observed"] == "UNRESOLVED" for r in rows) / len(rows),
        "incorrect_rejection_rate": rejected_positive / positives if positives else 0.0,
        "field_level_failure_localization": reason_exact / len(rows),
        "authority_monotonicity_violations": monotonic_violations,
        "applicability_errors": sum(("applicability" in r["axis"] or r["axis"] == "operator_inapplicable") and not r["exact"] for r in rows),
        "composition_errors": sum(r["axis"].startswith("composition_") and not r["exact"] for r in rows),
    })
    result["scientific_state"] = (
        "FORMAL_AUTHORITY_GATE_SUPPORTED_WITH_BOUNDS"
        if result["unsafe_warranted_atoms"] == 0
        and result["exact"] == result["case_count"]
        and monotonic_violations == 0
        else "AUTHORITY_GATE_FALSIFIED"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["qualify", "science"], required=True)
    parser.add_argument("--candidate", default="research.semantic_authority_machinery_rc8.authority_contract")
    parser.add_argument("--out")
    args = parser.parse_args()
    payload = qualification() if args.mode == "qualify" else science(args.candidate)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.out:
        Path(args.out).write_text(rendered)


if __name__ == "__main__":
    main()
