from __future__ import annotations

import hashlib
import json
from typing import Any

from research.population_semantics_contract_rc5.build_corpus import build as build_rc5

SCHEMA_VERSION = "population-semantics-contract-rc5a.0"


def _internally_consistent(case: dict[str, Any]) -> bool:
    if case.get("dimension") != "only_permission":
        return True
    authority = case["authority"]
    impossible = (
        authority.get("only_population_may") is True
        and authority.get("membership") == "non_member"
        and authority.get("explicit_permission") == "permitted"
    )
    return not impossible


def build() -> dict[str, Any]:
    parent = build_rc5()
    cases = [case for case in parent["cases"] if _internally_consistent(case)]
    return {
        "schema_version": SCHEMA_VERSION,
        "parent_schema_version": parent["schema_version"],
        "correction": "remove internally inconsistent declared-authority states only",
        "cases": cases,
        "ablation_witnesses": parent["ablation_witnesses"],
        "metamorphic_pairs": parent["metamorphic_pairs"],
    }


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256() -> str:
    return hashlib.sha256(canonical_bytes(build())).hexdigest()


if __name__ == "__main__":
    corpus = build()
    print(json.dumps({
        "sha256": sha256(),
        "n_cases": len(corpus["cases"]),
        "n_ablation_witnesses": len(corpus["ablation_witnesses"]),
        "n_metamorphic_pairs": len(corpus["metamorphic_pairs"]),
    }, indent=2, sort_keys=True))
