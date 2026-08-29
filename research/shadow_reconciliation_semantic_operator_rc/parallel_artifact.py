"""Research-only parallel epistemic artifact built beside AuditTrace.

The emitter consumes the predecessor shadow comparison record, which itself is
receipt-bound to a real ``run_default_audit`` execution.  It does not read the
legacy verdict to construct epistemic state and it does not change Contract C.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class _Strict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class ExecutionState(_Strict):
    status: Literal["completed", "failed"]
    execution_head_sha: str | None = None
    failure_class: str | None = None
    failure_detail: str | None = None

    @model_validator(mode="after")
    def _pair(self) -> "ExecutionState":
        if self.status == "completed" and (self.failure_class or self.failure_detail):
            raise ValueError("completed execution may not carry failure fields")
        if self.status == "failed" and not self.failure_class:
            raise ValueError("failed execution requires a failure class")
        return self


class ParallelEpistemicArtifact(_Strict):
    schema_version: Literal["cal-parallel-epistemic-artifact-research-v0.1"] = (
        "cal-parallel-epistemic-artifact-research-v0.1"
    )
    authority: Literal["non_authoritative_research"] = "non_authoritative_research"
    claim_id: str = Field(min_length=1)
    request_receipt_sha256: str | None = None
    audit_trace_receipt_sha256: str | None = None
    execution: ExecutionState
    source_passage_ids: tuple[str, ...] = ()
    model_measurements: tuple[dict[str, Any], ...] = ()
    raw_evidence_state: dict[str, Any] | None = None
    eligible_evidence_state: dict[str, Any] | None = None
    semantic_valid_evidence_state: dict[str, Any] | None = None
    contribution_ledger: tuple[dict[str, Any], ...] = ()
    apertures: tuple[dict[str, Any], ...] = ()
    stage_receipts: tuple[dict[str, Any], ...] = ()
    decision_or_abstention: dict[str, Any] | None = None
    operator_receipts: tuple[dict[str, Any], ...] = ()
    unknowns: tuple[dict[str, str], ...] = ()
    causal_basis_contribution_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _execution_boundary(self) -> "ParallelEpistemicArtifact":
        if self.execution.status == "failed":
            epistemic_payload = (
                self.raw_evidence_state,
                self.eligible_evidence_state,
                self.semantic_valid_evidence_state,
                self.decision_or_abstention,
            )
            if any(item is not None for item in epistemic_payload):
                raise ValueError("execution failure may not masquerade as an epistemic result")
        return self


def _unknowns(candidate: dict[str, Any]) -> tuple[dict[str, str], ...]:
    rows: list[dict[str, str]] = []
    for contribution in candidate["inputs"]["contributions"]:
        if contribution["eligibility"]["status"] == "unknown":
            rows.append(
                {
                    "kind": "eligibility",
                    "id": str(contribution["contribution_id"]),
                    "reason": str(contribution["eligibility"]["reason"]),
                }
            )
        if contribution["validity"]["status"] == "unknown":
            rows.append(
                {
                    "kind": "semantic_validity",
                    "id": str(contribution["contribution_id"]),
                    "reason": str(contribution["validity"]["reason"]),
                }
            )
    for aperture in candidate["inputs"]["apertures"]:
        if aperture["status"] != "complete":
            rows.append(
                {
                    "kind": "aperture",
                    "id": str(aperture["channel"]),
                    "reason": str(aperture["reason"]),
                }
            )
    if candidate["inputs"]["scope_status"] == "unknown":
        rows.append({"kind": "scope", "id": "claim", "reason": "claim scope is unresolved"})
    return tuple(rows)


def build_completed_artifact(
    comparison: dict[str, Any], request: dict[str, Any], *, execution_head_sha: str
) -> ParallelEpistemicArtifact:
    """Project only already-observed fields from one real-execution comparison row."""
    explicit = comparison["explicit"]["candidate"]
    legacy = comparison["legacy"]
    request_passage_ids = tuple(
        sorted(str(item["passage_id"]) for item in request["passages"])
    )
    # Exact source IDs come from the separately hash-bound original AuditRequest.
    operators = tuple(
        {
            "contribution_id": str(item["contribution_id"]),
            "operator": str(item["validity"]["operator"]),
            "status": str(item["validity"]["status"]),
            "reason": str(item["validity"]["reason"]),
            "evidence_path": str(item["validity"]["evidence_path"]),
            "receipt_sha256": str(item["validity"]["receipt_sha256"]),
        }
        for item in explicit["inputs"]["contributions"]
    )
    decision = explicit["decision"]
    return ParallelEpistemicArtifact(
        claim_id=str(comparison["claim_id"]),
        request_receipt_sha256=str(comparison["request_receipt_sha256"]),
        audit_trace_receipt_sha256=str(comparison["trace_receipt_sha256"]),
        execution=ExecutionState(status="completed", execution_head_sha=execution_head_sha),
        source_passage_ids=request_passage_ids,
        model_measurements=tuple(dict(item) for item in legacy["nli_measurements"]),
        raw_evidence_state=dict(explicit["raw"]),
        eligible_evidence_state=dict(explicit["eligible"]),
        semantic_valid_evidence_state=dict(explicit["valid"]),
        contribution_ledger=tuple(dict(item) for item in explicit["inputs"]["contributions"]),
        apertures=tuple(dict(item) for item in explicit["inputs"]["apertures"]),
        stage_receipts=tuple(dict(item) for item in explicit["inputs"]["stage_receipts"]),
        decision_or_abstention=dict(decision),
        operator_receipts=operators,
        unknowns=_unknowns(explicit),
        causal_basis_contribution_ids=tuple(decision["basis_contribution_ids"]),
    )


def build_failure_artifact(
    *, claim_id: str, failure_class: str, failure_detail: str, execution_head_sha: str | None = None
) -> ParallelEpistemicArtifact:
    """Represent execution failure without fabricating an epistemic abstention."""
    return ParallelEpistemicArtifact(
        claim_id=claim_id,
        execution=ExecutionState(
            status="failed",
            execution_head_sha=execution_head_sha,
            failure_class=failure_class,
            failure_detail=failure_detail,
        ),
    )
