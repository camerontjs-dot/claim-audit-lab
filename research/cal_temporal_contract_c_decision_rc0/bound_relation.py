"""Evidence-world-bound successor for Phase-3 temporal relations.

Research-only. A BoundTemporalProof retains the original immutable AuditContext
and authenticated inputs needed to reconstruct and re-verify the temporal atom
and proposition relation. Composition never trusts a naked Phase-3 relation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from research.cal_measurement_envelope_rc0.envelope import AuditContext, MeasurementReceipt
from research.cal_event_order_authority_rc0 import candidate as event_authority
from research.cal_event_order_relation_rc0 import candidate as temporal

TrustedKeys = Mapping[str, bytes]


class BoundRelationRefusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True, slots=True)
class BoundTemporalProof:
    context: AuditContext
    measurement_receipt: MeasurementReceipt
    passage_id: str
    proposition: temporal.TemporalProposition
    atom_warrant: dict[str, Any]
    proposition_binding: dict[str, Any]
    relation: temporal.TemporalRelationRecord


@dataclass(frozen=True, slots=True)
class VerifiedBoundTemporalRelation:
    relation: temporal.TemporalRelationRecord
    audit_context_sha256: str
    contract_b_version: str
    bundle_id: str
    bundle_hash: str
    source_id: str
    passage_id: str
    passage_sha256: str
    measurement_receipt_id: str
    atom_id: str
    proposition_projection: dict[str, Any]

    @property
    def evidence_world_identity(self) -> tuple[str, str, str, str]:
        return (
            self.audit_context_sha256,
            self.contract_b_version,
            self.bundle_id,
            self.bundle_hash,
        )


@dataclass(frozen=True, slots=True)
class BoundTemporalComposition:
    conclusion: temporal.TemporalConclusion
    audit_context_sha256: str
    contract_b_version: str
    bundle_id: str
    bundle_hash: str
    proposition_projection: dict[str, Any]
    relation_ids: tuple[str, ...]

    @property
    def evidence_world_identity(self) -> tuple[str, str, str, str]:
        return (
            self.audit_context_sha256,
            self.contract_b_version,
            self.bundle_id,
            self.bundle_hash,
        )


def _context_proposition_checks(
    *, context: AuditContext, proposition: temporal.TemporalProposition
) -> None:
    if context.proposition_id != proposition.claim_id:
        raise BoundRelationRefusal(
            "CONTEXT_PROPOSITION_ID_MISMATCH",
            f"{context.proposition_id!r} != {proposition.claim_id!r}",
        )
    if context.original_claim_id != proposition.claim_id:
        raise BoundRelationRefusal(
            "CONTEXT_CLAIM_ID_MISMATCH",
            f"{context.original_claim_id!r} != {proposition.claim_id!r}",
        )
    if context.original_claim_text != proposition.claim_text:
        raise BoundRelationRefusal(
            "CONTEXT_CLAIM_TEXT_MISMATCH",
            "AuditContext original claim text differs from exact proposition text",
        )
    payload = context.proposition_payload
    if payload.get("family") != temporal.EVENT_FAMILY:
        raise BoundRelationRefusal(
            "CONTEXT_SEMANTIC_FAMILY_MISMATCH",
            repr(payload.get("family")),
        )


def verify_bound_temporal_proof(
    *,
    proof: BoundTemporalProof,
    atom_trusted_keys: TrustedKeys,
    proposition_trusted_keys: TrustedKeys,
) -> VerifiedBoundTemporalRelation:
    if not isinstance(proof, BoundTemporalProof):
        raise BoundRelationRefusal("INVALID_BOUND_PROOF", type(proof).__name__)
    context = proof.context
    proposition = proof.proposition
    _context_proposition_checks(context=context, proposition=proposition)

    try:
        atom = event_authority.complete_event_order_atom(
            context=context,
            receipt=proof.measurement_receipt,
            passage_id=proof.passage_id,
        )
    except Exception as exc:
        code = getattr(exc, "code", type(exc).__name__)
        raise BoundRelationRefusal("SOURCE_RECONSTRUCTION_FAILED", str(code)) from exc

    case = event_authority.build_rc8j_case(atom=atom)
    try:
        temporal.verify_event_atom_warrant(
            case=case,
            receipt=proof.atom_warrant,
            trusted_keys=atom_trusted_keys,
        )
    except temporal.RelationRefusal as exc:
        raise BoundRelationRefusal("ATOM_WARRANT_REVERIFY_FAILED", exc.code) from exc
    try:
        temporal.verify_proposition_binding(
            proposition=proposition,
            receipt=proof.proposition_binding,
            trusted_keys=proposition_trusted_keys,
        )
    except temporal.RelationRefusal as exc:
        raise BoundRelationRefusal("PROPOSITION_BINDING_REVERIFY_FAILED", exc.code) from exc

    try:
        derived = temporal.derive_temporal_relation(
            case=case,
            proposition=proposition,
            atom_warrant=proof.atom_warrant,
            atom_trusted_keys=atom_trusted_keys,
            proposition_binding=proof.proposition_binding,
            proposition_trusted_keys=proposition_trusted_keys,
        )
    except temporal.RelationRefusal as exc:
        raise BoundRelationRefusal("RELATION_REDERIVATION_FAILED", exc.code) from exc
    if derived != proof.relation:
        raise BoundRelationRefusal(
            "RELATION_REDERIVATION_MISMATCH",
            proof.relation.relation_id,
        )

    passage = context.passage(proof.passage_id)
    if derived.evidence_ref != {
        "source_id": passage.source_id,
        "passage_id": passage.passage_id,
    }:
        raise BoundRelationRefusal(
            "RELATION_EVIDENCE_CONTEXT_MISMATCH",
            derived.relation_id,
        )
    if derived.atom_id != atom.atom_id:
        raise BoundRelationRefusal("RELATION_ATOM_MISMATCH", derived.relation_id)

    return VerifiedBoundTemporalRelation(
        relation=derived,
        audit_context_sha256=context.context_sha256,
        contract_b_version=context.contract_b_version,
        bundle_id=context.bundle_id,
        bundle_hash=context.bundle_hash,
        source_id=passage.source_id,
        passage_id=passage.passage_id,
        passage_sha256=passage.passage_sha256,
        measurement_receipt_id=proof.measurement_receipt.receipt_id,
        atom_id=atom.atom_id,
        proposition_projection=temporal.proposition_projection(proposition),
    )


def compose_bound_temporal_proofs(
    *,
    proposition: temporal.TemporalProposition,
    proofs: Iterable[BoundTemporalProof],
    atom_trusted_keys: TrustedKeys,
    proposition_trusted_keys: TrustedKeys,
) -> BoundTemporalComposition:
    rows = tuple(proofs)
    if not rows:
        raise BoundRelationRefusal("NO_BOUND_RELATIONS", proposition.claim_id)
    exact_projection = temporal.proposition_projection(proposition)
    verified: list[VerifiedBoundTemporalRelation] = []
    for proof in rows:
        if proof.proposition != proposition:
            raise BoundRelationRefusal(
                "BOUND_PROPOSITION_OBJECT_MISMATCH",
                proof.relation.relation_id,
            )
        item = verify_bound_temporal_proof(
            proof=proof,
            atom_trusted_keys=atom_trusted_keys,
            proposition_trusted_keys=proposition_trusted_keys,
        )
        if item.proposition_projection != exact_projection:
            raise BoundRelationRefusal(
                "BOUND_PROPOSITION_PROJECTION_MISMATCH",
                item.relation.relation_id,
            )
        verified.append(item)

    first_world = verified[0].evidence_world_identity
    for item in verified[1:]:
        if item.evidence_world_identity != first_world:
            raise BoundRelationRefusal(
                "COMMON_EVIDENCE_WORLD_MISMATCH",
                item.relation.relation_id,
            )

    relation_ids = tuple(item.relation.relation_id for item in verified)
    if len(relation_ids) != len(set(relation_ids)):
        raise BoundRelationRefusal("DUPLICATE_BOUND_RELATION", proposition.claim_id)

    conclusion = temporal.compose_temporal_relations(
        proposition=proposition,
        relations=tuple(item.relation for item in verified),
    )
    context = rows[0].context
    return BoundTemporalComposition(
        conclusion=conclusion,
        audit_context_sha256=context.context_sha256,
        contract_b_version=context.contract_b_version,
        bundle_id=context.bundle_id,
        bundle_hash=context.bundle_hash,
        proposition_projection=exact_projection,
        relation_ids=tuple(sorted(relation_ids)),
    )


__all__ = [
    "BoundRelationRefusal",
    "BoundTemporalComposition",
    "BoundTemporalProof",
    "VerifiedBoundTemporalRelation",
    "compose_bound_temporal_proofs",
    "verify_bound_temporal_proof",
]
