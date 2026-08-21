"""Execute the single preregistered Lane A SLG-01-d T2 CAL measurement.

This command is intentionally single-shot. It completes every read-only
preflight check before creating the measured-run directory. Immediately before
the one ``run_default_audit`` call it writes ``attempt-start.json``; from that
point any success or failure consumes the run directory and blocks a rerun.

Do not invoke without Cameron's separate approval of the exact command and
prepared receipt hashes. DEV evidence only; never validation or gate evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.runner import run_default_audit

try:
    from scripts.pilot001_premise_granularity_run04 import build_request_index
    from scripts.simple_logic_gold_direct_lane import _map_cal_verdict
    from scripts.slg_scaled_first_cell_prepare import (
        ATOM_ID,
        CANDIDATE_RAW_SHA256,
        CLAIM_TEXT,
        FACT_ID,
        FACT_TEXT,
        PASSAGE_IDS,
        WORLD_ID,
        sha256_file,
        sha256_text,
        verify_sha256_manifest,
        verify_workbench_boundary,
        write_recursive_manifest,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from pilot001_premise_granularity_run04 import (  # type: ignore[no-redef]
        build_request_index,
    )
    from simple_logic_gold_direct_lane import _map_cal_verdict  # type: ignore[no-redef]
    from slg_scaled_first_cell_prepare import (  # type: ignore[no-redef]
        ATOM_ID,
        CANDIDATE_RAW_SHA256,
        CLAIM_TEXT,
        FACT_ID,
        FACT_TEXT,
        PASSAGE_IDS,
        WORLD_ID,
        sha256_file,
        sha256_text,
        verify_sha256_manifest,
        verify_workbench_boundary,
        write_recursive_manifest,
    )

BASELINE_RUN_SHA256 = "c60a30129a055791e8392ef20c3fb991358ca644a0109b09f18e9901184c92f5"
AUDIT_CONFIG_HASH = "sha256:739fc95bb6920b47a3a8d4c8242751ebc83322ae3fdc2aa5fcb18e855e0e12c7"
SOURCE_ID = "src-slg-01-d-t2"
QUALIFIED_PASSAGE_IDS = tuple(f"{SOURCE_ID}/{passage_id}" for passage_id in sorted(PASSAGE_IDS))


def is_fact_passage_id(passage_id: str) -> bool:
    """Accept the raw scaffold ID or Evidence Bundler's source-qualified ID."""
    return passage_id == FACT_ID or passage_id == f"{SOURCE_ID}/{FACT_ID}"


def utc_now() -> str:
    """Return an RFC 3339 UTC timestamp."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def load_baseline_atom(path: Path) -> dict[str, Any]:
    """Load the exact preserved T1 record without rerunning it."""
    if sha256_file(path) != BASELINE_RUN_SHA256:
        raise ValueError("preserved T1 domain-run hash mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    atoms = [atom for atom in payload["atoms"] if atom["atom_id"] == ATOM_ID]
    if len(atoms) != 1:
        raise ValueError(f"preserved T1 must contain exactly one {ATOM_ID} record")
    atom = atoms[0]
    if (
        atom.get("base_case_id"),
        atom.get("expected_relation"),
        atom.get("cal_support_verdict"),
        atom.get("cal_observed_relation"),
        atom.get("match"),
    ) != (WORLD_ID, "supports", "supported", "supports", True):
        raise ValueError("preserved T1 outcome drifted from the preregistration")
    trace = atom["trace"]
    if trace.get("audit_config_hash") != AUDIT_CONFIG_HASH:
        raise ValueError("preserved T1 config hash drifted")
    if trace.get("claim_text") != CLAIM_TEXT:
        raise ValueError("preserved T1 claim text drifted")
    return atom


def build_measurement_summary(
    trace: dict[str, Any], baseline: dict[str, Any], *, retrieval_floor: float
) -> dict[str, Any]:
    """Build the preregistered primary/secondary comparison fields."""
    retrieval = trace["retrieval"]
    fact_rows = [
        (rank, row)
        for rank, row in enumerate(retrieval, start=1)
        if is_fact_passage_id(row["passage_id"])
    ]
    if len(fact_rows) > 1:
        raise ValueError("fresh trace contains duplicate load-bearing fact retrieval rows")
    fact_rank = fact_rows[0][0] if fact_rows else None
    fact_score = fact_rows[0][1]["score"] if fact_rows else None
    fact_retrieved = fact_rank is not None
    floor_survival = fact_score is not None and fact_score >= retrieval_floor
    contributing_id = trace["support_signal"]["contributing_passage_id"]
    contributing = contributing_id is not None and is_fact_passage_id(contributing_id)
    verdict_supported = trace["verdict"]["support_verdict"] == "supported"
    observed_relation = _map_cal_verdict(trace["verdict"]["support_verdict"])
    verdict_stable = observed_relation == baseline["cal_observed_relation"]
    flags = list(trace["verdict"]["audit_flags"])

    failure_classes: list[str] = []
    if not fact_retrieved:
        failure_classes.append("fact_outside_top_k")
    if fact_retrieved and not floor_survival:
        failure_classes.append("fact_below_floor")
    if not contributing:
        failure_classes.append("fact_not_contributing")
    if trace["verdict"].get("support_verdict_reason") == "no_entail_signal":
        failure_classes.append("no_entail_signal")
    if not verdict_stable:
        failure_classes.append("verdict_flip")
    if flags:
        failure_classes.append("unexpected_audit_flag")

    stable = all((verdict_stable, fact_retrieved, floor_survival, contributing, verdict_supported))
    return {
        "primary": {
            "verdict_stable_vs_preserved_t1": verdict_stable,
            "fact_retrieved": fact_retrieved,
            "fact_at_or_above_floor": floor_survival,
            "fact_is_contributing_passage": contributing,
            "t2_verdict_supported": verdict_supported,
            "classification": "stable" if stable else "first_cell_failure",
            "failure_classes": failure_classes,
        },
        "secondary": {
            "fact_retrieval_rank": fact_rank,
            "fact_retrieval_score": fact_score,
            "ordered_retrieval": retrieval,
            "entailment_call_count": len(trace["entailment"]),
            "entailment": trace["entailment"],
            "max_entailment_score": trace["support_signal"]["max_entailment_score"],
            "support_verdict_reason": trace["verdict"].get("support_verdict_reason"),
            "rules_fired": trace["rules_fired"],
            "audit_flags": flags,
        },
        "comparison": {
            "t1_source": "preserved; not rerun",
            "t1_support_verdict": baseline["cal_support_verdict"],
            "t1_observed_relation": baseline["cal_observed_relation"],
            "t2_support_verdict": trace["verdict"]["support_verdict"],
            "t2_observed_relation": observed_relation,
        },
    }


def preflight(
    packet: Path,
    preparation_receipt: Path,
    expected_preparation_sha256: str,
    expected_manifest_sha256: str,
    preregistration: Path,
    expected_preregistration_sha256: str,
    expected_runner_sha256: str,
    baseline_run: Path,
) -> tuple[Any, dict[str, Any], dict[str, Any], dict[str, str]]:
    """Perform every possible check before consuming the measured run."""
    if sha256_file(Path(__file__)) != expected_runner_sha256:
        raise ValueError("measured runner hash does not match the approved command")
    if sha256_file(preregistration) != expected_preregistration_sha256:
        raise ValueError("preregistration hash does not match the approved command")
    prep_root = preparation_receipt.parent.resolve()
    if packet.resolve() != prep_root / "packet":
        raise ValueError("packet must be the packet directory adjacent to preparation receipt")
    if sha256_file(preparation_receipt) != expected_preparation_sha256:
        raise ValueError("preparation receipt hash does not match the approved command")
    manifest = prep_root / "SHA256SUMS"
    if sha256_file(manifest) != expected_manifest_sha256:
        raise ValueError("preparation manifest hash does not match the approved command")
    verify_sha256_manifest(prep_root, manifest)

    prep = json.loads(preparation_receipt.read_text(encoding="utf-8"))
    if prep.get("measured_inference_run") is not False:
        raise ValueError("preparation receipt does not declare zero measured inference")
    if prep.get("next_gate") != "Cameron approval of the exact measured-run command":
        raise ValueError("preparation receipt approval boundary drifted")
    if prep.get("inputs", {}).get("candidate_raw_sha256") != ("sha256:" + CANDIDATE_RAW_SHA256):
        raise ValueError("preparation receipt does not bind the approved candidate")
    construction = prep.get("construction", {})
    if construction.get("passage_order") != list(PASSAGE_IDS):
        raise ValueError("prepared passage order drifted")
    if construction.get("fact_insert_after_filler_paragraph") != 3:
        raise ValueError("prepared fact placement drifted")

    workbench = Path(__file__).resolve().parents[1]
    cal_boundary = verify_workbench_boundary(workbench)
    config = load_default_audit_config()
    config_hash = hash_audit_config(config)
    if config_hash != AUDIT_CONFIG_HASH or config.top_k != 5 or config.retrieval_floor != 0.40:
        raise ValueError(
            "CAL default configuration drifted: "
            f"hash={config_hash} top_k={config.top_k} floor={config.retrieval_floor}"
        )
    baseline = load_baseline_atom(baseline_run)
    requests = build_request_index(packet, config)
    if set(requests) != {ATOM_ID}:
        raise ValueError(f"prepared packet request IDs drifted: {sorted(requests)}")
    request = requests[ATOM_ID]
    if request.claim_text != CLAIM_TEXT:
        raise ValueError("prepared request claim text drifted")
    observed_ids = [passage.passage_id for passage in request.passages]
    if observed_ids != list(QUALIFIED_PASSAGE_IDS):
        raise ValueError(f"prepared request passage order drifted: {observed_ids}")
    text_hashes = construction.get("passage_text_sha256", {})
    for passage in request.passages:
        raw_passage_id = passage.passage_id.removeprefix(f"{SOURCE_ID}/")
        expected = text_hashes.get(raw_passage_id)
        actual = sha256_text(passage.text)
        if expected != actual:
            raise ValueError(f"prepared passage text drifted: {passage.passage_id}")
    fact = next(passage for passage in request.passages if is_fact_passage_id(passage.passage_id))
    if fact.text != FACT_TEXT:
        raise ValueError("load-bearing fact text drifted")
    return request, baseline, prep, cal_boundary


def run_once(
    packet: Path,
    preparation_receipt: Path,
    expected_preparation_sha256: str,
    expected_manifest_sha256: str,
    preregistration: Path,
    expected_preregistration_sha256: str,
    expected_runner_sha256: str,
    baseline_run: Path,
    out: Path,
) -> dict[str, Any]:
    """Preflight, consume one run, and preserve success or error evidence."""
    if out.exists():
        raise FileExistsError(f"measured-run directory already exists; rerun forbidden: {out}")
    request, baseline, prep, cal_boundary = preflight(
        packet,
        preparation_receipt,
        expected_preparation_sha256,
        expected_manifest_sha256,
        preregistration,
        expected_preregistration_sha256,
        expected_runner_sha256,
        baseline_run,
    )
    config = load_default_audit_config()
    out.mkdir(parents=True, exist_ok=False)
    started_at = utc_now()
    attempt = {
        "schema_version": "cal-lane-a-first-cell-attempt-v1",
        "label": "DEV-only measured attempt; not validation or gate evidence",
        "status": "inference_starting",
        "started_at_utc": started_at,
        "command": sys.argv,
        "world_id": WORLD_ID,
        "atom_id": ATOM_ID,
        "preparation_receipt_sha256": "sha256:" + expected_preparation_sha256,
        "preparation_manifest_sha256": "sha256:" + expected_manifest_sha256,
        "preregistration_sha256": "sha256:" + expected_preregistration_sha256,
        "runner_sha256": "sha256:" + expected_runner_sha256,
        "baseline_run_sha256": "sha256:" + BASELINE_RUN_SHA256,
        "audit_config_hash": AUDIT_CONFIG_HASH,
        "cal_boundary": cal_boundary,
    }
    (out / "attempt-start.json").write_text(
        json.dumps(attempt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    start = time.perf_counter()
    try:
        trace = run_default_audit(request)
    except BaseException as exc:
        elapsed = time.perf_counter() - start
        error = {
            "schema_version": "cal-lane-a-first-cell-error-v1",
            "status": "inference_error_run_consumed",
            "finished_at_utc": utc_now(),
            "wall_time_seconds": elapsed,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "rerun_allowed": False,
        }
        (out / "attempt-error.json").write_text(
            json.dumps(error, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        write_recursive_manifest(out)
        raise

    elapsed = time.perf_counter() - start
    trace_payload = trace.model_dump(mode="json")
    summary = build_measurement_summary(
        trace_payload, baseline, retrieval_floor=config.retrieval_floor
    )
    result: dict[str, Any] = {
        "schema_version": "cal-lane-a-first-cell-result-v1",
        "label": "DEV-only first-cell result; not validation or gate evidence",
        "status": "completed_run_consumed",
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "wall_time_seconds": elapsed,
        "lane": "A",
        "world_id": WORLD_ID,
        "atom_id": ATOM_ID,
        "tier": "T2",
        "difficulty": "easy",
        "genre": "pharmaceutical-paperwork",
        "parameters": {
            "top_k": config.top_k,
            "retrieval_floor": config.retrieval_floor,
            "audit_config_hash": hash_audit_config(config),
        },
        "inputs": {
            "preparation_receipt_sha256": "sha256:" + expected_preparation_sha256,
            "preparation_manifest_sha256": "sha256:" + expected_manifest_sha256,
            "preregistration_sha256": "sha256:" + expected_preregistration_sha256,
            "runner_sha256": "sha256:" + expected_runner_sha256,
            "candidate_raw_sha256": prep["inputs"]["candidate_raw_sha256"],
            "baseline_run_sha256": "sha256:" + BASELINE_RUN_SHA256,
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
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--expected-preregistration-sha256", required=True)
    parser.add_argument("--expected-runner-sha256", required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run_once(
        args.packet.resolve(),
        args.preparation_receipt.resolve(),
        args.expected_preparation_sha256,
        args.expected_manifest_sha256,
        args.preregistration.resolve(),
        args.expected_preregistration_sha256,
        args.expected_runner_sha256,
        args.baseline_run.resolve(),
        args.out.resolve(),
    )
    print(json.dumps(result["primary"], sort_keys=True))


if __name__ == "__main__":
    main()
