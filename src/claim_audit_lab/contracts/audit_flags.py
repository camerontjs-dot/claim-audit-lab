"""Compute false_caution_flag, deviation_flag, and audit_confidence.

Definitions
-----------
false_caution_flag
    The scaffold was uncertain or pessimistic (uncertain / unsupported),
    but CAL's deterministic audit finds strong positive support
    (supported or partially_supported).  Signals a potential scaffold
    over-caution worth reviewing.

deviation_flag
    The scaffold_support_status and CAL's audit_support_verdict materially
    disagree.  "Material" is defined by the _MATERIAL_DISAGREE set below.
    Not every disagreement is material; minor gradations are not flagged.

audit_confidence
    CAL's deterministic support signal in [0.0, 1.0]: maximum linked support
    score minus the configured counterevidence penalty. It is not a truth
    probability or a claim-quality score.
"""

from __future__ import annotations

from dataclasses import dataclass

from claim_audit_lab.contracts.cb_models import CBClaim
from claim_audit_lab.models import ClaimAssessment

_SCAFFOLD_CAUTIOUS = frozenset({"uncertain", "unsupported"})
_CAL_POSITIVE = frozenset({"supported", "partially_supported"})

# Pairs (scaffold_support_status, cal_verdict) that constitute a material
# disagreement worth flagging for human review.
_MATERIAL_DISAGREE: frozenset[tuple[str, str]] = frozenset(
    {
        ("sourced", "unsupported"),
        ("sourced", "needs_source"),
        ("sourced", "overstated"),
        ("sourced", "not_checkable"),
        ("uncertain", "supported"),
        ("uncertain", "partially_supported"),
        ("unsupported", "supported"),
        ("unsupported", "partially_supported"),
        ("inferred", "unsupported"),
        ("inferred", "overstated"),
    }
)

_DEFAULT_FALSE_CAUTION_THRESHOLD = 0.85


def is_material_deviation(scaffold_status: str, cb_verdict: str) -> bool:
    """Return whether ``(scaffold_status, cb_verdict)`` is a material disagreement.

    Shared by the v0.2 (`compute_flags`) and v1 (`v1.cb_writeback`) audit paths so
    the C-B ``deviation_flag`` is computed identically regardless of which auditor
    produced ``cb_verdict``.
    """
    return (scaffold_status, cb_verdict) in _MATERIAL_DISAGREE


@dataclass(frozen=True)
class AuditFlagResult:
    """Computed C-B audit output flags for one claim."""

    false_caution_flag: bool
    deviation_flag: bool
    audit_confidence: float
    deviation_notes: str


def compute_flags(
    cb_claim: CBClaim,
    assessment: ClaimAssessment,
    *,
    false_caution_detection: bool = True,
    false_caution_threshold: float = _DEFAULT_FALSE_CAUTION_THRESHOLD,
) -> AuditFlagResult:
    """Return computed C-B audit flags and confidence.

    Parameters
    ----------
    cb_claim:
        The original C-B claim (supplies scaffold_support_status).
    assessment:
        CAL's ClaimAssessment for the same claim.
    """
    scaffold_status = cb_claim.scaffold_support_status
    cal_verdict = assessment.support_label
    confidence = _audit_confidence(assessment)

    false_caution = (
        false_caution_detection
        and scaffold_status in _SCAFFOLD_CAUTIOUS
        and cal_verdict in _CAL_POSITIVE
        and confidence >= false_caution_threshold
    )
    deviation = is_material_deviation(scaffold_status, cal_verdict)
    notes = _deviation_notes(
        scaffold_status=scaffold_status,
        cal_verdict=cal_verdict,
        false_caution=false_caution,
        deviation=deviation,
    )

    return AuditFlagResult(
        false_caution_flag=false_caution,
        deviation_flag=deviation,
        audit_confidence=confidence,
        deviation_notes=notes,
    )


def _audit_confidence(assessment: ClaimAssessment) -> float:
    if assessment.support_signal is not None:
        return assessment.support_signal
    return max(
        (candidate.score for candidate in assessment.candidate_evidence),
        default=0.0,
    )


def _deviation_notes(
    *,
    scaffold_status: str,
    cal_verdict: str,
    false_caution: bool,
    deviation: bool,
) -> str:
    context = f"scaffold_support_status={scaffold_status}; audit_support_verdict={cal_verdict}"
    if false_caution:
        return (
            f"Material disagreement: {context}; false_caution_flag=true because the "
            "scaffold was cautious and CAL found supplied-evidence support."
        )
    if deviation:
        return f"Material disagreement: {context}."
    return f"No material disagreement between scaffold support status and CAL verdict: {context}."


__all__ = ["AuditFlagResult", "compute_flags", "is_material_deviation"]
