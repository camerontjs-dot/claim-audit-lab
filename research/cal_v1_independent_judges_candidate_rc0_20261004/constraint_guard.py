"""Independent scope, property, measure, and quantifier constraint check.

This module does not import the relation judge and does not emit a support or
refutation. Polarity is recorded and is not itself a guard violation: a negated
comparison can be a real refutation of the same scoped claim.
"""

from __future__ import annotations

import re
from typing import Any

from codec import digest, parse_envelope

_ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
_YEAR = re.compile(r"\b(20\d{2})\b")
_QUANTIFIER = re.compile(r"\bin (all|some) age groups\b")
_MEASURE = re.compile(
    r"\b(share|rate|percentage|proportion|output|count|volume|score|yield)\b",
    re.IGNORECASE,
)
_DIRECTION = re.compile(
    r"\b(higher|greater|larger|lower|smaller|more|fewer|less)\b",
    re.IGNORECASE,
)
_COMPARISON = re.compile(r"\bthan\b", re.IGNORECASE)
_EVENT = re.compile(
    r"\b(before|after)\b.*\b(reviewed|approved|signed|inspected|released|archived|processed|verified|recorded)\b"
    r"|\b(reviewed|approved|signed|inspected|released|archived|processed|verified|recorded)\b.*\b(before|after)\b",
    re.IGNORECASE,
)
_PROPERTY = re.compile(
    r"\b(?:higher|greater|larger|lower|smaller|more|fewer|less)\b"
    r"(?P<middle>.*?)"
    r"\b(?P<measure>share|rate|percentage|proportion|output|count|volume|score|yield)\b",
    re.IGNORECASE,
)
_ENDPOINTS = re.compile(rf"^(?P<lhs>{_ENTITY})\b.*\bthan (?P<rhs>{_ENTITY})\b", re.IGNORECASE)
_ALLEGATION = re.compile(r"^A report alleged that ", re.IGNORECASE)
_TIME_PREFIX = re.compile(r"^In 20\d{2}, ")


def _comparison(text: str) -> bool:
    return _DIRECTION.search(text) is not None and _COMPARISON.search(text) is not None and _MEASURE.search(text) is not None


def _event(text: str) -> bool:
    return _EVENT.search(text) is not None


def _constraints(text: str) -> dict[str, Any]:
    stripped = _TIME_PREFIX.sub("", _ALLEGATION.sub("", " ".join(text.strip().split())))
    endpoints = _ENDPOINTS.search(stripped)
    pair: list[str] | None = None
    if endpoints is not None:
        pair = sorted([endpoints.group("lhs").casefold(), endpoints.group("rhs").casefold()])
    property_match = _PROPERTY.search(stripped)
    property_text = ""
    measure = None
    if property_match is not None:
        property_text = " ".join(property_match.group("middle").split())
        measure = property_match.group("measure").casefold()
    return {
        "years": sorted(set(_YEAR.findall(text))),
        "quantifiers": sorted(set(_QUANTIFIER.findall(text))),
        "property": property_text.casefold(),
        "measure": measure,
        "pair": pair,
        "allegation": _ALLEGATION.match(" ".join(text.strip().split())) is not None,
    }


def _base(raw: bytes) -> dict[str, Any]:
    return {
        "process_id": "scope_guard",
        "input_sha256": digest(raw),
        "execution": "completed",
        "role": "guard",
        "material_loss": False,
        "warrant": "qualified",
        "instrument_id": "constraint-guard-rc0",
        "instrument_version": "deterministic-text-rc0",
        "model": None,
        "dependence_group": "same-author-comparison-text",
        "local_material_conflict": False,
    }


def judge(raw: bytes) -> dict[str, Any]:
    envelope = parse_envelope(raw)
    claim = envelope["claim"]
    claim_is_comparison = _comparison(claim)
    claim_is_event = _event(claim)
    if claim_is_comparison and claim_is_event:
        return {
            **_base(raw),
            "applicability": "unknown",
            "conclusion": "unresolved",
            "abstention_cause": "ambiguous_form",
            "claim_constraints": None,
            "evidence_constraints": [],
        }
    if claim_is_event and not claim_is_comparison:
        return {
            **_base(raw),
            "applicability": "not_applicable",
            "conclusion": "not_applicable",
            "abstention_cause": "not_a_comparison_constraint",
            "claim_constraints": None,
            "evidence_constraints": [],
        }
    if not claim_is_comparison:
        return {
            **_base(raw),
            "applicability": "unknown",
            "conclusion": "unresolved",
            "abstention_cause": "uninterpreted_claim",
            "claim_constraints": None,
            "evidence_constraints": [],
        }
    claim_constraints = _constraints(claim)
    if len(claim_constraints["years"]) > 1 or len(claim_constraints["quantifiers"]) > 1:
        return {
            **_base(raw),
            "applicability": "applicable",
            "conclusion": "unresolved",
            "abstention_cause": "ambiguous_constraint",
            "claim_constraints": claim_constraints,
            "evidence_constraints": [],
        }
    evidence_rows = []
    violated = False
    for passage in envelope["evidence"]:
        if not _comparison(passage["text"]):
            evidence_rows.append({"passage_id": passage["id"], "compared": False})
            continue
        observed = _constraints(passage["text"])
        evidence_rows.append({"passage_id": passage["id"], "compared": True, "constraints": observed})
        if observed["allegation"] or observed["pair"] is None or observed["pair"] != claim_constraints["pair"]:
            continue
        mismatch = (
            observed["years"] != claim_constraints["years"]
            or observed["quantifiers"] != claim_constraints["quantifiers"]
            or observed["property"] != claim_constraints["property"]
            or observed["measure"] != claim_constraints["measure"]
        )
        if mismatch:
            violated = True
    conclusion = "violated" if violated else "satisfied"
    return {
        **_base(raw),
        "applicability": "applicable",
        "conclusion": conclusion,
        "abstention_cause": "scope_mismatch" if violated else None,
        "claim_constraints": claim_constraints,
        "evidence_constraints": evidence_rows,
        "consumed_passage_ids": [item["id"] for item in envelope["evidence"]],
        "available_passage_ids": [item["id"] for item in envelope["evidence"]],
        "consumed_claim": claim,
    }
