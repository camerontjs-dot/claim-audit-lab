from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from .cli import context_from_packet
from .engine import AuditResult, audit
from .models import AuditContext
from .report import render_markdown

PROTOTYPE_PROFILE = "cal-v1-frozen-prototype-rc0"
SEMANTIC_IMPLEMENTATION_SHA = "a902621e8baea3063dddd7f92ba975aade305464"
OUTPUT_SCHEMA = "cal-v1-frozen-prototype-result-v1"


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return cast(Mapping[str, Any], value)


def _trace_dict(result: AuditResult) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for trace in result.traces:
        relation = None
        if trace.relation is not None:
            relation = {
                "relation_id": trace.relation.relation_id,
                "categorical_relation": trace.relation.categorical_relation.value,
                "authority_id": trace.relation.authority_id,
            }
        rows.append(
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
                "authority_id": (
                    None if trace.authority is None else trace.authority.authority_id
                ),
                "relation": relation,
                "failure_code": None if trace.failure_code is None else trace.failure_code.value,
                "detail": trace.detail,
            }
        )
    return rows


def result_record(
    context: AuditContext,
    result: AuditResult,
    *,
    packet_sha256: str,
) -> dict[str, Any]:
    return {
        "schema": OUTPUT_SCHEMA,
        "prototype_profile": PROTOTYPE_PROFILE,
        "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
        "input_packet_sha256": packet_sha256,
        "original_claim": context.original_claim,
        "proposition": {
            "proposition_id": context.proposition.proposition_id,
            "text_sha256": context.proposition.text_sha256,
            "semantic_family": result.semantic_family.value,
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
        },
        "result": {
            "conclusion": result.conclusion.value,
            "failure_code": None if result.failure_code is None else result.failure_code.value,
            "non_deciding_passage_ids": list(result.non_deciding_passage_ids),
            "traces": _trace_dict(result),
        },
        "contract_c_handoff": {
            "state": "not_emitted",
            "reason": "canonical_contract_c_2_authority_not_frozen_in_this_prototype",
        },
        "authorization": {
            "state": "not_evaluated",
            "automatic_action_allowed": False,
        },
    }


def run_packet(
    packet: Mapping[str, Any], *, packet_sha256: str
) -> tuple[AuditContext, AuditResult, dict[str, Any]]:
    context = context_from_packet(packet)
    result = audit(context)
    return context, result, result_record(context, result, packet_sha256=packet_sha256)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the frozen CAL V1 research prototype on one typed claim packet."
    )
    parser.add_argument("packet", type=Path)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--report-out", type=Path, required=True)
    args = parser.parse_args()

    raw_bytes = args.packet.read_bytes()
    raw: Any = json.loads(raw_bytes.decode("utf-8"))
    packet = _object(raw, "packet")
    packet_sha256 = "sha256:" + hashlib.sha256(raw_bytes).hexdigest()
    context, result, record = run_packet(packet, packet_sha256=packet_sha256)

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.report_out.write_text(render_markdown(context, result), encoding="utf-8")


if __name__ == "__main__":
    main()
