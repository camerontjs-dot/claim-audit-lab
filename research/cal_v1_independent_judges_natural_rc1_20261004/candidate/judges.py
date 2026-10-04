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


def _is_year_token(item: dict[str, Any]) -> bool:
    return item["unit"] == "" and item["number"] not in {"19", "20"} and bool(
        re.fullmatch(r"(?:19|20)\d{2}", item["number"])
    )


def _quantities(view: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in view["numbers"]
        if item["number"] not in {"19", "20"} and not _is_year_token(item)
    ]


def _key(item: dict[str, Any]) -> tuple[str, str, str]:
    return (str(item["sign"]), str(item["number"]), str(item["unit"]))


def _pair(claim_number: dict[str, Any], evidence_number: dict[str, Any]) -> str:
    claim_direction = claim_number.get("direction")
    evidence_direction = evidence_number.get("direction")
    if claim_direction == "unchanged" or evidence_direction == "unchanged":
        return "supports" if claim_direction == evidence_direction else "unresolved"
    if claim_direction is None and evidence_direction is None:
        return "supports"
    if claim_direction is None or evidence_direction is None:
        return "unresolved"
    same_direction = claim_direction == evidence_direction
    same_polarity = claim_number.get("polarity") == evidence_number.get("polarity")
    opposite = {claim_direction, evidence_direction} == {"increase", "decrease"}
    if same_direction and same_polarity:
        return "supports"
    if same_direction and not same_polarity:
        return "refutes"
    if opposite and claim_number.get("polarity") == "positive" and evidence_number.get("polarity") == "positive":
        return "refutes"
    return "unresolved"


def _passage_opinion(claim_numbers: list[dict[str, Any]], evidence_numbers: list[dict[str, Any]]) -> str | None:
    labels: list[str] = []
    for claim_number in claim_numbers:
        matches = [item for item in evidence_numbers if _key(item) == _key(claim_number)]
        if not matches:
            return None
        local = [_pair(claim_number, item) for item in matches]
        if "supports" in local and "refutes" in local:
            return "conflict"
        if "refutes" in local:
            labels.append("refutes")
        elif "supports" in local:
            labels.append("supports")
        else:
            labels.append("unresolved")
    if "refutes" in labels:
        return "refutes"
    if "unresolved" in labels:
        return "unresolved"
    return "supports"


def _union_scope(claim: dict[str, Any], passages: list[dict[str, Any]]) -> str | None:
    years: set[str] = set()
    quantifiers: set[str] = set()
    for passage in passages:
        view = parse_view(str(passage["text"]))
        years.update(view["years"])
        quantifiers.update(view["quantifiers"])
    if claim["years"] and not set(claim["years"]).issubset(years):
        return "time_mismatch"
    if claim["quantifiers"] and not set(claim["quantifiers"]).issubset(quantifiers):
        return "quantifier_mismatch"
    return None


def quantity_relation(raw: bytes) -> dict[str, Any]:
    receipt = _base("quantity_relation", "relation", raw)
    envelope = parse_envelope(raw)
    claim = parse_view(envelope["claim"])
    receipt["claim_interpretation"] = claim
    claim_numbers = _quantities(claim)
    if not claim_numbers:
        receipt["abstention_cause"] = "unparsed_comparison"
        return receipt
    receipt["applicability"] = "applicable"
    if not envelope["evidence"]:
        receipt["conclusion"] = "unresolved"
        receipt["abstention_cause"] = "missing_evidence"
        return receipt
    mismatch = _union_scope(claim, envelope["evidence"])
    if mismatch is not None:
        receipt["conclusion"] = "unresolved"
        receipt["abstention_cause"] = mismatch
        return receipt
    opinions: list[str] = []
    for passage in envelope["evidence"]:
        opinion = _passage_opinion(claim_numbers, _quantities(parse_view(str(passage["text"]))))
        if opinion is not None:
            opinions.append(opinion)
    if "conflict" in opinions or ("supports" in opinions and "refutes" in opinions):
        receipt["conclusion"] = "unresolved"
        receipt["abstention_cause"] = "material_conflict"
        receipt["local_material_conflict"] = True
        return receipt
    if "supports" in opinions:
        receipt["conclusion"] = "supports"
        receipt["abstention_cause"] = None
        return receipt
    if "refutes" in opinions:
        receipt["conclusion"] = "refutes"
        receipt["abstention_cause"] = None
        return receipt
    receipt["conclusion"] = "unresolved"
    receipt["abstention_cause"] = "no_matching_passage"
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
