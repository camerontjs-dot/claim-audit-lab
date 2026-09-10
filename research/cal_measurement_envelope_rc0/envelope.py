"""Common information-preserving envelope for CAL research measurements.

Research-only. This module does not decide proposition verdicts and does not
grant semantic authority. A MeasurementReceipt is an observation record bound
to an immutable AuditContext; authority/warrant is a separate downstream step.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Callable, Iterable, Mapping

AUDIT_CONTEXT_SCHEMA = "cal.audit-context.rc0.v1"
MEASUREMENT_RECEIPT_SCHEMA = "cal.measurement-receipt.rc0.v1"
MEASUREMENT_LEDGER_SCHEMA = "cal.measurement-ledger.rc0.v1"
AUTHORITY_NOT_EVALUATED = "NOT_EVALUATED"
_ALLOWED_MEASUREMENT_STATUS = frozenset({"CLAIMED", "UNRESOLVED", "NOT_APPLICABLE", "ERROR"})
_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
MeasureFn = Callable[[str], Mapping[str, Any]]


class EnvelopeRefusal(ValueError):
    """Fail-closed envelope refusal with a typed code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_json_text(value: Any) -> str:
    return canonical_json_bytes(value).decode("utf-8")


def sha256_receipt(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _canonical_object(value: Mapping[str, Any], *, field: str) -> str:
    if not isinstance(value, Mapping):
        raise EnvelopeRefusal("INVALID_JSON_OBJECT", f"{field} must be an object")
    try:
        text = canonical_json_text(dict(value))
    except (TypeError, ValueError) as exc:
        raise EnvelopeRefusal("INVALID_JSON_OBJECT", f"{field} is not canonical JSON data") from exc
    decoded = json.loads(text)
    if not isinstance(decoded, dict):
        raise EnvelopeRefusal("INVALID_JSON_OBJECT", f"{field} must canonicalize to an object")
    return text


def _decode_object(text: str, *, field: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EnvelopeRefusal("INVALID_JSON_OBJECT", f"{field} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise EnvelopeRefusal("INVALID_JSON_OBJECT", f"{field} must be an object")
    return value


def _require_nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EnvelopeRefusal("INVALID_FIELD", f"{field} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class AdmittedPassage:
    source_id: str
    passage_id: str
    passage_sha256: str
    passage_text: str

    def __post_init__(self) -> None:
        _require_nonempty(self.source_id, "source_id")
        _require_nonempty(self.passage_id, "passage_id")
        if not _SHA256_RE.fullmatch(self.passage_sha256):
            raise EnvelopeRefusal("INVALID_PASSAGE_HASH", self.passage_id)
        if not isinstance(self.passage_text, str):
            raise EnvelopeRefusal("INVALID_PASSAGE_TEXT", self.passage_id)

    def payload(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "passage_id": self.passage_id,
            "passage_sha256": self.passage_sha256,
            "passage_text": self.passage_text,
        }


@dataclass(frozen=True, slots=True)
class AuditContext:
    audit_id: str
    original_claim_id: str
    original_claim_text: str
    proposition_id: str
    proposition_payload_json: str
    decomposition_path: tuple[str, ...]
    contract_b_version: str
    bundle_id: str
    bundle_hash: str
    admitted_passages: tuple[AdmittedPassage, ...]

    @classmethod
    def create(
        cls,
        *,
        audit_id: str,
        original_claim_id: str,
        original_claim_text: str,
        proposition_id: str,
        proposition_payload: Mapping[str, Any],
        decomposition_path: Iterable[str] = (),
        contract_b_version: str,
        bundle_id: str,
        bundle_hash: str,
        admitted_passages: Iterable[AdmittedPassage],
    ) -> "AuditContext":
        return cls(
            audit_id=audit_id,
            original_claim_id=original_claim_id,
            original_claim_text=original_claim_text,
            proposition_id=proposition_id,
            proposition_payload_json=_canonical_object(
                proposition_payload, field="proposition_payload"
            ),
            decomposition_path=tuple(decomposition_path),
            contract_b_version=contract_b_version,
            bundle_id=bundle_id,
            bundle_hash=bundle_hash,
            admitted_passages=tuple(
                sorted(admitted_passages, key=lambda item: item.passage_id)
            ),
        )

    def __post_init__(self) -> None:
        _require_nonempty(self.audit_id, "audit_id")
        _require_nonempty(self.original_claim_id, "original_claim_id")
        _require_nonempty(self.original_claim_text, "original_claim_text")
        _require_nonempty(self.proposition_id, "proposition_id")
        _decode_object(self.proposition_payload_json, field="proposition_payload_json")
        _require_nonempty(self.contract_b_version, "contract_b_version")
        _require_nonempty(self.bundle_id, "bundle_id")
        if not _SHA256_RE.fullmatch(self.bundle_hash):
            raise EnvelopeRefusal("INVALID_BUNDLE_HASH", self.bundle_hash)
        if any(not isinstance(item, str) or not item for item in self.decomposition_path):
            raise EnvelopeRefusal("INVALID_DECOMPOSITION_PATH", "path entries must be non-empty")
        ids = tuple(item.passage_id for item in self.admitted_passages)
        if len(ids) != len(set(ids)):
            raise EnvelopeRefusal("DUPLICATE_ADMITTED_PASSAGE", "passage IDs must be unique")
        if ids != tuple(sorted(ids)):
            raise EnvelopeRefusal("NONCANONICAL_ADMITTED_ORDER", "passages must be sorted")

    @property
    def proposition_payload(self) -> dict[str, Any]:
        return _decode_object(self.proposition_payload_json, field="proposition_payload_json")

    @property
    def admitted_passage_ids(self) -> tuple[str, ...]:
        return tuple(item.passage_id for item in self.admitted_passages)

    def passage(self, passage_id: str) -> AdmittedPassage:
        for item in self.admitted_passages:
            if item.passage_id == passage_id:
                return item
        raise EnvelopeRefusal("PASSAGE_NOT_ADMITTED", passage_id)

    def payload(self) -> dict[str, Any]:
        return {
            "schema": AUDIT_CONTEXT_SCHEMA,
            "audit_id": self.audit_id,
            "original_claim": {
                "claim_id": self.original_claim_id,
                "claim_text": self.original_claim_text,
            },
            "proposition": {
                "proposition_id": self.proposition_id,
                "payload": self.proposition_payload,
                "decomposition_path": list(self.decomposition_path),
            },
            "contract_b": {
                "contract_version": self.contract_b_version,
                "bundle_id": self.bundle_id,
                "bundle_hash": self.bundle_hash,
            },
            "admitted_passages": [item.payload() for item in self.admitted_passages],
        }

    @property
    def context_sha256(self) -> str:
        return sha256_receipt(canonical_json_bytes(self.payload()))


@dataclass(frozen=True, slots=True)
class ConsumedSpan:
    passage_id: str
    start: int
    end: int
    label: str = "measurement_span"

    def __post_init__(self) -> None:
        _require_nonempty(self.passage_id, "span.passage_id")
        _require_nonempty(self.label, "span.label")
        if (
            not isinstance(self.start, int)
            or isinstance(self.start, bool)
            or not isinstance(self.end, int)
            or isinstance(self.end, bool)
            or self.start < 0
            or self.end < self.start
        ):
            raise EnvelopeRefusal("INVALID_SPAN", f"{self.passage_id}:{self.start}:{self.end}")

    def payload(self) -> dict[str, Any]:
        return {
            "passage_id": self.passage_id,
            "start": self.start,
            "end": self.end,
            "label": self.label,
        }


@dataclass(frozen=True, slots=True)
class MeasurementReceipt:
    receipt_id: str
    audit_context_sha256: str
    proposition_id: str
    instrument_id: str
    instrument_version: str
    semantic_family: str
    measurement_status: str
    available_passage_ids: tuple[str, ...]
    consumed_passage_ids: tuple[str, ...]
    consumed_spans: tuple[ConsumedSpan, ...]
    raw_measurement_json: str
    authority_state: str = AUTHORITY_NOT_EVALUATED

    @classmethod
    def create(
        cls,
        *,
        context: AuditContext,
        instrument_id: str,
        instrument_version: str,
        semantic_family: str,
        measurement_status: str,
        consumed_passage_ids: Iterable[str],
        raw_measurement: Mapping[str, Any],
        consumed_spans: Iterable[ConsumedSpan] = (),
    ) -> "MeasurementReceipt":
        raw_json = _canonical_object(raw_measurement, field="raw_measurement")
        provisional = cls(
            receipt_id="sha256:" + ("0" * 64),
            audit_context_sha256=context.context_sha256,
            proposition_id=context.proposition_id,
            instrument_id=instrument_id,
            instrument_version=instrument_version,
            semantic_family=semantic_family,
            measurement_status=measurement_status,
            available_passage_ids=context.admitted_passage_ids,
            consumed_passage_ids=tuple(sorted(set(consumed_passage_ids))),
            consumed_spans=tuple(
                sorted(
                    consumed_spans,
                    key=lambda item: (item.passage_id, item.start, item.end, item.label),
                )
            ),
            raw_measurement_json=raw_json,
        )
        receipt_id = sha256_receipt(canonical_json_bytes(provisional.body_payload()))
        receipt = cls(
            receipt_id=receipt_id,
            audit_context_sha256=provisional.audit_context_sha256,
            proposition_id=provisional.proposition_id,
            instrument_id=provisional.instrument_id,
            instrument_version=provisional.instrument_version,
            semantic_family=provisional.semantic_family,
            measurement_status=provisional.measurement_status,
            available_passage_ids=provisional.available_passage_ids,
            consumed_passage_ids=provisional.consumed_passage_ids,
            consumed_spans=provisional.consumed_spans,
            raw_measurement_json=provisional.raw_measurement_json,
        )
        verify_measurement_receipt(context=context, receipt=receipt)
        return receipt

    def __post_init__(self) -> None:
        if not _SHA256_RE.fullmatch(self.receipt_id):
            raise EnvelopeRefusal("INVALID_RECEIPT_ID", self.receipt_id)
        if not _SHA256_RE.fullmatch(self.audit_context_sha256):
            raise EnvelopeRefusal("INVALID_CONTEXT_BINDING", self.audit_context_sha256)
        _require_nonempty(self.proposition_id, "proposition_id")
        _require_nonempty(self.instrument_id, "instrument_id")
        _require_nonempty(self.instrument_version, "instrument_version")
        _require_nonempty(self.semantic_family, "semantic_family")
        if self.measurement_status not in _ALLOWED_MEASUREMENT_STATUS:
            raise EnvelopeRefusal("INVALID_MEASUREMENT_STATUS", self.measurement_status)
        _decode_object(self.raw_measurement_json, field="raw_measurement_json")
        if self.authority_state != AUTHORITY_NOT_EVALUATED:
            raise EnvelopeRefusal(
                "AUTHORITY_LAUNDERING",
                "measurement receipts never grant semantic authority",
            )
        if self.available_passage_ids != tuple(sorted(set(self.available_passage_ids))):
            raise EnvelopeRefusal("NONCANONICAL_AVAILABLE_SET", "available passage IDs")
        if self.consumed_passage_ids != tuple(sorted(set(self.consumed_passage_ids))):
            raise EnvelopeRefusal("NONCANONICAL_CONSUMED_SET", "consumed passage IDs")

    @property
    def raw_measurement(self) -> dict[str, Any]:
        return _decode_object(self.raw_measurement_json, field="raw_measurement_json")

    def body_payload(self) -> dict[str, Any]:
        return {
            "schema": MEASUREMENT_RECEIPT_SCHEMA,
            "audit_context_sha256": self.audit_context_sha256,
            "proposition_id": self.proposition_id,
            "instrument": {
                "instrument_id": self.instrument_id,
                "instrument_version": self.instrument_version,
                "semantic_family": self.semantic_family,
            },
            "measurement_status": self.measurement_status,
            "available_passage_ids": list(self.available_passage_ids),
            "consumed_passage_ids": list(self.consumed_passage_ids),
            "consumed_spans": [item.payload() for item in self.consumed_spans],
            "raw_measurement": self.raw_measurement,
            "authority_state": self.authority_state,
        }

    def payload(self) -> dict[str, Any]:
        return {"receipt_id": self.receipt_id, **self.body_payload()}


def verify_measurement_receipt(
    *, context: AuditContext, receipt: MeasurementReceipt
) -> None:
    if receipt.audit_context_sha256 != context.context_sha256:
        raise EnvelopeRefusal("CONTEXT_BINDING_MISMATCH", receipt.receipt_id)
    if receipt.proposition_id != context.proposition_id:
        raise EnvelopeRefusal("PROPOSITION_BINDING_MISMATCH", receipt.receipt_id)
    if receipt.available_passage_ids != context.admitted_passage_ids:
        raise EnvelopeRefusal("AVAILABLE_CONTEXT_MISMATCH", receipt.receipt_id)
    admitted = set(context.admitted_passage_ids)
    if not set(receipt.consumed_passage_ids).issubset(admitted):
        raise EnvelopeRefusal("CONSUMED_CONTEXT_OUTSIDE_ADMISSION", receipt.receipt_id)
    for span in receipt.consumed_spans:
        if span.passage_id not in receipt.consumed_passage_ids:
            raise EnvelopeRefusal("SPAN_OUTSIDE_CONSUMED_CONTEXT", span.passage_id)
        passage = context.passage(span.passage_id)
        if span.end > len(passage.passage_text):
            raise EnvelopeRefusal("SPAN_OUT_OF_RANGE", span.passage_id)
    expected = sha256_receipt(canonical_json_bytes(receipt.body_payload()))
    if receipt.receipt_id != expected:
        raise EnvelopeRefusal("RECEIPT_ID_MISMATCH", receipt.receipt_id)


def proposal_spans(
    *, passage_id: str, raw_measurement: Mapping[str, Any]
) -> tuple[ConsumedSpan, ...]:
    """Capture proposal cue spans when an instrument exposes them."""
    proposals = raw_measurement.get("proposals")
    if not isinstance(proposals, list):
        return ()
    rows: list[ConsumedSpan] = []
    for index, proposal in enumerate(proposals):
        if not isinstance(proposal, Mapping):
            continue
        span = proposal.get("span")
        if (
            isinstance(span, list)
            and len(span) == 2
            and all(isinstance(item, int) and not isinstance(item, bool) for item in span)
        ):
            rows.append(
                ConsumedSpan(
                    passage_id=passage_id,
                    start=span[0],
                    end=span[1],
                    label=f"proposal[{index}].span",
                )
            )
    return tuple(rows)


def measure_passage(
    *,
    context: AuditContext,
    passage_id: str,
    instrument_id: str,
    instrument_version: str,
    semantic_family: str,
    measure_fn: MeasureFn,
) -> MeasurementReceipt:
    """Run a passage-scoped measurement while binding it to full audit context."""
    passage = context.passage(passage_id)
    try:
        raw = dict(measure_fn(passage.passage_text))
    except Exception as exc:
        raw = {
            "status": "ERROR",
            "proposals": [],
            "residue": [f"{type(exc).__name__}:{exc}"],
            "version": instrument_version,
        }
    status = raw.get("status")
    if status not in _ALLOWED_MEASUREMENT_STATUS:
        raise EnvelopeRefusal(
            "INVALID_INSTRUMENT_OUTPUT",
            f"{instrument_id} emitted unsupported status {status!r}",
        )
    return MeasurementReceipt.create(
        context=context,
        instrument_id=instrument_id,
        instrument_version=instrument_version,
        semantic_family=semantic_family,
        measurement_status=str(status),
        consumed_passage_ids=(passage_id,),
        raw_measurement=raw,
        consumed_spans=proposal_spans(passage_id=passage_id, raw_measurement=raw),
    )


@dataclass(frozen=True, slots=True)
class MeasurementLedger:
    context: AuditContext
    receipts: tuple[MeasurementReceipt, ...] = ()

    def __post_init__(self) -> None:
        ordered = tuple(sorted(self.receipts, key=lambda item: item.receipt_id))
        if ordered != self.receipts:
            raise EnvelopeRefusal("NONCANONICAL_LEDGER_ORDER", "receipts must be sorted")
        ids = tuple(item.receipt_id for item in self.receipts)
        if len(ids) != len(set(ids)):
            raise EnvelopeRefusal("DUPLICATE_MEASUREMENT_RECEIPT", "receipt IDs must be unique")
        for receipt in self.receipts:
            verify_measurement_receipt(context=self.context, receipt=receipt)

    def append(self, receipt: MeasurementReceipt) -> "MeasurementLedger":
        verify_measurement_receipt(context=self.context, receipt=receipt)
        if receipt.receipt_id in {item.receipt_id for item in self.receipts}:
            return self
        return MeasurementLedger(
            context=self.context,
            receipts=tuple(sorted((*self.receipts, receipt), key=lambda item: item.receipt_id)),
        )

    def extend(self, receipts: Iterable[MeasurementReceipt]) -> "MeasurementLedger":
        ledger = self
        for receipt in receipts:
            ledger = ledger.append(receipt)
        return ledger

    def payload(self) -> dict[str, Any]:
        return {
            "schema": MEASUREMENT_LEDGER_SCHEMA,
            "audit_context": self.context.payload(),
            "audit_context_sha256": self.context.context_sha256,
            "measurement_receipts": [item.payload() for item in self.receipts],
        }

    @property
    def ledger_sha256(self) -> str:
        return sha256_receipt(canonical_json_bytes(self.payload()))


__all__ = [
    "AUDIT_CONTEXT_SCHEMA",
    "AUTHORITY_NOT_EVALUATED",
    "MEASUREMENT_LEDGER_SCHEMA",
    "MEASUREMENT_RECEIPT_SCHEMA",
    "AdmittedPassage",
    "AuditContext",
    "ConsumedSpan",
    "EnvelopeRefusal",
    "MeasurementLedger",
    "MeasurementReceipt",
    "canonical_json_bytes",
    "measure_passage",
    "proposal_spans",
    "sha256_receipt",
    "verify_measurement_receipt",
]
