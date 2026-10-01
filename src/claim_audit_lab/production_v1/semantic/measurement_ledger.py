from __future__ import annotations

from dataclasses import dataclass

from .measurements import MeasurementReceipt, verify_measurement_receipt
from .models import AuditContext, stable_id


class MeasurementLedgerRefusal(ValueError):
    """Raised when a measurement cannot enter or verify against the ledger."""


def _available_passage_ids(context: AuditContext) -> tuple[str, ...]:
    return tuple(passage.passage_id for passage in context.evidence_world.admitted_passages)


def _ledger_material(
    audit_context_sha256: str,
    available_passage_ids: tuple[str, ...],
    receipts: tuple[MeasurementReceipt, ...],
) -> dict[str, object]:
    return {
        "audit_context_sha256": audit_context_sha256,
        "available_passage_ids": list(available_passage_ids),
        "measurement_receipt_ids": [receipt.receipt_id for receipt in receipts],
    }


def _canonical_receipts(
    receipts: tuple[MeasurementReceipt, ...],
) -> tuple[MeasurementReceipt, ...]:
    return tuple(sorted(receipts, key=lambda receipt: receipt.receipt_id))


@dataclass(frozen=True, slots=True)
class MeasurementLedger:
    """Immutable observation ledger; it carries no semantic authority or verdict state."""

    ledger_id: str
    audit_context_sha256: str
    available_passage_ids: tuple[str, ...]
    receipts: tuple[MeasurementReceipt, ...]

    @classmethod
    def empty(cls, context: AuditContext) -> MeasurementLedger:
        context.verify()
        available = _available_passage_ids(context)
        receipts: tuple[MeasurementReceipt, ...] = ()
        material = _ledger_material(context.context_sha256, available, receipts)
        return cls(
            ledger_id=stable_id("measurement-ledger", material),
            audit_context_sha256=context.context_sha256,
            available_passage_ids=available,
            receipts=receipts,
        )

    def append(
        self,
        context: AuditContext,
        receipt: MeasurementReceipt,
    ) -> MeasurementLedger:
        self.verify(context)
        if receipt.audit_context_sha256 != context.context_sha256:
            raise MeasurementLedgerRefusal("measurement audit-context mismatch")
        try:
            verify_measurement_receipt(context, receipt)
        except ValueError as exc:
            raise MeasurementLedgerRefusal(str(exc)) from exc
        if any(existing.receipt_id == receipt.receipt_id for existing in self.receipts):
            raise MeasurementLedgerRefusal(f"duplicate measurement receipt: {receipt.receipt_id}")
        receipts = _canonical_receipts((*self.receipts, receipt))
        material = _ledger_material(
            self.audit_context_sha256,
            self.available_passage_ids,
            receipts,
        )
        return MeasurementLedger(
            ledger_id=stable_id("measurement-ledger", material),
            audit_context_sha256=self.audit_context_sha256,
            available_passage_ids=self.available_passage_ids,
            receipts=receipts,
        )

    def verify(self, context: AuditContext) -> None:
        context.verify()
        if self.audit_context_sha256 != context.context_sha256:
            raise MeasurementLedgerRefusal("measurement-ledger audit-context mismatch")
        expected_available = _available_passage_ids(context)
        if self.available_passage_ids != expected_available:
            raise MeasurementLedgerRefusal("measurement-ledger evidence aperture mismatch")
        if self.receipts != _canonical_receipts(self.receipts):
            raise MeasurementLedgerRefusal("measurement-ledger receipt order is not canonical")
        receipt_ids = tuple(receipt.receipt_id for receipt in self.receipts)
        if len(receipt_ids) != len(set(receipt_ids)):
            raise MeasurementLedgerRefusal("duplicate measurement receipt identity")
        for receipt in self.receipts:
            try:
                verify_measurement_receipt(context, receipt)
            except ValueError as exc:
                raise MeasurementLedgerRefusal(str(exc)) from exc
        material = _ledger_material(
            self.audit_context_sha256,
            self.available_passage_ids,
            self.receipts,
        )
        if self.ledger_id != stable_id("measurement-ledger", material):
            raise MeasurementLedgerRefusal("measurement-ledger identity mismatch")


__all__ = ["MeasurementLedger", "MeasurementLedgerRefusal"]
