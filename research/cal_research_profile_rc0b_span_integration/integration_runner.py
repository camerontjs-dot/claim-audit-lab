"""Frozen RC0B integration evaluator for the RC0A entity-span resolver."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RC0_DIR = ROOT / "research" / "cal_research_profile_rc0"
RC0A_DIR = ROOT / "research" / "cal_research_profile_rc0a_span_anchoring"

sys.path.insert(0, str(RC0_DIR))
import runtime as rc0  # type: ignore  # exact frozen research module
import smoke_runner as smoke  # type: ignore  # exact frozen post-profile apparatus
sys.path.insert(0, str(RC0A_DIR))
from span_anchor import unique_lexical_span, weak_first_lexical_span  # type: ignore

from integration_adapter import complete_atom_with_entity_resolver, execute_with_entity_resolver

CASES_PATH = HERE / "CASES.json"
ATOM_KEY = b"rc0b-atom-key-material-at-least-32-bytes"
PROP_KEY = b"rc0b-prop-key-material-at-least-32-bytes"
ATOM_KEY_ID = "rc0b-atom-key"
PROP_KEY_ID = "rc0b-prop-key"
SEMANTIC_SHA = "ad9e47a2102202450238bf780eb69c4b01a7cd3d"


def _load_cases() -> dict[str, Any]:
    value = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("RC0B cohort must be an object")
    return value


def _evidence(case: dict[str, Any]) -> Any:
    ev = case["evidence"][0]
    return rc0.EvidenceInput(
        source_id=ev["source_id"],
        bundle_id="cal-rc0-naturalistic-smoke-bundle-v1",
        passage_id=ev["passage_id"],
        passage_text=ev["text"],
        passage_sha256=smoke.passage_hash(ev["text"]),
        semantic_family="strict_comparison",
        metadata={"rc0b_case_id": case["id"]},
    )


def _proposition(case: dict[str, Any]) -> Any:
    claim = case["claim"]
    return rc0.BoundProposition(
        claim_id=claim["claim_id"],
        claim_text=claim["text"],
        family="strict_comparison",
        lhs_entity=claim["lhs_entity"],
        rhs_entity=claim["rhs_entity"],
        comparison_direction=claim["comparison_direction"],
    )


def _execute_case(
    case: dict[str, Any],
    *,
    resolver: Any,
    measure_fn: Any,
    authority_evaluator: Any,
    b_binding: dict[str, str],
) -> dict[str, Any]:
    return execute_with_entity_resolver(
        rc0,
        resolver,
        proposition=_proposition(case),
        admitted_evidence=[_evidence(case)],
        contract_b_validation={
            "contract_version": "1.2.0",
            "authority_commit": "c314e53bd91c0736aa4370a364673b069aceb43e",
            "status": "PASS",
        },
        contract_b_binding=b_binding,
        measure_fn=measure_fn,
        authority_evaluator=authority_evaluator,
        atom_key=ATOM_KEY,
        atom_key_id=ATOM_KEY_ID,
        proposition_key=PROP_KEY,
        proposition_key_id=PROP_KEY_ID,
        semantic_implementation_sha=SEMANTIC_SHA,
        baseline_diagnostic={"status": "NOT_RUN", "causal_influence": False},
    )


def _relation(candidate: dict[str, Any]) -> str:
    stages = candidate.get("stages") or []
    if not stages:
        return "UNRESOLVED"
    obj = stages[0].get("categorical_relation")
    return str(obj.get("relation")) if isinstance(obj, dict) else "UNRESOLVED"


def _candidate_rows(
    cohort: dict[str, Any],
    *,
    measure_fn: Any,
    authority_evaluator: Any,
    b_binding: dict[str, str],
    apparatus_c: Path,
    index_path: Path,
    out_root: Path,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    rows: list[dict[str, Any]] = []
    unsafe: list[str] = []
    mismatches: list[str] = []
    c_dir = out_root / "contract-c"
    c_dir.mkdir(parents=True, exist_ok=True)

    for case in cohort["cases"]:
        candidate = _execute_case(
            case,
            resolver=unique_lexical_span,
            measure_fn=measure_fn,
            authority_evaluator=authority_evaluator,
            b_binding=b_binding,
        )
        relation = _relation(candidate)
        conclusion = candidate["internal_cal_conclusion"]
        c_projection = candidate["contract_c_projection"]
        c_path = c_dir / f"{case['id']}.json"
        c_path.write_text(candidate["contract_c_bytes"], encoding="utf-8")
        c_validation = smoke.validate_contract_c(c_path, index_path, apparatus_c)

        actual = {
            "relation": relation,
            "disposition": conclusion.get("disposition"),
            "verdict": conclusion.get("verdict"),
            "c_verdict": c_projection.get("contract_c_reported_verdict"),
            "failure_category": (candidate.get("stages") or [{}])[0].get("failure_category"),
        }
        expected = {
            "relation": case["expected_relation"],
            "disposition": case["expected_disposition"],
            "verdict": case["expected_verdict"],
            "c_verdict": case["expected_c_verdict"],
        }
        exact = actual["relation"] == expected["relation"] and actual["disposition"] == expected["disposition"] \
            and actual["verdict"] == expected["verdict"] and actual["c_verdict"] == expected["c_verdict"] \
            and c_validation["status"] == "PASS" \
            and candidate.get("baseline_only", {}).get("causal_influence") is False

        if not exact:
            mismatches.append(case["id"])
        if expected["relation"] in {"UNRESOLVED", "IRRELEVANT"} and relation in {"SUPPORTS", "REFUTES"}:
            unsafe.append(case["id"])
        if expected["relation"] == "SUPPORTS" and relation == "REFUTES":
            unsafe.append(case["id"])
        if expected["relation"] == "REFUTES" and relation == "SUPPORTS":
            unsafe.append(case["id"])
        if conclusion.get("disposition") == "abstained" and c_projection.get("contract_c_reported_verdict") != "not_checkable":
            unsafe.append(case["id"])

        stage = (candidate.get("stages") or [{}])[0]
        typed_atom = stage.get("typed_atom")
        rows.append({
            "id": case["id"],
            "expected": expected,
            "actual": actual,
            "measurement_status": (stage.get("measurement") or {}).get("status"),
            "typed_atom": typed_atom,
            "warrant_status": stage.get("warrant_status"),
            "contract_c_validation": c_validation["status"],
            "baseline_causal_influence": candidate.get("baseline_only", {}).get("causal_influence"),
            "exact": exact,
        })
    return rows, sorted(set(unsafe)), mismatches


def _weak_role_control(case: dict[str, Any], *, measure_fn: Any, authority_evaluator: Any, b_binding: dict[str, str]) -> dict[str, Any]:
    weak = _execute_case(
        case,
        resolver=weak_first_lexical_span,
        measure_fn=measure_fn,
        authority_evaluator=authority_evaluator,
        b_binding=b_binding,
    )
    candidate = _execute_case(
        case,
        resolver=unique_lexical_span,
        measure_fn=measure_fn,
        authority_evaluator=authority_evaluator,
        b_binding=b_binding,
    )
    weak_stage = weak["stages"][0]
    weak_atom = weak_stage.get("typed_atom") or {}
    lhs_span = weak_atom.get("lhs_span")
    rhs_span = weak_atom.get("rhs_span")
    overlap = bool(
        isinstance(lhs_span, list)
        and isinstance(rhs_span, list)
        and lhs_span[0] <= rhs_span[0] < lhs_span[1]
    )
    result = {
        "weak_lhs_span": lhs_span,
        "weak_rhs_span": rhs_span,
        "weak_spans_overlap": overlap,
        "weak_warrant_status": weak_stage.get("warrant_status"),
        "weak_relation": _relation(weak),
        "weak_conclusion": weak["internal_cal_conclusion"],
        "candidate_relation": _relation(candidate),
        "candidate_conclusion": candidate["internal_cal_conclusion"],
    }
    result["control_valid"] = (
        lhs_span == [0, 8]
        and rhs_span == [4, 8]
        and overlap
        and (weak_stage.get("warrant_status") or {}).get("authority_status") == "WARRANTED"
        and _relation(weak) == "SUPPORTS"
        and weak["internal_cal_conclusion"].get("disposition") == "decided"
        and _relation(candidate) == "UNRESOLVED"
        and candidate["internal_cal_conclusion"].get("disposition") == "abstained"
    )
    return result


def _receipt_binding_control(case: dict[str, Any], *, measure_fn: Any, authority_evaluator: Any) -> dict[str, Any]:
    evidence = _evidence(case)
    proposition = _proposition(case)
    measurement = measure_fn(evidence.passage_text)
    atom, state = complete_atom_with_entity_resolver(
        rc0,
        unique_lexical_span,
        claim_id=proposition.claim_id,
        evidence=evidence,
        measurement=measurement,
    )
    if atom is None:
        return {"control_valid": False, "setup_state": state}
    authority_case = rc0.build_rc8j_case(atom=atom, evidence=evidence)
    observed = authority_evaluator(deepcopy(authority_case))
    receipt = rc0.issue_atom_warrant(
        case=authority_case,
        authority_evaluator=authority_evaluator,
        key=ATOM_KEY,
        key_id=ATOM_KEY_ID,
    )
    mutated = deepcopy(authority_case)
    mutated["field_warrants"]["rhs_entity"]["span"] = [2, 5]
    mutated_rc8j = authority_evaluator(deepcopy(mutated))
    stale_refused = False
    refusal_code = None
    try:
        rc0.verify_atom_warrant(case=mutated, receipt=receipt, trusted_keys={ATOM_KEY_ID: ATOM_KEY})
    except rc0.RC0Refusal as exc:
        stale_refused = True
        refusal_code = exc.code
    result = {
        "setup_state": state,
        "base_rc8j": observed,
        "mutated_wrong_span": [2, 5],
        "mutated_rc8j": mutated_rc8j,
        "stale_warrant_refused": stale_refused,
        "stale_warrant_refusal_code": refusal_code,
    }
    result["control_valid"] = (
        observed.get("authority_status") == "WARRANTED"
        and mutated_rc8j.get("authority_status") == "WARRANTED"
        and stale_refused
        and refusal_code == "ATOM_BINDING_FAILURE"
    )
    return result


def execute(args: argparse.Namespace) -> dict[str, Any]:
    cohort = _load_cases()
    out_root = args.out.parent
    out_root.mkdir(parents=True, exist_ok=True)

    measure_fn = smoke.load_measure(args.rc7fb1_root)
    authority_evaluator = smoke.load_rc8j(args.rc8j_root)

    gold_stub = {"gold_id": "cal-rc0b-span-integration-gold-v1"}
    bundle, b_binding, b_index = smoke.build_contract_b_bundle(cohort, gold_stub, out_root)
    b_validation = smoke.validate_contract_b(bundle, args.apparatus_b)
    index_path = out_root / "CONTRACT-B-INDEX.json"
    index_path.write_bytes(rc0.canonical_json_bytes(b_index, trailing_newline=True))

    if b_validation["status"] != "PASS":
        result = {
            "experiment": "cal-rc0b-span-integration",
            "research_disposition": "APPARATUS_FAILURE",
            "contract_b_validation": b_validation,
            "production_promotion_authorized": False,
        }
        args.out.write_bytes(rc0.canonical_json_bytes(result, trailing_newline=True))
        return result

    rows, unsafe, mismatches = _candidate_rows(
        cohort,
        measure_fn=measure_fn,
        authority_evaluator=authority_evaluator,
        b_binding=b_binding,
        apparatus_c=args.apparatus_c,
        index_path=index_path,
        out_root=out_root,
    )
    weak_case = next(case for case in cohort["cases"] if case["id"] == "RC0B-09-NEW-YORK-YORK-AMBIGUOUS")
    weak_control = _weak_role_control(
        weak_case,
        measure_fn=measure_fn,
        authority_evaluator=authority_evaluator,
        b_binding=b_binding,
    )
    receipt_case = next(case for case in cohort["cases"] if case["id"] == "RC0B-01-WOMEN-MEN-REFUTE")
    receipt_control = _receipt_binding_control(
        receipt_case,
        measure_fn=measure_fn,
        authority_evaluator=authority_evaluator,
    )

    exact_count = sum(1 for row in rows if row["exact"])
    all_c_pass = all(row["contract_c_validation"] == "PASS" for row in rows)
    supported = (
        exact_count == cohort["case_count"]
        and not unsafe
        and not mismatches
        and all_c_pass
        and weak_control.get("control_valid") is True
        and receipt_control.get("control_valid") is True
    )
    result = {
        "experiment": "cal-rc0b-span-integration",
        "parent_rc0_head": "8c52a00b93c7c33c159a484c47944faf9d97f7f1",
        "rc0a_head": "9baa981d9e5209c08911b992effbce5c59604884",
        "cohort_id": cohort["cohort_id"],
        "case_count": cohort["case_count"],
        "exact_count": exact_count,
        "mismatch_ids": mismatches,
        "unsafe_candidate_ids": unsafe,
        "contract_b_validation": b_validation,
        "all_contract_c_valid": all_c_pass,
        "candidate_cases": rows,
        "weak_role_misattachment_control": weak_control,
        "stale_span_receipt_control": receipt_control,
        "baseline_causal_influence": False,
        "next_step_authorized": "RC0C_FRESH_NATURALISTIC_SPAN_TRANSFER" if supported else None,
        "production_promotion_authorized": False,
        "research_disposition": "SUPPORTED_WITH_BOUNDS" if supported else "FALSIFIED_OR_INCONCLUSIVE",
    }
    args.out.write_bytes(rc0.canonical_json_bytes(result, trailing_newline=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rc7fb1-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--apparatus-b", type=Path, required=True)
    parser.add_argument("--apparatus-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result.get("research_disposition") == "APPARATUS_FAILURE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
