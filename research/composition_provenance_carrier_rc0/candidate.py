"""Generic provenance-bearing carrier for qualified composition decisions."""

from __future__ import annotations

from .apparatus import (
    CompositionReceipt,
    CompositionRequest,
    expected_material,
    expected_receipt_id,
)


def bind_composition(request: CompositionRequest) -> CompositionReceipt:
    material = expected_material(request)
    return CompositionReceipt(
        receipt_id=expected_receipt_id(request),
        module_id=request.module_id,
        relation=request.relation,
        input_authority_ids=request.input_authority_ids,
        semantic_input_sha256=str(material["semantic_input_sha256"]),
        modifier_state_sha256=str(material["modifier_state_sha256"]),
        query_sha256=str(material["query_sha256"]),
    )
