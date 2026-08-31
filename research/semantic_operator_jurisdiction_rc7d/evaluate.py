"""RC7D evaluator for semantic-operator jurisdiction and composition."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
from collections import Counter, defaultdict

from research.semantic_operator_jurisdiction_rc7d import candidate

EXPECTED_CASE_COUNT = 74
CANDIDATE_FREEZE = "b5b04485cb1e09f025017e25cd6d008e6c5030f6"
COHORT_DEFECTIVE_FREEZE = "4a5148bce7d861815a08fcdf8623a7e9e28fa367"


def load_cohort() -> list[dict]:
    p = Path(__file__).with_name("cohort.py")
    src = p.read_text(encoding="utf-8")
    needle = "assert len(CASES) == 86, len(CASES)"
    assert src.count(needle) == 1, "unauthorized cohort shape"
    patched = src.replace(needle, "assert len(CASES) == 74, len(CASES)")
    ns: dict = {"__name__": "rc7d_cohort_materialized"}
    exec(compile(patched, str(p), "exec"), ns)
    cases = ns["CASES"]
    assert len(cases) == EXPECTED_CASE_COUNT
    return cases


def canon(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def claimed_atoms(output: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = defaultdict(list)
    for r in output.get("receipts", []):
        if r.get("status") == "CLAIMED":
            out[r["dimension"]].extend(r.get("atoms", []))
    return dict(out)


def _composition_map(output: dict) -> dict[tuple[str, str], str]:
    ans = {}
    for row in output.get("pair_decisions", []):
        ans[tuple(sorted(row["dimensions"]))] = row["decision"]
    return ans


def score_case(case: dict, output: dict) -> dict:
    gold = case["gold"]
    gold_dims = set(case["gold_dimensions"])
    pred_atoms = claimed_atoms(output)
    pred_dims = set(pred_atoms)

    raw_ok = output.get("raw_source") == case["text"] and output.get("raw_source_sha256") == hashlib.sha256(case["text"].encode()).hexdigest()

    gold_atom_sets = {d: {canon(a) for a in atoms} for d, atoms in gold.items()}
    pred_atom_sets = {d: {canon(a) for a in atoms} for d, atoms in pred_atoms.items()}

    correct_atoms = 0
    missing_atoms = 0
    unsafe_atoms = 0
    atom_rows = []
    for dim in sorted(gold_dims | pred_dims):
        gs = gold_atom_sets.get(dim, set())
        ps = pred_atom_sets.get(dim, set())
        correct = len(gs & ps)
        missing = len(gs - ps)
        unsafe = len(ps - gs)
        correct_atoms += correct
        missing_atoms += missing
        unsafe_atoms += unsafe
        atom_rows.append({"dimension": dim, "correct": correct, "missing": missing, "unsafe": unsafe, "gold": len(gs), "predicted": len(ps)})

    false_dims = sorted(pred_dims - gold_dims)
    missing_dims = sorted(gold_dims - pred_dims)

    expected_comp = {tuple(row["dimensions"]): row["expected"] for row in case.get("composition", [])}
    observed_comp = _composition_map(output)
    composition_errors = []
    composition_correct = 0
    for pair, expected in expected_comp.items():
        observed = observed_comp.get(pair)
        if observed == expected:
            composition_correct += 1
        else:
            composition_errors.append({"dimensions": list(pair), "expected": expected, "observed": observed})
    for pair, observed in observed_comp.items():
        if pair not in expected_comp and observed != "unresolved":
            composition_errors.append({"dimensions": list(pair), "expected": "unresolved", "observed": observed})

    # A residue signal does not prove semantic completeness. It only proves that a
    # missed gold dimension was not accompanied by a claim that all source text was consumed.
    residue_signal = bool(output.get("surface_residue")) or any(r.get("status") == "UNRESOLVED" for r in output.get("receipts", []))
    residue_hits = len(missing_dims) if residue_signal else 0

    conflict_preserved = None
    if case["group"] == "internal_conflict":
        conflict_preserved = False
        for dim, atoms in gold.items():
            receipts = [r for r in output.get("receipts", []) if r.get("dimension") == dim]
            if any(r.get("status") == "UNRESOLVED" for r in receipts):
                conflict_preserved = True
            if gold_atom_sets[dim].issubset(pred_atom_sets.get(dim, set())) and len(gold_atom_sets[dim]) > 1:
                conflict_preserved = True

    q_audit = output.get("quantifier_audit", {})
    q_audit_row = None
    if "quantifier" in gold_dims:
        ga = gold_atom_sets["quantifier"]
        primary = q_audit.get("primary") or {}
        audit = q_audit.get("audit") or {}
        primary_set = {canon(a) for a in primary.get("atoms", [])} if primary.get("status") == "CLAIMED" else set()
        audit_set = {canon(a) for a in audit.get("atoms", [])} if audit.get("status") == "CLAIMED" else set()
        q_audit_row = {
            "agreement": q_audit.get("agreement"),
            "primary_exact": primary_set == ga,
            "audit_exact": audit_set == ga,
            "primary_status": primary.get("status"),
            "audit_status": audit.get("status"),
        }

    return {
        "case_id": case["case_id"],
        "group": case["group"],
        "raw_source": case["text"],
        "raw_source_preserved": raw_ok,
        "gold_dimensions": sorted(gold_dims),
        "predicted_dimensions": sorted(pred_dims),
        "correct_dimension_count": len(gold_dims & pred_dims),
        "missing_dimensions": missing_dims,
        "false_dimensions": false_dims,
        "gold_atom_count": sum(len(v) for v in gold.values()),
        "predicted_atom_count": sum(len(v) for v in pred_atoms.values()),
        "correct_atom_count": correct_atoms,
        "missing_atom_count": missing_atoms,
        "unsafe_atom_count": unsafe_atoms,
        "atom_rows": atom_rows,
        "composition_expected": len(expected_comp),
        "composition_correct": composition_correct,
        "composition_errors": composition_errors,
        "residue_signal": residue_signal,
        "residue_hits": residue_hits,
        "conflict_preserved": conflict_preserved,
        "specialists_invoked": output.get("specialists_invoked", 0),
        "fallback": output.get("fallback", False),
        "quantifier_audit": q_audit_row,
        "full_output": output,
    }


def aggregate(name: str, rows: list[dict]) -> dict:
    gold_dims = sum(len(r["gold_dimensions"]) for r in rows)
    pred_dims = sum(len(r["predicted_dimensions"]) for r in rows)
    correct_dims = sum(r["correct_dimension_count"] for r in rows)
    false_dims = sum(len(r["false_dimensions"]) for r in rows)
    missing_dims = sum(len(r["missing_dimensions"]) for r in rows)
    gold_atoms = sum(r["gold_atom_count"] for r in rows)
    pred_atoms = sum(r["predicted_atom_count"] for r in rows)
    correct_atoms = sum(r["correct_atom_count"] for r in rows)
    unsafe_atoms = sum(r["unsafe_atom_count"] for r in rows)
    expected_comp = sum(r["composition_expected"] for r in rows)
    correct_comp = sum(r["composition_correct"] for r in rows)
    comp_errors = sum(len(r["composition_errors"]) for r in rows)
    residue_possible = sum(len(r["missing_dimensions"]) for r in rows)
    residue_hits = sum(r["residue_hits"] for r in rows)
    conflicts = [r for r in rows if r["conflict_preserved"] is not None]
    conflict_ok = sum(bool(r["conflict_preserved"]) for r in conflicts)

    mixed = [r for r in rows if len(r["gold_dimensions"]) > 1]
    mixed_gold = sum(len(r["gold_dimensions"]) for r in mixed)
    mixed_correct = sum(r["correct_dimension_count"] for r in mixed)

    qrows = [r["quantifier_audit"] for r in rows if r["quantifier_audit"] is not None]
    q_disagree = [q for q in qrows if q["agreement"] is False]
    q_agree = [q for q in qrows if q["agreement"] is True]
    q_disagree_error = sum(not (q["primary_exact"] and q["audit_exact"]) for q in q_disagree)
    q_agree_error = sum(not (q["primary_exact"] and q["audit_exact"]) for q in q_agree)

    return {
        "architecture": name,
        "case_count": len(rows),
        "raw_source_preservation": sum(r["raw_source_preserved"] for r in rows) / len(rows),
        "semantic_dimension_recall": correct_dims / gold_dims if gold_dims else 1.0,
        "typed_atom_recall": correct_atoms / gold_atoms if gold_atoms else 1.0,
        "false_jurisdiction_claim_rate": false_dims / pred_dims if pred_dims else 0.0,
        "false_jurisdiction_case_rate": sum(bool(r["false_dimensions"]) for r in rows) / len(rows),
        "unsafe_semantic_atom_rate": unsafe_atoms / pred_atoms if pred_atoms else 0.0,
        "unsafe_semantic_atom_count": unsafe_atoms,
        "unsafe_case_rate": sum(r["unsafe_atom_count"] > 0 for r in rows) / len(rows),
        "missing_dimension_count": missing_dims,
        "residue_signal_recall": residue_hits / residue_possible if residue_possible else 1.0,
        "composition_precision_recall": correct_comp / expected_comp if expected_comp else 1.0,
        "composition_error_count": comp_errors,
        "conflict_preservation_recall": conflict_ok / len(conflicts) if conflicts else 1.0,
        "overlap_conflict_detection_recall": (correct_comp + conflict_ok) / (expected_comp + len(conflicts)) if (expected_comp + len(conflicts)) else 1.0,
        "mixed_semantic_dimension_recall": mixed_correct / mixed_gold if mixed_gold else 1.0,
        "mixed_correct_dimensions": mixed_correct,
        "mixed_gold_dimensions": mixed_gold,
        "average_specialists_invoked": sum(r["specialists_invoked"] for r in rows) / len(rows),
        "fallback_rate": sum(r["fallback"] for r in rows) / len(rows),
        "quantifier_audit": {
            "case_count": len(qrows),
            "disagreement_count": len(q_disagree),
            "agreement_count": len(q_agree),
            "error_rate_when_disagree": q_disagree_error / len(q_disagree) if q_disagree else None,
            "error_rate_when_agree": q_agree_error / len(q_agree) if q_agree else None,
        },
    }


def run_architecture(cases: list[dict], name: str) -> tuple[dict, list[dict]]:
    fn = {
        "single_router": candidate.single_router,
        "broadcast_all": candidate.broadcast_all,
        "conservative_router_fallback": candidate.conservative_router_fallback,
        "greedy_claim": candidate.greedy_claim,
        "union_without_composition_governor": candidate.union_without_composition_governor,
    }[name]
    rows = [score_case(case, fn(case["text"])) for case in cases]
    return aggregate(name, rows), rows


def stress(cases: list[dict]) -> list[dict]:
    out = []
    for n in (2, 4, 6, 8):
        rows = [score_case(case, candidate.broadcast_all(case["text"], bank_size=n)) for case in cases]
        agg = aggregate(f"broadcast_{n}", rows)
        out.append({
            "bank_size": n,
            "false_jurisdiction_claim_rate": agg["false_jurisdiction_claim_rate"],
            "false_jurisdiction_case_rate": agg["false_jurisdiction_case_rate"],
            "unsafe_semantic_atom_rate": agg["unsafe_semantic_atom_rate"],
            "unsafe_case_rate": agg["unsafe_case_rate"],
            "semantic_dimension_recall": agg["semantic_dimension_recall"],
        })
    return out


def determine_state(metrics: dict[str, dict], stress_rows: list[dict]) -> str:
    b = metrics["broadcast_all"]
    f = metrics["conservative_router_fallback"]
    s = metrics["single_router"]
    g = metrics["greedy_claim"]
    u = metrics["union_without_composition_governor"]

    if any(m["raw_source_preservation"] != 1.0 for m in metrics.values()):
        return "APPARATUS_INVALID"

    st2, st8 = stress_rows[0], stress_rows[-1]
    multiple_overclaim = (
        st8["false_jurisdiction_claim_rate"] > 0.02
        and st8["false_jurisdiction_claim_rate"] > st2["false_jurisdiction_claim_rate"] + 0.02
    ) or (
        st8["unsafe_case_rate"] > st2["unsafe_case_rate"] + 0.05
    )
    if multiple_overclaim:
        return "MULTIPLE_TESTING_OVERCLAIM"

    if b["composition_error_count"] > 0 or b["overlap_conflict_detection_recall"] < 0.90:
        return "COMPOSITION_GOVERNANCE_INSUFFICIENT"

    broadcast_supported = (
        b["semantic_dimension_recall"] >= 0.95
        and b["typed_atom_recall"] >= 0.90
        and b["false_jurisdiction_claim_rate"] <= 0.02
        and b["unsafe_semantic_atom_count"] == 0
        and b["composition_error_count"] == 0
        and b["residue_signal_recall"] >= 0.95
        and b["overlap_conflict_detection_recall"] >= 0.90
        and b["mixed_correct_dimensions"] > s["mixed_correct_dimensions"]
        and (g["unsafe_case_rate"] > b["unsafe_case_rate"] or u["composition_error_count"] > b["composition_error_count"])
    )
    if broadcast_supported:
        return "OPERATOR_BANK_SUPPORTED_WITH_BOUNDS"

    fallback_supported = (
        f["semantic_dimension_recall"] >= 0.95
        and f["false_jurisdiction_claim_rate"] <= 0.02
        and f["unsafe_semantic_atom_count"] == 0
        and f["composition_error_count"] == 0
        and f["average_specialists_invoked"] < b["average_specialists_invoked"]
    )
    if fallback_supported:
        return "ROUTED_FALLBACK_SUPPORTED_WITH_BOUNDS"

    if b["unsafe_semantic_atom_count"] == 0 and b["false_jurisdiction_claim_rate"] <= 0.02 and b["semantic_dimension_recall"] < 0.95:
        return "SPECIALIST_COVERAGE_INSUFFICIENT"

    if s["mixed_correct_dimensions"] >= b["mixed_correct_dimensions"] or (b["mixed_correct_dimensions"] > s["mixed_correct_dimensions"] and (b["unsafe_semantic_atom_count"] > 0 or b["false_jurisdiction_claim_rate"] > 0.02)):
        return "HYPOTHESIS_FALSIFIED"

    return "HYPOTHESIS_FALSIFIED"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    cases = load_cohort()
    names = ["single_router", "broadcast_all", "conservative_router_fallback", "greedy_claim", "union_without_composition_governor"]
    metrics: dict[str, dict] = {}
    all_rows: dict[str, list[dict]] = {}
    for name in names:
        metrics[name], all_rows[name] = run_architecture(cases, name)

    stress_rows = stress(cases)
    state = determine_state(metrics, stress_rows)

    group_table: dict[str, dict] = {}
    groups = sorted({c["group"] for c in cases})
    for group in groups:
        subset_ids = {c["case_id"] for c in cases if c["group"] == group}
        group_table[group] = {}
        for name in ("single_router", "broadcast_all", "conservative_router_fallback"):
            rs = [r for r in all_rows[name] if r["case_id"] in subset_ids]
            group_table[group][name] = aggregate(name, rs)

    disagreements = []
    by_id = {name: {r["case_id"]: r for r in rows} for name, rows in all_rows.items()}
    for case in cases:
        cid = case["case_id"]
        s = by_id["single_router"][cid]
        b = by_id["broadcast_all"][cid]
        f = by_id["conservative_router_fallback"][cid]
        if (s["predicted_dimensions"] != b["predicted_dimensions"] or b["predicted_dimensions"] != f["predicted_dimensions"] or s["unsafe_atom_count"] != b["unsafe_atom_count"]):
            disagreements.append({
                "case_id": cid,
                "group": case["group"],
                "raw_source": case["text"],
                "gold_dimensions": case["gold_dimensions"],
                "single_router": {k: s[k] for k in ("predicted_dimensions", "missing_dimensions", "false_dimensions", "unsafe_atom_count")},
                "broadcast_all": {k: b[k] for k in ("predicted_dimensions", "missing_dimensions", "false_dimensions", "unsafe_atom_count")},
                "fallback": {k: f[k] for k in ("predicted_dimensions", "missing_dimensions", "false_dimensions", "unsafe_atom_count")},
            })

    counterexamples = {
        name: [
            {
                "case_id": r["case_id"],
                "group": r["group"],
                "raw_source": r["raw_source"],
                "missing_dimensions": r["missing_dimensions"],
                "false_dimensions": r["false_dimensions"],
                "unsafe_atom_count": r["unsafe_atom_count"],
                "composition_errors": r["composition_errors"],
                "conflict_preserved": r["conflict_preserved"],
            }
            for r in rows
            if r["missing_dimensions"] or r["false_dimensions"] or r["unsafe_atom_count"] or r["composition_errors"] or r["conflict_preserved"] is False
        ]
        for name, rows in all_rows.items()
    }

    result = {
        "scientific_state": state,
        "claim_boundary": {"context_free": False, "independent_reproduction": False, "production_authorization": False, "llm_used": False},
        "candidate_freeze": CANDIDATE_FREEZE,
        "cohort_freeze_with_assertion_typo": COHORT_DEFECTIVE_FREEZE,
        "case_count": len(cases),
        "metrics": metrics,
        "operator_count_stress": stress_rows,
        "group_metrics": group_table,
        "interpretation_notes": {
            "raw_source_preservation_is_not_semantic_completeness": True,
            "residue_signal_is_nonsemantic_and_does_not_prove_meaning_coverage": True,
            "quantifier_duplicate_agreement_is_risk_evidence_not_truth": True,
        },
    }

    (outdir / "RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (outdir / "CASE_ROWS.json").write_text(json.dumps(all_rows, indent=2, sort_keys=True) + "\n")
    (outdir / "STRESS.json").write_text(json.dumps(stress_rows, indent=2, sort_keys=True) + "\n")
    (outdir / "DISAGREEMENTS.json").write_text(json.dumps(disagreements, indent=2, sort_keys=True) + "\n")
    (outdir / "COUNTEREXAMPLES.json").write_text(json.dumps(counterexamples, indent=2, sort_keys=True) + "\n")

    report = [
        "# RC7D Semantic Operator Jurisdiction and Composition Results",
        "",
        f"Scientific state: **`{state}`**",
        "",
        "No LLM or learned semantic router was used.",
        "",
    ]
    for name in ("single_router", "broadcast_all", "conservative_router_fallback"):
        m = metrics[name]
        report += [
            f"## {name}",
            f"- semantic dimension recall: {m['semantic_dimension_recall']:.3f}",
            f"- typed atom recall: {m['typed_atom_recall']:.3f}",
            f"- false jurisdiction claim rate: {m['false_jurisdiction_claim_rate']:.3f}",
            f"- unsafe semantic atom count: {m['unsafe_semantic_atom_count']}",
            f"- overlap/conflict detection recall: {m['overlap_conflict_detection_recall']:.3f}",
            f"- mixed-semantic dimension recall: {m['mixed_semantic_dimension_recall']:.3f}",
            f"- average specialists invoked: {m['average_specialists_invoked']:.2f}",
            f"- fallback rate: {m['fallback_rate']:.3f}",
            "",
        ]
    report += ["## Operator-count stress"]
    for row in stress_rows:
        report.append(f"- bank {row['bank_size']}: false-claim case rate={row['false_jurisdiction_case_rate']:.3f}, unsafe-case rate={row['unsafe_case_rate']:.3f}, dimension recall={row['semantic_dimension_recall']:.3f}")
    report += ["", "## Boundary", "This is post-reveal diagnostic hardening. It does not establish independent consumability or production authority."]
    (outdir / "REPORT.md").write_text("\n".join(report) + "\n")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
