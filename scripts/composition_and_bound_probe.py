"""Why does CAL abstain on the construction corpus? Separate the mechanisms.

All eleven misses on construction gold v0.2 are **false abstentions** — ten
``supported`` and one ``contradicted`` returned as ``not_checkable``. Read off
the agreement number alone they look like one defect. They are not. This probe
sorts them by mechanism, using two read-only counterfactuals that the shipped
pipeline never forms.

**Counterfactual A — the concatenated premise.** v1 entails one passage at a
time and the aggregator takes a max over independent per-passage readings; no
operator anywhere composes two passages into one premise (``MaxEntailmentAggregator``
docstring: concatenated-premise and M×N aggregation are deferred to v2). Feeding
the support passages to the entailer as a single premise measures what that
design costs: a miss that the concatenation recovers is evidence the pipeline
never composed, not evidence the entailer cannot read.

**Counterfactual B — the split hop.** For a claim that needs a numeric bound
instantiated *and* a class-to-consequence chain, entail each hop separately, and
entail the bound hop twice — once with the threshold restated verbatim, once
with a satisfying value substituted. If the model entails the first and goes
neutral on the second, it is matching the sentence rather than comparing the
quantities.

NEITHER COUNTERFACTUAL IS A PROPOSED FIX. Both localize the loss. Concatenation
in particular buys recall by handing the entailer more text, which is the trade
the floor exists to refuse (Decision F4); adopting it is a v2 design question
with its own precision cost, not a conclusion of this probe.

Two confounds are detected and reported rather than left to the reader:

* A case carrying distractors is **confounded** under counterfactual A, because
  concatenating only the *support* passages silently removes the distractor that
  caused the abstention. The recovery is then an artefact of the test.
* An absence claim is **not safely recoverable** under counterfactual A. The
  entailer agreeing that a document does not say something is exactly the reading
  ``A6_absence_not_decidable`` exists to distrust.

Read-only. Runs the pinned models, writes a dated record, decides nothing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer
from claim_audit_lab.v1.impl.retriever import BiEncoderRetriever
from claim_audit_lab.v1.models import ModelRevision, Passage

GOLD = Path(__file__).resolve().parents[2] / "outputs" / "2026-08-19-construction-gold"
OUT = Path(__file__).resolve().parents[2] / "outputs" / "2026-08-19-composition-and-bound-probe"

# Counterfactual B is authored, so the hypotheses live here in the open rather
# than being derived from the claim by a rule nobody can inspect. Each entry is
# (label, premise_passage_id, hypothesis).
HOP_PROBES: list[tuple[str, str, str]] = [
    (
        "CG-05 hop 1, bound restated verbatim",
        "SRC-DEV#p3",
        "Cold-chain product held above 8 degrees Celsius for more than 6 hours "
        "is a critical deviation.",
    ),
    (
        "CG-05 hop 1, bound instantiated at 10 C / 7 h",
        "SRC-DEV#p3",
        "A cold-chain batch held at 10 degrees Celsius for 7 hours is a critical deviation.",
    ),
    (
        "CG-05 hop 1, bound instantiated at 9 C / 7 h",
        "SRC-DEV#p3",
        "A cold-chain batch held at 9 degrees Celsius for 7 hours is a critical deviation.",
    ),
    (
        "CG-05 hop 2, class to consequence",
        "SRC-DEV#p2",
        "A batch with a critical deviation must be placed on Quality Hold.",
    ),
    (
        "CG-15 hop 1, instance to class (no quantities)",
        "SRC-CC#p1",
        "Relocating manufacturing equipment between production suites is a major change.",
    ),
    (
        "CG-15 hop 2, class to consequence (no quantities)",
        "SRC-CC#p2",
        "A major change requires requalification of the affected equipment before "
        "production resumes.",
    ),
]


def _classify(row: dict[str, Any], case: dict[str, Any], recovered: bool) -> str:
    """Name the mechanism from the rule that fired, not from the verdict."""
    rules = set(row["rules"])
    if "A2_retrieval_empty" in rules:
        return "no_evidence_admitted"
    if "A6_absence_not_decidable" in rules:
        return "absence_gate_by_design"
    if "A5_conflicting_evidence" in rules:
        return "scope_conflict"
    if "A4_negation_consistency" in rules:
        return "probe_stood_down_contradiction"
    if recovered and case["n_support_passages"] > 1:
        return "composition_never_formed"
    if case.get("relation") == "instantiates_bound":
        return "bound_not_instantiated"
    return "unclassified"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT)
    args = parser.parse_args()

    corpus = json.loads((GOLD / "corpus.json").read_text(encoding="utf-8"))
    results = json.loads((GOLD / "audit_results.json").read_text(encoding="utf-8"))
    cases = {c["case_id"]: c for c in corpus["cases"]}
    misses = [r for r in results["rows"] if r["gold"] != r["cal"]]

    config = load_default_audit_config()
    entailer = DeBERTaEntailer(revision=ModelRevision(**config.entailer.model_dump()))
    retriever = BiEncoderRetriever(revision=ModelRevision(**config.retriever.model_dump()))
    floor, threshold = config.retrieval_floor, config.supported_threshold

    print(f"floor={floor}  supported_threshold={threshold}  top_k={config.top_k}")
    print(f"misses on construction gold v0.2: {len(misses)}/{results['n']}")
    print(f"all abstentions: {all(r['cal'] == 'not_checkable' for r in misses)}\n")

    rows: list[dict[str, Any]] = []
    header = (
        f"{'case':<8} {'relation':<20} {'supp':>4} {'adm':>4} "
        f"{'solo_pe':>8} {'concat_pe':>10}  {'mechanism':<32} confound"
    )
    print(header)
    print("-" * len(header))
    for row in misses:
        case = cases[row["case_id"]]
        passages = [Passage(passage_id=p["passage_id"], text=p["text"]) for p in case["passages"]]
        ranked = {
            r.passage_id: r.score
            for r in retriever.retrieve(case["claim_text"], passages, config.top_k)
        }
        supports = [p for p in case["passages"] if p["role"] == "support"]

        solo = {
            p["passage_id"]: entailer.entail(
                case["claim_text"], p["text"], p["passage_id"]
            ).p_entail
            or 0.0
            for p in case["passages"]
        }
        joined = entailer.entail(
            case["claim_text"], " ".join(p["text"] for p in supports), "concat"
        )
        concat_pe = joined.p_entail or 0.0
        recovered = concat_pe >= threshold and case["expected_verdict"] == "supported"

        confounds: list[str] = []
        if case["n_distractor_passages"]:
            confounds.append("concat_drops_distractor")
        if case["relation"] == "absent_from":
            confounds.append("absence_claim_not_safely_recoverable")

        mechanism = _classify(row, case, recovered)
        rows.append(
            {
                "case_id": row["case_id"],
                "relation": case["relation"],
                "gold": row["gold"],
                "cal": row["cal"],
                "rules_fired": row["rules"],
                "n_support_passages": case["n_support_passages"],
                "n_distractor_passages": case["n_distractor_passages"],
                "retrieval": {pid: round(s, 4) for pid, s in sorted(ranked.items())},
                "n_admitted": sum(1 for s in ranked.values() if s >= floor),
                "solo_p_entail": {pid: round(v, 4) for pid, v in sorted(solo.items())},
                "best_solo_p_entail": round(max(solo.values()), 4),
                "concat_label": joined.label,
                "concat_p_entail": round(concat_pe, 4),
                "concat_recovers": recovered,
                "confounds": confounds,
                "mechanism": mechanism,
            }
        )
        print(
            f"{row['case_id']:<8} {case['relation']:<20} {case['n_support_passages']:>4} "
            f"{sum(1 for s in ranked.values() if s >= floor):>4} "
            f"{max(solo.values()):>8.4f} {concat_pe:>10.4f}  {mechanism:<32} "
            f"{','.join(confounds) or '-'}"
        )

    clean = [r for r in rows if r["mechanism"] == "composition_never_formed" and not r["confounds"]]
    print(f"\nclean composition misses (recovered, unconfounded): {len(clean)}/{len(rows)}")
    print(f"  {', '.join(r['case_id'] for r in clean)}")
    for mech in sorted({r["mechanism"] for r in rows}):
        ids = [r["case_id"] for r in rows if r["mechanism"] == mech]
        print(f"  {mech:<34} {len(ids)}  {', '.join(ids)}")

    # --- counterfactual B: which hop fails --------------------------------
    texts = {p["passage_id"]: p["text"] for c in corpus["cases"] for p in c["passages"]}
    print("\ncounterfactual B — each hop entailed on its own:\n")
    print(f"{'probe':<48} {'label':<10} {'p_entail':>9}")
    print("-" * 69)
    hops: list[dict[str, Any]] = []
    for label, passage_id, hypothesis in HOP_PROBES:
        result = entailer.entail(hypothesis, texts[passage_id], passage_id)
        hops.append(
            {
                "probe": label,
                "premise_passage_id": passage_id,
                "hypothesis": hypothesis,
                "label": result.label,
                "p_entail": round(result.p_entail or 0.0, 4),
            }
        )
        print(f"{label:<48} {result.label:<10} {result.p_entail or 0.0:>9.4f}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "probe_id": "2026-08-19-composition-and-bound-probe",
        "source_corpus": corpus["corpus_id"],
        "audit_config_sha": config.rules_file_sha,
        "retrieval_floor": floor,
        "supported_threshold": threshold,
        "n_misses": len(rows),
        "clean_composition_misses": [r["case_id"] for r in clean],
        "mechanisms": {
            m: [r["case_id"] for r in rows if r["mechanism"] == m]
            for m in sorted({r["mechanism"] for r in rows})
        },
        "misses": rows,
        "hop_probes": hops,
    }
    target = args.out_dir / "results.json"
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nwrote {target}")


if __name__ == "__main__":
    main()
