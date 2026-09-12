from __future__ import annotations

from typing import Any

from .authority import (
    AuthorityReceipt,
    AuthorityRefusal,
    SemanticAtom,
    _event_source_fields,
    _strict_source_fields,
)
from .models import AuditContext, SemanticFamily, stable_id

_EXPECTED_STATUS = "WARRANTED"
_EXPECTED_REASON = "ALL_REQUIRED_WARRANT_ESTABLISHED"


class AuthorityIntegrityRefusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _atom_material(atom: SemanticAtom) -> dict[str, Any]:
    return {
        "semantic_family": atom.semantic_family.value,
        "audit_context_sha256": atom.audit_context_sha256,
        "evidence_world_sha256": atom.evidence_world_sha256,
        "passage_id": atom.passage_id,
        "source_id": atom.source_id,
        "fields": atom.field_map(),
        "measurement_receipt_id": atom.measurement_receipt_id,
    }


def _authority_material(authority: AuthorityReceipt) -> dict[str, Any]:
    return {
        "atom_id": authority.atom.atom_id,
        "audit_context_sha256": authority.audit_context_sha256,
        "evidence_world_sha256": authority.evidence_world_sha256,
        "status": authority.status,
        "reason": authority.reason,
    }


def _source_grounded_fields(context: AuditContext, atom: SemanticAtom) -> dict[str, str]:
    try:
        passage = context.evidence_world.passage(atom.passage_id)
    except KeyError as exc:
        raise AuthorityIntegrityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "authority atom passage is outside admitted evidence world",
        ) from exc
    if atom.source_id != passage.source_id:
        raise AuthorityIntegrityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "authority atom source does not match admitted passage source",
        )
    try:
        if atom.semantic_family is SemanticFamily.STRICT_COMPARISON:
            return _strict_source_fields(passage.text)
        if atom.semantic_family is SemanticFamily.DIRECT_EVENT_ORDER:
            return _event_source_fields(passage.text)
    except AuthorityRefusal as exc:
        raise AuthorityIntegrityRefusal(exc.code, exc.detail) from exc
    raise AuthorityIntegrityRefusal(
        "SEMANTIC_AUTHORITY_UNRESOLVED",
        "authority atom semantic family is unsupported",
    )


def verify_authority_for_relation(context: AuditContext, authority: AuthorityReceipt) -> None:
    """Revalidate authority integrity and source grounding before relation use.

    This is deliberately stronger than checking supplied context/world fields alone.
    It recomputes content-derived identities and re-grounds the semantic atom in the
    exact admitted passage available to the consumer.
    """

    if authority.status != _EXPECTED_STATUS or authority.reason != _EXPECTED_REASON:
        raise AuthorityIntegrityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "authority status/reason is not the warranted terminal state",
        )
    if authority.audit_context_sha256 != context.context_sha256:
        raise AuthorityIntegrityRefusal("PROPOSITION_BINDING_FAILED", "authority/context mismatch")
    if authority.evidence_world_sha256 != context.evidence_world.evidence_world_sha256:
        raise AuthorityIntegrityRefusal(
            "COMMON_EVIDENCE_WORLD_MISMATCH", "authority/world mismatch"
        )

    atom = authority.atom
    if atom.audit_context_sha256 != authority.audit_context_sha256:
        raise AuthorityIntegrityRefusal(
            "PROPOSITION_BINDING_FAILED", "atom/authority context mismatch"
        )
    if atom.evidence_world_sha256 != authority.evidence_world_sha256:
        raise AuthorityIntegrityRefusal(
            "COMMON_EVIDENCE_WORLD_MISMATCH", "atom/authority world mismatch"
        )
    if atom.semantic_family is not context.proposition.semantic_family:
        raise AuthorityIntegrityRefusal(
            "PROPOSITION_BINDING_FAILED", "atom/proposition semantic-family mismatch"
        )

    grounded = _source_grounded_fields(context, atom)
    if atom.field_map() != grounded:
        raise AuthorityIntegrityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "authority atom fields do not match independent source completion",
        )

    expected_atom_id = stable_id("semantic-atom", _atom_material(atom))
    if atom.atom_id != expected_atom_id:
        raise AuthorityIntegrityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED", "semantic atom identity mismatch"
        )

    expected_authority_id = stable_id("semantic-authority", _authority_material(authority))
    if authority.authority_id != expected_authority_id:
        raise AuthorityIntegrityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED", "semantic authority identity mismatch"
        )
