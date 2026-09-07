"""Small preregistered seam/falsifier suite for CAL Research Profile RC0."""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Callable

from runtime import (
    BoundProposition,
    EvidenceInput,
    PROFILE_SEMANTIC_FAMILY,
    RC0Refusal,
    RelationRecord,
    build_rc8j_case,
    canonical_json_bytes,
    complete_strict_comparison_atom,
    compose_categorical_relations,
    execute_rc0_case,
    issue_atom_warrant,
    issue_proposition_binding,
    proposition_projection,
    sha256_hex,
    stable_id,
    verify_atom_warrant,
    verify_proposition_binding,
)

ATOM_KEY = b"rc0-atom-binding-test-key-32-bytes!!"
PROP_KEY = b"rc0-proposition-test-key-32-bytes!!"
ATOM_KEY_ID = "rc0-atom-test-key"
PROP_KEY_ID = "rc0-prop-test-key"
IMPLEMENTATION_SHA_FOR_PREREVEAL = "1" * 40
B_VALIDATION = {
    "contract_version": "1.2.0",
    "authority_commit": "c314e53bd91c0736aa4370a364673b069aceb43e",
    "status": "PASS",
}
B_BINDING = {
    "contract_version": "1.2.0",
    "bundle_id": "rc0-seam-suite-bundle",
    "bundle_hash": "sha256:" + "a" * 64,
}


def _load_measure(root: Path) -> Callable[[str], dict[str, Any]]:
    path = root / "research" / "comparative_relation_measurement_rc7fb1" / "comparator.py"
    spec = importlib.util.spec_from_file_location("rc7fb1_exact", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load RC7F-B1 from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.measure


def _load_rc8j(root: Path) -> Callable[[dict[str, Any]], dict[str, Any]]:
    sys.path.insert(0, str(root))
    try:
        from research.semantic_authority_machinery_rc8.authority_contract_rc8j import assess_authority
    finally:
        sys.path.pop(0)
    return assess_authority


def _prop(
    *,
    claim_id: str = "clm-seam",
    claim_text: str = "North Plant produced more units than South Plant.",
    lhs: str = "north plant",
    rhs: str = "south plant",
    direction: str = "greater_than",
) -> BoundProposition:
    return BoundProposition(
        claim_id=claim_id,
        claim_text=claim_text,
        family=PROFILE_SEMANTIC_FAMILY,
        lhs_entity=lhs,
        rhs_entity=rhs,
        comparison_direction=direction,
    )


def _evidence(
    text: str,
    *,
    passage_id: str = "pass-seam",
    semantic_family: str = PROFILE_SEMANTIC_FAMILY,
    metadata: dict[str, Any] | None = None,
) -> EvidenceInput:
    return EvidenceInput(
        source_id="src-seam",
        bundle_id=B_BINDING["bundle_id"],
        passage_id=passage_id,
        passage_text=text,
        passage_sha256="sha256:" + sha256_hex(text.encode("utf-8")),
        semantic_family=semantic_family,
        metadata=metadata,
    )


def _run(
    proposition: BoundProposition,
    evidence: list[EvidenceInput],
    measure: Callable[[str], dict[str, Any]],
    rc8j: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    return execute_rc0_case(
        proposition=proposition,
        admitted_evidence=evidence,
        contract_b_validation=B_VALIDATION,
        contract_b_binding=B_BINDING,
        measure_fn=measure,
        authority_evaluator=rc8j,
        atom_key=ATOM_KEY,
        atom_key_id=ATOM_KEY_ID,
        proposition_key=PROP_KEY,
        proposition_key_id=PROP_KEY_ID,
        semantic_implementation_sha=IMPLEMENTATION_SHA_FOR_PREREVEAL,
    )


def _manual_relation(proposition: BoundProposition, relation: str, suffix: str) -> RelationRecord:
    warranted = relation != "UNRESOLVED"
    return RelationRecord(
        relation_id=stable_id("relation", {"suffix": suffix, "relation": relation}),
        claim_id=proposition.claim_id,
        atom_id=(stable_id("atom", suffix) if warranted else None),
        relation=relation,
        warranted=warranted,
        reason=f"seam matrix {relation}",
        evidence_ref={
            "source_id": "src-seam",
            "passage_id": f"pass-{suffix}",
            "passage_sha256": "sha256:" + sha256_hex(suffix.encode("utf-8")),
        },
        proposition_projection=proposition_projection(proposition),
    )


def _result(case_id: str, passed: bool, observation: Any, falsifier: str) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "passed": bool(passed),
        "falsifier_if_failed": falsifier,
        "observation": observation,
    }


def execute_suite(
    measure: Callable[[str], dict[str, Any]],
    rc8j: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    proposition = _prop()
    direct = _evidence("North Plant exceeded South Plant by 12 units.")

    measurement = measure(direct.passage_text)
    atom, state = complete_strict_comparison_atom(
        claim_id=proposition.claim_id, evidence=direct, measurement=measurement
    )
    assert atom is not None, state
    case = build_rc8j_case(atom=atom, evidence=direct)
    warrant = issue_atom_warrant(
        case=case, authority_evaluator=rc8j, key=ATOM_KEY, key_id=ATOM_KEY_ID
    )
    changed = deepcopy(case)
    changed["proposal"]["fields"]["comparison_direction"] = "less_than"
    changed["field_warrants"]["comparison_direction"]["value"] = "less_than"
    try:
        verify_atom_warrant(case=changed, receipt=warrant, trusted_keys={ATOM_KEY_ID: ATOM_KEY})
        stale_rejected = False
        detail = "accepted"
    except RC0Refusal as exc:
        stale_rejected = exc.code == "ATOM_BINDING_FAILURE"
        detail = f"{exc.code}:{exc.detail}"
    rows.append(_result("STALE-WARRANT-CHANGED-ATOM", stale_rejected, detail, "stale/changed atom accepted"))

    prop_receipt = issue_proposition_binding(
        proposition=proposition, key=PROP_KEY, key_id=PROP_KEY_ID
    )
    changed_prop = _prop(direction="less_than")
    try:
        verify_proposition_binding(
            proposition=changed_prop, receipt=prop_receipt, trusted_keys={PROP_KEY_ID: PROP_KEY}
        )
        prop_rejected = False
        detail = "accepted"
    except RC0Refusal as exc:
        prop_rejected = exc.code == "PROPOSITION_BINDING_FAILURE"
        detail = f"{exc.code}:{exc.detail}"
    rows.append(_result("VALID-ATOM-RECEIPT-CHANGED-PROPOSITION", prop_rejected, detail,
                        "typed proposition substitution accepted"))

    changed_text_prop = _prop(claim_text="North Plant definitely outproduced South Plant.")
    try:
        verify_proposition_binding(
            proposition=changed_text_prop, receipt=prop_receipt, trusted_keys={PROP_KEY_ID: PROP_KEY}
        )
        text_rejected = False
        detail = "accepted"
    except RC0Refusal as exc:
        text_rejected = exc.code == "PROPOSITION_BINDING_FAILURE"
        detail = f"{exc.code}:{exc.detail}"
    rows.append(_result("SAME-ID-CHANGED-CLAIM-CONTENT", text_rejected, detail,
                        "same-id claim-text substitution accepted"))

    reversed_run = _run(
        proposition,
        [_evidence("North Plant trailed South Plant by 12 units.", passage_id="pass-reversal")],
        measure,
        rc8j,
    )
    reversal_relation = reversed_run["stages"][0]["categorical_relation"]["relation"]
    rows.append(_result(
        "COMPARISON-DIRECTION-REVERSAL",
        reversal_relation == "REFUTES" and reversed_run["internal_cal_conclusion"]["verdict"] == "contradicted",
        {"relation": reversal_relation, "conclusion": reversed_run["internal_cal_conclusion"]},
        "direction reversal did not refute",
    ))

    changed_entity = deepcopy(case)
    changed_entity["proposal"]["fields"]["lhs_entity"] = "east plant"
    changed_entity["field_warrants"]["lhs_entity"]["value"] = "east plant"
    try:
        verify_atom_warrant(case=changed_entity, receipt=warrant, trusted_keys={ATOM_KEY_ID: ATOM_KEY})
        entity_rejected = False
        detail = "accepted"
    except RC0Refusal as exc:
        entity_rejected = exc.code == "ATOM_BINDING_FAILURE"
        detail = f"{exc.code}:{exc.detail}"
    rows.append(_result("ENTITY-ROLE-SUBSTITUTION", entity_rejected, detail,
                        "entity substitution accepted under prior warrant"))

    nonwarranted = deepcopy(case)
    nonwarranted["field_warrants"]["lhs_entity"]["status"] = "insufficient_authority"
    observed = rc8j(deepcopy(nonwarranted))
    try:
        issue_atom_warrant(case=nonwarranted, authority_evaluator=rc8j, key=ATOM_KEY, key_id=ATOM_KEY_ID)
        issuance_refused = False
    except RC0Refusal as exc:
        issuance_refused = exc.code == "WARRANT_UNRESOLVED"
    rows.append(_result(
        "NON-WARRANTED-ATOM-PARTICIPATION",
        observed.get("authority_status") != "WARRANTED" and issuance_refused,
        {"authority": observed, "warrant_issued": not issuance_refused},
        "non-warranted atom gained participation authority",
    ))

    unsupported = _run(
        proposition,
        [_evidence("North Plant exceeded South Plant by 12 units.", passage_id="pass-unsupported",
                   semantic_family="assertion_scope")],
        measure,
        rc8j,
    )
    rows.append(_result(
        "UNSUPPORTED-SEMANTIC-FAMILY",
        unsupported["internal_cal_conclusion"]["disposition"] == "abstained"
        and unsupported["stages"][0]["failure_category"] == "SAFE_ABSTENTION"
        and unsupported["baseline_only"]["causal_influence"] is False,
        {"conclusion": unsupported["internal_cal_conclusion"],
         "failure_category": unsupported["stages"][0]["failure_category"],
         "baseline": unsupported["baseline_only"]},
        "unsupported family influenced terminal conclusion",
    ))

    s = _manual_relation(proposition, "SUPPORTS", "s")
    r = _manual_relation(proposition, "REFUTES", "r")
    i = _manual_relation(proposition, "IRRELEVANT", "i")
    u = _manual_relation(proposition, "UNRESOLVED", "u")
    matrix = {
        "support_only": asdict(compose_categorical_relations(proposition=proposition, relations=[s])),
        "refutation_only": asdict(compose_categorical_relations(proposition=proposition, relations=[r])),
        "irrelevant_only": asdict(compose_categorical_relations(proposition=proposition, relations=[i])),
        "unresolved_only": asdict(compose_categorical_relations(proposition=proposition, relations=[u])),
        "support_irrelevant": asdict(compose_categorical_relations(proposition=proposition, relations=[s, i])),
        "support_unresolved": asdict(compose_categorical_relations(proposition=proposition, relations=[s, u])),
        "support_refutation": asdict(compose_categorical_relations(proposition=proposition, relations=[s, r])),
        "incomplete_required": asdict(compose_categorical_relations(
            proposition=proposition, relations=[s], required_relation_count=2
        )),
    }
    matrix_pass = (
        matrix["support_only"]["verdict"] == "supported"
        and matrix["refutation_only"]["verdict"] == "contradicted"
        and matrix["irrelevant_only"]["disposition"] == "abstained"
        and matrix["unresolved_only"]["reason_code"] == "unresolved_categorical_relation"
        and matrix["support_irrelevant"]["verdict"] == "supported"
        and matrix["support_unresolved"]["disposition"] == "abstained"
        and matrix["support_refutation"]["reason_code"] == "mixed_categorical_relations"
        and matrix["incomplete_required"]["reason_code"] == "incomplete_required_composition"
    )
    rows.append(_result("SCORELESS-COMPOSITION-MATRIX", matrix_pass, matrix,
                        "categorical composer violated frozen fail-closed matrix"))

    low = _run(proposition, [_evidence(direct.passage_text, passage_id="pass-confidence",
                                       metadata={"confidence": 0.01, "score": 0.01})], measure, rc8j)
    high = _run(proposition, [_evidence(direct.passage_text, passage_id="pass-confidence",
                                        metadata={"confidence": 0.99, "score": 999.0})], measure, rc8j)
    rows.append(_result(
        "CONFIDENCE-SCORE-PERTURBATION",
        low["internal_cal_conclusion"] == high["internal_cal_conclusion"],
        {"low": low["internal_cal_conclusion"], "high": high["internal_cal_conclusion"]},
        "confidence/score perturbation changed terminal relation",
    ))

    one = _run(proposition, [_evidence(direct.passage_text, passage_id="pass-readers",
                                       metadata={"reader_count": 1, "agreement_count": 1})], measure, rc8j)
    many = _run(proposition, [_evidence(direct.passage_text, passage_id="pass-readers",
                                        metadata={"reader_count": 101, "agreement_count": 101})], measure, rc8j)
    rows.append(_result(
        "READER-AGREEMENT-COUNT-PERTURBATION",
        one["internal_cal_conclusion"] == many["internal_cal_conclusion"],
        {"one": one["internal_cal_conclusion"], "many": many["internal_cal_conclusion"]},
        "reader/agreement count changed terminal relation",
    ))

    qualifier = _run(
        proposition,
        [_evidence("The preliminary estimate suggested North Plant may have exceeded South Plant by 12 units, pending reconciliation.",
                   passage_id="pass-qualifier")],
        measure,
        rc8j,
    )
    c_obj = json.loads(qualifier["contract_c_bytes"])
    c_conclusion = c_obj["propositions"][0]["conclusion"]
    rows.append(_result(
        "CONTRACT-C-NO-STRENGTHENING",
        qualifier["internal_cal_conclusion"]["disposition"] == "abstained"
        and c_obj["propositions"][0]["execution"]["completion"] == "not_checkable"
        and c_conclusion["reported_verdict"] == "not_checkable",
        {"internal": qualifier["internal_cal_conclusion"], "contract_c": c_conclusion},
        "Contract C strengthened internal abstention",
    ))

    incomplete = _run(
        proposition,
        [_evidence("North Plant exceeded South Plant by four units.", passage_id="pass-incomplete",
                   metadata={"confidence": 1.0, "reader_count": 1000, "agreement_count": 1000})],
        measure,
        rc8j,
    )
    rows.append(_result(
        "INCOMPLETE-ATOM-NO-SCORE-REPAIR",
        incomplete["stages"][0]["failure_category"] in {"ATOM_INCOMPLETE", "MEASUREMENT_MISS_SAFE"}
        and incomplete["internal_cal_conclusion"]["disposition"] == "abstained",
        {"measurement": incomplete["stages"][0]["measurement"],
         "failure_category": incomplete["stages"][0]["failure_category"],
         "conclusion": incomplete["internal_cal_conclusion"]},
        "incomplete atom became deciding through non-authority metadata",
    ))

    unsafe = [row for row in rows if not row["passed"]]
    return {
        "suite_id": "cal-research-profile-rc0-seam-falsifier-v1",
        "case_count": len(rows),
        "passed_count": len(rows) - len(unsafe),
        "failed_count": len(unsafe),
        "cases": rows,
        "unsafe_results": unsafe,
        "terminal_result": "SEAM_SUITE_SUPPORTED" if not unsafe else "SEAM_SUITE_FALSIFIER_TRIGGERED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rc7fb1-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    measure = _load_measure(args.rc7fb1_root.resolve())
    rc8j = _load_rc8j(args.rc8j_root.resolve())
    result = execute_suite(measure, rc8j)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical_json_bytes(result, trailing_newline=True))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["failed_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
