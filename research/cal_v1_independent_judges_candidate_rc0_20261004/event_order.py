"""Direct event-order lane for the same dispatch used by comparison claims.

The verb list is the closed positive list already used by the frozen kernel.
Negative event polarity is recognized and left unresolved. This lane does not
read comparison conclusions.
"""

from __future__ import annotations

import re
from typing import Any

from codec import digest, parse_envelope

_ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
_VERBS = {
    "reviewed": "review",
    "signed": "sign",
    "inspected": "inspect",
    "released": "release",
    "approved": "approve",
    "archived": "archive",
    "processed": "process",
    "verified": "verify",
    "recorded": "record",
}
_SIDE = re.compile(
    rf"^(?P<subject>{_ENTITY}) (?P<verb>{'|'.join(_VERBS)}) "
    rf"(?P<object>[A-Za-z0-9-]+(?: [A-Za-z0-9-]+){{0,5}})$"
)
_CUE = re.compile(r"\b(before|after)\b", re.IGNORECASE)


def parse_event_text(text: str) -> dict[str, Any] | None:
    normalized = " ".join(text.strip().split())
    if normalized.endswith("."):
        normalized = normalized[:-1]
    cues = list(_CUE.finditer(normalized))
    if len(cues) != 1:
        return None
    cue = cues[0]
    left = _SIDE.fullmatch(normalized[: cue.start()].strip())
    right = _SIDE.fullmatch(normalized[cue.end() :].strip())
    if left is None or right is None:
        return None
    return {
        "left": _side(left),
        "right": _side(right),
        "relation": cue.group(1).upper(),
    }


def _side(match: re.Match[str]) -> dict[str, str]:
    return {
        "subject": match.group("subject").casefold(),
        "predicate": _VERBS[match.group("verb").casefold()],
        "object": match.group("object").casefold(),
        "polarity": "positive",
    }


def _tuple(side: dict[str, str]) -> tuple[str, str, str, str]:
    return (side["subject"], side["predicate"], side["object"], side["polarity"])


def relate_events(claim: dict[str, Any], evidence: dict[str, Any] | None) -> str:
    if evidence is None:
        return "uninterpreted"
    claim_left = _tuple(claim["left"])
    claim_right = _tuple(claim["right"])
    evidence_left = _tuple(evidence["left"])
    evidence_right = _tuple(evidence["right"])
    if claim["relation"] not in {"BEFORE", "AFTER"} or evidence["relation"] not in {"BEFORE", "AFTER"}:
        return "unresolved"
    if (evidence_left, evidence_right) == (claim_left, claim_right):
        normalized = evidence["relation"]
    elif (evidence_left, evidence_right) == (claim_right, claim_left):
        normalized = "AFTER" if evidence["relation"] == "BEFORE" else "BEFORE"
    else:
        return "irrelevant"
    return "supports" if normalized == claim["relation"] else "refutes"


def judge(raw: bytes) -> dict[str, Any]:
    envelope = parse_envelope(raw)
    base = {
        "process_id": "event_order",
        "input_sha256": digest(raw),
        "execution": "completed",
        "role": "relation",
        "material_loss": False,
        "instrument_id": "event-order-rc0",
        "instrument_version": "deterministic-text-rc0",
        "model": None,
        "dependence_group": "event-order-text",
        "local_material_conflict": False,
        "available_passage_ids": [item["id"] for item in envelope["evidence"]],
    }
    claim = parse_event_text(envelope["claim"])
    if claim is None:
        return {
            **base,
            "applicability": "not_applicable",
            "conclusion": "not_applicable",
            "warrant": "qualified",
            "abstention_cause": "unsupported_form",
            "claim_interpretation": None,
            "evidence_interpretations": [],
            "consumed_passage_ids": [],
        }
    findings = []
    for passage in envelope["evidence"]:
        evidence = parse_event_text(passage["text"])
        findings.append(
            {
                "passage_id": passage["id"],
                "interpretation": evidence,
                "relation": relate_events(claim, evidence),
            }
        )
    votes = [item["relation"] for item in findings if item["relation"] in {"supports", "refutes"}]
    if not envelope["evidence"]:
        conclusion, cause, conflict = "unresolved", "missing_evidence", False
    elif "supports" in votes and "refutes" in votes:
        conclusion, cause, conflict = "unresolved", "material_conflict", True
    elif votes and all(vote == "supports" for vote in votes):
        conclusion, cause, conflict = "supports", None, False
    elif votes and all(vote == "refutes" for vote in votes):
        conclusion, cause, conflict = "refutes", None, False
    else:
        conclusion, cause, conflict = "unresolved", "measurement_miss", False
    return {
        **base,
        "applicability": "applicable",
        "conclusion": conclusion,
        "warrant": "qualified",
        "abstention_cause": cause,
        "claim_interpretation": claim,
        "evidence_interpretations": findings,
        "local_material_conflict": conflict,
        "consumed_passage_ids": [item["id"] for item in envelope["evidence"]],
        "consumed_claim": envelope["claim"],
    }
