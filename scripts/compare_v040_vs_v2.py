"""Comprehensive Benchmark Comparison: CAL v0.4.0 (Shipped v1.13.0) vs. CAL v2 (Epistemic Pipeline).

Evaluates across all canonical gold benchmark corpora:
1. Construction Gold v1.13.0 (33 cases)
2. Fresh Blind Constructed (30 cases)
3. X5 Adversarial Twins (56 cases)
4. PILOT-001 Real-World Human Gold (98 claims)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from claim_audit_lab.v1.features import scope_anchors
from claim_audit_lab.v1.impl.pipeline_rules import Mode, run_v2

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"


def _mode_from_relation(relation: str | None) -> Mode | None:
    if relation == "absent_from":
        return "coverage"
    if relation in ("supported_by", "contradicted_by", "uncheckable", "restates"):
        return "ordinary"
    return None


def run_comparison_corpus(
    name: str,
    corpus_root: Path,
    traces_rel: str,
    gold_path: Path,
    corpus_path: Path | None = None,
    is_yaml_gold: bool = False,
) -> dict[str, Any]:
    print(f"\n================================================================================")
    print(f" EVALUATING CORPUS: {name}")
    print(f"================================================================================")

    # Load Gold
    if is_yaml_gold:
        raw_gold = yaml.safe_load(gold_path.read_text(encoding="utf-8"))
        gold_map = {
            item["claim_id"]: item.get("gold_verdict") or item.get("expected_verdict")
            for item in raw_gold.get("claims", [])
        }
        rel_map: dict[str, str | None] = {}
        boundary_map: dict[str, str | None] = {}
        gap_map: dict[str, bool] = {}
    else:
        raw_gold = json.loads(gold_path.read_text(encoding="utf-8"))
        gold_map = {
            c["claim_id"]: c.get("gold_verdict") or c.get("expected_verdict")
            for c in raw_gold.get("claims", [])
        }
        rel_map = {}
        boundary_map = {}
        gap_map = {}

    cases_map: dict[str, Any] = {}
    if corpus_path and corpus_path.exists():
        raw_corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        cases_map = {c["claim_id"]: c for c in raw_corpus.get("cases", [])}
        for cid, c in cases_map.items():
            rel_map[cid] = c.get("relation")
            boundary_map[cid] = c.get("source_boundary")
            gap_map[cid] = bool(c.get("claimed_material_is_a_named_gap", False))

    traces_dir = corpus_root / traces_rel
    trace_files = sorted(traces_dir.glob("*.json"))

    v040_agree = 0
    v040_false_adverse = 0
    v040_false_support = 0

    v2_agree = 0
    v2_false_adverse = 0
    v2_false_support = 0

    deltas: list[dict[str, Any]] = []
    total_evaluated = 0
    reachable_evaluated = 0
    v040_reachable_agree = 0
    v2_reachable_agree = 0

    for tf in trace_files:
        trace = json.loads(tf.read_text(encoding="utf-8"))
        cid = trace.get("claim_id") or tf.stem
        if cid not in gold_map:
            continue

        gold_v = gold_map[cid]
        v040_v = trace.get("verdict", {}).get("support_verdict")
        if not v040_v:
            v040_v = trace.get("support_verdict")

        # Prepare v2 inputs
        case = cases_map.get(cid, {})
        texts: dict[str, str] = {}
        if case and "passages" in case:
            texts = {p["passage_id"]: p["text"] for p in case["passages"]}

        c_scope = scope_anchors(trace["claim_text"])
        p_scope = {pid: scope_anchors(txt) for pid, txt in texts.items()} if texts else None

        v2_res = run_v2(
            claim_text=trace["claim_text"],
            features=trace.get("features", {}),
            retrieval=trace.get("retrieval", []),
            entailment=trace.get("entailment", []),
            source_boundary=boundary_map.get(cid, trace.get("source_boundary")),
            claimed_material_is_a_named_gap=gap_map.get(
                cid, bool(trace.get("claimed_material_is_a_named_gap", False))
            ),
            declared_mode=_mode_from_relation(rel_map.get(cid, trace.get("relation"))),
            claim_scope=c_scope,
            passage_scope=p_scope,
            passage_texts=texts if texts else None,
            trust_levels=trace.get("trust_levels"),
        )
        v2_v = v2_res.degree

        total_evaluated += 1
        is_reachable = gold_v in ("supported", "contradicted", "not_checkable", "unsupported")
        if is_reachable:
            reachable_evaluated += 1

        # Check v0.4.0 metrics
        if v040_v == gold_v or (gold_v == "unsupported" and v040_v == "not_checkable"):
            v040_agree += 1
            if is_reachable:
                v040_reachable_agree += 1
        elif v040_v in ("contradicted", "unsupported") and gold_v not in ("contradicted", "unsupported"):
            v040_false_adverse += 1
        elif v040_v in ("supported", "partially_supported") and gold_v not in (
            "supported",
            "partially_supported",
        ):
            v040_false_support += 1

        # Check v2 metrics
        if v2_v == gold_v or (gold_v == "unsupported" and v2_v == "not_checkable"):
            v2_agree += 1
            if is_reachable:
                v2_reachable_agree += 1
        elif v2_v in ("contradicted", "unsupported") and gold_v not in ("contradicted", "unsupported"):
            v2_false_adverse += 1
        elif v2_v == "supported" and gold_v not in ("supported", "partially_supported"):
            v2_false_support += 1

        # Track movements / deltas
        if v040_v != v2_v:
            deltas.append(
                {
                    "claim_id": cid,
                    "claim_snippet": trace["claim_text"][:65],
                    "gold": gold_v,
                    "v0.4.0": v040_v,
                    "v2": v2_v,
                    "v2_reason": v2_res.notes[0] if v2_res.notes else v2_res.null_reason,
                }
            )

    print(f"Total Cases in Corpus  : {total_evaluated}")
    print(f"\n[Accuracy & Agreement]")
    print(
        f"  • Raw Agreement      : v0.4.0 = {v040_agree}/{total_evaluated} ({v040_agree/total_evaluated*100:.1f}%) "
        f"| v2 = {v2_agree}/{total_evaluated} ({v2_agree/total_evaluated*100:.1f}%)"
    )
    if reachable_evaluated < total_evaluated:
        print(
            f"  • Reachable 3-Degree : v0.4.0 = {v040_reachable_agree}/{reachable_evaluated} ({v040_reachable_agree/reachable_evaluated*100:.1f}%) "
            f"| v2 = {v2_reachable_agree}/{reachable_evaluated} ({v2_reachable_agree/reachable_evaluated*100:.1f}%)"
        )
    print(f"\n[Safety & Error Profiles]")
    print(f"  • False Adverse (Refuting true/neutral facts) : v0.4.0 = {v040_false_adverse} | v2 = {v2_false_adverse}")
    print(f"  • False Support (Hallucinated substantiation) : v0.4.0 = {v040_false_support} | v2 = {v2_false_support}")

    if deltas:
        print(f"\n[Movements: v0.4.0 vs v2 ({len(deltas)} deltas)]")
        for d in deltas[:10]:
            print(
                f"  • [{d['claim_id']}] Gold: {d['gold']} | v0.4.0: {d['v0.4.0']} -> v2: {d['v2']} "
                f"({d['v2_reason']})"
            )
        if len(deltas) > 10:
            print(f"    ... and {len(deltas) - 10} more movements.")

    return {
        "name": name,
        "total": total_evaluated,
        "v040_agree": v040_agree,
        "v2_agree": v2_agree,
        "v040_false_adverse": v040_false_adverse,
        "v2_false_adverse": v2_false_adverse,
        "v040_false_support": v040_false_support,
        "v2_false_support": v2_false_support,
        "deltas": deltas,
    }


def main() -> None:
    # 1. Construction Gold v1.13.0
    cg_dir = OUTPUTS / "2026-08-20-construction-gold-v1.13.0"
    if cg_dir.exists():
        run_comparison_corpus(
            name="Construction Gold Benchmark (33 Cases)",
            corpus_root=cg_dir,
            traces_rel="traces",
            gold_path=cg_dir / "gold.json",
            corpus_path=cg_dir / "corpus.json",
        )

    # 2. Fresh Blind Constructed
    fb_dir = OUTPUTS / "2026-08-20-fresh-blind-constructed"
    if fb_dir.exists():
        run_comparison_corpus(
            name="Fresh Blind Constructed (30 Cases)",
            corpus_root=fb_dir,
            traces_rel="traces",
            gold_path=fb_dir / "gold.json",
            corpus_path=fb_dir / "corpus.json",
        )

    # 3. X5 Adversarial Twins
    twins_dir = OUTPUTS / "2026-08-21-x5-adversarial-twins"
    if twins_dir.exists():
        run_comparison_corpus(
            name="X5 Adversarial Twins (56 Invariance Cases)",
            corpus_root=twins_dir,
            traces_rel="results/traces",
            gold_path=twins_dir / "gold.json",
            corpus_path=twins_dir / "corpus.json",
        )

    # 4. PILOT-001 Realistic Human Gold
    pilot_dir = OUTPUTS / "pilot-001-dev-calibration" / "run-12-d14fix-end-to-end-2026-08-20"
    pilot_gold = (
        OUTPUTS / "pilot-001-dev-calibration" / "run-06-a1-landing-2026-07-16" / "gold.dev.yaml"
    )
    if pilot_dir.exists() and pilot_gold.exists():
        run_comparison_corpus(
            name="PILOT-001 Real-World Human Gold (98 Claims)",
            corpus_root=pilot_dir,
            traces_rel="traces",
            gold_path=pilot_gold,
            is_yaml_gold=True,
        )


if __name__ == "__main__":
    main()
