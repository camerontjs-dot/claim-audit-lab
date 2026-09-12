from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from claim_audit_lab.cal_v1_candidate import (
    AdmittedPassage,
    AuditContext,
    CategoricalRelation,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)
from claim_audit_lab.cal_v1_candidate.authority import complete_and_warrant
from claim_audit_lab.cal_v1_candidate.measurements import measure_strict_comparison
from claim_audit_lab.cal_v1_candidate.models import stable_id
from claim_audit_lab.cal_v1_candidate.relations import RelationRefusal, derive_relation


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _context(bundle_id: str) -> AuditContext:
    passage = AdmittedPassage.create(
        "rc1-p1",
        "rc1-source",
        "Quartz Lab recorded a higher rate than Flint Lab.",
    )
    world = EvidenceWorld.create(
        "1.2.0",
        bundle_id,
        _tagged(bundle_id),
        (passage,),
        {
            "search_scope": {"fixture": "authority-integrity-rc1"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        "rc1-claim",
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Quartz Lab",
            "rhs_entity": "Flint Lab",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=_hex("Quartz Lab had a higher rate than Flint Lab."),
    )
    return AuditContext(
        "Quartz Lab had a higher rate than Flint Lab.", proposition, world
    )


def _authority(context: AuditContext):
    receipt = measure_strict_comparison(context, "rc1-p1")
    return complete_and_warrant(context, receipt, "rc1-p1")


def _atom_material(atom) -> dict[str, object]:
    return {
        "semantic_family": atom.semantic_family.value,
        "audit_context_sha256": atom.audit_context_sha256,
        "evidence_world_sha256": atom.evidence_world_sha256,
        "passage_id": atom.passage_id,
        "source_id": atom.source_id,
        "fields": atom.field_map(),
        "measurement_receipt_id": atom.measurement_receipt_id,
    }


def _authority_material(authority) -> dict[str, object]:
    return {
        "atom_id": authority.atom.atom_id,
        "audit_context_sha256": authority.audit_context_sha256,
        "evidence_world_sha256": authority.evidence_world_sha256,
        "status": authority.status,
        "reason": authority.reason,
    }


def test_valid_authority_still_derives_support() -> None:
    context = _context("rc1-control")
    relation = derive_relation(context, _authority(context))
    assert relation.categorical_relation is CategoricalRelation.SUPPORTS


def test_rebound_authority_with_stale_ids_is_rejected() -> None:
    source = _context("rc1-world-a")
    target = _context("rc1-world-b")
    authority = _authority(source)
    rebound_atom = replace(
        authority.atom,
        audit_context_sha256=target.context_sha256,
        evidence_world_sha256=target.evidence_world.evidence_world_sha256,
    )
    rebound = replace(
        authority,
        audit_context_sha256=target.context_sha256,
        evidence_world_sha256=target.evidence_world.evidence_world_sha256,
        atom=rebound_atom,
    )
    with pytest.raises(RelationRefusal, match="semantic atom identity mismatch"):
        derive_relation(target, rebound)


def test_recomputed_atom_with_stale_authority_id_is_rejected() -> None:
    source = _context("rc1-partial-a")
    target = _context("rc1-partial-b")
    authority = _authority(source)
    rebound_atom = replace(
        authority.atom,
        audit_context_sha256=target.context_sha256,
        evidence_world_sha256=target.evidence_world.evidence_world_sha256,
    )
    rebound_atom = replace(
        rebound_atom,
        atom_id=stable_id("semantic-atom", _atom_material(rebound_atom)),
    )
    rebound = replace(
        authority,
        audit_context_sha256=target.context_sha256,
        evidence_world_sha256=target.evidence_world.evidence_world_sha256,
        atom=rebound_atom,
    )
    with pytest.raises(RelationRefusal, match="semantic authority identity mismatch"):
        derive_relation(target, rebound)


def test_self_consistent_fabricated_atom_semantics_are_source_refused() -> None:
    context = _context("rc1-forged-fields")
    authority = _authority(context)
    forged_atom = replace(
        authority.atom,
        fields=(
            ("left", "quartz lab"),
            ("relation", "LESS_THAN"),
            ("right", "flint lab"),
        ),
    )
    forged_atom = replace(
        forged_atom,
        atom_id=stable_id("semantic-atom", _atom_material(forged_atom)),
    )
    forged = replace(authority, atom=forged_atom)
    forged = replace(
        forged,
        authority_id=stable_id("semantic-authority", _authority_material(forged)),
    )
    with pytest.raises(
        RelationRefusal,
        match="authority atom fields do not match independent source completion",
    ):
        derive_relation(context, forged)
