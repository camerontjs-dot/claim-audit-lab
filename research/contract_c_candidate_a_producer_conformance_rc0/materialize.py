from __future__ import annotations

from itertools import combinations
from typing import Any

from claim_audit_lab.cal_v1_candidate import (
    AuditContext,
    AuditResult,
    CategoricalRelation,
    Conclusion,
    FailureCode,
    PassageTrace,
    compose,
)

PROFILE = "contract-c-successor-candidate-a-rc1-research"
POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"
POLICY_RESOLVER_COMMIT = "43b571464734325277374ee81098553fb7c1b944"


class UnrepresentablePublicReason(ValueError):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def public_terminal_state(result: AuditResult) -> tuple[str, str]:
    """Return Candidate-A public terminal semantics from already-owned CAL state.

    This function does not perform measurement, semantic completion, authority
    evaluation, or relation derivation. It only interprets the frozen terminal
    conclusion/failure plus already-derived categorical relation records.
    """
    if result.conclusion is Conclusion.SUPPORTED:
        return "supported", "categorical_support"
    if result.conclusion is Conclusion.CONTRADICTED:
        return "contradicted", "categorical_refutation"
    if result.failure_code is FailureCode.MIXED_RELATIONS:
        return "not_checkable", "MIXED_RELATIONS"
    if result.failure_code is FailureCode.RELATION_UNRESOLVED:
        has_unresolved_relation = any(
            trace.relation is not None
            and trace.relation.categorical_relation is CategoricalRelation.UNRESOLVED
            for trace in result.traces
        )
        return (
            ("not_checkable", "unresolved_categorical_relation")
            if has_unresolved_relation
            else ("not_checkable", "no_deciding_relation")
        )
    reason = result.failure_code.value if result.failure_code is not None else result.conclusion.value
    raise UnrepresentablePublicReason(reason)


def _same_public_terminal(left: AuditResult, right: AuditResult) -> bool:
    return public_terminal_state(left) == public_terminal_state(right)


def derive_basis_passage_ids(
    context: AuditContext,
    result: AuditResult,
) -> tuple[tuple[str, ...], ...]:
    """Derive inclusion-minimal sufficient passage sets via compose-only replay."""
    _, reason = public_terminal_state(result)
    if reason == "no_deciding_relation":
        return ()

    traces = tuple(result.traces)
    minimal: list[frozenset[str]] = []
    for size in range(1, len(traces) + 1):
        for indexes in combinations(range(len(traces)), size):
            subset: tuple[PassageTrace, ...] = tuple(traces[index] for index in indexes)
            replay = compose(context, subset)
            if not _same_public_terminal(result, replay):
                continue
            passage_ids = frozenset(trace.passage_id for trace in subset)
            if any(existing < passage_ids or existing == passage_ids for existing in minimal):
                continue
            minimal.append(passage_ids)

    return tuple(sorted((tuple(sorted(group)) for group in minimal)))


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
    semantic_implementation_sha: str,
) -> dict[str, Any]:
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
            "semantic_implementation_sha": semantic_implementation_sha,
            "policy_sha256": POLICY_SHA256,
            "policy_resolver_commit_sha": POLICY_RESOLVER_COMMIT,
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
