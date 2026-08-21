"""Operator-facing reason codes derived *from* CAL's verdict, never re-decided.

The rule this module exists to enforce: an explanation must be a reading of the
verdict CAL actually returned, not a second decision procedure run over the raw
probabilities.  A previous version recomputed a decision from ``p_entail`` /
``p_contradict`` against its own copies of the thresholds, which meant it
announced ``DIRECT_CONTRADICTION`` on claims the rules layer had deliberately
stood down (A3 bound instantiation, A4 negation consistency, subject-scope
eligibility).  An explanation that contradicts its own verdict is worse than no
explanation, so every branch here keys off ``verdict.support_verdict`` first and
uses CAL's recorded reasons — ``support_verdict_reason``, ``rules_fired``, and
``parent_aggregation`` — as the source of the wording.

Thresholds are never hardcoded.  Where a number appears in operator text it is
read from the pinned ``AuditConfig`` so it cannot drift from the rules file.

Nothing here asserts that a claim is safe to accept or must be rejected.  CAL
reports what the supplied evidence supports; the accept/reject decision is not
CAL's to make and the vocabulary must not imply it is.
"""

from __future__ import annotations

from typing import Any

from claim_audit_lab.v1.explicit_claims import ExplicitClaimTrace
from claim_audit_lab.v1.models import AuditConfig, AuditTrace

# Display hint only. Never a decision.
_COLOR_BY_VERDICT: dict[str, str] = {
    "supported": "green",
    "partially_supported": "amber",
    "not_checkable": "amber",
    "unsupported": "amber",
    "contradicted": "red",
}

# Operator-facing gloss for CAL's five not_checkable reasons. The first three map
# onto the B1/B2/B3 split in
# outputs/2026-08-05-abstention-decomposition/FINDINGS.md; `conflicting_evidence`
# arrived with A5 in cal-rules-v1.9.0 and has no B-bucket yet.
_ABSTENTION_GLOSS: dict[str, tuple[str, str]] = {
    "no_evidence": (
        "NO_EVIDENCE_ADMITTED",
        "No passage cleared the retrieval floor ({floor:.2f}), so nothing was read.",
    ),
    "no_entail_signal": (
        "READ_NO_SUPPORT_ESTABLISHED",
        "Evidence was admitted and read; it neither established support nor "
        "contradicted the claim.",
    ),
    "out_of_scope": (
        "OUT_OF_SCOPE",
        "The admitted evidence is not about the claim's subject, so it cannot bear on it.",
    ),
    "absence_not_decidable": (
        "ABSENCE_NOT_DECIDABLE",
        "The claim says a document omits something. Passages taken from that "
        "document cannot settle it — confirm against the complete source.",
    ),
    "conflicting_evidence": (
        "EVIDENCE_DISAGREES",
        "Two admitted passages take opposite positions on the claim, both above "
        "threshold. Read both before relying on either.",
    ),
}


def _rule_provenance(rules_fired: list[Any]) -> list[str]:
    """The deterministic rules that produced this verdict, in fire order."""
    return [f"{r.rule_id}: {r.reason}" for r in rules_fired]


def _explicit_reason(trace: ExplicitClaimTrace) -> dict[str, Any]:
    """Read the parent verdict off CAL's own aggregation receipt."""
    agg = trace.parent_aggregation
    verdict = trace.verdict.support_verdict

    # Group atoms by the degree CAL gave them, so the detail line can never
    # claim "none are supported" while a supported atom sits in the list.
    by_degree: dict[str, list[str]] = {}
    for atom in trace.atom_audits:
        by_degree.setdefault(atom.audit_trace.verdict.support_verdict, []).append(atom.claim_text)

    parts = [
        f"{degree}: {len(texts)} ({'; '.join(texts)})"
        for degree, texts in sorted(by_degree.items())
    ]

    return {
        # CAL's own rule id is the reason code. No parallel vocabulary.
        "reason_code": agg.rule_id,
        "verdict": verdict,
        "detail": agg.reason,
        "atom_breakdown": parts,
        "provenance": [f"{agg.rule_id}: {agg.reason}"],
        "triage_color": _COLOR_BY_VERDICT.get(verdict, "amber"),
        "triage_label": _LABEL_BY_VERDICT.get(verdict, "REVIEW"),
        "triage_action": _routing(verdict),
        "routing": _routing(verdict),
    }


_LABEL_BY_VERDICT: dict[str, str] = {
    "supported": "SUPPORTED",
    "partially_supported": "PARTIAL",
    "not_checkable": "NOT ESTABLISHED",
    "unsupported": "LEANS AGAINST",
    "contradicted": "ADVERSE",
}


def _routing(verdict: str) -> str:
    """What a human still has to do. Never an accept/reject instruction."""
    if verdict == "supported":
        return (
            "CAL found the supplied evidence sufficient. Acceptance remains an operator decision."
        )
    if verdict == "contradicted":
        return (
            "Adverse finding against the supplied record. Review the cited passage before acting."
        )
    if verdict == "partially_supported":
        return "Some declared parts are evidenced and some are not. Review the unevidenced parts."
    if verdict == "unsupported":
        return "Evidence was read and leans against the claim. Review the cited passage."
    return "CAL did not establish support either way. Human judgement required."


def derive_reason(
    trace: AuditTrace | ExplicitClaimTrace,
    config: AuditConfig | None = None,
) -> dict[str, Any]:
    """Explain a verdict using only what CAL recorded when it produced it.

    ``config`` supplies the pinned thresholds quoted in operator text. It is
    optional so callers holding only a trace still get a correct reason; the
    numeric gloss is simply omitted rather than guessed.
    """
    if isinstance(trace, ExplicitClaimTrace):
        return _explicit_reason(trace)

    verdict = trace.verdict.support_verdict
    provenance = _rule_provenance(trace.rules_fired)

    if verdict == "not_checkable":
        reason_key = trace.verdict.support_verdict_reason or "no_entail_signal"
        code, template = _ABSTENTION_GLOSS.get(
            reason_key,
            ("NOT_ESTABLISHED", "CAL did not establish support; reason code {reason}."),
        )
        floor = config.retrieval_floor if config is not None else float("nan")
        detail = template.format(floor=floor, reason=reason_key)
    elif verdict == "contradicted":
        code = "CONTRADICTED"
        detail = "The rules layer resolved an admitted passage as refuting the claim."
    elif verdict == "supported":
        code = "SUPPORTED"
        detail = "The rules layer resolved an admitted passage as entailing the claim."
    elif verdict == "partially_supported":
        code = "PARTIALLY_SUPPORTED"
        detail = "Support was established for part of the claim only."
    else:
        code = "UNSUPPORTED"
        detail = "Evidence was admitted and read, and it leans against the claim."

    return {
        "reason_code": code,
        "verdict": verdict,
        "detail": detail,
        "audit_flags": list(trace.verdict.audit_flags),
        "provenance": provenance,
        "triage_color": _COLOR_BY_VERDICT.get(verdict, "amber"),
        "triage_label": _LABEL_BY_VERDICT.get(verdict, "REVIEW"),
        "triage_action": _routing(verdict),
        "routing": _routing(verdict),
    }
