"""Frozen RC2-D rule-family attribution and multiplicity sweep.

The probe imports production CAL only to observe the frozen v0.2 behavior and run
causal interventions. Receipt validation is delegated to ``validator.py``, which
imports no CAL production implementation.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict, replace
from datetime import date as Date
from pathlib import Path
from typing import Any

from claim_audit_lab.models import Claim, EvidenceBundle, EvidenceCandidate, EvidenceExcerpt, EvidenceSource
from claim_audit_lab.policy import CAL_RULES_V1_2_0, AuditPolicy
from claim_audit_lab.rules import assess_claim_support

from research_contract_c_rc2_d.validator import (
    RECEIPT_MARKER,
    REQUIRED_ASSESSMENTS,
    policy_hash as independent_policy_hash,
    validate_receipt,
    validate_suite,
)

PRODUCTION_SHA = "33a928db97316a3652d57df9cafb8ca240305233"
RESEARCH_BASE_SHA = "18592eef336ffc7c2b6b34d8ac489843f5274583"
RULE_VECTOR_BLOB = "ed42acb8c21843676028ccd8c2b9ecc776ad2154"
RULES_BLOB = "4e2c7ebb1a7866d941fc2570757e64098359413a"
POLICY_BLOB = "cdd7c248b50660c0d2ed93db0f351e3c0630f67f"
EXPECTED_POLICY_HASH = "88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d"
OUT_PATH = Path("build/research/contract-c-rc2-d/attribution-sweep.json")


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def policy_object(policy: AuditPolicy) -> dict[str, Any]:
    return asdict(policy)


def policy_hash(policy: AuditPolicy) -> str:
    return sha256_bytes(canonical_bytes(policy_object(policy)))


def _source(
    source_id: str,
    excerpt_id: str,
    text: str,
    *,
    reliability: str = "high",
) -> EvidenceSource:
    return EvidenceSource(
        id=source_id,
        title=f"Fictional {source_id}",
        reliability=reliability,
        date=Date(2026, 1, 1),
        url=f"https://example.com/{source_id}",
        excerpts=[EvidenceExcerpt(id=excerpt_id, text=text)],
    )


def _candidate(
    source_id: str,
    excerpt_id: str,
    score: float,
    *,
    reliability: str = "high",
) -> EvidenceCandidate:
    return EvidenceCandidate(
        source_id=source_id,
        excerpt_id=excerpt_id,
        score=score,
        source_reliability=reliability,
        source_date=Date(2026, 1, 1),
        source_url=f"https://example.com/{source_id}",
    )


def _eref(candidate: EvidenceCandidate) -> str:
    return f"evidence:{candidate.source_id}:{candidate.excerpt_id}"


def _terminal_branch(verdict: str, support_signal: float | None, policy: AuditPolicy) -> str:
    if verdict == "not_checkable":
        return "unclassified_early_return"
    if verdict == "needs_source":
        return "needs_source_rule_family"
    if verdict == "overstated":
        return "overstated_rule_family"
    if verdict == "unsupported":
        return "support_below_partial_threshold"
    if verdict == "partially_supported":
        if support_signal is not None and support_signal < policy.sourced_support:
            return "support_between_thresholds"
        return "residual_or_counter_limit_branch"
    if verdict == "supported":
        return "supported_score_branch"
    return f"other:{verdict}"


def _observe(
    claim: Claim,
    bundle: EvidenceBundle,
    support: list[EvidenceCandidate],
    *,
    counters: list[EvidenceCandidate] | None = None,
    policy: AuditPolicy = CAL_RULES_V1_2_0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    assessment = assess_claim_support(
        claim,
        bundle,
        support,
        counterevidence=counters or [],
        policy=policy,
    )
    outcome = {
        "final_verdict": assessment.support_label,
        "terminal_branch": _terminal_branch(
            assessment.support_label,
            assessment.support_signal,
            policy,
        ),
        "support_signal": assessment.support_signal,
        "rule_codes": sorted(flag.code for flag in assessment.rule_flags),
        "rule_ids": sorted(flag.id for flag in assessment.rule_flags),
    }
    return outcome, assessment.model_dump(mode="json")


def _generic_assessments() -> dict[str, dict[str, str]]:
    return {name: {"state": "not_performed"} for name in REQUIRED_ASSESSMENTS}


def _rule_rows(outcome: dict[str, Any], roles: dict[str, str]) -> list[dict[str, str]]:
    return [
        {"code": code, "terminal_role": roles.get(code, "present")}
        for code in outcome["rule_codes"]
    ]


def _receipt(
    *,
    family_id: str,
    vector_source: str,
    baseline: dict[str, Any],
    mutations: dict[str, dict[str, Any]],
    causal_claim: dict[str, Any],
    input_state: list[dict[str, Any]],
    trigger_state: list[dict[str, Any]],
    rule_roles: dict[str, str],
    dependency_edges: list[dict[str, str]],
    co_maximal_support_refs: list[str] | None = None,
    residual_non_deciding: list[str] | None = None,
    policy: AuditPolicy = CAL_RULES_V1_2_0,
) -> dict[str, Any]:
    return {
        "research_receipt": RECEIPT_MARKER,
        "family_id": family_id,
        "vector_source": vector_source,
        "execution": {
            "production_semantic_sha": PRODUCTION_SHA,
            "rule_vector_blob": RULE_VECTOR_BLOB,
        },
        "policy": {
            "config_id": policy.config_id,
            "canonical": policy_object(policy),
            "sha256": policy_hash(policy),
        },
        "input_state": input_state,
        "trigger_state": trigger_state,
        "rule_results": _rule_rows(baseline, rule_roles),
        "dependency_edges": dependency_edges,
        "generic_assessments": _generic_assessments(),
        "baseline": baseline,
        "mutation_observations": mutations,
        "causal_claim": causal_claim,
        "co_maximal_support_refs": co_maximal_support_refs or [],
        "residual_non_deciding": residual_non_deciding or [],
    }


def _threshold_case() -> tuple[dict[str, Any], bool, str]:
    text = "The tool can generate audit summaries."
    claim = Claim(id="threshold-claim", text=text, claim_type="capability")
    source = _source("source-a", "excerpt-a", text)
    candidate = _candidate("source-a", "excerpt-a", 0.80)
    bundle = EvidenceBundle(sources=[source])

    baseline, baseline_dump = _observe(claim, bundle, [candidate])
    removed, _ = _observe(claim, bundle, [])

    unrelated = _source(
        "source-irrelevant",
        "excerpt-irrelevant",
        "A separate note describes report formatting.",
    )
    irrelevant_bundle = EvidenceBundle(sources=[source, unrelated])
    irrelevant, irrelevant_dump = _observe(claim, irrelevant_bundle, [candidate])
    irrelevant_ref = "evidence:source-irrelevant:excerpt-irrelevant"

    evidence_ref = _eref(candidate)
    receipt = _receipt(
        family_id="threshold_no_rule",
        vector_source="test_frozen_support_threshold_boundaries[sourced]",
        baseline=baseline,
        mutations={"remove_candidate": removed, "add_irrelevant_world_state": irrelevant},
        causal_claim={
            "classification": "single_necessary",
            "target_verdict": baseline["final_verdict"],
            "members": [evidence_ref],
            "removal_mutation": "remove_candidate",
        },
        input_state=[{"id": evidence_ref, "score": 0.80, "candidate": True}],
        trigger_state=[
            {
                "id": "state:support_signal_max",
                "value": 0.80,
                "sourced_support_threshold": 0.80,
            }
        ],
        rule_roles={},
        dependency_edges=[
            {
                "from": evidence_ref,
                "to": "state:support_signal_max",
                "relation": "determines_scalar_max",
            },
            {
                "from": "state:support_signal_max",
                "to": "terminal:supported_score_branch",
                "relation": "crosses_sourced_threshold",
            },
        ],
    )
    invariant = baseline_dump == irrelevant_dump
    falsely_causal = any(
        edge.get("from") == irrelevant_ref for edge in receipt["dependency_edges"]
    )
    return receipt, invariant and not falsely_causal, irrelevant_ref


def _credential_case() -> tuple[dict[str, Any], dict[str, Any]]:
    claim_text = "The reviewer is a licensed sterile manufacturing specialist."
    claim = Claim(id="credential-claim", text=claim_text, claim_type="credential")
    unrelated = _source("source-unrelated", "excerpt-unrelated", "The reviewer works on audit notes.")
    baseline_bundle = EvidenceBundle(sources=[unrelated])
    baseline, _ = _observe(claim, baseline_bundle, [])

    direct_source = _source("source-direct", "excerpt-direct", claim_text)
    direct_candidate = _candidate("source-direct", "excerpt-direct", 0.90)
    direct_bundle = EvidenceBundle(sources=[unrelated, direct_source])
    direct, _ = _observe(claim, direct_bundle, [direct_candidate])

    mutated_policy = replace(CAL_RULES_V1_2_0, needs_source_detection=False)
    policy_off, _ = _observe(claim, baseline_bundle, [], policy=mutated_policy)

    member = "state:direct_contexts_empty"
    receipt = _receipt(
        family_id="credential_needs_source",
        vector_source="test_credential_claim_without_source_needs_source",
        baseline=baseline,
        mutations={"add_direct_support": direct, "same_config_policy_off": policy_off},
        causal_claim={
            "classification": "single_necessary",
            "target_verdict": baseline["final_verdict"],
            "members": [member],
            "removal_mutation": "add_direct_support",
        },
        input_state=[
            {"id": "state:claim_type_credential", "value": True},
            {"id": member, "value": True},
        ],
        trigger_state=[
            {
                "id": "trigger:credential_missing_source",
                "claim_type_credential": True,
                "direct_contexts_empty": True,
                "needs_source_detection": True,
                "result": True,
            }
        ],
        rule_roles={"credential_missing_source": "causal_to_needs_source_override"},
        dependency_edges=[
            {
                "from": member,
                "to": "rule:credential_missing_source",
                "relation": "causes_rule_emission_under_fixed_claim_type_policy",
            },
            {
                "from": "rule:credential_missing_source",
                "to": "terminal:needs_source_rule_family",
                "relation": "causes_priority_override",
            },
        ],
    )
    control = {
        "mutated_policy": mutated_policy,
        "mutated_outcome": policy_off,
        "baseline_outcome": baseline,
    }
    return receipt, control


def _low_reliability_case() -> dict[str, Any]:
    text = "The tool can generate audit summaries."
    claim = Claim(id="low-rel-claim", text=text, claim_type="capability")
    low_source = _source("source-low", "excerpt-low", text, reliability="low")
    low_candidate = _candidate("source-low", "excerpt-low", 0.60, reliability="low")
    low_bundle = EvidenceBundle(sources=[low_source])
    baseline, _ = _observe(claim, low_bundle, [low_candidate])

    high_source = _source("source-low", "excerpt-low", text, reliability="high")
    high_candidate = _candidate("source-low", "excerpt-low", 0.60, reliability="high")
    high_bundle = EvidenceBundle(sources=[high_source])
    reliability_removed, _ = _observe(claim, high_bundle, [high_candidate])

    residual = "rule:low_reliability_only"
    return _receipt(
        family_id="low_reliability_residual",
        vector_source="test_low_reliability_only_support_lowers_assessment + score=0.60 mutation",
        baseline=baseline,
        mutations={"remove_low_reliability_state": reliability_removed},
        causal_claim={
            "classification": "redundant_non_deciding",
            "target_verdict": baseline["final_verdict"],
            "members": [residual],
            "removal_mutation": "remove_low_reliability_state",
        },
        input_state=[
            {"id": "evidence:source-low:excerpt-low", "score": 0.60},
            {"id": "state:all_direct_support_low_or_unknown", "value": True},
        ],
        trigger_state=[
            {
                "id": "trigger:low_reliability_only",
                "all_direct_support_low_or_unknown": True,
                "result": True,
            },
            {
                "id": "state:support_signal_max",
                "value": 0.60,
                "partial_support_threshold": 0.55,
                "sourced_support_threshold": 0.80,
            },
        ],
        rule_roles={"low_reliability_only": "residual_under_threshold_branch"},
        dependency_edges=[
            {
                "from": "evidence:source-low:excerpt-low",
                "to": "state:support_signal_max",
                "relation": "determines_scalar_max",
            },
            {
                "from": "state:support_signal_max",
                "to": "terminal:support_between_thresholds",
                "relation": "causes_threshold_branch",
            },
            {
                "from": "state:all_direct_support_low_or_unknown",
                "to": residual,
                "relation": "causes_rule_emission",
            },
            {
                "from": residual,
                "to": "terminal:support_between_thresholds",
                "relation": "residual_after_preceding_threshold",
            },
        ],
        residual_non_deciding=[residual],
    )


def _unclassified_case() -> dict[str, Any]:
    text = "The report describes the pilot."
    claim = Claim(id="unclassified-claim", text=text, claim_type="unclassified")
    bundle = EvidenceBundle()
    baseline, _ = _observe(claim, bundle, [])

    governed_claim = Claim(id="unclassified-claim", text=text, claim_type="capability")
    governed, _ = _observe(governed_claim, bundle, [])

    member = "state:claim_type_unclassified"
    return _receipt(
        family_id="unclassified_not_checkable",
        vector_source="test_unclassified_claim_is_not_checkable",
        baseline=baseline,
        mutations={"change_to_governed_claim_type": governed},
        causal_claim={
            "classification": "single_necessary",
            "target_verdict": baseline["final_verdict"],
            "members": [member],
            "removal_mutation": "change_to_governed_claim_type",
        },
        input_state=[{"id": member, "value": True}],
        trigger_state=[
            {
                "id": "trigger:unclassified_early_return",
                "claim_type_unclassified": True,
                "result": True,
            }
        ],
        rule_roles={},
        dependency_edges=[
            {
                "from": member,
                "to": "terminal:unclassified_early_return",
                "relation": "causes_early_return",
            }
        ],
    )


def _absolute_joint_case() -> tuple[dict[str, Any], dict[str, Any]]:
    evidence_text = "The tool guarantees audit summaries."
    source = _source("source-abs", "excerpt-abs", evidence_text)
    support = _candidate("source-abs", "excerpt-abs", 1.0)
    counter = _candidate("source-abs", "excerpt-abs", 0.5)
    bundle = EvidenceBundle(sources=[source])

    lexical_claim = Claim(
        id="absolute-claim",
        text="The tool guarantees audit summaries.",
        claim_type="prediction",
    )
    nonlexical_claim = Claim(
        id="absolute-claim",
        text="The tool can generate audit summaries.",
        claim_type="prediction",
    )

    baseline, _ = _observe(lexical_claim, bundle, [support], counters=[counter])
    lexical_only, _ = _observe(lexical_claim, bundle, [support], counters=[])
    counter_only, _ = _observe(nonlexical_claim, bundle, [support], counters=[counter])
    neither, _ = _observe(nonlexical_claim, bundle, [support], counters=[])

    mutated_policy = replace(CAL_RULES_V1_2_0, overstated_detection=False)
    policy_off, _ = _observe(
        lexical_claim,
        bundle,
        [support],
        counters=[counter],
        policy=mutated_policy,
    )

    lexical = "state:absolute_lexical_trigger"
    counter_state = "state:counterevidence_contexts_nonempty"
    residual = "rule:counterevidence_present"
    causal_rules = {"future_certainty", "overconfident_wording"}
    edges: list[dict[str, str]] = []
    for code in sorted(causal_rules):
        edges.extend(
            [
                {
                    "from": lexical,
                    "to": f"rule:{code}",
                    "relation": "required_lexical_trigger",
                },
                {
                    "from": counter_state,
                    "to": f"rule:{code}",
                    "relation": "causes_absolute_wording_trigger_true",
                },
                {
                    "from": f"rule:{code}",
                    "to": "terminal:overstated_rule_family",
                    "relation": "sufficient_rule_for_terminal_family",
                },
            ]
        )

    receipt = _receipt(
        family_id="absolute_wording_joint",
        vector_source="test_linked_counterevidence_restores_absolute_wording_flags / CAL #21 seam",
        baseline=baseline,
        mutations={
            "lexical_only": lexical_only,
            "counter_only": counter_only,
            "neither": neither,
            "same_config_policy_off": policy_off,
        },
        causal_claim={
            "classification": "jointly_sufficient",
            "target_verdict": baseline["final_verdict"],
            "members": [lexical, counter_state],
            "isolated_mutations": {
                lexical: "lexical_only",
                counter_state: "counter_only",
            },
            "none_mutation": "neither",
        },
        input_state=[
            {"id": lexical, "value": True},
            {"id": counter_state, "value": True, "counterevidence_count": 1},
            {"id": "evidence:source-abs:excerpt-abs", "support_score": 1.0},
        ],
        trigger_state=[
            {
                "id": "trigger:absolute_wording",
                "lexical_trigger": "guarantees",
                "counterevidence_contexts_nonempty": True,
                "policy_overstated_detection": True,
                "result": True,
            }
        ],
        rule_roles={
            "future_certainty": "causal_to_overstated_branch",
            "overconfident_wording": "causal_to_overstated_branch",
            "counterevidence_present": "residual_after_overstated_branch",
        },
        dependency_edges=edges,
        residual_non_deciding=[residual],
    )
    control = {
        "mutated_policy": mutated_policy,
        "mutated_outcome": policy_off,
        "baseline_outcome": baseline,
    }
    return receipt, control


def _tied_independent_case() -> dict[str, Any]:
    text = "The tool can generate audit summaries."
    claim = Claim(id="tie-claim", text=text, claim_type="capability")
    source_a = _source("source-tie-a", "excerpt-tie-a", text)
    source_b = _source("source-tie-b", "excerpt-tie-b", text)
    candidate_a = _candidate("source-tie-a", "excerpt-tie-a", 0.80)
    candidate_b = _candidate("source-tie-b", "excerpt-tie-b", 0.80)
    bundle = EvidenceBundle(sources=[source_a, source_b])

    both, _ = _observe(claim, bundle, [candidate_a, candidate_b])
    a_only, _ = _observe(claim, bundle, [candidate_a])
    b_only, _ = _observe(claim, bundle, [candidate_b])
    neither, _ = _observe(claim, bundle, [])

    ref_a = _eref(candidate_a)
    ref_b = _eref(candidate_b)
    members = [ref_a, ref_b]
    return _receipt(
        family_id="tied_independent_support",
        vector_source="test_frozen_support_threshold_boundaries[sourced] + frozen two-source tie perturbation",
        baseline=both,
        mutations={"a_only": a_only, "b_only": b_only, "neither": neither},
        causal_claim={
            "classification": "independent_sufficient_alternatives",
            "target_verdict": both["final_verdict"],
            "members": members,
            "isolated_mutations": {ref_a: "a_only", ref_b: "b_only"},
            "none_mutation": "neither",
        },
        input_state=[
            {"id": ref_a, "score": 0.80, "scalar_co_maximal": True},
            {"id": ref_b, "score": 0.80, "scalar_co_maximal": True},
        ],
        trigger_state=[
            {
                "id": "state:support_signal_max",
                "value": 0.80,
                "sourced_support_threshold": 0.80,
                "co_maximal_count": 2,
            }
        ],
        rule_roles={},
        dependency_edges=[
            {
                "from": ref_a,
                "to": "state:support_signal_max",
                "relation": "co_maximal_scalar_contributor",
            },
            {
                "from": ref_b,
                "to": "state:support_signal_max",
                "relation": "co_maximal_scalar_contributor",
            },
            {
                "from": "state:support_signal_max",
                "to": "terminal:supported_score_branch",
                "relation": "crosses_sourced_threshold",
            },
        ],
        co_maximal_support_refs=members,
    )


def run_sweep() -> dict[str, Any]:
    if policy_hash(CAL_RULES_V1_2_0) != EXPECTED_POLICY_HASH:
        raise AssertionError("frozen production policy hash drifted")
    if independent_policy_hash(policy_object(CAL_RULES_V1_2_0)) != EXPECTED_POLICY_HASH:
        raise AssertionError("independent policy hashing disagrees with frozen identity")

    threshold, irrelevant_ok, irrelevant_ref = _threshold_case()
    credential, credential_policy = _credential_case()
    low_reliability = _low_reliability_case()
    unclassified = _unclassified_case()
    absolute, absolute_policy = _absolute_joint_case()
    tied = _tied_independent_case()
    receipts = [threshold, credential, low_reliability, unclassified, absolute, tied]

    suite = {
        "experiment": "contract-c-rc2-d-rule-family-attribution",
        "pins": {
            "production_semantic_sha": PRODUCTION_SHA,
            "research_base_sha": RESEARCH_BASE_SHA,
            "rule_vector_blob": RULE_VECTOR_BLOB,
            "rules_blob": RULES_BLOB,
            "policy_blob": POLICY_BLOB,
            "policy_sha256": EXPECTED_POLICY_HASH,
        },
        "receipts": receipts,
    }
    suite_errors = validate_suite(suite)

    missing_assessment = copy.deepcopy(threshold)
    del missing_assessment["generic_assessments"]["citation"]
    missing_assessment_errors = validate_receipt(missing_assessment)

    missing_edges = copy.deepcopy(credential)
    missing_edges["dependency_edges"] = []
    missing_edge_errors = validate_receipt(missing_edges)

    false_joint = copy.deepcopy(tied)
    false_joint["causal_claim"]["classification"] = "jointly_sufficient"
    false_joint_errors = validate_receipt(false_joint)

    false_independent = copy.deepcopy(absolute)
    false_independent["causal_claim"]["classification"] = "independent_sufficient_alternatives"
    false_independent["co_maximal_support_refs"] = list(false_independent["causal_claim"]["members"])
    false_independent_errors = validate_receipt(false_independent)

    bad_policy_binding = copy.deepcopy(absolute)
    mutated_policy = absolute_policy["mutated_policy"]
    bad_policy_binding["policy"]["canonical"] = policy_object(mutated_policy)
    bad_policy_binding_errors = validate_receipt(bad_policy_binding)

    credential_mutated_policy = credential_policy["mutated_policy"]
    policy_controls = {
        "credential": {
            "config_id_unchanged": credential_mutated_policy.config_id == CAL_RULES_V1_2_0.config_id,
            "hash_changed": policy_hash(credential_mutated_policy) != EXPECTED_POLICY_HASH,
            "behavior_changed": credential_policy["mutated_outcome"]["final_verdict"]
            != credential_policy["baseline_outcome"]["final_verdict"],
        },
        "absolute_wording": {
            "config_id_unchanged": mutated_policy.config_id == CAL_RULES_V1_2_0.config_id,
            "hash_changed": policy_hash(mutated_policy) != EXPECTED_POLICY_HASH,
            "behavior_changed": absolute_policy["mutated_outcome"]["final_verdict"]
            != absolute_policy["baseline_outcome"]["final_verdict"],
        },
    }

    controls = {
        "suite_validates": not suite_errors,
        "missing_generic_assessment_fails_closed": bool(missing_assessment_errors),
        "missing_dependency_edges_fail_closed": bool(missing_edge_errors),
        "false_joint_theory_rejected": bool(false_joint_errors),
        "false_independent_theory_rejected": bool(false_independent_errors),
        "same_config_policy_mutations_change_hash_and_behavior": all(
            all(row.values()) for row in policy_controls.values()
        ),
        "policy_hash_mismatch_fails_closed": bool(bad_policy_binding_errors),
        "irrelevant_evidence_world_state_is_output_invariant_and_noncausal": irrelevant_ok,
        "all_generic_assessments_explicit_not_performed": all(
            all(
                receipt["generic_assessments"][name]["state"] == "not_performed"
                for name in REQUIRED_ASSESSMENTS
            )
            for receipt in receipts
        ),
        "tied_co_maxima_preserved": sorted(tied["co_maximal_support_refs"])
        == sorted(tied["causal_claim"]["members"]),
    }

    result = {
        **suite,
        "controls": controls,
        "control_details": {
            "suite_validation_errors": suite_errors,
            "missing_generic_assessment_errors": missing_assessment_errors,
            "missing_dependency_edge_errors": missing_edge_errors,
            "false_joint_errors": false_joint_errors,
            "false_independent_errors": false_independent_errors,
            "bad_policy_binding_errors": bad_policy_binding_errors,
            "policy_mutations": {
                name: {
                    "config_id_unchanged": row["config_id_unchanged"],
                    "hash_changed": row["hash_changed"],
                    "behavior_changed": row["behavior_changed"],
                }
                for name, row in policy_controls.items()
            },
            "irrelevant_evidence_ref": irrelevant_ref,
        },
        "available_multiplicity_shapes": {
            "single_necessary": ["threshold_no_rule", "credential_needs_source", "unclassified_not_checkable"],
            "independent_sufficient_alternatives": ["tied_independent_support"],
            "jointly_sufficient": ["absolute_wording_joint"],
            "redundant_non_deciding": ["low_reliability_residual"],
            "co_maximal_tied": ["tied_independent_support"],
        },
        "unavailable_requested_shapes": [],
        "falsified_simpler_theories": [
            "terminal branch replay alone establishes causal contribution",
            "two present contributors may be encoded as jointly necessary without interventions",
            "jointly required contributors may be encoded as independent alternatives",
            "one arbitrary scalar winner is sufficient when tied co-maxima exist",
            "an emitted residual rule is necessarily causal to the terminal branch",
            "config_id alone is sufficient policy identity",
        ],
        "bounds": {
            "production_change": False,
            "contract_c_version": False,
            "consumer_b_run": False,
            "decision_engine_change": False,
            "contract_b_change": False,
        },
    }
    result["all_controls_passed"] = all(controls.values())
    return result


def main() -> int:
    result = run_sweep()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(canonical_bytes(result))
    print(json.dumps({
        "all_controls_passed": result["all_controls_passed"],
        "controls": result["controls"],
        "families": [receipt["family_id"] for receipt in result["receipts"]],
        "artifact": str(OUT_PATH),
    }, indent=2, sort_keys=True))
    return 0 if result["all_controls_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
