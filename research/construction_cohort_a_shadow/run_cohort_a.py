#!/usr/bin/env python3
"""Run blind Construction Cohort A through the frozen explicit shadow apparatus."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.models import AuditRequest, Passage
from claim_audit_lab.v1.runner import run_default_audit
from research.production_trace_decision_shadow import run_shadow_experiment as predecessor
from research.shadow_reconciliation_semantic_operator_rc.parallel_artifact import (
    build_completed_artifact,
    build_failure_artifact,
)
from scripts.decision_model_replay import build_report
from scripts.evidence_state_eligibility_shadow import build_eligibility_report
from scripts.evidence_state_operator_shadow import build_operator_report

SUPPORT_THRESHOLD = 0.70
REFUTATION_THRESHOLD = 0.70
SIGNAL_FLOOR = 0.20


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _trust_map(request: AuditRequest) -> dict[str, str]:
    trust: dict[str, str] = {}
    for passage in request.passages:
        level = passage.source_meta.get("trust_level")
        if level is not None:
            trust[passage.passage_id.split("/", 1)[0]] = level
    return trust


def _legacy_group(verdict: str) -> str:
    if verdict in {"supported", "partially_supported"}:
        return "support"
    if verdict in {"unsupported", "contradicted"}:
        return "adverse"
    return "unknown"


def _candidate_group(outcome: str) -> str:
    if outcome == "supported":
        return "support"
    if outcome == "contradicted":
        return "adverse"
    return "unknown"


def run(manifest_path: Path, output_dir: Path, *, execution_head_sha: str) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["n_cases"] != 33 or len(manifest["cases"]) != 33:
        raise RuntimeError("Cohort A manifest must contain exactly 33 cases")

    forbidden = {"expected_verdict", "gold", "gold_verdict", "derivation", "expected_rule"}
    encoded = json.dumps(manifest)
    for key in forbidden:
        if f'"{key}"' in encoded:
            raise RuntimeError(f"assessment leakage in execution manifest: {key}")

    config = load_default_audit_config()
    if config.supported_threshold != SUPPORT_THRESHOLD:
        raise RuntimeError("support threshold drift")
    if config.contradicted_threshold != REFUTATION_THRESHOLD:
        raise RuntimeError("refutation threshold drift")

    output_dir.mkdir(parents=True, exist_ok=True)
    cases_root = output_dir / "cases"
    artifacts_root = output_dir / "parallel-artifacts"
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for case in manifest["cases"]:
        claim_id = str(case["claim_id"])
        case_dir = cases_root / claim_id
        try:
            request = AuditRequest(
                claim_id=claim_id,
                claim_text=str(case["claim_text"]),
                passages=[
                    Passage(passage_id=str(p["passage_id"]), text=str(p["text"]))
                    for p in case["passages"]
                ],
                audit_config=config,
                source_boundary=str(case["source_boundary"]),
                claimed_material_is_a_named_gap=bool(
                    case.get("claimed_material_is_a_named_gap", False)
                ),
            )
            request_path = case_dir / "audit-request.json"
            request_path.parent.mkdir(parents=True, exist_ok=True)
            request_path.write_text(request.model_dump_json(indent=2) + "\n", encoding="utf-8")

            trace = run_default_audit(request)
            trace_dir = case_dir / "traces"
            trace_dir.mkdir(parents=True, exist_ok=True)
            trace_path = trace_dir / f"{claim_id}.json"
            trace_path.write_text(trace.model_dump_json(indent=2) + "\n", encoding="utf-8")

            eligibility = build_eligibility_report(
                trace_dir,
                signal_floor=SIGNAL_FLOOR,
                trust_by_source=_trust_map(request),
            )
            eligibility_path = case_dir / "eligibility-shadow.json"
            _write_json(eligibility_path, eligibility)

            operator = build_operator_report(eligibility, [])
            operator_path = case_dir / "operator-shadow.json"
            _write_json(operator_path, operator)

            replay = build_report(
                eligibility_path,
                operator_path,
                support_threshold=SUPPORT_THRESHOLD,
                refutation_threshold=REFUTATION_THRESHOLD,
            )
            replay_row = replay["rows"][0]
            candidate = replay_row["candidate"]

            comparison = {
                "claim_id": claim_id,
                "request_receipt_sha256": _sha(request_path),
                "trace_receipt_sha256": _sha(trace_path),
                "legacy": {
                    "verdict": trace.verdict.model_dump(mode="json"),
                    "rules_fired": [item.model_dump(mode="json") for item in trace.rules_fired],
                    "retrieval": [item.model_dump(mode="json") for item in trace.retrieval],
                    "admitted_passage_ids": [item.passage_id for item in trace.entailment],
                    "nli_measurements": [
                        item.model_dump(mode="json") for item in trace.entailment
                    ],
                    "support_signal": trace.support_signal.model_dump(mode="json"),
                    "audit_config_hash": trace.audit_config_hash,
                    "library_version": trace.library_version,
                    "negation_probe": (
                        trace.negation_probe.model_dump(mode="json")
                        if trace.negation_probe
                        else None
                    ),
                },
                "explicit": {
                    "candidate_outcome": replay_row["candidate_outcome"],
                    "candidate": candidate,
                    "eligibility_row": eligibility["rows"][0],
                    "operator_row": operator["rows"][0],
                    "adapter_exclusions": replay_row["adapter_exclusions"],
                },
            }

            first_divergence = predecessor._first_divergence(trace, replay_row)
            legacy_outcome = trace.verdict.support_verdict
            explicit_outcome = replay_row["candidate_outcome"]
            comparison["comparison"] = {
                "legacy_outcome": legacy_outcome,
                "candidate_outcome": explicit_outcome,
                "first_divergence_stage": first_divergence,
                "candidate_reason": candidate["decision"]["reason_code"],
            }
            comparison["input_metadata"] = {
                key: case.get(key)
                for key in (
                    "case_id",
                    "relation",
                    "source_boundary",
                    "variant_group",
                    "n_distractor_passages",
                    "multi_document",
                    "distractor_kind",
                )
            }
            _write_json(case_dir / "comparison.json", comparison)

            artifact = build_completed_artifact(
                comparison,
                request.model_dump(mode="json"),
                execution_head_sha=execution_head_sha,
            )
            artifact_path = artifacts_root / f"{claim_id}.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(artifact.model_dump_json(indent=2) + "\n", encoding="utf-8")

            unknown_validities = [
                item
                for item in candidate["inputs"]["contributions"]
                if item["validity"]["status"] == "unknown"
            ]
            operator_statuses = Counter(
                (str(item["validity"]["operator"]), str(item["validity"]["status"]))
                for item in candidate["inputs"]["contributions"]
            )
            rows.append(
                {
                    "case_id": case["case_id"],
                    "claim_id": claim_id,
                    "relation": case["relation"],
                    "source_boundary": case["source_boundary"],
                    "variant_group": case.get("variant_group"),
                    "legacy_outcome": legacy_outcome,
                    "candidate_outcome": explicit_outcome,
                    "first_divergence_stage": first_divergence,
                    "raw_state": candidate["raw"]["state"],
                    "eligible_state": candidate["eligible"]["state"],
                    "valid_state": candidate["valid"]["state"],
                    "decision_reason": candidate["decision"]["reason_code"],
                    "unknown_semantic_validity_count": len(unknown_validities),
                    "operator_statuses": [
                        {"operator": op, "status": status, "count": count}
                        for (op, status), count in sorted(operator_statuses.items())
                    ],
                    "aperture_statuses": [
                        {"channel": a["channel"], "status": a["status"], "reason": a["reason"]}
                        for a in candidate["inputs"]["apertures"]
                    ],
                    "source_passage_ids": [p["passage_id"] for p in case["passages"]],
                    "artifact_sha256": _sha(artifact_path),
                }
            )
        except Exception as exc:
            failure = build_failure_artifact(
                claim_id=claim_id,
                failure_class=type(exc).__name__,
                failure_detail=str(exc),
                execution_head_sha=execution_head_sha,
            )
            path = artifacts_root / f"{claim_id}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(failure.model_dump_json(indent=2) + "\n", encoding="utf-8")
            failures.append(
                {
                    "case_id": case["case_id"],
                    "claim_id": claim_id,
                    "failure_class": type(exc).__name__,
                    "failure_detail": str(exc),
                    "artifact_sha256": _sha(path),
                }
            )

    first_divergence = Counter(
        row["first_divergence_stage"] or "none" for row in rows
    )
    valid_states = Counter(row["valid_state"] for row in rows)
    decision_reasons = Counter(row["decision_reason"] for row in rows)
    legacy_counts = Counter(row["legacy_outcome"] for row in rows)
    candidate_counts = Counter(row["candidate_outcome"] for row in rows)

    support_to_adverse = sum(
        _legacy_group(row["legacy_outcome"]) == "support"
        and _candidate_group(row["candidate_outcome"]) == "adverse"
        for row in rows
    )
    adverse_to_support = sum(
        _legacy_group(row["legacy_outcome"]) == "adverse"
        and _candidate_group(row["candidate_outcome"]) == "support"
        for row in rows
    )
    unknown_validity_cases = sum(row["unknown_semantic_validity_count"] > 0 for row in rows)
    aperture_failure_cases = sum(
        any(item["status"] != "complete" for item in row["aperture_statuses"]) for row in rows
    )

    by_variant: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["variant_group"]:
            by_variant[str(row["variant_group"])].append(row)
    variant_groups = {
        gid: {
            "members": [r["case_id"] for r in members],
            "legacy_outcomes": {r["case_id"]: r["legacy_outcome"] for r in members},
            "candidate_outcomes": {r["case_id"]: r["candidate_outcome"] for r in members},
            "explicit_valid_states": {r["case_id"]: r["valid_state"] for r in members},
        }
        for gid, members in sorted(by_variant.items())
    }

    result = {
        "schema_version": "cal-construction-cohort-a-shadow-v0.1",
        "experiment_class": "Research Infrastructure / epistemic-machinery",
        "authority": "non_authoritative_research",
        "execution_head_sha": execution_head_sha,
        "input_manifest_sha256": _sha(manifest_path),
        "input_manifest_cases": manifest["n_cases"],
        "threshold_tuning_performed": False,
        "production_behavior_changed": False,
        "summary": {
            "completed_cases": len(rows),
            "execution_failures": len(failures),
            "legacy_outcome_counts": dict(sorted(legacy_counts.items())),
            "candidate_outcome_counts": dict(sorted(candidate_counts.items())),
            "first_divergence_stage_counts": dict(sorted(first_divergence.items())),
            "explicit_valid_state_counts": dict(sorted(valid_states.items())),
            "decision_reason_counts": dict(sorted(decision_reasons.items())),
            "unknown_semantic_validity_cases": unknown_validity_cases,
            "aperture_failure_cases": aperture_failure_cases,
            "support_to_adverse_transitions": support_to_adverse,
            "adverse_to_support_transitions": adverse_to_support,
        },
        "variant_groups": variant_groups,
        "failures": failures,
        "rows": rows,
    }
    result_path = output_dir / "RESULTS.json"
    _write_json(result_path, result)
    (output_dir / "RESULTS.sha256").write_text(_sha(result_path) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execution-head-sha", default=os.environ.get("GITHUB_SHA", "local"))
    args = parser.parse_args()
    result = run(args.manifest, args.output_dir, execution_head_sha=args.execution_head_sha)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
