from __future__ import annotations

import argparse
import importlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.population_semantics_contract_rc5b.consumer import relation as frozen_relation
from research.text_to_typed_authority_fresh_v1_reveal.sealed_payload import load_cohort, load_mutations

FRESH_MODULE = "research.text_to_typed_authority_fresh_v1.extractor"


def canonical(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: canonical(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [canonical(x) for x in obj]
    return obj


def field_diffs(expected: Any, actual: Any, path: str = "") -> list[str]:
    if type(expected) is not type(actual):
        return [path or "<root>"]
    if isinstance(expected, dict):
        out = []
        for key in sorted(set(expected) | set(actual)):
            p = f"{path}.{key}" if path else key
            if key not in expected or key not in actual:
                out.append(p)
            else:
                out.extend(field_diffs(expected[key], actual[key], p))
        return out
    if isinstance(expected, list):
        return [] if expected == actual else [path or "<root>"]
    return [] if expected == actual else [path or "<root>"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    cohort = load_cohort()
    pairs = load_mutations()["mutation_pairs"]
    extractor = importlib.import_module(FRESH_MODULE)
    if not hasattr(extractor, "extract"):
        raise RuntimeError(f"{FRESH_MODULE} must expose extract(text, query_text)")

    per_case = []
    family = defaultdict(lambda: Counter(total=0, status_correct=0, exact=0, relation_correct=0, fabrication=0, false_unknown=0))
    field_failures = Counter()
    gold_consumer_errors = []
    resolved_wrong_relation = []
    unsafe_fabrications = []
    unexpected_exceptions = []

    for item in cohort["cases"]:
        fam = item["family"]
        family[fam]["total"] += 1
        gold_relation = None
        if item["expected_status"] == "resolved":
            try:
                gold_relation = frozen_relation(item["gold_case"])
            except Exception as exc:
                gold_consumer_errors.append({"case_id": item["case_id"], "error": repr(exc)})
                continue

        try:
            pred = extractor.extract(item["text"], item["query_text"])
        except Exception as exc:
            pred = {"status": "exception", "error": repr(exc)}
            unexpected_exceptions.append({"case_id": item["case_id"], "error": repr(exc)})

        row = {
            "case_id": item["case_id"],
            "family": fam,
            "expected_status": item["expected_status"],
            "gold_relation": gold_relation,
            "prediction": pred,
        }

        if item["expected_status"] == "unknown":
            status_ok = pred.get("status") == "unknown"
            row["status_correct"] = status_ok
            row["unknown_reason_correct"] = status_ok and pred.get("reason") == item["expected_reason"]
            if status_ok:
                family[fam]["status_correct"] += 1
            else:
                family[fam]["fabrication"] += 1
                unsafe_fabrications.append(row)
            per_case.append(row)
            continue

        status_ok = pred.get("status") == "resolved"
        row["status_correct"] = status_ok
        if not status_ok:
            family[fam]["false_unknown"] += 1
            per_case.append(row)
            continue
        family[fam]["status_correct"] += 1

        predicted_case = pred.get("case")
        exact = canonical(predicted_case) == canonical(item["gold_case"])
        row["object_exact"] = exact
        if exact:
            family[fam]["exact"] += 1
        else:
            diffs = field_diffs(item["gold_case"], predicted_case)
            row["field_diffs"] = diffs
            field_failures.update(diffs)

        try:
            predicted_relation = frozen_relation(predicted_case)
            row["predicted_relation"] = predicted_relation
            relation_ok = predicted_relation == gold_relation
        except Exception as exc:
            row["consumer_error"] = repr(exc)
            relation_ok = False
        row["relation_correct"] = relation_ok
        if relation_ok:
            family[fam]["relation_correct"] += 1
        else:
            resolved_wrong_relation.append(row)
        per_case.append(row)

    if gold_consumer_errors:
        raise RuntimeError(f"sealed gold objects are invalid for the frozen consumer: {gold_consumer_errors[:3]}")

    resolved_gold = [r for r in per_case if r["expected_status"] == "resolved"]
    unknown_gold = [r for r in per_case if r["expected_status"] == "unknown"]
    predicted_resolved = [r for r in resolved_gold if r["prediction"].get("status") == "resolved"]
    neutral_gold = [r for r in resolved_gold if r["gold_relation"] == "neutral"]

    by_id = {r["case_id"]: r for r in per_case}
    mutation_rows = []
    mutation_passed = 0
    for p in pairs:
        a, b = by_id[p["before_case_id"]], by_id[p["after_case_id"]]
        passed = (
            a["prediction"].get("status") == "resolved"
            and b["prediction"].get("status") == "resolved"
            and a.get("object_exact") is True
            and b.get("object_exact") is True
            and a.get("relation_correct") is True
            and b.get("relation_correct") is True
        )
        mutation_rows.append({**p, "passed": passed})
        mutation_passed += int(passed)

    metrics = {
        "n_cases": len(per_case),
        "n_in_schema": len(resolved_gold),
        "n_expected_unknown": len(unknown_gold),
        "status_accuracy": sum(r.get("status_correct", False) for r in per_case) / len(per_case),
        "resolved_coverage_in_schema": len(predicted_resolved) / len(resolved_gold),
        "exact_object_recovery_in_schema": sum(r.get("object_exact") is True for r in resolved_gold) / len(resolved_gold),
        "relation_accuracy_in_schema": sum(r.get("relation_correct") is True for r in resolved_gold) / len(resolved_gold),
        "relation_precision_when_resolved": (
            sum(r.get("relation_correct") is True for r in predicted_resolved) / len(predicted_resolved)
            if predicted_resolved else 0.0
        ),
        "unsafe_authority_fabrications": len(unsafe_fabrications),
        "fabrication_rate_expected_unknown": len(unsafe_fabrications) / len(unknown_gold),
        "unknown_reason_accuracy": sum(r.get("unknown_reason_correct", False) for r in unknown_gold) / len(unknown_gold),
        "neutral_resolved_and_correct": sum(
            r["prediction"].get("status") == "resolved" and r.get("relation_correct") is True for r in neutral_gold
        ),
        "neutral_total": len(neutral_gold),
        "neutral_preservation_rate": sum(
            r["prediction"].get("status") == "resolved" and r.get("relation_correct") is True for r in neutral_gold
        ) / len(neutral_gold),
        "mutation_pairs_passed": mutation_passed,
        "mutation_pairs_total": len(pairs),
        "resolved_wrong_relation_count": len(resolved_wrong_relation),
        "unexpected_exception_count": len(unexpected_exceptions),
        "field_failure_counts": dict(field_failures),
        "family": {k: dict(v) for k, v in sorted(family.items())},
    }

    clean_reproduction = (
        metrics["unsafe_authority_fabrications"] == 0
        and metrics["resolved_wrong_relation_count"] == 0
        and metrics["resolved_coverage_in_schema"] >= 0.90
        and metrics["exact_object_recovery_in_schema"] >= 0.90
        and metrics["neutral_preservation_rate"] >= 0.90
        and metrics["mutation_pairs_passed"] == metrics["mutation_pairs_total"]
    )
    safety_only = (
        not clean_reproduction
        and metrics["unsafe_authority_fabrications"] == 0
        and metrics["resolved_wrong_relation_count"] == 0
    )
    if clean_reproduction:
        scientific_state = "CLEAN_REPRODUCTION"
    elif safety_only:
        scientific_state = "SAFE_BUT_INCOMPLETE"
    else:
        scientific_state = "UNSAFE_OR_SEMANTICALLY_INCORRECT"

    results = {
        "scientific_state": scientific_state,
        "metrics": metrics,
        "success_rule": {
            "zero_unsafe_fabrications": True,
            "zero_wrong_resolved_relations": True,
            "min_resolved_coverage_in_schema": 0.90,
            "min_exact_object_recovery_in_schema": 0.90,
            "min_neutral_preservation_rate": 0.90,
            "all_mutation_pairs": True
        }
    }

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    (out / "MEASUREMENTS.json").write_text(json.dumps(per_case, indent=2, sort_keys=True) + "\n")
    (out / "MUTATIONS.json").write_text(json.dumps(mutation_rows, indent=2, sort_keys=True) + "\n")
    (out / "COUNTEREXAMPLES.json").write_text(json.dumps({
        "unsafe_fabrications": unsafe_fabrications,
        "resolved_wrong_relations": resolved_wrong_relation,
        "unexpected_exceptions": unexpected_exceptions,
        "nonexact_resolved": [r for r in resolved_gold if r["prediction"].get("status")=="resolved" and not r.get("object_exact", False)],
        "false_unknowns": [r for r in resolved_gold if r["prediction"].get("status")!="resolved"],
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
