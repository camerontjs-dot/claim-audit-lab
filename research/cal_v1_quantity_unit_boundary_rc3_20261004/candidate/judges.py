"""Successor judges. Each function sees only the bytes it is given."""

from __future__ import annotations

import os
import re
from typing import Any

from codec import digest, parse_envelope
from views import parse_view

_BEFORE = re.compile(
    r"^(?P<left>.+?) (?:before|prior to) (?P<right>.+?)\.?$",
    re.IGNORECASE,
)
_AFTER = re.compile(r"^(?P<left>.+?) after (?P<right>.+?)\.?$", re.IGNORECASE)


def _base(process_id: str, role: str, raw: bytes) -> dict[str, Any]:
    return {
        "process_id": process_id,
        "input_sha256": digest(raw),
        "execution": "completed",
        "applicability": "not_applicable",
        "role": role,
        "conclusion": "not_applicable",
        "warrant": "qualified",
        "material_loss": False,
        "abstention_cause": None,
        "local_material_conflict": False,
        "dependence_group": {
            "quantity_relation": "quantity-text",
            "event_order": "event-order-text",
            "scope_guard": "scope-guard",
            "attribution_guard": "attribution-guard",
        }[process_id],
        "instrument_id": process_id,
        "model": None,
        "prompt_name": os.environ.get("CAL_PROMPT_NAME"),
        "worker_pid": os.getpid(),
    }


def quantity_relation(raw: bytes) -> dict[str, Any]:
    """RC3 unit/dimension binder with frozen RC2 fallback for unitless comparisons."""
    receipt = _base("quantity_relation", "relation", raw)
    envelope = parse_envelope(raw)
    from unit_binding import apply_quantity_receipt
    apply_quantity_receipt(receipt, envelope)
    return receipt


def _order(text: str) -> tuple[str, str, str] | None:
    cleaned = " ".join(text.strip().split())
    before = _BEFORE.fullmatch(cleaned)
    if before is not None:
        return ("before", before.group("left").casefold(), before.group("right").casefold())
    after = _AFTER.fullmatch(cleaned)
    if after is not None:
        return ("after", after.group("left").casefold(), after.group("right").casefold())
    return None


def event_order(raw: bytes) -> dict[str, Any]:
    receipt = _base("event_order", "relation", raw)
    envelope = parse_envelope(raw)
    claim = _order(envelope["claim"])
    if claim is None:
        receipt["abstention_cause"] = "unparsed_event_order"
        return receipt
    receipt["applicability"] = "applicable"
    receipt["claim_interpretation"] = {"order": claim[0], "left": claim[1], "right": claim[2]}
    if not envelope["evidence"]:
        receipt["conclusion"] = "unresolved"
        receipt["abstention_cause"] = "missing_evidence"
        return receipt
    opinions: list[str] = []
    for passage in envelope["evidence"]:
        evidence = _order(passage["text"])
        if evidence is None:
            continue
        same_events = {claim[1], claim[2]} == {evidence[1], evidence[2]}
        if not same_events:
            continue
        same_order = claim == evidence
        opinions.append("supports" if same_order else "refutes")
    if "supports" in opinions and "refutes" in opinions:
        receipt["conclusion"] = "unresolved"
        receipt["abstention_cause"] = "material_conflict"
        receipt["local_material_conflict"] = True
        return receipt
    if opinions:
        receipt["conclusion"] = opinions[0]
        receipt["abstention_cause"] = None
        return receipt
    receipt["conclusion"] = "unresolved"
    receipt["abstention_cause"] = "event_order_not_in_evidence"
    return receipt


def scope_guard(raw: bytes) -> dict[str, Any]:
    receipt = _base("scope_guard", "guard", raw)
    envelope = parse_envelope(raw)
    claim = parse_view(envelope["claim"])
    if not claim["years"] and not claim["quantifiers"]:
        receipt["abstention_cause"] = "no_scope_constraint"
        return receipt
    receipt["applicability"] = "applicable"
    if not envelope["evidence"]:
        receipt["conclusion"] = "unresolved"
        receipt["abstention_cause"] = "missing_evidence"
        return receipt
    evidence_years: set[str] = set()
    evidence_quantifiers: set[str] = set()
    for passage in envelope["evidence"]:
        view = parse_view(passage["text"])
        evidence_years.update(view["years"])
        evidence_quantifiers.update(view["quantifiers"])
    if claim["years"] and not set(claim["years"]).issubset(evidence_years):
        receipt["conclusion"] = "violated"
        receipt["abstention_cause"] = "time_mismatch"
        return receipt
    if claim["quantifiers"] and not set(claim["quantifiers"]).issubset(evidence_quantifiers):
        receipt["conclusion"] = "violated"
        receipt["abstention_cause"] = "quantifier_mismatch"
        return receipt
    receipt["conclusion"] = "satisfied"
    receipt["abstention_cause"] = None
    return receipt


def attribution_guard(raw: bytes) -> dict[str, Any]:
    receipt = _base("attribution_guard", "guard", raw)
    envelope = parse_envelope(raw)
    claim = parse_view(envelope["claim"])
    if not envelope["evidence"] and not claim["hedges"]:
        receipt["abstention_cause"] = "no_attribution_constraint"
        return receipt
    evidence_hedges: set[str] = set()
    for passage in envelope["evidence"]:
        evidence_hedges.update(parse_view(passage["text"])["hedges"])
    claim_hedges = set(claim["hedges"])
    if not claim_hedges and not evidence_hedges:
        receipt["abstention_cause"] = "no_attribution_constraint"
        return receipt
    receipt["applicability"] = "applicable"
    if claim_hedges != evidence_hedges:
        receipt["conclusion"] = "violated"
        receipt["abstention_cause"] = "attribution_mismatch"
        return receipt
    receipt["conclusion"] = "satisfied"
    receipt["abstention_cause"] = None
    return receipt


JUDGES = {
    "quantity_relation": quantity_relation,
    "event_order": event_order,
    "scope_guard": scope_guard,
    "attribution_guard": attribution_guard,
}
