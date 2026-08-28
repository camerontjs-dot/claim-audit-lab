"""Research-only RC2-C dependency receipt probe for one frozen v0.2 seam."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import asdict, replace
from datetime import date as Date
from pathlib import Path
from typing import Any

from claim_audit_lab import rules as production_rules
from claim_audit_lab.models import (
    Claim,
    EvidenceBundle,
    EvidenceCandidate,
    EvidenceExcerpt,
    EvidenceSource,
)
from claim_audit_lab.policy import CAL_RULES_V1_2_0, AuditPolicy
from claim_audit_lab.rules import assess_claim_support

from research_contract_c_rc2_c.validator import (
    counterevidence_dependency_codes,
    validate_dependency_receipt,
)

PRODUCTION_SHA = "33a928db97316a3652d57df9cafb8ca240305233"
RESEARCH_BASE_SHA = "18592eef336ffc7c2b6b34d8ac489843f5274583"
RULE_VECTOR_BLOB = "ed42acb8c21843676028ccd8c2b9ecc776ad2154"
RULES_BLOB = "4e2c7ebb1a7866d941fc2570757e64098359413a"
POLICY_BLOB = "cdd7c248b50660c0d2ed93db0f351e3c0630f67f"
EXPECTED_POLICY_HASH = (
    "88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d"
)
SEAM_ID = "rc2-c:absolute-wording-counterevidence"
CLAIM_TEXT = "The tool guarantees audit summaries."
EVIDENCE_TEXT = "The tool guarantees audit summaries."


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


def evidence_ref(candidate: EvidenceCandidate) -> dict[str, str]:
    return {
        "source_id": candidate.source_id,
        "excerpt_id": candidate.excerpt_id,
    }


def _source(
    source_id: str,
    excerpt_id: str,
    text: str,
) -> EvidenceSource:
    return EvidenceSource(
        id=source_id,
        title=f"Fictional {source_id}",
        reliability="high",
        date=Date(2026, 1, 1),
        url=f"https://example.com/{source_id}",
        excerpts=[EvidenceExcerpt(id=excerpt_id, text=text)],
    )


def _candidate(
    source_id: str,
    excerpt_id: str,
    score: float,
) -> EvidenceCandidate:
    return EvidenceCandidate(
        source_id=source_id,
        excerpt_id=excerpt_id,
        score=score,
        source_reliability="high",
        source_date=Date(2026, 1, 1),
        source_url=f"https://example.com/{source_id}",
    )


def frozen_inputs(
    *,
    counterevidence: bool = True,
    irrelevant_support: bool = False,
) -> tuple[Claim, EvidenceBundle, list[EvidenceCandidate], list[EvidenceCandidate]]:
    claim = Claim(id="claim-001", text=CLAIM_TEXT, claim_type="prediction")
    sources = [_source("source-001", "excerpt-001", EVIDENCE_TEXT)]
    support = [_candidate("source-001", "excerpt-001", 1.0)]
    if irrelevant_support:
        sources.append(
            _source(
                "source-irrelevant",
                "excerpt-irrelevant",
                "A separate note describes report formatting.",
            )
        )
        support.append(_candidate("source-irrelevant", "excerpt-irrelevant", 0.41))
    counters = [_candidate("source-001", "excerpt-001", 0.5)] if counterevidence else []
    return claim, EvidenceBundle(sources=sources), support, counters


def _context_ref(context: Any) -> dict[str, str]:
    return evidence_ref(context.candidate)


def _matching_trigger(code: str, claim_text: str) -> str:
    if code == "overconfident_wording":
        patterns = production_rules._OVERCONFIDENT_PATTERNS
    elif code == "future_certainty":
        patterns = production_rules._FUTURE_CERTAINTY_PATTERNS
    else:
        raise ValueError(f"unsupported RC2-C rule code: {code}")
    matches = production_rules._matching_triggers(claim_text, patterns)
    if len(matches) != 1:
        raise AssertionError(f"expected one frozen trigger for {code}, got {matches!r}")
    return matches[0]


def _direct_refs_examined(
    trigger: str,
    direct_contexts: list[Any],
    counter_contexts: list[Any],
) -> list[dict[str, str]]:
    if counter_contexts:
        return []
    normalized_trigger = production_rules.normalize_text(trigger)
    examined: list[dict[str, str]] = []
    for context in direct_contexts:
        examined.append(_context_ref(context))
        text = production_rules.normalize_text(production_rules._evidence_text(context))
        if normalized_trigger in text:
            break
    return examined


def _terminal_branch(verdict: str) -> str:
    if verdict == "overstated":
        return "overstated_rule_family"
    if verdict == "supported":
        return "supported_score_branch"
    if verdict == "partially_supported":
        return "partial_or_residual_branch"
    return f"other:{verdict}"


def build_receipt(
    claim: Claim,
    bundle: EvidenceBundle,
    support: list[EvidenceCandidate],
    counters: list[EvidenceCandidate],
    *,
    policy: AuditPolicy = CAL_RULES_V1_2_0,
) -> dict[str, Any]:
    assessment = assess_claim_support(
        claim,
        bundle,
        support,
        counterevidence=counters,
        policy=policy,
    )
    contexts = production_rules._build_contexts(support, bundle)
    counter_contexts = production_rules._build_contexts(counters, bundle)
    direct_contexts = [
        context
        for context in contexts
        if production_rules._is_direct_support(claim, context)
    ]
    flags_by_code = {flag.code: flag for flag in assessment.rule_flags}
    causal_codes = [
        code
        for code in ("overconfident_wording", "future_certainty")
        if code in flags_by_code
    ]
    counter_state_id = "state:counterevidence_contexts_nonempty"
    claim_trigger_id = "state:claim_trigger:guarantees"
    edges: list[dict[str, str]] = []
    emitted_rules: list[dict[str, Any]] = []
    trigger_conditions: list[dict[str, Any]] = []

    for code in causal_codes:
        trigger = _matching_trigger(code, claim.text)
        trigger_result = production_rules._absolute_wording_needs_flag(
            trigger,
            direct_contexts,
            counter_contexts,
        )
        if not trigger_result:
            raise AssertionError(f"production emitted {code} but trigger evaluated false")
        flag = flags_by_code[code]
        emitted_rules.append(
            {
                "rule_id": flag.id,
                "code": flag.code,
                "risk": flag.risk,
                "result": "emitted",
                "terminal_role": "causal_to_overstated_branch",
            }
        )
        trigger_conditions.append(
            {
                "rule_id": flag.id,
                "code": code,
                "lexical_trigger": trigger,
                "policy_overstated_detection": policy.overstated_detection,
                "counterevidence_contexts_nonempty": bool(counter_contexts),
                "counterevidence_collection_examined": True,
                "individual_counterevidence_payloads_examined": [],
                "available_direct_support_refs": [
                    _context_ref(context) for context in direct_contexts
                ],
                "direct_support_refs_examined_by_trigger": _direct_refs_examined(
                    trigger,
                    direct_contexts,
                    counter_contexts,
                ),
                "trigger_result": True,
            }
        )
        edges.extend(
            [
                {
                    "from": claim_trigger_id,
                    "to": f"rule:{flag.id}",
                    "relation": "required_lexical_trigger",
                },
                {
                    "from": counter_state_id,
                    "to": f"rule:{flag.id}",
                    "relation": "causes_absolute_wording_trigger_true",
                },
            ]
        )

    residual_outputs: list[dict[str, Any]] = []
    counter_flag = flags_by_code.get("counterevidence_present")
    if counter_flag is not None:
        residual_outputs.append(
            {
                "rule_id": counter_flag.id,
                "code": counter_flag.code,
                "result": "emitted",
                "source_state": counter_state_id,
                "terminal_role": (
                    "residual_after_overstated_branch"
                    if assessment.support_label == "overstated"
                    else "may_limit_non_overstated_branch"
                ),
            }
        )

    return {
        "research_receipt": "contract-c-rc2-c-dependency-v0",
        "execution": {
            "seam_id": SEAM_ID,
            "production_semantic_sha": PRODUCTION_SHA,
            "claim_id": claim.id,
            "claim_text_sha256": sha256_bytes(claim.text.encode("utf-8")),
        },
        "policy": {
            "config_id": policy.config_id,
            "canonical": policy_object(policy),
            "sha256": policy_hash(policy),
        },
        "evidence_state": {
            "available_support_refs": [evidence_ref(candidate) for candidate in support],
            "counterevidence_refs_at_trigger": [
                evidence_ref(candidate) for candidate in counters
            ],
            "counterevidence_contexts_nonempty": bool(counters),
        },
        "trigger_conditions": trigger_conditions,
        "emitted_causal_rules": emitted_rules,
        "dependency_edges": edges,
        "terminally_residual_outputs": residual_outputs,
        "terminal": {
            "branch": _terminal_branch(assessment.support_label),
            "final_verdict": assessment.support_label,
            "support_signal": assessment.support_signal,
            "all_rule_codes": sorted(flag.code for flag in assessment.rule_flags),
        },
    }


def run_experiment() -> dict[str, Any]:
    if policy_hash(CAL_RULES_V1_2_0) != EXPECTED_POLICY_HASH:
        raise AssertionError("frozen production policy hash drifted")

    claim, bundle, support, counters = frozen_inputs()
    original_assessment = assess_claim_support(
        claim,
        bundle,
        support,
        counterevidence=counters,
    )
    original_receipt = build_receipt(claim, bundle, support, counters)
    original_errors = validate_dependency_receipt(original_receipt)

    removal_claim, removal_bundle, removal_support, removal_counters = frozen_inputs(
        counterevidence=False
    )
    removal_assessment = assess_claim_support(
        removal_claim,
        removal_bundle,
        removal_support,
        counterevidence=removal_counters,
    )
    removal_receipt = build_receipt(
        removal_claim,
        removal_bundle,
        removal_support,
        removal_counters,
    )
    removal_errors = validate_dependency_receipt(removal_receipt)

    neg_claim, neg_bundle, neg_support, neg_counters = frozen_inputs(
        irrelevant_support=True
    )
    negative_assessment = assess_claim_support(
        neg_claim,
        neg_bundle,
        neg_support,
        counterevidence=neg_counters,
    )
    negative_receipt = build_receipt(
        neg_claim,
        neg_bundle,
        neg_support,
        neg_counters,
    )

    missing_edge = copy.deepcopy(original_receipt)
    missing_edge["dependency_edges"] = [
        edge
        for edge in missing_edge["dependency_edges"]
        if not (
            edge["from"] == "state:counterevidence_contexts_nonempty"
            and edge["relation"] == "causes_absolute_wording_trigger_true"
        )
    ]
    missing_edge_errors = validate_dependency_receipt(missing_edge)

    missing_trigger = copy.deepcopy(original_receipt)
    missing_trigger["trigger_conditions"] = []
    missing_trigger_errors = validate_dependency_receipt(missing_trigger)

    terminal_only = copy.deepcopy(original_receipt)
    terminal_only["dependency_edges"] = []
    terminal_only_codes = counterevidence_dependency_codes(terminal_only)
    full_dependency_codes = counterevidence_dependency_codes(original_receipt)

    policy_mutation = replace(CAL_RULES_V1_2_0, overstated_detection=False)
    policy_mutation_assessment = assess_claim_support(
        claim,
        bundle,
        support,
        counterevidence=counters,
        policy=policy_mutation,
    )

    irrelevant_ref = {
        "source_id": "source-irrelevant",
        "excerpt_id": "excerpt-irrelevant",
    }
    negative_edges = negative_receipt["dependency_edges"]
    irrelevant_falsely_causal = any(
        edge.get("from") == f"evidence:{irrelevant_ref}" for edge in negative_edges
    )

    controls = {
        "original_production_vector": (
            original_assessment.support_label == "overstated"
            and original_assessment.support_signal == 0.85
            and {flag.code for flag in original_assessment.rule_flags}
            == {
                "counterevidence_present",
                "future_certainty",
                "overconfident_wording",
            }
            and not original_errors
        ),
        "causal_removal": (
            removal_assessment.support_label == "supported"
            and removal_assessment.support_signal == 1.0
            and not removal_assessment.rule_flags
            and not removal_receipt["dependency_edges"]
            and not removal_errors
        ),
        "irrelevant_state_negative": (
            negative_assessment.model_dump(mode="json")
            == original_assessment.model_dump(mode="json")
            and not irrelevant_falsely_causal
        ),
        "missing_dependency_fails_closed": bool(missing_edge_errors),
        "missing_trigger_fails_closed": bool(missing_trigger_errors),
        "policy_identity": (
            policy_mutation.config_id == CAL_RULES_V1_2_0.config_id
            and policy_hash(policy_mutation) != EXPECTED_POLICY_HASH
            and policy_mutation_assessment.support_label == "partially_supported"
            and {flag.code for flag in policy_mutation_assessment.rule_flags}
            == {"counterevidence_present"}
        ),
        "causal_attribution_distinction": (
            full_dependency_codes
            == {"future_certainty", "overconfident_wording"}
            and terminal_only_codes is None
        ),
    }

    return {
        "experiment": "contract-c-rc2-c-evidence-rule-dependency",
        "pins": {
            "production_semantic_sha": PRODUCTION_SHA,
            "research_base_sha": RESEARCH_BASE_SHA,
            "rule_vector_blob": RULE_VECTOR_BLOB,
            "rules_blob": RULES_BLOB,
            "policy_blob": POLICY_BLOB,
            "policy_sha256": EXPECTED_POLICY_HASH,
        },
        "original_receipt": original_receipt,
        "causal_removal_receipt": removal_receipt,
        "negative_control": {
            "production_output_unchanged": (
                negative_assessment.model_dump(mode="json")
                == original_assessment.model_dump(mode="json")
            ),
            "unrelated_support_ref": irrelevant_ref,
            "falsely_recorded_causal": irrelevant_falsely_causal,
        },
        "fail_closed": {
            "missing_edge_errors": missing_edge_errors,
            "missing_trigger_errors": missing_trigger_errors,
        },
        "policy_identity_control": {
            "config_id_unchanged": (
                policy_mutation.config_id == CAL_RULES_V1_2_0.config_id
            ),
            "baseline_hash": EXPECTED_POLICY_HASH,
            "mutated_hash": policy_hash(policy_mutation),
            "mutated_overstated_detection": policy_mutation.overstated_detection,
            "mutated_verdict": policy_mutation_assessment.support_label,
            "mutated_rule_codes": sorted(
                flag.code for flag in policy_mutation_assessment.rule_flags
            ),
        },
        "necessity_control": {
            "full_receipt_counterevidence_dependency_codes": sorted(
                full_dependency_codes or set()
            ),
            "terminal_only_counterevidence_dependency_codes": (
                None if terminal_only_codes is None else sorted(terminal_only_codes)
            ),
            "lost_distinction": (
                "Without explicit dependency edges, an independent consumer cannot "
                "establish from the receipt which overstatement rules depended on "
                "counterevidence presence; it must re-execute private CAL semantics."
            ),
        },
        "controls": controls,
        "all_controls_passed": all(controls.values()),
        "bounds": {
            "rule_family_scope": "absolute-wording/counterevidence seam only",
            "multiplicity": (
                "Not resolved: the frozen seam contains one counterevidence candidate."
            ),
            "production_change": False,
        },
    }


def main() -> int:
    result = run_experiment()
    output = Path("build/research/contract-c-rc2-c/dependency-receipt.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_bytes(result))
    print(json.dumps(result["controls"], sort_keys=True))
    if not result["all_controls_passed"]:
        raise AssertionError("one or more preregistered RC2-C controls failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
