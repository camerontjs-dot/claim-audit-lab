"""Preregistered RC1 consumer probes over the candidate package.

These are research policies, not CAL semantics and not production decisions.
Their purpose is field-family ablation: expose what information a materially
plural consumer set actually loses.
"""

from __future__ import annotations

from typing import Any, Callable


class InsufficientPackage(ValueError):
    pass


def _need(package: dict[str, Any], *families: str) -> None:
    missing = [family for family in families if family not in package]
    if missing:
        raise InsufficientPackage("missing: " + ", ".join(missing))


def publication_probe(package: dict[str, Any]) -> str:
    _need(package, "identity", "evidence", "assessments", "conclusion", "execution")
    if package["execution"]["status"] != "completed":
        return "hold"
    aperture = package["assessments"]["aperture"]
    if aperture["state"] != "performed" or aperture.get("value") in {"unknown", "incomplete"}:
        return "review"
    if package["conclusion"]["residual"]["counterevidence_ids"]:
        return "review"
    verdict = package["conclusion"]["reported_verdict"]
    if verdict == "not_checkable":
        return "review"
    return "publish_review" if verdict == "supported" else "withhold"


def sop_conformance_probe(package: dict[str, Any]) -> str:
    _need(package, "identity", "evidence", "assessments", "conclusion", "execution")
    if package["execution"]["status"] != "completed":
        return "indeterminate_execution"
    for name in ("eligibility", "semantic_validity", "temporal_applicability"):
        item = package["assessments"][name]
        if item["state"] != "performed" or item.get("value") == "unknown":
            return "indeterminate"
    if package["assessments"]["eligibility"].get("value") == "ineligible":
        return "indeterminate_applicability"
    if package["assessments"]["semantic_validity"].get("value") == "invalid":
        return "indeterminate_invalid_evidence"
    temporal = package["assessments"]["temporal_applicability"].get("value")
    if temporal in {"not_applicable", "historical_only"}:
        return "indeterminate_applicability"
    verdict = package["conclusion"]["reported_verdict"]
    if verdict == "supported":
        return "conformance_supported"
    if verdict in {"contradicted", "unsupported"}:
        return "nonconformance_supported"
    return "indeterminate"


def investigation_probe(package: dict[str, Any]) -> str:
    _need(package, "identity", "evidence", "assessments", "conclusion", "reassessment", "execution")
    if package["execution"]["status"] != "completed":
        return "further_investigation_execution"
    if package["conclusion"]["residual"]["unresolved_evidence_ids"]:
        return "further_investigation"
    if package["conclusion"]["residual"]["counterevidence_ids"]:
        return "further_investigation"
    if package["reassessment"].get("relation") in {"recomputed", "superseding"}:
        return "review_lineage"
    return "procedural_decision_ready"


def reconstruction_probe(package: dict[str, Any]) -> str:
    _need(package, "identity", "evidence", "measurements", "assessments", "conclusion", "execution")
    if not package["identity"].get("audit_config_sha256"):
        raise InsufficientPackage("missing audit config identity")
    if not package["measurements"]:
        raise InsufficientPackage("missing semantic measurements")
    return "reconstructable"


def assessment_state_probe(package: dict[str, Any], name: str) -> str:
    _need(package, "assessments")
    if name not in package["assessments"]:
        return "incompatible_absent"
    item = package["assessments"][name]
    state = item.get("state")
    if state == "not_performed":
        return "hold_assessment_required"
    if state == "failed":
        return "hold_execution_failure"
    if state == "not_applicable":
        return "not_applicable"
    if state == "performed" and item.get("value") == "unknown":
        return "hold_unresolved"
    if state == "performed" and item.get("value") in {"invalid", "ineligible"}:
        return "explicit_negative"
    if state == "performed":
        return "performed_value"
    return "incompatible_state"


CONSUMERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "publication": publication_probe,
    "sop_conformance": sop_conformance_probe,
    "investigation": investigation_probe,
    "reconstruction": reconstruction_probe,
}
