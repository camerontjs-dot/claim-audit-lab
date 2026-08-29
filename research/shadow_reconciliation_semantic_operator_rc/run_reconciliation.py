"""Reconcile the frozen production-trace shadow and emit research-only artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.semantic_operators import SemanticProbeReceipt, project_negation
from research.shadow_reconciliation_semantic_operator_rc.operator_contract import (
    a4_application,
    operator_contract_matrix,
)
from research.shadow_reconciliation_semantic_operator_rc.parallel_artifact import (
    build_completed_artifact,
)

E2E08_CLAIM = "The service meets 95 percent uptime and 40 percent capacity."
E2E09_CLAIM = "All submitted records pass schema validation."


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_case(root: Path, claim_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    case_dir = root / "cases" / claim_id
    comparison = json.loads((case_dir / "comparison.json").read_text(encoding="utf-8"))
    request = json.loads((case_dir / "audit-request.json").read_text(encoding="utf-8"))
    return comparison, request


def _synthetic_projection_cases() -> list[dict[str, Any]]:
    cases = [
        (
            "explicit_lexical_negation",
            "The batch was released on schedule.",
            "The batch was not released on schedule.",
        ),
        (
            "numeric_mismatch",
            E2E08_CLAIM,
            "The service meets 95 percent uptime and 70 percent capacity.",
        ),
        (
            "threshold_mismatch",
            "The batch potency is at least 40 percent.",
            "The batch potency is 35 percent.",
        ),
        (
            "quantity_mismatch",
            "The vial contains 5 milligrams of compound.",
            "The vial contains 9 milligrams of compound.",
        ),
        (
            "categorical_incompatibility",
            "The release status is approved.",
            "The release status is rejected.",
        ),
        (
            "scope_mismatch",
            "The Toronto site is validated for release.",
            "The Montreal site is not validated for release.",
        ),
    ]
    rendered: list[dict[str, Any]] = []
    for phenomenon, claim, evidence in cases:
        projection = project_negation(claim)
        rendered.append(
            {
                "phenomenon": phenomenon,
                "claim": claim,
                "evidence": evidence,
                "projection_kind": projection.kind,
                "canonical_complement": projection.complement,
                "projection_reason": projection.reason,
                "a4_has_canonical_target": projection.complement is not None,
                "note": "grammar/applicability probe only; evidence truth is not treated as gold",
            }
        )
    return rendered


def _a4_receipt(comparison: dict[str, Any]) -> SemanticProbeReceipt:
    probe = comparison["legacy"]["negation_probe"]
    passage_id = str(comparison["legacy"]["support_signal"]["contributing_passage_id"])
    if probe["abstained"]:
        return SemanticProbeReceipt(
            passage_ids=(passage_id,),
            hypothesis=None,
            label=None,
            abstained=True,
            evidence_path="frozen real AuditTrace.negation_probe",
            receipt_sha256=str(comparison["trace_receipt_sha256"]),
        )
    result = probe["result"]
    return SemanticProbeReceipt(
        passage_ids=(passage_id,),
        hypothesis=str(probe["negated_claim"]),
        label=str(result["label"]),
        abstained=False,
        evidence_path="frozen real AuditTrace.negation_probe",
        receipt_sha256=str(comparison["trace_receipt_sha256"]),
    )


def reconcile(shadow_root: Path, output_dir: Path, *, execution_head_sha: str) -> dict[str, Any]:
    predecessor = json.loads((shadow_root / "RESULTS.json").read_text(encoding="utf-8"))
    if predecessor["summary"]["total_claims"] != 25:
        raise RuntimeError("predecessor result is not the frozen 25-case diagnostic run")
    if predecessor["threshold_tuning_performed"]:
        raise RuntimeError("predecessor reports threshold tuning; reconciliation must stop")
    if predecessor["production_behavior_changed"]:
        raise RuntimeError("predecessor reports production behavior change; reconciliation must stop")

    e08, req08 = _load_case(shadow_root, "e2e-08")
    e09, req09 = _load_case(shadow_root, "e2e-09")
    if req08["claim_text"] != E2E08_CLAIM or req09["claim_text"] != E2E09_CLAIM:
        raise RuntimeError("receipt-bound focal claims drifted")

    a4 = a4_application(
        claim=req08["claim_text"],
        contribution_passage_ids=(
            str(e08["legacy"]["support_signal"]["contributing_passage_id"]),
        ),
        receipt=_a4_receipt(e08),
    )
    e08_refutation = next(
        item
        for item in e08["explicit"]["candidate"]["inputs"]["contributions"]
        if item["channel"] == "refutation"
    )
    h08_supported = (
        e08["legacy"]["negation_probe"]["abstained"] is True
        and e08["legacy"]["negation_probe"]["negated_claim"] is None
        and a4.applicability == "inapplicable"
        and a4.validity is None
        and e08_refutation["validity"]["status"] == "unknown"
    )

    e09_judgments = e09["explicit"]["operator_row"]["operator_judgments"]
    e09_refutation = next(
        item
        for item in e09["explicit"]["candidate"]["inputs"]["contributions"]
        if item["channel"] == "refutation"
    )
    h09_supported = (
        e09_judgments == []
        and e09_refutation["validity"]["status"] == "unknown"
        and e09_refutation["validity"]["operator"] == "refutation_operator_unmeasured"
        and e09["legacy"]["support_signal"]["max_entailment_score"] == 0.673828125
        and e09["legacy"]["verdict"]["support_verdict"] == "unsupported"
        and any(rule["rule_id"] == "B5_degree" for rule in e09["legacy"]["rules_fired"])
    )

    artifact_dir = output_dir / "parallel-artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_receipts: list[dict[str, str]] = []
    for case_dir in sorted((shadow_root / "cases").iterdir()):
        if not case_dir.is_dir():
            continue
        comparison = json.loads((case_dir / "comparison.json").read_text(encoding="utf-8"))
        request = json.loads((case_dir / "audit-request.json").read_text(encoding="utf-8"))
        artifact = build_completed_artifact(
            comparison,
            request,
            execution_head_sha=execution_head_sha,
        )
        path = artifact_dir / f"{artifact.claim_id}.json"
        path.write_text(artifact.model_dump_json(indent=2) + "\n", encoding="utf-8")
        artifact_receipts.append({"claim_id": artifact.claim_id, "sha256": _sha(path)})

    summary = predecessor["summary"]
    result = {
        "schema_version": "cal-shadow-reconciliation-semantic-operator-rc-v0.1",
        "experiment_class": "Research Infrastructure / epistemic-machinery",
        "authority": {
            "production_base_sha": predecessor["base_sha"],
            "predecessor_execution_head_sha": predecessor["execution_head_sha"],
            "successor_execution_head_sha": execution_head_sha,
            "predecessor_results_sha256": _sha(shadow_root / "RESULTS.json"),
        },
        "reproduction_audit": {
            "total_claims": summary["total_claims"],
            "terminal_agreements": summary["agreement_count"],
            "terminal_disagreements": summary["disagreement_count"],
            "support_to_adverse_transitions": summary["support_to_adverse_transitions"],
            "adverse_to_support_transitions": summary["adverse_to_support_transitions"],
            "first_divergence_stage_counts": summary["first_divergence_stage_counts"],
            "predecessor_metamorphic_all_passed": predecessor["metamorphic"]["all_passed"],
            "predecessor_metamorphic_n_passed": predecessor["metamorphic"]["n_passed"],
            "threshold_tuning_performed": predecessor["threshold_tuning_performed"],
            "production_behavior_changed": predecessor["production_behavior_changed"],
        },
        "e2e_08_falsifier": {
            "disposition": "SUPPORTED_WITH_BOUNDS" if h08_supported else "FALSIFIED",
            "claim": req08["claim_text"],
            "evidence": req08["passages"][0]["text"],
            "p_contradict": e08["legacy"]["nli_measurements"][0]["p_contradict"],
            "negation_probe": e08["legacy"]["negation_probe"],
            "a4_applicability": a4.applicability,
            "a4_projection_kind": a4.projection_kind,
            "a4_reason": a4.reason,
            "observed_explicit_validity": e08_refutation["validity"],
            "interpretation": (
                "A4 supplied no semantic measurement for this receipt-bound numeric mismatch. "
                "The predecessor replay represented the missing A4 result as unknown validity; "
                "the reconciliation distinguishes operator inapplicability from a measured unknown. "
                "No typed numeric-validity receipt is present, so the explicit refutation still may not decide."
            ),
        },
        "e2e_09_interpretation": {
            "disposition": "SUPPORTED_WITH_BOUNDS" if h09_supported else "FALSIFIED",
            "claim": req09["claim_text"],
            "evidence": req09["passages"][0]["text"],
            "p_contradict": e09["legacy"]["nli_measurements"][0]["p_contradict"],
            "frozen_refutation_threshold": e09["explicit"]["candidate"]["inputs"]["refutation_threshold"],
            "legacy_rule_ids": [item["rule_id"] for item in e09["legacy"]["rules_fired"]],
            "operator_judgment_count": len(e09_judgments),
            "observed_explicit_validity": e09_refutation["validity"],
            "interpretation": (
                "The frozen object contains a sub-threshold adverse NLI measurement and a B5 reporting degree, "
                "but no independent semantic-validity judgment. `unsupported` therefore cannot be reused as a "
                "validated adverse epistemic state without manufacturing missing assessment state."
            ),
        },
        "synthetic_operator_cases": _synthetic_projection_cases(),
        "operator_contract_matrix": list(operator_contract_matrix()),
        "parallel_artifact": {
            "justified": h08_supported and h09_supported,
            "authority": "non_authoritative_research",
            "n_artifacts": len(artifact_receipts),
            "artifact_receipts": artifact_receipts,
            "contract_c_changed": False,
            "audit_trace_replaced": False,
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "RESULTS.json"
    result_path.write_bytes(_canonical_bytes(result) + b"\n")
    (output_dir / "RESULTS.sha256").write_text(_sha(result_path) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shadow-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execution-head-sha", default=os.environ.get("GITHUB_SHA", "local"))
    args = parser.parse_args()
    result = reconcile(
        args.shadow_root,
        args.output_dir,
        execution_head_sha=args.execution_head_sha,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
