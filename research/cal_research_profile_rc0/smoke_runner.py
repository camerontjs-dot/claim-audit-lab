"""Post-profile-freeze naturalistic smoke executor for CAL Research Profile RC0.

This is execution/scoring apparatus, not the frozen semantic runtime. It refuses
candidate execution until SMOKE-EXECUTION-MANIFEST.json binds the exact frozen
profile, cohort, gold, runtime, and this harness.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Callable

import yaml

from runtime import (
    BoundProposition,
    EvidenceInput,
    canonical_json_bytes,
    claim_text_sha256,
    execute_rc0_case,
    sha256_hex,
)

HERE = Path(__file__).resolve().parent
PROFILE_PATH = HERE / "PROFILE-MANIFEST.json"
COHORT_PATH = HERE / "SMOKE-COHORT.json"
GOLD_PATH = HERE / "SMOKE-GOLD.json"
EXECUTION_MANIFEST_PATH = HERE / "SMOKE-EXECUTION-MANIFEST.json"
ATOM_KEY = b"rc0-naturalistic-atom-key-32-bytes!"
PROP_KEY = b"rc0-naturalistic-prop-key-32-bytes!"
ATOM_KEY_ID = "rc0-naturalistic-atom-key"
PROP_KEY_ID = "rc0-naturalistic-prop-key"
GENERATED_AT = "2026-09-07T03:20:00Z"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object in {path}")
    return value


def git_blob(path: Path) -> str:
    proc = subprocess.run(["git", "hash-object", str(path)], check=True, capture_output=True, text=True)
    return proc.stdout.strip()


def require_execution_binding() -> dict[str, Any] | None:
    if not EXECUTION_MANIFEST_PATH.exists():
        print("SMOKE_NOT_AUTHORIZED: execution manifest not frozen yet")
        return None
    manifest = load_json(EXECUTION_MANIFEST_PATH)
    bindings = manifest.get("bindings")
    if not isinstance(bindings, dict):
        raise RuntimeError("execution manifest bindings missing")
    checks = {
        "profile_manifest_blob": git_blob(PROFILE_PATH),
        "cohort_blob": git_blob(COHORT_PATH),
        "gold_blob": git_blob(GOLD_PATH),
        "runtime_blob": git_blob(HERE / "runtime.py"),
        "smoke_runner_blob": git_blob(Path(__file__).resolve()),
    }
    for key, actual in checks.items():
        expected = bindings.get(key)
        if expected != actual:
            raise RuntimeError(f"execution binding mismatch for {key}: expected {expected}, got {actual}")
    return manifest


def load_measure(root: Path) -> Callable[[str], dict[str, Any]]:
    path = root / "research" / "comparative_relation_measurement_rc7fb1" / "comparator.py"
    spec = importlib.util.spec_from_file_location("rc7fb1_smoke_exact", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load RC7F-B1 from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.measure


def load_rc8j(root: Path) -> Callable[[dict[str, Any]], dict[str, Any]]:
    sys.path.insert(0, str(root))
    try:
        from research.semantic_authority_machinery_rc8.authority_contract_rc8j import assess_authority
    finally:
        sys.path.pop(0)
    return assess_authority


def dump_yaml(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=True, allow_unicode=True), encoding="utf-8")


def passage_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_contract_b_bundle(cohort: dict[str, Any], gold: dict[str, Any], out_root: Path) -> tuple[Path, dict[str, str], dict[str, Any]]:
    bundle = out_root / "contract-b-bundle"
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)
    cohort_raw = canonical_json_bytes(cohort, trailing_newline=True)
    gold_raw = canonical_json_bytes(gold, trailing_newline=True)
    bundle_hash = "sha256:" + sha256_hex(cohort_raw)
    config_hash = "sha256:" + sha256_hex(b"cal-rc0-smoke-audit-config-v1")
    bundle_id = "cal-rc0-naturalistic-smoke-bundle-v1"
    cases = cohort["cases"]

    dump_yaml(bundle / "audit_config.yaml", {
        "config_id": "cal-rc0-smoke-audit-config-v1",
        "config_hash": config_hash,
        "schema_version": "1.2.0",
        "frozen_at_utc": GENERATED_AT,
        "scoring": {"support_threshold_sourced": 0.0, "support_threshold_partial": 0.0, "counterevidence_weight": 0.0},
        "rule_policies": {
            "require_passage_level_match": True,
            "flag_unsupported_threshold": 0.0,
            "false_caution_detection": False,
            "false_caution_threshold": 0.0,
            "overstated_detection": False,
            "needs_source_detection": False,
        },
        "known_limitations": [
            "Contract-B scalar/scoring fields are apparatus-only and are not consumed by RC0.",
            "Public source URLs are provenance pointers; bundle integrity binds admitted passage bytes, not full webpage snapshots."
        ],
        "change_log": [],
    })

    transformations: list[dict[str, Any]] = []
    passage_index: dict[str, dict[str, str]] = {}
    proposition_index: dict[str, str] = {}
    total_passages = 0
    for case in cases:
        claim = case["claim"]
        claim_id = claim["claim_id"]
        evidence_entries: list[dict[str, Any]] = []
        for ev in case["evidence"]:
            text = ev["text"]
            phash = passage_hash(text)
            pid = ev["passage_id"]
            sid = ev["source_id"]
            evidence_entries.append({
                "passage_id": pid,
                "source_id": sid,
                "passage_text": text,
                "section": ev["source_locator"],
                "char_start": 0,
                "char_end": len(text),
                "source_trust_level": "secondary",
                "passage_hash": phash,
            })
            dump_yaml(bundle / "evidence" / sid / "passages" / f"{pid}.yaml", {
                "passage_id": pid,
                "source_id": sid,
                "bundle_id": bundle_id,
                "schema_version": "1.2.0",
                "passage_text": text,
                "section": ev["source_locator"],
                "paragraph_index": 0,
                "char_start": 0,
                "char_end": len(text),
                "passage_hash": phash,
                "cited_by_claims": [claim_id],
                "extraction_method": "scaffold_cited",
                "provenance": {
                    "source_url": ev["source_url"],
                    "source_access_date_utc": "2026-09-06",
                    "source_content_hash": phash,
                    "scaffold_run_id": "cal-rc0-naturalistic-smoke-source-run-v1",
                    "evidence_builder_version": "cal-rc0-research-adapter-v1",
                    "bundle_created_at_utc": GENERATED_AT,
                },
            })
            passage_index[pid] = {"source_id": sid, "passage_sha256": phash}
            transformations.append({
                "type": ev["text_mode"],
                "description": ev["transformation_record"],
                "claims_affected": [claim_id],
            })
            total_passages += 1
        dump_yaml(bundle / "claims" / f"{claim_id}.yaml", {
            "claim_id": claim_id,
            "bundle_id": bundle_id,
            "schema_version": "1.2.0",
            "claim_text": claim["text"],
            "claim_type": "extracted_claim",
            "workflow_condition": "baseline",
            "task_id": "cal-research-profile-rc0-naturalistic-smoke",
            "scaffold_support_status": "uncertain",
            "scaffold_claim_strength": 0.0,
            "scaffold_extraction_fidelity": 1.0,
            "scaffold_counterevidence_found": False,
            "scaffold_downgraded": False,
            "evidence_passages": evidence_entries,
            "counterevidence_passages": [],
            "audit": {},
        })
        proposition_index[claim_id] = claim_text_sha256(claim["text"])

    dump_yaml(bundle / "bundle_manifest.yaml", {
        "bundle_id": bundle_id,
        "schema_version": "1.2.0",
        "generated_at_utc": GENERATED_AT,
        "source_run_id": "cal-rc0-naturalistic-smoke-source-run-v1",
        "source_contract_version": "1.2.0",
        "source_corpus_hash": "sha256:" + sha256_hex(cohort_raw),
        "evidence_builder": {
            "version": "cal-rc0-research-adapter-v1",
            "config_hash": "sha256:" + sha256_hex(b"cal-rc0-research-adapter-v1"),
            "operator": "cal-pipeline-supervisor",
            "build_timestamp_utc": GENERATED_AT,
        },
        "bundle": {
            "total_claims_in_source": len(cases),
            "claims_included": len(cases),
            "claims_excluded": 0,
            "exclusion_rationale": "none",
            "total_evidence_passages": total_passages,
            "bundle_hash": bundle_hash,
        },
        "transformations": transformations,
        "quality_gates": {
            "every_claim_has_at_least_one_passage": True,
            "every_passage_links_to_source_profile": True,
            "source_hashes_verified": False,
            "bundle_integrity_verified": True,
        },
        "audit_config_version": "cal-rc0-smoke-audit-config-v1",
        "audit_config_hash": config_hash,
        "validation_set_version": gold["gold_id"],
        "validation_set_hash": "sha256:" + sha256_hex(gold_raw),
        "reviewer_sign_off": {"required": False, "signed_by": None, "signature_timestamp_utc": None, "signature_notes": None},
    })
    (bundle / "CONTRACT_VERSION").write_text("1.2.0\n", encoding="utf-8")
    files = sorted(p for p in bundle.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    sums = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(bundle).as_posix()}" for path in files]
    (bundle / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    binding = {"contract_version": "1.2.0", "bundle_id": bundle_id, "bundle_hash": bundle_hash}
    index = {
        "contract_version": "1.2.0",
        "bundle_id": bundle_id,
        "bundle_hash": bundle_hash,
        "propositions": proposition_index,
        "passages": passage_index,
    }
    return bundle, binding, index


def validate_contract_b(bundle: Path, apparatus_b: Path) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(apparatus_b)
    proc = subprocess.run(
        [sys.executable, "-m", "validators.verify_contract_integrity", str(bundle), "--against-pin", "1.2.0"],
        cwd=apparatus_b, env=env, capture_output=True, text=True,
    )
    return {"status": "PASS" if proc.returncode == 0 else "FAIL", "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def validate_contract_c(raw_path: Path, index_path: Path, apparatus_c: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(apparatus_c / "validators" / "contract_c.py"), str(raw_path), "--contract-b-index", str(index_path)],
        capture_output=True, text=True,
    )
    return {"status": "PASS" if proc.returncode == 0 else "FAIL", "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def measurement_status(stage: dict[str, Any]) -> str:
    measurement = stage.get("measurement")
    return str(measurement.get("status")) if isinstance(measurement, dict) else "UNKNOWN"


def score_case(gold: dict[str, Any], candidate: dict[str, Any], c_validation: dict[str, Any]) -> tuple[str, bool, str | None]:
    stages = candidate.get("stages") or []
    stage = stages[0] if stages else {}
    relation_obj = stage.get("categorical_relation") if isinstance(stage, dict) else None
    actual_relation = relation_obj.get("relation") if isinstance(relation_obj, dict) else "UNRESOLVED"
    internal = candidate["internal_cal_conclusion"]
    actual_disposition = internal.get("disposition")
    actual_verdict = internal.get("verdict")
    expected_relation = gold["expected_relation"]
    allowed = bool(gold["proposition_decision_allowed"])

    if c_validation["status"] != "PASS":
        return "CONTRACT_C_PROJECTION_FAILURE", True, "Contract C exact validator failed"
    c_projection = candidate["contract_c_projection"]
    if actual_disposition == "abstained" and c_projection.get("contract_c_reported_verdict") != "not_checkable":
        return "CONTRACT_C_PROJECTION_FAILURE", True, "Contract C strengthened internal abstention"
    if actual_disposition == "decided" and c_projection.get("contract_c_reported_verdict") != actual_verdict:
        return "CONTRACT_C_PROJECTION_FAILURE", True, "Contract C changed decided verdict"
    if not allowed and actual_relation == "SUPPORTS":
        return "UNSAFE_SUPPORT", True, "RC0 supported a case whose frozen gold forbids proposition decision"
    if not allowed and actual_relation == "REFUTES":
        return "UNSAFE_REFUTATION", True, "RC0 refuted a case whose frozen gold forbids proposition decision"
    if expected_relation == "SUPPORTS" and actual_relation == "REFUTES":
        return "UNSAFE_REFUTATION", True, "opposite deciding relation"
    if expected_relation == "REFUTES" and actual_relation == "SUPPORTS":
        return "UNSAFE_SUPPORT", True, "opposite deciding relation"

    exact = (
        actual_relation == expected_relation
        and actual_disposition == gold["expected_internal_disposition"]
        and actual_verdict == gold["expected_internal_verdict"]
        and measurement_status(stage) == gold["expected_measurement_status"]
    )
    if exact:
        if expected_relation == "UNRESOLVED":
            return "SAFE_ABSTENTION", False, None
        if expected_relation == "IRRELEVANT":
            return "PASS_IRRELEVANT", False, None
        return "PASS_EXACT", False, None
    failure_category = stage.get("failure_category") if isinstance(stage, dict) else None
    if actual_disposition == "abstained" and failure_category in {"MEASUREMENT_MISS_SAFE", "ATOM_INCOMPLETE", "WARRANT_UNRESOLVED", "SAFE_ABSTENTION"}:
        return str(failure_category), False, "safe miss versus frozen gold"
    if actual_relation != expected_relation:
        return "RELATION_WRONG", False, f"expected {expected_relation}, got {actual_relation}"
    return "APPARATUS_FAILURE", False, "stage/result mismatch versus frozen gold"


def execute(args: argparse.Namespace) -> dict[str, Any]:
    execution_manifest = require_execution_binding()
    if execution_manifest is None:
        return {"status": "SMOKE_NOT_AUTHORIZED"}
    cohort = load_json(COHORT_PATH)
    gold_doc = load_json(GOLD_PATH)
    gold_by_id = {item["case_id"]: item for item in gold_doc["cases"]}
    measure = load_measure(args.rc7fb1_root.resolve())
    rc8j = load_rc8j(args.rc8j_root.resolve())
    out_path = args.out.resolve()
    out_root = out_path.parent
    out_root.mkdir(parents=True, exist_ok=True)

    bundle, b_binding, c_index = build_contract_b_bundle(cohort, gold_doc, out_root)
    b_validation_observed = validate_contract_b(bundle, args.apparatus_b.resolve())
    if b_validation_observed["status"] != "PASS":
        result = {
            "status": "APPARATUS_FAILURE",
            "hard_stop": True,
            "reason": "exact Contract B 1.2.0 validation failed before candidate execution",
            "contract_b_validation": b_validation_observed,
            "cases": [],
        }
        out_path.write_bytes(canonical_json_bytes(result, trailing_newline=True))
        return result

    b_receipt = {"contract_version": "1.2.0", "authority_commit": "c314e53bd91c0736aa4370a364673b069aceb43e", "status": "PASS"}
    index_path = out_root / "CONTRACT-B-INDEX.json"
    index_path.write_bytes(canonical_json_bytes(c_index, trailing_newline=True))
    results: list[dict[str, Any]] = []
    unsafe_results: list[dict[str, Any]] = []
    exact_count = 0
    safe_abstention_count = 0

    for cohort_case in cohort["cases"]:
        case_id = cohort_case["case_id"]
        gold = gold_by_id[case_id]
        claim = cohort_case["claim"]
        proposition = BoundProposition(
            claim_id=claim["claim_id"], claim_text=claim["text"], family=claim["family"],
            lhs_entity=claim["lhs_entity"], rhs_entity=claim["rhs_entity"], comparison_direction=claim["comparison_direction"],
        )
        admitted = [EvidenceInput(
            source_id=ev["source_id"], bundle_id=b_binding["bundle_id"], passage_id=ev["passage_id"],
            passage_text=ev["text"], passage_sha256=passage_hash(ev["text"]), semantic_family=ev["semantic_family"],
            metadata={"source_url": ev["source_url"], "text_mode": ev["text_mode"]},
        ) for ev in cohort_case["evidence"]]
        candidate = execute_rc0_case(
            proposition=proposition, admitted_evidence=admitted, contract_b_validation=b_receipt,
            contract_b_binding=b_binding, measure_fn=measure, authority_evaluator=rc8j,
            atom_key=ATOM_KEY, atom_key_id=ATOM_KEY_ID, proposition_key=PROP_KEY, proposition_key_id=PROP_KEY_ID,
            semantic_implementation_sha=args.implementation_sha,
            baseline_diagnostic={
                "status": "NOT_RUN", "distribution": "0.5.0", "engine": "v1-retrieve-entail",
                "rules": "cal-rules-v1.13.0", "reason": "optional released-v1 inference stack not needed for bounded causal test",
                "causal_influence": False,
            },
        )
        c_dir = out_root / "contract-c"
        c_dir.mkdir(exist_ok=True)
        c_path = c_dir / f"{case_id}.json"
        c_path.write_text(candidate["contract_c_bytes"], encoding="utf-8")
        c_validation = validate_contract_c(c_path, index_path, args.apparatus_c.resolve())
        category, hard_stop, note = score_case(gold, candidate, c_validation)
        exact_match = category in {"PASS_EXACT", "PASS_IRRELEVANT", "SAFE_ABSTENTION"}
        if exact_match:
            exact_count += 1
        if category == "SAFE_ABSTENTION":
            safe_abstention_count += 1
        row = {
            "case_id": case_id,
            "gold": deepcopy(gold),
            "candidate": candidate,
            "contract_c_validation": c_validation,
            "failure_category": category,
            "exact_match": exact_match,
            "hard_stop": hard_stop,
            "note": note,
        }
        results.append(row)
        if hard_stop:
            unsafe_results.append(row)
            break

    executed_ids = {row["case_id"] for row in results}
    not_run = [item["case_id"] for item in cohort["cases"] if item["case_id"] not in executed_ids]
    if unsafe_results:
        disposition = "RC0_VERTICAL_FALSIFIED"
    elif len(results) != cohort["case_count"]:
        disposition = "RC0_VERTICAL_INCONCLUSIVE"
    elif exact_count == cohort["case_count"]:
        disposition = "RC0_VERTICAL_SUPPORTED_WITH_BOUNDS"
    else:
        disposition = "RC0_VERTICAL_INCONCLUSIVE"

    result = {
        "schema": "cal-research-profile-rc0-smoke-results-v1",
        "execution_manifest_id": execution_manifest["execution_id"],
        "profile_id": "cal-research-profile-rc0-strict-comparison",
        "cohort_id": cohort["cohort_id"],
        "gold_id": gold_doc["gold_id"],
        "contract_b_validation": b_validation_observed,
        "contract_b_binding": b_binding,
        "case_count": cohort["case_count"],
        "executed_count": len(results),
        "exact_match_count": exact_count,
        "safe_abstention_count": safe_abstention_count,
        "unsafe_count": len(unsafe_results),
        "not_run_case_ids": not_run,
        "cases": results,
        "unsafe_results": unsafe_results,
        "baseline_only": {
            "status": "NOT_RUN", "distribution": "0.5.0", "engine": "v1-retrieve-entail",
            "rules": "cal-rules-v1.13.0", "causal_influence": False,
        },
        "gold_adjudication_status": gold_doc["adjudication_status"],
        "terminal_disposition": disposition,
    }
    out_path.write_bytes(canonical_json_bytes(result, trailing_newline=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rc7fb1-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--apparatus-b", type=Path, required=True)
    parser.add_argument("--apparatus-c", type=Path, required=True)
    parser.add_argument("--implementation-sha", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("status") == "SMOKE_NOT_AUTHORIZED":
        return 0
    if result.get("status") == "APPARATUS_FAILURE":
        return 2
    return 2 if result.get("unsafe_count", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
