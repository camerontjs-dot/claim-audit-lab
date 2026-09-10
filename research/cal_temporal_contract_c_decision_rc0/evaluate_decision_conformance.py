"""Downstream conformance evaluator for bound temporal Contract C -> Decision Engine."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from research.cal_temporal_contract_c_decision_rc0 import bound_projection
from research.cal_temporal_contract_c_decision_rc0 import evaluate_bound_successor as bound_eval
from research.cal_temporal_contract_c_decision_rc0 import projection as c_projection

SCHEMA = "cal-temporal-decision-conformance-rc0-v1"
BOUND_FREEZE = "10ce0894a56f265434b24963bf0543765c453996"
DECISION_HEAD = "358c2bb20f490bf25e808434394b26a70a16a123"
DECISION_BLOBS = {
    "scripts/decision-engine-evaluate.mjs": "b3808a536ca5f976ca1022c7c9f13a229d31af79",
    "src/contractCIngress.js": "f57a8067dadc04afb459f1d0342b2b786ec775e6",
    "src/contractCDecision.js": "3529b75f75936fffb9b2d9e2972cb7117b526661",
    "src/contractCDecisionRuntime.js": "7020006a350f78b0381df3309f8085966890a049",
    "src/contractDCanonicalOutput.js": "0ea61767b9ae61b3b80c0c2f26de4292f213b7fb",
}
CONTRACT_C_HEAD = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
CONTRACT_D_HEAD = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"
POLICY = "decision-engine.contract-c.supported-claim-verification@1.0.0"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _sha_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(c_projection.canonical_bytes(value))


def _decision_cli(
    *,
    decision_root: Path,
    contract_c_root: Path,
    contract_d_root: Path,
    contract_c: dict[str, Any],
    out_dir: Path,
    name: str,
    expected_sha: str | None = None,
    expected_b_override: dict[str, Any] | None = None,
    target_hash_override: str | None = None,
) -> dict[str, Any]:
    case_dir = out_dir / name
    case_dir.mkdir(parents=True, exist_ok=True)
    c_bytes = c_projection.canonical_bytes(contract_c)
    c_path = case_dir / "contract-c.json"
    c_path.write_bytes(c_bytes)
    expected_b = expected_b_override or deepcopy(contract_c["input"]["contract_b"])
    b_path = case_dir / "expected-contract-b.json"
    _write_json(b_path, expected_b)
    proposition = contract_c["propositions"][0]
    text_hash = proposition["proposition"]["text_sha256"]
    context = {
        "proposition_id": proposition["proposition"]["proposition_id"],
        "target": {
            "kind": "claim",
            "id": proposition["proposition"]["proposition_id"],
            "content_sha256": target_hash_override or f"sha256:{text_hash}",
        },
    }
    context_path = case_dir / "decision-context.json"
    _write_json(context_path, context)
    supplied_sha = expected_sha or _sha_bytes(c_bytes)
    proc = subprocess.run(
        [
            "node",
            str(decision_root / "scripts" / "decision-engine-evaluate.mjs"),
            "--contract-c", str(c_path),
            "--contract-c-sha256", supplied_sha,
            "--contract-c-authority", str(contract_c_root),
            "--contract-d-authority", str(contract_d_root),
            "--expected-contract-b", str(b_path),
            "--policy", POLICY,
            "--context", str(context_path),
            "--python", "python3",
        ],
        capture_output=True,
    )
    stdout = proc.stdout.decode("utf-8", errors="replace")
    stderr = proc.stderr.decode("utf-8", errors="replace")
    payload = None
    if proc.returncode == 0:
        payload = json.loads(stdout)
        (case_dir / "contract-d.json").write_bytes(proc.stdout)
    error = None
    if proc.returncode != 0:
        try:
            error = json.loads(stderr.strip().splitlines()[-1])
        except Exception:
            error = {"status": "unparsed", "raw": stderr.strip()}
    return {
        "returncode": proc.returncode,
        "expected_contract_c_sha256": supplied_sha,
        "actual_contract_c_sha256": _sha_bytes(c_bytes),
        "contract_d": payload,
        "error": error,
        "stdout": stdout.strip(),
        "stderr": stderr.strip(),
    }


def _decision_summary(run: dict[str, Any]) -> dict[str, Any]:
    d = run["contract_d"]
    if not isinstance(d, dict):
        return {"evaluation": None, "reason_codes": None, "effect": None}
    return {
        "evaluation": d.get("evaluation"),
        "reason_codes": (d.get("metadata") or {}).get("reason_codes"),
        "effect": d.get("effect"),
        "policy": d.get("policy"),
    }


def _expected_error(run: dict[str, Any], code: str) -> bool:
    return run["returncode"] != 0 and isinstance(run["error"], dict) and run["error"].get("code") == code


def _reidentity(value: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(value)
    payload["producer"]["policy"]["sha256"] = c_projection.sha256_hex(
        c_projection.canonical_bytes(payload["producer"]["policy"]["canonical"])
    )
    return c_projection.with_result_set_id(payload)


def execute(
    *,
    repo_root: Path,
    event_root: Path,
    rc8j_root: Path,
    contract_c_root: Path,
    contract_d_root: Path,
    decision_root: Path,
    cohort_path: Path,
    out_dir: Path,
) -> dict[str, Any]:
    if _git(decision_root, "rev-parse", "HEAD") != DECISION_HEAD:
        raise RuntimeError("Decision Engine exact head mismatch")
    for path, expected in DECISION_BLOBS.items():
        actual = _git(decision_root, "hash-object", path)
        if actual != expected:
            raise RuntimeError(f"Decision Engine blob drift {path}: {actual} != {expected}")
    if _git(contract_c_root, "rev-parse", "HEAD") != CONTRACT_C_HEAD:
        raise RuntimeError("Contract C authority head mismatch")
    if _git(contract_d_root, "rev-parse", "HEAD") != CONTRACT_D_HEAD:
        raise RuntimeError("Contract D authority head mismatch")

    cohort = json.loads(cohort_path.read_text(encoding="utf-8"))
    event_module = bound_eval.phase3._load_module(
        "cal_temporal_decision_event", event_root / bound_eval.phase3.EVENT_PATH
    )
    bound_eval.phase3._require_dependency(
        event_root, bound_eval.phase3.EVENT_HEAD,
        {bound_eval.phase3.EVENT_PATH: bound_eval.phase3.EVENT_BLOB},
    )
    bound_eval.phase3._require_dependency(
        rc8j_root, bound_eval.phase3.RC8J_HEAD, bound_eval.phase3.RC8J_BLOBS
    )

    prop = bound_eval._proposition(cohort["proposition"])
    support_context = bound_eval._context(spec=cohort["single_support"], proposition=prop)
    support = bound_eval._proof(
        context=support_context,
        passage_id=cohort["single_support"]["passages"][0]["passage_id"],
        proposition=prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    support_c = bound_projection.project_bound_temporal_contract_c(
        proposition=prop,
        proofs=(support,),
        atom_trusted_keys=bound_eval.ATOM_KEYS,
        proposition_trusted_keys=bound_eval.PROP_KEYS,
    )

    refute_context = bound_eval._context(spec=cohort["single_refute"], proposition=prop)
    refute = bound_eval._proof(
        context=refute_context,
        passage_id=cohort["single_refute"]["passages"][0]["passage_id"],
        proposition=prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    refute_c = bound_projection.project_bound_temporal_contract_c(
        proposition=prop,
        proofs=(refute,),
        atom_trusted_keys=bound_eval.ATOM_KEYS,
        proposition_trusted_keys=bound_eval.PROP_KEYS,
    )

    mixed_context = bound_eval._context(spec=cohort["same_world_mixed"], proposition=prop)
    mixed_support = bound_eval._proof(
        context=mixed_context,
        passage_id=cohort["same_world_mixed"]["passages"][0]["passage_id"],
        proposition=prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    mixed_refute = bound_eval._proof(
        context=mixed_context,
        passage_id=cohort["same_world_mixed"]["passages"][1]["passage_id"],
        proposition=prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    mixed_c = bound_projection.project_bound_temporal_contract_c(
        proposition=prop,
        proofs=(mixed_support, mixed_refute),
        atom_trusted_keys=bound_eval.ATOM_KEYS,
        proposition_trusted_keys=bound_eval.PROP_KEYS,
    )

    unresolved_prop = bound_eval._proposition(cohort["single_unresolved"]["proposition"])
    unresolved_context = bound_eval._context(
        spec=cohort["single_unresolved"], proposition=unresolved_prop
    )
    unresolved = bound_eval._proof(
        context=unresolved_context,
        passage_id=cohort["single_unresolved"]["passages"][0]["passage_id"],
        proposition=unresolved_prop,
        event_module=event_module,
        rc8j_root=rc8j_root,
    )
    unresolved_c = bound_projection.project_bound_temporal_contract_c(
        proposition=unresolved_prop,
        proofs=(unresolved,),
        atom_trusted_keys=bound_eval.ATOM_KEYS,
        proposition_trusted_keys=bound_eval.PROP_KEYS,
    )

    runs = {
        "support": _decision_cli(
            decision_root=decision_root, contract_c_root=contract_c_root,
            contract_d_root=contract_d_root, contract_c=support_c.contract_c,
            out_dir=out_dir, name="support",
        ),
        "refute": _decision_cli(
            decision_root=decision_root, contract_c_root=contract_c_root,
            contract_d_root=contract_d_root, contract_c=refute_c.contract_c,
            out_dir=out_dir, name="refute",
        ),
        "mixed": _decision_cli(
            decision_root=decision_root, contract_c_root=contract_c_root,
            contract_d_root=contract_d_root, contract_c=mixed_c.contract_c,
            out_dir=out_dir, name="mixed",
        ),
        "unresolved": _decision_cli(
            decision_root=decision_root, contract_c_root=contract_c_root,
            contract_d_root=contract_d_root, contract_c=unresolved_c.contract_c,
            out_dir=out_dir, name="unresolved",
        ),
    }

    summaries = {name: _decision_summary(run) for name, run in runs.items()}
    positive = {
        "support_clear": (
            runs["support"]["returncode"] == 0
            and summaries["support"]["evaluation"] == {"state": "completed", "disposition": "clear"}
            and summaries["support"]["reason_codes"] == ["contract_c_supported"]
        ),
        "refute_hold": (
            runs["refute"]["returncode"] == 0
            and summaries["refute"]["evaluation"] == {"state": "completed", "disposition": "hold"}
            and summaries["refute"]["reason_codes"] == ["contract_c_reported_verdict_not_supported"]
        ),
        "mixed_hold": (
            runs["mixed"]["returncode"] == 0
            and summaries["mixed"]["evaluation"] == {"state": "completed", "disposition": "hold"}
            and summaries["mixed"]["reason_codes"] == ["contract_c_proposition_not_checkable"]
        ),
        "unresolved_hold": (
            runs["unresolved"]["returncode"] == 0
            and summaries["unresolved"]["evaluation"] == {"state": "completed", "disposition": "hold"}
            and summaries["unresolved"]["reason_codes"] == ["contract_c_proposition_not_checkable"]
        ),
    }

    wrong_sha = "sha256:" + ("0" * 64)
    if wrong_sha == runs["support"]["actual_contract_c_sha256"]:
        wrong_sha = "sha256:" + ("1" * 64)
    wrong_digest_run = _decision_cli(
        decision_root=decision_root, contract_c_root=contract_c_root,
        contract_d_root=contract_d_root, contract_c=support_c.contract_c,
        out_dir=out_dir, name="wrong-digest", expected_sha=wrong_sha,
    )
    wrong_b = deepcopy(support_c.contract_c["input"]["contract_b"])
    wrong_b["bundle_id"] = wrong_b["bundle_id"] + "-wrong"
    wrong_b_run = _decision_cli(
        decision_root=decision_root, contract_c_root=contract_c_root,
        contract_d_root=contract_d_root, contract_c=support_c.contract_c,
        out_dir=out_dir, name="wrong-contract-b", expected_b_override=wrong_b,
    )
    wrong_target = "sha256:" + ("f" * 64)
    if wrong_target == f"sha256:{support_c.contract_c['propositions'][0]['proposition']['text_sha256']}":
        wrong_target = "sha256:" + ("e" * 64)
    wrong_target_run = _decision_cli(
        decision_root=decision_root, contract_c_root=contract_c_root,
        contract_d_root=contract_d_root, contract_c=support_c.contract_c,
        out_dir=out_dir, name="wrong-target", target_hash_override=wrong_target,
    )

    illegal_family = deepcopy(support_c.contract_c)
    illegal_family["propositions"][0]["semantic_family"] = "event_ordering"
    illegal_family = c_projection.with_result_set_id(illegal_family)
    illegal_family_run = _decision_cli(
        decision_root=decision_root, contract_c_root=contract_c_root,
        contract_d_root=contract_d_root, contract_c=illegal_family,
        out_dir=out_dir, name="illegal-family-field",
    )

    illegal_measurement = deepcopy(support_c.contract_c)
    contribution_id = illegal_measurement["propositions"][0]["contributions"][0]["contribution_id"]
    illegal_measurement["propositions"][0]["measurement"] = {
        "kind": "event_order",
        "value": "BEFORE",
        "basis_contribution_ids": [contribution_id],
    }
    illegal_measurement = c_projection.with_result_set_id(illegal_measurement)
    illegal_measurement_run = _decision_cli(
        decision_root=decision_root, contract_c_root=contract_c_root,
        contract_d_root=contract_d_root, contract_c=illegal_measurement,
        out_dir=out_dir, name="illegal-string-measurement",
    )

    policy_meta = deepcopy(support_c.contract_c)
    policy_meta["producer"]["policy"]["canonical"]["semantic_family"] = "control-family-label"
    policy_meta["producer"]["policy"]["canonical"]["profile"] = "control-producer-metadata"
    policy_meta = _reidentity(policy_meta)
    policy_meta_run = _decision_cli(
        decision_root=decision_root, contract_c_root=contract_c_root,
        contract_d_root=contract_d_root, contract_c=policy_meta,
        out_dir=out_dir, name="producer-policy-metamorphism",
    )
    policy_meta_summary = _decision_summary(policy_meta_run)

    falsifiers = {
        "wrong_contract_c_digest_refused": _expected_error(
            wrong_digest_run, "contract_c_whole_object_mismatch"
        ),
        "wrong_contract_b_refused": _expected_error(
            wrong_b_run, "contract_b_binding_mismatch"
        ),
        "wrong_target_hash_refused": _expected_error(
            wrong_target_run, "target_binding_mismatch"
        ),
        "illegal_semantic_family_field_refused": _expected_error(
            illegal_family_run, "contract_c_validation_failed"
        ),
        "illegal_string_temporal_measurement_refused": _expected_error(
            illegal_measurement_run, "contract_c_validation_failed"
        ),
        "producer_policy_metadata_decision_invariant": (
            policy_meta_run["returncode"] == 0
            and policy_meta_summary["evaluation"] == summaries["support"]["evaluation"]
            and policy_meta_summary["reason_codes"] == summaries["support"]["reason_codes"]
            and policy_meta_summary["effect"] == summaries["support"]["effect"]
        ),
    }

    positive_failures = [name for name, passed in positive.items() if not passed]
    falsifier_failures = [name for name, passed in falsifiers.items() if not passed]
    disposition = (
        "SUPPORTED_WITH_BOUNDS_AND_UPSTREAM_PROVENANCE_GAP"
        if not positive_failures and not falsifier_failures
        else "FALSIFIED_TEMPORAL_DECISION_CONFORMANCE"
    )
    result = {
        "schema": SCHEMA,
        "bound_successor_freeze": BOUND_FREEZE,
        "decision_engine_head": DECISION_HEAD,
        "decision_engine_blobs": DECISION_BLOBS,
        "contract_c_authority": CONTRACT_C_HEAD,
        "contract_d_authority": CONTRACT_D_HEAD,
        "positive": positive,
        "decision_summaries": summaries,
        "falsifiers": falsifiers,
        "negative_runs": {
            "wrong_digest": wrong_digest_run,
            "wrong_contract_b": wrong_b_run,
            "wrong_target": wrong_target_run,
            "illegal_family_field": illegal_family_run,
            "illegal_string_measurement": illegal_measurement_run,
        },
        "producer_policy_metamorphism": {
            "run": policy_meta_run,
            "summary": policy_meta_summary,
        },
        "summary": {
            "positive_failures": positive_failures,
            "falsifier_failures": falsifier_failures,
            "support_clear": positive["support_clear"],
            "refute_hold": positive["refute_hold"],
            "mixed_hold": positive["mixed_hold"],
            "unresolved_hold": positive["unresolved_hold"],
            "policy_metadata_invariant": falsifiers["producer_policy_metadata_decision_invariant"],
        },
        "research_disposition": disposition,
        "interpretation": {
            "decision_consumer_requires_strict_comparison_family": False if not positive_failures else None,
            "contract_c_unresolved_evidence_provenance_lossless": False,
            "contract_d_clear_is_authorization": False,
            "contract_e_authorization_evaluated": False,
            "external_mutation_performed": False,
            "production_promotion_authorized": False,
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "DECISION-EVALUATION.json").write_bytes(c_projection.canonical_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--contract-c-root", type=Path, required=True)
    parser.add_argument("--contract-d-root", type=Path, required=True)
    parser.add_argument("--decision-root", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(
        repo_root=args.repo_root.resolve(),
        event_root=args.event_root.resolve(),
        rc8j_root=args.rc8j_root.resolve(),
        contract_c_root=args.contract_c_root.resolve(),
        contract_d_root=args.contract_d_root.resolve(),
        decision_root=args.decision_root.resolve(),
        cohort_path=args.cohort.resolve(),
        out_dir=args.out.resolve(),
    )
    print(json.dumps({"research_disposition": result["research_disposition"], **result["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
