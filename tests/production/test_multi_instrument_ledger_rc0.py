from __future__ import annotations

import hashlib

import pytest

from claim_audit_lab.production_v1.semantic.authority import (
    AuthorityRefusal,
    complete_and_warrant,
)
from claim_audit_lab.production_v1.semantic.measurements import (
    measure_direct_event_order,
    measure_strict_comparison,
)
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _mixed_context() -> AuditContext:
    comparison = AdmittedPassage.create(
        "comparison-passage",
        "source-comparison",
        "Women had a higher rate than Men.",
    )
    event = AdmittedPassage.create(
        "event-passage",
        "source-event",
        "Alice reviewed dossier before Bob archived dossier.",
    )
    residual = AdmittedPassage.create(
        "residual-passage",
        "source-residual",
        "A third admitted passage is unrelated to either instrument.",
    )
    world = EvidenceWorld.create(
        "1.2.0",
        "bundle-ledger-rc0",
        _tagged("bundle-ledger-rc0"),
        (comparison, event, residual),
        {
            "search_scope": {"corpus": "multi-instrument-ledger-rc0"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        "claim-ledger-rc0",
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=_hex("Women had a higher rate than Men."),
    )
    return AuditContext("Women had a higher rate than Men.", proposition, world)


def test_same_family_direct_authority_path_remains_valid() -> None:
    context = _mixed_context()
    receipt = measure_strict_comparison(context, "comparison-passage")

    authority = complete_and_warrant(context, receipt, "comparison-passage")

    assert authority.atom.semantic_family is SemanticFamily.STRICT_COMPARISON
    assert authority.atom.measurement_receipt_id == receipt.receipt_id


def test_foreign_family_measurement_cannot_be_warranted_directly() -> None:
    context = _mixed_context()
    foreign = measure_direct_event_order(context, "event-passage")
    assert foreign.semantic_family is SemanticFamily.DIRECT_EVENT_ORDER
    assert foreign.audit_context_sha256 == context.context_sha256

    with pytest.raises(
        AuthorityRefusal,
        match="measurement/proposition semantic-family mismatch",
    ):
        complete_and_warrant(context, foreign, "event-passage")
