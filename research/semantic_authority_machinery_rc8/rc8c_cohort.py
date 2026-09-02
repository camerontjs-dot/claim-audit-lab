from __future__ import annotations

from copy import deepcopy

from .rc8b_heldout_cohort import base_case


def build_rc8c_cases() -> list[dict[str, object]]:
    positive = deepcopy(base_case())
    positive["case_id"] = "C-ANCHOR-POSITIVE"
    positive["mutation_axis"] = "evidence_anchor_positive"
    positive["expected_authority"] = "WARRANTED"
    positive["expected_reason"] = "ALL_REQUIRED_WARRANT_ESTABLISHED"

    substituted = deepcopy(positive)
    substituted["case_id"] = "C-ANCHOR-SOURCE-SUBSTITUTED"
    substituted["mutation_axis"] = "raw_source_id_substitution_only"
    substituted["raw_source_id"] = "source:prospective:beta"
    substituted["expected_authority"] = "REJECTED"
    substituted["expected_reason"] = "AUTHORITY_EVIDENCE_SOURCE_MISMATCH"

    missing = deepcopy(positive)
    missing["case_id"] = "C-ANCHOR-SOURCE-MISSING"
    missing["mutation_axis"] = "raw_source_id_missing_with_admitted_evidence"
    missing.pop("raw_source_id")
    missing["expected_authority"] = "UNRESOLVED"
    missing["expected_reason"] = "AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED"

    return [positive, substituted, missing]
