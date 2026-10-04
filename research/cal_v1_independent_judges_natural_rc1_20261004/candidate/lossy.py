"""Shared reduction used only by arm B. Judges do not import this module."""

from __future__ import annotations

import re
from typing import Any

from codec import canonical

_TRANSFORM_ID = "shared-lossy-rc1-strip-year-quantifier-hedge"
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_QUANTIFIER = re.compile(r"\b(?:all|some|every|most|each)\b", re.IGNORECASE)
_HEDGE = re.compile(r"\b(?:alleged|reportedly|projected|projection|according to)\b", re.IGNORECASE)


def lossy_text(text: str) -> str:
    rewritten = _HEDGE.sub("", text)
    rewritten = _YEAR.sub("", rewritten)
    rewritten = _QUANTIFIER.sub("", rewritten)
    return " ".join(rewritten.split())


def lossy_envelope(envelope: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    claim = lossy_text(str(envelope["claim"]))
    evidence = [
        {"id": item["id"], "text": lossy_text(str(item["text"]))} for item in envelope["evidence"]
    ]
    changed = claim != " ".join(str(envelope["claim"]).split()) or any(
        item["text"] != " ".join(str(original["text"]).split())
        for item, original in zip(evidence, envelope["evidence"], strict=True)
    )
    return canonical({"claim": claim, "evidence": evidence}), {
        "transform_id": _TRANSFORM_ID,
        "material_tokens_removed": changed,
        "operations": [
            "strip_four_digit_years",
            "strip_quantifier_words",
            "strip_hedge_words",
        ],
    }
