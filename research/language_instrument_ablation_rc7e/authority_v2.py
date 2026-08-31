"""RC7E portfolio authority with per-receipt provenance preserved.

The first candidate pooled anchors across the complete proposal union. This
pre-held-out revision validates each instrument receipt separately and merges
only the resulting authority records, preventing cross-instrument anchor
leakage while preserving every rejection and unresolved proposal.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from research.language_instrument_ablation_rc7e.authority import validate_common_receipt
from research.language_instrument_ablation_rc7e.contract import source_sha


def validate_portfolio(raw: str, receipts: list[dict[str, Any]]) -> dict[str, Any]:
    authorized: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rejected: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    validations: list[dict[str, Any]] = []

    for receipt in receipts:
        if receipt.get("raw_source") != raw or receipt.get("raw_source_sha256") != source_sha(raw):
            raise AssertionError("portfolio authority received altered or mismatched source")
        if receipt.get("instrument_id") == "deberta_nli":
            unresolved.append(
                {
                    "instrument_id": "deberta_nli",
                    "dimension": None,
                    "atom": None,
                    "reason": "nli_relation_measurement_has_no_direct_authority_jurisdiction",
                }
            )
            continue
        result = validate_common_receipt(receipt)
        validations.append(result)
        for dim, atoms in result.get("authorized_atoms", {}).items():
            authorized[dim].extend(atoms)
        rejected.extend(result.get("rejected_proposals", []))
        unresolved.extend(result.get("unresolved_proposals", []))

    return {
        "raw_source": raw,
        "raw_source_sha256": source_sha(raw),
        "instrument_id": "portfolio_authority_v2",
        "authority_version": "rc7e-portfolio-authority-v2",
        "authorized_atoms": dict(authorized),
        "authorized_dimensions": sorted(authorized),
        "rejected_proposals": rejected,
        "unresolved_proposals": unresolved,
        "validation_receipts": validations,
        "apparatus_note": "each instrument receipt validated separately before authority merge",
    }
