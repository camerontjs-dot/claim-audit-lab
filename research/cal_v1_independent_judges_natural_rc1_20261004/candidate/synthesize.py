"""Late synthesis. Self-scored confidence, relevance, and weight are not votes."""

from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction
from typing import Any


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _problem(row: dict[str, Any]) -> str | None:
    execution = row["execution"]
    if execution == "not_run":
        return "not_run"
    if execution == "failed":
        return "execution_failed"
    if execution == "timeout":
        return "timeout"
    if row["applicability"] == "unknown":
        return "unknown_applicability"
    if row["applicability"] == "not_applicable":
        if row["conclusion"] != "not_applicable":
            raise ValueError("not-applicable conclusion mismatch")
        return "not_applicable"
    if row["warrant"] != "qualified":
        return "unqualified"
    if row["material_loss"] is True:
        return "material_loss"
    if row.get("local_material_conflict") is True:
        return "local_material_conflict"
    if row["conclusion"] == "unresolved":
        return "unresolved"
    return None


def synthesize(raw: bytes, receipts: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    spec = policy["lanes"]
    identities = [row["process_id"] for row in receipts]
    if len(identities) != len(set(identities)) or set(identities) != set(spec):
        raise ValueError("incomplete or duplicate process set")
    minimum = Fraction(policy["minimum"])
    if minimum <= 0:
        raise ValueError("invalid threshold")
    groups: dict[str, dict[str, Fraction]] = {}
    excluded: dict[str, str] = {}
    blockers: set[str] = set()
    bound = _digest(raw)
    for row in receipts:
        lane = spec[row["process_id"]]
        if row["input_sha256"] != bound or row["role"] != lane["role"]:
            raise ValueError("foreign input or role")
        if "claimed_weight" in row or "claimed_confidence" in row or "claimed_relevance" in row:
            excluded.setdefault(row["process_id"] + ":self_score", "ignored")
        weight = Fraction(lane["weight"])
        if weight < 0:
            raise ValueError("negative weight")
        problem = _problem(row)
        if problem is not None:
            excluded[row["process_id"]] = problem
            if lane["required"] and problem not in {"not_applicable", "not_run"}:
                blockers.add("required_unknown")
            if lane["required"] and problem == "not_run":
                blockers.add("required_not_run")
            if problem == "material_loss":
                blockers.add("material_loss")
            if problem == "local_material_conflict":
                blockers.add("material_conflict")
            continue
        if lane["role"] == "guard":
            if row["conclusion"] == "violated" and lane["required"]:
                blockers.add("guard_violation")
            excluded[row["process_id"]] = "non_voting_guard"
            continue
        if row["conclusion"] not in {"supports", "refutes"}:
            raise ValueError("incoherent relation")
        if weight == 0:
            excluded[row["process_id"]] = "zero_relevance"
            continue
        bucket = groups.setdefault(str(lane["group"]), {})
        direction = str(row["conclusion"])
        bucket[direction] = max(bucket.get(direction, Fraction(0)), weight)
    scores = {
        direction: sum((bucket.get(direction, Fraction(0)) for bucket in groups.values()), Fraction(0))
        for direction in ("supports", "refutes")
    }
    if scores["supports"] and scores["refutes"]:
        blockers.add("material_conflict")
    outcome = "not_checkable"
    if not blockers:
        if scores["supports"] >= minimum and scores["supports"] > scores["refutes"]:
            outcome = "supported"
        elif scores["refutes"] >= minimum and scores["refutes"] > scores["supports"]:
            outcome = "contradicted"
    return {
        "conclusion": outcome,
        "scores": {key: str(value) for key, value in scores.items()},
        "blockers": sorted(blockers),
        "exclusions": excluded,
        "receipts": sorted(copy.deepcopy(receipts), key=lambda row: str(row["process_id"])),
        "policy_sha256": _digest(_canonical(policy)),
        "input_sha256": bound,
    }
