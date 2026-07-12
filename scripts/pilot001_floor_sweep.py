"""Run and diff PILOT-001 retrieval-floor development experiments.

This is deliberately an in-process tool. ``claim-audit calibrate --config``
materializes verdict thresholds from the packaged rules file and therefore
cannot express a temporary retrieval-floor experiment. Here the shipped
default is loaded once and copied with only ``retrieval_floor`` changed; the
rules file and every other config field remain pinned, while the resulting
``audit_config_hash`` honestly changes.

The tool treats the run-01 traces as an immutable baseline, verifies that they
match the shipped 0.40 config hash and the supplied gold, runs each requested
floor, and writes deterministic per-claim diffs.

Usage (from the workbench venv)::

    python scripts/pilot001_floor_sweep.py \
      --packet ../../scaffold-claims-study/workbench/reproduce/build/\
pilot-001-v2-audit/bundles \
      --gold ../outputs/pilot-001-dev-calibration/\
run-01-2026-07-03/gold.dev.yaml \
      --baseline-run ../outputs/pilot-001-dev-calibration/\
run-01-2026-07-03 \
      --out ../outputs/pilot-001-dev-calibration/\
run-02-floor-sweep-2026-07-03 \
      --floors 0.35 0.30 \
      --pinned-at 2026-07-03T00:00:00Z
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Literal

import yaml

from claim_audit_lab.v1.calibrate import (
    CalibrationGold,
    CalibrationResult,
    compute_calibration,
    crosswalk_gold,
    load_gold,
    render_report,
    run_calibration,
)
from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.models import AuditConfig, AuditTrace

DiffClass = Literal[
    "recovered",
    "regressed",
    "changed_but_still_miss",
    "unchanged_match",
    "unchanged_miss",
]

_DIFF_FIELDS = (
    "claim_id",
    "gold_raw",
    "gold_crosswalk",
    "baseline_verdict",
    "candidate_verdict",
    "classification",
    "baseline_reason",
    "candidate_reason",
    "baseline_support_signal",
    "candidate_support_signal",
    "baseline_entailment_count",
    "candidate_entailment_count",
    "newly_admitted_passage_ids",
    "new_gold_supported_to_cal_contradicted",
)


def load_traces(path: Path) -> dict[str, AuditTrace]:
    """Load all trace JSON files in ``path`` keyed by claim ID, fail-closed."""
    traces: dict[str, AuditTrace] = {}
    for trace_path in sorted(path.glob("*.json")):
        trace = AuditTrace.model_validate_json(trace_path.read_text(encoding="utf-8"))
        if trace.claim_id in traces:
            raise ValueError(f"duplicate trace claim_id: {trace.claim_id}")
        if trace_path.stem != trace.claim_id:
            raise ValueError(
                f"trace filename/claim_id mismatch: {trace_path.name} != {trace.claim_id}.json"
            )
        traces[trace.claim_id] = trace
    if not traces:
        raise ValueError(f"no trace JSON files found in {path}")
    return traces


def classify_diff(gold: str, baseline: str, candidate: str) -> DiffClass:
    """Classify one candidate verdict relative to run-01 and gold."""
    baseline_match = baseline == gold
    candidate_match = candidate == gold
    if not baseline_match and candidate_match:
        return "recovered"
    if baseline_match and not candidate_match:
        return "regressed"
    if not baseline_match and not candidate_match and baseline != candidate:
        return "changed_but_still_miss"
    if candidate_match:
        return "unchanged_match"
    return "unchanged_miss"


def build_diff_rows(
    gold: CalibrationGold,
    baseline: dict[str, AuditTrace],
    candidate: dict[str, AuditTrace],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return per-claim diff rows plus a compact classification summary."""
    gold_by_id = {claim.claim_id: claim for claim in gold.claims}
    expected = set(gold_by_id)
    for name, traces in (("baseline", baseline), ("candidate", candidate)):
        missing = sorted(expected - set(traces))
        extra = sorted(set(traces) - expected)
        if missing or extra:
            raise ValueError(
                f"{name}/gold trace alignment failed: missing={missing}, extra={extra}"
            )

    rows: list[dict[str, Any]] = []
    for claim_id in sorted(expected):
        gold_claim = gold_by_id[claim_id]
        gold_verdict = crosswalk_gold(gold_claim.gold_verdict, gold_claim.gold_flags)
        baseline_trace = baseline[claim_id]
        candidate_trace = candidate[claim_id]
        baseline_degree = baseline_trace.verdict.support_verdict
        candidate_degree = candidate_trace.verdict.support_verdict
        gold_degree = gold_verdict.support_verdict
        classification = classify_diff(gold_degree, baseline_degree, candidate_degree)
        baseline_admitted = {result.passage_id for result in baseline_trace.entailment}
        candidate_admitted = {result.passage_id for result in candidate_trace.entailment}
        new_false_contradiction = (
            gold_degree == "supported"
            and baseline_degree != "contradicted"
            and candidate_degree == "contradicted"
        )
        rows.append(
            {
                "claim_id": claim_id,
                "gold_raw": gold_claim.gold_verdict,
                "gold_crosswalk": gold_degree,
                "baseline_verdict": baseline_degree,
                "candidate_verdict": candidate_degree,
                "classification": classification,
                "baseline_reason": baseline_trace.verdict.support_verdict_reason or "",
                "candidate_reason": candidate_trace.verdict.support_verdict_reason or "",
                "baseline_support_signal": baseline_trace.support_signal.label,
                "candidate_support_signal": candidate_trace.support_signal.label,
                "baseline_entailment_count": len(baseline_trace.entailment),
                "candidate_entailment_count": len(candidate_trace.entailment),
                "newly_admitted_passage_ids": ";".join(
                    sorted(candidate_admitted - baseline_admitted)
                ),
                "new_gold_supported_to_cal_contradicted": new_false_contradiction,
            }
        )

    counts = Counter(row["classification"] for row in rows)
    changed = [row for row in rows if row["baseline_verdict"] != row["candidate_verdict"]]
    summary: dict[str, Any] = {
        "claims": len(rows),
        "recovered": counts["recovered"],
        "regressed": counts["regressed"],
        "changed_but_still_miss": counts["changed_but_still_miss"],
        "unchanged_match": counts["unchanged_match"],
        "unchanged_miss": counts["unchanged_miss"],
        "verdict_changed": len(changed),
        "new_gold_supported_to_cal_contradicted": sum(
            bool(row["new_gold_supported_to_cal_contradicted"]) for row in rows
        ),
        "new_gold_supported_to_cal_contradicted_claim_ids": [
            row["claim_id"] for row in rows if row["new_gold_supported_to_cal_contradicted"]
        ],
    }
    return rows, summary


def write_diff(
    output_dir: Path,
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    """Write deterministic machine-readable diff artifacts."""
    with (output_dir / "per-claim-diff.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_DIFF_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    _write_json(output_dir / "diff-summary.json", summary)


def write_run_artifacts(
    output_dir: Path,
    result: CalibrationResult,
    traces: dict[str, AuditTrace],
    config: AuditConfig,
    *,
    pinned_at: str,
) -> None:
    """Write one floor's report, traces, config, and metric result."""
    output_dir.mkdir(parents=True, exist_ok=True)
    traces_dir = output_dir / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "calibration-report.md").write_text(
        render_report(result, pinned_at=pinned_at), encoding="utf-8"
    )
    (output_dir / "audit-config.yaml").write_text(
        yaml.safe_dump(config.model_dump(mode="json"), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    _write_json(output_dir / "calibration-result.json", result.model_dump(mode="json"))
    for claim_id in sorted(traces):
        (traces_dir / f"{claim_id}.json").write_text(
            traces[claim_id].model_dump_json(indent=2) + "\n", encoding="utf-8"
        )


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_baseline_config(traces: dict[str, AuditTrace], config: AuditConfig) -> str:
    hashes = {trace.audit_config_hash for trace in traces.values()}
    expected = hash_audit_config(config)
    if hashes != {expected}:
        raise ValueError(
            "baseline traces do not match the shipped default 0.40 config: "
            f"trace hashes={sorted(hashes)}, expected={expected}"
        )
    return expected


def run_sweep(args: argparse.Namespace) -> None:
    """Execute all requested floors and write reports, traces, and diffs."""
    base_config = load_default_audit_config()
    if base_config.retrieval_floor != 0.40:
        raise ValueError(
            f"expected shipped retrieval_floor 0.40, got {base_config.retrieval_floor}"
        )
    gold = load_gold(args.gold)
    baseline = load_traces(args.baseline_run / "traces")
    baseline_hash = _assert_baseline_config(baseline, base_config)
    baseline_result = compute_calibration(baseline, gold, base_config)

    args.out.mkdir(parents=True, exist_ok=True)
    copied_gold = args.out / "gold.dev.yaml"
    shutil.copyfile(args.gold, copied_gold)
    _write_json(args.out / "baseline-result.json", baseline_result.model_dump(mode="json"))

    metadata: dict[str, Any] = {
        "label": "dev (adaptation set), not validated and not a gate",
        "packet": str(args.packet.resolve()),
        "gold_source": str(args.gold.resolve()),
        "gold_copy": str(copied_gold.resolve()),
        "gold_sha256": _sha256(copied_gold),
        "baseline_run": str(args.baseline_run.resolve()),
        "baseline_audit_config_hash": baseline_hash,
        "baseline_exact": {
            "agree": baseline_result.agreement.n_agree,
            "total": baseline_result.agreement.n_total,
        },
        "pinned_at": args.pinned_at,
        "floors": [],
    }

    # Heavy inference import is intentionally local. Model constructors cache
    # weights across floors in this one background process.
    from claim_audit_lab.v1.runner import run_default_audit

    for floor in args.floors:
        config = base_config.model_copy(update={"retrieval_floor": floor})
        floor_dir = args.out / f"floor-{floor:.2f}"
        print(f"starting retrieval_floor={floor:.2f}", file=sys.stderr, flush=True)
        result, traces = run_calibration(
            args.packet,
            gold,
            config,
            auditor=run_default_audit,
            deviations_dir=floor_dir / "deviations",
        )
        write_run_artifacts(
            floor_dir,
            result,
            traces,
            config,
            pinned_at=args.pinned_at,
        )
        rows, summary = build_diff_rows(gold, baseline, traces)
        summary = {
            "retrieval_floor": floor,
            "audit_config_hash": result.audit_config_hash,
            **summary,
        }
        write_diff(floor_dir, rows, summary)
        metadata["floors"].append(
            {
                "retrieval_floor": floor,
                "output": str(floor_dir.resolve()),
                "audit_config_hash": result.audit_config_hash,
                "exact_agree": result.agreement.n_agree,
                "exact_total": result.agreement.n_total,
            }
        )
        _write_json(args.out / "sweep-metadata.json", metadata)
        print(
            f"finished retrieval_floor={floor:.2f}: "
            f"exact={result.agreement.n_agree}/{result.agreement.n_total}; "
            f"recovered={summary['recovered']}; regressed={summary['regressed']}; "
            f"new_supported_to_contradicted="
            f"{summary['new_gold_supported_to_cal_contradicted']}",
            file=sys.stderr,
            flush=True,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--baseline-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--floors", type=float, nargs="+", required=True)
    parser.add_argument("--pinned-at", required=True)
    args = parser.parse_args()
    if len(set(args.floors)) != len(args.floors):
        parser.error("--floors must not contain duplicates")
    for floor in args.floors:
        if not 0.0 <= floor <= 1.0:
            parser.error(f"floor outside [0, 1]: {floor}")
        if floor == 0.40:
            parser.error("0.40 is the immutable run-01 baseline, not a sweep candidate")
    return args


if __name__ == "__main__":
    run_sweep(parse_args())
