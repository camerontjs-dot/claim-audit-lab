# ruff: noqa: I001
"""Positive structural eligibility gate for strict-comparison warranting."""

import re
from dataclasses import dataclass

from claim_audit_lab.cal_v1_candidate.engine import AuditResult, audit
from claim_audit_lab.cal_v1_candidate.models import AuditContext, Conclusion

_ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
_REL = r"(?:greater|higher|larger|lower|smaller)"
_DEGREE = r"(?:slightly|substantially|notably|considerably|materially|significantly)"
_MEASURE = r"(?:share|rate|percentage|proportion|output|count|volume|score|yield)"

_DIRECT = re.compile(
    rf"^(?P<left>{_ENTITY})\s+(?:is|was|remained|stayed)\s+"
    rf"(?:(?:{_DEGREE})\s+)?{_REL}\s+than\s+(?P<right>{_ENTITY})\.?$",
    re.IGNORECASE,
)
_MEASURE_HEAD = re.compile(
    rf"^(?P<left>{_ENTITY})\s+(?:recorded|showed|had)\s+(?:a\s+)?"
    rf"(?:(?:{_DEGREE})\s+)?{_REL}\s+{_MEASURE}\s+than\s+"
    rf"(?P<right>{_ENTITY})\.?$",
    re.IGNORECASE,
)
_VERB = re.compile(
    rf"^(?P<left>{_ENTITY})\s+(?:exceeded|trailed)\s+(?P<right>{_ENTITY})"
    rf"(?:\s+by\s+\d+(?:\.\d+)?(?:\s+(?:percentage\s+points?|percent|%|"
    rf"files?|samples?|units?|items?))?)?\.?$",
    re.IGNORECASE,
)
_DELTA = re.compile(
    rf"^(?P<left>{_ENTITY})\s+(?:processed|recorded|produced|counted|handled)\s+"
    rf"[^,]{{1,80}},\s+\d+(?:\.\d+)?(?:\s+(?:percentage\s+points?|"
    rf"percent|%|files?|samples?|units?|items?))?\s+"
    rf"(?:more|fewer|less)\s+than\s+(?P<right>{_ENTITY})\.?$",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class Eligibility:
    eligible: bool
    form: str


def eligibility(text: str) -> Eligibility:
    if not isinstance(text, str) or not text.strip():
        return Eligibility(False, "NONE")
    compact = " ".join(text.strip().split())
    for name, pattern in (
        ("DIRECT", _DIRECT),
        ("MEASURE_HEAD", _MEASURE_HEAD),
        ("VERB", _VERB),
        ("DELTA", _DELTA),
    ):
        if pattern.fullmatch(compact):
            return Eligibility(True, name)
    return Eligibility(False, "NONE")


def guarded_audit(context: AuditContext) -> AuditResult | None:
    passages = context.evidence_world.admitted_passages
    if len(passages) != 1:
        return None
    if not eligibility(passages[0].text).eligible:
        return None
    return audit(context)


def deciding_conclusion(context: AuditContext) -> Conclusion:
    result = guarded_audit(context)
    return Conclusion.NOT_CHECKABLE if result is None else result.conclusion
