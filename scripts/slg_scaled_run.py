"""Execute exactly one hash-bound Lane A scaled-corpus atom measurement.

All deterministic checks and offline model-cache loads complete before the
output directory is created. Creating ``attempt-start.json`` consumes the cell;
success, failure, or interruption never authorizes a rerun. The command is a
DEV-only measurement harness, not validation, release, or GxP evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.impl.entailer import _load_model as load_entailer_model
from claim_audit_lab.v1.impl.retriever import _load_model as load_retriever_model
from claim_audit_lab.v1.models import AuditConfig, AuditRequest
from claim_audit_lab.v1.runner import run_default_audit

try:
    from scripts.pilot001_premise_granularity_run04 import build_request_index
    from scripts.simple_logic_gold_direct_lane import _map_cal_verdict
    from scripts.slg_scaled_first_cell_prepare import (
        _run,
        sha256_file,
        sha256_text,
        verify_sha256_manifest,
        write_recursive_manifest,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from pilot001_premise_granularity_run04 import build_request_index  # type: ignore
    from simple_logic_gold_direct_lane import _map_cal_verdict  # type: ignore
    from slg_scaled_first_cell_prepare import (  # type: ignore
        _run,
        sha256_file,
        sha256_text,
        verify_sha256_manifest,
        write_recursive_manifest,
    )

AUDIT_CONFIG_HASH = "sha256:739fc95bb6920b47a3a8d4c8242751ebc83322ae3fdc2aa5fcb18e855e0e12c7"


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def require_offline_environment(environment: Mapping[str, str]) -> dict[str, str]:
    """Fail before loading models unless both offline flags are exact."""
    required = {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    missing = [key for key, value in required.items() if environment.get(key) != value]
    if missing:
        raise ValueError(f"offline contract requires {', '.join(missing)}=1")
    return required


def preload_default_models(
    config: AuditConfig,
    *,
    retriever_loader: Callable[[str, str], Any] = load_retriever_model,
    entailer_loader: Callable[[str, str], Any] = load_entailer_model,
) -> dict[str, Any]:
    """Load pinned local revisions without constructing or auditing a request."""
    retriever_loader(config.retriever.model_id, config.retriever.hf_revision_sha)
    entailer_loader(config.entailer.model_id, config.entailer.hf_revision_sha)
    return {
        "status": "loaded_from_local_cache_before_attempt_start",
        "retriever": {
            "model_id": config.retriever.model_id,
            "revision": config.retriever.hf_revision_sha,
        },
        "entailer": {
            "model_id": config.entailer.model_id,
            "revision": config.entailer.hf_revision_sha,
        },
        "cal_inference_performed": False,
    }


def load_baseline_atom(path: Path, atom_id: str, expected_sha256: str) -> dict[str, Any]:
    """Load one atom from the preserved T1 result; never rerun the baseline."""
    if sha256_file(path) != expected_sha256:
        raise ValueError("preserved T1 run hash mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    matches = [atom for atom in payload["atoms"] if atom["atom_id"] == atom_id]
    if len(matches) != 1:
        raise ValueError(f"preserved T1 must contain exactly one {atom_id} record")
    atom = matches[0]
    if atom["trace"].get("audit_config_hash") != AUDIT_CONFIG_HASH:
        raise ValueError("preserved T1 audit-config hash drifted")
    return atom


def verify_workbench(workbench: Path, expected_head: str) -> dict[str, str]:
    """Bind the exact committed harness and require package/config cleanliness."""
    head = _run(["git", "rev-parse", "HEAD"], cwd=workbench)
    branch = _run(["git", "branch", "--show-current"], cwd=workbench)
    if head != expected_head or branch != "cal-v1-skeleton":
        raise ValueError(f"CAL workbench drifted: branch={branch} head={head}")
    package_status = _run(
        ["git", "status", "--porcelain", "--", "src/claim_audit_lab", "pyproject.toml"],
        cwd=workbench,
    )
    if package_status:
        raise ValueError(f"CAL package/config is dirty:\n{package_status}")
    return {"branch": branch, "head": head, "package_status": "clean"}


def _raw_passage_id(passage_id: str) -> str:
    return passage_id.rsplit("/", 1)[-1]


def build_measurement_summary(
    trace: dict[str, Any],
    baseline: dict[str, Any],
    fact_ids: list[str],
    *,
    retrieval_floor: float,
) -> dict[str, Any]:
    """Report retrieval, contribution, verdict, and stability without suppression."""
    retrieval = trace["retrieval"]
    retrieved = {
        _raw_passage_id(row["passage_id"]): {"rank": rank, "score": row["score"]}
        for rank, row in enumerate(retrieval, 1)
        if _raw_passage_id(row["passage_id"]) in fact_ids
    }
    missing = [fact_id for fact_id in fact_ids if fact_id not in retrieved]
    below_floor = [fact_id for fact_id, row in retrieved.items() if row["score"] < retrieval_floor]
    contributing_id = trace["support_signal"].get("contributing_passage_id")
    contributing_fact = (
        _raw_passage_id(contributing_id) if isinstance(contributing_id, str) else None
    )
    contributing = contributing_fact in fact_ids
    observed_relation = _map_cal_verdict(trace["verdict"]["support_verdict"])
    verdict_stable = observed_relation == baseline["cal_observed_relation"]
    fresh_reason = trace["verdict"].get("support_verdict_reason")
    baseline_reason = baseline.get("trace", {}).get("verdict", {}).get("support_verdict_reason")
    reason_stable = fresh_reason == baseline_reason
    flags = list(trace["verdict"]["audit_flags"])
    failures: list[str] = []
    if missing:
        failures.append("fact_outside_top_k")
    if below_floor:
        failures.append("fact_below_floor")
    if not contributing:
        failures.append("fact_not_contributing")
    if not reason_stable:
        failures.append(
            "no_entail_signal"
            if fresh_reason == "no_entail_signal"
            else "support_verdict_reason_flip"
        )
    if not verdict_stable:
        failures.append("verdict_flip")
    if flags:
        failures.append("unexpected_audit_flag")
    stable = not failures
    return {
        "primary": {
            "verdict_stable_vs_preserved_t1": verdict_stable,
            "all_facts_retrieved": not missing,
            "all_retrieved_facts_at_or_above_floor": not below_floor,
            "contributing_passage_is_frozen_fact": contributing,
            "classification": "stable" if stable else "cell_failure",
            "failure_classes": failures,
        },
        "secondary": {
            "fact_retrieval": retrieved,
            "missing_fact_ids": missing,
            "below_floor_fact_ids": below_floor,
            "contributing_passage_id": contributing_id,
            "ordered_retrieval": retrieval,
            "entailment_call_count": len(trace["entailment"]),
            "entailment": trace["entailment"],
            "max_entailment_score": trace["support_signal"]["max_entailment_score"],
            "support_verdict_reason": fresh_reason,
            "rules_fired": trace["rules_fired"],
            "audit_flags": flags,
        },
        "comparison": {
            "t1_source": "preserved; not rerun",
            "t1_support_verdict": baseline["cal_support_verdict"],
            "t1_observed_relation": baseline["cal_observed_relation"],
            "t1_support_verdict_reason": baseline_reason,
            "fresh_support_verdict": trace["verdict"]["support_verdict"],
            "fresh_observed_relation": observed_relation,
            "fresh_support_verdict_reason": fresh_reason,
            "support_verdict_reason_stable": reason_stable,
        },
    }


def preflight(
    prepared_root: Path,
    expected_preparation_receipt_sha256: str,
    expected_preparation_manifest_sha256: str,
    preregistration: Path,
    expected_preregistration_sha256: str,
    expected_runner_sha256: str,
    expected_workbench_head: str,
    baseline_run: Path,
    expected_baseline_sha256: str,
    atom_id: str,
    out: Path,
) -> tuple[AuditRequest, dict[str, Any], dict[str, Any], AuditConfig, dict[str, Any]]:
    """Complete every safe check and model load before the sealed boundary."""
    if out.exists():
        raise FileExistsError(f"measured-run directory already exists; rerun forbidden: {out}")
    if sha256_file(Path(__file__)) != expected_runner_sha256:
        raise ValueError("runner hash does not match the approved command")
    if sha256_file(preregistration) != expected_preregistration_sha256:
        raise ValueError("preregistration hash does not match the approved command")

    receipt_path = prepared_root / "preparation-receipt.json"
    manifest_path = prepared_root / "SHA256SUMS"
    if sha256_file(receipt_path) != expected_preparation_receipt_sha256:
        raise ValueError("preparation receipt hash mismatch")
    if sha256_file(manifest_path) != expected_preparation_manifest_sha256:
        raise ValueError("preparation manifest hash mismatch")
    verify_sha256_manifest(prepared_root, manifest_path)
    preparation = json.loads(receipt_path.read_text(encoding="utf-8"))
    if preparation.get("measured_inference_run") is not False:
        raise ValueError("preparation receipt does not declare zero measured inference")
    if preparation.get("next_gate") != "Cameron approval of the exact measured-run command":
        raise ValueError("preparation receipt approval boundary drifted")
    if atom_id not in preparation["atom_ids"]:
        raise ValueError(f"atom {atom_id} is not in the prepared cell")

    workbench = Path(__file__).resolve().parents[1]
    boundary = verify_workbench(workbench, expected_workbench_head)
    offline = require_offline_environment(os.environ)
    config = load_default_audit_config()
    if hash_audit_config(config) != AUDIT_CONFIG_HASH:
        raise ValueError("CAL default audit-config hash drifted")
    packet = prepared_root / "packet"
    requests = build_request_index(packet, config)
    if atom_id not in requests:
        raise ValueError(f"prepared packet does not contain {atom_id}")
    request = requests[atom_id]
    baseline = load_baseline_atom(baseline_run, atom_id, expected_baseline_sha256)
    if request.claim_text != baseline["trace"]["claim_text"]:
        raise ValueError("prepared claim text differs from preserved T1")
    fact_ids = preparation["construction"]["fact_ids"]
    expected_text_hashes = preparation["construction"]["passage_text_sha256"]
    for passage in request.passages:
        raw_id = _raw_passage_id(passage.passage_id)
        if expected_text_hashes.get(raw_id) != sha256_text(passage.text):
            raise ValueError(f"prepared passage text drifted: {passage.passage_id}")
    model_preflight = preload_default_models(config)
    readiness = {
        "schema_version": "cal-lane-a-scaled-cell-preflight-v1",
        "status": "ready_awaiting_exact_command_approval",
        "cal_inference_performed": False,
        "output_directory_created": False,
        "world_id": preparation["world_id"],
        "atom_id": atom_id,
        "tier": preparation["tier"],
        "fact_ids": fact_ids,
        "preparation_receipt_sha256": "sha256:" + expected_preparation_receipt_sha256,
        "preparation_manifest_sha256": "sha256:" + expected_preparation_manifest_sha256,
        "preregistration_sha256": "sha256:" + expected_preregistration_sha256,
        "runner_sha256": "sha256:" + expected_runner_sha256,
        "baseline_run_sha256": "sha256:" + expected_baseline_sha256,
        "audit_config_hash": AUDIT_CONFIG_HASH,
        "cal_boundary": boundary,
        "offline_environment": offline,
        "model_preflight": model_preflight,
    }
    return request, baseline, preparation, config, readiness


def run_once(*args: Any) -> dict[str, Any]:
    """Preflight, consume one attempt, and preserve success or failure."""
    out = args[-1]
    request, baseline, preparation, config, readiness = preflight(*args)
    out.mkdir(parents=True, exist_ok=False)
    started_at = utc_now()
    attempt = {
        **readiness,
        "schema_version": "cal-lane-a-scaled-cell-attempt-v1",
        "status": "inference_starting",
        "started_at_utc": started_at,
        "command": sys.argv,
        "output_directory_created": True,
    }
    (out / "attempt-start.json").write_text(
        json.dumps(attempt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    start = time.perf_counter()
    try:
        trace = run_default_audit(request).model_dump(mode="json")
    except BaseException as exc:
        error = {
            "schema_version": "cal-lane-a-scaled-cell-error-v1",
            "status": "inference_error_run_consumed",
            "finished_at_utc": utc_now(),
            "wall_time_seconds": time.perf_counter() - start,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "rerun_allowed": False,
        }
        (out / "attempt-error.json").write_text(
            json.dumps(error, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        write_recursive_manifest(out)
        raise

    summary = build_measurement_summary(
        trace,
        baseline,
        preparation["construction"]["fact_ids"],
        retrieval_floor=config.retrieval_floor,
    )
    result = {
        "schema_version": "cal-lane-a-scaled-cell-result-v1",
        "label": "DEV-only measured cell; not validation or gate evidence",
        "status": "completed_run_consumed",
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "wall_time_seconds": time.perf_counter() - start,
        "world_id": preparation["world_id"],
        "atom_id": request.claim_id,
        "tier": preparation["tier"],
        "parameters": {
            "top_k": config.top_k,
            "retrieval_floor": config.retrieval_floor,
            "audit_config_hash": hash_audit_config(config),
        },
        **summary,
        "trace": trace,
        "report_boundary": {
            "can_establish": "one DEV scaled-corpus atom comparison only",
            "cannot_establish": [
                "dilution curve",
                "optimal bundle operating point",
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
    parser.add_argument("--prepared-root", type=Path, required=True)
    parser.add_argument("--expected-preparation-receipt-sha256", required=True)
    parser.add_argument("--expected-preparation-manifest-sha256", required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--expected-preregistration-sha256", required=True)
    parser.add_argument("--expected-runner-sha256", required=True)
    parser.add_argument("--expected-workbench-head", required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--expected-baseline-sha256", required=True)
    parser.add_argument("--atom-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preflight-only", action="store_true")
    parsed = parser.parse_args()
    args = (
        parsed.prepared_root.resolve(),
        parsed.expected_preparation_receipt_sha256,
        parsed.expected_preparation_manifest_sha256,
        parsed.preregistration.resolve(),
        parsed.expected_preregistration_sha256,
        parsed.expected_runner_sha256,
        parsed.expected_workbench_head,
        parsed.baseline_run.resolve(),
        parsed.expected_baseline_sha256,
        parsed.atom_id,
        parsed.out.resolve(),
    )
    if parsed.preflight_only:
        *_, readiness = preflight(*args)
        print(json.dumps(readiness, ensure_ascii=False, sort_keys=True))
        return
    result = run_once(*args)
    print(json.dumps(result["primary"], sort_keys=True))


if __name__ == "__main__":
    main()
