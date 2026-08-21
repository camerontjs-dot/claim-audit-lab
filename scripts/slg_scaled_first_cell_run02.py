"""Execute the offline-preflighted Lane A generation-05 first cell once.

This v2 wrapper preserves the frozen v1 experiment and adds only proven offline
model loading plus dual-generation hash binding. Do not invoke without Cameron's
approval of the exact command. DEV-only; never validation or gate evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config

try:
    from scripts import slg_scaled_first_cell_run as base
    from scripts.slg_scaled_first_cell_prepare import sha256_file, write_recursive_manifest
    from scripts.slg_scaled_rejected_control_run02 import (
        preload_default_models,
        require_offline_environment,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    import slg_scaled_first_cell_run as base  # type: ignore[no-redef]
    from slg_scaled_first_cell_prepare import (  # type: ignore[no-redef]
        sha256_file,
        write_recursive_manifest,
    )
    from slg_scaled_rejected_control_run02 import (  # type: ignore[no-redef]
        preload_default_models,
        require_offline_environment,
    )

BASE_RUNNER_SHA256 = "54fcffcdc814fd7a7e236e1d777f3a704836bfeb3a9d3e2e75f62051791d5d34"
BASE_PREREGISTRATION_SHA256 = "b6f9c59ea71a7dd39f58f4a6cd209c1db80e81b18f3e00841f388fc0d67f1a1f"


def preflight(
    packet: Path,
    preparation_receipt: Path,
    expected_preparation_sha256: str,
    expected_manifest_sha256: str,
    frozen_preregistration: Path,
    superseding_preregistration: Path,
    expected_superseding_preregistration_sha256: str,
    expected_runner_sha256: str,
    baseline_run: Path,
    out: Path,
) -> tuple[Any, dict[str, Any], dict[str, Any], dict[str, str], dict[str, Any]]:
    """Run every deterministic and model-cache check without CAL inference."""
    if out.exists():
        raise FileExistsError(f"measured-run directory already exists; rerun forbidden: {out}")
    if sha256_file(Path(__file__)) != expected_runner_sha256:
        raise ValueError("offline measured runner hash does not match the approved command")
    if sha256_file(superseding_preregistration) != expected_superseding_preregistration_sha256:
        raise ValueError("offline superseding preregistration hash mismatch")
    if sha256_file(Path(base.__file__)) != BASE_RUNNER_SHA256:
        raise ValueError("frozen base measured runner hash drifted")
    if sha256_file(frozen_preregistration) != BASE_PREREGISTRATION_SHA256:
        raise ValueError("frozen first-cell preregistration hash drifted")

    offline = require_offline_environment(os.environ)
    request, baseline, preparation, cal_boundary = base.preflight(
        packet,
        preparation_receipt,
        expected_preparation_sha256,
        expected_manifest_sha256,
        frozen_preregistration,
        BASE_PREREGISTRATION_SHA256,
        BASE_RUNNER_SHA256,
        baseline_run,
    )
    config = load_default_audit_config()
    model_preflight = preload_default_models(config)
    readiness = {
        "schema_version": "cal-lane-a-first-cell-preflight-v2",
        "status": "ready_awaiting_exact_command_approval",
        "cal_inference_performed": False,
        "output_directory_created": False,
        "lane": "A",
        "world_id": base.WORLD_ID,
        "atom_id": base.ATOM_ID,
        "candidate_raw_sha256": preparation["inputs"]["candidate_raw_sha256"],
        "frozen_preregistration_sha256": "sha256:" + BASE_PREREGISTRATION_SHA256,
        "base_runner_sha256": "sha256:" + BASE_RUNNER_SHA256,
        "superseding_preregistration_sha256": (
            "sha256:" + expected_superseding_preregistration_sha256
        ),
        "runner_sha256": "sha256:" + expected_runner_sha256,
        "cal_boundary": cal_boundary,
        "offline_environment": offline,
        "model_preflight": model_preflight,
    }
    return request, baseline, preparation, cal_boundary, readiness


def run_once(
    packet: Path,
    preparation_receipt: Path,
    expected_preparation_sha256: str,
    expected_manifest_sha256: str,
    frozen_preregistration: Path,
    superseding_preregistration: Path,
    expected_superseding_preregistration_sha256: str,
    expected_runner_sha256: str,
    baseline_run: Path,
    out: Path,
) -> dict[str, Any]:
    """Preflight offline, then consume the one authorized Lane A first cell."""
    request, baseline, preparation, cal_boundary, readiness = preflight(
        packet,
        preparation_receipt,
        expected_preparation_sha256,
        expected_manifest_sha256,
        frozen_preregistration,
        superseding_preregistration,
        expected_superseding_preregistration_sha256,
        expected_runner_sha256,
        baseline_run,
        out,
    )
    config = load_default_audit_config()
    out.mkdir(parents=True, exist_ok=False)
    started_at = base.utc_now()
    attempt = {
        "schema_version": "cal-lane-a-first-cell-attempt-v2",
        "label": "DEV-only measured attempt; not validation or gate evidence",
        "status": "inference_starting",
        "started_at_utc": started_at,
        "command": sys.argv,
        "world_id": base.WORLD_ID,
        "atom_id": base.ATOM_ID,
        "preparation_receipt_sha256": "sha256:" + expected_preparation_sha256,
        "preparation_manifest_sha256": "sha256:" + expected_manifest_sha256,
        "frozen_preregistration_sha256": "sha256:" + BASE_PREREGISTRATION_SHA256,
        "base_runner_sha256": "sha256:" + BASE_RUNNER_SHA256,
        "superseding_preregistration_sha256": (
            "sha256:" + expected_superseding_preregistration_sha256
        ),
        "runner_sha256": "sha256:" + expected_runner_sha256,
        "baseline_run_sha256": "sha256:" + base.BASELINE_RUN_SHA256,
        "audit_config_hash": base.AUDIT_CONFIG_HASH,
        "cal_boundary": cal_boundary,
        "offline_environment": readiness["offline_environment"],
        "model_preflight": readiness["model_preflight"],
    }
    (out / "attempt-start.json").write_text(
        json.dumps(attempt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    start = time.perf_counter()
    try:
        trace = base.run_default_audit(request)
    except BaseException as exc:
        error = {
            "schema_version": "cal-lane-a-first-cell-error-v2",
            "status": "inference_error_run_consumed",
            "finished_at_utc": base.utc_now(),
            "wall_time_seconds": time.perf_counter() - start,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "rerun_allowed": False,
            "runner_sha256": "sha256:" + expected_runner_sha256,
            "superseding_preregistration_sha256": (
                "sha256:" + expected_superseding_preregistration_sha256
            ),
        }
        (out / "attempt-error.json").write_text(
            json.dumps(error, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        write_recursive_manifest(out)
        raise

    trace_payload = trace.model_dump(mode="json")
    summary = base.build_measurement_summary(
        trace_payload, baseline, retrieval_floor=config.retrieval_floor
    )
    result: dict[str, Any] = {
        "schema_version": "cal-lane-a-first-cell-result-v2",
        "label": "DEV-only first-cell result; not validation or gate evidence",
        "status": "completed_run_consumed",
        "started_at_utc": started_at,
        "finished_at_utc": base.utc_now(),
        "wall_time_seconds": time.perf_counter() - start,
        "lane": "A",
        "world_id": base.WORLD_ID,
        "atom_id": base.ATOM_ID,
        "tier": "T2",
        "difficulty": "easy",
        "genre": "pharmaceutical-paperwork",
        "parameters": {
            "top_k": config.top_k,
            "retrieval_floor": config.retrieval_floor,
            "audit_config_hash": hash_audit_config(config),
        },
        "offline_environment": readiness["offline_environment"],
        "model_preflight": readiness["model_preflight"],
        "inputs": {
            "preparation_receipt_sha256": "sha256:" + expected_preparation_sha256,
            "preparation_manifest_sha256": "sha256:" + expected_manifest_sha256,
            "frozen_preregistration_sha256": "sha256:" + BASE_PREREGISTRATION_SHA256,
            "base_runner_sha256": "sha256:" + BASE_RUNNER_SHA256,
            "superseding_preregistration_sha256": (
                "sha256:" + expected_superseding_preregistration_sha256
            ),
            "runner_sha256": "sha256:" + expected_runner_sha256,
            "candidate_raw_sha256": preparation["inputs"]["candidate_raw_sha256"],
            "baseline_run_sha256": "sha256:" + base.BASELINE_RUN_SHA256,
        },
        **summary,
        "trace": trace_payload,
        "report_boundary": {
            "can_establish": "one DEV T2-vs-preserved-T1 harness cell only",
            "cannot_establish": [
                "dilution curve",
                "optimal bundle operating point",
                "safe intake limit",
                "Lane B quality",
                "validation or fresh-gate clearance",
                "release, production, or GxP qualification",
            ],
        },
        "rerun_allowed": False,
    }
    (out / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_recursive_manifest(out)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--preparation-receipt", type=Path, required=True)
    parser.add_argument("--expected-preparation-sha256", required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--frozen-preregistration", type=Path, required=True)
    parser.add_argument("--superseding-preregistration", type=Path, required=True)
    parser.add_argument("--expected-superseding-preregistration-sha256", required=True)
    parser.add_argument("--expected-runner-sha256", required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    positional = (
        args.packet.resolve(),
        args.preparation_receipt.resolve(),
        args.expected_preparation_sha256,
        args.expected_manifest_sha256,
        args.frozen_preregistration.resolve(),
        args.superseding_preregistration.resolve(),
        args.expected_superseding_preregistration_sha256,
        args.expected_runner_sha256,
        args.baseline_run.resolve(),
        args.out.resolve(),
    )
    if args.preflight_only:
        *_, readiness = preflight(*positional)
        print(json.dumps(readiness, ensure_ascii=False, sort_keys=True))
        return
    result = run_once(*positional)
    print(json.dumps(result["primary"], sort_keys=True))


if __name__ == "__main__":
    main()
