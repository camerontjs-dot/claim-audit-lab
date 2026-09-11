#!/usr/bin/env python3
"""Adversarial evaluator for the independent EB V1 structural consumer."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from consumer import StructuralValidationError, reseal, validate_and_reconstruct


def expect_refused(name: str, mutated: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_and_reconstruct(reseal(mutated))
    except StructuralValidationError as exc:
        return {"name": name, "refused": True, "reason": str(exc)}
    return {"name": name, "refused": False, "reason": None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    package = json.loads(args.package.read_text(encoding="utf-8"))
    projection = validate_and_reconstruct(package)
    mutations: list[dict[str, Any]] = []

    changed = deepcopy(package)
    changed["contract_a"]["decomposition"]["children"][0]["text"] += " changed"
    mutations.append(expect_refused("proposition_text_substitution", changed))

    changed = deepcopy(package)
    changed["retrieval_plans"][0]["retrieval_lane"] = "root"
    mutations.append(expect_refused("normative_lane_substitution", changed))

    changed = deepcopy(package)
    changed["candidates"][0]["text"] += " changed"
    mutations.append(expect_refused("passage_bytes_substitution", changed))

    changed = deepcopy(package)
    changed["retrieval_plans"][0]["query_id"] = "query:" + "0" * 32
    mutations.append(expect_refused("query_identity_substitution", changed))

    changed = deepcopy(package)
    nonretained = next(
        (row for row in changed["candidates"] if row["selection_state"] == "not_retained"),
        None,
    )
    if nonretained is None:
        raise StructuralValidationError("fixture must include a non-retained mutation control")
    nonretained["admission_state"] = "accepted"
    mutations.append(expect_refused("nonretained_admission_laundering", changed))

    changed = deepcopy(package)
    execution = changed["retrieval_executions"][0]
    if execution["aperture_state"] == "bounded_at_limit":
        execution["aperture_state"] = "bounded_under_limit"
        execution["candidate_depth_hit"] = False
    else:
        execution["aperture_state"] = "bounded_at_limit"
        execution["candidate_depth_hit"] = True
    mutations.append(expect_refused("aperture_state_substitution", changed))

    changed = deepcopy(package)
    changed["verdict"] = "supported"
    mutations.append(expect_refused("semantic_authority_injection", changed))

    receipt = {
        "schema": "cal-eb-v1-structural-consumer-receipt-v1",
        "eb_head": projection["eb_head"],
        "valid_package_accepted": True,
        "projection": projection,
        "mutations": mutations,
        "all_mutations_refused": all(bool(row["refused"]) for row in mutations),
        "consumer_imports_evidence_bundler": False,
        "consumer_imports_cal_semantic_engine": False,
        "production_promotion_authorized": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["all_mutations_refused"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
