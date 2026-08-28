"""Independent receipt validator for RC2-C.

This module intentionally imports no Claim Audit Lab production code. It validates
the frozen research receipt from its own bytes/state only.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

OVERSTATED_CODES = frozenset(
    {"future_certainty", "overconfident_wording", "scope_overreach"}
)
COUNTER_STATE = "state:counterevidence_contexts_nonempty"


def _canonical_bytes(value: Any) -> bytes:
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


def _policy_hash(policy: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(policy)).hexdigest()


def counterevidence_dependency_codes(receipt: dict[str, Any]) -> set[str] | None:
    rules = {
        f"rule:{row['rule_id']}": row["code"]
        for row in receipt.get("emitted_causal_rules", [])
    }
    edges = [
        edge
        for edge in receipt.get("dependency_edges", [])
        if edge.get("from") == COUNTER_STATE
        and edge.get("relation") == "causes_absolute_wording_trigger_true"
    ]
    if not edges:
        return None
    codes = {rules[edge.get("to")] for edge in edges if edge.get("to") in rules}
    return codes or None


def validate_dependency_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("research_receipt") != "contract-c-rc2-c-dependency-v0":
        errors.append("unexpected research receipt marker")

    policy = receipt.get("policy")
    if not isinstance(policy, dict):
        errors.append("policy missing")
        return errors
    canonical = policy.get("canonical")
    if not isinstance(canonical, dict):
        errors.append("canonical policy missing")
    else:
        observed_hash = _policy_hash(canonical)
        if policy.get("sha256") != observed_hash:
            errors.append("policy hash mismatch")
        if policy.get("config_id") != canonical.get("config_id"):
            errors.append("config_id is not bound to canonical policy")

    terminal = receipt.get("terminal")
    if not isinstance(terminal, dict):
        errors.append("terminal state missing")
        return errors
    verdict = terminal.get("final_verdict")
    branch = terminal.get("branch")
    rules = receipt.get("emitted_causal_rules", [])
    triggers = receipt.get("trigger_conditions", [])
    edges = receipt.get("dependency_edges", [])

    if verdict == "overstated":
        if branch != "overstated_rule_family":
            errors.append("overstated verdict lacks overstated terminal branch")
        causal = [
            row
            for row in rules
            if isinstance(row, dict) and row.get("code") in OVERSTATED_CODES
        ]
        if not causal:
            errors.append("overstated branch lacks causal overstatement rule")
        trigger_by_rule = {
            row.get("rule_id"): row
            for row in triggers
            if isinstance(row, dict) and row.get("rule_id")
        }
        edge_pairs = {
            (edge.get("from"), edge.get("to"), edge.get("relation"))
            for edge in edges
            if isinstance(edge, dict)
        }
        for row in causal:
            rule_id = row.get("rule_id")
            trigger = trigger_by_rule.get(rule_id)
            if trigger is None:
                errors.append(f"missing trigger condition for {rule_id}")
                continue
            if trigger.get("trigger_result") is not True:
                errors.append(f"trigger result not true for {rule_id}")
            if trigger.get("policy_overstated_detection") is not True:
                errors.append(f"overstated policy gate not true for {rule_id}")
            counter_edge = (
                COUNTER_STATE,
                f"rule:{rule_id}",
                "causes_absolute_wording_trigger_true",
            )
            if counter_edge not in edge_pairs:
                errors.append(f"missing counterevidence dependency for {rule_id}")
            claim_edge = (
                "state:claim_trigger:guarantees",
                f"rule:{rule_id}",
                "required_lexical_trigger",
            )
            if claim_edge not in edge_pairs:
                errors.append(f"missing lexical-trigger dependency for {rule_id}")
    elif verdict == "supported":
        if branch != "supported_score_branch":
            errors.append("supported verdict lacks supported score branch")
        if any(
            isinstance(row, dict) and row.get("code") in OVERSTATED_CODES
            for row in rules
        ):
            errors.append("supported receipt retains causal overstatement rules")
        if counterevidence_dependency_codes(receipt) is not None:
            errors.append("supported receipt retains counterevidence dependency")
    else:
        errors.append(f"validator does not cover RC2-C verdict {verdict!r}")

    evidence_state = receipt.get("evidence_state")
    if not isinstance(evidence_state, dict):
        errors.append("evidence state missing")
    elif verdict == "overstated" and not evidence_state.get(
        "counterevidence_contexts_nonempty"
    ):
        errors.append("overstated seam lacks counterevidence collection state")

    return errors
