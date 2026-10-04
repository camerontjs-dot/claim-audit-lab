"""Run arms K, R, B, and C on one envelope."""

from __future__ import annotations

import time
from typing import Any

from codec import canonical, parse_envelope
from dispatch import ROLES, not_run, run_process
from lossy import lossy_envelope
from router import route
from synthesize import synthesize

SUCCESSOR = ("quantity_relation", "event_order", "scope_guard", "attribution_guard")


def _map_kernel(conclusion: str) -> str:
    return {
        "supports": "supported",
        "refutes": "contradicted",
        "unresolved": "not_checkable",
        "not_applicable": "not_checkable",
    }.get(conclusion, "not_checkable")


def _selected(raw: bytes, lanes: list[tuple[str, str]], policy: dict[str, Any]) -> dict[str, Any]:
    traced = [run_process(raw, lane=lane, process_id=process_id) for process_id, lane in lanes]
    if any(item["state"] != "completed" for item in traced):
        return {
            "conclusion": "not_checkable",
            "dispatch_failure": next(item["process_id"] for item in traced if item["state"] != "completed"),
            "traces": traced,
            "synthesis": None,
        }
    started = time.perf_counter()
    synthesis = synthesize(raw, [item["receipt"] for item in traced], policy)
    elapsed = time.perf_counter() - started
    return {
        "conclusion": synthesis["conclusion"],
        "traces": traced,
        "synthesis": synthesis,
        "synthesis_seconds": elapsed,
    }


def evaluate_envelope(raw: bytes, policy: dict[str, Any]) -> dict[str, Any]:
    envelope = parse_envelope(raw)
    lossy_raw, loss_record = lossy_envelope(envelope)
    started = time.perf_counter()
    kernel = run_process(raw, lane="kernel_legacy")
    kernel_seconds = time.perf_counter() - started
    kernel_receipt = kernel["receipt"]
    arm_k = {
        "conclusion": _map_kernel(str(kernel_receipt.get("conclusion", "unresolved"))),
        "authoring_status": kernel_receipt.get("authoring_status"),
        "abstention_cause": kernel_receipt.get("abstention_cause"),
        "traces": [kernel],
        "synthesis": None,
        "seconds": kernel_seconds,
        "role": "historical_reference_not_topology",
    }
    routed = route(envelope["claim"])
    selected = [str(item) for item in routed["processes"]]
    ran = [run_process(raw, lane=process_id) for process_id in selected]
    idle = [not_run(process_id, ROLES[process_id], raw) for process_id in SUCCESSOR if process_id not in selected]
    arm_r_traces = ran + idle
    if any(item["state"] == "failed" or item["state"] == "timeout" for item in ran):
        arm_r = {"conclusion": "not_checkable", "traces": arm_r_traces, "synthesis": None}
    else:
        arm_r_synthesis = synthesize(raw, [item["receipt"] for item in arm_r_traces], policy)
        arm_r = {
            "conclusion": arm_r_synthesis["conclusion"],
            "traces": arm_r_traces,
            "synthesis": arm_r_synthesis,
            "router": routed,
        }
    arm_b = _selected(lossy_raw, [(process_id, process_id) for process_id in SUCCESSOR], policy)
    arm_b["loss"] = loss_record
    arm_c = _selected(raw, [(process_id, process_id) for process_id in SUCCESSOR], policy)
    return {"K": arm_k, "R": arm_r, "B": arm_b, "C": arm_c}


def envelope_bytes(claim: str, evidence: list[dict[str, str]]) -> bytes:
    return canonical({"claim": claim, "evidence": evidence})
