from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from claim_audit_lab.production_v1.semantic.authority import (
    AuthorityRefusal,
    complete_and_warrant,
)
from claim_audit_lab.production_v1.semantic.measurement_ledger import (
    MeasurementLedger,
    MeasurementLedgerRefusal,
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


def _receipts(context: AuditContext):
    strict = measure_strict_comparison(context, "comparison-passage")
    event = measure_direct_event_order(context, "event-passage")
    return strict, event


def test_empty_ledger_is_context_and_aperture_bound() -> None:
    context = _mixed_context()
    ledger = MeasurementLedger.empty(context)

    ledger.verify(context)
    assert ledger.audit_context_sha256 == context.context_sha256
    assert ledger.available_passage_ids == (
        "comparison-passage",
        "event-passage",
        "residual-passage",
    )
    assert ledger.receipts == ()
    assert ledger == MeasurementLedger.empty(context)


def test_heterogeneous_receipts_coexist_without_collapsing_observations() -> None:
    context = _mixed_context()
    strict, event = _receipts(context)

    ledger = MeasurementLedger.empty(context).append(context, strict).append(context, event)

    ledger.verify(context)
    assert {receipt.receipt_id for receipt in ledger.receipts} == {
        strict.receipt_id,
        event.receipt_id,
    }
    assert strict in ledger.receipts
    assert event in ledger.receipts
    assert strict.raw_measurement_json in {r.raw_measurement_json for r in ledger.receipts}
    assert event.raw_measurement_json in {r.raw_measurement_json for r in ledger.receipts}
    assert strict.available_passage_ids == ledger.available_passage_ids
    assert event.available_passage_ids == ledger.available_passage_ids
    assert strict.consumed_passage_ids == ("comparison-passage",)
    assert event.consumed_passage_ids == ("event-passage",)
    assert "residual-passage" not in strict.consumed_passage_ids
    assert "residual-passage" not in event.consumed_passage_ids


def test_ledger_identity_is_append_order_independent() -> None:
    context = _mixed_context()
    strict, event = _receipts(context)

    strict_first = MeasurementLedger.empty(context).append(context, strict).append(context, event)
    event_first = MeasurementLedger.empty(context).append(context, event).append(context, strict)

    assert strict_first.ledger_id == event_first.ledger_id
    assert strict_first.receipts == event_first.receipts


def test_ledger_rejects_duplicate_receipt_identity() -> None:
    context = _mixed_context()
    strict, _ = _receipts(context)
    ledger = MeasurementLedger.empty(context).append(context, strict)

    with pytest.raises(MeasurementLedgerRefusal, match="duplicate measurement receipt"):
        ledger.append(context, strict)


def test_ledger_rejects_receipt_from_foreign_context() -> None:
    context = _mixed_context()
    strict, _ = _receipts(context)
    foreign_context = replace(context, original_claim="A different exact claim surface.")
    foreign_ledger = MeasurementLedger.empty(foreign_context)

    with pytest.raises(MeasurementLedgerRefusal, match="measurement audit-context mismatch"):
        foreign_ledger.append(foreign_context, strict)


def test_ledger_rejects_stale_receipt_identity_after_payload_mutation() -> None:
    context = _mixed_context()
    strict, _ = _receipts(context)
    mutated = replace(
        strict,
        raw_measurement_json='{"proposals":[],"status":"NOT_APPLICABLE"}',
    )

    with pytest.raises(MeasurementLedgerRefusal, match="measurement receipt identity mismatch"):
        MeasurementLedger.empty(context).append(context, mutated)


def test_ledger_rejects_aperture_omission_or_rebinding() -> None:
    context = _mixed_context()
    strict, _ = _receipts(context)
    truncated = replace(strict, available_passage_ids=strict.available_passage_ids[:-1])

    with pytest.raises(
        MeasurementLedgerRefusal,
        match="measurement available-evidence aperture mismatch",
    ):
        MeasurementLedger.empty(context).append(context, truncated)


def test_ledger_exposes_observations_not_authority_or_aggregation() -> None:
    context = _mixed_context()
    strict, event = _receipts(context)
    ledger = MeasurementLedger.empty(context).append(context, strict).append(context, event)

    forbidden = (
        "authority",
        "warrant",
        "verdict",
        "conclusion",
        "relation",
        "decision",
        "confidence",
        "vote",
        "winner",
        "aggregate_score",
    )
    for name in forbidden:
        assert not hasattr(ledger, name)


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
