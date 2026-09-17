from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from typing import Any

from claim_audit_lab.production_v1.semantic.engine import (
    ShadowMeasurementInstrument,
    audit,
    audit_observed,
)
from claim_audit_lab.production_v1.semantic.measurements import (
    MeasurementReceipt,
    measure_direct_event_order,
)
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
    stable_id,
)


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _context() -> AuditContext:
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
        "bundle-shadow-runtime-rc0",
        _tagged("bundle-shadow-runtime-rc0"),
        (comparison, event, residual),
        {
            "search_scope": {"corpus": "shadow-observation-runtime-rc0"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        "claim-shadow-runtime-rc0",
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=_hex("Women had a higher rate than Men."),
    )
    return AuditContext("Women had a higher rate than Men.", proposition, world)


def _custom_receipt(
    context: AuditContext,
    passage_id: str,
    *,
    instrument_id: str,
    family: SemanticFamily,
    status: str,
) -> MeasurementReceipt:
    available = tuple(p.passage_id for p in context.evidence_world.admitted_passages)
    raw: dict[str, Any]
    if status == "CLAIMED":
        raw = {
            "status": "CLAIMED",
            "proposals": [
                {
                    "shadow": instrument_id,
                    "passage_id": passage_id,
                }
            ],
        }
    else:
        raw = {"status": status, "proposals": []}
    raw_json = json.dumps(raw, sort_keys=True, separators=(",", ":"))
    material = {
        "audit_context_sha256": context.context_sha256,
        "semantic_family": family.value,
        "instrument_id": instrument_id,
        "instrument_version": "shadow-rc0",
        "available_passage_ids": list(available),
        "consumed_passage_ids": [passage_id],
        "raw_measurement": raw,
        "diagnostics": {},
    }
    return MeasurementReceipt(
        receipt_id=stable_id("measurement", material),
        audit_context_sha256=context.context_sha256,
        semantic_family=family,
        instrument_id=instrument_id,
        instrument_version="shadow-rc0",
        available_passage_ids=available,
        consumed_passage_ids=(passage_id,),
        raw_measurement_json=raw_json,
    )


def _primary_authority_measurement_ids(result) -> tuple[str, ...]:
    return tuple(
        trace.authority.atom.measurement_receipt_id
        for trace in result.traces
        if trace.authority is not None
    )


def _relation_ids(result) -> tuple[str, ...]:
    return tuple(
        trace.relation.relation_id
        for trace in result.traces
        if trace.relation is not None
    )


def test_no_shadow_observed_run_is_exactly_equivalent_to_audit() -> None:
    context = _context()
    baseline = audit(context)

    observed = audit_observed(context)

    assert observed.audit_result == baseline
    assert observed.shadow_failures == ()
    primary_receipts = tuple(
        trace.measurement for trace in baseline.traces if trace.measurement is not None
    )
    assert set(observed.measurement_ledger.receipts) == set(primary_receipts)


def test_foreign_family_shadow_is_collected_without_changing_primary_semantics() -> None:
    context = _context()
    baseline = audit(context)
    shadow = ShadowMeasurementInstrument(
        "event-order-shadow",
        measure_direct_event_order,
    )

    observed = audit_observed(context, shadow_instruments=(shadow,))

    assert observed.audit_result == baseline
    assert observed.shadow_failures == ()
    assert any(
        receipt.semantic_family is SemanticFamily.DIRECT_EVENT_ORDER
        for receipt in observed.measurement_ledger.receipts
    )
    shadow_ids = {
        receipt.receipt_id
        for receipt in observed.measurement_ledger.receipts
        if receipt.semantic_family is SemanticFamily.DIRECT_EVENT_ORDER
    }
    assert shadow_ids
    assert shadow_ids.isdisjoint(_primary_authority_measurement_ids(observed.audit_result))


def test_shadow_order_cannot_change_result_or_canonical_ledger_identity() -> None:
    context = _context()

    def shadow_a(ctx: AuditContext, passage_id: str) -> MeasurementReceipt:
        return _custom_receipt(
            ctx,
            passage_id,
            instrument_id="shadow-a",
            family=SemanticFamily.DIRECT_EVENT_ORDER,
            status="NOT_APPLICABLE",
        )

    def shadow_b(ctx: AuditContext, passage_id: str) -> MeasurementReceipt:
        return _custom_receipt(
            ctx,
            passage_id,
            instrument_id="shadow-b",
            family=SemanticFamily.DIRECT_EVENT_ORDER,
            status="UNRESOLVED",
        )

    a = ShadowMeasurementInstrument("shadow-a", shadow_a)
    b = ShadowMeasurementInstrument("shadow-b", shadow_b)

    first = audit_observed(context, shadow_instruments=(a, b))
    second = audit_observed(context, shadow_instruments=(b, a))

    assert first.audit_result == second.audit_result == audit(context)
    assert first.measurement_ledger == second.measurement_ledger
    assert first.shadow_failures == second.shadow_failures == ()


def test_tampered_shadow_receipt_is_quarantined_without_changing_result() -> None:
    context = _context()
    baseline = audit(context)

    def tampered(ctx: AuditContext, passage_id: str) -> MeasurementReceipt:
        valid = _custom_receipt(
            ctx,
            passage_id,
            instrument_id="tampered-shadow",
            family=SemanticFamily.DIRECT_EVENT_ORDER,
            status="CLAIMED",
        )
        return replace(valid, receipt_id="sha256:tampered")

    observed = audit_observed(
        context,
        shadow_instruments=(ShadowMeasurementInstrument("tampered-shadow", tampered),),
    )

    assert observed.audit_result == baseline
    assert len(observed.shadow_failures) == len(context.evidence_world.admitted_passages)
    assert all(f.instrument_id == "tampered-shadow" for f in observed.shadow_failures)
    assert all(
        "measurement receipt identity mismatch" in f.detail
        for f in observed.shadow_failures
    )
    assert all(
        r.instrument_id != "tampered-shadow"
        for r in observed.measurement_ledger.receipts
    )


def test_raising_shadow_is_quarantined_without_changing_result() -> None:
    context = _context()
    baseline = audit(context)

    def raising(_ctx: AuditContext, passage_id: str) -> MeasurementReceipt:
        raise RuntimeError(f"shadow exploded at {passage_id}")

    observed = audit_observed(
        context,
        shadow_instruments=(ShadowMeasurementInstrument("raising-shadow", raising),),
    )

    assert observed.audit_result == baseline
    assert len(observed.shadow_failures) == len(context.evidence_world.admitted_passages)
    assert all(f.instrument_id == "raising-shadow" for f in observed.shadow_failures)
    assert all("RuntimeError" in f.detail for f in observed.shadow_failures)


def test_same_family_unqualified_shadow_cannot_replace_primary_warrant_input() -> None:
    context = _context()
    baseline = audit(context)

    def same_family_shadow(ctx: AuditContext, passage_id: str) -> MeasurementReceipt:
        return _custom_receipt(
            ctx,
            passage_id,
            instrument_id="unqualified-strict-shadow",
            family=SemanticFamily.STRICT_COMPARISON,
            status="CLAIMED",
        )

    observed = audit_observed(
        context,
        shadow_instruments=(
            ShadowMeasurementInstrument("unqualified-strict-shadow", same_family_shadow),
        ),
    )

    assert observed.audit_result == baseline
    shadow_ids = {
        r.receipt_id
        for r in observed.measurement_ledger.receipts
        if r.instrument_id == "unqualified-strict-shadow"
    }
    assert shadow_ids
    assert shadow_ids.isdisjoint(_primary_authority_measurement_ids(observed.audit_result))
    assert _primary_authority_measurement_ids(
        observed.audit_result
    ) == _primary_authority_measurement_ids(baseline)
    assert _relation_ids(observed.audit_result) == _relation_ids(baseline)


def test_shadow_measurement_status_cannot_change_verdict() -> None:
    context = _context()
    baseline = audit(context)

    def instrument(status: str):
        def measure(ctx: AuditContext, passage_id: str) -> MeasurementReceipt:
            return _custom_receipt(
                ctx,
                passage_id,
                instrument_id=f"status-{status.casefold()}",
                family=SemanticFamily.DIRECT_EVENT_ORDER,
                status=status,
            )

        return ShadowMeasurementInstrument(f"status-{status.casefold()}", measure)

    observed = audit_observed(
        context,
        shadow_instruments=(
            instrument("CLAIMED"),
            instrument("UNRESOLVED"),
            instrument("NOT_APPLICABLE"),
        ),
    )

    assert observed.audit_result == baseline
    assert observed.audit_result.conclusion == baseline.conclusion
    assert observed.audit_result.failure_code == baseline.failure_code
    assert observed.audit_result.deciding_passage_ids == baseline.deciding_passage_ids
    assert observed.audit_result.non_deciding_passage_ids == baseline.non_deciding_passage_ids


def test_no_shadow_receipt_identity_enters_primary_authority_or_relation() -> None:
    context = _context()

    def shadow(ctx: AuditContext, passage_id: str) -> MeasurementReceipt:
        return _custom_receipt(
            ctx,
            passage_id,
            instrument_id="identity-shadow",
            family=SemanticFamily.STRICT_COMPARISON,
            status="CLAIMED",
        )

    observed = audit_observed(
        context,
        shadow_instruments=(ShadowMeasurementInstrument("identity-shadow", shadow),),
    )
    shadow_ids = {
        r.receipt_id
        for r in observed.measurement_ledger.receipts
        if r.instrument_id == "identity-shadow"
    }

    assert shadow_ids
    assert shadow_ids.isdisjoint(_primary_authority_measurement_ids(observed.audit_result))
    assert all(
        trace.authority is None
        or trace.authority.atom.measurement_receipt_id not in shadow_ids
        for trace in observed.audit_result.traces
    )


def test_repeated_observed_execution_is_deterministic() -> None:
    context = _context()
    shadow = ShadowMeasurementInstrument("event-order-shadow", measure_direct_event_order)

    first = audit_observed(context, shadow_instruments=(shadow,))
    second = audit_observed(context, shadow_instruments=(shadow,))

    assert first == second
    assert first.audit_result == audit(context)
