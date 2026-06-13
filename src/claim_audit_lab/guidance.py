"""Deterministic rewrite guidance derived from assessment outcomes."""

from __future__ import annotations

from claim_audit_lab.models import RuleFlag, SupportLabel


def build_rewrite_guidance(
    support_label: SupportLabel,
    flags: list[RuleFlag],
) -> list[str]:
    """Return stable, actionable rewrite guidance for one assessment."""
    guidance: list[str] = []
    codes = {flag.code for flag in flags}
    if "numeric_mismatch" in codes:
        guidance.append("Correct the number or supply evidence with the matching value.")
    if "causal_overreach" in codes:
        guidance.append(
            "Use weaker causal wording unless the supplied evidence directly supports causality."
        )
    if "comparison_missing" in codes:
        guidance.append("Name the comparison evidence or soften the comparative claim.")
    if "credential_missing_source" in codes:
        guidance.append("Add a supplied credential source before keeping this credential claim.")
    if "public_link_missing_source" in codes:
        guidance.append("Add supplied URL metadata before keeping this public-link claim.")
    if "overconfident_wording" in codes:
        guidance.append("Replace absolute wording with bounded supplied-evidence language.")
    if "future_certainty" in codes:
        guidance.append(
            "Avoid universal future wording; state only what the supplied evidence covers."
        )
    if "scope_overreach" in codes:
        guidance.append("Narrow the scope to the observed source, fixture, sample, or setting.")
    if "low_reliability_only" in codes:
        guidance.append(
            "Caveat the claim because direct support comes from weak source reliability."
        )
    if "stale_source" in codes:
        guidance.append("Use newer supplied evidence or add a freshness caveat.")
    if "date_missing_support" in codes:
        guidance.append("Add matching date evidence or remove the unsupported date detail.")
    if "counterevidence_present" in codes:
        guidance.append("Address the linked counterevidence or narrow the claim around it.")

    if support_label == "unsupported" and not guidance:
        guidance.append("Remove the claim or add supplied evidence that directly supports it.")
    if support_label == "needs_source" and not guidance:
        guidance.append("Add a supplied source before presenting this claim.")
    if support_label == "overstated" and not guidance:
        guidance.append("Narrow the claim until it matches the supplied evidence.")
    if support_label == "partially_supported" and not guidance:
        guidance.append("Keep the supported part and caveat the unsupported part.")

    return guidance


__all__ = ["build_rewrite_guidance"]
