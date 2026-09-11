from __future__ import annotations

from typing import Any

from .engine import AuditResult
from .models import AuditContext, CategoricalRelation, Conclusion, stable_id


CONTRACT_C_RESEARCH_SENTINEL = "research-non-deciding-rc0"


def project_contract_c_successor(
    context: AuditContext, result: AuditResult
) -> dict[str, Any]:
    """Project to the qualified Contract C research successor shape.

    The sentinel is deliberately non-canonical. This adapter does not assign or
    imply an official Contract C successor version.
    """
    if result.audit_context_sha256 != context.context_sha256:
        raise ValueError("result/context mismatch")
    contributions: list[dict[str, Any]] = []
    causal_basis: list[str] = []
    residual_basis: list[str] = []
    for trace in result.traces:
        relation = (
            trace.relation.categorical_relation if trace.relation is not None else None
        )
        if relation is CategoricalRelation.SUPPORTS:
            channel = "support"
            basis_class = "causal"
        elif relation is CategoricalRelation.REFUTES:
            channel = "counterevidence"
            basis_class = "causal"
        else:
            channel = "non_deciding"
            basis_class = "causal" if trace.relation is not None else "residual"
        contribution_id = stable_id(
            "contribution",
            {
                "passage_id": trace.passage_id,
                "channel": channel,
                "basis_class": basis_class,
                "proposition_sha256": result.proposition_sha256,
                "evidence_world_sha256": result.evidence_world_sha256,
            },
        )
        contributions.append(
            {
                "contribution_id": contribution_id,
                "channel": channel,
                "basis_class": basis_class,
                "evidence_ref": {
                    "contract_b_version": context.evidence_world.contract_b_version,
                    "bundle_id": context.evidence_world.bundle_id,
                    "bundle_hash": context.evidence_world.bundle_hash,
                    "passage_id": trace.passage_id,
                },
            }
        )
        if basis_class == "causal":
            causal_basis.append(contribution_id)
        else:
            residual_basis.append(contribution_id)
    if result.conclusion is Conclusion.SUPPORTED:
        state = "supported"
    elif result.conclusion is Conclusion.CONTRADICTED:
        state = "contradicted"
    else:
        state = "not_checkable"
    causal_form = (
        "independent_sufficient_alternatives" if len(causal_basis) > 1 else "single"
    )
    payload: dict[str, Any] = {
        "contract_c_version": CONTRACT_C_RESEARCH_SENTINEL,
        "proposition_id": context.proposition.proposition_id,
        "proposition_sha256": context.proposition.sha256,
        "contract_b_binding": {
            "contract_b_version": context.evidence_world.contract_b_version,
            "bundle_id": context.evidence_world.bundle_id,
            "bundle_hash": context.evidence_world.bundle_hash,
            "evidence_world_sha256": context.evidence_world.evidence_world_sha256,
        },
        "state": state,
        "contributions": contributions,
        "basis": {
            "causal_contribution_ids": causal_basis,
            "residual_contribution_ids": residual_basis,
            "causal_form": causal_form,
        },
    }
    payload["result_set_id"] = stable_id("result-set", payload)
    return payload
