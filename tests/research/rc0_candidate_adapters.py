"""Phase-2 shadow adapters for the frozen RC0 evaluator.

These are deliberately small representational probes, not replacement CAL
implementations.  Each adapter exposes only state that the named methodology
could legitimately make reconstructable.  The frozen evaluator remains in
``rc0_evaluator.py`` and is not modified after v2 exposure.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def _base(case: dict[str, Any]) -> dict[str, Any]:
    facts = case["facts"]
    return {
        "measurement_token": facts.get("measurement_token"),
        "retained_evidence_ids": list(facts.get("evidence_ids", [])),
        "deciding_evidence_ids": [],
        "non_deciding": {},
        "assessment_states": {},
        "source_facts": deepcopy(facts.get("source_facts", {})),
        "execution_state": facts.get("execution"),
        "terminal_class": facts.get("expected_terminal_class"),
        "terminal_reason": None,
        "basis_form": None,
        "basis_members": [],
        "policy_id": facts.get("policy_id") or facts.get("named_policy"),
        "aggregation_status": facts.get("aggregation_status"),
    }


def current_v050_trace_adapter(case: dict[str, Any]) -> dict[str, Any]:
    """Current v0.5.0 v1 trace + bound input, without invented new state.

    What it can expose legitimately:
    - raw retrieval/entailment measurement and retained input identities;
    - existing terminal reason/rule identity;
    - source facts from the bound Contract-B input.

    What it does not expose as first-class typed state:
    - proposition-specific generic assessment execution/value;
    - final post-suppression deciding pool;
    - intervention-derived causal form;
    - a v1 trace object for an execution that failed before trace creation.
    """
    out = _base(case)
    cid = case["id"]
    if cid == "F01_no_evidence":
        out["terminal_reason"] = "no_evidence"
    elif cid == "F02_read_silent":
        out["terminal_reason"] = "no_entail_signal"
    elif cid == "F03_out_of_scope_after_measurement":
        out["terminal_reason"] = "out_of_scope"
    elif cid == "F04_signal_excluded_by_policy":
        out["terminal_reason"] = "no_entail_signal"
        out["non_deciding"] = {"p-bg": "P1_eligibility_suppressed"}
    elif cid == "F05_louder_excluded_signal_plus_deciding_signal":
        out["non_deciding"] = {"p-bg": "P1_eligibility_suppressed"}
        # The final re-aggregated signal is not a typed AuditTrace field.
        out["deciding_evidence_ids"] = []
    elif cid.startswith("F06"):
        out["terminal_class"] = "supported"
    elif cid.startswith("F08"):
        # Current v1 has no generic typed eligibility assessment state.
        out["assessment_states"] = {}
    elif cid == "F09_execution_failed":
        # A failed run does not produce an AuditTrace subject-matter object.
        out["execution_state"] = None
        out["terminal_class"] = None
        out["retained_evidence_ids"] = []
    elif cid == "F10_distributed_partial_evidence":
        out["terminal_class"] = "not_checkable"
        out["terminal_reason"] = "no_entail_signal"
    return out


def terminal_reason_augmentation_adapter(case: dict[str, Any]) -> dict[str, Any]:
    """Candidate A: current trace plus a richer terminal reason taxonomy only."""
    out = current_v050_trace_adapter(case)
    cid = case["id"]
    richer = {
        "F02_read_silent": "read_silent",
        "F04_signal_excluded_by_policy": "all_deciding_signals_excluded",
        "F10_distributed_partial_evidence": "aggregation_unresolved",
    }
    if cid in richer:
        out["terminal_reason"] = richer[cid]
    return out


def additive_epistemic_receipt_adapter(case: dict[str, Any]) -> dict[str, Any]:
    """Candidate B: current semantics plus an additive typed epistemic receipt.

    The receipt records source facts, named assessment execution state,
    participation/removal roles, execution state, and intervention-derived basis.
    It does not require the decision implementation itself to be decomposed into
    software stages.
    """
    facts = case["facts"]
    out = _base(case)
    out["assessment_states"] = dict(facts.get("required_assessments", {}))
    cid = case["id"]
    if cid == "F01_no_evidence":
        out["terminal_reason"] = "no_evidence"
        out["deciding_evidence_ids"] = []
    elif cid == "F02_read_silent":
        out["terminal_reason"] = "read_silent"
        out["deciding_evidence_ids"] = []
    elif cid == "F03_out_of_scope_after_measurement":
        out["terminal_reason"] = "out_of_scope"
        out["deciding_evidence_ids"] = []
    elif cid == "F04_signal_excluded_by_policy":
        out["terminal_reason"] = "signal_excluded"
        out["deciding_evidence_ids"] = []
        out["non_deciding"] = {"p-bg": "named_policy_excluded"}
    elif cid == "F05_louder_excluded_signal_plus_deciding_signal":
        out["deciding_evidence_ids"] = ["p-primary"]
        out["non_deciding"] = {"p-bg": "named_policy_excluded"}
        out["basis_form"] = "single_necessary"
        out["basis_members"] = ["p-primary"]
    elif cid.startswith("F06"):
        out["terminal_class"] = "supported"
    elif cid.startswith("F07"):
        # Trust is retained as a source fact.  The absence of a separate
        # proposition-specific eligibility assessment stays explicit.
        out["assessment_states"] = {"eligibility": "not_performed"}
    elif cid == "F09_execution_failed":
        out["execution_state"] = "failed"
        out["terminal_class"] = None
        out["terminal_reason"] = None
        out["deciding_evidence_ids"] = []
    elif cid == "F10_distributed_partial_evidence":
        out["terminal_class"] = "unresolved"
        out["terminal_reason"] = "aggregation_unresolved"
        out["deciding_evidence_ids"] = []
        out["non_deciding"] = {"p-a": "partial", "p-b": "partial"}
    elif cid == "F11_independent_sufficient_alternatives":
        out["deciding_evidence_ids"] = ["p-a", "p-b"]
        out["basis_form"] = "independent_sufficient_alternatives"
        out["basis_members"] = ["p-a", "p-b"]
    elif cid == "F12_jointly_sufficient":
        out["deciding_evidence_ids"] = ["p-a", "p-b"]
        out["basis_form"] = "jointly_sufficient"
        out["basis_members"] = ["p-a", "p-b"]
    return out


def historical_v2_surface_adapter(case: dict[str, Any]) -> dict[str, Any]:
    """Candidate C: capabilities actually present in old pipeline_rules.V2Verdict.

    The historical branch separates precomputed measurement from later
    qualification, records removals, uses per-role eligibility, exposes null
    reasons and deciding passages, and omits upstream nomination roles.

    It does *not* provide Contract-C-style generic assessment execution/value,
    does not distinguish not-performed from unknown eligibility, treats absent
    trust as eligible in Q1, has no execution-failure result record, and exposes
    deciding passages without intervention-derived causal form.
    """
    facts = case["facts"]
    out = _base(case)
    cid = case["id"]

    if cid == "F01_no_evidence":
        out["terminal_reason"] = "no_evidence"
        out["deciding_evidence_ids"] = []
    elif cid == "F02_read_silent":
        out["terminal_reason"] = "no_signal"
        out["deciding_evidence_ids"] = []
    elif cid == "F03_out_of_scope_after_measurement":
        out["terminal_reason"] = "out_of_form"
        out["deciding_evidence_ids"] = []
    elif cid == "F04_signal_excluded_by_policy":
        out["terminal_reason"] = "all_ineligible"
        out["deciding_evidence_ids"] = []
        out["non_deciding"] = {"p-bg": "Q1_provenance"}
    elif cid == "F05_louder_excluded_signal_plus_deciding_signal":
        out["deciding_evidence_ids"] = ["p-primary"]
        out["non_deciding"] = {"p-bg": "Q1_provenance"}
    elif cid.startswith("F06"):
        out["terminal_class"] = "supported"
    elif cid.startswith("F07"):
        # Q1 directly maps trust to role eligibility; there is no separately
        # typed proposition eligibility-assessment execution state.
        out["assessment_states"] = {}
    elif cid.startswith("F08"):
        # The historical surface has no performed_unknown/not_performed/
        # not_applicable assessment vocabulary.
        out["assessment_states"] = {}
    elif cid == "F09_execution_failed":
        out["execution_state"] = None
        out["terminal_class"] = None
        out["retained_evidence_ids"] = []
    elif cid == "F10_distributed_partial_evidence":
        out["terminal_class"] = "not_checkable"
        out["terminal_reason"] = "not_resolvable"
        out["deciding_evidence_ids"] = []
    elif cid in ("F11_independent_sufficient_alternatives", "F12_jointly_sufficient"):
        # V2Verdict can list deciding passages but does not state whether they
        # are independent alternatives or jointly sufficient.
        out["deciding_evidence_ids"] = ["p-a", "p-b"]
        out["basis_form"] = None
        out["basis_members"] = []
    return out


def internal_staged_ledger_adapter(case: dict[str, Any]) -> dict[str, Any]:
    """Candidate D: fully staged internal ledger with the same observable state.

    For RC0's behavioral properties this is deliberately observationally
    equivalent to Candidate B.  If both pass, the evaluator supports the state
    boundaries but does not establish that internal stage decomposition is
    necessary.
    """
    return additive_epistemic_receipt_adapter(case)


__all__ = [
    "additive_epistemic_receipt_adapter",
    "current_v050_trace_adapter",
    "historical_v2_surface_adapter",
    "internal_staged_ledger_adapter",
    "terminal_reason_augmentation_adapter",
]
