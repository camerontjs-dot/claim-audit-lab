"""Frozen deterministic audit policy for Claim Audit Lab v0.2."""

from __future__ import annotations

from dataclasses import dataclass

from claim_audit_lab.contracts.cb_models import CBAuditConfig


@dataclass(frozen=True)
class AuditPolicy:
    """Binding thresholds and switches for deterministic claim assessment."""

    config_id: str = "cal-rules-v1.2.0"
    candidate_admission: float = 0.40
    partial_support: float = 0.55
    sourced_support: float = 0.80
    counterevidence_weight: float = 0.30
    false_caution_detection: bool = True
    false_caution_threshold: float = 0.85
    overstated_detection: bool = True
    needs_source_detection: bool = True
    require_passage_level_match: bool = True


CAL_RULES_V1_2_0 = AuditPolicy()


def audit_policy_drift(config: CBAuditConfig) -> list[str]:
    """Return field-level differences from the only supported v0.2 C-B policy."""
    expected = CAL_RULES_V1_2_0
    actual_values: dict[str, object] = {
        "config_id": config.config_id,
        "scoring.support_threshold_sourced": config.scoring.support_threshold_sourced,
        "scoring.support_threshold_partial": config.scoring.support_threshold_partial,
        "scoring.counterevidence_weight": config.scoring.counterevidence_weight,
        "rule_policies.require_passage_level_match": (
            config.rule_policies.require_passage_level_match
        ),
        "rule_policies.flag_unsupported_threshold": (
            config.rule_policies.flag_unsupported_threshold
        ),
        "rule_policies.false_caution_detection": (config.rule_policies.false_caution_detection),
        "rule_policies.false_caution_threshold": (config.rule_policies.false_caution_threshold),
        "rule_policies.overstated_detection": config.rule_policies.overstated_detection,
        "rule_policies.needs_source_detection": config.rule_policies.needs_source_detection,
    }
    expected_values: dict[str, object] = {
        "config_id": expected.config_id,
        "scoring.support_threshold_sourced": expected.sourced_support,
        "scoring.support_threshold_partial": expected.partial_support,
        "scoring.counterevidence_weight": expected.counterevidence_weight,
        "rule_policies.require_passage_level_match": expected.require_passage_level_match,
        "rule_policies.flag_unsupported_threshold": expected.candidate_admission,
        "rule_policies.false_caution_detection": expected.false_caution_detection,
        "rule_policies.false_caution_threshold": expected.false_caution_threshold,
        "rule_policies.overstated_detection": expected.overstated_detection,
        "rule_policies.needs_source_detection": expected.needs_source_detection,
    }
    return [
        f"{field}: expected {expected_values[field]!r}, got {actual!r}"
        for field, actual in actual_values.items()
        if actual != expected_values[field]
    ]


__all__ = ["AuditPolicy", "CAL_RULES_V1_2_0", "audit_policy_drift"]
