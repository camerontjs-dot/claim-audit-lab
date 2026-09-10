"""Evidence-world-bound temporal Contract C projection successor.

This module deliberately reuses the frozen first projector only after a stronger
proof boundary re-establishes the exact AuditContext / Contract-B evidence world.
It accepts no caller-supplied Contract-B binding or passage index.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from research.cal_event_order_relation_rc0 import candidate as temporal
from research.cal_temporal_contract_c_decision_rc0 import projection as first_projection
from research.cal_temporal_contract_c_decision_rc0.bound_relation import (
    BoundRelationRefusal,
    BoundTemporalComposition,
    BoundTemporalProof,
    compose_bound_temporal_proofs,
    verify_bound_temporal_proof,
)

TrustedKeys = Mapping[str, bytes]


@dataclass(frozen=True, slots=True)
class BoundProjectionResult:
    contract_c: dict
    contract_b_index: dict
    projection_status: str
    omitted_relation_ids: tuple[str, ...]
    carried_relation_ids: tuple[str, ...]
    composition: BoundTemporalComposition


def project_bound_temporal_contract_c(
    *,
    proposition: temporal.TemporalProposition,
    proofs: Iterable[BoundTemporalProof],
    atom_trusted_keys: TrustedKeys,
    proposition_trusted_keys: TrustedKeys,
) -> BoundProjectionResult:
    """Reverify exact proof inputs, compose one evidence world, then project C."""
    rows = tuple(proofs)
    if not rows:
        raise BoundRelationRefusal("NO_BOUND_RELATIONS", proposition.claim_id)

    composition = compose_bound_temporal_proofs(
        proposition=proposition,
        proofs=rows,
        atom_trusted_keys=atom_trusted_keys,
        proposition_trusted_keys=proposition_trusted_keys,
    )
    context = rows[0].context
    if composition.evidence_world_identity != (
        context.context_sha256,
        context.contract_b_version,
        context.bundle_id,
        context.bundle_hash,
    ):
        raise BoundRelationRefusal(
            "COMPOSITION_CONTEXT_BINDING_MISMATCH",
            proposition.claim_id,
        )

    verified = tuple(
        verify_bound_temporal_proof(
            proof=proof,
            atom_trusted_keys=atom_trusted_keys,
            proposition_trusted_keys=proposition_trusted_keys,
        )
        for proof in rows
    )
    for item in verified:
        if item.evidence_world_identity != composition.evidence_world_identity:
            raise BoundRelationRefusal(
                "PROJECTION_EVIDENCE_WORLD_MISMATCH",
                item.relation.relation_id,
            )

    binding = {
        "contract_version": context.contract_b_version,
        "bundle_id": context.bundle_id,
        "bundle_hash": context.bundle_hash,
    }
    evidence_index = {
        passage.passage_id: {
            "source_id": passage.source_id,
            "passage_sha256": passage.passage_sha256,
        }
        for passage in context.admitted_passages
    }
    projected = first_projection.project_temporal_contract_c(
        proposition=proposition,
        relations=tuple(item.relation for item in verified),
        conclusion=composition.conclusion,
        contract_b_binding=binding,
        evidence_index=evidence_index,
    )

    if projected.contract_c["input"]["contract_b"] != binding:
        raise BoundRelationRefusal("PROJECTED_CONTRACT_B_BINDING_MISMATCH", proposition.claim_id)
    if projected.contract_b_index["contract_version"] != binding["contract_version"]:
        raise BoundRelationRefusal("PROJECTED_INDEX_VERSION_MISMATCH", proposition.claim_id)
    if projected.contract_b_index["bundle_id"] != binding["bundle_id"]:
        raise BoundRelationRefusal("PROJECTED_INDEX_BUNDLE_ID_MISMATCH", proposition.claim_id)
    if projected.contract_b_index["bundle_hash"] != binding["bundle_hash"]:
        raise BoundRelationRefusal("PROJECTED_INDEX_BUNDLE_HASH_MISMATCH", proposition.claim_id)

    return BoundProjectionResult(
        contract_c=projected.contract_c,
        contract_b_index=projected.contract_b_index,
        projection_status=projected.projection_status,
        omitted_relation_ids=projected.omitted_relation_ids,
        carried_relation_ids=projected.carried_relation_ids,
        composition=composition,
    )


__all__ = ["BoundProjectionResult", "project_bound_temporal_contract_c"]
