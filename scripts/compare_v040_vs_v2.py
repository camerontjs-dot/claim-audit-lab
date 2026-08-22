"""Benchmark comparison: CAL v0.4.0 (shipped `cal-rules-v1.13.0`) vs. CAL v2.

Evaluates across the canonical gold benchmark corpora:

1. Construction Gold v1.13.0 (33 cases)
2. Fresh Blind Constructed (30 cases)
3. X5 Adversarial Twins (56 cases)
4. PILOT-001 Real-World Human Gold (98 claims)

## The two sides are not given the same inputs

**Read this before quoting any number this script prints.**

The v0.4.0 verdict is *read from a sealed trace*. The v2 verdict is *recomputed
live*, and it is handed inputs the v1 run never had:

===========================================  ===================================
input                                        where it comes from
===========================================  ===================================
``declared_mode``                            ``case["relation"]``
``source_boundary``                          ``case["source_boundary"]``
``claimed_material_is_a_named_gap``           ``case["claimed_material_is_a_named_gap"]``
``claim_scope`` / ``passage_scope``          parsed from claim and passage text
``passage_texts``                            ``case["passages"]``
===========================================  ===================================

The first three are corpus construction parameters, and on a constructed corpus a
construction parameter is close to the label. ``relation="absent_from"`` maps to
``mode="coverage"``, and a coverage claim over a source declared ``exhaustive``
resolves to *supported* by rule R2 without reading a passage at all.
``claimed_material_is_a_named_gap`` is read by R1 and returns *contradicted* on
its own — the rule's own docstring says "the flag is the whole discriminator".

So a v2 win on those subsets is partly the corpus telling v2 the answer. That is
a legitimate thing to measure — it is the declared-mode design working, and the
module header is explicit that the caller declares claim type — but it is not the
same measurement as v1's, and reporting a single side-by-side percentage without
this qualification produces exactly the kind of unqualified figure the project's
README refuses to publish.

Every printed block therefore carries a DECLARED-INPUT DISCLOSURE naming how many
cases in that corpus received each oracle-adjacent input. A corpus where that
count is zero is a like-for-like comparison; a corpus where it is high is not.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from claim_audit_lab.v1.features import scope_anchors
from claim_audit_lab.v1.impl.pipeline_rules import Mode, run_v2

# `outputs/` is a sibling of the repository root, not a directory inside it: the
# research outputs are sealed with SHA256SUMS manifests and never version
# controlled. `parents[1]` is the repo root, so the workbench holding both is
# `parents[2]`.
WORKBENCH_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = WORKBENCH_ROOT / "outputs"

#: Verdict families, named once so both engines are scored by identical code.
_ADVERSE = ("contradicted", "unsupported")
_SUPPORTIVE = ("supported", "partially_supported")


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
    print("\n================================================================================")
    print(f" EVALUATING CORPUS: {name}")
    print("================================================================================")

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

    # How many cases handed v2 an input the sealed v0.4.0 run never had.
    n_declared_mode = 0
    n_declared_boundary = 0
    n_declared_gap = 0
    n_passage_texts = 0

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

        declared_mode = _mode_from_relation(rel_map.get(cid, trace.get("relation")))
        declared_boundary = boundary_map.get(cid, trace.get("source_boundary"))
        declared_gap = gap_map.get(cid, bool(trace.get("claimed_material_is_a_named_gap", False)))

        # Count the asymmetry rather than leaving it to the reader to infer.
        n_declared_mode += declared_mode is not None
        n_declared_boundary += declared_boundary is not None
        n_declared_gap += bool(declared_gap)
        n_passage_texts += bool(texts)

        v2_res = run_v2(
            claim_text=trace["claim_text"],
            features=trace.get("features", {}),
            retrieval=trace.get("retrieval", []),
            entailment=trace.get("entailment", []),
            source_boundary=declared_boundary,
            claimed_material_is_a_named_gap=declared_gap,
            declared_mode=declared_mode,
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
        elif v040_v in _ADVERSE and gold_v not in _ADVERSE:
            v040_false_adverse += 1
        elif v040_v in _SUPPORTIVE and gold_v not in _SUPPORTIVE:
            v040_false_support += 1

        # Check v2 metrics
        if v2_v == gold_v or (gold_v == "unsupported" and v2_v == "not_checkable"):
            v2_agree += 1
            if is_reachable:
                v2_reachable_agree += 1
        elif v2_v in _ADVERSE and gold_v not in _ADVERSE:
            v2_false_adverse += 1
        # Same predicate as the v0.4.0 branch above. v2's `Degree` has no
        # `partially_supported`, so including it changes no count — but the two
        # sides of a comparison must be scored by identical code, or the
        # comparison is measuring the scorer.
        elif v2_v in _SUPPORTIVE and gold_v not in _SUPPORTIVE:
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
    if total_evaluated == 0:
        print("\n  No trace matched a gold claim_id. Nothing was measured for this corpus.")
        return {
            "name": name,
            "total": 0,
            "v040_agree": 0,
            "v2_agree": 0,
            "v040_false_adverse": 0,
            "v2_false_adverse": 0,
            "v040_false_support": 0,
            "v2_false_support": 0,
            "deltas": [],
        }

    print("\n[Accuracy & Agreement]")
    print(
        f"  • Raw Agreement      : "
        f"v0.4.0 = {v040_agree}/{total_evaluated} ({v040_agree / total_evaluated * 100:.1f}%) "
        f"| v2 = {v2_agree}/{total_evaluated} ({v2_agree / total_evaluated * 100:.1f}%)"
    )
    if reachable_evaluated < total_evaluated and reachable_evaluated > 0:
        print(
            f"  • Reachable 3-Degree : "
            f"v0.4.0 = {v040_reachable_agree}/{reachable_evaluated} "
            f"({v040_reachable_agree / reachable_evaluated * 100:.1f}%) "
            f"| v2 = {v2_reachable_agree}/{reachable_evaluated} "
            f"({v2_reachable_agree / reachable_evaluated * 100:.1f}%)"
        )
    print("\n[Safety & Error Profiles]")
    print(
        f"  • False Adverse (Refuting true/neutral facts) : "
        f"v0.4.0 = {v040_false_adverse} | v2 = {v2_false_adverse}"
    )
    print(
        f"  • False Support (Hallucinated substantiation) : "
        f"v0.4.0 = {v040_false_support} | v2 = {v2_false_support}"
    )

    print("\n[DECLARED-INPUT DISCLOSURE — v2 only; v0.4.0 is read from a sealed trace]")
    n = total_evaluated
    print(f"  • declared_mode from case['relation']  : {n_declared_mode}/{n} cases")
    print(f"  • source_boundary declared             : {n_declared_boundary}/{n} cases")
    print(f"  • claimed_material_is_a_named_gap set  : {n_declared_gap}/{n} cases")
    print(f"  • passage_texts supplied               : {n_passage_texts}/{n} cases")
    if n_declared_mode or n_declared_gap:
        print(
            "    ^ These are corpus construction parameters, not inference outputs. On the\n"
            "      cases that carry them the two engines were not asked the same question,\n"
            "      and the agreement figures above are not like-for-like. See the module\n"
            "      docstring."
        )

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


def main() -> int:
    """Run every corpus present. Returns a process exit code.

    Each corpus is guarded on its directory existing, because the sealed research
    outputs are not version controlled and a given checkout may hold any subset.
    A run that finds *none* of them measured nothing, and says so on stderr with a
    non-zero exit rather than printing an empty report and succeeding.
    """
    pilot_root = OUTPUTS / "pilot-001-dev-calibration"
    corpora: list[dict[str, Any]] = [
        {
            "name": "Construction Gold Benchmark (33 Cases)",
            "corpus_root": OUTPUTS / "2026-08-20-construction-gold-v1.13.0",
            "traces_rel": "traces",
            "gold_path": OUTPUTS / "2026-08-20-construction-gold-v1.13.0" / "gold.json",
            "corpus_path": OUTPUTS / "2026-08-20-construction-gold-v1.13.0" / "corpus.json",
        },
        {
            "name": "Fresh Blind Constructed (30 Cases)",
            "corpus_root": OUTPUTS / "2026-08-20-fresh-blind-constructed",
            "traces_rel": "traces",
            "gold_path": OUTPUTS / "2026-08-20-fresh-blind-constructed" / "gold.json",
            "corpus_path": OUTPUTS / "2026-08-20-fresh-blind-constructed" / "corpus.json",
        },
        {
            "name": "X5 Adversarial Twins (56 Invariance Cases)",
            "corpus_root": OUTPUTS / "2026-08-21-x5-adversarial-twins",
            "traces_rel": "results/traces",
            "gold_path": OUTPUTS / "2026-08-21-x5-adversarial-twins" / "gold.json",
            "corpus_path": OUTPUTS / "2026-08-21-x5-adversarial-twins" / "corpus.json",
        },
        {
            "name": "PILOT-001 Real-World Human Gold (98 Claims)",
            "corpus_root": pilot_root / "run-12-d14fix-end-to-end-2026-08-20",
            "traces_rel": "traces",
            "gold_path": pilot_root / "run-06-a1-landing-2026-07-16" / "gold.dev.yaml",
            "corpus_path": None,
            "is_yaml_gold": True,
        },
    ]

    ran = 0
    missing: list[str] = []
    for spec in corpora:
        root = spec["corpus_root"]
        gold = spec["gold_path"]
        if not root.exists() or not gold.exists():
            missing.append(f"{spec['name']}  (expected {root})")
            continue
        run_comparison_corpus(
            name=spec["name"],
            corpus_root=root,
            traces_rel=spec["traces_rel"],
            gold_path=gold,
            corpus_path=spec.get("corpus_path"),
            is_yaml_gold=bool(spec.get("is_yaml_gold", False)),
        )
        ran += 1

    if missing:
        print(f"\n[Corpora not found: {len(missing)}]", file=sys.stderr)
        for entry in missing:
            print(f"  - {entry}", file=sys.stderr)

    if ran == 0:
        print(
            f"\nNo corpus was evaluated. Nothing was measured.\n"
            f"Sealed research outputs are expected under {OUTPUTS}, which is a sibling of\n"
            f"the repository root and is not version controlled.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
