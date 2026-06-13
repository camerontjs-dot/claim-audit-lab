"""Deterministic semantic claim classification."""

from __future__ import annotations

import re
from re import Pattern

from claim_audit_lab.models import ClaimType
from claim_audit_lab.text import normalize_text

_CLAIM_TYPE_PATTERNS: tuple[tuple[ClaimType, tuple[Pattern[str], ...]], ...] = (
    (
        "prediction",
        (
            re.compile(r"\b(will|would|should|always|never|guarantees?|ensures?)\b"),
            re.compile(r"\b(future|predicts?|expected to|likely to|forecast|project)\b"),
        ),
    ),
    (
        "scope",
        (
            re.compile(r"\b(all|every|across|throughout|universal|any|entire|broad)\b"),
            re.compile(r"\b(multi step|enterprise|organization wide)\b"),
        ),
    ),
    (
        "causal",
        (
            re.compile(r"\b(causes?|caused|because|after|prevents?|reduced?|reduces?)\b"),
            re.compile(r"\b(leads? to|led to|fell from|eliminates?|resulted in|due to)\b"),
        ),
    ),
    (
        "comparative",
        (
            re.compile(r"\b(more|less|better|worse|stronger|weaker|higher|lower)\b"),
            re.compile(r"\b(faster|slower|compared with|compared to|versus|vs|than)\b"),
        ),
    ),
    (
        "credential",
        (
            re.compile(r"\b(certified|certification|degree|bachelor|master|phd|doctorate)\b"),
            re.compile(r"\b(licensed|licence|license|years? of experience|worked at)\b"),
            re.compile(r"\b(employer|published|publication|author|manager|director)\b"),
            re.compile(r"\b(technician|specialist|officer|role|qualified|credential)\b"),
        ),
    ),
    (
        "capability",
        (
            re.compile(r"\b(can|could|supports?|detects?|allows?|enables?|handles?)\b"),
            re.compile(r"\b(is able to|are able to|capable of|generates?|extracts?)\b"),
        ),
    ),
    ("numeric", (re.compile(r"\b\d+(?:\.\d+)?%?\b"),)),
    (
        "interpretive",
        (
            re.compile(r"\b(clear|clearly|robust|credible|important|strong|weak)\b"),
            re.compile(r"\b(useful|effective|meaningful|material|significant)\b"),
        ),
    ),
)


def classify_claim_text(text: str) -> ClaimType:
    """Return the first matching semantic claim type in governed priority order."""
    normalized = normalize_text(text)
    for claim_type, patterns in _CLAIM_TYPE_PATTERNS:
        if any(pattern.search(normalized) for pattern in patterns):
            return claim_type
    return "unclassified"


__all__ = ["classify_claim_text"]
