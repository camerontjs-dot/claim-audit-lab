from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .engine import AuditResult, PassageTrace
from .models import AuditContext, CategoricalRelation, Conclusion, FailureCode, stable_id


CONTRACT_C_RESEARCH_SENTINEL = "research-non-deciding-rc0"
PROFILE = "cal-v1-candidate-2026-09"
_SEMANTIC_SHA = re.compile(r"^[0-9a-f]{40}$")


def _canonical_contract_c_bytes(value: dict[str, Any]) -> bytes:
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


def _result_set_identity(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("result_set_id", None)
    return "result-set:" + hashlib.sha256(_canonical_contract_c_bytes(payload)).hexdigest()


def _policy() -> dict[str, Any]:
    canonical: dict[str, Any] = {
        "profile": PROFILE,
        "semantics": "typed-source-grounded-scoreless-categorical",
        "supported_families": ["direct_event_order", "strict_comparison"],
    }
    return {
        "canonical": canonical,
        "sha256": hashlib.sha256(_canonical_contract_c_bytes(canonical)).hexdigest(),
    }


def _is_causal(result: AuditResult, trace: PassageTrace) -> bool:
    if trace.relation is None:
        return False
    relation = trace.relation.categorical_relation
    if result.conclusion is Conclusion.SUPPORTED:
        return relation is CategoricalRelation.SUPPORTS
    if result.conclusion is Conclusion.CONTRADICTED:
        return relation is CategoricalRelation.REFUTES
    if result.failure_code is FailureCode.MIXED_RELATIONS:
        return relation in {CategoricalRelation.SUPPORTS, CategoricalRelation.REFUTES}
    return relation is CategoricalRelation.UNRESOLVED


def _terminal_branch(result: AuditResult) -> str:
    if result.conclusion is Conclusion.SUPPORTED:
        return "categorical_support"
    if result.conclusion is Conclusion.CONTRADICTED:
        return "categorical_refutation"
    if result.failure_code is FailureCode.MIXED_RELATIONS:
        return "mixed_categorical_relations"
    if result.failure_code is FailureCode.UNSUPPORTED_SEMANTIC_FAMILY:
        return "unsupported_semantic_family"
    return "unresolved_categorical_relation"


def _causal_form(result: AuditResult, causal_ids: list[str]) -> str:
    if not causal_ids:
        return "redundant_non_deciding"
    if len(causal_ids) == 1:
        return "single_necessary"
    if result.failure_code is FailureCode.MIXED_RELATIONS:
        return "jointly_sufficient"
    return "independent_sufficient_alternatives"


def project_contract_c_successor(
    context: AuditContext,
    result: AuditResult,
    *,
    semantic_implementation_sha: str,
) -> dict[str, Any]:
    """Project to the exact qualified Contract C research-shadow shape.

    The wire sentinel is deliberately non-canonical. This adapter preserves the
    released Contract C structure and the qualified ``non_deciding`` channel
    delta but does not assign or imply an official successor version.
    """
    if _SEMANTIC_SHA.fullmatch(semantic_implementation_sha) is None:
        raise ValueError("semantic_implementation_sha must be 40 lowercase hex characters")
    if result.audit_context_sha256 != context.context_sha256:
        raise ValueError("result/context mismatch")
    if result.proposition_sha256 != context.proposition.sha256:
        raise ValueError("result/proposition mismatch")
    if result.evidence_world_sha256 != context.evidence_world.evidence_world_sha256:
        raise ValueError("result/evidence-world mismatch")

    contributions: list[dict[str, Any]] = []
    causal_ids: list[str] = []
    residual_ids: list[str] = []
    for trace in result.traces:
        passage = context.evidence_world.passage(trace.passage_id)
        relation = (
            trace.relation.categorical_relation if trace.relation is not None else None
        )
        if relation is CategoricalRelation.SUPPORTS:
            channel = "support"
        elif relation is CategoricalRelation.REFUTES:
            channel = "counterevidence"
        else:
            channel = "non_deciding"
        contribution_id = stable_id(
            "contribution",
            {
                "passage_id": passage.passage_id,
                "passage_sha256": passage.text_sha256,
                "source_id": passage.source_id,
                "channel": channel,
                "proposition_sha256": result.proposition_sha256,
                "evidence_world_sha256": result.evidence_world_sha256,
            },
        )
        contributions.append(
            {
                "contribution_id": contribution_id,
                "channel": channel,
                "evidence_ref": {
                    "source_id": passage.source_id,
                    "passage_id": passage.passage_id,
                    "passage_sha256": passage.text_sha256,
                },
            }
        )
        if _is_causal(result, trace):
            causal_ids.append(contribution_id)
        else:
            residual_ids.append(contribution_id)

    reported_verdict = (
        "supported"
        if result.conclusion is Conclusion.SUPPORTED
        else "contradicted"
        if result.conclusion is Conclusion.CONTRADICTED
        else "not_checkable"
    )
    completion = (
        "assessed"
        if result.conclusion in {Conclusion.SUPPORTED, Conclusion.CONTRADICTED}
        else "not_checkable"
    )
    proposition_result: dict[str, Any] = {
        "proposition": {
            "proposition_id": context.proposition.proposition_id,
            "text_sha256": context.proposition.text_sha256,
        },
        "execution": {"state": "completed", "completion": completion},
        "assessments": {
            "eligibility": {"state": "not_performed"},
            "semantic_validity": {"state": "not_performed"},
            "aperture_completeness": {"state": "not_performed"},
            "temporal_applicability": {"state": "not_performed"},
        },
        "contributions": contributions,
        "measurement": None,
        "conclusion": {
            "reported_verdict": reported_verdict,
            "terminal_branch": _terminal_branch(result),
            "causal_form": _causal_form(result, causal_ids),
            "basis_members": [
                {"namespace": "contribution", "id": contribution_id}
                for contribution_id in causal_ids
            ],
            "residual_contribution_ids": residual_ids,
            "rule_roles": [],
        },
    }
    payload: dict[str, Any] = {
        "contract_c_version": CONTRACT_C_RESEARCH_SENTINEL,
        "input": {
            "contract_b": {
                "contract_version": context.evidence_world.contract_b_version,
                "bundle_id": context.evidence_world.bundle_id,
                "bundle_hash": context.evidence_world.bundle_hash,
            }
        },
        "producer": {
            "semantic_implementation_sha": semantic_implementation_sha,
            "policy": _policy(),
        },
        "execution": {"state": "completed"},
        "propositions": [proposition_result],
    }
    payload["result_set_id"] = _result_set_identity(payload)
    return payload
