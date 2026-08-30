from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.population_semantics_contract_rc5.consumer import relation as consumer_relation
from research.population_semantics_contract_rc5.oracle import relation as oracle_relation

from .build_corpus import build, canonical_bytes

EXPECTED_COHORT_SHA256 = "92721e5144aa582ff00c10c4fc3666d43c05c5cd77e4a7669d10545c23395308"


def _semantic_projection(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "dimension": copy.deepcopy(case["dimension"]),
        "authority": copy.deepcopy(case["authority"]),
        "query": copy.deepcopy(case["query"]),
    }


def _remove_path_from_semantics(case: dict[str, Any], path: list[str]) -> dict[str, Any]:
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
    by_dimension: dict[str, Counter[str]] = defaultdict(Counter)
    relations_seen: set[str] = set()

    for case in corpus["cases"]:
        oracle = oracle_relation(case)
        consumer = consumer_relation(case)
        relations_seen.add(oracle)
        by_dimension[case["dimension"]][oracle] += 1
        row = {
            "case_id": case["case_id"],
            "dimension": case["dimension"],
            "oracle": oracle,
            "consumer": consumer,
        }
        rows.append(row)
        if oracle != consumer:
            disagreements.append({**row, "case": case})

    ablations: list[dict[str, Any]] = []
    for witness in corpus["ablation_witnesses"]:
        left = witness["left"]
        right = witness["right"]
        left_relation = oracle_relation(left)
        right_relation = oracle_relation(right)
        left_projection = _remove_path_from_semantics(left, witness["field_path"])
        right_projection = _remove_path_from_semantics(right, witness["field_path"])
        collision = _hash(left_projection) == _hash(right_projection)
        relation_differs = left_relation != right_relation
        ablations.append({
            "field": witness["field"],
            "field_path": witness["field_path"],
            "left_relation": left_relation,
            "right_relation": right_relation,
            "projected_collision": collision,
            "relation_differs": relation_differs,
            "witness_valid": collision and relation_differs,
        })

    case_map = {case["case_id"]: case for case in corpus["cases"]}
    metamorphic: list[dict[str, Any]] = []
    for pair in corpus["metamorphic_pairs"]:
        left = case_map[pair["left_case_id"]]
        right = case_map[pair["right_case_id"]]
        oracle_left = oracle_relation(left)
        oracle_right = oracle_relation(right)
        consumer_left = consumer_relation(left)
        consumer_right = consumer_relation(right)
        oracle_ok = (
            oracle_left == oracle_right
            if pair["relation"] == "same"
            else oracle_left != oracle_right
        )
        consumer_ok = (
            consumer_left == consumer_right
            if pair["relation"] == "same"
            else consumer_left != consumer_right
        )
        metamorphic.append({
            **pair,
            "oracle_left": oracle_left,
            "oracle_right": oracle_right,
            "oracle_ok": oracle_ok,
            "consumer_left": consumer_left,
            "consumer_right": consumer_right,
            "consumer_ok": consumer_ok,
        })

    all_ablations = all(item["witness_valid"] for item in ablations)
    all_metamorphic = all(item["oracle_ok"] and item["consumer_ok"] for item in metamorphic)
    three_way_only = relations_seen <= {"entailment", "neutral", "contradiction"}
    disposition = (
        "CONTRACT_SUFFICIENT"
        if not disagreements and all_ablations and all_metamorphic and three_way_only
        else "CONTRACT_INCOMPLETE"
    )
    return {
        "cohort_sha256": cohort_sha,
        "n_cases": len(corpus["cases"]),
        "oracle_consumer_disagreements": len(disagreements),
        "disagreements": disagreements,
        "n_ablation_witnesses": len(ablations),
        "valid_ablation_witnesses": sum(item["witness_valid"] for item in ablations),
        "ablation_witnesses": ablations,
        "n_metamorphic_pairs": len(metamorphic),
        "passing_metamorphic_pairs": sum(item["oracle_ok"] and item["consumer_ok"] for item in metamorphic),
        "metamorphic": metamorphic,
        "three_way_relations_seen": sorted(relations_seen),
        "three_way_sufficient_for_modeled_cases": three_way_only,
        "per_dimension_oracle_relation_counts": {key: dict(value) for key, value in sorted(by_dimension.items())},
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
    summary = {
        "cohort_sha256": result["cohort_sha256"],
        "n_cases": result["n_cases"],
        "oracle_consumer_disagreements": result["oracle_consumer_disagreements"],
        "valid_ablation_witnesses": result["valid_ablation_witnesses"],
        "n_ablation_witnesses": result["n_ablation_witnesses"],
        "passing_metamorphic_pairs": result["passing_metamorphic_pairs"],
        "n_metamorphic_pairs": result["n_metamorphic_pairs"],
        "three_way_sufficient_for_modeled_cases": result["three_way_sufficient_for_modeled_cases"],
        "disposition": result["disposition"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
