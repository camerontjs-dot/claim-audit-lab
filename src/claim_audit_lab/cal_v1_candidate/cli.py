from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from .engine import AuditResult, audit
from .models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)
from .projection import project_contract_c_successor
from .report import render_markdown


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return cast(Mapping[str, Any], value)


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def semantic_implementation_sha_from_packet(packet: Mapping[str, Any]) -> str:
    producer = _object(packet.get("producer"), "producer")
    return _string(
        producer.get("semantic_implementation_sha"),
        "producer.semantic_implementation_sha",
    )


def context_from_packet(packet: Mapping[str, Any]) -> AuditContext:
    proposition_raw = _object(packet.get("proposition"), "proposition")
    family = SemanticFamily(
        _string(proposition_raw.get("semantic_family"), "proposition.semantic_family")
    )
    fields_raw = _object(proposition_raw.get("fields"), "proposition.fields")
    fields = {str(key): _string(value, f"proposition.fields.{key}") for key, value in fields_raw.items()}
    proposition = TypedProposition.create(
        _string(proposition_raw.get("proposition_id"), "proposition.proposition_id"),
        family,
        fields,
        text_sha256=_string(proposition_raw.get("text_sha256"), "proposition.text_sha256"),
    )

    world_raw = _object(packet.get("evidence_world"), "evidence_world")
    passage_values = world_raw.get("admitted_passages")
    if not isinstance(passage_values, list):
        raise ValueError("evidence_world.admitted_passages must be an array")
    passages: list[AdmittedPassage] = []
    for index, value in enumerate(passage_values):
        row = _object(value, f"admitted_passages[{index}]")
        passage = AdmittedPassage(
            passage_id=_string(row.get("passage_id"), f"passages[{index}].passage_id"),
            source_id=_string(row.get("source_id"), f"passages[{index}].source_id"),
            text=_string(row.get("text"), f"passages[{index}].text"),
            text_sha256=_string(row.get("text_sha256"), f"passages[{index}].text_sha256"),
            source_sha256=_string(row.get("source_sha256"), f"passages[{index}].source_sha256"),
        )
        passage.verify()
        passages.append(passage)

    root_value = world_raw.get("root_id")
    child_value = world_raw.get("child_id")
    root_id = None if root_value is None else _string(root_value, "evidence_world.root_id")
    child_id = None if child_value is None else _string(child_value, "evidence_world.child_id")
    aperture_observation = _object(
        world_raw.get("aperture_observation"), "evidence_world.aperture_observation"
    )
    world = EvidenceWorld.create(
        contract_b_version=_string(
            world_raw.get("contract_b_version"), "evidence_world.contract_b_version"
        ),
        bundle_id=_string(world_raw.get("bundle_id"), "evidence_world.bundle_id"),
        bundle_hash=_string(world_raw.get("bundle_hash"), "evidence_world.bundle_hash"),
        admitted_passages=tuple(passages),
        aperture_observation=aperture_observation,
        root_id=root_id,
        child_id=child_id,
    )
    context = AuditContext(
        original_claim=_string(packet.get("original_claim"), "original_claim"),
        proposition=proposition,
        evidence_world=world,
    )
    context.verify()
    return context


def result_dict(
    context: AuditContext,
    result: AuditResult,
    *,
    semantic_implementation_sha: str,
) -> dict[str, Any]:
    traces: list[dict[str, Any]] = []
    for trace in result.traces:
        relation = None
        if trace.relation is not None:
            relation = {
                "relation_id": trace.relation.relation_id,
                "categorical_relation": trace.relation.categorical_relation.value,
                "authority_id": trace.relation.authority_id,
            }
        traces.append(
            {
                "passage_id": trace.passage_id,
                "measurement_receipt_id": (
                    None if trace.measurement is None else trace.measurement.receipt_id
                ),
                "available_passage_ids": (
                    []
                    if trace.measurement is None
                    else list(trace.measurement.available_passage_ids)
                ),
                "consumed_passage_ids": (
                    []
                    if trace.measurement is None
                    else list(trace.measurement.consumed_passage_ids)
                ),
                "authority_id": (None if trace.authority is None else trace.authority.authority_id),
                "relation": relation,
                "failure_code": (None if trace.failure_code is None else trace.failure_code.value),
                "detail": trace.detail,
            }
        )
    return {
        "profile": "cal-v1-candidate-2026-09",
        "original_claim": context.original_claim,
        "proposition_id": context.proposition.proposition_id,
        "proposition_text_sha256": context.proposition.text_sha256,
        "proposition_sha256": result.proposition_sha256,
        "semantic_family": result.semantic_family.value,
        "conclusion": result.conclusion.value,
        "failure_code": None if result.failure_code is None else result.failure_code.value,
        "audit_context_sha256": result.audit_context_sha256,
        "evidence_world_sha256": result.evidence_world_sha256,
        "aperture_observation": context.evidence_world.aperture_observation(),
        "traces": traces,
        "contract_c_candidate": project_contract_c_successor(
            context,
            result,
            semantic_implementation_sha=semantic_implementation_sha,
        ),
    }


def run_packet(
    packet: Mapping[str, Any],
) -> tuple[AuditContext, AuditResult, str]:
    semantic_sha = semantic_implementation_sha_from_packet(packet)
    context = context_from_packet(packet)
    return context, audit(context), semantic_sha


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the maintained research-backed CAL V1 candidate."
    )
    parser.add_argument("packet", type=Path)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--report-out", type=Path, required=True)
    args = parser.parse_args()

    raw: Any = json.loads(args.packet.read_text(encoding="utf-8"))
    packet = _object(raw, "packet")
    context, result, semantic_sha = run_packet(packet)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(
            result_dict(
                context,
                result,
                semantic_implementation_sha=semantic_sha,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    args.report_out.write_text(render_markdown(context, result), encoding="utf-8")


if __name__ == "__main__":
    main()
