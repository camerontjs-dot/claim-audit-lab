"""Diagnostic-only localization for run 34435011700 positive-case refusals.

Reconstructs the exact preregistered semantic inputs with the frozen bound
successor and captures Decision CLI error payloads that the first evaluator did
not retain. No semantic candidate or external consumer is modified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.cal_temporal_contract_c_decision_rc0 import bound_projection
from research.cal_temporal_contract_c_decision_rc0 import evaluate_bound_successor as bound_eval
from research.cal_temporal_contract_c_decision_rc0 import evaluate_decision_conformance as first_eval
from research.cal_temporal_contract_c_decision_rc0 import projection as c_projection


def _build_cases(*, cohort: dict, event_module, rc8j_root: Path):
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
    unresolved_context = bound_eval._context(spec=cohort["single_unresolved"], proposition=unresolved_prop)
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
    return {
        "support": support_c.contract_c,
        "refute": refute_c.contract_c,
        "mixed": mixed_c.contract_c,
        "unresolved": unresolved_c.contract_c,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--contract-c-root", type=Path, required=True)
    parser.add_argument("--contract-d-root", type=Path, required=True)
    parser.add_argument("--decision-root", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    decision_root = args.decision_root.resolve()
    if first_eval._git(decision_root, "rev-parse", "HEAD") != first_eval.DECISION_HEAD:
        raise RuntimeError("Decision Engine exact head mismatch")
    for path, expected in first_eval.DECISION_BLOBS.items():
        if first_eval._git(decision_root, "hash-object", path) != expected:
            raise RuntimeError(f"Decision blob drift: {path}")

    cohort = json.loads(args.cohort.read_text(encoding="utf-8"))
    event_root = args.event_root.resolve()
    rc8j_root = args.rc8j_root.resolve()
    event_module = bound_eval.phase3._load_module(
        "cal_temporal_decision_diagnostic_event",
        event_root / bound_eval.phase3.EVENT_PATH,
    )
    bound_eval.phase3._require_dependency(
        event_root,
        bound_eval.phase3.EVENT_HEAD,
        {bound_eval.phase3.EVENT_PATH: bound_eval.phase3.EVENT_BLOB},
    )
    bound_eval.phase3._require_dependency(
        rc8j_root,
        bound_eval.phase3.RC8J_HEAD,
        bound_eval.phase3.RC8J_BLOBS,
    )

    cases = _build_cases(cohort=cohort, event_module=event_module, rc8j_root=rc8j_root)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, contract_c in cases.items():
        run = first_eval._decision_cli(
            decision_root=decision_root,
            contract_c_root=args.contract_c_root.resolve(),
            contract_d_root=args.contract_d_root.resolve(),
            contract_c=contract_c,
            out_dir=out,
            name=name,
        )
        results[name] = {
            "returncode": run["returncode"],
            "error": run["error"],
            "actual_contract_c_sha256": run["actual_contract_c_sha256"],
            "expected_contract_c_sha256": run["expected_contract_c_sha256"],
            "stdout": run["stdout"],
            "stderr": run["stderr"],
        }

    report = {
        "schema": "cal-temporal-decision-refusal-localization-v1",
        "source_run": 34435011700,
        "semantic_inputs_changed": False,
        "bound_successor_freeze": first_eval.BOUND_FREEZE,
        "decision_engine_head": first_eval.DECISION_HEAD,
        "results": results,
        "all_positive_inputs_refused": all(row["returncode"] != 0 for row in results.values()),
        "interpretation": {
            "source_run_broad_scientific_label_final": False,
            "this_is_diagnostic_only": True,
            "production_promotion_authorized": False,
        },
    }
    (out / "DECISION-REFUSAL-DIAGNOSTIC.json").write_bytes(c_projection.canonical_bytes(report))
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
