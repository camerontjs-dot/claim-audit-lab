"""Run a Contract B 1.2 evidence bundle through CAL RC0 and Decision Engine.

Research/integration apparatus only. This accepts an already-built Evidence
Bundler Contract B tree, executes the supported strict-comparison CAL slice,
emits exact Contract C 1.0, then invokes the maintained Decision Engine
supported-claim-verification policy to emit canonical Contract D 1.0.

It performs no Authorization or execution.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
from types import ModuleType
from typing import Any, Callable

import run_pipeline as base

DECISION_ENGINE_HEAD = "a4425f8eb47449ff6c683222921bbea9483742e2"
DECISION_ENGINE_BLOBS = {
    "scripts/decision-engine-evaluate.mjs": "b3808a536ca5f976ca1022c7c9f13a229d31af79",
    "src/contractCDecisionRuntime.js": "7020006a350f78b0381df3309f8085966890a049",
    "src/contractCDecision.js": "3529b75f75936fffb9b2d9e2972cb7117b526661",
    "src/contractCIngress.js": "f57a8067dadc04afb459f1d0342b2b786ec775e6",
}
CONTRACT_D_AUTHORITY = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"
DECISION_POLICY = "decision-engine.contract-c.supported-claim-verification@1.0.0"
RECEIPT_SCHEMA = "cal-contract-b-to-decision-rc0-receipt-v1"

SpanResolver = Callable[[str, str], tuple[int, int] | None]


class _EntityScopedRuntime:
    """Apply RC0A only to lhs/rhs entity span lookups during frozen RC0 execution."""

    def __init__(self, module: ModuleType, entity_resolver: SpanResolver) -> None:
        self._module = module
        self._entity_resolver = entity_resolver

    def __getattr__(self, name: str) -> Any:
        if name == "execute_rc0_case":
            return self._execute_rc0_case
        return getattr(self._module, name)

    def _execute_rc0_case(self, **kwargs: Any) -> dict[str, Any]:
        module = self._module
        frozen_complete = module.complete_strict_comparison_atom
        frozen_span = module._unique_casefold_span
        resolver = self._entity_resolver

        def adapted_complete(
            *, claim_id: str, evidence: Any, measurement: dict[str, Any]
        ) -> tuple[Any, str]:
            calls = 0

            def entity_then_frozen(text: str, surface: str) -> tuple[int, int] | None:
                nonlocal calls
                calls += 1
                return resolver(text, surface) if calls <= 2 else frozen_span(text, surface)

            module._unique_casefold_span = entity_then_frozen
            try:
                return frozen_complete(
                    claim_id=claim_id,
                    evidence=evidence,
                    measurement=measurement,
                )
            finally:
                module._unique_casefold_span = frozen_span

        module.complete_strict_comparison_atom = adapted_complete
        try:
            return module.execute_rc0_case(**kwargs)
        finally:
            module.complete_strict_comparison_atom = frozen_complete
            module._unique_casefold_span = frozen_span


def _claim_rows(bundle: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((bundle / "claims").glob("*.yaml")):
        row = base.load_yaml(path)
        claim_id = str(row.get("claim_id") or "")
        if not claim_id or claim_id in rows:
            raise RuntimeError(f"invalid or duplicate Contract B claim id: {claim_id!r}")
        rows[claim_id] = row
    return rows


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _run_decision_engine(
    *,
    decision_engine_root: Path,
    apparatus_c: Path,
    apparatus_d: Path,
    contract_c_path: Path,
    contract_c_sha256: str,
    expected_contract_b: dict[str, str],
    proposition_id: str,
    claim_text_sha256: str,
    out_dir: Path,
) -> tuple[Path, dict[str, Any]]:
    inputs = out_dir / "decision-inputs"
    decisions = out_dir / "contract-d"
    inputs.mkdir(parents=True, exist_ok=True)
    decisions.mkdir(parents=True, exist_ok=True)

    safe = hashlib.sha256(proposition_id.encode("utf-8")).hexdigest()[:16]
    expected_b_path = inputs / f"{safe}.expected-contract-b.json"
    context_path = inputs / f"{safe}.context.json"
    decision_path = decisions / f"{safe}.json"

    expected_b_path.write_bytes(base.canonical_bytes(expected_contract_b))
    context = {
        "proposition_id": proposition_id,
        "target": {
            "kind": "claim",
            "id": proposition_id,
            "content_sha256": f"sha256:{claim_text_sha256}",
        },
    }
    context_path.write_bytes(base.canonical_bytes(context))

    proc = subprocess.run(
        [
            "node",
            str(decision_engine_root / "scripts" / "decision-engine-evaluate.mjs"),
            "--contract-c",
            str(contract_c_path),
            "--contract-c-sha256",
            contract_c_sha256,
            "--contract-c-authority",
            str(apparatus_c),
            "--contract-d-authority",
            str(apparatus_d),
            "--expected-contract-b",
            str(expected_b_path),
            "--policy",
            DECISION_POLICY,
            "--context",
            str(context_path),
            "--python",
            "python3",
        ],
        capture_output=True,
        text=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or b"").decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Decision Engine failed for {proposition_id}: {detail}")
    decision_path.write_bytes(proc.stdout)
    try:
        decision = json.loads(proc.stdout.decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Decision Engine emitted non-JSON Contract D for {proposition_id}") from exc
    return decision_path, decision


def execute(args: argparse.Namespace) -> dict[str, Any]:
    cal_root = args.cal_root.resolve()
    bundle = args.bundle.resolve()
    rc7_root = args.rc7fb1_root.resolve()
    rc8_root = args.rc8j_root.resolve()
    apparatus_b = args.apparatus_b.resolve()
    apparatus_c = args.apparatus_c.resolve()
    apparatus_d = args.apparatus_d.resolve()
    decision_engine_root = args.decision_engine_root.resolve()
    out = args.out_dir.resolve()

    base.require_identity(
        cal_root,
        head=args.cal_head,
        blobs={
            "research/cal_research_profile_rc0/runtime.py": base.RC0_RUNTIME_BLOB,
            "research/cal_research_profile_rc0a_span_anchoring/span_anchor.py": base.RC0A_SPAN_BLOB,
        },
    )
    base.require_identity(
        rc7_root,
        head=base.RC7FB1_HEAD,
        blobs={"research/comparative_relation_measurement_rc7fb1/comparator.py": base.RC7FB1_BLOB},
    )
    base.require_identity(
        rc8_root,
        head=base.RC8J_HEAD,
        blobs={"research/semantic_authority_machinery_rc8/authority_contract_rc8j.py": base.RC8J_BLOB},
    )
    if base.git_head(apparatus_b) != base.CONTRACT_B_AUTHORITY:
        raise RuntimeError("Contract B authority checkout mismatch")
    if base.git_head(apparatus_c) != base.CONTRACT_C_AUTHORITY:
        raise RuntimeError("Contract C authority checkout mismatch")
    if base.git_head(apparatus_d) != CONTRACT_D_AUTHORITY:
        raise RuntimeError("Contract D authority checkout mismatch")
    base.require_identity(
        decision_engine_root,
        head=DECISION_ENGINE_HEAD,
        blobs=DECISION_ENGINE_BLOBS,
    )

    runtime_module = base.load_module(
        "cal_bundle_runtime",
        cal_root / "research" / "cal_research_profile_rc0" / "runtime.py",
    )
    span = base.load_module(
        "cal_bundle_span",
        cal_root / "research" / "cal_research_profile_rc0a_span_anchoring" / "span_anchor.py",
    )
    if span.unique_lexical_span("Women trailed Men by 11 percentage points.", "Men") != (14, 17):
        raise RuntimeError("RC0A entity span control failed")
    runtime = _EntityScopedRuntime(runtime_module, span.unique_lexical_span)
    measure_fn = base.load_measure(rc7_root)
    authority_evaluator = base.load_rc8j(rc8_root)

    b_validation_raw = base.validate_contract_b(bundle, apparatus_b)
    if b_validation_raw["status"] != "PASS":
        raise RuntimeError("exact Contract B 1.2 validation failed")

    claims = _claim_rows(bundle)
    manifest = base.load_yaml(bundle / "bundle_manifest.yaml")
    bundle_id = str(manifest["bundle_id"])
    targets_doc = base.load_json(args.targets.resolve())
    tmap = base.target_map(targets_doc, bundle_id)
    missing = sorted(set(tmap) - set(claims))
    if missing:
        raise RuntimeError(f"CAL targets absent from Contract B claims: {missing}")

    extension_path = bundle / "extensions" / "contract-b-factual-context-v1.json"
    if not extension_path.exists():
        raise RuntimeError("Contract B factual-context admission extension is required")
    extension = base.load_json(extension_path)
    passages = base.passage_rows(bundle)
    b_index = base.build_contract_b_index(bundle, runtime.claim_text_sha256)
    expected_b = {
        "contract_version": str(b_index["contract_version"]),
        "bundle_id": str(b_index["bundle_id"]),
        "bundle_hash": str(b_index["bundle_hash"]),
    }

    out.mkdir(parents=True, exist_ok=True)
    index_path = out / "CONTRACT-B-INDEX.json"
    index_path.write_bytes(base.canonical_bytes(b_index))
    (out / "CONTRACT-B-VALIDATION.json").write_bytes(base.canonical_bytes(b_validation_raw))

    atom_key, prop_key, atom_key_id, prop_key_id = base.key_material(test_keys=args.test_keys)
    c_dir = out / "contract-c"
    c_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    for proposition_id in sorted(tmap):
        target = tmap[proposition_id]
        claim = claims[proposition_id]
        proposition = runtime.BoundProposition(
            claim_id=proposition_id,
            claim_text=str(claim["claim_text"]),
            family=str(target["family"]),
            lhs_entity=str(target["lhs_entity"]).casefold(),
            rhs_entity=str(target["rhs_entity"]).casefold(),
            comparison_direction=str(target["comparison_direction"]),
        )

        accepted_ids = base.accepted_passage_ids(extension, proposition_id)
        admitted: list[Any] = []
        for passage_id in accepted_ids:
            passage = passages.get(passage_id)
            if passage is None:
                raise RuntimeError(f"accepted Contract B passage missing: {passage_id}")
            admitted.append(
                runtime.EvidenceInput(
                    source_id=str(passage["source_id"]),
                    bundle_id=bundle_id,
                    passage_id=passage_id,
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
            contract_b_validation={
                "contract_version": "1.2.0",
                "authority_commit": base.CONTRACT_B_AUTHORITY,
                "status": "PASS",
            },
            contract_b_binding=expected_b,
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

        safe = hashlib.sha256(proposition_id.encode("utf-8")).hexdigest()[:16]
        c_path = c_dir / f"{safe}.json"
        c_path.write_text(candidate["contract_c_bytes"], encoding="utf-8")
        c_validation = base.validate_contract_c(c_path, index_path, apparatus_c)
        if c_validation["status"] != "PASS":
            raise RuntimeError(f"exact Contract C 1.0 validation failed for {proposition_id}")

        c_sha = _sha256_file(c_path)
        d_path, decision = _run_decision_engine(
            decision_engine_root=decision_engine_root,
            apparatus_c=apparatus_c,
            apparatus_d=apparatus_d,
            contract_c_path=c_path,
            contract_c_sha256=c_sha,
            expected_contract_b=expected_b,
            proposition_id=proposition_id,
            claim_text_sha256=runtime.claim_text_sha256(proposition.claim_text),
            out_dir=out,
        )
        results.append(
            {
                "proposition_id": proposition_id,
                "admitted_passage_ids": accepted_ids,
                "cal_conclusion": deepcopy(candidate["internal_cal_conclusion"]),
                "contract_c": {
                    "path": str(c_path.relative_to(out)),
                    "sha256": c_sha,
                    "validation": "PASS",
                },
                "decision_engine": {
                    "policy": DECISION_POLICY,
                    "contract_d_path": str(d_path.relative_to(out)),
                    "evaluation": deepcopy(decision.get("evaluation")),
                    "effect": deepcopy(decision.get("effect")),
                    "metadata": deepcopy(decision.get("metadata")),
                },
            }
        )

    return {
        "schema": RECEIPT_SCHEMA,
        "pipeline_status": "PASS",
        "input_contract_b": expected_b,
        "pins": {
            "cal_head": args.cal_head,
            "rc0_runtime_blob": base.RC0_RUNTIME_BLOB,
            "rc0a_span_blob": base.RC0A_SPAN_BLOB,
            "rc7fb1_head": base.RC7FB1_HEAD,
            "rc8j_head": base.RC8J_HEAD,
            "contract_b_authority": base.CONTRACT_B_AUTHORITY,
            "contract_c_authority": base.CONTRACT_C_AUTHORITY,
            "decision_engine_head": DECISION_ENGINE_HEAD,
            "contract_d_authority": CONTRACT_D_AUTHORITY,
        },
        "cal": {
            "semantic_family": "strict_comparison",
            "entity_span_resolver": "rc0a_unique_exact_lexical_boundary",
            "terminal_decision_semantics": "scoreless_categorical",
        },
        "results": results,
        "authorization": {
            "state": "NOT_EVALUATED",
            "detail": "Contract D is Decision output only; no Contract E or execution is invoked.",
        },
        "production_promotion_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path, help="Contract B 1.2 evidence-bundle directory")
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--cal-root", type=Path, default=Path("."))
    parser.add_argument("--cal-head", required=True)
    parser.add_argument("--rc7fb1-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--apparatus-b", type=Path, required=True)
    parser.add_argument("--apparatus-c", type=Path, required=True)
    parser.add_argument("--apparatus-d", type=Path, required=True)
    parser.add_argument("--decision-engine-root", type=Path, required=True)
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
            "schema": RECEIPT_SCHEMA,
            "pipeline_status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "production_promotion_authorized": False,
        }
        (args.out_dir / "BUNDLE-TO-DECISION-FAILURE.json").write_bytes(base.canonical_bytes(failure))
        raise

    (args.out_dir / "BUNDLE-TO-DECISION-RECEIPT.json").write_bytes(base.canonical_bytes(receipt))
    print(json.dumps(receipt, sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
