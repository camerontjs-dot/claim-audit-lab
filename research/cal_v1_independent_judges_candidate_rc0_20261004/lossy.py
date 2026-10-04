"""Parent-side shared loss used only by arm B.

Lanes do not import this module. The transform is a counterfactual input, not
a production interpretation.
"""

from __future__ import annotations

import re
from typing import Any

from codec import canonical

_TRANSFORM_ID = "shared-lossy-rc0-strip-time-property-quantifier-attribution"
_ALLEGATION = re.compile(r"^A report alleged that ")
_TIME = re.compile(r"^In 20\d{2}, ")
_QUANTIFIER = re.compile(r" in (?:all|some) age groups(?=\.|$)")
_PROPERTY = re.compile(
    r"\b(higher|greater|larger|lower|smaller|more|fewer|less)\s+(?:[A-Za-z]+\s+)+"
    r"(share|rate|percentage|proportion|output|count|volume|score|yield)\b",
    re.IGNORECASE,
)


def lossy_text(text: str) -> str:
    rewritten = " ".join(text.strip().split())
    rewritten = _ALLEGATION.sub("", rewritten)
    rewritten = _TIME.sub("", rewritten)
    rewritten = _QUANTIFIER.sub("", rewritten)
    rewritten = _PROPERTY.sub(r"\1 \2", rewritten)
    return rewritten


def lossy_envelope(envelope: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    claim = lossy_text(str(envelope["claim"]))
    evidence = [
        {"id": item["id"], "text": lossy_text(str(item["text"]))} for item in envelope["evidence"]
    ]
    raw = canonical({"claim": claim, "evidence": evidence})
    record = {
        "transform_id": _TRANSFORM_ID,
        "operations": [
            "strip_leading_allegation_wrapper",
            "strip_leading_year",
            "strip_all_or_some_age_group_tail",
            "strip_property_span_between_direction_and_measure",
        ],
    }
    return raw, record
