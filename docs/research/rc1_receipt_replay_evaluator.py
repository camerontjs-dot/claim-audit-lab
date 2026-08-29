"""Frozen evaluator for CAL RC1 bounded receipt/replay research.

This evaluator is itself part of the research apparatus. Its expectations are
frozen before the candidate module is created.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES_PATH = HERE / "rc1-receipt-replay-cases.json"
CANDIDATE_PATH = HERE / "rc1_receipt_replay_candidate.py"

GateResult = dict[str, Any]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def stable_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def semantic_payload(trace: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "entailment": trace.get("entailment", []),
        "support_signal": trace["support_signal"],
    }
    if "negation_probe" in trace:
        payload["negation_probe"] = trace["negation_probe"]
    return payload


def semantic_hash(trace: dict[str, Any]) -> str:
    return stable_hash(semantic_payload(trace))


def verdict_hash(trace: dict[str, Any]) -> str:
    return stable_hash(trace["verdict"])


def git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()  # noqa: S324 - Git object identity


def load_cases() -> dict[str, Any]:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def load_candidate(path: Path = CANDIDATE_PATH) -> ModuleType:
    spec = importlib.util.spec_from_file_location("rc1_receipt_replay_candidate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import candidate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "emit_receipt", None)):
        raise TypeError("candidate must expose callable emit_receipt")
    return module


def generic_state(trace: dict[str, Any]) -> dict[str, Any]:
    passage_ids = sorted(
        {
            row["passage_id"]
            for row in trace.get("entailment", [])
            if isinstance(row, dict) and "passage_id" in row
        }
    )
    return {
        "execution": {"state": "completed", "failure": None},
        "assessments": {
            passage_id: {"eligibility": "performed-positive"}
            for passage_id in passage_ids
        },
        "source_facts": {
            passage_id: {"trust": "primary"} for passage_id in passage_ids
        },
        "policy": {
            "policy_id": "REGRESSION_ALL_PRIMARY",
            "allowed_trust": ["primary"],
        },
        "aggregation": {
            "state": "unresolved",
            "reason": "regression-invariance-only",
        },
    }


def weak_emit_receipt(
    trace: dict[str, Any],
    state: dict[str, Any],
    *,
    replay: Callable[[tuple[str, ...]], str] | None = None,
) -> dict[str, Any]:
    """Intentionally weak control.

    Defects are deliberate: trust is substituted for assessment state, missing
    state defaults silently, and deciding evidence is called necessary without
    an intervention.
    """
    source_facts = state.get("source_facts", {})
    assessments: dict[str, dict[str, str]] = {}
    participation: dict[str, str] = {}
    for passage_id, facts in source_facts.items():
        trust = facts.get("trust", "background")
        eligibility = "performed-positive" if trust == "primary" else "performed-adverse"
        assessments[passage_id] = {"eligibility": eligibility}
        participation[passage_id] = "deciding" if trust == "primary" else "excluded"

    deciding = sorted(pid for pid, role in participation.items() if role == "deciding")
    return {
        "trace": copy.deepcopy(trace),
        "receipt": {
            "semantic_measurement_hash": semantic_hash(trace),
            "production_verdict_hash": verdict_hash(trace),
            "execution": copy.deepcopy(
                state.get("execution", {"state": "completed", "failure": None})
            ),
            "assessments": assessments,
            "participation": participation,
            "policy": copy.deepcopy(
                state.get(
                    "policy",
                    {"policy_id": "DEFAULT_PRIMARY", "allowed_trust": ["primary"]},
                )
            ),
            "aggregation": copy.deepcopy(
                state.get(
                    "aggregation",
                    {"state": "unresolved", "reason": "defaulted"},
                )
            ),
            "causal_basis": {
                "form": "necessary",
                "passage_ids": deciding,
            },
        },
    }


def _gate(name: str, passed: bool, detail: Any) -> GateResult:
    return {"name": name, "pass": bool(passed), "detail": detail}


def evaluate_emitter(
    emit: Callable[..., dict[str, Any]],
    *,
    cases: dict[str, Any],
    verify_regression_files: bool,
) -> dict[str, Any]:
    trace = copy.deepcopy(cases["synthetic_trace"])
    state = copy.deepcopy(cases["participation_state"])
    gates: list[GateResult] = []

    # 1. Existing semantic measurements remain invariant and candidate reports
    # the evaluator-computed identity rather than a candidate-defined surrogate.
    baseline_semantic = semantic_hash(trace)
    baseline_trace_bytes = canonical_bytes(trace)
    metadata_state = copy.deepcopy(state)
    meta = cases["irrelevant_metadata"]
    metadata_state["source_facts"][meta["passage_id"]][meta["field"]] = meta["value"]
    try:
        out = emit(copy.deepcopy(trace), copy.deepcopy(state))
        out_meta = emit(copy.deepcopy(trace), metadata_state)
        gate1_pass = (
            canonical_bytes(out["trace"]) == baseline_trace_bytes
            and canonical_bytes(out_meta["trace"]) == baseline_trace_bytes
            and out["receipt"]["semantic_measurement_hash"] == baseline_semantic
            and out_meta["receipt"]["semantic_measurement_hash"] == baseline_semantic
        )
        gate1_detail = {
            "expected_semantic_hash": baseline_semantic,
            "baseline_reported": out["receipt"].get("semantic_measurement_hash"),
            "metadata_mutation_reported": out_meta["receipt"].get(
                "semantic_measurement_hash"
            ),
            "trace_unchanged": canonical_bytes(out["trace"]) == baseline_trace_bytes,
        }
    except Exception as exc:  # apparatus records failure rather than hiding it
        gate1_pass = False
        gate1_detail = {"error": f"{type(exc).__name__}: {exc}"}
    gates.append(_gate("measurement_stability", gate1_pass, gate1_detail))

    # 2. All frozen existing v1 traces are immutable through receipt production.
    regression_details: list[dict[str, Any]] = []
    gate2_pass = True
    if verify_regression_files:
        for item in cases["regression_traces"]:
            path = ROOT / item["path"]
            try:
                raw = path.read_bytes()
                observed_blob = git_blob_sha(raw)
                source_identity_ok = observed_blob == item["git_blob"]
                fixture_trace = json.loads(raw)
                before_verdict = verdict_hash(fixture_trace)
                before_semantic = semantic_hash(fixture_trace)
                result = emit(
                    copy.deepcopy(fixture_trace),
                    generic_state(fixture_trace),
                )
                trace_unchanged = canonical_bytes(result["trace"]) == canonical_bytes(
                    fixture_trace
                )
                verdict_unchanged = (
                    result["receipt"]["production_verdict_hash"] == before_verdict
                    and verdict_hash(result["trace"]) == before_verdict
                )
                semantic_unchanged = (
                    result["receipt"]["semantic_measurement_hash"] == before_semantic
                    and semantic_hash(result["trace"]) == before_semantic
                )
                row_pass = (
                    source_identity_ok
                    and trace_unchanged
                    and verdict_unchanged
                    and semantic_unchanged
                )
                gate2_pass = gate2_pass and row_pass
                regression_details.append(
                    {
                        "path": item["path"],
                        "expected_git_blob": item["git_blob"],
                        "observed_git_blob": observed_blob,
                        "semantic_hash": before_semantic,
                        "verdict_hash": before_verdict,
                        "pass": row_pass,
                    }
                )
            except Exception as exc:
                gate2_pass = False
                regression_details.append(
                    {
                        "path": item["path"],
                        "expected_git_blob": item["git_blob"],
                        "pass": False,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
    else:
        # Weak-control self-test deliberately omits repository fixture I/O.
        gate2_pass = True
        regression_details = [{"skipped": "weak-control self-test"}]
    gates.append(
        _gate(
            "production_verdict_and_trace_stability",
            gate2_pass,
            {
                "fixture_count": len(cases["regression_traces"]),
                "fixtures": regression_details,
            },
        )
    )

    # 3. Six assessment execution/value states must remain distinct.
    assessment_observed: list[str | None] = []
    assessment_errors: list[str] = []
    for value in cases["assessment_ladder"]:
        ladder_state = copy.deepcopy(state)
        ladder_state["assessments"]["e1"] = {"eligibility": value}
        try:
            result = emit(copy.deepcopy(trace), ladder_state)
            assessment_observed.append(
                result["receipt"]["assessments"]["e1"]["eligibility"]
            )
        except Exception as exc:
            assessment_observed.append(None)
            assessment_errors.append(f"{value}: {type(exc).__name__}: {exc}")
    gate3_pass = (
        assessment_observed == cases["assessment_ladder"]
        and len(set(assessment_observed)) == len(cases["assessment_ladder"])
    )
    gates.append(
        _gate(
            "assessment_ladder",
            gate3_pass,
            {"expected": cases["assessment_ladder"], "observed": assessment_observed,
             "errors": assessment_errors},
        )
    )

    # 4. Participation family under frozen policy semantics.
    expected_participation = {
        "e1": "deciding",
        "e2": "residual",
        "e3": "excluded",
        "e4": "unresolved",
    }
    try:
        result = emit(copy.deepcopy(trace), copy.deepcopy(state))
        observed_participation = result["receipt"]["participation"]
        gate4_pass = observed_participation == expected_participation
        gate4_detail = {
            "expected": expected_participation,
            "observed": observed_participation,
        }
    except Exception as exc:
        gate4_pass = False
        gate4_detail = {"error": f"{type(exc).__name__}: {exc}"}
    gates.append(
        _gate("participation_reconstruction", gate4_pass, gate4_detail)
    )

    # 5. Named-policy counterfactual with evidence/measurement held fixed.
    try:
        baseline_state = copy.deepcopy(state)
        counter_state = copy.deepcopy(state)
        baseline_state["policy"] = copy.deepcopy(
            cases["policy_counterfactual"]["baseline"]
        )
        counter_state["policy"] = copy.deepcopy(
            cases["policy_counterfactual"]["counterfactual"]
        )
        baseline_out = emit(copy.deepcopy(trace), baseline_state)
        counter_out = emit(copy.deepcopy(trace), counter_state)
        target = cases["policy_counterfactual"]["target_passage"]
        gate5_pass = (
            baseline_out["receipt"]["semantic_measurement_hash"]
            == counter_out["receipt"]["semantic_measurement_hash"]
            == baseline_semantic
            and baseline_out["receipt"]["participation"][target] == "deciding"
            and counter_out["receipt"]["participation"][target] == "residual"
            and baseline_out["receipt"]["policy"]["policy_id"]
            != counter_out["receipt"]["policy"]["policy_id"]
        )
        gate5_detail = {
            "semantic_hash": baseline_semantic,
            "target": target,
            "baseline_participation": baseline_out["receipt"]["participation"].get(
                target
            ),
            "counterfactual_participation": counter_out["receipt"][
                "participation"
            ].get(target),
            "baseline_policy": baseline_out["receipt"]["policy"],
            "counterfactual_policy": counter_out["receipt"]["policy"],
        }
    except Exception as exc:
        gate5_pass = False
        gate5_detail = {"error": f"{type(exc).__name__}: {exc}"}
    gates.append(_gate("policy_counterfactual", gate5_pass, gate5_detail))

    # 6. Outer execution failure remains orthogonal to subject-matter verdict.
    try:
        completed_state = copy.deepcopy(state)
        failed_state = copy.deepcopy(state)
        completed_state["execution"] = copy.deepcopy(
            cases["execution_cases"]["completed"]
        )
        failed_state["execution"] = copy.deepcopy(cases["execution_cases"]["failed"])
        completed_out = emit(copy.deepcopy(trace), completed_state)
        failed_out = emit(copy.deepcopy(trace), failed_state)
        gate6_pass = (
            completed_out["trace"]["verdict"] == failed_out["trace"]["verdict"]
            and completed_out["receipt"]["execution"]
            == cases["execution_cases"]["completed"]
            and failed_out["receipt"]["execution"] == cases["execution_cases"]["failed"]
            and completed_out["receipt"]["execution"]
            != failed_out["receipt"]["execution"]
        )
        gate6_detail = {
            "production_verdict": trace["verdict"],
            "completed_execution": completed_out["receipt"]["execution"],
            "failed_execution": failed_out["receipt"]["execution"],
        }
    except Exception as exc:
        gate6_pass = False
        gate6_detail = {"error": f"{type(exc).__name__}: {exc}"}
    gates.append(_gate("execution_failure_distinction", gate6_pass, gate6_detail))

    # 7. Distributed evidence remains unresolved absent composition semantics.
    try:
        unresolved_state = copy.deepcopy(state)
        unresolved_state["aggregation"] = {
            "state": "unresolved",
            "reason": "composition-absent",
        }
        unresolved_out = emit(copy.deepcopy(trace), unresolved_state)
        aggregation = unresolved_out["receipt"]["aggregation"]
        gate7_pass = (
            aggregation
            == {"state": "unresolved", "reason": "composition-absent"}
            and "composed" not in aggregation
            and "composition_result" not in aggregation
        )
        gate7_detail = {"aggregation": aggregation}
    except Exception as exc:
        gate7_pass = False
        gate7_detail = {"error": f"{type(exc).__name__}: {exc}"}
    gates.append(_gate("unresolved_distributed_evidence", gate7_pass, gate7_detail))

    # 8. Exact causal necessity only when removal replay changes terminal result.
    target = cases["causal_case"]["target_passage"]

    def causal_replay(active_ids: tuple[str, ...]) -> str:
        return (
            cases["causal_case"]["baseline_terminal"]
            if target in active_ids
            else cases["causal_case"]["removed_terminal"]
        )

    try:
        causal_state = copy.deepcopy(state)
        causal_state["policy"] = copy.deepcopy(
            cases["policy_counterfactual"]["baseline"]
        )
        with_replay = emit(copy.deepcopy(trace), causal_state, replay=causal_replay)
        without_replay = emit(copy.deepcopy(trace), causal_state)
        causal = with_replay["receipt"]["causal_basis"]
        unavailable = without_replay["receipt"]["causal_basis"]
        gate8_pass = (
            causal.get("form") == "necessary"
            and causal.get("passage_ids") == [target]
            and causal.get("baseline_terminal")
            == cases["causal_case"]["baseline_terminal"]
            and unavailable == {"form": "unavailable", "passage_ids": []}
        )
        gate8_detail = {
            "with_replay": causal,
            "without_replay": unavailable,
        }
    except Exception as exc:
        gate8_pass = False
        gate8_detail = {"error": f"{type(exc).__name__}: {exc}"}
    gates.append(_gate("replay_derived_causal_basis", gate8_pass, gate8_detail))

    # 9. Metadata explicitly irrelevant to the receipt semantics is inert.
    try:
        base_out = emit(copy.deepcopy(trace), copy.deepcopy(state))
        mutated_state = copy.deepcopy(state)
        meta = cases["irrelevant_metadata"]
        mutated_state["source_facts"][meta["passage_id"]][meta["field"]] = meta[
            "value"
        ]
        mutated_out = emit(copy.deepcopy(trace), mutated_state)
        gate9_pass = (
            base_out["receipt"]["semantic_measurement_hash"]
            == mutated_out["receipt"]["semantic_measurement_hash"]
            and base_out["receipt"]["assessments"]
            == mutated_out["receipt"]["assessments"]
            and base_out["receipt"]["participation"]
            == mutated_out["receipt"]["participation"]
        )
        gate9_detail = {
            "mutated_field": f'{meta["passage_id"]}.{meta["field"]}',
            "semantic_hash": base_out["receipt"]["semantic_measurement_hash"],
            "participation_unchanged": base_out["receipt"]["participation"]
            == mutated_out["receipt"]["participation"],
        }
    except Exception as exc:
        gate9_pass = False
        gate9_detail = {"error": f"{type(exc).__name__}: {exc}"}
    gates.append(_gate("irrelevant_metadata_invariance", gate9_pass, gate9_detail))

    # 10. Required receipt input fails closed rather than defaulting.
    missing_results: dict[str, bool] = {}
    missing_errors: dict[str, str] = {}
    for key in cases["required_top_level_state"]:
        incomplete = copy.deepcopy(state)
        incomplete.pop(key, None)
        try:
            emit(copy.deepcopy(trace), incomplete)
            missing_results[key] = False
        except Exception as exc:
            missing_results[key] = True
            missing_errors[key] = f"{type(exc).__name__}: {exc}"
    gate10_pass = all(missing_results.values())
    gates.append(
        _gate(
            "missing_required_state_fails_closed",
            gate10_pass,
            {"raised": missing_results, "errors": missing_errors},
        )
    )

    failed = [gate["name"] for gate in gates if not gate["pass"]]
    return {
        "all_pass": not failed,
        "passed_count": sum(1 for gate in gates if gate["pass"]),
        "gate_count": len(gates),
        "failed_gates": failed,
        "gates": gates,
    }


def evaluate_all(*, candidate_path: Path = CANDIDATE_PATH) -> dict[str, Any]:
    cases = load_cases()
    weak = evaluate_emitter(
        weak_emit_receipt,
        cases=cases,
        verify_regression_files=False,
    )
    candidate = load_candidate(candidate_path)
    candidate_result = evaluate_emitter(
        candidate.emit_receipt,
        cases=cases,
        verify_regression_files=True,
    )
    return {
        "production_baseline": cases["production_baseline"],
        "candidate_path": str(candidate_path.relative_to(ROOT)),
        "weak_control": weak,
        "candidate": candidate_result,
        "acceptance": bool(candidate_result["all_pass"] and not weak["all_pass"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test-weak", action="store_true")
    args = parser.parse_args()

    cases = load_cases()
    if args.self_test_weak:
        result = evaluate_emitter(
            weak_emit_receipt,
            cases=cases,
            verify_regression_files=False,
        )
        payload = {
            "weak_control": result,
            "self_test_pass": not result["all_pass"],
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(
                f"weak control rejected={not result['all_pass']} "
                f"failed={','.join(result['failed_gates'])}"
            )
        return 0 if payload["self_test_pass"] else 1

    payload = evaluate_all()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"candidate={payload['candidate']['all_pass']} "
            f"weak_rejected={not payload['weak_control']['all_pass']} "
            f"acceptance={payload['acceptance']}"
        )
    return 0 if payload["acceptance"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
