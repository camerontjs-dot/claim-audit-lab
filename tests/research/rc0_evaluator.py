"""Frozen Phase-1 behavioral evaluator for CAL Epistemic Methodology RC0.

This is a research-only adapter surface.  It does not prescribe a production
schema, class layout, stage count, or module boundary.  A candidate methodology
may use any internal representation; its adapter only has to expose the
observable facts needed to test the preregistered properties.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable
import json

Adapter = Callable[[dict[str, Any]], dict[str, Any]]

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "epistemic_methodology_rc0_cases.json"

GATES = (
    "A_state_distinguishability",
    "B_fail_closed_missing_state",
    "C_evidence_retention",
    "D_measurement_policy_separation",
    "E_upstream_role_invariance",
    "F_trust_eligibility_separation",
    "G_causal_basis_reconstruction",
    "H_execution_state_separation",
    "I_policy_counterfactual_stability",
    "J_replayability",
)


def load_cases() -> list[dict[str, Any]]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return payload["cases"]


def _run(adapter: Adapter, cases: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {case["id"]: adapter(deepcopy(case)) for case in cases}


def _signature(output: dict[str, Any]) -> tuple[Any, ...]:
    """Architecture-neutral observable signature for non-decision causes."""
    return (
        output.get("execution_state"),
        output.get("terminal_class"),
        output.get("terminal_reason"),
        output.get("measurement_token"),
        tuple(sorted(output.get("retained_evidence_ids", []))),
        tuple(sorted(output.get("deciding_evidence_ids", []))),
        tuple(sorted(output.get("non_deciding", {}).items())),
        tuple(sorted(output.get("assessment_states", {}).items())),
        output.get("aggregation_status"),
    )


def evaluate(adapter: Adapter) -> dict[str, bool]:
    """Evaluate one candidate methodology adapter against the frozen properties."""
    cases = load_cases()
    first = _run(adapter, cases)
    second = _run(adapter, cases)

    # A. Different epistemic causes must remain observably different.  These four
    # cases all look like some form of non-decision from far away, but they mean
    # different things: nothing admitted, evidence read/silent, strong evidence
    # made non-deciding, and execution failure.
    state_ids = ["F01_no_evidence", "F02_read_silent", "F04_signal_excluded_by_policy", "F09_execution_failed"]
    signatures = {_signature(first[case_id]) for case_id in state_ids}
    gate_a = len(signatures) == len(state_ids)

    # B. Required assessment state must not be manufactured from absence.  The
    # evaluator intentionally distinguishes performed-unknown, adverse,
    # not-performed, and not-applicable.
    expected_assessment = {
        "F08a_eligibility_unknown": "performed_unknown",
        "F08b_eligibility_adverse": "performed_adverse",
        "F08c_eligibility_not_performed": "not_performed",
        "F08d_eligibility_not_applicable": "not_applicable",
    }
    gate_b = all(
        first[case_id].get("assessment_states", {}).get("eligibility") == expected
        for case_id, expected in expected_assessment.items()
    )

    # C. Evidence may become non-deciding without disappearing.  The louder
    # excluded signal remains reconstructable, and the eventual deciding signal
    # is separately identifiable.
    f04 = first["F04_signal_excluded_by_policy"]
    f05 = first["F05_louder_excluded_signal_plus_deciding_signal"]
    gate_c = (
        set(f04.get("retained_evidence_ids", [])) == {"p-bg"}
        and "p-bg" in f04.get("non_deciding", {})
        and set(f05.get("retained_evidence_ids", [])) == {"p-bg", "p-primary"}
        and "p-bg" in f05.get("non_deciding", {})
        and set(f05.get("deciding_evidence_ids", [])) == {"p-primary"}
    )

    # D. Measurement is not policy.  Pure source-metadata and downstream-policy
    # mutations must not rewrite the claim/passage semantic measurement.
    gate_d = (
        first["F07a_trust_primary"].get("measurement_token")
        == first["F07b_trust_background"].get("measurement_token")
        == "m:contradict:0.92"
        and first["F13a_policy_counterfactual_P0"].get("measurement_token")
        == first["F13b_policy_counterfactual_P1"].get("measurement_token")
        == "m:contradict:0.92"
    )

    # E. Upstream nomination is provenance, not a semantic label.  Holding the
    # passage fixed while mutating nomination containers may not mutate the
    # semantic measurement or terminal interpretation solely for that reason.
    gate_e = (
        first["F06a_nomination_support"].get("measurement_token")
        == first["F06b_nomination_counter"].get("measurement_token")
        == "m:entail:0.91"
        and first["F06a_nomination_support"].get("terminal_class")
        == first["F06b_nomination_counter"].get("terminal_class")
    )

    # F. Source facts and proposition-specific assessments are separate domains.
    # An implementation may have a named policy that reads a source fact, but it
    # may not rewrite "not performed" into a performed eligibility assessment.
    gate_f = all(
        first[case_id].get("source_facts") == next(
            case["facts"].get("source_facts", {}) for case in cases if case["id"] == case_id
        )
        and first[case_id].get("assessment_states", {}).get("eligibility") == "not_performed"
        for case_id in ("F07a_trust_primary", "F07b_trust_background")
    )

    # G. Causal claims are tested by intervention structure, not by choosing a
    # convenient winner.  Tied independent sufficiency and joint sufficiency are
    # different, and excluded residual evidence is not a basis member.
    f11 = first["F11_independent_sufficient_alternatives"]
    f12 = first["F12_jointly_sufficient"]
    gate_g = (
        f11.get("basis_form") == "independent_sufficient_alternatives"
        and set(f11.get("basis_members", [])) == {"p-a", "p-b"}
        and f12.get("basis_form") == "jointly_sufficient"
        and set(f12.get("basis_members", [])) == {"p-a", "p-b"}
        and "p-bg" not in set(f05.get("basis_members", []))
        and "p-primary" in set(f05.get("basis_members", []))
    )

    # H. A failed execution is not a subject-matter unknown/not-checkable result.
    f09 = first["F09_execution_failed"]
    f02 = first["F02_read_silent"]
    gate_h = (
        f09.get("execution_state") == "failed"
        and f09.get("terminal_class") is None
        and f02.get("execution_state") == "completed"
        and f02.get("terminal_class") == "not_checkable"
    )

    # I. Policy identity may change the derived terminal result, but not the
    # frozen semantic measurement or retained evidence facts.
    p0 = first["F13a_policy_counterfactual_P0"]
    p1 = first["F13b_policy_counterfactual_P1"]
    gate_i = (
        p0.get("policy_id") == "P0"
        and p1.get("policy_id") == "P1"
        and p0.get("measurement_token") == p1.get("measurement_token")
        and p0.get("retained_evidence_ids") == p1.get("retained_evidence_ids")
    )

    # J. Replaying the same frozen case through the adapter must produce the same
    # observable record.  This tests deterministic reconstruction, not universal
    # runtime determinism of external models.
    gate_j = first == second

    return dict(zip(GATES, (gate_a, gate_b, gate_c, gate_d, gate_e, gate_f, gate_g, gate_h, gate_i, gate_j), strict=True))


def reference_observability_control(case: dict[str, Any]) -> dict[str, Any]:
    """Positive control: explicit record with no architectural claim.

    This exists only to prove the evaluator can observe every preregistered
    property.  It is not a candidate architecture and must not be promoted.
    """
    facts = case["facts"]
    result: dict[str, Any] = {
        "measurement_token": facts.get("measurement_token"),
        "retained_evidence_ids": list(facts.get("evidence_ids", [])),
        "deciding_evidence_ids": list(facts.get("admitted_ids", [])),
        "non_deciding": {},
        "assessment_states": dict(facts.get("required_assessments", {})),
        "source_facts": deepcopy(facts.get("source_facts", {})),
        "execution_state": facts.get("execution"),
        "terminal_class": facts.get("expected_terminal_class"),
        "terminal_reason": None,
        "basis_form": None,
        "basis_members": [],
        "policy_id": facts.get("policy_id") or facts.get("named_policy"),
        "aggregation_status": facts.get("aggregation_status"),
    }
    case_id = case["id"]
    if case_id == "F01_no_evidence":
        result["terminal_reason"] = "no_evidence"
        result["deciding_evidence_ids"] = []
    elif case_id == "F02_read_silent":
        result["terminal_reason"] = "read_silent"
    elif case_id == "F03_out_of_scope_after_measurement":
        result["terminal_reason"] = "out_of_scope"
    elif case_id == "F04_signal_excluded_by_policy":
        result["terminal_reason"] = "signal_excluded"
        result["deciding_evidence_ids"] = []
        result["non_deciding"] = {"p-bg": "policy_excluded"}
    elif case_id == "F05_louder_excluded_signal_plus_deciding_signal":
        result["deciding_evidence_ids"] = ["p-primary"]
        result["non_deciding"] = {"p-bg": "policy_excluded"}
        result["basis_form"] = "single_necessary"
        result["basis_members"] = ["p-primary"]
    elif case_id.startswith("F06"):
        result["terminal_class"] = "supported"
    elif case_id.startswith("F07"):
        # Source metadata is retained, but no proposition-specific eligibility
        # assessment is invented from it.
        result["assessment_states"] = {"eligibility": "not_performed"}
    elif case_id == "F09_execution_failed":
        result["terminal_class"] = None
        result["terminal_reason"] = None
        result["deciding_evidence_ids"] = []
    elif case_id == "F10_distributed_partial_evidence":
        result["terminal_class"] = "unresolved"
        result["terminal_reason"] = "aggregation_unresolved"
        result["deciding_evidence_ids"] = []
        result["non_deciding"] = {"p-a": "partial", "p-b": "partial"}
    elif case_id == "F11_independent_sufficient_alternatives":
        result["basis_form"] = "independent_sufficient_alternatives"
        result["basis_members"] = ["p-a", "p-b"]
    elif case_id == "F12_jointly_sufficient":
        result["basis_form"] = "jointly_sufficient"
        result["basis_members"] = ["p-a", "p-b"]
    return result


def generic_abstention_weak_control(case: dict[str, Any]) -> dict[str, Any]:
    """Deliberately weak control: collapse every non-success into abstention."""
    facts = case["facts"]
    return {
        "measurement_token": None,
        "retained_evidence_ids": [],
        "deciding_evidence_ids": [],
        "non_deciding": {},
        "assessment_states": {},
        "source_facts": {},
        "execution_state": "completed",
        "terminal_class": facts.get("expected_terminal_class") or "not_checkable",
        "terminal_reason": "abstain",
        "basis_form": None,
        "basis_members": [],
        "policy_id": None,
        "aggregation_status": None,
    }


def terminal_reason_only_weak_control(case: dict[str, Any]) -> dict[str, Any]:
    """Plausible weak control: add terminal reasons but no state/evidence ledger."""
    facts = case["facts"]
    reason = {
        "F01_no_evidence": "no_evidence",
        "F02_read_silent": "no_entail_signal",
        "F03_out_of_scope_after_measurement": "out_of_scope",
        "F04_signal_excluded_by_policy": "excluded_signal",
        "F09_execution_failed": "execution_failed",
    }.get(case["id"])
    return {
        "measurement_token": facts.get("measurement_token"),
        "retained_evidence_ids": [],
        "deciding_evidence_ids": [],
        "non_deciding": {},
        "assessment_states": {},
        "source_facts": {},
        "execution_state": facts.get("execution", "completed"),
        "terminal_class": None if facts.get("execution") == "failed" else facts.get("expected_terminal_class"),
        "terminal_reason": reason,
        "basis_form": None,
        "basis_members": [],
        "policy_id": facts.get("policy_id"),
        "aggregation_status": facts.get("aggregation_status"),
    }


__all__ = [
    "GATES",
    "evaluate",
    "generic_abstention_weak_control",
    "load_cases",
    "reference_observability_control",
    "terminal_reason_only_weak_control",
]
