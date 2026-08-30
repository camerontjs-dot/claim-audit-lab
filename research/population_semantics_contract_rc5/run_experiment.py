from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .build_corpus import build, canonical_bytes
from .consumer import relation as consumer_relation
from .oracle import relation as oracle_relation

EXPECTED_COHORT_SHA256 = "9b5ce098f92061b310e812e2681ff4a7b710f05c8f3d777395a75c87ef8fa92a"


def _remove_path(obj: dict[str, Any], path: list[str]) -> dict[str, Any]:
    clone = copy.deepcopy(obj)
    cur: Any = clone
    for key in path[:-1]: cur = cur[key]
    cur.pop(path[-1], None)
    return clone


def _hash(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def evaluate() -> dict[str, Any]:
    corpus = build()
    cohort_sha = _hash(corpus)
    if cohort_sha != EXPECTED_COHORT_SHA256:
        raise RuntimeError(f"frozen corpus mismatch: {cohort_sha}")

    rows: list[dict[str, Any]] = []
    disagreements: list[dict[str, Any]] = []
    by_dimension: dict[str, Counter[str]] = defaultdict(Counter)
    three_way_seen: set[str] = set()
    for c in corpus["cases"]:
        oracle = oracle_relation(c); consumer = consumer_relation(c)
        three_way_seen.add(oracle); by_dimension[c["dimension"]][oracle] += 1
        row = {"case_id": c["case_id"], "dimension": c["dimension"], "oracle": oracle, "consumer": consumer}
        rows.append(row)
        if oracle != consumer: disagreements.append({**row, "case": c})

    ablations: list[dict[str, Any]] = []
    for witness in corpus["ablation_witnesses"]:
        left, right = witness["left"], witness["right"]
        left_rel, right_rel = oracle_relation(left), oracle_relation(right)
        collision = _hash(_remove_path(left, witness["field_path"])) == _hash(_remove_path(right, witness["field_path"]))
        relation_differs = left_rel != right_rel
        ablations.append({"field": witness["field"], "field_path": witness["field_path"],
                          "left_relation": left_rel, "right_relation": right_rel,
                          "projected_collision": collision, "relation_differs": relation_differs,
                          "witness_valid": collision and relation_differs})

    case_map = {c["case_id"]: c for c in corpus["cases"]}
    metamorphic: list[dict[str, Any]] = []
    for pair in corpus["metamorphic_pairs"]:
        left, right = case_map[pair["left_case_id"]], case_map[pair["right_case_id"]]
        ol, or_ = oracle_relation(left), oracle_relation(right)
        cl, cr = consumer_relation(left), consumer_relation(right)
        ook = ol == or_ if pair["relation"] == "same" else ol != or_
        cok = cl == cr if pair["relation"] == "same" else cl != cr
        metamorphic.append({**pair, "oracle_left": ol, "oracle_right": or_, "oracle_ok": ook,
                            "consumer_left": cl, "consumer_right": cr, "consumer_ok": cok})

    all_ablations = all(x["witness_valid"] for x in ablations)
    all_meta = all(x["oracle_ok"] and x["consumer_ok"] for x in metamorphic)
    three_way_only = three_way_seen <= {"entailment", "neutral", "contradiction"}
    disposition = "CONTRACT_SUFFICIENT" if not disagreements and all_ablations and all_meta and three_way_only else "CONTRACT_INCOMPLETE"
    return {"cohort_sha256": cohort_sha, "n_cases": len(corpus["cases"]),
            "n_ablation_witnesses": len(ablations), "n_metamorphic_pairs": len(metamorphic),
            "oracle_consumer_disagreements": len(disagreements), "disagreements": disagreements,
            "ablation_witnesses": ablations, "metamorphic": metamorphic,
            "three_way_relations_seen": sorted(three_way_seen),
            "three_way_sufficient_for_modeled_cases": three_way_only,
            "per_dimension_oracle_relation_counts": {k: dict(v) for k, v in sorted(by_dimension.items())},
            "rows": rows, "disposition": disposition}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--output-dir", type=Path, required=True); args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = evaluate(); (args.output_dir / "RESULTS.json").write_bytes(canonical_bytes(result))
    summary = {"cohort_sha256": result["cohort_sha256"], "n_cases": result["n_cases"],
               "oracle_consumer_disagreements": result["oracle_consumer_disagreements"],
               "valid_ablation_witnesses": sum(x["witness_valid"] for x in result["ablation_witnesses"]),
               "n_ablation_witnesses": result["n_ablation_witnesses"],
               "passing_metamorphic_pairs": sum(x["oracle_ok"] and x["consumer_ok"] for x in result["metamorphic"]),
               "n_metamorphic_pairs": result["n_metamorphic_pairs"],
               "three_way_sufficient_for_modeled_cases": result["three_way_sufficient_for_modeled_cases"],
               "disposition": result["disposition"]}
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__": main()
