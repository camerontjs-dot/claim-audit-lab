from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from research.population_semantics_contract_rc5.oracle import relation as oracle_relation
from research.population_semantics_contract_rc5a.build_corpus import build, canonical_bytes
from research.population_semantics_contract_rc5b.consumer import relation as consumer_relation

EXPECTED_COHORT_SHA256 = "92721e5144aa582ff00c10c4fc3666d43c05c5cd77e4a7669d10545c23395308"


def _semantic_projection(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "dimension": copy.deepcopy(case["dimension"]),
        "authority": copy.deepcopy(case["authority"]),
        "query": copy.deepcopy(case["query"]),
    }


def _remove_path(case: dict[str, Any], path: list[str]) -> dict[str, Any]:
    projected = _semantic_projection(case)
    cur: Any = projected
    for key in path[:-1]:
        cur = cur[key]
    cur.pop(path[-1], None)
    return projected


def _hash(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def evaluate() -> dict[str, Any]:
    corpus = build()
    cohort_sha = _hash(corpus)
    if cohort_sha != EXPECTED_COHORT_SHA256:
        raise RuntimeError(f"frozen RC5A corpus mismatch: {cohort_sha}")

    rows: list[dict[str, Any]] = []
    disagreements: list[dict[str, Any]] = []
    relations_seen: set[str] = set()
    per_dimension: dict[str, dict[str, int]] = {}

    for case in corpus["cases"]:
        oracle = oracle_relation(case)
        consumer = consumer_relation(case)
        relations_seen.add(oracle)
        counts = per_dimension.setdefault(case["dimension"], {"n": 0, "disagreements": 0})
        counts["n"] += 1
        row = {"case_id": case["case_id"], "dimension": case["dimension"], "oracle": oracle, "consumer": consumer}
        rows.append(row)
        if oracle != consumer:
            counts["disagreements"] += 1
            disagreements.append({**row, "case": case})

    ablations: list[dict[str, Any]] = []
    for witness in corpus["ablation_witnesses"]:
        left = witness["left"]
        right = witness["right"]
        left_relation = oracle_relation(left)
        right_relation = oracle_relation(right)
        collision = _hash(_remove_path(left, witness["field_path"])) == _hash(_remove_path(right, witness["field_path"]))
        differs = left_relation != right_relation
        ablations.append({
            "field": witness["field"],
            "left_relation": left_relation,
            "right_relation": right_relation,
            "projected_collision": collision,
            "relation_differs": differs,
            "witness_valid": collision and differs,
        })

    case_map = {case["case_id"]: case for case in corpus["cases"]}
    metamorphic: list[dict[str, Any]] = []
    for pair in corpus["metamorphic_pairs"]:
        left = case_map[pair["left_case_id"]]
        right = case_map[pair["right_case_id"]]
        ol, or_ = oracle_relation(left), oracle_relation(right)
        cl, cr = consumer_relation(left), consumer_relation(right)
        oracle_ok = ol == or_ if pair["relation"] == "same" else ol != or_
        consumer_ok = cl == cr if pair["relation"] == "same" else cl != cr
        metamorphic.append({**pair, "oracle_left": ol, "oracle_right": or_, "oracle_ok": oracle_ok,
                            "consumer_left": cl, "consumer_right": cr, "consumer_ok": consumer_ok})

    valid_ablations = sum(item["witness_valid"] for item in ablations)
    passing_meta = sum(item["oracle_ok"] and item["consumer_ok"] for item in metamorphic)
    three_way = relations_seen <= {"entailment", "neutral", "contradiction"}
    disposition = "CONTRACT_SUFFICIENT" if not disagreements and valid_ablations == 13 and passing_meta == 8 and three_way else "CONTRACT_INCOMPLETE"
    return {
        "cohort_sha256": cohort_sha,
        "n_cases": len(corpus["cases"]),
        "oracle_consumer_disagreements": len(disagreements),
        "disagreements": disagreements,
        "valid_ablation_witnesses": valid_ablations,
        "n_ablation_witnesses": len(ablations),
        "ablation_witnesses": ablations,
        "passing_metamorphic_pairs": passing_meta,
        "n_metamorphic_pairs": len(metamorphic),
        "metamorphic": metamorphic,
        "three_way_relations_seen": sorted(relations_seen),
        "three_way_sufficient_for_modeled_cases": three_way,
        "per_dimension": per_dimension,
        "rows": rows,
        "disposition": disposition,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = evaluate()
    (args.output_dir / "RESULTS.json").write_bytes(canonical_bytes(result))
    summary = {key: result[key] for key in (
        "cohort_sha256", "n_cases", "oracle_consumer_disagreements", "valid_ablation_witnesses",
        "n_ablation_witnesses", "passing_metamorphic_pairs", "n_metamorphic_pairs",
        "three_way_sufficient_for_modeled_cases", "disposition"
    )}
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
