"""Deterministic CAL V1 native result and audit-artifact rendering."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from claim_audit_lab.production_v1 import (
    DISTRIBUTION_VERSION,
    PROFILE,
    SEMANTIC_IMPLEMENTATION_SHA,
)
from claim_audit_lab.production_v1.semantic.authority import AuthorityReceipt
from claim_audit_lab.production_v1.semantic.engine import AuditResult, PassageTrace
from claim_audit_lab.production_v1.semantic.measurements import MeasurementReceipt
from claim_audit_lab.production_v1.semantic.models import AuditContext, CategoricalRelation


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        + b"\n"
    )


def audit_context_record(context: AuditContext) -> dict[str, Any]:
    """Render the complete immutable semantic context used by CAL."""
    return {
        "schema": "cal-v1-audit-context-v1",
        "audit_context_sha256": context.context_sha256,
        "original_claim": context.original_claim,
        "proposition": {
            "proposition_id": context.proposition.proposition_id,
            "text_sha256": context.proposition.text_sha256,
            "semantic_family": context.proposition.semantic_family.value,
            "fields": context.proposition.field_map(),
            "proposition_sha256": context.proposition.sha256,
        },
        "evidence_world": {
            "contract_b_version": context.evidence_world.contract_b_version,
            "bundle_id": context.evidence_world.bundle_id,
            "bundle_hash": context.evidence_world.bundle_hash,
            "evidence_world_sha256": context.evidence_world.evidence_world_sha256,
            "aperture_observation": context.evidence_world.aperture_observation(),
            "root_id": context.evidence_world.root_id,
            "child_id": context.evidence_world.child_id,
            "admitted_passages": [
                {
                    "passage_id": passage.passage_id,
                    "source_id": passage.source_id,
                    "text": passage.text,
                    "text_sha256": passage.text_sha256,
                    "source_sha256": passage.source_sha256,
                }
                for passage in context.evidence_world.admitted_passages
            ],
        },
    }


def _observed_spans(measurement: MeasurementReceipt) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    raw = measurement.raw_measurement()
    proposals = raw.get("proposals")
    if not isinstance(proposals, list):
        return spans
    for proposal in proposals:
        if not isinstance(proposal, dict):
            continue
        for role, key in (("comparison_cue", "cue_span"), ("temporal_cue", "span")):
            value = proposal.get(key)
            if (
                isinstance(value, list)
                and len(value) == 2
                and all(isinstance(part, int) for part in value)
            ):
                spans.append({"role": role, "start": value[0], "end": value[1]})
    return spans


def _measurement_record(
    context: AuditContext, measurement: MeasurementReceipt | None
) -> dict[str, Any] | None:
    if measurement is None:
        return None
    consumed_spans = [
        {
            "passage_id": passage_id,
            "start": 0,
            "end": len(context.evidence_world.passage(passage_id).text),
        }
        for passage_id in measurement.consumed_passage_ids
    ]
    return {
        "receipt_id": measurement.receipt_id,
        "audit_context_sha256": measurement.audit_context_sha256,
        "semantic_family": measurement.semantic_family.value,
        "instrument_id": measurement.instrument_id,
        "instrument_version": measurement.instrument_version,
        "available_passage_ids": list(measurement.available_passage_ids),
        "consumed_passage_ids": list(measurement.consumed_passage_ids),
        "consumed_spans": consumed_spans,
        "observed_semantic_spans": _observed_spans(measurement),
        "raw_measurement": measurement.raw_measurement(),
        "diagnostics": dict(measurement.diagnostics),
    }


def _authority_record(authority: AuthorityReceipt | None) -> dict[str, Any] | None:
    if authority is None:
        return None
    atom = authority.atom
    return {
        "authority_id": authority.authority_id,
        "audit_context_sha256": authority.audit_context_sha256,
        "evidence_world_sha256": authority.evidence_world_sha256,
        "status": authority.status,
        "reason": authority.reason,
        "atom": {
            "atom_id": atom.atom_id,
            "semantic_family": atom.semantic_family.value,
            "audit_context_sha256": atom.audit_context_sha256,
            "evidence_world_sha256": atom.evidence_world_sha256,
            "passage_id": atom.passage_id,
            "source_id": atom.source_id,
            "fields": atom.field_map(),
            "measurement_receipt_id": atom.measurement_receipt_id,
        },
    }


def _relation_record(trace: PassageTrace) -> dict[str, Any] | None:
    if trace.relation is None:
        return None
    return {
        "relation_id": trace.relation.relation_id,
        "categorical_relation": trace.relation.categorical_relation.value,
        "audit_context_sha256": trace.relation.audit_context_sha256,
        "evidence_world_sha256": trace.relation.evidence_world_sha256,
        "proposition_sha256": trace.relation.proposition_sha256,
        "authority_id": trace.relation.authority_id,
        "passage_id": trace.relation.passage_id,
    }


def _trace_record(context: AuditContext, trace: PassageTrace) -> dict[str, Any]:
    return {
        "passage_id": trace.passage_id,
        "measurement": _measurement_record(context, trace.measurement),
        "authority": _authority_record(trace.authority),
        "relation": _relation_record(trace),
        "failure_code": None if trace.failure_code is None else trace.failure_code.value,
        "detail": trace.detail,
    }


def _composition_record(result: AuditResult) -> dict[str, Any]:
    relations = [trace.relation for trace in result.traces if trace.relation is not None]
    deciding = [
        relation.relation_id
        for relation in relations
        if relation.categorical_relation
        in {CategoricalRelation.SUPPORTS, CategoricalRelation.REFUTES}
    ]
    non_deciding = [
        relation.relation_id
        for relation in relations
        if relation.categorical_relation
        in {CategoricalRelation.IRRELEVANT, CategoricalRelation.UNRESOLVED}
    ]
    return {
        "rule_id": "scoreless-categorical-v1",
        "precedence": [
            "UNRESOLVED",
            "SUPPORT_REFUTE_CONFLICT",
            "SUPPORTS",
            "REFUTES",
            "NO_DECIDING_RELATION",
        ],
        "audit_context_sha256": result.audit_context_sha256,
        "evidence_world_sha256": result.evidence_world_sha256,
        "proposition_sha256": result.proposition_sha256,
        "relation_ids": [relation.relation_id for relation in relations],
        "relation_categories": sorted(
            {relation.categorical_relation.value for relation in relations}
        ),
        "deciding_relation_ids": deciding,
        "non_deciding_relation_ids": non_deciding,
        "conclusion": result.conclusion.value,
        "failure_code": None if result.failure_code is None else result.failure_code.value,
    }


def result_record(
    context: AuditContext,
    result: AuditResult,
    *,
    input_binding: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the native immutable CAL result receipt."""
    measurements = [
        record
        for trace in result.traces
        if (record := _measurement_record(context, trace.measurement)) is not None
    ]
    authorities = [
        record
        for trace in result.traces
        if (record := _authority_record(trace.authority)) is not None
    ]
    relations = [
        record for trace in result.traces if (record := _relation_record(trace)) is not None
    ]
    return {
        "schema": "cal-v1-result-v2",
        "profile": PROFILE,
        "distribution_version": DISTRIBUTION_VERSION,
        "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
        "input": dict(input_binding),
        "original_claim": context.original_claim,
        "proposition": {
            "proposition_id": context.proposition.proposition_id,
            "text_sha256": context.proposition.text_sha256,
            "semantic_family": result.semantic_family.value,
            "fields": context.proposition.field_map(),
            "proposition_sha256": result.proposition_sha256,
        },
        "evidence_world": {
            "contract_b_version": context.evidence_world.contract_b_version,
            "bundle_id": context.evidence_world.bundle_id,
            "bundle_hash": context.evidence_world.bundle_hash,
            "evidence_world_sha256": result.evidence_world_sha256,
            "audit_context_sha256": result.audit_context_sha256,
            "aperture_observation": context.evidence_world.aperture_observation(),
            "admitted_passage_ids": [
                passage.passage_id for passage in context.evidence_world.admitted_passages
            ],
            "available_but_unused_passage_ids": [
                passage.passage_id
                for passage in context.evidence_world.admitted_passages
                if all(
                    trace.measurement is None
                    or passage.passage_id not in trace.measurement.consumed_passage_ids
                    for trace in result.traces
                )
            ],
        },
        "measurements": measurements,
        "authorities": authorities,
        "relations": relations,
        "composition": _composition_record(result),
        "result": {
            "conclusion": result.conclusion.value,
            "failure_code": None if result.failure_code is None else result.failure_code.value,
            "deciding_passage_ids": list(result.deciding_passage_ids),
            "non_deciding_passage_ids": list(result.non_deciding_passage_ids),
            "traces": [_trace_record(context, trace) for trace in result.traces],
        },
        "contract_c_handoff": {
            "state": "not_emitted",
            "owner": "apparatus-contracts",
            "reason": "separate_compose_only_versioned_handoff_layer",
        },
        "authorization": {
            "state": "not_evaluated",
            "automatic_action_allowed": False,
        },
    }


def render_markdown(context: AuditContext, result: AuditResult) -> str:
    """Render a deterministic human-readable report."""
    aperture = json.dumps(
        context.evidence_world.aperture_observation(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    composition = _composition_record(result)
    lines = [
        "# Claim Audit Lab V1 integration-candidate result",
        "",
        f"- Profile: '{PROFILE}'",
        f"- Distribution metadata: 'claim-audit-lab {DISTRIBUTION_VERSION}'",
        f"- Semantic implementation: '{SEMANTIC_IMPLEMENTATION_SHA}'",
        f"- Proposition: {context.original_claim}",
        f"- Proposition ID: '{context.proposition.proposition_id}'",
        f"- Proposition text SHA-256: '{context.proposition.text_sha256}'",
        f"- Semantic family: '{result.semantic_family.value}'",
        f"- Conclusion: '{result.conclusion.value}'",
        (
            f"- Failure localization: '{result.failure_code.value}'"
            if result.failure_code is not None
            else "- Failure localization: none"
        ),
        (
            f"- Contract B: '{context.evidence_world.contract_b_version}' / "
            f"'{context.evidence_world.bundle_id}'"
        ),
        f"- Contract B bundle hash: '{context.evidence_world.bundle_hash}'",
        f"- Evidence-world SHA-256: '{result.evidence_world_sha256}'",
        f"- Composition rule: '{composition['rule_id']}'",
        "- Contract C handoff: 'not_emitted' (separate compose-only versioned layer).",
        "- Authorization: 'not_evaluated'; automatic action is not allowed.",
        "- Limitation: CAL decides only within the supported semantic envelope "
        "and admitted evidence.",
        "",
        "## Upstream aperture observation",
        "",
        "```json",
        aperture,
        "```",
        "",
        "## Evidence trace",
        "",
    ]
    for trace in result.traces:
        role = "non_deciding"
        if trace.relation is not None:
            if trace.relation.categorical_relation is CategoricalRelation.SUPPORTS:
                role = "support"
            elif trace.relation.categorical_relation is CategoricalRelation.REFUTES:
                role = "counterevidence"
        passage = context.evidence_world.passage(trace.passage_id)
        lines.extend(
            [
                f"### '{trace.passage_id}': {role}",
                "",
                passage.text,
                "",
                f"Source: '{passage.source_id}'; passage SHA-256: '{passage.text_sha256}'.",
                (
                    f"Measurement: '{trace.measurement.instrument_id}' / "
                    f"'{trace.measurement.instrument_version}' / "
                    f"receipt '{trace.measurement.receipt_id}'."
                    if trace.measurement is not None
                    else "Measurement: not performed."
                ),
                (
                    f"Authority: '{trace.authority.authority_id}'."
                    if trace.authority is not None
                    else "Authority: not established."
                ),
                (
                    "Relation: "
                    f"'{trace.relation.categorical_relation.value}' / "
                    f"'{trace.relation.relation_id}'."
                    if trace.relation is not None
                    else "Relation: unresolved/not derived."
                ),
                (
                    f"Failure localization: '{trace.failure_code.value}'."
                    if trace.failure_code is not None
                    else "Failure localization: none."
                ),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "audit_context_record",
    "canonical_json_bytes",
    "render_markdown",
    "result_record",
]
