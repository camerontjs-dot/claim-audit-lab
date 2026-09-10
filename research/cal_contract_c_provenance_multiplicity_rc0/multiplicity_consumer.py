"""Independent consumer for frozen provenance-repair shadow candidates.

No CAL imports and no source-text semantic re-evaluation.
"""
from __future__ import annotations

from typing import Any

from research.cal_contract_c_provenance_repair_rc0 import consumer as provenance_consumer


def _target(contract_c: dict[str, Any]) -> dict[str, Any]:
    rows = contract_c["propositions"]
    if len(rows) != 1:
        raise ValueError("expected exactly one proposition")
    return rows[0]


def inspect_candidate(
    name: str,
    payload: dict[str, Any],
    index: dict[str, Any],
    contract_c_sha256: str,
) -> dict[str, Any]:
    c = payload["contract_c"]
    prop = _target(c)
    if name.startswith("A_"):
        refs = provenance_consumer.consume_a(c, index)
        basis = prop["conclusion"]["basis_members"]
        neutral_basis_ids = {
            row["id"] for row in basis if row.get("namespace") == "contribution"
        }
        neutral_contributions = [
            row for row in prop["contributions"]
            if row.get("channel") == "non_deciding"
            and row.get("contribution_id") in neutral_basis_ids
        ]
        if len(neutral_contributions) != len(refs):
            multiplicity = "not_reconstructable"
        else:
            multiplicity = prop["conclusion"].get("causal_form", "not_reconstructable")
    elif name.startswith("B_"):
        refs = provenance_consumer.consume_b(c, index)
        # The conclusion's causal_form classifies the single opaque state basis,
        # not the relation among evidence refs inside a state_evidence_links array.
        multiplicity = "not_reconstructable_at_evidence_level"
    elif name.startswith("C_"):
        refs = provenance_consumer.consume_c(c, index)
        # Multiple refs are payload on one state basis member. No field states whether
        # those evidence refs are alternatives, jointly required, or merely grouped.
        multiplicity = "not_reconstructable_at_evidence_level"
    elif name.startswith("D_"):
        refs = provenance_consumer.consume_d(c, index, payload["sidecar"], contract_c_sha256)
        # Sidecar role is causal_non_deciding but contains no multiplicity operator.
        multiplicity = "not_reconstructable_at_evidence_level"
    else:
        raise ValueError(name)
    return {
        "causal_passage_ids": sorted(row["passage_id"] for row in refs),
        "evidence_level_causal_form": multiplicity,
        "semantic_reaudit_performed": False,
    }


__all__ = ["inspect_candidate"]
