"""Original-text comparison relation. Claim text and passage text are parsed apart.

The grammar keeps a year, a property span, and an all/some age-group quantifier
when they are present. A form this module cannot represent is uninterpreted.
It does not delete those spans in order to match a simpler comparison.
"""

from __future__ import annotations

import re
from typing import Any

from codec import digest, parse_envelope

_ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
_DIRECTIONS = {
    "higher": "MORE_THAN",
    "greater": "MORE_THAN",
    "larger": "MORE_THAN",
    "more": "MORE_THAN",
    "lower": "LESS_THAN",
    "smaller": "LESS_THAN",
    "fewer": "LESS_THAN",
    "less": "LESS_THAN",
}
_MEASURES = "share|rate|percentage|proportion|output|count|volume|score|yield"
_CORE = re.compile(
    rf"^(?P<lhs>{_ENTITY}) (?P<polarity>did not have|had) (?:a )?"
    rf"(?P<direction>{'|'.join(_DIRECTIONS)}) "
    rf"(?:(?P<property>[A-Za-z]+(?: [A-Za-z]+)*) )?"
    rf"(?P<measure>{_MEASURES}) than (?P<rhs>{_ENTITY})$"
)
_TIME = re.compile(r"^In (?P<time>20\d{2}), (?P<rest>.+)$")
_QUANTIFIER = re.compile(r"^(?P<body>.+) in (?P<quantifier>all|some) age groups$")
_ALLEGATION = "A report alleged that "


def _space(text: str) -> str:
    return " ".join(text.strip().split())


def parse_comparison_text(text: str) -> dict[str, Any] | None:
    """Interpret one string alone. Returns None when the string is not this form."""
    normalized = _space(text)
    if normalized.endswith("."):
        normalized = normalized[:-1]
    assertion = "direct"
    if normalized.startswith(_ALLEGATION):
        assertion = "allegation"
        normalized = normalized[len(_ALLEGATION) :]
    time: str | None = None
    timed = _TIME.fullmatch(normalized)
    if timed is not None:
        time = timed.group("time")
        normalized = timed.group("rest")
    quantifier: str | None = None
    quantified = _QUANTIFIER.fullmatch(normalized)
    if quantified is not None:
        quantifier = quantified.group("quantifier")
        normalized = quantified.group("body")
    matched = _CORE.fullmatch(normalized)
    if matched is None:
        return None
    return {
        "lhs": matched.group("lhs"),
        "rhs": matched.group("rhs"),
        "direction": _DIRECTIONS[matched.group("direction").casefold()],
        "polarity": "negative" if matched.group("polarity") == "did not have" else "positive",
        "measure": matched.group("measure").casefold(),
        "property": (matched.group("property") or "").strip(),
        "time": time,
        "quantifier": quantifier,
        "assertion": assertion,
    }


def _orient(view: dict[str, Any]) -> dict[str, Any]:
    lhs = str(view["lhs"]).casefold()
    rhs = str(view["rhs"]).casefold()
    if view["direction"] == "MORE_THAN":
        high, low = lhs, rhs
    else:
        high, low = rhs, lhs
    stance = "asserted" if view["polarity"] == "positive" else "denied"
    return {
        "high": high,
        "low": low,
        "stance": stance,
        "measure": view["measure"],
        "property": str(view["property"]).casefold(),
        "time": view["time"],
        "quantifier": view["quantifier"],
        "assertion": view["assertion"],
    }


def _same_dimensions(claim: dict[str, Any], evidence: dict[str, Any]) -> bool:
    return (
        claim["measure"] == evidence["measure"]
        and claim["property"] == evidence["property"]
        and claim["time"] == evidence["time"]
        and claim["quantifier"] == evidence["quantifier"]
    )


def relate_passage(claim: dict[str, Any], evidence: dict[str, Any] | None) -> str:
    if evidence is None:
        return "uninterpreted"
    claim_view = _orient(claim)
    evidence_view = _orient(evidence)
    if {claim_view["high"], claim_view["low"]} != {evidence_view["high"], evidence_view["low"]}:
        return "irrelevant"
    if evidence_view["assertion"] != "direct":
        return "attribution"
    if not _same_dimensions(claim_view, evidence_view):
        return "constraint_mismatch"
    same_orientation = (claim_view["high"], claim_view["low"]) == (
        evidence_view["high"],
        evidence_view["low"],
    )
    if same_orientation:
        if claim_view["stance"] == evidence_view["stance"]:
            return "supports"
        return "refutes"
    if claim_view["stance"] == "asserted" and evidence_view["stance"] == "asserted":
        return "refutes"
    return "polarity_non_establishing"


def _base(raw: bytes, process_id: str = "original_relation") -> dict[str, Any]:
    return {
        "process_id": process_id,
        "input_sha256": digest(raw),
        "execution": "completed",
        "role": "relation",
        "material_loss": False,
        "instrument_id": "comparison-relation-rc0",
        "instrument_version": "deterministic-text-rc0",
        "model": None,
        "dependence_group": "same-author-comparison-text",
    }


def judge(raw: bytes) -> dict[str, Any]:
    envelope = parse_envelope(raw)
    claim = parse_comparison_text(envelope["claim"])
    if claim is None:
        return {
            **_base(raw),
            "applicability": "not_applicable",
            "conclusion": "not_applicable",
            "warrant": "qualified",
            "abstention_cause": "unsupported_form",
            "claim_interpretation": None,
            "evidence_interpretations": [],
            "local_material_conflict": False,
            "consumed_passage_ids": [],
            "available_passage_ids": [item["id"] for item in envelope["evidence"]],
        }
    findings: list[dict[str, Any]] = []
    for passage in envelope["evidence"]:
        evidence = parse_comparison_text(passage["text"])
        findings.append(
            {
                "passage_id": passage["id"],
                "interpretation": evidence,
                "relation": relate_passage(claim, evidence),
            }
        )
    votes = [item["relation"] for item in findings if item["relation"] in {"supports", "refutes"}]
    cause: str | None = None
    warrant = "qualified"
    conflict = False
    if not envelope["evidence"]:
        conclusion = "unresolved"
        cause = "missing_evidence"
    elif "supports" in votes and "refutes" in votes:
        conclusion = "unresolved"
        cause = "material_conflict"
        conflict = True
    elif votes and all(vote == "supports" for vote in votes):
        conclusion = "supports"
    elif votes and all(vote == "refutes" for vote in votes):
        conclusion = "refutes"
    elif any(item["relation"] == "attribution" for item in findings):
        conclusion = "unresolved"
        cause = "attribution"
        warrant = "unqualified"
    elif any(item["relation"] == "constraint_mismatch" for item in findings):
        conclusion = "unresolved"
        cause = "scope_mismatch"
    elif any(item["relation"] == "polarity_non_establishing" for item in findings):
        conclusion = "unresolved"
        cause = "polarity_non_establishing"
    else:
        conclusion = "unresolved"
        cause = "measurement_miss"
    return {
        **_base(raw),
        "applicability": "applicable",
        "conclusion": conclusion,
        "warrant": warrant,
        "abstention_cause": cause,
        "claim_interpretation": claim,
        "evidence_interpretations": findings,
        "local_material_conflict": conflict,
        "consumed_passage_ids": [item["id"] for item in envelope["evidence"]],
        "available_passage_ids": [item["id"] for item in envelope["evidence"]],
        "consumed_claim": envelope["claim"],
    }
