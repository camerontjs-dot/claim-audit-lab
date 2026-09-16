from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from claim_audit_lab.production_v1.semantic.engine import audit

HERE = Path(__file__).resolve().parent
RC0 = HERE.parent / "contract_c2_current_cal_producer_conformance_rc0"
CURRENT_CAL = "847cc970642bb648dc994b929c2053b5c9d4648c"
OLD_CAL = "a902621e8baea3063dddd7f92ba975aade305464"
OLD_RESOLVER = "43b571464734325277374ee81098553fb7c1b944"


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_rc0() -> tuple[ModuleType, ModuleType]:
    rc0_materialize = _load("rc0_materialize_frozen", RC0 / "materialize.py")
    prior = sys.modules.get("materialize")
    sys.modules["materialize"] = rc0_materialize
    try:
        rc0_evaluate = _load("rc0_evaluate_frozen", RC0 / "evaluate.py")
    finally:
        if prior is None:
            sys.modules.pop("materialize", None)
        else:
            sys.modules["materialize"] = prior
    return rc0_materialize, rc0_evaluate


def _load_rc1_materialize() -> ModuleType:
    return _load("rc1_materialize_candidate", HERE / "materialize.py")


def _load_c2(root: Path) -> ModuleType:
    sys.path.insert(0, str(root))
    try:
        import importlib

        return importlib.import_module("validators.contract_c_v2")
    finally:
        sys.path.pop(0)


def _cases(e: ModuleType) -> dict[str, Any]:
    return {
        "strict_support": e.strict_context([("S1", e.SUPPORT_A)], "strict-support"),
        "strict_refutation": e.strict_context([("R1", e.REFUTE_A)], "strict-refutation"),
        "two_supports": e.strict_context([("S1", e.SUPPORT_A), ("S2", e.SUPPORT_B)], "two-supports"),
        "support_irrelevant": e.strict_context([("S1", e.SUPPORT_A), ("N1", e.IRRELEVANT)], "support-irrelevant"),
        "minimal_mixed": e.strict_context([("S1", e.SUPPORT_A), ("R1", e.REFUTE_A)], "minimal-mixed"),
        "alternative_joint": e.strict_context(
            [("S1", e.SUPPORT_A), ("S2", e.SUPPORT_B), ("R1", e.REFUTE_A)], "alternative-joint"
        ),
        "symmetric_alternative_joint": e.strict_context(
            [("S1", e.SUPPORT_A), ("R1", e.REFUTE_A), ("R2", e.REFUTE_B)], "symmetric-alternative-joint"
        ),
        "four_way_mixed": e.strict_context(
            [("S1", e.SUPPORT_A), ("S2", e.SUPPORT_B), ("R1", e.REFUTE_A), ("R2", e.REFUTE_B)],
            "four-way-mixed",
        ),
        "irrelevant_only": e.strict_context([("N1", e.IRRELEVANT)], "irrelevant-only"),
        "measurement_not_applicable": e.strict_context(
            [("N1", "The report describes annual enrollment totals.")], "measurement-not-applicable"
        ),
        "event_support": e.event_context(
            [("E1", "Alice reviewed dossier before Bob archived dossier.")], "event-support"
        ),
        "event_refutation": e.event_context(
            [("E1", "Alice reviewed dossier after Bob archived dossier.")], "event-refutation"
        ),
        "negative_event_unresolved": e.event_context(
            [("E1", "Alice did not review dossier before Bob archived dossier.")],
            "negative-event-unresolved",
            left_polarity="negative",
        ),
        "support_plus_unresolved": e.event_context(
            [
                ("E1", "Alice reviewed dossier before Bob archived dossier."),
                ("E2", "Alice did not review dossier before Bob archived dossier."),
            ],
            "support-plus-unresolved",
        ),
        "event_scope_stress": e.event_context(
            [("E1", "Report says Alice reviewed dossier before Bob archived dossier.")],
            "event-scope-stress",
        ),
        "unsupported_family": e.unsupported_context(),
    }


def _expect_reject(fn, label: str) -> str:
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - negative control
        return f"{type(exc).__name__}: {exc}"
    raise AssertionError(f"negative control unexpectedly succeeded: {label}")


def evaluate(apparatus: Path, resolver_root: Path, materializer_blob: str) -> dict[str, Any]:
    rc0_m, rc0_e = _load_rc0()
    rc1_m = _load_rc1_materialize()
    c2 = _load_c2(apparatus)
    resolver = json.loads(
        (
            resolver_root
            / "research/contract_c_successor_ground_up_20260913/PHASE_1_5_POLICY_RESOLVER.json"
        ).read_text(encoding="utf-8")
    )

    signature = inspect.signature(rc1_m.materialize_unsealed)
    if "semantic_implementation_sha" in signature.parameters:
        raise AssertionError("RC1 still exposes caller-selectable semantic implementation identity")
    if rc1_m.SEMANTIC_IMPLEMENTATION_SHA != CURRENT_CAL:
        raise AssertionError("RC1 runtime identity drift")
    if rc1_m.POLICY_SHA256 != rc0_m.POLICY_SHA256:
        raise AssertionError("RC1 policy digest changed")
    if rc1_m.POLICY != rc0_m.POLICY:
        raise AssertionError("RC1 policy payload changed")

    cases = _cases(rc0_e)
    observations: dict[str, Any] = {}
    failures: list[str] = []
    for case_id, context in cases.items():
        try:
            result = audit(context)
            predecessor = rc0_m.materialize_unsealed(
                context,
                result,
                semantic_implementation_sha=CURRENT_CAL,
                policy_resolver_commit_sha=OLD_RESOLVER,
            )
            successor = rc1_m.materialize_unsealed(
                context,
                result,
                policy_resolver_commit_sha=OLD_RESOLVER,
            )
            if successor != predecessor:
                raise AssertionError("RC1 output differs from frozen RC0 for correct identity")
            sealed = c2.seal(successor)
            c2.validate_object(sealed)
            if sealed["producer"]["semantic_implementation_sha"] != CURRENT_CAL:
                raise AssertionError("sealed producer identity mismatch")
            observations[case_id] = {
                "byte_equivalent_to_rc0": c2.canonical_bytes(sealed)
                == c2.canonical_bytes(c2.seal(predecessor)),
                "terminal": sealed["propositions"][0]["terminal"],
                "result_set_id": sealed["result_set_id"],
                "whole_object_sha256": c2.whole_object_sha256(sealed),
            }
            if not observations[case_id]["byte_equivalent_to_rc0"]:
                raise AssertionError("RC1 canonical bytes differ from RC0")
        except Exception as exc:  # noqa: BLE001 - terminal experiment record
            failures.append(f"{case_id}: {type(exc).__name__}: {exc}")

    sample_context = cases["strict_support"]
    sample_result = audit(sample_context)
    negative_controls: dict[str, str] = {}
    negative_controls["legacy_caller_identity_argument_rejected"] = _expect_reject(
        lambda: rc1_m.materialize_unsealed(
            sample_context,
            sample_result,
            policy_resolver_commit_sha=OLD_RESOLVER,
            semantic_implementation_sha=OLD_CAL,
        ),
        "legacy caller-selected semantic implementation",
    )

    original_identity = rc1_m.SEMANTIC_IMPLEMENTATION_SHA
    try:
        rc1_m.SEMANTIC_IMPLEMENTATION_SHA = OLD_CAL
        negative_controls["runtime_identity_drift_rejected"] = _expect_reject(
            lambda: rc1_m.materialize_unsealed(
                sample_context,
                sample_result,
                policy_resolver_commit_sha=OLD_RESOLVER,
            ),
            "runtime semantic identity drift",
        )
    finally:
        rc1_m.SEMANTIC_IMPLEMENTATION_SHA = original_identity

    correctly_bound = c2.seal(
        rc1_m.materialize_unsealed(
            sample_context,
            sample_result,
            policy_resolver_commit_sha=OLD_RESOLVER,
        )
    )
    negative_controls["predecessor_resolver_still_rejects_current_cal"] = _expect_reject(
        lambda: c2.verify_policy_resolution(
            correctly_bound,
            independently_selected_resolver_commit_sha=OLD_RESOLVER,
            resolver_entries=resolver["entries"],
        ),
        "predecessor resolver accepted current CAL",
    )

    classification = (
        "SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION"
        if not failures
        and len(observations) == 16
        and len(negative_controls) == 3
        else "FALSIFIED_PRODUCER_IDENTITY_BINDING"
    )
    return {
        "schema": "current-cal-contract-c2-producer-conformance-rc1-result-v1",
        "classification": classification,
        "materializer_blob": materializer_blob,
        "semantic_implementation_sha": CURRENT_CAL,
        "policy_sha256": rc1_m.POLICY_SHA256,
        "cases": observations,
        "negative_controls": negative_controls,
        "failures": failures,
        "successor_delta": "producer semantic identity is runtime-bound and not caller-selectable",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apparatus", type=Path, required=True)
    parser.add_argument("--resolver", type=Path, required=True)
    parser.add_argument("--materializer-blob", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.apparatus.resolve(), args.resolver.resolve(), args.materializer_blob)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"classification": result["classification"], "failures": result["failures"]}, sort_keys=True))
    return 0 if result["classification"] == "SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
