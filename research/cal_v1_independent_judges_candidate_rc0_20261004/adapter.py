"""Mechanical collect/synthesize transport for the RC0 toy policy.

This module is loaded by the frozen contract tests. It is not the fixture
probe, and it does not implement the semantic judges.
"""

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


def _snapshot(value: Any) -> dict[str, Any]:
    parsed = json.loads(_canonical(value))
    if not isinstance(parsed, dict):
        raise TypeError("lane receipt must be an object")
    return parsed


def _failed(lane: dict[str, Any], raw: bytes, exc: BaseException) -> dict[str, Any]:
    return {
        "process_id": lane["id"],
        "input_sha256": _digest(raw),
        "execution": "failed",
        "applicability": "unknown",
        "role": lane["role"],
        "conclusion": "unresolved",
        "warrant": "unqualified",
        "material_loss": False,
        "error": type(exc).__name__,
    }


def collect(raw: bytes, lanes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Call every lane with the same bytes and snapshot each receipt immediately."""
    found: list[dict[str, Any]] = []
    for lane in lanes:
        try:
            found.append(_snapshot(lane["call"](raw)))
        except Exception as exc:
            found.append(_failed(lane, raw, exc))
    return sorted(found, key=lambda row: str(row["process_id"]))


def _vocabulary(row: dict[str, Any], role: str) -> None:
    if row["execution"] not in {"completed", "failed"}:
        raise ValueError("execution vocabulary")
    if row["applicability"] not in {"applicable", "not_applicable", "unknown"}:
        raise ValueError("applicability vocabulary")
    if row["warrant"] not in {"qualified", "unqualified"} or type(row["material_loss"]) is not bool:
        raise ValueError("warrant or loss vocabulary")
    allowed = (
        {"supports", "refutes", "unresolved", "not_applicable"}
        if role == "relation"
        else {"satisfied", "violated", "unresolved", "not_applicable"}
    )
    if row["conclusion"] not in allowed:
        raise ValueError("local conclusion vocabulary")


def synthesize(raw: bytes, receipts: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    """Apply the toy policy. Extra receipt fields, including claimed_weight, are not votes."""
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
        weight = Fraction(lane["weight"])
        if weight < 0:
            raise ValueError("negative weight")
        _vocabulary(row, lane["role"])
        problem = _problem(row)
        if problem is not None:
            excluded[row["process_id"]] = problem
            if lane["required"] and problem != "not_applicable":
                blockers.add("required_unknown")
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
        bucket = groups.setdefault(lane["group"], {})
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
        if scores["supports"] >= minimum:
            outcome = "supported"
        elif scores["refutes"] >= minimum:
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


def _problem(row: dict[str, Any]) -> str | None:
    if row["execution"] == "failed":
        return "execution_failed"
    if row["applicability"] == "unknown":
        return "unknown_applicability"
    if row["applicability"] == "not_applicable":
        if row["conclusion"] != "not_applicable":
            raise ValueError("not-applicable conclusion mismatch")
        return "not_applicable"
    if row["warrant"] != "qualified":
        return "unqualified"
    if row["material_loss"]:
        return "material_loss"
    if row["conclusion"] == "unresolved":
        return "unresolved"
    return None
