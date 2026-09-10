"""Research-only shadow representations for Contract C unresolved provenance."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Iterable


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _stable_id(namespace: str, value: Any) -> str:
    return f"{namespace}:{hashlib.sha256(canonical_bytes(value)).hexdigest()}"


def _target(base_c: dict[str, Any]) -> dict[str, Any]:
    props = base_c.get("propositions")
    if not isinstance(props, list) or len(props) != 1 or not isinstance(props[0], dict):
        raise ValueError("repair comparison requires exactly one proposition")
    return props[0]


def _state_ids(base_c: dict[str, Any]) -> list[str]:
    basis = _target(base_c)["conclusion"]["basis_members"]
    return [row["id"] for row in basis if row.get("namespace") == "state"]


def _normalize_refs(refs: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for ref in refs:
        row = {
            "source_id": str(ref["source_id"]),
            "passage_id": str(ref["passage_id"]),
            "passage_sha256": str(ref["passage_sha256"]),
        }
        rows.append(row)
    return sorted(rows, key=lambda row: (row["passage_id"], row["source_id"], row["passage_sha256"]))


def _reidentity(value: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(value)
    payload = deepcopy(out)
    payload.pop("result_set_id", None)
    out["result_set_id"] = "result-set:" + hashlib.sha256(canonical_bytes(payload)).hexdigest()
    return out


def candidate_a_neutral_contribution(
    base_c: dict[str, Any], causal_refs: Iterable[dict[str, str]]
) -> dict[str, Any]:
    """Shadow C: new non_deciding contribution type replaces opaque state-only basis."""
    out = deepcopy(base_c)
    prop = _target(out)
    refs = _normalize_refs(causal_refs)
    neutral = []
    for ref in refs:
        cid = _stable_id("contribution", {"channel": "non_deciding", "evidence_ref": ref})
        neutral.append({"contribution_id": cid, "channel": "non_deciding", "evidence_ref": ref})
    existing = list(prop.get("contributions") or [])
    prop["contributions"] = sorted(existing + neutral, key=lambda row: row["contribution_id"])
    prop["conclusion"]["basis_members"] = [
        {"namespace": "contribution", "id": row["contribution_id"]} for row in neutral
    ]
    prop["conclusion"]["causal_form"] = (
        "single_necessary" if len(neutral) == 1 else "independent_sufficient_alternatives"
    )
    all_basis = {row["id"] for row in prop["conclusion"]["basis_members"] if row["namespace"] == "contribution"}
    prop["conclusion"]["residual_contribution_ids"] = sorted(
        row["contribution_id"] for row in prop["contributions"] if row["contribution_id"] not in all_basis
    )
    return _reidentity(out)


def candidate_b_state_evidence_links(
    base_c: dict[str, Any], causal_refs: Iterable[dict[str, str]]
) -> dict[str, Any]:
    """Shadow C: preserve opaque state basis and add explicit state->evidence links."""
    out = deepcopy(base_c)
    prop = _target(out)
    state_ids = _state_ids(out)
    if len(state_ids) != 1:
        raise ValueError("candidate B expects exactly one opaque state basis id")
    prop["state_evidence_links"] = [
        {
            "state_id": state_ids[0],
            "evidence_refs": _normalize_refs(causal_refs),
            "role": "causal_non_deciding",
        }
    ]
    return _reidentity(out)


def candidate_c_evidence_bearing_state_basis(
    base_c: dict[str, Any], causal_refs: Iterable[dict[str, str]]
) -> dict[str, Any]:
    """Shadow C: keep state basis identity but make the basis member evidence-bearing."""
    out = deepcopy(base_c)
    prop = _target(out)
    refs = _normalize_refs(causal_refs)
    replaced = []
    for row in prop["conclusion"]["basis_members"]:
        member = deepcopy(row)
        if member.get("namespace") == "state":
            member["evidence_refs"] = refs
        replaced.append(member)
    prop["conclusion"]["basis_members"] = replaced
    return _reidentity(out)


def candidate_d_sidecar(
    base_c: dict[str, Any], causal_refs: Iterable[dict[str, str]], contract_c_sha256: str
) -> dict[str, Any]:
    """Leave Contract C unchanged; bind a separate immutable attribution receipt."""
    prop = _target(base_c)
    state_ids = _state_ids(base_c)
    if len(state_ids) != 1:
        raise ValueError("candidate D expects exactly one opaque state basis id")
    body = {
        "schema": "cal-producer-attribution-sidecar-rc0-v1",
        "contract_c_result_set_id": base_c["result_set_id"],
        "contract_c_sha256": contract_c_sha256,
        "proposition_id": prop["proposition"]["proposition_id"],
        "state_id": state_ids[0],
        "evidence_refs": _normalize_refs(causal_refs),
        "role": "causal_non_deciding",
    }
    return {**body, "receipt_id": _stable_id("producer-attribution", body)}


__all__ = [
    "canonical_bytes",
    "candidate_a_neutral_contribution",
    "candidate_b_state_evidence_links",
    "candidate_c_evidence_bearing_state_basis",
    "candidate_d_sidecar",
]
