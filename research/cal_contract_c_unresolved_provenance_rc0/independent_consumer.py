"""Independent released-Contract-C attribution consumer.

This module intentionally imports no CAL research/production code and performs no
semantic re-evaluation of source text. It asks only what exact evidence refs are
normatively linked to the terminal causal basis by Contract C 1.0 plus its bound
Contract-B index.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


class ConsumerRefusal(ValueError):
    pass


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConsumerRefusal(f"{label} must be an object")
    return value


def reconstruct_terminal_evidence(
    contract_c: dict[str, Any], contract_b_index: dict[str, Any], proposition_id: str
) -> dict[str, Any]:
    """Return only evidence refs reachable through released Contract C semantics."""
    c = _require_object(contract_c, "contract_c")
    b = _require_object(contract_b_index, "contract_b_index")
    binding = _require_object(_require_object(c.get("input"), "input").get("contract_b"), "contract_b")
    for key in ("contract_version", "bundle_id", "bundle_hash"):
        if binding.get(key) != b.get(key):
            raise ConsumerRefusal(f"Contract-B binding mismatch: {key}")

    propositions = c.get("propositions")
    if not isinstance(propositions, list):
        raise ConsumerRefusal("propositions must be an array")
    rows = [
        row for row in propositions
        if isinstance(row, dict)
        and isinstance(row.get("proposition"), dict)
        and row["proposition"].get("proposition_id") == proposition_id
    ]
    if len(rows) != 1:
        raise ConsumerRefusal("expected exactly one target proposition")
    row = rows[0]
    contributions = row.get("contributions")
    conclusion = _require_object(row.get("conclusion"), "conclusion")
    if not isinstance(contributions, list):
        raise ConsumerRefusal("contributions must be an array")
    by_id: dict[str, dict[str, Any]] = {}
    for item in contributions:
        obj = _require_object(item, "contribution")
        cid = obj.get("contribution_id")
        if not isinstance(cid, str) or cid in by_id:
            raise ConsumerRefusal("invalid or duplicate contribution id")
        by_id[cid] = obj

    basis = conclusion.get("basis_members")
    if not isinstance(basis, list):
        raise ConsumerRefusal("basis_members must be an array")

    evidence_refs: list[dict[str, str]] = []
    opaque_basis: list[dict[str, str]] = []
    for member in basis:
        obj = _require_object(member, "basis member")
        namespace = obj.get("namespace")
        identifier = obj.get("id")
        if not isinstance(namespace, str) or not isinstance(identifier, str):
            raise ConsumerRefusal("malformed basis member")
        if namespace == "contribution":
            contribution = by_id.get(identifier)
            if contribution is None:
                raise ConsumerRefusal("causal contribution basis is missing")
            ref = _require_object(contribution.get("evidence_ref"), "evidence_ref")
            evidence_refs.append(
                {
                    "source_id": str(ref.get("source_id")),
                    "passage_id": str(ref.get("passage_id")),
                    "passage_sha256": str(ref.get("passage_sha256")),
                }
            )
        else:
            # Contract C defines rule/state basis IDs as typed opaque identities.
            # There is no normative state/rule -> evidence reference edge here.
            opaque_basis.append({"namespace": namespace, "id": identifier})

    passages = _require_object(b.get("passages"), "Contract-B passages")
    all_bound_evidence = []
    for passage_id, raw in sorted(passages.items()):
        ref = _require_object(raw, f"passage {passage_id}")
        all_bound_evidence.append(
            {
                "source_id": str(ref.get("source_id")),
                "passage_id": str(passage_id),
                "passage_sha256": str(ref.get("passage_sha256")),
            }
        )

    uniquely_reconstructable = len(evidence_refs) == 1 and not opaque_basis
    return {
        "proposition_id": proposition_id,
        "reported_verdict": conclusion.get("reported_verdict"),
        "terminal_branch": conclusion.get("terminal_branch"),
        "causal_evidence_refs": deepcopy(evidence_refs),
        "opaque_causal_basis_members": deepcopy(opaque_basis),
        "all_bound_evidence_refs": all_bound_evidence,
        "unique_causal_evidence_ref_reconstructable": uniquely_reconstructable,
        "consumer_used_cal": False,
        "consumer_reran_semantics": False,
    }


__all__ = ["ConsumerRefusal", "reconstruct_terminal_evidence"]
