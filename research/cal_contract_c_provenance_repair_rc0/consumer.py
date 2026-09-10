"""Candidate-specific independent reconstruction consumers.

No CAL semantic code is imported. Consumers follow only each shadow candidate's
published attribution semantics and exact Contract-B evidence references.
"""
from __future__ import annotations

from typing import Any


def _target(contract_c: dict[str, Any]) -> dict[str, Any]:
    rows = contract_c["propositions"]
    if len(rows) != 1:
        raise ValueError("expected exactly one proposition")
    return rows[0]


def _verify_ref(ref: dict[str, str], index: dict[str, Any]) -> dict[str, str]:
    passage_id = ref["passage_id"]
    expected = index["passages"].get(passage_id)
    if expected is None:
        raise ValueError(f"unknown evidence passage {passage_id}")
    if expected["source_id"] != ref["source_id"] or expected["passage_sha256"] != ref["passage_sha256"]:
        raise ValueError(f"evidence reference mismatch {passage_id}")
    return dict(ref)


def consume_a(contract_c: dict[str, Any], index: dict[str, Any]) -> list[dict[str, str]]:
    prop = _target(contract_c)
    by_id = {row["contribution_id"]: row for row in prop["contributions"]}
    refs = []
    for member in prop["conclusion"]["basis_members"]:
        if member["namespace"] != "contribution":
            continue
        row = by_id[member["id"]]
        if row["channel"] == "non_deciding":
            refs.append(_verify_ref(row["evidence_ref"], index))
    return sorted(refs, key=lambda row: row["passage_id"])


def consume_b(contract_c: dict[str, Any], index: dict[str, Any]) -> list[dict[str, str]]:
    prop = _target(contract_c)
    state_ids = {
        row["id"] for row in prop["conclusion"]["basis_members"] if row["namespace"] == "state"
    }
    refs = []
    for link in prop.get("state_evidence_links", []):
        if link["state_id"] not in state_ids:
            raise ValueError("state evidence link is not bound to causal state basis")
        if link["role"] != "causal_non_deciding":
            raise ValueError("unexpected state evidence role")
        refs.extend(_verify_ref(ref, index) for ref in link["evidence_refs"])
    return sorted(refs, key=lambda row: row["passage_id"])


def consume_c(contract_c: dict[str, Any], index: dict[str, Any]) -> list[dict[str, str]]:
    prop = _target(contract_c)
    refs = []
    for member in prop["conclusion"]["basis_members"]:
        if member["namespace"] == "state":
            refs.extend(_verify_ref(ref, index) for ref in member.get("evidence_refs", []))
    return sorted(refs, key=lambda row: row["passage_id"])


def consume_d(
    contract_c: dict[str, Any], index: dict[str, Any], sidecar: dict[str, Any], contract_c_sha256: str
) -> list[dict[str, str]]:
    prop = _target(contract_c)
    state_ids = {
        row["id"] for row in prop["conclusion"]["basis_members"] if row["namespace"] == "state"
    }
    if sidecar["contract_c_result_set_id"] != contract_c["result_set_id"]:
        raise ValueError("sidecar result-set binding mismatch")
    if sidecar["contract_c_sha256"] != contract_c_sha256:
        raise ValueError("sidecar whole-object binding mismatch")
    if sidecar["proposition_id"] != prop["proposition"]["proposition_id"]:
        raise ValueError("sidecar proposition mismatch")
    if sidecar["state_id"] not in state_ids:
        raise ValueError("sidecar state mismatch")
    if sidecar["role"] != "causal_non_deciding":
        raise ValueError("unexpected sidecar role")
    return sorted(
        (_verify_ref(ref, index) for ref in sidecar["evidence_refs"]),
        key=lambda row: row["passage_id"],
    )


__all__ = ["consume_a", "consume_b", "consume_c", "consume_d"]
