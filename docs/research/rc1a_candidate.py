"""RC1A bounded research-only real-execution receipt wrapper.

This module deliberately does not alter CAL v1. It accepts the exact current
AuditRequest boundary, calls the supplied unchanged run_audit delegate, returns
that exact AuditTrace object, and emits a separate research receipt.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Mapping

from claim_audit_lab.v1.models import AuditRequest, AuditTrace, Passage

_ALLOWED_POLICIES = {"ALLOW_PRIMARY_OR_SECONDARY", "PRIMARY_ONLY"}
_ALLOWED_PLAN_STATES = {"perform", "not-performed", "not-applicable"}
_ALLOWED_ASSESSOR_OUTCOMES = {"positive", "adverse", "unknown"}
_LAYER_KEYS = ("feature_extractor", "retriever", "entailer", "aggregator", "rules")


def _validate_plan(
    request: AuditRequest,
    assessment_plan: Mapping[str, str],
) -> None:
    passage_ids = {p.passage_id for p in request.passages}
    plan_ids = set(assessment_plan)
    if plan_ids != passage_ids:
        missing = sorted(passage_ids - plan_ids)
        extra = sorted(plan_ids - passage_ids)
        raise ValueError(
            "assessment receipt plan must explicitly cover every passage; "
            f"missing={missing}, extra={extra}"
        )
    invalid = {
        pid: state
        for pid, state in assessment_plan.items()
        if state not in _ALLOWED_PLAN_STATES
    }
    if invalid:
        raise ValueError(f"invalid assessment receipt plan state: {invalid}")


def _trust_level(passage: Passage) -> str:
    value = passage.source_meta.get("trust_level")
    return str(value) if value is not None else "unknown"


def _participation_for(
    assessment_state: str,
    trust_level: str,
    policy_id: str,
) -> tuple[str, str]:
    if assessment_state == "performed-adverse":
        return "excluded", "performed adverse assessment excludes item"
    if assessment_state in {"performed-unknown", "not-performed", "failed"}:
        return "unresolved", f"assessment state {assessment_state} is unresolved"
    if assessment_state == "not-applicable":
        return "residual", "assessment explicitly not applicable"
    if assessment_state != "performed-positive":
        raise ValueError(f"unknown assessment state: {assessment_state}")

    if trust_level == "primary":
        return "deciding", "performed-positive primary item accepted by policy"
    if trust_level == "secondary":
        if policy_id == "ALLOW_PRIMARY_OR_SECONDARY":
            return (
                "deciding",
                "performed-positive secondary item accepted by policy",
            )
        return (
            "residual",
            "performed-positive secondary item retained but not deciding under PRIMARY_ONLY",
        )
    return (
        "residual",
        "performed-positive non-primary/non-secondary item retained as residual",
    )


def _derive_policy_receipt(
    request: AuditRequest,
    assessments: Mapping[str, Mapping[str, Any]],
    policy_id: str,
) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    participation: dict[str, dict[str, str]] = {}
    inputs: dict[str, dict[str, str]] = {}
    effects: dict[str, dict[str, str]] = {}
    by_id = {p.passage_id: p for p in request.passages}

    for pid in by_id:
        assessment_state = str(assessments[pid]["state"])
        trust_level = _trust_level(by_id[pid])
        state, reason = _participation_for(
            assessment_state,
            trust_level,
            policy_id,
        )
        inputs[pid] = {
            "assessment_state": assessment_state,
            "trust_level": trust_level,
        }
        participation[pid] = {"state": state, "reason": reason}
        effects[pid] = {"participation": state, "reason": reason}

    return participation, {
        "id": policy_id,
        "inputs": inputs,
        "effects": effects,
    }


def _aggregation_receipt(
    request: AuditRequest,
    aggregation_mode: str | None,
) -> dict[str, Any]:
    if aggregation_mode is None:
        return {
            "state": "not-requested",
            "passage_ids": [],
            "composed_result": None,
        }
    if aggregation_mode != "no_authorized_composition":
        raise ValueError(f"unknown aggregation mode: {aggregation_mode}")
    return {
        "state": "unresolved",
        "passage_ids": [p.passage_id for p in request.passages],
        "composed_result": None,
    }


def _verdict_identity(trace: AuditTrace) -> str:
    return json.dumps(
        trace.verdict.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )


def _run_replays(
    request: AuditRequest,
    baseline: AuditTrace,
    replay_ids: tuple[str, ...],
    audit_runner: Callable[..., AuditTrace],
    layers: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    if not replay_ids:
        return {}

    passage_ids = {p.passage_id for p in request.passages}
    unknown = sorted(set(replay_ids) - passage_ids)
    if unknown:
        raise ValueError(f"causal replay passage not present in request: {unknown}")

    baseline_identity = _verdict_identity(baseline)
    basis: dict[str, dict[str, Any]] = {}
    for removed_id in replay_ids:
        intervention = request.model_copy(
            update={
                "passages": [
                    p for p in request.passages if p.passage_id != removed_id
                ]
            }
        )
        intervention_trace = audit_runner(intervention, **layers)
        intervention_identity = _verdict_identity(intervention_trace)
        basis[removed_id] = {
            "available": True,
            "necessary": baseline_identity != intervention_identity,
            "baseline_verdict": baseline.verdict.support_verdict,
            "baseline_reason": baseline.verdict.support_verdict_reason,
            "intervention_verdict": intervention_trace.verdict.support_verdict,
            "intervention_reason": (
                intervention_trace.verdict.support_verdict_reason
            ),
        }
    return basis


def _failure_execution(
    state: str,
    stage: str,
    exc: Exception,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "state": state,
        "stage": stage,
        "failure_type": type(exc).__name__,
        "failure_message": str(exc),
        **extra,
    }


def run_captured_audit(
    request: AuditRequest,
    *,
    audit_runner: Callable[..., AuditTrace],
    assessment_plan: Mapping[str, str],
    assessor: Callable[[str, Passage, AuditTrace], str],
    policy_id: str,
    aggregation_mode: str | None,
    causal_replay_ids: tuple[str, ...],
    failure_injector: Callable[[str], None] | None,
    feature_extractor: Any,
    retriever: Any,
    entailer: Any,
    aggregator: Any,
    rules: Any,
) -> dict[str, Any]:
    """Execute unchanged v1 and emit a separate typed research receipt."""

    if policy_id not in _ALLOWED_POLICIES:
        raise ValueError(f"unknown research policy: {policy_id}")
    _validate_plan(request, assessment_plan)

    layers = {
        "feature_extractor": feature_extractor,
        "retriever": retriever,
        "entailer": entailer,
        "aggregator": aggregator,
        "rules": rules,
    }
    assert set(layers) == set(_LAYER_KEYS)

    if failure_injector is not None:
        try:
            failure_injector("pre_run")
        except Exception as exc:
            assessments = {
                p.passage_id: {
                    "state": "not-performed",
                    "reason": "wrapper failed before assessment execution",
                }
                for p in request.passages
            }
            participation, policy = _derive_policy_receipt(
                request,
                assessments,
                policy_id,
            )
            return {
                "trace": None,
                "receipt": {
                    "execution": _failure_execution(
                        "wrapper_failure",
                        "pre_run",
                        exc,
                    ),
                    "assessments": assessments,
                    "participation": participation,
                    "policy": policy,
                    "aggregation": {
                        "state": "not-completed",
                        "passage_ids": [],
                        "composed_result": None,
                    },
                    "causal_basis": {},
                    "epistemic_conclusion": None,
                },
            }

    try:
        trace = audit_runner(request, **layers)
    except Exception as exc:
        return {
            "trace": None,
            "receipt": {
                "execution": _failure_execution(
                    "incomplete_execution",
                    "run_audit",
                    exc,
                ),
                "assessments": {
                    p.passage_id: {
                        "state": "not-performed",
                        "reason": "run_audit did not complete",
                    }
                    for p in request.passages
                },
                "participation": {},
                "policy": {
                    "id": policy_id,
                    "inputs": {},
                    "effects": {},
                },
                "aggregation": {
                    "state": "not-completed",
                    "passage_ids": [],
                    "composed_result": None,
                },
                "causal_basis": {},
                "epistemic_conclusion": None,
            },
        }

    assessments: dict[str, dict[str, Any]] = {}
    passages = {p.passage_id: p for p in request.passages}
    ordered_ids = [p.passage_id for p in request.passages]

    for index, pid in enumerate(ordered_ids):
        plan_state = assessment_plan[pid]
        if plan_state == "not-performed":
            assessments[pid] = {"state": "not-performed"}
            continue
        if plan_state == "not-applicable":
            assessments[pid] = {"state": "not-applicable"}
            continue

        try:
            outcome = assessor(pid, passages[pid], trace)
            if outcome not in _ALLOWED_ASSESSOR_OUTCOMES:
                raise ValueError(f"invalid assessor outcome for {pid}: {outcome}")
            assessments[pid] = {"state": f"performed-{outcome}"}
        except Exception as exc:
            assessments[pid] = {
                "state": "failed",
                "failure_type": type(exc).__name__,
                "failure_message": str(exc),
            }
            for remaining in ordered_ids[index + 1 :]:
                assessments[remaining] = {
                    "state": "not-performed",
                    "reason": "assessment execution stopped after prior failure",
                }
            participation, policy = _derive_policy_receipt(
                request,
                assessments,
                policy_id,
            )
            return {
                "trace": trace,
                "receipt": {
                    "execution": _failure_execution(
                        "assessment_failure",
                        "assessment",
                        exc,
                        passage_id=pid,
                    ),
                    "assessments": assessments,
                    "participation": participation,
                    "policy": policy,
                    "aggregation": {
                        "state": "not-completed",
                        "passage_ids": [],
                        "composed_result": None,
                    },
                    "causal_basis": {},
                    "epistemic_conclusion": None,
                },
            }

    participation, policy = _derive_policy_receipt(
        request,
        assessments,
        policy_id,
    )
    aggregation_receipt = _aggregation_receipt(request, aggregation_mode)
    causal_basis = _run_replays(
        request,
        trace,
        causal_replay_ids,
        audit_runner,
        layers,
    )

    return {
        "trace": trace,
        "receipt": {
            "execution": {"state": "successful"},
            "assessments": assessments,
            "participation": participation,
            "policy": policy,
            "aggregation": aggregation_receipt,
            "causal_basis": causal_basis,
            "epistemic_conclusion": trace.verdict.model_dump(mode="json"),
        },
    }
