from __future__ import annotations

import re
from itertools import combinations
from typing import Any

from claim_audit_lab.production_v1 import SEMANTIC_IMPLEMENTATION_SHA
from claim_audit_lab.production_v1.semantic.engine import AuditResult, PassageTrace, compose
from claim_audit_lab.production_v1.semantic.models import (
    AuditContext,
    CategoricalRelation,
    Conclusion,
    FailureCode,
)

PROFILE = "contract-c-successor-candidate-a-rc2-research"
POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"
POLICY = {
    "profile": "cal-v1-candidate-2026-09",
    "semantics": "typed-source-grounded-scoreless-categorical",
    "supported_families": ["direct_event_order", "strict_comparison"],
}
_HEX40 = re.compile(r"^[0-9a-f]{40}$")


def public_terminal_state(result: AuditResult) -> tuple[str, str]:
    if result.conclusion is Conclusion.SUPPORTED:
        return "supported", "categorical_support"
    if result.conclusion is Conclusion.CONTRADICTED:
        return "contradicted", "categorical_refutation"
    if result.failure_code is FailureCode.MIXED_RELATIONS:
        return "not_checkable", "MIXED_RELATIONS"
    if result.failure_code is FailureCode.UNSUPPORTED_SEMANTIC_FAMILY:
        return "not_checkable", "UNSUPPORTED_SEMANTIC_FAMILY"
    if any(
        trace.relation is not None
        and trace.relation.categorical_relation is CategoricalRelation.UNRESOLVED
        for trace in result.traces
    ):
        return "not_checkable", "unresolved_categorical_relation"
    if result.conclusion is Conclusion.NOT_CHECKABLE:
        return "not_checkable", "no_deciding_relation"
    raise ValueError(
        "unrepresentable CAL public terminal state: "
        + (result.failure_code.value if result.failure_code is not None else result.conclusion.value)
    )


def derive_basis_passage_ids(
    context: AuditContext,
    result: AuditResult,
) -> tuple[tuple[str, ...], ...]:
    _, reason = public_terminal_state(result)
    if reason in {"no_deciding_relation", "UNSUPPORTED_SEMANTIC_FAMILY"}:
        return ()

    traces = tuple(result.traces)
    minimal: list[frozenset[str]] = []
    for size in range(1, len(traces) + 1):
        for indexes in combinations(range(len(traces)), size):
            subset: tuple[PassageTrace, ...] = tuple(traces[index] for index in indexes)
            replay = compose(context, subset)
            if public_terminal_state(replay) != public_terminal_state(result):
                continue
            ids = frozenset(trace.passage_id for trace in subset)
            if any(existing <= ids for existing in minimal):
                continue
            minimal.append(ids)
    return tuple(sorted(tuple(sorted(group)) for group in minimal))


def _relation_label(trace: PassageTrace) -> str:
    if trace.relation is None:
        return "non_polarized"
    relation = trace.relation.categorical_relation
    if relation is CategoricalRelation.SUPPORTS:
        return "supports"
    if relation is CategoricalRelation.REFUTES:
        return "refutes"
    return "non_polarized"


def materialize_unsealed(
    context: AuditContext,
    result: AuditResult,
    *,
    policy_resolver_commit_sha: str,
) -> dict[str, Any]:
    if SEMANTIC_IMPLEMENTATION_SHA != "847cc970642bb648dc994b929c2053b5c9d4648c":
        raise ValueError("unexpected CAL semantic implementation authority")
    if _HEX40.fullmatch(policy_resolver_commit_sha) is None:
        raise ValueError("policy_resolver_commit_sha must be 40 lowercase hex")
    if result.audit_context_sha256 != context.context_sha256:
        raise ValueError("result/context mismatch")
    if result.proposition_sha256 != context.proposition.sha256:
        raise ValueError("result/proposition mismatch")
    if result.evidence_world_sha256 != context.evidence_world.evidence_world_sha256:
        raise ValueError("result/evidence-world mismatch")

    verdict, reason = public_terminal_state(result)
    basis_ids = derive_basis_passage_ids(context, result)
    causal_ids = {passage_id for group in basis_ids for passage_id in group}

    participants: list[dict[str, Any]] = []
    ref_by_passage: dict[str, dict[str, str]] = {}
    for trace in result.traces:
        passage = context.evidence_world.passage(trace.passage_id)
        ref = {"source_id": passage.source_id, "passage_id": passage.passage_id}
        ref_by_passage[passage.passage_id] = ref
        participants.append(
            {
                "evidence_ref": ref,
                "relation": _relation_label(trace),
                "role": "causal" if trace.passage_id in causal_ids else "residual",
            }
        )

    basis_groups = [
        [ref_by_passage[passage_id] for passage_id in group]
        for group in basis_ids
    ]
    completion = (
        "assessed"
        if result.conclusion in {Conclusion.SUPPORTED, Conclusion.CONTRADICTED}
        else "not_checkable"
    )
    return {
        "profile": PROFILE,
        "contract_b": {
            "contract_version": context.evidence_world.contract_b_version,
            "bundle_id": context.evidence_world.bundle_id,
            "bundle_hash": context.evidence_world.bundle_hash,
        },
        "producer": {
            "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
            "policy_sha256": POLICY_SHA256,
            "policy_resolver_commit_sha": policy_resolver_commit_sha,
        },
        "execution": {"state": "completed"},
        "propositions": [
            {
                "proposition": {
                    "proposition_id": context.proposition.proposition_id,
                    "content_sha256": f"sha256:{context.proposition.sha256}",
                },
                "execution": {"state": "completed", "completion": completion},
                "terminal": {"verdict": verdict, "reason": reason},
                "participants": participants,
                "basis_groups": basis_groups,
            }
        ],
    }
