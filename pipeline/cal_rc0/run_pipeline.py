"""Runnable CAL Pipeline RC0 integration vertical.

This module assembles already-supported research boundaries without changing
Contract A, Contract B, Contract C, the frozen RC7F-B1 measurement operator, or
the frozen RC8J authority evaluator.

Data flow:
Contract A 2.0 declaration
-> Evidence Bundler exact-child retrieval
-> retained candidates
-> explicit admission
-> exact Contract B 1.2 validation
-> admitted strict-comparison evidence
-> RC7F-B1 measurement
-> RC0A exact lexical span anchoring
-> RC8J warrant
-> authenticated atom/proposition bindings
-> scoreless categorical relation/composition
-> Contract C 1.0 projection and exact validation

The cross-child root proposition is intentionally not composed. No rule for
Contract A all_of semantics at the CAL conclusion layer has been established.
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

EB_HEAD = "50270b9bfcf6b5112c6ec88c02c7cdd7215e0ff4"
EB_RESEARCH_IMPLEMENTATION = "15e550fb18393835b6dc9a9f2cf7d78050ef9e5f"
EB_FROZEN_PROFILE_BLOB = "b7fe64d019ae4304294a51e8e658d43d412955d0"
RC0_PARENT_HEAD = "8c52a00b93c7c33c159a484c47944faf9d97f7f1"
RC0_RUNTIME_BLOB = "b36dacf39d158601368b89df8fa66431ce1b4a07"
RC0A_HEAD = "9baa981d9e5209c08911b992effbce5c59604884"
RC0A_SPAN_BLOB = "7dd0b1d0077682d121aaa386067531cca3b742d8"
RC7FB1_HEAD = "0ecdedc5cea970485a635508255f3670ab231c33"
RC7FB1_BLOB = "33820f55e2a87c4de6336fca6b5e5b93a2bccde3"
RC8J_HEAD = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"
CONTRACT_B_AUTHORITY = "c314e53bd91c0736aa4370a364673b069aceb43e"
CONTRACT_C_AUTHORITY = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
TARGET_SCHEMA = "cal-pipeline-rc0-targets-v1"
PIPELINE_RECEIPT_SCHEMA = "cal-pipeline-rc0-receipt-v1"

_TEST_ATOM_KEY = b"cal-pipeline-rc0-test-atom-key-0001"
_TEST_PROP_KEY = b"cal-pipeline-rc0-test-prop-key-0001"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML object: {path}")
    return value


def git_head(root: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def git_blob(root: Path, relative: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), "hash-object", relative],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def require_identity(root: Path, *, head: str, blobs: dict[str, str]) -> None:
    observed_head = git_head(root)
    if observed_head != head:
        raise RuntimeError(f"dependency head mismatch for {root}: {observed_head} != {head}")
    for relative, expected in blobs.items():
        observed = git_blob(root, relative)
        if observed != expected:
            raise RuntimeError(
                f"dependency blob mismatch for {root}/{relative}: {observed} != {expected}"
            )


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_measure(root: Path) -> Callable[[str], dict[str, Any]]:
    module = load_module(
        "cal_pipeline_rc7fb1",
        root / "research" / "comparative_relation_measurement_rc7fb1" / "comparator.py",
    )
    return module.measure


def load_rc8j(root: Path) -> Callable[[dict[str, Any]], dict[str, Any]]:
    sys.path.insert(0, str(root))
    try:
        from research.semantic_authority_machinery_rc8.authority_contract_rc8j import (
            assess_authority,
        )
    finally:
        sys.path.pop(0)
    return assess_authority


def validate_contract_b(bundle: Path, apparatus_b: Path) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(apparatus_b)
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "validators.verify_contract_integrity",
            str(bundle),
            "--against-pin",
            "1.2.0",
        ],
        cwd=apparatus_b,
        env=env,
        capture_output=True,
        text=True,
    )
    return {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def validate_contract_c(
    contract_c_path: Path, index_path: Path, apparatus_c: Path
) -> dict[str, Any]:
    proc = subprocess.run(
        [
            sys.executable,
            str(apparatus_c / "validators" / "contract_c.py"),
            str(contract_c_path),
            "--contract-b-index",
            str(index_path),
        ],
        capture_output=True,
        text=True,
    )
    return {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def build_contract_b_index(bundle: Path, claim_text_sha256: Callable[[str], str]) -> dict[str, Any]:
    manifest = load_yaml(bundle / "bundle_manifest.yaml")
    propositions: dict[str, str] = {}
    for path in sorted((bundle / "claims").glob("*.yaml")):
        row = load_yaml(path)
        propositions[str(row["claim_id"])] = claim_text_sha256(str(row["claim_text"]))

    passages: dict[str, dict[str, str]] = {}
    for path in sorted((bundle / "evidence").glob("*/passages/*.yaml")):
        row = load_yaml(path)
        passages[str(row["passage_id"])] = {
            "source_id": str(row["source_id"]),
            "passage_sha256": str(row["passage_hash"]),
        }

    return {
        "contract_version": "1.2.0",
        "bundle_id": str(manifest["bundle_id"]),
        "bundle_hash": str(manifest["bundle"]["bundle_hash"]),
        "propositions": propositions,
        "passages": passages,
    }


def claim_row(bundle: Path, proposition_id: str) -> dict[str, Any]:
    path = bundle / "claims" / f"{proposition_id}.yaml"
    if not path.exists():
        raise RuntimeError(f"Contract B claim missing for target {proposition_id}")
    return load_yaml(path)


def passage_rows(bundle: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((bundle / "evidence").glob("*/passages/*.yaml")):
        row = load_yaml(path)
        pid = str(row["passage_id"])
        if pid in rows:
            raise RuntimeError(f"duplicate Contract B passage id {pid}")
        rows[pid] = row
    return rows


def accepted_passage_ids(extension: dict[str, Any], proposition_id: str) -> list[str]:
    accepted: list[str] = []
    for link in extension.get("history", []):
        if not isinstance(link, dict) or link.get("claim_id") != proposition_id:
            continue
        nomination = link.get("nomination")
        review = link.get("review")
        if not isinstance(nomination, dict) or not isinstance(review, dict):
            raise RuntimeError(f"malformed Contract B history link for {proposition_id}")
        if nomination.get("retrieval_lane") != "declared_child":
            continue
        if review.get("decision") == "accepted":
            accepted.append(str(link["passage_id"]))
    return sorted(set(accepted))


def key_material(*, test_keys: bool) -> tuple[bytes, bytes, str, str]:
    if test_keys:
        return (
            _TEST_ATOM_KEY,
            _TEST_PROP_KEY,
            "cal-pipeline-rc0-test-atom",
            "cal-pipeline-rc0-test-proposition",
        )
    atom = os.environ.get("CAL_PIPELINE_ATOM_HMAC_KEY")
    prop = os.environ.get("CAL_PIPELINE_PROPOSITION_HMAC_KEY")
    if atom is None or prop is None:
        raise RuntimeError(
            "normal execution requires CAL_PIPELINE_ATOM_HMAC_KEY and "
            "CAL_PIPELINE_PROPOSITION_HMAC_KEY; use --test-keys only for bounded tests"
        )
    atom_bytes = atom.encode("utf-8")
    prop_bytes = prop.encode("utf-8")
    if len(atom_bytes) < 32 or len(prop_bytes) < 32:
        raise RuntimeError("integration HMAC keys must each be at least 32 UTF-8 bytes")
    return atom_bytes, prop_bytes, "cal-pipeline-atom-env-v1", "cal-pipeline-prop-env-v1"


def target_map(targets: dict[str, Any], case_id: str) -> dict[str, dict[str, Any]]:
    if targets.get("schema") != TARGET_SCHEMA:
        raise ValueError("CAL target schema mismatch")
    if targets.get("case_id") != case_id:
        raise ValueError("CAL target case_id mismatch")
    rows = targets.get("targets")
    if not isinstance(rows, list):
        raise ValueError("CAL target rows missing")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("CAL target row must be an object")
        pid = str(row.get("proposition_id") or "")
        if not pid or pid in result:
            raise ValueError(f"invalid or duplicate CAL target proposition_id: {pid!r}")
        if set(row) != {
            "proposition_id",
            "family",
            "lhs_entity",
            "rhs_entity",
            "comparison_direction",
        }:
            raise ValueError(f"unexpected CAL target shape for {pid}")
        result[pid] = row
    return result


def execute(args: argparse.Namespace) -> dict[str, Any]:
    cal_root = args.cal_root.resolve()
    eb_root = args.evidence_bundler_root.resolve()
    rc7_root = args.rc7fb1_root.resolve()
    rc8_root = args.rc8j_root.resolve()
    apparatus_b = args.apparatus_b.resolve()
    apparatus_c = args.apparatus_c.resolve()

    require_identity(
        cal_root,
        head=args.cal_head,
        blobs={
            "research/cal_research_profile_rc0/runtime.py": RC0_RUNTIME_BLOB,
            "research/cal_research_profile_rc0a_span_anchoring/span_anchor.py": RC0A_SPAN_BLOB,
        },
    )
    require_identity(
        eb_root,
        head=EB_HEAD,
        blobs={"research/cal_rc0_contract_b_handoff/RESEARCH_EB_PROFILE.json": EB_FROZEN_PROFILE_BLOB},
    )
    require_identity(
        rc7_root,
        head=RC7FB1_HEAD,
        blobs={"research/comparative_relation_measurement_rc7fb1/comparator.py": RC7FB1_BLOB},
    )
    require_identity(
        rc8_root,
        head=RC8J_HEAD,
        blobs={"research/semantic_authority_machinery_rc8/authority_contract_rc8j.py": RC8J_BLOB},
    )
    if git_head(apparatus_b) != CONTRACT_B_AUTHORITY:
        raise RuntimeError("Contract B authority checkout mismatch")
    if git_head(apparatus_c) != CONTRACT_C_AUTHORITY:
        raise RuntimeError("Contract C authority checkout mismatch")

    runtime = load_module(
        "cal_pipeline_rc0_runtime",
        cal_root / "research" / "cal_research_profile_rc0" / "runtime.py",
    )
    span = load_module(
        "cal_pipeline_rc0a_span",
        cal_root
        / "research"
        / "cal_research_profile_rc0a_span_anchoring"
        / "span_anchor.py",
    )
    runtime._unique_casefold_span = span.unique_lexical_span
    if runtime._unique_casefold_span(
        "Women trailed Men by 11 percentage points.", "Men"
    ) != (14, 17):
        raise RuntimeError("RC0A lexical span integration control failed")

    measure_fn = load_measure(rc7_root)
    authority_evaluator = load_rc8j(rc8_root)

    cohort = load_json(args.cohort)
    admission = load_json(args.admission)
    targets_doc = load_json(args.targets)
    profile = load_json(args.eb_profile)
    if profile.get("source_evidence", {}).get("frozen_profile_blob") != EB_FROZEN_PROFILE_BLOB:
        raise RuntimeError("integration EB profile does not cite the frozen supported profile")
    retrieval = profile.get("retrieval")
    expected_retrieval = {
        "context_policy": {
            "mode": "full_fixture_passage",
            "token_limit": None,
            "truncation": False,
        },
        "engine": "research_okapi_bm25_v1",
        "engine_parameters": {"b": 0.75, "k1": 1.5, "tokenizer": "lowercase_word"},
        "parent_child_flattening": False,
        "per_query_candidate_depth": 5,
        "query_strategy": "one_query_per_exact_declared_child",
        "reranker": {"enabled": False, "identity": None},
        "retained_k": 3,
        "retrieval_lane": "declared_child",
        "retrieval_model_identity": "none_learned_research_qualification_retriever",
        "root_child_union_default": False,
        "root_diagnostic_enabled": False,
        "root_diagnostic_lane": "diagnostic_root_rescue",
    }
    if retrieval != expected_retrieval:
        raise RuntimeError("integration EB retrieval settings drifted from supported RC0 profile")

    sys.path.insert(0, str(eb_root))
    try:
        from research.cal_rc0_contract_b_handoff.build_handoff import (
            build_runtime_receipt,
        )
        from research.cal_rc0_contract_b_handoff.qualified_handoff import (
            build_all_contract_b_qualified,
        )
    finally:
        sys.path.pop(0)

    if cohort.get("schema") != "research-eb-rc0-cohort-v1":
        raise ValueError("integration cohort schema mismatch")
    cases = cohort.get("cases")
    if not isinstance(cases, list) or len(cases) != 1:
        raise ValueError("RC0 integration runner currently requires exactly one case")
    case = cases[0]
    case_id = str(case["case_id"])
    tmap = target_map(targets_doc, case_id)
    declared_ids = {
        str(child["proposition_id"])
        for child in case["contract_a"]["decomposition"]["children"]
    }
    if set(tmap) != declared_ids:
        raise ValueError("CAL targets must bind exactly the declared Contract A children")

    out = args.out_dir.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    eb_receipt = build_runtime_receipt(
        cohort=cohort,
        admission=admission,
        profile=profile,
        diagnostic_root_rescue=False,
    )
    if eb_receipt.get("diagnostic_root_rescue_enabled") is not False:
        raise RuntimeError("root diagnostic rescue unexpectedly enabled")
    if any(row.get("flattened_parent_child") is not False for row in eb_receipt["cases"]):
        raise RuntimeError("parent/child provenance was flattened")
    (out / "EVIDENCE-BUNDLER-RECEIPT.json").write_bytes(canonical_bytes(eb_receipt))

    eb_out = out / "evidence-bundler"
    b_results = build_all_contract_b_qualified(
        cohort=cohort,
        receipt=eb_receipt,
        profile=profile,
        out_dir=eb_out,
    )
    if len(b_results) != 1 or b_results[0].get("tree_validation") != "PASS":
        raise RuntimeError("Evidence Bundler did not produce one valid Contract B tree")

    bundle = eb_out / "contract_b" / case_id
    b_validation_raw = validate_contract_b(bundle, apparatus_b)
    (out / "CONTRACT-B-VALIDATION.json").write_bytes(canonical_bytes(b_validation_raw))
    if b_validation_raw["status"] != "PASS":
        raise RuntimeError("exact Contract B 1.2 validator failed")

    b_validation = {
        "contract_version": "1.2.0",
        "authority_commit": CONTRACT_B_AUTHORITY,
        "status": "PASS",
    }
    b_index = build_contract_b_index(bundle, runtime.claim_text_sha256)
    index_path = out / "CONTRACT-B-INDEX.json"
    index_path.write_bytes(canonical_bytes(b_index))

    extension_path = bundle / "extensions" / "contract-b-factual-context-v1.json"
    extension = load_json(extension_path)
    passage_by_id = passage_rows(bundle)
    atom_key, prop_key, atom_key_id, prop_key_id = key_material(test_keys=args.test_keys)

    c_dir = out / "contract-c"
    c_dir.mkdir(parents=True)
    child_results: list[dict[str, Any]] = []
    for proposition_id in sorted(tmap):
        target = tmap[proposition_id]
        b_claim = claim_row(bundle, proposition_id)
        proposition = runtime.BoundProposition(
            claim_id=proposition_id,
            claim_text=str(b_claim["claim_text"]),
            family=str(target["family"]),
            lhs_entity=str(target["lhs_entity"]).casefold(),
            rhs_entity=str(target["rhs_entity"]).casefold(),
            comparison_direction=str(target["comparison_direction"]),
        )

        accepted_ids = accepted_passage_ids(extension, proposition_id)
        admitted: list[Any] = []
        for pid in accepted_ids:
            passage = passage_by_id.get(pid)
            if passage is None:
                raise RuntimeError(f"accepted Contract B passage missing: {pid}")
            admitted.append(
                runtime.EvidenceInput(
                    source_id=str(passage["source_id"]),
                    bundle_id=str(b_index["bundle_id"]),
                    passage_id=pid,
                    passage_text=str(passage["passage_text"]),
                    passage_sha256=str(passage["passage_hash"]),
                    semantic_family=str(target["family"]),
                    metadata={
                        "admission_source": "contract-b-factual-context-v1",
                        "review_decision": "accepted",
                    },
                )
            )

        candidate = runtime.execute_rc0_case(
            proposition=proposition,
            admitted_evidence=admitted,
            contract_b_validation=b_validation,
            contract_b_binding={
                "contract_version": str(b_index["contract_version"]),
                "bundle_id": str(b_index["bundle_id"]),
                "bundle_hash": str(b_index["bundle_hash"]),
            },
            measure_fn=measure_fn,
            authority_evaluator=authority_evaluator,
            atom_key=atom_key,
            atom_key_id=atom_key_id,
            proposition_key=prop_key,
            proposition_key_id=prop_key_id,
            semantic_implementation_sha=args.semantic_implementation_sha,
            baseline_diagnostic={
                "status": "NOT_RUN",
                "reason": "released CAL v1 is outside the RC0 terminal causal path",
                "causal_influence": False,
            },
        )
        safe_name = hashlib.sha256(proposition_id.encode("utf-8")).hexdigest()[:16]
        c_path = c_dir / f"{safe_name}.json"
        c_path.write_text(candidate["contract_c_bytes"], encoding="utf-8")
        c_validation = validate_contract_c(c_path, index_path, apparatus_c)
        if c_validation["status"] != "PASS":
            raise RuntimeError(f"exact Contract C 1.0 validator failed for {proposition_id}")
        child_results.append(
            {
                "proposition_id": proposition_id,
                "claim_text_sha256": runtime.claim_text_sha256(proposition.claim_text),
                "cal_target_sha256": sha256_bytes(canonical_bytes(target)),
                "admitted_passage_ids": accepted_ids,
                "internal_cal_conclusion": deepcopy(candidate["internal_cal_conclusion"]),
                "stages": deepcopy(candidate["stages"]),
                "contract_c_projection": deepcopy(candidate["contract_c_projection"]),
                "contract_c_path": str(c_path.relative_to(out)),
                "contract_c_validation": {
                    "status": "PASS",
                    "authority_commit": CONTRACT_C_AUTHORITY,
                },
            }
        )

    root = case["contract_a"]["root_proposition"]
    receipt = {
        "schema": PIPELINE_RECEIPT_SCHEMA,
        "pipeline_status": "PASS",
        "pins": {
            "cal_integration_head": args.cal_head,
            "rc0_parent_head": RC0_PARENT_HEAD,
            "rc0_runtime_blob": RC0_RUNTIME_BLOB,
            "rc0a_head": RC0A_HEAD,
            "rc0a_span_blob": RC0A_SPAN_BLOB,
            "rc7fb1_head": RC7FB1_HEAD,
            "rc7fb1_blob": RC7FB1_BLOB,
            "rc8j_head": RC8J_HEAD,
            "rc8j_blob": RC8J_BLOB,
            "evidence_bundler_head": EB_HEAD,
            "evidence_bundler_research_implementation": EB_RESEARCH_IMPLEMENTATION,
            "contract_b_authority": CONTRACT_B_AUTHORITY,
            "contract_c_authority": CONTRACT_C_AUTHORITY,
        },
        "input": {
            "case_id": case_id,
            "contract_a_handoff_id": case["contract_a"]["handoff_id"],
            "contract_a_handoff_sha256": case["contract_a"]["handoff_sha256"],
            "cal_targets_sha256": sha256_bytes(canonical_bytes(targets_doc)),
            "eb_profile_sha256": sha256_bytes(canonical_bytes(profile)),
        },
        "evidence_bundler": {
            "profile_id": profile["profile_id"],
            "candidate_pool_count": sum(
                len(row["candidate_pool"]) for row in eb_receipt["cases"]
            ),
            "retained_count": sum(len(row["retained"]) for row in eb_receipt["cases"]),
            "admission_count": sum(len(row["admission"]) for row in eb_receipt["cases"]),
            "root_diagnostic_rescue_enabled": False,
            "parent_child_flattened": False,
        },
        "contract_b": {
            "validation": b_validation,
            "bundle_id": b_index["bundle_id"],
            "bundle_hash": b_index["bundle_hash"],
            "factual_context_extension": "extensions/contract-b-factual-context-v1.json",
        },
        "cal": {
            "semantic_family": "strict_comparison",
            "span_resolver": "rc0a_unique_exact_lexical_boundary",
            "terminal_decision_semantics": "scoreless_categorical",
            "scalar_terminal_influence": False,
            "children": child_results,
        },
        "root_composition": {
            "root_proposition_id": root["proposition_id"],
            "decomposition_operator": case["contract_a"]["decomposition"]["operator"],
            "state": "NOT_COMPOSED",
            "reason": (
                "No supported CAL RC0 rule composes child categorical conclusions into "
                "a root all_of proposition conclusion; the build refuses to invent one."
            ),
        },
        "operational_authorization": {
            "state": "NOT_EVALUATED",
            "reason": "Decision Engine and Contract E are outside this RC0 build.",
        },
        "production_promotion_authorized": False,
    }
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cal-root", type=Path, default=Path("."))
    parser.add_argument("--cal-head", required=True)
    parser.add_argument("--evidence-bundler-root", type=Path, required=True)
    parser.add_argument("--rc7fb1-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--apparatus-b", type=Path, required=True)
    parser.add_argument("--apparatus-c", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--eb-profile", type=Path, required=True)
    parser.add_argument("--semantic-implementation-sha", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--test-keys", action="store_true")
    args = parser.parse_args()

    if not __import__("re").fullmatch(r"[0-9a-f]{40}", args.semantic_implementation_sha):
        raise SystemExit("--semantic-implementation-sha must be exact 40-hex")

    try:
        receipt = execute(args)
    except Exception as exc:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        failure = {
            "schema": PIPELINE_RECEIPT_SCHEMA,
            "pipeline_status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "production_promotion_authorized": False,
        }
        (args.out_dir / "PIPELINE-FAILURE.json").write_bytes(canonical_bytes(failure))
        raise

    (args.out_dir / "PIPELINE-RECEIPT.json").write_bytes(canonical_bytes(receipt))
    print(json.dumps(receipt, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
