"""Benchmark comparison: CAL v0.4.0 (shipped `cal-rules-v1.13.0`) vs. CAL v2.

Evaluates across the canonical gold benchmark corpora:

1. Construction Gold v1.13.0 (33 cases)
2. Fresh Blind Constructed (30 cases)
3. X5 Adversarial Twins (56 cases)
4. PILOT-001 Real-World Human Gold (98 claims)

## Two things will otherwise make this report lie to you

**Read both before quoting any number this script prints.**

### 1. The two sides are not given the same inputs

The v0.4.0 verdict is *read from a sealed trace*. The v2 verdict is *recomputed
live*, and it is handed inputs the v1 run never had:

===========================================  ===================================
input                                        where it comes from
===========================================  ===================================
``declared_mode``                            ``case["relation"]``
``source_boundary``                          ``case["source_boundary"]``
``claimed_material_is_a_named_gap``          ``case["claimed_material_is_a_named_gap"]``
``claim_scope`` / ``passage_scope``          parsed from claim and passage text
``passage_texts``                            ``case["passages"]``
===========================================  ===================================

The first three are corpus construction parameters, and on a constructed corpus a
construction parameter is close to the label. ``relation="absent_from"`` maps to
``mode="coverage"``, and a coverage claim over a source declared ``exhaustive``
resolves to *supported* by rule R2 without reading a passage at all.
``claimed_material_is_a_named_gap`` is read by R1 and returns *contradicted* on
its own — the rule's own docstring says "the flag is the whole discriminator".

So a v2 win on those subsets is partly the corpus telling v2 the answer. Every
printed block carries a DECLARED-INPUT DISCLOSURE naming how many cases in that
corpus received each. A corpus where those counts are zero is a like-for-like
comparison; a corpus where they are high is not.

### 2. v2 gained a degree, and naive scoring reads that as a regression

v2 now emits ``unsupported`` where it previously emitted ``not_checkable`` with
the null reason ``no_signal``. The scoring buckets treat ``unsupported`` as
adverse, so **with byte-identical behaviour** the relabelling alone moves cases:

===================  ==========================  ========================
gold                 v2 said ``not_checkable``   v2 says ``unsupported``
===================  ==========================  ========================
supported            miss                        **false adverse**
partially_supported  miss                        **false adverse**
not_checkable        **agree**                   **false adverse**
unsupported          agree                       agree
===================  ==========================  ========================

A gold ``not_checkable`` case loses an agreement *and* gains a false adverse
without anything about the decision changing. On a corpus where most claims come
back ``not_checkable`` — DEV-004 records 56 of 98 for PILOT-001 — that is enough
to invert the headline.

So every corpus is scored **twice**:

- **raw** — v2's four degrees against gold's five, the number that describes what
  v2 now actually emits.
- **vocabulary-neutral** — v2's ``unsupported`` folded back to ``not_checkable``,
  which is exactly what the previous revision would have emitted for the same
  decision. This is the number to compare against a previous run.

Raw vs vocabulary-neutral isolates the relabelling. Vocabulary-neutral against a
prior run isolates the behaviour change. Neither alone tells you anything.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from claim_audit_lab.v1.features import scope_anchors
from claim_audit_lab.v1.impl.pipeline_rules import Mode, TrustPolicy, run_v2

# `outputs/` is a sibling of the repository root, not a directory inside it: the
# research outputs are sealed with SHA256SUMS manifests and never version
# controlled. `parents[1]` is the repo root, so the workbench holding both is
# `parents[2]`.
WORKBENCH_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUTS = WORKBENCH_ROOT / "outputs"

#: Verdict families, named once so both engines are scored by identical code.
_ADVERSE = ("contradicted", "unsupported")
_SUPPORTIVE = ("supported", "partially_supported")
_REACHABLE = ("supported", "contradicted", "not_checkable", "unsupported")
_DEGREES = ("supported", "partially_supported", "unsupported", "contradicted", "not_checkable")


def _mode_from_relation(relation: str | None) -> Mode | None:
    if relation == "absent_from":
        return "coverage"
    if relation in ("supported_by", "contradicted_by", "uncheckable", "restates"):
        return "ordinary"
    return None


class Tally:
    """One engine's scores under one scoring convention."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.agree = 0
        self.reachable_agree = 0
        self.false_adverse = 0
        self.false_support = 0
        self.miss = 0

    def record(self, verdict: str | None, gold: str | None, *, reachable: bool) -> None:
        if verdict == gold or (gold == "unsupported" and verdict == "not_checkable"):
            self.agree += 1
            if reachable:
                self.reachable_agree += 1
        elif verdict in _ADVERSE and gold not in _ADVERSE:
            self.false_adverse += 1
        elif verdict in _SUPPORTIVE and gold not in _SUPPORTIVE:
            self.false_support += 1
        else:
            self.miss += 1


def _fold_vocabulary(degree: str) -> str:
    """Map v2's degrees back to the three the previous revision could emit.

    `unsupported` was `not_checkable` carrying the null reason `no_signal`. This
    is the only difference, so folding it makes a run directly comparable to one
    taken before the degree existed.
    """
    return "not_checkable" if degree == "unsupported" else degree


def _pct(n: int, d: int) -> str:
    return f"{n}/{d} ({n / d * 100:.1f}%)" if d else f"{n}/0 (n/a)"


def run_comparison_corpus(
    name: str,
    corpus_root: Path,
    traces_rel: str,
    gold_path: Path,
    corpus_path: Path | None = None,
    is_yaml_gold: bool = False,
    trust_policy: TrustPolicy = "optional",
) -> dict[str, Any]:
    print("\n" + "=" * 80)
    print(f" EVALUATING CORPUS: {name}")
    print("=" * 80)

    if is_yaml_gold:
        raw_gold = yaml.safe_load(gold_path.read_text(encoding="utf-8"))
        gold_map = {
            item["claim_id"]: item.get("gold_verdict") or item.get("expected_verdict")
            for item in raw_gold.get("claims", [])
        }
    else:
        raw_gold = json.loads(gold_path.read_text(encoding="utf-8"))
        gold_map = {
            c["claim_id"]: c.get("gold_verdict") or c.get("expected_verdict")
            for c in raw_gold.get("claims", [])
        }
    rel_map: dict[str, str | None] = {}
    boundary_map: dict[str, str | None] = {}
    gap_map: dict[str, bool] = {}

    cases_map: dict[str, Any] = {}
    if corpus_path and corpus_path.exists():
        raw_corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        cases_map = {c["claim_id"]: c for c in raw_corpus.get("cases", [])}
        for cid, c in cases_map.items():
            rel_map[cid] = c.get("relation")
            boundary_map[cid] = c.get("source_boundary")
            gap_map[cid] = bool(c.get("claimed_material_is_a_named_gap", False))

    trace_files = sorted((corpus_root / traces_rel).glob("*.json"))

    v040 = Tally("v0.4.0")
    v2_raw = Tally("v2 raw")
    v2_folded = Tally("v2 vocabulary-neutral")

    deltas: list[dict[str, Any]] = []
    total = 0
    reachable_total = 0

    gold_dist: Counter[str] = Counter()
    v040_dist: Counter[str] = Counter()
    v2_dist: Counter[str] = Counter()
    movement: Counter[tuple[str, str]] = Counter()

    n_declared_mode = n_declared_boundary = n_declared_gap = n_passage_texts = 0
    n_mode_guessed = n_boundary_undeclared = 0
    blind_predicates: Counter[str] = Counter()
    blind_total = 0

    for tf in trace_files:
        trace = json.loads(tf.read_text(encoding="utf-8"))
        cid = trace.get("claim_id") or tf.stem
        if cid not in gold_map:
            continue

        gold_v = gold_map[cid]
        v040_v = trace.get("verdict", {}).get("support_verdict") or trace.get("support_verdict")

        case = cases_map.get(cid, {})
        texts: dict[str, str] = {}
        if case and "passages" in case:
            texts = {p["passage_id"]: p["text"] for p in case["passages"]}

        c_scope = scope_anchors(trace["claim_text"])
        p_scope = {pid: scope_anchors(txt) for pid, txt in texts.items()} if texts else None

        declared_mode = _mode_from_relation(rel_map.get(cid, trace.get("relation")))
        declared_boundary = boundary_map.get(cid, trace.get("source_boundary"))
        declared_gap = gap_map.get(cid, bool(trace.get("claimed_material_is_a_named_gap", False)))

        n_declared_mode += declared_mode is not None
        n_declared_boundary += declared_boundary is not None
        n_declared_gap += bool(declared_gap)
        n_passage_texts += bool(texts)

        v2_res = run_v2(
            claim_text=trace["claim_text"],
            features=trace.get("features", {}),
            retrieval=trace.get("retrieval", []),
            entailment=trace.get("entailment", []),
            source_boundary=declared_boundary,  # type: ignore[arg-type]
            claimed_material_is_a_named_gap=declared_gap,
            declared_mode=declared_mode,
            claim_scope=c_scope,
            passage_scope=p_scope,
            passage_texts=texts if texts else None,
            trust_levels=trace.get("trust_levels"),
            trust_policy=trust_policy,
        )
        v2_v = v2_res.degree
        v2_v_folded = _fold_vocabulary(v2_v)

        if v2_res.checks is not None:
            n_mode_guessed += not v2_res.checks.mode_declared
            n_boundary_undeclared += not v2_res.checks.boundary_declared
            for predicate in v2_res.checks.predicates_not_evaluated:
                blind_predicates[predicate] += 1
            blind_total += len(v2_res.checks.predicates_not_evaluated)

        total += 1
        reachable = gold_v in _REACHABLE
        reachable_total += reachable

        gold_dist[str(gold_v)] += 1
        v040_dist[str(v040_v)] += 1
        v2_dist[v2_v] += 1
        movement[(str(v040_v), v2_v)] += 1

        v040.record(v040_v, gold_v, reachable=reachable)
        v2_raw.record(v2_v, gold_v, reachable=reachable)
        v2_folded.record(v2_v_folded, gold_v, reachable=reachable)

        if v040_v != v2_v:
            deltas.append(
                {
                    "claim_id": cid,
                    "gold": gold_v,
                    "v0.4.0": v040_v,
                    "v2": v2_v,
                    "v2_reason": v2_res.notes[0] if v2_res.notes else v2_res.null_reason,
                }
            )

    print(f"Total Cases in Corpus  : {total}")
    if total == 0:
        print("\n  No trace matched a gold claim_id. Nothing was measured for this corpus.")
        return {"name": name, "total": 0, "deltas": []}

    print("\n[Agreement — scored two ways]")
    for tally in (v040, v2_raw, v2_folded):
        line = f"  {tally.label:<22} agree {_pct(tally.agree, total):<18}"
        if reachable_total and reachable_total < total:
            line += f" | reachable {_pct(tally.reachable_agree, reachable_total)}"
        print(line)
    print(
        "\n  Compare `v2 vocabulary-neutral` against a PREVIOUS run to see the behaviour\n"
        "  change. Compare `v2 raw` against it to see what the new `unsupported` degree\n"
        "  did to the score. They answer different questions."
    )

    print("\n[Safety]")
    print(f"  {'engine':<22} {'false adverse':>14} {'false support':>15}")
    for tally in (v040, v2_raw, v2_folded):
        print(f"  {tally.label:<22} {tally.false_adverse:>14} {tally.false_support:>15}")

    print("\n[Degree distribution]")
    print(f"  {'degree':<22} {'gold':>7} {'v0.4.0':>8} {'v2':>7}")
    for degree in _DEGREES:
        if gold_dist[degree] or v040_dist[degree] or v2_dist[degree]:
            print(
                f"  {degree:<22} {gold_dist[degree]:>7} {v040_dist[degree]:>8} {v2_dist[degree]:>7}"
            )

    print("\n[Movement: v0.4.0 -> v2]")
    for (was, now), count in sorted(movement.items(), key=lambda kv: -kv[1]):
        marker = "" if was == now else "   <-- changed"
        print(f"  {was:<22} -> {now:<22} {count:>4}{marker}")

    print("\n[DECLARED-INPUT DISCLOSURE — v2 only; v0.4.0 is read from a sealed trace]")
    n = total
    print(f"  • declared_mode from case['relation']  : {n_declared_mode}/{n} cases")
    print(f"  • source_boundary declared             : {n_declared_boundary}/{n} cases")
    print(f"  • claimed_material_is_a_named_gap set  : {n_declared_gap}/{n} cases")
    print(f"  • passage_texts supplied               : {n_passage_texts}/{n} cases")
    if n_declared_mode or n_declared_gap:
        print(
            "    ^ These are corpus construction parameters, not inference outputs. On the\n"
            "      cases that carry them the two engines were not asked the same question."
        )

    print(f"\n[APPARATUS COMPLETENESS — how much of v2 ran; trust_policy={trust_policy}]")
    print(f"  • mode guessed by the lexicon          : {n_mode_guessed}/{n} cases")
    print(f"  • source boundary undeclared           : {n_boundary_undeclared}/{n} cases")
    print(f"  • blind stage-2 predicate evaluations  : {blind_total}")
    for predicate, count in sorted(blind_predicates.items(), key=lambda kv: -kv[1]):
        print(f"      {predicate:<32} {count:>4} cases")
    print(
        "    ^ Not a confidence. These are counts of checks that could not run for want\n"
        "      of an input, which is the ceiling on what any decision layer can do here."
    )

    if deltas:
        print(f"\n[Movements in detail ({len(deltas)})]")
        for d in deltas[:12]:
            print(
                f"  • [{d['claim_id']}] gold={d['gold']} | v0.4.0={d['v0.4.0']} -> v2={d['v2']}\n"
                f"      {d['v2_reason']}"
            )
        if len(deltas) > 12:
            print(f"    ... and {len(deltas) - 12} more.")

    return {
        "name": name,
        "total": total,
        "v040_agree": v040.agree,
        "v2_agree_raw": v2_raw.agree,
        "v2_agree_folded": v2_folded.agree,
        "v040_false_adverse": v040.false_adverse,
        "v2_false_adverse_raw": v2_raw.false_adverse,
        "v2_false_adverse_folded": v2_folded.false_adverse,
        "deltas": deltas,
    }


def _corpora(outputs: Path) -> list[dict[str, Any]]:
    pilot = outputs / "pilot-001-dev-calibration"
    return [
        {
            "key": "construction-gold",
            "name": "Construction Gold Benchmark (33 Cases)",
            "corpus_root": outputs / "2026-08-20-construction-gold-v1.13.0",
            "traces_rel": "traces",
            "gold_path": outputs / "2026-08-20-construction-gold-v1.13.0" / "gold.json",
            "corpus_path": outputs / "2026-08-20-construction-gold-v1.13.0" / "corpus.json",
        },
        {
            "key": "fresh-blind",
            "name": "Fresh Blind Constructed (30 Cases)",
            "corpus_root": outputs / "2026-08-20-fresh-blind-constructed",
            "traces_rel": "traces",
            "gold_path": outputs / "2026-08-20-fresh-blind-constructed" / "gold.json",
            "corpus_path": outputs / "2026-08-20-fresh-blind-constructed" / "corpus.json",
        },
        {
            "key": "x5-twins",
            "name": "X5 Adversarial Twins (56 Invariance Cases)",
            "corpus_root": outputs / "2026-08-21-x5-adversarial-twins",
            "traces_rel": "results/traces",
            "gold_path": outputs / "2026-08-21-x5-adversarial-twins" / "gold.json",
            "corpus_path": outputs / "2026-08-21-x5-adversarial-twins" / "corpus.json",
        },
        {
            "key": "pilot-001",
            "name": "PILOT-001 Real-World Human Gold (98 Claims)",
            "corpus_root": pilot / "run-12-d14fix-end-to-end-2026-08-20",
            "traces_rel": "traces",
            "gold_path": pilot / "run-06-a1-landing-2026-07-16" / "gold.dev.yaml",
            "corpus_path": None,
            "is_yaml_gold": True,
        },
    ]


def _selftest() -> int:
    """Run the whole path over a synthetic corpus written to a temp directory.

    Exists because this script cannot be exercised without sealed research
    outputs, and a benchmark harness nobody can test is how a scoring bug reaches
    a published figure.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "corpus"
        (root / "traces").mkdir(parents=True)

        cases = [
            ("c1", "supported", "entail", 0.95, "supported"),
            ("c2", "contradicted", "contradict", 0.95, "contradicted"),
            ("c3", "unsupported", "neutral", 0.60, "not_checkable"),
            ("c4", "not_checkable", "neutral", 0.55, "not_checkable"),
        ]
        gold, corpus = [], []
        for cid, gold_v, label, score, v040_v in cases:
            (root / "traces" / f"{cid}.json").write_text(
                json.dumps(
                    {
                        "claim_id": cid,
                        "claim_text": "Retention samples are held for six months.",
                        "features": {
                            "has_explicit_negation": False,
                            "claim_token_count": 7,
                            "sentence_type": "declarative",
                        },
                        "retrieval": [{"passage_id": "p1", "score": 0.9}],
                        "entailment": [{"passage_id": "p1", "label": label, "score": score}],
                        "verdict": {"support_verdict": v040_v},
                    }
                ),
                encoding="utf-8",
            )
            gold.append({"claim_id": cid, "gold_verdict": gold_v})
            corpus.append(
                {
                    "claim_id": cid,
                    "relation": "supported_by",
                    "passages": [{"passage_id": "p1", "text": "Retains are kept six months."}],
                }
            )
        (root / "gold.json").write_text(json.dumps({"claims": gold}), encoding="utf-8")
        (root / "corpus.json").write_text(json.dumps({"cases": corpus}), encoding="utf-8")

        result = run_comparison_corpus(
            name="SELFTEST (synthetic)",
            corpus_root=root,
            traces_rel="traces",
            gold_path=root / "gold.json",
            corpus_path=root / "corpus.json",
        )

    print("\n" + "=" * 80)
    if result["total"] != len(cases):
        print(f" SELFTEST FAILED: scored {result['total']} of {len(cases)} cases")
        return 1
    # c3 and c4 both resolve `unsupported` under v2. Folded, both read
    # `not_checkable`: c4 then agrees with gold and c3 agrees by the charity rule.
    if result["v2_agree_folded"] <= result["v2_agree_raw"]:
        print(" SELFTEST FAILED: folding did not change the score, so the two")
        print(" scoring conventions are not actually distinct.")
        return 1
    print(
        f" SELFTEST PASSED: {result['total']} cases scored, "
        f"raw agree={result['v2_agree_raw']}, folded agree={result['v2_agree_folded']}"
    )
    print("=" * 80)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--outputs-root",
        type=Path,
        default=DEFAULT_OUTPUTS,
        help=f"directory holding the sealed corpora (default: {DEFAULT_OUTPUTS})",
    )
    parser.add_argument(
        "--trust-policy",
        choices=("optional", "required"),
        default="optional",
        help=(
            "what an absent per-passage trust level means. Replay corpora whose traces "
            "carry no `trust_levels` need `required` for provenance gating to run at all; "
            "corpora that build passages directly need `optional`."
        ),
    )
    parser.add_argument("--only", help="run a single corpus by key")
    parser.add_argument("--selftest", action="store_true", help="run on synthetic data and exit")
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()

    ran, missing = 0, []
    for spec in _corpora(args.outputs_root):
        if args.only and spec["key"] != args.only:
            continue
        root, gold = spec["corpus_root"], spec["gold_path"]
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
            trust_policy=args.trust_policy,
        )
        ran += 1

    if missing:
        print(f"\n[Corpora not found: {len(missing)}]", file=sys.stderr)
        for entry in missing:
            print(f"  - {entry}", file=sys.stderr)

    if ran == 0:
        print(
            f"\nNo corpus was evaluated. Nothing was measured.\n"
            f"Sealed research outputs are expected under {args.outputs_root}.\n"
            f"Point --outputs-root at them, or run --selftest to check this harness.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
