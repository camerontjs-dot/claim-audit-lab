"""Modifier-aware independent source completion for strict-comparison Gate-1B RC1."""

from __future__ import annotations

import re
from typing import Any

from claim_audit_lab.production_v1.semantic.authority import (
    AuthorityReceipt,
    AuthorityRefusal,
    SemanticAtom,
)
from claim_audit_lab.production_v1.semantic.measurements import (
    STRICT_INSTRUMENT_ID,
    STRICT_INSTRUMENT_VERSION,
    MeasurementReceipt,
    verify_measurement_receipt,
)
from claim_audit_lab.production_v1.semantic.models import (
    AuditContext,
    SemanticFamily,
    stable_id,
)


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip(" .,:;\"'")).casefold()


_ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
_MEASURE = r"share|rate|percentage|proportion|output|count|volume|score|yield"


def _refuse_modifier_scope(text: str) -> None:
    low = f" {_norm(text)} "

    if re.search(
        r"\b(report|study|author|witness)\b.*\b(says?|said|states?|reported|claims?)\b",
        low,
    ):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "reported or attributed comparison is outside direct authority",
        )

    if re.search(
        r"\b(probably|possibly|perhaps|allegedly|apparently|reportedly|may|might|could)\b",
        low,
    ):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "epistemic or attribution modifier is outside direct authority",
        )

    if re.search(
        r"\bnot\s+(?:greater|higher|larger|lower|smaller|more|less|fewer)\b",
        low,
    ):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "comparison negation is not represented by the strict atom",
        )

    if re.search(
        r"\bno\s+(?:greater|higher|larger|lower|smaller|more|less|fewer)\b",
        low,
    ):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "no-comparison scope is not represented by the strict atom",
        )


def _source_fields(text: str) -> dict[str, str]:
    _refuse_modifier_scope(text)
    normalized = " ".join(text.strip().split())

    numeric_delta = re.fullmatch(
        rf"(?P<left>{_ENTITY})\s+.+?,\s*.+?\s+"
        rf"(?P<rel>(?i:more|fewer|less))\s+than\s+"
        rf"(?P<right>{_ENTITY})\.?",
        normalized,
    )
    if numeric_delta is not None:
        rel = numeric_delta.group("rel").casefold()
        return {
            "left": _norm(numeric_delta.group("left")),
            "relation": "MORE_THAN" if rel == "more" else "LESS_THAN",
            "right": _norm(numeric_delta.group("right")),
        }

    adjective = re.fullmatch(
        rf"(?P<left>{_ENTITY})\s+.+?\b"
        rf"(?P<rel>(?i:greater|higher|larger|lower|smaller))\b"
        rf"(?:\s+(?:{_MEASURE}))?\s+than\s+"
        rf"(?P<right>{_ENTITY})\.?",
        normalized,
    )
    if adjective is not None:
        rel = adjective.group("rel").casefold()
        return {
            "left": _norm(adjective.group("left")),
            "relation": (
                "MORE_THAN"
                if rel in {"greater", "higher", "larger"}
                else "LESS_THAN"
            ),
            "right": _norm(adjective.group("right")),
        }

    verb = re.fullmatch(
        rf"(?P<left>{_ENTITY})\s+"
        rf"(?P<verb>(?i:exceeded|trailed))\s+"
        rf"(?P<right>{_ENTITY})(?:\s+by\s+.+)?\.?",
        normalized,
    )
    if verb is not None:
        return {
            "left": _norm(verb.group("left")),
            "relation": (
                "MORE_THAN"
                if verb.group("verb").casefold() == "exceeded"
                else "LESS_THAN"
            ),
            "right": _norm(verb.group("right")),
        }

    raise AuthorityRefusal(
        "SOURCE_COMPLETION_FAILED",
        "strict comparison source not independently reconstructable",
    )


def _measurement_fields(receipt: MeasurementReceipt) -> dict[str, str]:
    raw = receipt.raw_measurement()
    if raw.get("status") != "CLAIMED":
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            str(raw.get("status")),
        )
    proposals = raw.get("proposals")
    if (
        not isinstance(proposals, list)
        or len(proposals) != 1
        or not isinstance(proposals[0], dict)
    ):
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "one strict-comparison proposal required",
        )
    proposal = proposals[0]
    try:
        return {
            "left": str(proposal["left"]),
            "relation": str(proposal["relation"]),
            "right": str(proposal["right"]),
        }
    except KeyError as exc:
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "comparison proposal shape",
        ) from exc


def complete_and_warrant_strict(
    context: AuditContext,
    receipt: MeasurementReceipt,
    passage_id: str,
) -> AuthorityReceipt:
    try:
        verify_measurement_receipt(context, receipt)
    except ValueError as exc:
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            str(exc),
        ) from exc

    if context.proposition.semantic_family is not SemanticFamily.STRICT_COMPARISON:
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "proposition family mismatch",
        )
    if receipt.semantic_family is not SemanticFamily.STRICT_COMPARISON:
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "measurement family mismatch",
        )
    if (
        receipt.instrument_id != STRICT_INSTRUMENT_ID
        or receipt.instrument_version != STRICT_INSTRUMENT_VERSION
    ):
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "strict instrument identity mismatch",
        )
    if receipt.consumed_passage_ids != (passage_id,):
        raise AuthorityRefusal(
            "SEMANTIC_AUTHORITY_UNRESOLVED",
            "authority requires exactly one named passage",
        )

    passage = context.evidence_world.passage(passage_id)
    measured = _measurement_fields(receipt)
    completed = _source_fields(passage.text)
    if measured != completed:
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "measurement semantics do not match independent source completion",
        )

    atom_material = {
        "semantic_family": receipt.semantic_family.value,
        "audit_context_sha256": context.context_sha256,
        "evidence_world_sha256": context.evidence_world.evidence_world_sha256,
        "passage_id": passage_id,
        "source_id": passage.source_id,
        "fields": completed,
        "measurement_receipt_id": receipt.receipt_id,
    }
    atom = SemanticAtom(
        atom_id=stable_id("semantic-atom", atom_material),
        semantic_family=receipt.semantic_family,
        audit_context_sha256=context.context_sha256,
        evidence_world_sha256=context.evidence_world.evidence_world_sha256,
        passage_id=passage_id,
        source_id=passage.source_id,
        fields=tuple(sorted(completed.items())),
        measurement_receipt_id=receipt.receipt_id,
    )
    authority_material: dict[str, Any] = {
        "atom_id": atom.atom_id,
        "audit_context_sha256": atom.audit_context_sha256,
        "evidence_world_sha256": atom.evidence_world_sha256,
        "status": "WARRANTED",
        "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
    }
    return AuthorityReceipt(
        authority_id=stable_id("semantic-authority", authority_material),
        audit_context_sha256=context.context_sha256,
        evidence_world_sha256=context.evidence_world.evidence_world_sha256,
        atom=atom,
    )
