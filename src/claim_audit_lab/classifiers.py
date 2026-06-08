"""Reusable text-based semantic claim type classifier.

CAL's ClaimType (numeric, causal, comparative, …) is a SEMANTIC type used
inside the audit pipeline.  It is entirely distinct from the C-B contract
vocabulary field claim_type (retrieval_seed | extracted_claim), which
describes the role of a claim inside the Evidence Bundler workflow.

Never copy a C-B claim_type value into a CAL Claim.claim_type slot.
Always derive CAL semantic type from the claim text via classify_claim_text().
"""
from __future__ import annotations

import re

from claim_audit_lab.models import ClaimType

_PATTERNS: list[tuple[re.Pattern[str], ClaimType]] = [
    (re.compile(r"\b\d[\d,.%$]+\b"), "numeric"),
    (re.compile(r"\b(cause[sd]?|lead[s]? to|result[s]? in|due to)\b", re.I), "causal"),
    (
        re.compile(
            r"\b(more|less|higher|lower|better|worse|compared|versus|vs\.?)\b", re.I
        ),
        "comparative",
    ),
    (
        re.compile(r"\b(certified|licensed|accredited|qualified|credential)\b", re.I),
        "credential",
    ),
    (
        re.compile(r"\b(will|would|forecast|predict|expect|project)\b", re.I),
        "prediction",
    ),
    (
        re.compile(r"\b(can|able to|capable|support[s]?|enable[s]?)\b", re.I),
        "capability",
    ),
    (re.compile(r"\b(all|most|some|none|any|every|no)\b", re.I), "scope"),
]
_DEFAULT: ClaimType = "interpretive"


def classify_claim_text(text: str) -> ClaimType:
    """Return a deterministic CAL semantic ClaimType for a claim text string.

    Pattern priority is first-match; order in _PATTERNS is intentional.
    Falls back to 'interpretive' when no pattern matches.
    """
    for pattern, label in _PATTERNS:
        if pattern.search(text):
            return label
    return _DEFAULT


__all__ = ["classify_claim_text"]
