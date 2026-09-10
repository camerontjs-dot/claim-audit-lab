"""Decisive evaluator for the preregistered CAL Measurement Envelope RC0 candidate."""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from envelope import (
    AdmittedPassage,
    AuditContext,
    AUTHORITY_NOT_EVALUATED,
    ConsumedSpan,
    EnvelopeRefusal,
    MeasurementLedger,
    MeasurementReceipt,
    canonical_json_bytes,
    measure_passage,
    verify_measurement_receipt,
)

STRICT_HEAD = "0ecdedc5cea970485a635508255f3670ab231c33"
STRICT_BLOB = "33820f55e2a87c4de6336fca6b5e5b93a2bccde3"
STRICT_PATH = "research/comparative_relation_measurement_rc7fb1/comparator.py"
EVENT_HEAD = "e8d33913db66ad21027dffdf731d50f7a0977c8f"
EVENT_BLOB = "3e29b0e2ec5d9ba2d873d1584e76635147e421aa"
EVENT_PATH = "research/event_ordering_measurement_rc7fc/event_order.py"
SCHEMA = "cal-measurement-envelope-rc0-evaluation-v1"


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _require_identity(root: Path, *, head: str, path: str, blob: str) -> None:
    observed_head = _git(root, "rev-parse", "HEAD")
    if observed_head != head:
        raise RuntimeError(f"dependency head mismatch: {observed_head} != {head}")
    observed_blob = _git(root, "hash-object", path)
    if observed_blob != blob:
        raise RuntimeError(f"dependency blob mismatch: {observed_blob} != {blob}")


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _context(
    *,
    original_claim_text: str | None = None,
    proposition_payload: dict[str, Any] | None = None,
    bundle_hash: str | None = None,
    passages: tuple[AdmittedPassage, ...] | None = None,
) -> AuditContext:
    p1 = "Alpha exceeded Beta by 4 units."
    p2 = "Alice reviewed dossier before Bob archived dossier."
    p3 = "The evidence packet also contains a retained context note for reconstruction."
    admitted = passages or (
        AdmittedPassage("SRC-1", "P1", _hash(p1), p1),
        AdmittedPassage("SRC-2", "P2", _hash(p2), p2),
        AdmittedPassage("SRC-3", "P3", _hash(p3), p3),
    )
    claim = original_claim_text or (
        "Alpha exceeded Beta by 4 units, and Alice reviewed dossier before Bob archived dossier."
    )
    payload = proposition_payload or {
        "kind": "compound_research_control",
        "text": claim,
        "measurement_targets": ["strict_comparison", "event_ordering"],
    }
    return AuditContext.create(
        audit_id="CAL-MEASUREMENT-ENVELOPE-RC0-001",
        original_claim_id="ROOT-001",
        original_claim_text=claim,
        proposition_id="PROP-001",
        proposition_payload=payload,
        decomposition_path=("ROOT-001", "PROP-001"),
        contract_b_version="1.2.0",
        bundle_id="11111111-2222-3333-4444-555555555555",
        bundle_hash=bundle_hash or ("sha256:" + "a" * 64),
        admitted_passages=admitted,
    )


def _expect_refusal(code: str, fn: Any) -> dict[str, Any]:
    try:
        fn()
    except EnvelopeRefusal as exc:
        if exc.code != code:
            raise AssertionError(f"expected {code}, got {exc.code}: {exc.detail}") from exc
        return {"pass": True, "code": exc.code, "detail": exc.detail}
    raise AssertionError(f"expected refusal {code}")


def execute(*, strict_root: Path, event_root: Path) -> dict[str, Any]:
    _require_identity(strict_root, head=STRICT_HEAD, path=STRICT_PATH, blob=STRICT_BLOB)
    _require_identity(event_root, head=EVENT_HEAD, path=EVENT_PATH, blob=EVENT_BLOB)
    strict = _load_module("measurement_envelope_strict", strict_root / STRICT_PATH)
    event = _load_module("measurement_envelope_event", event_root / EVENT_PATH)

    context = _context()
    strict_receipt = measure_passage(
        context=context,
        passage_id="P1",
        instrument_id="rc7fb1-comparator",
        instrument_version=str(strict.VERSION),
        semantic_family="strict_comparison",
        measure_fn=strict.measure,
    )
    event_receipt = measure_passage(
        context=context,
        passage_id="P2",
        instrument_id="rc7fc-event-order",
        instrument_version=str(event.VERSION),
        semantic_family="event_ordering",
        measure_fn=event.measure,
    )

    strict_expected = strict.measure(context.passage("P1").passage_text)
    event_expected = event.measure(context.passage("P2").passage_text)
    assert strict_expected["status"] == "CLAIMED"
    assert event_expected["status"] == "CLAIMED"
    assert strict_receipt.raw_measurement == strict_expected
    assert event_receipt.raw_measurement == event_expected
    assert strict_receipt.audit_context_sha256 == context.context_sha256
    assert event_receipt.audit_context_sha256 == context.context_sha256
    assert strict_receipt.available_passage_ids == ("P1", "P2", "P3")
    assert event_receipt.available_passage_ids == ("P1", "P2", "P3")
    assert strict_receipt.consumed_passage_ids == ("P1",)
    assert event_receipt.consumed_passage_ids == ("P2",)
    assert strict_receipt.authority_state == AUTHORITY_NOT_EVALUATED
    assert event_receipt.authority_state == AUTHORITY_NOT_EVALUATED

    deterministic_strict = measure_passage(
        context=context,
        passage_id="P1",
        instrument_id="rc7fb1-comparator",
        instrument_version=str(strict.VERSION),
        semantic_family="strict_comparison",
        measure_fn=strict.measure,
    )
    assert deterministic_strict == strict_receipt

    ledger_ab = MeasurementLedger(context).extend((strict_receipt, event_receipt))
    ledger_ba = MeasurementLedger(context).extend((event_receipt, strict_receipt))
    assert ledger_ab.ledger_sha256 == ledger_ba.ledger_sha256
    assert ledger_ab.payload() == ledger_ba.payload()
    assert ledger_ab.context.passage("P3").passage_text == context.passage("P3").passage_text

    changed_claim = _context(original_claim_text=context.original_claim_text + " Changed.")
    claim_mutation = _expect_refusal(
        "CONTEXT_BINDING_MISMATCH",
        lambda: verify_measurement_receipt(context=changed_claim, receipt=strict_receipt),
    )

    changed_prop = _context(
        proposition_payload={
            "kind": "compound_research_control",
            "text": context.original_claim_text,
            "measurement_targets": ["event_ordering"],
        }
    )
    proposition_mutation = _expect_refusal(
        "CONTEXT_BINDING_MISMATCH",
        lambda: verify_measurement_receipt(context=changed_prop, receipt=strict_receipt),
    )

    changed_bundle = _context(bundle_hash="sha256:" + "b" * 64)
    bundle_mutation = _expect_refusal(
        "CONTEXT_BINDING_MISMATCH",
        lambda: verify_measurement_receipt(context=changed_bundle, receipt=strict_receipt),
    )

    reduced_passages = tuple(item for item in context.admitted_passages if item.passage_id != "P3")
    reduced_context = _context(passages=reduced_passages)
    admission_mutation = _expect_refusal(
        "CONTEXT_BINDING_MISMATCH",
        lambda: verify_measurement_receipt(context=reduced_context, receipt=strict_receipt),
    )

    p1 = context.passage("P1")
    changed_p1 = AdmittedPassage(
        p1.source_id,
        p1.passage_id,
        p1.passage_sha256,
        p1.passage_text + " altered",
    )
    changed_text_context = _context(
        passages=(changed_p1, context.passage("P2"), context.passage("P3"))
    )
    passage_text_mutation = _expect_refusal(
        "CONTEXT_BINDING_MISMATCH",
        lambda: verify_measurement_receipt(context=changed_text_context, receipt=strict_receipt),
    )

    foreign_consumption = replace(strict_receipt, consumed_passage_ids=("FOREIGN",))
    foreign_consumption_result = _expect_refusal(
        "CONSUMED_CONTEXT_OUTSIDE_ADMISSION",
        lambda: verify_measurement_receipt(context=context, receipt=foreign_consumption),
    )

    bad_span = replace(
        strict_receipt,
        consumed_spans=(ConsumedSpan("P1", 0, len(p1.passage_text) + 100, "bad"),),
    )
    bad_span_result = _expect_refusal(
        "SPAN_OUT_OF_RANGE",
        lambda: verify_measurement_receipt(context=context, receipt=bad_span),
    )

    missing_available = replace(strict_receipt, available_passage_ids=("P1", "P2"))
    available_context_result = _expect_refusal(
        "AVAILABLE_CONTEXT_MISMATCH",
        lambda: verify_measurement_receipt(context=context, receipt=missing_available),
    )

    mutated_raw = dict(strict_receipt.raw_measurement)
    mutated_raw["residue"] = ["tampered-after-issuance"]
    proposal_tamper = replace(
        strict_receipt,
        raw_measurement_json=json.dumps(mutated_raw, sort_keys=True, separators=(",", ":")),
    )
    proposal_tamper_result = _expect_refusal(
        "RECEIPT_ID_MISMATCH",
        lambda: verify_measurement_receipt(context=context, receipt=proposal_tamper),
    )

    authority_laundering = _expect_refusal(
        "AUTHORITY_LAUNDERING",
        lambda: replace(event_receipt, authority_state="WARRANTED"),
    )

    strict_keys = set(strict_receipt.body_payload()) - {"raw_measurement"}
    event_keys = set(event_receipt.body_payload()) - {"raw_measurement"}
    assert strict_keys == event_keys
    forbidden_common = {
        "verdict",
        "confidence_threshold",
        "majority_vote",
        "score_aggregation",
        "decision",
    }
    assert not (forbidden_common & set(ledger_ab.payload()))
    assert not hasattr(ledger_ab, "verdict")
    assert not hasattr(ledger_ab, "decide")

    result = {
        "schema": SCHEMA,
        "research_disposition": "SUPPORTED_WITH_BOUNDS",
        "candidate": {
            "audit_context_sha256": context.context_sha256,
            "ledger_sha256": ledger_ab.ledger_sha256,
            "full_admitted_passage_ids": list(context.admitted_passage_ids),
            "non_consumed_context_recoverable": ledger_ab.context.passage("P3").payload(),
        },
        "dependency_identity": {
            "strict_comparison": {"head": STRICT_HEAD, "blob": STRICT_BLOB},
            "event_ordering": {"head": EVENT_HEAD, "blob": EVENT_BLOB},
        },
        "positive_controls": {
            "strict_comparison": strict_receipt.payload(),
            "event_ordering": event_receipt.payload(),
            "same_full_context_binding": (
                strict_receipt.audit_context_sha256
                == event_receipt.audit_context_sha256
                == context.context_sha256
            ),
            "different_consumed_context": (
                strict_receipt.consumed_passage_ids != event_receipt.consumed_passage_ids
            ),
            "deterministic_repeat": deterministic_strict.receipt_id == strict_receipt.receipt_id,
            "ledger_order_invariant": ledger_ab.ledger_sha256 == ledger_ba.ledger_sha256,
            "common_family_neutral_schema": strict_keys == event_keys,
            "event_authority_state": event_receipt.authority_state,
        },
        "falsifiers": {
            "original_claim_mutation": claim_mutation,
            "proposition_payload_mutation": proposition_mutation,
            "bundle_hash_mutation": bundle_mutation,
            "admitted_set_mutation": admission_mutation,
            "passage_text_mutation_stale_hash": passage_text_mutation,
            "foreign_consumed_passage": foreign_consumption_result,
            "out_of_range_span": bad_span_result,
            "available_context_omission": available_context_result,
            "proposal_tamper_stale_receipt_id": proposal_tamper_result,
            "authority_laundering": authority_laundering,
        },
        "interpretation": {
            "measurement_envelope_grants_authority": False,
            "event_ordering_warrant_established": False,
            "terminal_verdict_surface_present": False,
            "released_cal_v1_causal_role": False,
            "production_promotion_authorized": False,
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict-root", type=Path, required=True)
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(strict_root=args.strict_root.resolve(), event_root=args.event_root.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical_json_bytes(result) + b"\n")
    print(json.dumps({
        "research_disposition": result["research_disposition"],
        "audit_context_sha256": result["candidate"]["audit_context_sha256"],
        "ledger_sha256": result["candidate"]["ledger_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
