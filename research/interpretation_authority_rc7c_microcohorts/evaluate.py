from __future__ import annotations

import argparse
import importlib.util
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from research.interpretation_authority_rc7c_microcohorts.candidate import (
    interpret_only_permission,
    jurisdiction_gate,
)
from research.interpretation_authority_rc7c_microcohorts.cohorts import (
    FIELD_INDEPENDENCE_PAIRS,
    JURISDICTION_CASES,
    ONLY_PERMISSION_CASES,
    ONLY_PERMISSION_MUTATIONS,
)


def _norm(value):
    if isinstance(value, str):
        value = unicodedata.normalize("NFKC", value).lower().strip()
        value = re.sub(r"[.?!]+$", "", value).strip()
        value = re.sub(r"\s+", " ", value)
        value = re.sub(r"^(?:a|an|the)\s+", "", value)
    return value


def _load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _field_signature(receipt, family):
    if not isinstance(receipt, dict) or receipt.get("status") != "receipt" or receipt.get("family") != family:
        return None
    fields = receipt.get("fields")
    if not isinstance(fields, dict):
        return None
    out = {}
    for name, row in fields.items():
        if isinstance(row, dict):
            out[name] = (row.get("status"), _norm(row.get("value")))
    return out


def evaluate_jurisdiction():
    rows = []
    by_category = defaultdict(lambda: {"total": 0, "correct": 0})
    ood_total = ood_correct = supported_total = supported_correct = 0
    for case in JURISDICTION_CASES:
        pred = jurisdiction_gate(case["text"])
        pred_class = "out_of_jurisdiction" if pred.get("status") == "out_of_jurisdiction" else "supported"
        correct = pred_class == case["expected"]
        by_category[case["category"]]["total"] += 1
        by_category[case["category"]]["correct"] += int(correct)
        if case["expected"] == "out_of_jurisdiction":
            ood_total += 1
            ood_correct += int(correct)
        else:
            supported_total += 1
            supported_correct += int(correct)
        rows.append({**case, "prediction": pred, "correct": correct})
    ood_recall = ood_correct / ood_total
    supported_acceptance = supported_correct / supported_total
    category_miss_rates = {k: 1 - v["correct"] / v["total"] for k, v in sorted(by_category.items())}
    worst_category_miss = max(category_miss_rates.values()) if category_miss_rates else 1.0
    supported = ood_recall >= 0.95 and supported_acceptance >= 0.95 and worst_category_miss < 0.25
    state = "JURISDICTION_HARDENING_SUPPORTED" if supported else "JURISDICTION_HARDENING_FALSIFIED"
    return {
        "state": state,
        "case_count": len(rows),
        "ood_recall": ood_recall,
        "supported_control_acceptance": supported_acceptance,
        "category_miss_rates": category_miss_rates,
        "rows": rows,
    }


def _safe_interpret(mod, text, query):
    try:
        return mod.interpret(text, query), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def evaluate_field_independence(mod_a, mod_b):
    rows = []
    stats = {"A": Counter(), "B": Counter()}
    denominators = Counter()
    for pair in FIELD_INDEPENDENCE_PAIRS:
        denominators[pair["kind"]] += 1
        record = {
            "pair_id": pair["pair_id"],
            "family": pair["family"],
            "kind": pair["kind"],
            "expected_changed_fields": pair["expected_changed_fields"],
        }
        for label, mod in (("A", mod_a), ("B", mod_b)):
            before, before_exc = _safe_interpret(mod, pair["before_text"], pair["before_query"])
            after, after_exc = _safe_interpret(mod, pair["after_text"], pair["after_query"])
            bsig = _field_signature(before, pair["family"])
            asig = _field_signature(after, pair["family"])
            if bsig is None or asig is None:
                observed = None
                exact = False
                unintended = None
                stats[label]["unusable"] += 1
            else:
                names = set(bsig) | set(asig)
                observed = sorted(name for name in names if bsig.get(name) != asig.get(name))
                expected = sorted(pair["expected_changed_fields"])
                exact = observed == expected
                unintended = sorted(set(observed) - set(expected))
                stats[label]["usable"] += 1
                stats[label]["exact_pairs"] += int(exact)
                if pair["kind"] == "role_swap" and "polarity" in unintended:
                    stats[label]["role_swap_polarity_coupling"] += 1
                if pair["kind"] == "quantifier_change" and "population" in unintended:
                    stats[label]["quantifier_population_coupling"] += 1
                if pair["kind"] == "paraphrase_invariant" and unintended:
                    stats[label]["paraphrase_unintended_change"] += 1
            record[label] = {
                "before_exception": before_exc,
                "after_exception": after_exc,
                "before_status": before.get("status") if isinstance(before, dict) else None,
                "after_status": after.get("status") if isinstance(after, dict) else None,
                "observed_changed_fields": observed,
                "unintended_fields": unintended,
                "exact_pair": exact,
            }
        rows.append(record)

    summary = {}
    for label in ("A", "B"):
        s = stats[label]
        summary[label] = {
            "pair_count": len(FIELD_INDEPENDENCE_PAIRS),
            "usable_pairs": s["usable"],
            "pair_coverage": s["usable"] / len(FIELD_INDEPENDENCE_PAIRS),
            "exact_pair_rate": s["exact_pairs"] / len(FIELD_INDEPENDENCE_PAIRS),
            "role_swap_polarity_coupling_rate": s["role_swap_polarity_coupling"] / max(1, denominators["role_swap"]),
            "quantifier_population_coupling_rate": s["quantifier_population_coupling"] / max(1, denominators["quantifier_change"]),
            "paraphrase_unintended_change_rate": s["paraphrase_unintended_change"] / max(1, denominators["paraphrase_invariant"]),
            "exceptions_or_unusable": s["unusable"],
        }

    coupling_rates = [summary[label]["role_swap_polarity_coupling_rate"] for label in ("A", "B")] + [
        summary[label]["quantifier_population_coupling_rate"] for label in ("A", "B")
    ]
    if max(coupling_rates) >= 0.25:
        state = "COUPLING_DEFECT_REPRODUCED"
    elif max(coupling_rates) < 0.10:
        state = "COUPLING_DEFECT_NOT_REPRODUCED"
    else:
        state = "COUPLING_DEFECT_INCONCLUSIVE"

    return {
        "state": state,
        "pair_count": len(FIELD_INDEPENDENCE_PAIRS),
        "kind_denominators": dict(denominators),
        "implementations": summary,
        "rows": rows,
    }


def _score_only_case(case):
    pred = interpret_only_permission(case["text"], case["query"])
    exact = total = unsafe = 0
    semantic_unknown_total = semantic_unknown_exact = 0
    insufficient_total = insufficient_exact = 0
    only_total = only_exact = 0
    field_rows = []
    pred_fields = pred.get("fields", {}) if isinstance(pred, dict) and pred.get("status") == "receipt" else {}

    for field, (gold_status, gold_value) in case["gold"].items():
        total += 1
        prow = pred_fields.get(field) if isinstance(pred_fields, dict) else None
        pred_status = prow.get("status") if isinstance(prow, dict) else None
        pred_value = _norm(prow.get("value")) if isinstance(prow, dict) else None
        gold_value_n = _norm(gold_value)
        field_exact = pred_status == gold_status and pred_value == gold_value_n
        exact += int(field_exact)
        pred_semantic = pred_status in {"established", "semantic_unknown"}
        if pred_semantic and not field_exact:
            unsafe += 1
        if gold_status == "semantic_unknown":
            semantic_unknown_total += 1
            semantic_unknown_exact += int(field_exact)
        if gold_status == "insufficient_authority":
            insufficient_total += 1
            insufficient_exact += int(pred_status == "insufficient_authority" and pred_value is None)
        if field == "only_population_may":
            only_total += 1
            only_exact += int(field_exact)
        field_rows.append({
            "field": field,
            "gold_status": gold_status,
            "gold_value": gold_value_n,
            "pred_status": pred_status,
            "pred_value": pred_value,
            "exact": field_exact,
            "unsafe": bool(pred_semantic and not field_exact),
        })

    return {
        "case_id": case["case_id"],
        "kind": case["kind"],
        "prediction_status": pred.get("status") if isinstance(pred, dict) else None,
        "field_exact": exact,
        "field_total": total,
        "unsafe_fields": unsafe,
        "semantic_unknown_total": semantic_unknown_total,
        "semantic_unknown_exact": semantic_unknown_exact,
        "insufficient_total": insufficient_total,
        "insufficient_exact": insufficient_exact,
        "only_total": only_total,
        "only_exact": only_exact,
        "field_rows": field_rows,
    }


def _candidate_changes(before, after):
    bsig = _field_signature(before, "only_permission")
    asig = _field_signature(after, "only_permission")
    if bsig is None or asig is None:
        return None
    return sorted(name for name in set(bsig) | set(asig) if bsig.get(name) != asig.get(name))


def evaluate_only_permission():
    rows = [_score_only_case(case) for case in ONLY_PERMISSION_CASES]
    field_exact = sum(r["field_exact"] for r in rows)
    field_total = sum(r["field_total"] for r in rows)
    unsafe = sum(r["unsafe_fields"] for r in rows)
    semantic_unknown_total = sum(r["semantic_unknown_total"] for r in rows)
    semantic_unknown_exact = sum(r["semantic_unknown_exact"] for r in rows)
    insufficient_total = sum(r["insufficient_total"] for r in rows)
    insufficient_exact = sum(r["insufficient_exact"] for r in rows)
    only_total = sum(r["only_total"] for r in rows)
    only_exact = sum(r["only_exact"] for r in rows)

    mutation_rows = []
    mutation_passed = 0
    for mutation in ONLY_PERMISSION_MUTATIONS:
        before = interpret_only_permission(mutation["before_text"], mutation["query"])
        after = interpret_only_permission(mutation["after_text"], mutation["query"])
        changed = _candidate_changes(before, after)
        passed = changed == sorted(mutation["expected_changed_fields"])
        mutation_passed += int(passed)
        mutation_rows.append({
            "mutation_id": mutation["mutation_id"],
            "expected_changed_fields": sorted(mutation["expected_changed_fields"]),
            "observed_changed_fields": changed,
            "passed": passed,
        })

    metrics = {
        "case_count": len(rows),
        "field_status_value_recovery": field_exact / field_total,
        "unsafe_semantic_field_assignments": unsafe,
        "semantic_unknown_recall": semantic_unknown_exact / semantic_unknown_total if semantic_unknown_total else None,
        "insufficient_authority_recall": insufficient_exact / insufficient_total if insufficient_total else None,
        "necessary_condition_recognition": only_exact / only_total if only_total else None,
        "mutations_passed": mutation_passed,
        "mutations_total": len(ONLY_PERMISSION_MUTATIONS),
    }
    supported = (
        unsafe == 0
        and metrics["field_status_value_recovery"] >= 0.95
        and (metrics["semantic_unknown_recall"] or 0) >= 0.95
        and (metrics["insufficient_authority_recall"] or 0) >= 0.95
        and (metrics["necessary_condition_recognition"] or 0) >= 0.95
        and mutation_passed == len(ONLY_PERMISSION_MUTATIONS)
    )
    state = "ONLY_PERMISSION_LOCAL_RULES_SUPPORTED" if supported else "ONLY_PERMISSION_LOCAL_RULES_FALSIFIED"
    return {"state": state, "metrics": metrics, "rows": rows, "mutations": mutation_rows}


def _write_report(result, path: Path):
    jurisdiction = result["jurisdiction"]
    field_independence = result["field_independence"]
    only_permission = result["only_permission"]
    lines = [
        "# RC7C Interpretation Boundary Microcohort Results",
        "",
        f"Overall terminal state: **`{result['overall_state']}`**",
        "",
        "## Jurisdiction gate",
        f"- state: `{jurisdiction['state']}`",
        f"- OOD recall: {jurisdiction['ood_recall']:.3f}",
        f"- supported-control acceptance: {jurisdiction['supported_control_acceptance']:.3f}",
        "- category miss rates:",
    ]
    for key, value in jurisdiction["category_miss_rates"].items():
        lines.append(f"  - {key}: {value:.3f}")
    lines += ["", "## Field-independence metamorphics", f"- state: `{field_independence['state']}`"]
    for label, metrics in field_independence["implementations"].items():
        lines += [
            f"- {label} pair coverage: {metrics['pair_coverage']:.3f}",
            f"- {label} exact-pair rate: {metrics['exact_pair_rate']:.3f}",
            f"- {label} role-swap→polarity coupling: {metrics['role_swap_polarity_coupling_rate']:.3f}",
            f"- {label} quantifier→population coupling: {metrics['quantifier_population_coupling_rate']:.3f}",
            f"- {label} paraphrase unintended-change rate: {metrics['paraphrase_unintended_change_rate']:.3f}",
        ]
    lines += ["", "## Only-permission bounded interpreter", f"- state: `{only_permission['state']}`"]
    for key, value in only_permission["metrics"].items():
        lines.append(f"- {key}: {value:.3f}" if isinstance(value, float) else f"- {key}: {value}")
    lines += [
        "",
        "## Interpretation boundary",
        "This post-reveal hardening experiment can support or falsify local interventions only. It cannot establish independent consumability of a successor contract.",
        "",
        "No production authorization.",
    ]
    path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--a-module-path", required=True)
    parser.add_argument("--b-module-path", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    mod_a = _load_module(args.a_module_path, "rc7c_sut_a")
    mod_b = _load_module(args.b_module_path, "rc7c_sut_b")

    jurisdiction = evaluate_jurisdiction()
    field_independence = evaluate_field_independence(mod_a, mod_b)
    only_permission = evaluate_only_permission()

    if jurisdiction["state"] == "JURISDICTION_HARDENING_SUPPORTED" and only_permission["state"] == "ONLY_PERMISSION_LOCAL_RULES_SUPPORTED":
        overall = "LOCAL_HARDENING_SUPPORTED"
    elif jurisdiction["state"] == "JURISDICTION_HARDENING_SUPPORTED" or only_permission["state"] == "ONLY_PERMISSION_LOCAL_RULES_SUPPORTED":
        overall = "PARTIAL_LOCAL_HARDENING"
    else:
        overall = "LOCAL_HARDENING_FALSIFIED"

    result = {
        "overall_state": overall,
        "jurisdiction": jurisdiction,
        "field_independence": field_independence,
        "only_permission": only_permission,
        "claim_boundary": {"context_free": False, "independent_reproduction": False, "production_authorization": False},
    }

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (out / "JURISDICTION_ROWS.json").write_text(json.dumps(jurisdiction["rows"], indent=2, sort_keys=True) + "\n")
    (out / "FIELD_INDEPENDENCE_ROWS.json").write_text(json.dumps(field_independence["rows"], indent=2, sort_keys=True) + "\n")
    (out / "ONLY_PERMISSION_ROWS.json").write_text(json.dumps(only_permission["rows"], indent=2, sort_keys=True) + "\n")
    (out / "ONLY_PERMISSION_MUTATIONS.json").write_text(json.dumps(only_permission["mutations"], indent=2, sort_keys=True) + "\n")
    _write_report(result, out / "REPORT.md")
    print(json.dumps({
        "overall_state": overall,
        "jurisdiction_state": jurisdiction["state"],
        "field_independence_state": field_independence["state"],
        "only_permission_state": only_permission["state"],
        "jurisdiction_ood_recall": jurisdiction["ood_recall"],
        "jurisdiction_supported_acceptance": jurisdiction["supported_control_acceptance"],
        "only_permission_metrics": only_permission["metrics"],
        "field_independence": field_independence["implementations"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
