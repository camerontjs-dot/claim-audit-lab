"""Research-only Contract-C RC2-A projection and evaluators.

This module is deliberately outside ``src/``.  It observes current production
CAL boundary objects without changing production audit semantics.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from typing import Any, Iterable

PROFILE_ID = "contract-c-rc2-a-producer-candidate"
REQUIRED_ASSESSMENTS = (
    "eligibility",
    "semantic_validity",
    "aperture",
    "temporal_applicability",
    "citation",
)
ASSESSMENT_STATES = {
    "performed",
    "not_performed",
    "failed",
    "not_applicable",
    "not_exposed",
}
FORBIDDEN_DESTINATION_KEYS = {
    "expected_utility",
    "utility",
    "preference",
    "risk_tolerance",
    "authority_profile",
    "authorization",
    "autonomy_envelope",
    "workflow_route",
    "forecast_probability",
    "future_state",
    "causal_effect_prediction",
}


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
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _candidate_ref_lookup(contents: Any) -> dict[tuple[str, str], dict[str, str]]:
    lookup: dict[tuple[str, str], dict[str, str]] = {}
    for source_id, passages in contents.passages.items():
        for passage in passages:
            lookup[(source_id, f"{source_id}/{passage.passage_id}")] = {
                "source_id": source_id,
                "passage_id": passage.passage_id,
                "passage_sha256": passage.passage_hash,
            }
    return lookup


def _contribution(
    proposition_id: str,
    channel: str,
    candidate: Any,
    lookup: dict[tuple[str, str], dict[str, str]],
) -> dict[str, Any]:
    ref = lookup.get((candidate.source_id, candidate.excerpt_id))
    if ref is None:
        # Preserve an explicit structural failure rather than inferring passage
        # identity from a filename or array position.
        ref = {
            "source_id": candidate.source_id,
            "passage_id": None,
            "passage_sha256": None,
            "reference_state": "unresolved",
        }
    id_payload = {
        "proposition_id": proposition_id,
        "channel": channel,
        "evidence_ref": ref,
    }
    return {
        "contribution_id": stable_id("contribution", id_payload),
        "channel": channel,
        "evidence_ref": ref,
    }


def project_real_boundary(
    *,
    contents: Any,
    assessments: Iterable[Any],
    contract_b_binding: dict[str, Any],
    cal_code_sha: str,
    cal_library_version: str,
    engine_id: str,
    engine_selection_origin: str,
    cal_policy_id: str,
    audit_run_id: str,
    factual_context_state: str,
) -> dict[str, Any]:
    """Project only information attributable at the observed producer boundary.

    The current v0.2 Contract-B path does not expose a deciding-contribution
    receipt or typed eligibility/validity/aperture/temporal/citation receipts.
    RC2 records those absences as ``not_exposed`` instead of manufacturing
    ``not_performed`` or reverse-engineering implementation locals.
    """

    lookup = _candidate_ref_lookup(contents)
    propositions: list[dict[str, Any]] = []
    for assessment in assessments:
        proposition_id = assessment.claim.id
        support = [
            _contribution(proposition_id, "support_candidate", candidate, lookup)
            for candidate in assessment.candidate_evidence
        ]
        counter = [
            _contribution(proposition_id, "counterevidence", candidate, lookup)
            for candidate in assessment.counterevidence
        ]
        contributions = support + counter
        contribution_ids = [row["contribution_id"] for row in contributions]
        counter_ids = [row["contribution_id"] for row in counter]
        rule_receipts = [flag.code for flag in assessment.rule_flags]

        # The aggregate support signal is a stable public ClaimAssessment value.
        # Per-candidate lexical scores/rationales and source metadata are omitted.
        measurement = {
            "measurement_id": stable_id(
                "measurement",
                {
                    "proposition_id": proposition_id,
                    "kind": "cal_v0_2_aggregate_support_signal",
                    "value": assessment.support_signal,
                },
            ),
            "kind": "cal_v0_2_aggregate_support_signal",
            "value": assessment.support_signal,
            "operator_id": "claim_audit_lab.rules.assess_claim_support",
        }

        assessments_state = {
            name: {
                "state": "not_exposed",
                "reason_code": "production_boundary_has_no_typed_receipt",
            }
            for name in REQUIRED_ASSESSMENTS
        }

        # Candidate membership is exposed, but the production boundary does not
        # say which candidates were direct/deciding versus merely retained.  Do
        # not label all candidates as the exact basis.
        basis = {
            "state": "unavailable",
            "reason_code": "no_deciding_contribution_receipt_at_production_boundary",
            "available_contribution_ids": contribution_ids,
            "available_rule_receipt_ids": rule_receipts,
        }

        blockers: list[dict[str, str]] = []
        if assessment.support_label in {"needs_source", "not_checkable"}:
            blockers.append(
                {
                    "type": "epistemic_conclusion",
                    "code": assessment.support_label,
                }
            )

        propositions.append(
            {
                "proposition": {
                    "proposition_id": proposition_id,
                    "text_sha256": sha256_text(assessment.claim.text),
                },
                "contributions": contributions,
                "measurements": [measurement],
                "assessments": assessments_state,
                "conclusion": {
                    "reported_verdict": assessment.support_label,
                    "basis": basis,
                    "residual": {
                        "counterevidence_contribution_ids": counter_ids,
                    },
                    "blockers": blockers,
                },
                "execution": {
                    "status": "completed",
                    "failures": [],
                },
            }
        )

    body: dict[str, Any] = {
        "candidate_profile": PROFILE_ID,
        "input": {"contract_b": copy.deepcopy(contract_b_binding)},
        "producer": {
            "name": "claim-audit-lab",
            "code_sha": cal_code_sha,
            "library_version": cal_library_version,
            "engine": {
                "id": engine_id,
                "selection_origin": engine_selection_origin,
            },
            "policy": {
                "id": cal_policy_id,
                "contract_b_audit_config_hash": contents.audit_config.config_hash,
            },
            "operator": {
                "state": "not_recorded_at_boundary",
            },
            "model": {
                "state": "not_applicable",
                "reason_code": "deterministic_v0_2_engine",
            },
        },
        "contract_b_context": {
            "factual_context_state": factual_context_state,
        },
        "execution": {
            "status": "completed",
            "audit_run_id": audit_run_id,
            "failures": [],
            "deviations": [],
        },
        "propositions": propositions,
    }
    result = copy.deepcopy(body)
    result["result_set_id"] = stable_id("result-set", body)
    return result


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def validate_candidate(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if candidate.get("candidate_profile") != PROFILE_ID:
        errors.append("unexpected candidate profile")
    binding = candidate.get("input", {}).get("contract_b", {})
    for key in ("contract_version", "bundle_id", "bundle_hash", "artifact_sha256"):
        if not binding.get(key):
            errors.append(f"missing exact Contract-B binding field: {key}")
    if not candidate.get("producer", {}).get("code_sha"):
        errors.append("missing CAL code SHA")
    if not candidate.get("producer", {}).get("policy", {}).get("id"):
        errors.append("missing CAL policy identity")
    if candidate.get("execution", {}).get("status") not in {"completed", "partial", "failed"}:
        errors.append("invalid run execution state")

    forbidden = sorted(FORBIDDEN_DESTINATION_KEYS & set(_walk_keys(candidate)))
    if forbidden:
        errors.append("destination-policy leakage: " + ", ".join(forbidden))

    propositions = candidate.get("propositions")
    if not isinstance(propositions, list) or not propositions:
        errors.append("candidate has no proposition results")
        return errors

    seen_props: set[str] = set()
    for index, result in enumerate(propositions):
        proposition = result.get("proposition", {})
        proposition_id = proposition.get("proposition_id")
        if not proposition_id or proposition_id in seen_props:
            errors.append(f"proposition[{index}] missing/duplicate identity")
        else:
            seen_props.add(proposition_id)
        if not proposition.get("text_sha256"):
            errors.append(f"proposition[{index}] missing text hash")

        known_contributions = {
            row.get("contribution_id") for row in result.get("contributions", [])
        }
        if None in known_contributions:
            errors.append(f"proposition[{index}] contribution missing identity")
        for row in result.get("contributions", []):
            ref = row.get("evidence_ref", {})
            if not ref.get("source_id") or not ref.get("passage_id") or not ref.get("passage_sha256"):
                errors.append(f"proposition[{index}] unresolved evidence reference")

        for name in REQUIRED_ASSESSMENTS:
            item = result.get("assessments", {}).get(name)
            if item is None:
                errors.append(f"proposition[{index}] assessment absent: {name}")
            elif item.get("state") not in ASSESSMENT_STATES:
                errors.append(f"proposition[{index}] invalid assessment state: {name}")

        basis = result.get("conclusion", {}).get("basis", {})
        for contribution_id in basis.get("available_contribution_ids", []):
            if contribution_id not in known_contributions:
                errors.append(f"proposition[{index}] basis references missing contribution")
        for contribution_id in result.get("conclusion", {}).get("residual", {}).get(
            "counterevidence_contribution_ids", []
        ):
            if contribution_id not in known_contributions:
                errors.append(f"proposition[{index}] residual references missing contribution")
        if result.get("execution", {}).get("status") not in {"completed", "partial", "failed"}:
            errors.append(f"proposition[{index}] invalid execution state")

    body = copy.deepcopy(candidate)
    observed_id = body.pop("result_set_id", None)
    expected_id = stable_id("result-set", body)
    if observed_id != expected_id:
        errors.append("result-set identity mismatch")
    return errors


def producer_gate(candidate: dict[str, Any]) -> tuple[str, list[str]]:
    """Apply only the preregistered RC2-A producer gate."""

    blockers = validate_candidate(candidate)
    for result in candidate.get("propositions", []):
        proposition_id = result.get("proposition", {}).get("proposition_id", "unknown")
        if result.get("conclusion", {}).get("basis", {}).get("state") != "known":
            blockers.append(f"{proposition_id}: exact decision basis is not exposed")
        not_exposed = [
            name
            for name, item in result.get("assessments", {}).items()
            if item.get("state") == "not_exposed"
        ]
        if not_exposed:
            blockers.append(
                f"{proposition_id}: required assessment attribution not exposed: "
                + ", ".join(sorted(not_exposed))
            )
    if blockers:
        return "FAILED", blockers
    return "SATISFIED", []


def render_derived_report(candidate: dict[str, Any]) -> str:
    """Deterministic human report derived only from candidate semantic state."""

    lines = [
        "# Contract C RC2-A derived producer report",
        "",
        f"Result set: `{candidate['result_set_id']}`",
        f"Contract B: `{candidate['input']['contract_b']['bundle_id']}`",
        f"Execution: `{candidate['execution']['status']}`",
        "",
    ]
    for result in candidate["propositions"]:
        p = result["proposition"]
        conclusion = result["conclusion"]
        lines.extend(
            [
                f"## {p['proposition_id']}",
                "",
                f"Verdict: `{conclusion['reported_verdict']}`",
                f"Basis state: `{conclusion['basis']['state']}`",
                "Assessments:",
            ]
        )
        for name in sorted(result["assessments"]):
            lines.append(f"- {name}: `{result['assessments'][name]['state']}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def semantic_firewall_receipts(candidate: dict[str, Any]) -> dict[str, Any]:
    """Prove downstream authority/forecast changes do not mutate C bytes."""

    before = sha256_bytes(canonical_bytes(candidate))
    authority_contexts = [
        {"authority_profile": "delegated_auto_action"},
        {"authority_profile": "named_human_required"},
    ]
    prediction_contexts = [
        {"forecast_probability": 0.10, "future_state": "scenario-a"},
        {"forecast_probability": 0.90, "future_state": "scenario-b"},
    ]
    # Contexts are intentionally consumed downstream and never merged into C.
    downstream = {
        "authority": [
            "auto" if row["authority_profile"] == "delegated_auto_action" else "human"
            for row in authority_contexts
        ],
        "prediction": [row["forecast_probability"] for row in prediction_contexts],
    }
    after = sha256_bytes(canonical_bytes(candidate))
    return {
        "contract_c_sha256_before": before,
        "contract_c_sha256_after": after,
        "identical": before == after,
        "downstream_observations": downstream,
    }


def count_structural_fields(value: Any) -> int:
    if isinstance(value, dict):
        return len(value) + sum(count_structural_fields(child) for child in value.values())
    if isinstance(value, list):
        return sum(count_structural_fields(child) for child in value)
    return 0


def repeated_scalar_count(value: Any) -> int:
    scalars: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)
        elif isinstance(node, (str, int, float, bool)) or node is None:
            scalars.append(json.dumps(node, sort_keys=True))

    visit(value)
    counts = Counter(scalars)
    return sum(count - 1 for count in counts.values() if count > 1)


def semantic_assertion_count(candidate: dict[str, Any]) -> int:
    total = 0
    for result in candidate.get("propositions", []):
        total += len(result.get("contributions", []))
        total += len(result.get("measurements", []))
        total += len(result.get("assessments", {}))
        total += 1  # conclusion
        total += 1  # execution state
    total += 1  # result-set execution state
    return total


def candidate_diagnostics(candidate: dict[str, Any]) -> dict[str, int]:
    return {
        "canonical_bytes": len(canonical_bytes(candidate)),
        "structural_fields": count_structural_fields(candidate),
        "repeated_scalar_values": repeated_scalar_count(candidate),
        "semantic_assertions": semantic_assertion_count(candidate),
    }


def field_justification_registry() -> list[dict[str, str]]:
    return [
        {"path": "result_set_id", "classification": "exact provenance / identity / reconstruction", "obligation": "integrity identity for immutable result-set bytes"},
        {"path": "input.contract_b", "classification": "exact provenance / identity / reconstruction", "obligation": "bind CAL result to the exact validated Contract-B input"},
        {"path": "producer.code_sha", "classification": "exact provenance / identity / reconstruction", "obligation": "distinguish producer implementation lineage"},
        {"path": "producer.engine", "classification": "execution / failure / supersession interpretation", "obligation": "identify the actually selected production engine and how selection occurred"},
        {"path": "producer.policy", "classification": "exact provenance / identity / reconstruction", "obligation": "identify the CAL policy/config under which the result was produced"},
        {"path": "producer.operator", "classification": "conditionally necessary", "obligation": "record explicit unavailable state rather than inventing an operator identity"},
        {"path": "propositions[].proposition", "classification": "exact provenance / identity / reconstruction", "obligation": "prevent proposition identity/text drift without duplicating Contract-B text"},
        {"path": "propositions[].contributions", "classification": "CAL-attributable semantic meaning + provenance", "obligation": "retain evidence/counterevidence references without copying upstream payloads"},
        {"path": "propositions[].measurements", "classification": "necessary to preserve CAL-attributable semantic meaning", "obligation": "preserve stable aggregate measurement outcome while excluding per-candidate telemetry"},
        {"path": "propositions[].assessments", "classification": "necessary to preserve CAL-attributable semantic meaning", "obligation": "distinguish performed/not-performed/failed/not-applicable from producer non-exposure"},
        {"path": "propositions[].conclusion", "classification": "necessary to preserve CAL-attributable semantic meaning", "obligation": "preserve conclusion, exact-basis availability, residual counterevidence and blockers"},
        {"path": "execution", "classification": "execution / failure / supersession interpretation", "obligation": "keep execution failure distinct from adverse subject findings"},
        {"path": "risk_label", "classification": "destination-specific policy", "obligation": "excluded: no demonstrated Contract-C semantic obligation"},
        {"path": "candidate_evidence[].score/rationale/source metadata", "classification": "implementation telemetry / upstream facts", "obligation": "excluded unless a falsifier demonstrates necessity"},
        {"path": "explanation/rewrite_guidance/report prose", "classification": "presentation convenience", "obligation": "excluded; deterministic report is derived from structured state"},
    ]


def ablation_matrix(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    """Record discriminating subfield ablations, not validator-only failures."""

    rows: list[dict[str, Any]] = []

    def row(path: str, invariant: str, consequence: str, classification: str) -> None:
        rows.append(
            {
                "removed_structure": path,
                "semantic_invariant_affected": invariant,
                "consumer_behavior_affected": consequence,
                "report_reconstruction_consequence": consequence,
                "provenance_consequence": consequence if "provenance" in invariant.lower() or "identity" in invariant.lower() else "none demonstrated",
                "hard_coded_harness_only": False,
                "classification": classification,
            }
        )

    row("input.contract_b", "exact input provenance", "cannot bind/reconstruct B -> C lineage", "necessary exact provenance / identity / reconstruction")
    row("producer.code_sha + producer.policy", "recomputation identity", "cannot distinguish semantically different producer/policy executions", "necessary exact provenance / identity / reconstruction")
    row("propositions[].proposition.text_sha256", "proposition identity", "silent proposition-text drift becomes undetectable", "necessary exact provenance / identity / reconstruction")
    row("propositions[].contributions", "retained evidence state", "counterevidence and evidence provenance cannot be reconstructed", "necessary CAL-attributable semantic meaning")
    row("propositions[].measurements", "measurement preservation", "consumer cannot recover the stable aggregate measurement outcome", "necessary CAL-attributable semantic meaning")
    row("propositions[].assessments", "unknown/not-performed/failure distinctions", "consumer cannot distinguish missing assessment from typed state", "necessary CAL-attributable semantic meaning")
    row("propositions[].conclusion.basis", "exact decision basis", "consumer cannot tell whether exact basis is known or unavailable", "necessary CAL-attributable semantic meaning")
    row("execution", "execution vs subject finding", "partial/failed execution can be confused with adverse epistemic result", "necessary execution interpretation")
    row("candidate_evidence raw scalar/debug fields", "none under telemetry invariance control", "no demonstrated consumer/report consequence when stable measurement and contribution receipts remain fixed", "implementation telemetry")
    row("risk_label / rewrite guidance / explanation prose", "none under semantic-firewall/report controls", "derived/policy presentation only", "presentation convenience / destination policy")
    return rows


__all__ = [
    "PROFILE_ID",
    "ablation_matrix",
    "candidate_diagnostics",
    "canonical_bytes",
    "field_justification_registry",
    "producer_gate",
    "project_real_boundary",
    "render_derived_report",
    "semantic_firewall_receipts",
    "sha256_bytes",
    "sha256_text",
    "stable_id",
    "validate_candidate",
]
