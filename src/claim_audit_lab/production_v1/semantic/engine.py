from __future__ import annotations

from dataclasses import dataclass

from .authority import AuthorityReceipt, AuthorityRefusal
from .measurements import MeasurementReceipt
from .models import (
    AuditContext,
    CategoricalRelation,
    Conclusion,
    FailureCode,
    SemanticFamily,
)
from .plugins import DEFAULT_FAMILY_REGISTRY, SemanticFamilyRegistry
from .relations import BoundRelation, RelationRefusal


@dataclass(frozen=True, slots=True)
class PassageTrace:
    passage_id: str
    measurement: MeasurementReceipt | None
    authority: AuthorityReceipt | None
    relation: BoundRelation | None
    failure_code: FailureCode | None
    detail: str | None


@dataclass(frozen=True, slots=True)
class AuditResult:
    conclusion: Conclusion
    failure_code: FailureCode | None
    semantic_family: SemanticFamily
    audit_context_sha256: str
    evidence_world_sha256: str
    proposition_sha256: str
    traces: tuple[PassageTrace, ...]

    @property
    def deciding_passage_ids(self) -> tuple[str, ...]:
        return tuple(
            trace.passage_id
            for trace in self.traces
            if trace.relation is not None
            and trace.relation.categorical_relation
            in {CategoricalRelation.SUPPORTS, CategoricalRelation.REFUTES}
        )

    @property
    def non_deciding_passage_ids(self) -> tuple[str, ...]:
        deciding = set(self.deciding_passage_ids)
        return tuple(trace.passage_id for trace in self.traces if trace.passage_id not in deciding)


def _failure_from_authority(code: str) -> FailureCode:
    if code == "SOURCE_COMPLETION_FAILED":
        return FailureCode.SOURCE_COMPLETION_FAILED
    return FailureCode.SEMANTIC_AUTHORITY_UNRESOLVED


def _unsupported_result(context: AuditContext) -> AuditResult:
    traces = tuple(
        PassageTrace(
            passage_id=passage.passage_id,
            measurement=None,
            authority=None,
            relation=None,
            failure_code=FailureCode.UNSUPPORTED_SEMANTIC_FAMILY,
            detail=context.proposition.semantic_family.value,
        )
        for passage in context.evidence_world.admitted_passages
    )
    return AuditResult(
        conclusion=Conclusion.NOT_CHECKABLE,
        failure_code=FailureCode.UNSUPPORTED_SEMANTIC_FAMILY,
        semantic_family=context.proposition.semantic_family,
        audit_context_sha256=context.context_sha256,
        evidence_world_sha256=context.evidence_world.evidence_world_sha256,
        proposition_sha256=context.proposition.sha256,
        traces=traces,
    )


def _failure_without_relation(traces: tuple[PassageTrace, ...]) -> FailureCode:
    """Localize the deepest observed stage failure when no relation was derived."""
    observed = {trace.failure_code for trace in traces if trace.failure_code is not None}
    for code in (
        FailureCode.PROPOSITION_BINDING_FAILED,
        FailureCode.COMMON_EVIDENCE_WORLD_MISMATCH,
        FailureCode.SEMANTIC_AUTHORITY_UNRESOLVED,
        FailureCode.SOURCE_COMPLETION_FAILED,
        FailureCode.MEASUREMENT_MISS,
        FailureCode.MEASUREMENT_NOT_APPLICABLE,
        FailureCode.EVIDENCE_NOT_ADMITTED,
        FailureCode.UPSTREAM_APERTURE_INSUFFICIENT,
    ):
        if code in observed:
            return code
    return FailureCode.NO_DECIDING_RELATION


def compose(context: AuditContext, traces: tuple[PassageTrace, ...]) -> AuditResult:
    relations = tuple(trace.relation for trace in traces if trace.relation is not None)
    for relation in relations:
        if relation.audit_context_sha256 != context.context_sha256:
            raise RelationRefusal("PROPOSITION_BINDING_FAILED", "relation/context mismatch")
        if relation.proposition_sha256 != context.proposition.sha256:
            raise RelationRefusal("PROPOSITION_BINDING_FAILED", "relation/proposition mismatch")
        if relation.evidence_world_sha256 != context.evidence_world.evidence_world_sha256:
            raise RelationRefusal(
                "COMMON_EVIDENCE_WORLD_MISMATCH", "cross-world relation composition"
            )
    categories = {relation.categorical_relation for relation in relations}
    # PR #97 established that any unresolved relation prevents a terminal
    # support/refute conclusion. This check intentionally precedes conflict and
    # support/refute selection so unresolved evidence cannot be silently ignored.
    if CategoricalRelation.UNRESOLVED in categories:
        conclusion = Conclusion.NOT_CHECKABLE
        failure = FailureCode.RELATION_UNRESOLVED
    elif CategoricalRelation.SUPPORTS in categories and CategoricalRelation.REFUTES in categories:
        conclusion = Conclusion.NOT_CHECKABLE
        failure = FailureCode.MIXED_RELATIONS
    elif CategoricalRelation.SUPPORTS in categories:
        conclusion = Conclusion.SUPPORTED
        failure = None
    elif CategoricalRelation.REFUTES in categories:
        conclusion = Conclusion.CONTRADICTED
        failure = None
    elif relations:
        conclusion = Conclusion.NOT_CHECKABLE
        failure = FailureCode.NO_DECIDING_RELATION
    else:
        conclusion = Conclusion.NOT_CHECKABLE
        failure = _failure_without_relation(traces)
    return AuditResult(
        conclusion=conclusion,
        failure_code=failure,
        semantic_family=context.proposition.semantic_family,
        audit_context_sha256=context.context_sha256,
        evidence_world_sha256=context.evidence_world.evidence_world_sha256,
        proposition_sha256=context.proposition.sha256,
        traces=traces,
    )


def audit(
    context: AuditContext,
    *,
    registry: SemanticFamilyRegistry = DEFAULT_FAMILY_REGISTRY,
) -> AuditResult:
    context.verify()
    family = context.proposition.semantic_family
    plugin = registry.get(family)
    if plugin is None:
        return _unsupported_result(context)
    traces: list[PassageTrace] = []
    for passage in context.evidence_world.admitted_passages:
        receipt = plugin.measure(context, passage.passage_id)
        raw = receipt.raw_measurement()
        if raw.get("status") != "CLAIMED":
            code = (
                FailureCode.MEASUREMENT_NOT_APPLICABLE
                if raw.get("status") == "NOT_APPLICABLE"
                else FailureCode.MEASUREMENT_MISS
            )
            traces.append(
                PassageTrace(
                    passage.passage_id,
                    receipt,
                    None,
                    None,
                    code,
                    str(raw.get("status")),
                )
            )
            continue
        try:
            authority = plugin.warrant(context, receipt, passage.passage_id)
        except AuthorityRefusal as exc:
            traces.append(
                PassageTrace(
                    passage.passage_id,
                    receipt,
                    None,
                    None,
                    _failure_from_authority(exc.code),
                    exc.detail,
                )
            )
            continue
        try:
            relation = plugin.relate(context, authority)
        except RelationRefusal as exc:
            code = (
                FailureCode.PROPOSITION_BINDING_FAILED
                if exc.code == "PROPOSITION_BINDING_FAILED"
                else FailureCode.COMMON_EVIDENCE_WORLD_MISMATCH
                if exc.code == "COMMON_EVIDENCE_WORLD_MISMATCH"
                else FailureCode.RELATION_UNRESOLVED
            )
            traces.append(
                PassageTrace(
                    passage.passage_id,
                    receipt,
                    authority,
                    None,
                    code,
                    exc.detail,
                )
            )
            continue
        traces.append(PassageTrace(passage.passage_id, receipt, authority, relation, None, None))
    return compose(context, tuple(traces))
