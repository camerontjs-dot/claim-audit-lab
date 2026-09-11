from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import fields as dataclass_fields
from dataclasses import replace
from pathlib import Path
from typing import Any

from claim_audit_lab.cal_v1_candidate import (
    AdmittedPassage,
    AuditContext,
    Conclusion,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
    audit,
    project_contract_c_successor,
)
from claim_audit_lab.cal_v1_candidate.authority import (
    AuthorityReceipt,
    AuthorityRefusal,
    complete_and_warrant,
)
from claim_audit_lab.cal_v1_candidate.cli import context_from_packet
from claim_audit_lab.cal_v1_candidate.engine import AuditResult, PassageTrace, compose
from claim_audit_lab.cal_v1_candidate.measurements import measure_strict_comparison
from claim_audit_lab.cal_v1_candidate.models import tagged_sha256
from claim_audit_lab.cal_v1_candidate.relations import BoundRelation, derive_relation

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
COHORT_PATH = HERE / "cohort.json"
GOLD_PATH = HERE / "gold.json"
FREEZE_PATH = HERE / "FREEZE_RECEIPT.json"
OUTPUT_PATH = HERE / "qualification_receipt.json"


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tagged(text: str) -> str:
    return "sha256:" + sha256_hex(text)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def build_context(case: dict[str, Any], *, bundle_suffix: str = "") -> AuditContext:
    case_id = str(case["case_id"])
    family = SemanticFamily(str(case["semantic_family"]))
    original_claim = str(case["original_claim"])
    raw_fields = case["fields"]
    if not isinstance(raw_fields, dict):
        raise ValueError(f"{case_id}: fields must be object")
    proposition = TypedProposition.create(
        f"prop-{case_id}",
        family,
        {str(key): str(value) for key, value in raw_fields.items()},
        text_sha256=sha256_hex(original_claim),
    )
    passages_raw = case["passages"]
    if not isinstance(passages_raw, list):
        raise ValueError(f"{case_id}: passages must be array")
    passages = tuple(
        AdmittedPassage.create(
            f"p{index}",
            f"source-{case_id}-{index}",
            str(text),
        )
        for index, text in enumerate(passages_raw, start=1)
    )
    bundle_id = f"bundle-{case_id}{bundle_suffix}"
    world = EvidenceWorld.create(
        "1.2.0",
        bundle_id,
        tagged(bundle_id),
        passages,
        {
            "search_scope": {"cohort": "cal-v1-fresh-qualification-20260911-15"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    return AuditContext(original_claim, proposition, world)


def verify_candidate_source(freeze: dict[str, Any]) -> dict[str, Any]:
    candidate = freeze["candidate"]
    source_root = ROOT / str(candidate["source_root"])
    expected = candidate["source_blobs"]
    observed: dict[str, str] = {}
    mismatches: dict[str, dict[str, str]] = {}
    for name, expected_sha in expected.items():
        path = source_root / name
        actual = subprocess.check_output(
            ["git", "hash-object", str(path.relative_to(ROOT))],
            cwd=ROOT,
            text=True,
        ).strip()
        observed[name] = actual
        if actual != expected_sha:
            mismatches[name] = {"expected": str(expected_sha), "observed": actual}
    return {
        "passed": not mismatches,
        "expected_commit": candidate["commit_sha"],
        "source_blobs": observed,
        "mismatches": mismatches,
    }


def expected_case_map(gold: dict[str, Any]) -> dict[str, dict[str, Any]]:
    cases = gold["cases"]
    if not isinstance(cases, dict):
        raise ValueError("gold cases must be object")
    return {str(key): dict(value) for key, value in cases.items()}


def classify_case(expected: dict[str, Any], result: AuditResult) -> str:
    wanted = str(expected["expected_conclusion"])
    actual = result.conclusion.value
    if actual == wanted:
        expected_failure = expected.get("expected_failure_code")
        actual_failure = None if result.failure_code is None else result.failure_code.value
        if actual_failure == expected_failure:
            return "exact"
        return "localization_mismatch"
    if wanted == "not_checkable" and actual in {"supported", "contradicted"}:
        return "unsafe"
    if wanted == "supported" and actual == "contradicted":
        return "unsafe"
    if wanted == "contradicted" and actual == "supported":
        return "unsafe"
    if bool(expected.get("decision_expected")) and actual == "not_checkable":
        return "safe_miss"
    return "mismatch"


def projection_check(context: AuditContext, result: AuditResult, semantic_sha: str) -> dict[str, Any]:
    payload = project_contract_c_successor(
        context,
        result,
        semantic_implementation_sha=semantic_sha,
    )
    expected_verdict = (
        "supported"
        if result.conclusion is Conclusion.SUPPORTED
        else "contradicted"
        if result.conclusion is Conclusion.CONTRADICTED
        else "not_checkable"
    )
    proposition = payload["propositions"][0]
    actual_verdict = proposition["conclusion"]["reported_verdict"]
    channels = [item["channel"] for item in proposition["contributions"]]
    return {
        "passed": actual_verdict == expected_verdict,
        "expected_reported_verdict": expected_verdict,
        "reported_verdict": actual_verdict,
        "channels": channels,
        "result_set_id": payload["result_set_id"],
    }


def control_measurement_tamper(case: dict[str, Any]) -> bool:
    context = build_context(case)
    receipt = measure_strict_comparison(context, "p1")
    tampered = replace(
        receipt,
        raw_measurement_json=receipt.raw_measurement_json.replace("MORE_THAN", "LESS_THAN"),
    )
    try:
        complete_and_warrant(context, tampered, "p1")
    except AuthorityRefusal:
        return True
    return False


def control_proposition_substitution(case: dict[str, Any]) -> bool:
    context = build_context(case)
    receipt = measure_strict_comparison(context, "p1")
    authority = complete_and_warrant(context, receipt, "p1")
    original = context.proposition.field_map()
    original["comparison_direction"] = (
        "LESS_THAN" if original["comparison_direction"] == "MORE_THAN" else "MORE_THAN"
    )
    substituted = AuditContext(
        context.original_claim,
        TypedProposition.create(
            context.proposition.proposition_id,
            context.proposition.semantic_family,
            original,
            text_sha256=context.proposition.text_sha256,
        ),
        context.evidence_world,
    )
    try:
        derive_relation(substituted, authority)
    except ValueError:
        return True
    return False


def control_cross_world(case: dict[str, Any]) -> bool:
    one = build_context(case, bundle_suffix="-one")
    two = build_context(case, bundle_suffix="-two")
    r1 = audit(one).traces[0].relation
    r2 = audit(two).traces[0].relation
    if r1 is None or r2 is None:
        return False
    traces = (
        PassageTrace("p1", None, None, r1, None, None),
        PassageTrace("p1", None, None, r2, None, None),
    )
    try:
        compose(one, traces)
    except ValueError:
        return True
    return False


def control_stale_passage_hash(case: dict[str, Any]) -> bool:
    text = str(case["passages"][0])
    claim = str(case["original_claim"])
    packet: dict[str, Any] = {
        "original_claim": claim,
        "proposition": {
            "proposition_id": f"prop-{case['case_id']}",
            "text_sha256": sha256_hex(claim),
            "semantic_family": str(case["semantic_family"]),
            "fields": case["fields"],
        },
        "evidence_world": {
            "contract_b_version": "1.2.0",
            "bundle_id": "stale-hash-control",
            "bundle_hash": tagged("stale-hash-control"),
            "aperture_observation": {
                "search_scope": {"control": "stale-hash"},
                "outcome": {"state": "unknown", "value": None},
                "limitations": [],
            },
            "admitted_passages": [
                {
                    "passage_id": "p1",
                    "source_id": "source-stale",
                    "text": text + " changed",
                    "text_sha256": tagged_sha256(text.encode("utf-8")),
                    "source_sha256": tagged("source-stale"),
                }
            ],
        },
    }
    try:
        context_from_packet(packet)
    except ValueError:
        return True
    return False


def control_no_scalar_terminal_surface() -> dict[str, Any]:
    prohibited = {"score", "confidence", "support_score", "refutation_score", "threshold"}
    surfaces = {
        "AuthorityReceipt": {field.name for field in dataclass_fields(AuthorityReceipt)},
        "BoundRelation": {field.name for field in dataclass_fields(BoundRelation)},
        "AuditResult": {field.name for field in dataclass_fields(AuditResult)},
    }
    hits = {name: sorted(names & prohibited) for name, names in surfaces.items() if names & prohibited}
    return {"passed": not hits, "prohibited_hits": hits}


def main() -> int:
    cohort = load_json(COHORT_PATH)
    gold = load_json(GOLD_PATH)
    freeze = load_json(FREEZE_PATH)
    semantic_sha = str(freeze["candidate"]["commit_sha"])
    source_guard = verify_candidate_source(freeze)
    expected = expected_case_map(gold)

    case_results: list[dict[str, Any]] = []
    contexts: dict[str, AuditContext] = {}
    results: dict[str, AuditResult] = {}
    projections: dict[str, dict[str, Any]] = {}

    for raw_case in cohort["cases"]:
        case = dict(raw_case)
        case_id = str(case["case_id"])
        context = build_context(case)
        result = audit(context)
        projection = projection_check(context, result, semantic_sha)
        classification = classify_case(expected[case_id], result)
        contexts[case_id] = context
        results[case_id] = result
        projections[case_id] = projection
        case_results.append(
            {
                "case_id": case_id,
                "expected_conclusion": expected[case_id]["expected_conclusion"],
                "observed_conclusion": result.conclusion.value,
                "expected_failure_code": expected[case_id].get("expected_failure_code"),
                "observed_failure_code": (
                    None if result.failure_code is None else result.failure_code.value
                ),
                "classification": classification,
                "trace_failure_codes": [
                    None if trace.failure_code is None else trace.failure_code.value
                    for trace in result.traces
                ],
                "trace_relations": [
                    None
                    if trace.relation is None
                    else trace.relation.categorical_relation.value
                    for trace in result.traces
                ],
                "contract_c_projection": projection,
            }
        )

    case_by_id = {str(case["case_id"]): dict(case) for case in cohort["cases"]}
    adversarial = {
        "measurement_tamper_rejected": control_measurement_tamper(
            case_by_id["Q01_STRICT_SUPPORT"]
        ),
        "same_id_proposition_substitution_rejected": control_proposition_substitution(
            case_by_id["Q01_STRICT_SUPPORT"]
        ),
        "cross_evidence_world_composition_rejected": control_cross_world(
            case_by_id["Q01_STRICT_SUPPORT"]
        ),
        "stale_passage_hash_rejected": control_stale_passage_hash(
            case_by_id["Q01_STRICT_SUPPORT"]
        ),
        "scalar_terminal_surface_absent": control_no_scalar_terminal_surface(),
        "unsupported_permission_no_fallback": (
            results["Q14_PERMISSION_UNSUPPORTED"].conclusion is Conclusion.NOT_CHECKABLE
            and results["Q14_PERMISSION_UNSUPPORTED"].failure_code is not None
            and results["Q14_PERMISSION_UNSUPPORTED"].failure_code.value
            == "UNSUPPORTED_SEMANTIC_FAMILY"
        ),
        "unsupported_assertion_scope_no_fallback": (
            results["Q15_ASSERTION_SCOPE_UNSUPPORTED"].conclusion is Conclusion.NOT_CHECKABLE
            and results["Q15_ASSERTION_SCOPE_UNSUPPORTED"].failure_code is not None
            and results["Q15_ASSERTION_SCOPE_UNSUPPORTED"].failure_code.value
            == "UNSUPPORTED_SEMANTIC_FAMILY"
        ),
        "mixed_relations_no_winner": (
            results["Q06_STRICT_MIXED"].conclusion is Conclusion.NOT_CHECKABLE
            and projections["Q06_STRICT_MIXED"]["reported_verdict"] == "not_checkable"
            and set(projections["Q06_STRICT_MIXED"]["channels"])
            == {"support", "counterevidence"}
        ),
        "non_deciding_attribution_preserved": (
            results["Q10_STRICT_SUPPORT_PLUS_IRRELEVANT"].conclusion is Conclusion.SUPPORTED
            and set(projections["Q10_STRICT_SUPPORT_PLUS_IRRELEVANT"]["channels"])
            == {"support", "non_deciding"}
        ),
        "all_contract_c_projections_non_strengthening": all(
            projection["passed"] for projection in projections.values()
        ),
    }

    unsafe_cases = [row["case_id"] for row in case_results if row["classification"] == "unsafe"]
    safe_misses = [
        row["case_id"] for row in case_results if row["classification"] == "safe_miss"
    ]
    localization_mismatches = [
        row["case_id"]
        for row in case_results
        if row["classification"] == "localization_mismatch"
    ]
    other_mismatches = [
        row["case_id"] for row in case_results if row["classification"] == "mismatch"
    ]
    expected_decisions = [
        case_id for case_id, row in expected.items() if bool(row.get("decision_expected"))
    ]
    exact_decisions = [
        row["case_id"]
        for row in case_results
        if row["case_id"] in expected_decisions and row["classification"] == "exact"
    ]

    adversarial_pass = all(
        value["passed"] if isinstance(value, dict) else bool(value)
        for value in adversarial.values()
    )
    usefulness_gate = len(exact_decisions) >= 7
    hard_pass = (
        source_guard["passed"]
        and not unsafe_cases
        and not other_mismatches
        and adversarial_pass
        and usefulness_gate
    )
    disposition = "CAL_V1_BOUNDED_QUALIFIED" if hard_pass else "CAL_V1_QUALIFICATION_FAILED"

    receipt = {
        "schema": "cal-v1-fresh-qualification-receipt-v1",
        "disposition": disposition,
        "candidate_commit": freeze["candidate"]["commit_sha"],
        "candidate_tree": freeze["candidate"]["tree_sha"],
        "qualification_execution_sha": os.environ.get("GITHUB_SHA"),
        "cohort": {
            "id": cohort["cohort_id"],
            "sha256": sha256_file(COHORT_PATH),
            "case_count": len(case_results),
        },
        "gold": {
            "sha256": sha256_file(GOLD_PATH),
            "status": gold["adjudication_status"],
        },
        "freeze_receipt_sha256": sha256_file(FREEZE_PATH),
        "candidate_source_guard": source_guard,
        "summary": {
            "exact_cases": sum(row["classification"] == "exact" for row in case_results),
            "unsafe_cases": unsafe_cases,
            "safe_misses": safe_misses,
            "localization_mismatches": localization_mismatches,
            "other_mismatches": other_mismatches,
            "expected_decision_cases": len(expected_decisions),
            "exact_decision_cases": len(exact_decisions),
            "minimum_exact_decision_cases": 7,
        },
        "adversarial_controls": adversarial,
        "case_results": case_results,
        "nonclaims": [
            "This qualification is bounded to the frozen strict-comparison and narrow direct-event-order V1 profile.",
            "It does not establish generic NLU/NLI, retrieval completeness, source truthworthiness, operational authorization, or Contract C production authority.",
            "Permission/exception and assertion/scope remain non-deciding in this candidate.",
            "The research Contract C non_deciding sentinel remains non-canonical."
        ],
    }
    OUTPUT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt["summary"], indent=2, sort_keys=True))
    print(disposition)
    return 0 if hard_pass else 1


if __name__ == "__main__":
    sys.exit(main())
