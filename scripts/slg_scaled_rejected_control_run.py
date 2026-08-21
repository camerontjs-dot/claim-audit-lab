"""Run one quarantined CAL diagnostic over preserved rejected generation 01.

The input failed generation admission because it contains ``returned``. This
script does not rehabilitate it: every result is labeled rejected, excluded
from Lane A, and stored under ``rejected-input-controls``. Its only purpose is
to verify that CAL's complete trace and the harness quarantine survive together.

One-shot DEV diagnostic only; never dilution, validation, or gate evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.models import AuditRequest, Passage
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

CANDIDATE_RAW_SHA256 = "3276a8ea3b48ce9ce0fc370a97c462bfdbfa16521152117fd0cf2919c6ec59fa"
CANDIDATE_CASE_SHA256 = "16b061efcaad48d35f8a5c3cbbe51599e5447ebd116d32dddf1c3105d57446b0"
REJECTION_RECEIPT_SHA256 = "e11fdb0f07ace2a3a7dc92e1af05a875c59f688d065ff97d225923aebf97fd47"


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def load_rejected_candidate(candidate_dir: Path) -> tuple[list[str], dict[str, Any]]:
    """Bind generation 01 and require its exact terminal rejection."""
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
    if case.get("candidate_id") != "slg01d-t2-easy-paperwork-generation-01":
        raise ValueError("rejected-control candidate ID drifted")
    if case.get("status") != "rejected_deterministic_screen":
        raise ValueError("candidate is not preserved as rejected")
    if screen.get("decision") != "reject" or screen.get("admissible") is not False:
        raise ValueError("candidate rejection receipt drifted")
    hits = screen.get("banned_outcome_verb_hits", {})
    if hits != {"return": ["returned"]}:
        raise ValueError(f"candidate rejection reason drifted: {hits}")

    blocks = [
        block.strip()
        for block in re.split(r"\n\s*\n", raw_path.read_text(encoding="utf-8").strip())
    ]
    if len(blocks) != 7 or blocks[0] != TITLE:
        raise ValueError("rejected candidate title/paragraph shape drifted")
    paragraphs = blocks[1:]
    word_count = len(re.findall(r"\b[\w’–-]+\b", "\n\n".join(paragraphs)))
    if word_count != 279:
        raise ValueError(f"rejected candidate word count drifted: {word_count}")
    return paragraphs, screen


def build_quarantine_fields(screen: dict[str, Any]) -> dict[str, Any]:
    """Return the non-negotiable invalid-input authority fields."""
    return {
        "input_admissibility": "rejected",
        "authority": "invalid-input diagnostic only",
        "included_in_lane_a_results": False,
        "candidate_raw_sha256": "sha256:" + CANDIDATE_RAW_SHA256,
        "rejection_receipt_sha256": "sha256:" + REJECTION_RECEIPT_SHA256,
        "rejection_reasons": list(screen["reasons"]),
        "rejection_hits": screen["banned_outcome_verb_hits"],
        "interpretation_rule": (
            "CAL behavior on this rejected input is not a dilution result and cannot "
            "rehabilitate the artifact."
        ),
    }


def build_request(candidate_dir: Path) -> tuple[AuditRequest, dict[str, Any], dict[str, Any]]:
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
                "source": "generation-01-negative-control",
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
    return request, screen, construction


def run_once(
    candidate_dir: Path,
    baseline_run: Path,
    preregistration: Path,
    expected_preregistration_sha256: str,
    expected_runner_sha256: str,
    out: Path,
) -> dict[str, Any]:
    """Preflight, consume one diagnostic run, and preserve its quarantine."""
    if out.exists():
        raise FileExistsError(f"rejected-control output already exists; rerun forbidden: {out}")
    if sha256_file(Path(__file__)) != expected_runner_sha256:
        raise ValueError("rejected-control runner hash mismatch")
    if sha256_file(preregistration) != expected_preregistration_sha256:
        raise ValueError("rejected-control preregistration hash mismatch")
    cal_boundary = verify_workbench_boundary(Path(__file__).resolve().parents[1])
    baseline = load_baseline_atom(baseline_run)
    request, screen, construction = build_request(candidate_dir)

    out.mkdir(parents=True, exist_ok=False)
    started_at = utc_now()
    attempt = {
        "schema_version": "cal-rejected-input-control-attempt-v1",
        "status": "inference_starting",
        "started_at_utc": started_at,
        "command": sys.argv,
        **build_quarantine_fields(screen),
        "preregistration_sha256": "sha256:" + expected_preregistration_sha256,
        "runner_sha256": "sha256:" + expected_runner_sha256,
        "cal_boundary": cal_boundary,
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
            "schema_version": "cal-rejected-input-control-error-v1",
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
        "schema_version": "cal-rejected-input-control-result-v1",
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
        "construction": construction,
        "diagnostic_comparison": build_measurement_summary(
            trace_payload,
            baseline,
            retrieval_floor=request.audit_config.retrieval_floor,
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--expected-preregistration-sha256", required=True)
    parser.add_argument("--expected-runner-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
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
