"""Retrospective RC7D-D typed measurement-comparison diagnostic.

The taxonomy is applied without gold. Gold is consulted only after each pair
relation has been frozen in-memory, to characterize the empirical error
composition of relation classes. No winner or authority is selected.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

from research.semantic_operator_jurisdiction_rc7d_c.equivalence import canonical_atom
from research.semantic_operator_jurisdiction_rc7d_d import cohort_final as cohort
from research.semantic_operator_jurisdiction_rc7d_d import multi_readers as readers
from research.semantic_operator_jurisdiction_rc7d_d import role_reader_v2
from research.semantic_measurement_comparison_calibration_rc1.taxonomy import compare_receipts, VERSION as TAXONOMY_VERSION

BASE_EVIDENCE = "253af5313e93932875bdd5956ac46246f3796271"
PREREGISTRATION = "af22cc1426f06179209ad8c73a125aacda9b38c2"


def key(atom: dict) -> str:
    return json.dumps(canonical_atom(atom), sort_keys=True, separators=(",", ":"))


def gold_set(case: dict, dimension: str) -> set[str]:
    return {key(a) for a in case.get("gold", {}).get(dimension, [])}


def measurement_receipts(text: str) -> list[dict]:
    out = readers.run_single(text)
    receipts = list(out["receipts"])
    receipts.extend(fn(text) for fn in readers.ALT_READERS.values())
    receipts.append(role_reader_v2.read(text))
    return receipts


def atom_set(receipt: dict) -> set[str]:
    if receipt.get("status") != "CLAIMED":
        return set()
    return {key(a) for a in receipt.get("atoms", [])}


def side_correct(pred: set[str], gold: set[str]) -> bool:
    return bool(pred) and pred <= gold


def score_outcome(left: dict, right: dict, gold: set[str]) -> str:
    """Gold-aware evaluator label; never used by taxonomy classification."""
    lp, rp = atom_set(left), atom_set(right)
    lc, rc = side_correct(lp, gold), side_correct(rp, gold)
    l_active, r_active = bool(lp), bool(rp)

    if l_active and r_active:
        if lc and rc:
            return "BOTH_CORRECT" if lp == rp else "BOTH_VALID_DISTINCT"
        if lc and not rc:
            return "LEFT_ONLY_CORRECT"
        if rc and not lc:
            return "RIGHT_ONLY_CORRECT"
        if lp == rp:
            return "BOTH_WRONG_SHARED"
        return "BOTH_WRONG_DIFFERENT"

    if l_active != r_active:
        active_pred = lp if l_active else rp
        active_correct = side_correct(active_pred, gold)
        if gold:
            return "CORRECT_CLAIM_VS_OMISSION" if active_correct else "WRONG_CLAIM_VS_OMISSION"
        return "WRONG_CLAIM_VS_CORRECT_INACTIVE"

    if gold:
        return "BOTH_OMIT_GOLD"
    return "BOTH_CORRECT_INACTIVE"


def outcome_flags(outcome: str) -> dict[str, bool]:
    any_error = outcome in {
        "LEFT_ONLY_CORRECT", "RIGHT_ONLY_CORRECT", "BOTH_WRONG_SHARED",
        "BOTH_WRONG_DIFFERENT", "WRONG_CLAIM_VS_OMISSION",
        "WRONG_CLAIM_VS_CORRECT_INACTIVE",
    }
    shared_error = outcome == "BOTH_WRONG_SHARED"
    exactly_one_correct = outcome in {"LEFT_ONLY_CORRECT", "RIGHT_ONLY_CORRECT", "CORRECT_CLAIM_VS_OMISSION"}
    both_correct = outcome in {"BOTH_CORRECT", "BOTH_VALID_DISTINCT"}
    return {
        "any_error": any_error,
        "shared_error": shared_error,
        "exactly_one_correct": exactly_one_correct,
        "both_correct": both_correct,
    }


def reader_profiles(cases: list[dict], receipts_by_case: list[list[dict]]) -> dict:
    stats = defaultdict(lambda: defaultdict(lambda: {
        "cases": 0, "gold_present_cases": 0, "claimed_cases": 0,
        "gold_atoms": 0, "correct_atoms": 0, "wrong_atoms": 0,
        "unique_correct_atoms": 0,
    }))

    for case, receipts in zip(cases, receipts_by_case):
        by_dim = defaultdict(list)
        for r in receipts:
            by_dim[r["dimension"]].append(r)
        all_dims = set(by_dim) | set(case.get("gold", {}))
        for dimension in all_dims:
            gold = gold_set(case, dimension)
            correct_by_reader: dict[str, set[str]] = {}
            for r in by_dim.get(dimension, []):
                rid = r["operator_id"]
                bucket = stats[rid][case["group"]]
                bucket["cases"] += 1
                if gold:
                    bucket["gold_present_cases"] += 1
                    bucket["gold_atoms"] += len(gold)
                pred = atom_set(r)
                if pred:
                    bucket["claimed_cases"] += 1
                good = pred & gold
                bad = pred - gold
                bucket["correct_atoms"] += len(good)
                bucket["wrong_atoms"] += len(bad)
                correct_by_reader[rid] = good
            for rid, good in correct_by_reader.items():
                others = set().union(*(v for k, v in correct_by_reader.items() if k != rid)) if len(correct_by_reader) > 1 else set()
                stats[rid][case["group"]]["unique_correct_atoms"] += len(good - others)

    out = {}
    for rid, groups in stats.items():
        out[rid] = {}
        for group, s in groups.items():
            proposed = s["correct_atoms"] + s["wrong_atoms"]
            out[rid][group] = {
                **s,
                "proposal_precision": s["correct_atoms"] / proposed if proposed else None,
                "atom_recall": s["correct_atoms"] / s["gold_atoms"] if s["gold_atoms"] else None,
            }
    return out


def evaluate(outdir: Path) -> dict:
    cases = cohort.CASES
    receipts_by_case = [measurement_receipts(c["text"]) for c in cases]
    rows = []

    for case, receipts in zip(cases, receipts_by_case):
        by_dim = defaultdict(list)
        for r in receipts:
            by_dim[r["dimension"]].append(r)
        for dimension, dim_receipts in by_dim.items():
            if len(dim_receipts) < 2:
                continue
            for left, right in itertools.combinations(dim_receipts, 2):
                comparison = compare_receipts(left, right)
                if comparison is None:
                    continue
                # Taxonomy classification is complete before this gold access.
                outcome = score_outcome(left, right, gold_set(case, dimension))
                rows.append({
                    "case_id": case["case_id"],
                    "group": case["group"],
                    "dimension": dimension,
                    "raw_source": case["text"],
                    "left_reader": left["operator_id"],
                    "right_reader": right["operator_id"],
                    "relation": comparison["relation"],
                    "facets": comparison["facets"],
                    "left_status": comparison["left_status"],
                    "right_status": comparison["right_status"],
                    "left_atoms": comparison["left_atoms"],
                    "right_atoms": comparison["right_atoms"],
                    "winner": comparison["winner"],
                    "outcome": outcome,
                    **outcome_flags(outcome),
                })

    rel = defaultdict(lambda: {"count": 0, "any_error": 0, "shared_error": 0, "exactly_one_correct": 0, "both_correct": 0, "outcomes": defaultdict(int)})
    for row in rows:
        s = rel[row["relation"]]
        s["count"] += 1
        s["any_error"] += int(row["any_error"])
        s["shared_error"] += int(row["shared_error"])
        s["exactly_one_correct"] += int(row["exactly_one_correct"])
        s["both_correct"] += int(row["both_correct"])
        s["outcomes"][row["outcome"]] += 1

    relation_summary = {}
    for relation, s in rel.items():
        n = s["count"]
        relation_summary[relation] = {
            "count": n,
            "p_any_error": s["any_error"] / n,
            "p_shared_error": s["shared_error"] / n,
            "p_exactly_one_correct": s["exactly_one_correct"] / n,
            "p_both_correct": s["both_correct"] / n,
            "outcomes": dict(sorted(s["outcomes"].items())),
        }

    raw_agreement = [r for r in rows if r["relation"] in {"EXACT_AGREEMENT", "SEMANTIC_EQUIVALENCE"}]
    raw_disagreement = [r for r in rows if r["relation"] not in {"EXACT_AGREEMENT", "SEMANTIC_EQUIVALENCE", "JURISDICTION_DISAGREEMENT"}]

    def pooled(rs: list[dict]) -> dict:
        n = len(rs)
        return {
            "count": n,
            "p_any_error": sum(r["any_error"] for r in rs) / n if n else None,
            "p_shared_error": sum(r["shared_error"] for r in rs) / n if n else None,
            "p_exactly_one_correct": sum(r["exactly_one_correct"] for r in rs) / n if n else None,
            "p_both_correct": sum(r["both_correct"] for r in rs) / n if n else None,
        }

    # Retrospective diagnostic criterion: at least two nontrivial relation classes
    # and an error-rate spread >= 0.20 among classes with n>=3.
    eligible_rates = [v["p_any_error"] for v in relation_summary.values() if v["count"] >= 3]
    spread = max(eligible_rates) - min(eligible_rates) if len(eligible_rates) >= 2 else 0.0
    state = "TYPED_COMPARISON_MORE_INFORMATIVE_WITH_BOUNDS" if len(eligible_rates) >= 2 and spread >= 0.20 else "RAW_AGREEMENT_TAXONOMY_NOT_IMPROVED"

    results = {
        "scientific_state": state,
        "classification": "post_reveal_retrospective_diagnostic",
        "production_authorization": False,
        "base_evidence_commit": BASE_EVIDENCE,
        "preregistration_commit": PREREGISTRATION,
        "taxonomy_version": TAXONOMY_VERSION,
        "case_count": len(cases),
        "pair_comparison_count": len(rows),
        "raw_agreement_pool": pooled(raw_agreement),
        "raw_disagreement_pool": pooled(raw_disagreement),
        "relation_error_rate_spread_n_ge_3": spread,
        "relation_summary": relation_summary,
        "weighting_authorized": False,
        "winner_selection_authorized": False,
        "prospective_generalization": False,
    }

    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    (outdir / "PAIR_ROWS.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    (outdir / "READER_USE_CASE_PROFILES.json").write_text(json.dumps(reader_profiles(cases, receipts_by_case), indent=2, sort_keys=True) + "\n")

    report = [
        "# Semantic Measurement Comparison Calibration RC1 — RC7D-D Retrospective\n",
        f"Scientific state: **`{state}`**\n",
        "This is retrospective diagnostic evidence only. It does not establish prospective calibration or production weights.\n",
        f"Pair comparisons: {len(rows)}\n",
        f"Typed relation error-rate spread (classes n>=3): {spread:.3f}\n",
        "## Relation classes\n",
    ]
    for relation, summary in sorted(relation_summary.items()):
        report.append(
            f"- `{relation}`: n={summary['count']}, any-error={summary['p_any_error']:.3f}, "
            f"shared-error={summary['p_shared_error']:.3f}, exactly-one-correct={summary['p_exactly_one_correct']:.3f}, "
            f"both-correct={summary['p_both_correct']:.3f}\n"
        )
    report.extend([
        "\n## Interpretation boundary\n",
        "The taxonomy describes measurement relationships. It never selects a winner and never grants semantic authority. "
        "Any future numeric weighting requires a separate calibration cohort and held-out validation, preferably per instrument pair, semantic use case, and measurement principle.\n",
    ])
    (outdir / "REPORT.md").write_text("".join(report))
    print(json.dumps(results, sort_keys=True))
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    evaluate(Path(args.output_dir))


if __name__ == "__main__":
    main()
