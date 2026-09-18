"""Positive-shape strict-comparison source completion for Gate-1B RC2."""

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

_ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
_MEASURE = r"share|rate|percentage|proportion|output|count|volume|score|yield"

_REL = {
    "more": "MORE_THAN",
    "fewer": "LESS_THAN",
    "less": "LESS_THAN",
    "greater": "MORE_THAN",
    "higher": "MORE_THAN",
    "larger": "MORE_THAN",
    "lower": "LESS_THAN",
    "smaller": "LESS_THAN",
}


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip(" .,:;\"'")).casefold()


def _scope_guard(text: str) -> None:
    low = _norm(text)

    if re.search(r"\b(?:not|no|never)\s+(?:greater|higher|larger|lower|smaller|more|less|fewer)\b", low):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "negated comparison is outside positive strict-comparison authority",
        )

    if re.search(
        r"\b(?:probably|possibly|perhaps|allegedly|supposedly|apparently|"
        r"reportedly|may|might|could|appears?|seems?)\b",
        low,
    ):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "epistemic or attribution scope is outside direct comparison authority",
        )

    if re.search(r"\baccording\s+to\b", low):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "attributed comparison is outside narrator authority",
        )

    if re.search(
        r"\b(?:report|study|article|author|witness)\b.*"
        r"\b(?:says?|said|states?|reported|claims?)\b",
        low,
    ):
        raise AuthorityRefusal(
            "SOURCE_COMPLETION_FAILED",
            "reported comparison is outside narrator authority",
        )


def _source_fields(text: str) -> dict[str, str]:
    _scope_guard(text)
    compact = " ".join(text.strip().split()).removesuffix(".")

    numeric_delta = re.fullmatch(
        rf"(?P<left>{_ENTITY})\s+"
        r"(?P<body>(?:processed|produced|recorded|handled|had)\b[^,]*),\s*"
        r"(?P<delta>.+?)\s+"
        r"(?P<rel>more|fewer|less)\s+than\s+"
        rf"(?P<right>{_ENTITY})",
        compact,
        re.IGNORECASE,
    )
    if numeric_delta is not None:
        rel = numeric_delta.group("rel").casefold()
        return {
            "left": _norm(numeric_delta.group("left")),
            "relation": _REL[rel],
            "right": _norm(numeric_delta.group("right")),
        }

    measured_adjective = re.fullmatch(
        rf"(?P<left>{_ENTITY})\s+"
        r"(?P<verb>had|has|recorded|records|showed|shows)\s+"
        r"(?:a\s+)?"
        r"(?P<rel>greater|higher|larger|lower|smaller)\s+"
        rf"(?P<measure>{_MEASURE})\s+than\s+"
        rf"(?P<right>{_ENTITY})",
        compact,
        re.IGNORECASE,
    )
    if measured_adjective is not None:
        rel = measured_adjective.group("rel").casefold()
        return {
            "left": _norm(measured_adjective.group("left")),
            "relation": _REL[rel],
            "right": _norm(measured_adjective.group("right")),
        }

    direct_copular = re.fullmatch(
        rf"(?P<left>{_ENTITY})\s+"
        r"(?P<verb>is|was|remained|stayed)\s+"
        r"(?P<rel>greater|higher|larger|lower|smaller)\s+than\s+"
        rf"(?P<right>{_ENTITY})",
        compact,
        re.IGNORECASE,
    )
    if direct_copular is not None:
        rel = direct_copular.group("rel").casefold()
        return {
            "left": _norm(direct_copular.group("left")),
            "relation": _REL[rel],
            "right": _norm(direct_copular.group("right")),
        }

    comparative_verb = re.fullmatch(
        rf"(?P<left>{_ENTITY})\s+"
        r"(?P<verb>exceeded|trailed)\s+"
        rf"(?P<right>{_ENTITY})(?:\s+by\s+.+)?",
        compact,
        re.IGNORECASE,
    )
    if comparative_verb is not None:
        relation = (
            "MORE_THAN"
            if comparative_verb.group("verb").casefold() == "exceeded"
            else "LESS_THAN"
        )
        return {
            "left": _norm(comparative_verb.group("left")),
            "relation": relation,
            "right": _norm(comparative_verb.group("right")),
        }

    raise AuthorityRefusal(
        "SOURCE_COMPLETION_FAILED",
        "source is outside the positive strict-comparison authority grammar",
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
            "one comparison proposal required",
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


def complete_and_warrant_strict_rc2(
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
