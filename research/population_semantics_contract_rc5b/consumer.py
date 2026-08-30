from __future__ import annotations

from typing import Any

from research.population_semantics_contract_rc5.consumer import relation as parent_relation


def _subclass_relation(case: dict[str, Any]) -> str:
    authority = case["authority"]
    query = case["query"]
    base = authority["membership_population"]
    target = query["population"]
    status = authority["membership"]
    edge = authority["subclass_edge"]

    if target == base:
        return {"member": "entailment", "non_member": "contradiction", "unknown": "neutral"}[status]

    if edge == "A_sub_B":
        if base == "A" and target == "B" and status == "member":
            return "entailment"
        if base == "B" and target == "A" and status == "non_member":
            return "contradiction"
        return "neutral"

    if edge == "B_sub_A":
        if base == "B" and target == "A" and status == "member":
            return "entailment"
        if base == "A" and target == "B" and status == "non_member":
            return "contradiction"
        return "neutral"

    if edge == "none":
        return "neutral"
    raise ValueError(edge)


def relation(case: dict[str, Any]) -> str:
    if case["dimension"] == "subclass":
        return _subclass_relation(case)
    return parent_relation(case)
