"""Conservative direct-assertion eligibility gate for strict comparison RC0."""

from __future__ import annotations

import re
from dataclasses import dataclass

from claim_audit_lab.cal_v1_candidate.engine import AuditResult, audit
from claim_audit_lab.cal_v1_candidate.models import AuditContext, Conclusion


_NEGATION = re.compile(
    r"(?:\b(?:not|no|never|neither|nor)\b|n['’]t\b)",
    re.IGNORECASE,
)
_EPISTEMIC = re.compile(
    r"\b(?:may|might|could|possibly|probably|perhaps|apparently|"
    r"likely|unlikely|seem|seems|seemed|appear|appears|appeared|"
    r"purportedly|ostensibly|reportedly|rumou?red)\b",
    re.IGNORECASE,
)
_ATTRIBUTION = re.compile(
    r"\b(?:according|allege(?:d|s)?|allegedly|author(?:s)?|"
    r"claim(?:ed|s)?|report(?:ed|s)?|said|says|state(?:d|s)?|"
    r"study|studies|suggest(?:ed|s)?|purport(?:ed|s)?)\b",
    re.IGNORECASE,
)
_CONDITIONAL = re.compile(
    r"(?:\b(?:if|unless|assuming|supposing|provided)\b|\bonly\s+if\b)",
    re.IGNORECASE,
)
_COMPOSITION = re.compile(r"\b(?:and|or)\b", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class Eligibility:
    eligible: bool
    reason: str


def eligibility(text: str) -> Eligibility:
    """Return whether text is eligible for strict-comparison warranting.

    This is deliberately a jurisdiction gate, not a comparison parser.
    """

    if not isinstance(text, str) or not text.strip():
        return Eligibility(False, "EMPTY_OR_NON_TEXT")
    compact = " ".join(text.strip().split())
    if '"' in compact or "“" in compact or "”" in compact or "?" in compact:
        return Eligibility(False, "QUOTED_OR_QUESTION_SURFACE")
    if _NEGATION.search(compact):
        return Eligibility(False, "NEGATION_PRESENT")
    if _EPISTEMIC.search(compact):
        return Eligibility(False, "EPISTEMIC_MODALITY_PRESENT")
    if _ATTRIBUTION.search(compact):
        return Eligibility(False, "ATTRIBUTION_PRESENT")
    if _CONDITIONAL.search(compact):
        return Eligibility(False, "CONDITIONAL_PRESENT")
    if _COMPOSITION.search(compact):
        return Eligibility(False, "UNSUPPORTED_COMPOSITION")
    return Eligibility(True, "DIRECT_ASSERTION_ELIGIBLE")


def guarded_audit(context: AuditContext) -> AuditResult | None:
    """Run frozen RC1 only when the single admitted passage is eligible."""

    passages = context.evidence_world.admitted_passages
    if len(passages) != 1:
        return None
    if not eligibility(passages[0].text).eligible:
        return None
    return audit(context)


def deciding_conclusion(context: AuditContext) -> Conclusion:
    result = guarded_audit(context)
    return Conclusion.NOT_CHECKABLE if result is None else result.conclusion
