"""Run the offline-preflighted rejected-generation-04 CAL reporting control.

Generation 04 is terminally rejected. This script cannot admit or rehabilitate
it: every post-start record is labeled invalid-input diagnostic only and is
excluded from Lane A. Model cache loading occurs before the single-shot boundary.

Do not invoke without Cameron's approval of the exact hash-bound command.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.impl.entailer import _load_model as load_entailer_model
from claim_audit_lab.v1.impl.retriever import _load_model as load_retriever_model
from claim_audit_lab.v1.models import AuditConfig, AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit

try:
    from scripts.slg_scaled_first_cell_prepare import (
        ATOM_ID,
        FACT_ID,
        PASSAGE_IDS,
        TITLE,
        build_content_and_passages,
        sha256_file,
        sha256_text,
        verify_workbench_boundary,
        write_recursive_manifest,
    )
    from scripts.slg_scaled_first_cell_run import (
        AUDIT_CONFIG_HASH,
        build_measurement_summary,
        load_baseline_atom,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from slg_scaled_first_cell_prepare import (  # type: ignore[no-redef]
        ATOM_ID,
        FACT_ID,
        PASSAGE_IDS,
        TITLE,
        build_content_and_passages,
        sha256_file,
        sha256_text,
        verify_workbench_boundary,
        write_recursive_manifest,
    )
    from slg_scaled_first_cell_run import (  # type: ignore[no-redef]
        AUDIT_CONFIG_HASH,
        build_measurement_summary,
        load_baseline_atom,
    )

CANDIDATE_RAW_SHA256 = "8722454fc310ed7e972d2b3794fb414470b992b1a91c40b67672ac8304fbfdda"
CANDIDATE_CASE_SHA256 = "89711b0e20ad2dc59663bb2adc537b937e1ce60f79361b06f945f1548f413666"
REJECTION_RECEIPT_SHA256 = "3776969bec39c35fe4cecfb76a7b9cabbc1e120198eb875d08d80b1e0c18d6a8"


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def require_offline_environment(environment: Mapping[str, str]) -> dict[str, str]:
    """Fail before model loading unless both Hugging Face offline flags are frozen."""
    required = {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    missing = [name for name, expected in required.items() if environment.get(name) != expected]
    if missing:
        raise ValueError(f"offline contract requires {', '.join(missing)}=1")
    return required


def preload_default_models(
    config: AuditConfig,
    *,
    retriever_loader: Callable[[str, str], Any] = load_retriever_model,
    entailer_loader: Callable[[str, str], Any] = load_entailer_model,
) -> dict[str, Any]:
    """Load exact pinned models into process caches without running CAL inference."""
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


def load_rejected_candidate(candidate_dir: Path) -> tuple[list[str], dict[str, Any]]:
    """Bind generation 04 and require its exact terminal rejection receipt."""
    raw_path = candidate_dir / "raw_response.txt"
    case_path = candidate_dir / "case.json"
    screen_path = candidate_dir / "deterministic-screen.json"
    expected_hashes = {
        raw_path: CANDIDATE_RAW_SHA256,
        case_path: CANDIDATE_CASE_SHA256,
        screen_path: REJECTION_RECEIPT_SHA256,
    }
    for path, expected in expected_hashes.items():
        if sha256_file(path) != expected:
            raise ValueError(f"rejected-control input hash mismatch: {path.name}")

    case = json.loads(case_path.read_text(encoding="utf-8"))
    screen = json.loads(screen_path.read_text(encoding="utf-8"))
    if case.get("candidate_id") != "slg01d-t2-easy-paperwork-generation-04":
        raise ValueError("rejected-control candidate ID drifted")
    if case.get("status") != "rejected_deterministic_screen":
        raise ValueError("candidate is not preserved as rejected")
    if screen.get("decision") != "reject" or screen.get("admissible") is not False:
        raise ValueError("candidate rejection receipt drifted")
    expected_screen = {
        "body_word_count": 197,
        "body_word_count_ok": False,
        "forbidden_subject_hits": [],
        "banned_outcome_or_derivation_hits": ["storage"],
        "exact_or_normalized_proposition_hits": [],
        "reasons": [
            "body word count outside contract",
            "banned outcome verb derivation hit",
        ],
    }
    for field, expected in expected_screen.items():
        if screen.get(field) != expected:
            raise ValueError(f"candidate rejection field drifted: {field}")

    blocks = [
        block.strip()
        for block in re.split(r"\n\s*\n", raw_path.read_text(encoding="utf-8").strip())
    ]
    if len(blocks) != 7 or blocks[0] != TITLE:
        raise ValueError("rejected candidate title/paragraph shape drifted")
    return blocks[1:], screen


def build_quarantine_fields(screen: dict[str, Any]) -> dict[str, Any]:
    """Return the immutable invalid-input authority and rejection evidence."""
    return {
        "input_admissibility": "rejected",
        "authority": "invalid-input diagnostic only",
        "included_in_lane_a_results": False,
        "candidate_raw_sha256": "sha256:" + CANDIDATE_RAW_SHA256,
        "rejection_receipt_sha256": "sha256:" + REJECTION_RECEIPT_SHA256,
        "rejection_evidence": {
            "body_word_count": screen["body_word_count"],
            "body_word_count_ok": screen["body_word_count_ok"],
            "forbidden_subject_hits": screen["forbidden_subject_hits"],
            "banned_outcome_or_derivation_hits": screen["banned_outcome_or_derivation_hits"],
            "exact_or_normalized_proposition_hits": screen["exact_or_normalized_proposition_hits"],
            "reasons": screen["reasons"],
        },
        "interpretation_rule": (
            "CAL behavior on this rejected input is not a dilution result and cannot "
            "rehabilitate the artifact."
        ),
    }


def build_request(
    candidate_dir: Path,
) -> tuple[AuditRequest, dict[str, Any], dict[str, Any], AuditConfig]:
    """Construct the seven-passage invalid-input request without a bundle adapter."""
    paragraphs, screen = load_rejected_candidate(candidate_dir)
    content, passage_records = build_content_and_passages(TITLE, paragraphs)
    config = load_default_audit_config()
    if hash_audit_config(config) != AUDIT_CONFIG_HASH:
        raise ValueError("CAL config hash drifted")
    if config.top_k != 5 or config.retrieval_floor != 0.40:
        raise ValueError("CAL retrieval parameters drifted")
    passages = [
        Passage(
            passage_id=record["passage_id"],
            text=record["text"],
            source_meta={
                "trust_level": "primary",
                "input_admissibility": "rejected",
                "source": "generation-04-negative-control",
            },
        )
        for record in passage_records
    ]
    request = AuditRequest(
        claim_id=ATOM_ID,
        claim_text="The retained sample is in cabinet A.",
        passages=passages,
        audit_config=config,
    )
    construction = {
        "content_sha256": sha256_text(content),
        "passage_order": list(PASSAGE_IDS),
        "passage_text_sha256": {
            passage.passage_id: sha256_text(passage.text) for passage in passages
        },
        "offsets": [
            {
                "passage_id": record["passage_id"],
                "char_start": record["char_start"],
                "char_end": record["char_end"],
            }
            for record in passage_records
        ],
        "fact_passage_id": FACT_ID,
        "fact_insert_after_filler_paragraph": 3,
    }
    return request, screen, construction, config


def run_once(
    candidate_dir: Path,
    baseline_run: Path,
    preregistration: Path,
    expected_preregistration_sha256: str,
    expected_runner_sha256: str,
    out: Path,
) -> dict[str, Any]:
    """Preflight offline, then consume one diagnostic audit and preserve quarantine."""
    request, baseline, screen, construction, config, readiness = preflight(
        candidate_dir,
        baseline_run,
        preregistration,
        expected_preregistration_sha256,
        expected_runner_sha256,
        out,
    )

    out.mkdir(parents=True, exist_ok=False)
    started_at = utc_now()
    attempt = {
        "schema_version": "cal-rejected-input-control-attempt-v2",
        "status": "inference_starting",
        "started_at_utc": started_at,
        "command": sys.argv,
        **build_quarantine_fields(screen),
        "preregistration_sha256": "sha256:" + expected_preregistration_sha256,
        "runner_sha256": "sha256:" + expected_runner_sha256,
        "cal_boundary": readiness["cal_boundary"],
        "offline_environment": readiness["offline_environment"],
        "model_preflight": readiness["model_preflight"],
        "construction": construction,
    }
    (out / "attempt-start.json").write_text(
        json.dumps(attempt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    start = time.perf_counter()
    try:
        trace = run_default_audit(request)
    except BaseException as exc:
        error = {
            "schema_version": "cal-rejected-input-control-error-v2",
            "status": "inference_error_run_consumed",
            "finished_at_utc": utc_now(),
            "wall_time_seconds": time.perf_counter() - start,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "rerun_allowed": False,
            **build_quarantine_fields(screen),
        }
        (out / "attempt-error.json").write_text(
            json.dumps(error, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        write_recursive_manifest(out)
        raise

    trace_payload = trace.model_dump(mode="json")
    result = {
        "schema_version": "cal-rejected-input-control-result-v2",
        "status": "completed_run_consumed",
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "wall_time_seconds": time.perf_counter() - start,
        **build_quarantine_fields(screen),
        "parameters": {
            "top_k": request.audit_config.top_k,
            "retrieval_floor": request.audit_config.retrieval_floor,
            "audit_config_hash": hash_audit_config(request.audit_config),
        },
        "offline_environment": readiness["offline_environment"],
        "model_preflight": readiness["model_preflight"],
        "construction": construction,
        "diagnostic_comparison": build_measurement_summary(
            trace_payload,
            baseline,
            retrieval_floor=config.retrieval_floor,
        ),
        "trace": trace_payload,
        "rerun_allowed": False,
    }
    (out / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_recursive_manifest(out)
    return result


def preflight(
    candidate_dir: Path,
    baseline_run: Path,
    preregistration: Path,
    expected_preregistration_sha256: str,
    expected_runner_sha256: str,
    out: Path,
) -> tuple[
    AuditRequest,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    AuditConfig,
    dict[str, Any],
]:
    """Complete all checks and model cache loads without starting a CAL audit."""
    if out.exists():
        raise FileExistsError(f"rejected-control output already exists; rerun forbidden: {out}")
    if sha256_file(Path(__file__)) != expected_runner_sha256:
        raise ValueError("rejected-control runner hash mismatch")
    if sha256_file(preregistration) != expected_preregistration_sha256:
        raise ValueError("rejected-control preregistration hash mismatch")

    offline = require_offline_environment(os.environ)
    cal_boundary = verify_workbench_boundary(Path(__file__).resolve().parents[1])
    baseline = load_baseline_atom(baseline_run)
    request, screen, construction, config = build_request(candidate_dir)
    model_preflight = preload_default_models(config)
    readiness = {
        "schema_version": "cal-rejected-input-control-preflight-v2",
        "status": "ready_awaiting_exact_command_approval",
        "cal_inference_performed": False,
        "output_directory_created": False,
        "cal_boundary": cal_boundary,
        "offline_environment": offline,
        "model_preflight": model_preflight,
        **build_quarantine_fields(screen),
    }
    return request, baseline, screen, construction, config, readiness


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--expected-preregistration-sha256", required=True)
    parser.add_argument("--expected-runner-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    if args.preflight_only:
        *_, readiness = preflight(
            args.candidate_dir.resolve(),
            args.baseline_run.resolve(),
            args.preregistration.resolve(),
            args.expected_preregistration_sha256,
            args.expected_runner_sha256,
            args.out.resolve(),
        )
        print(json.dumps(readiness, ensure_ascii=False, sort_keys=True))
        return
    result = run_once(
        args.candidate_dir.resolve(),
        args.baseline_run.resolve(),
        args.preregistration.resolve(),
        args.expected_preregistration_sha256,
        args.expected_runner_sha256,
        args.out.resolve(),
    )
    print(
        json.dumps(
            {
                "input_admissibility": result["input_admissibility"],
                "included_in_lane_a_results": result["included_in_lane_a_results"],
                "diagnostic_primary": result["diagnostic_comparison"]["primary"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
