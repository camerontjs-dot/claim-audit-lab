"""Execute the preregistered RC8J authority-consumption seam.

The existing PR #75 v5 integration must run first and produce its ordinary
run-output tree. This runner then:

* verifies the exact frozen RC8J dependency;
* confirms real-text RC7F CLAIMED measurements remain insufficient-authority;
* builds one explicitly typed fixture-only authority control using only validated
  Contract-B identity/coordinate facts from the controlled admitted corpus;
* executes the real frozen RC8J evaluator on the positive control and directed
  binding mutations;
* keeps every result blocked from CAL strengthening / positive Contract-C
  projection in this experiment.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import importlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

import yaml

from claim_audit_lab.contracts.factual_context import load_contract_b_intake

import run_integration as parent
from authority_consumption_rc1 import (
    RC8J_CANDIDATE_BLOB,
    RC8J_CANDIDATE_PATH,
    RC8J_FREEZE_COMMIT,
    consume_external_authority,
)
from shadow_candidate import canonical_bytes


def _git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def _load_rc8j(root: Path) -> Callable[[dict[str, Any]], dict[str, Any]]:
    if _git(root, "rev-parse", "HEAD") != RC8J_FREEZE_COMMIT:
        raise AssertionError("RC8J dependency checkout is not the frozen candidate commit")
    blob = _git(root, "hash-object", RC8J_CANDIDATE_PATH)
    if blob != RC8J_CANDIDATE_BLOB:
        raise AssertionError(f"RC8J candidate blob mismatch: {blob} != {RC8J_CANDIDATE_BLOB}")

    sys.path.insert(0, str(root))
    try:
        module = importlib.import_module(
            "research.semantic_authority_machinery_rc8.authority_contract_rc8j"
        )
    finally:
        sys.path.pop(0)
    evaluator = getattr(module, "assess_authority", None)
    if not callable(evaluator):
        raise AssertionError("frozen RC8J module does not expose assess_authority")
    return evaluator


def _find_passage_row(bundle_dir: Path, passage_id: str) -> dict[str, Any]:
    for path in sorted((bundle_dir / "evidence").glob("*/passages/*.yaml")):
        row = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(row, dict) and row.get("passage_id") == passage_id:
            return row
    raise AssertionError(f"passage not found in validated Contract B bundle: {passage_id}")


def _real_text_negative_control(run_output: Path) -> dict[str, Any]:
    case_dir = run_output / "cases" / "controlled-semantic-admitted"
    internal = json.loads((case_dir / "candidate-internal.json").read_text(encoding="utf-8"))
    shadow_c = json.loads((case_dir / "shadow-contract-c.json").read_text(encoding="utf-8"))

    claimed: list[dict[str, Any]] = []
    for claim_id, record in internal.items():
        for observation in record["semantic_measurements"]:
            measurement = observation.get("measurement") or {}
            if measurement.get("status") != "CLAIMED":
                continue
            authority = observation["authority"]
            if authority.get("state") != "insufficient_authority":
                raise AssertionError(f"real-text CLAIMED measurement gained authority: {claim_id}")
            if authority.get("may_strengthen_conclusion") is not False:
                raise AssertionError(f"real-text CLAIMED measurement may strengthen: {claim_id}")
            claimed.append(
                {
                    "claim_id": claim_id,
                    "passage_id": observation["passage_id"],
                    "family": observation["family"],
                    "authority_state": authority["state"],
                }
            )

    if not claimed:
        raise AssertionError("controlled admitted B case produced no CLAIMED measurements")

    verdicts = [row["conclusion"]["reported_verdict"] for row in shadow_c["propositions"]]
    if any(verdict != "not_checkable" for verdict in verdicts):
        raise AssertionError(f"conservative shadow C changed under seam test: {verdicts}")

    return {
        "claimed_measurement_count": len(claimed),
        "claimed_measurements": claimed,
        "all_claimed_remain_insufficient_authority": True,
        "shadow_contract_c_verdicts": verdicts,
        "positive_contract_c_projection_performed": False,
    }


def _validated_b_coordinates(run_output: Path) -> dict[str, Any]:
    bundle_dir = run_output / "corpus" / "controlled-semantic-admitted"
    intake = load_contract_b_intake(bundle_dir)
    if intake.extension_state != "present":
        raise AssertionError("controlled admitted corpus no longer has factual-context extension")

    claim_id = "clm-comparison"
    selected, _excluded, _basis, _aperture = parent._selection(intake, claim_id)
    if not selected:
        raise AssertionError("controlled comparison claim has no admitted passage")
    passage_id = selected[0]
    passage = _find_passage_row(bundle_dir, passage_id)

    start = passage.get("char_start")
    end = passage.get("char_end")
    source_id = passage.get("source_id")
    if not isinstance(start, int) or isinstance(start, bool):
        raise AssertionError("validated B passage char_start is not an integer")
    if not isinstance(end, int) or isinstance(end, bool) or start > end:
        raise AssertionError("validated B passage char_end is not a valid ordered coordinate")
    if not isinstance(source_id, str) or not source_id:
        raise AssertionError("validated B passage source_id is unavailable")

    return {
        "bundle_id": intake.bundle.manifest.bundle_id,
        "source_id": source_id,
        "passage_id": passage_id,
        "passage_span": [start, end],
        "claim_id": claim_id,
        "contract_b_validator": "already_passed_in_parent_v5_run",
    }


def _typed_seam_control(coords: dict[str, Any]) -> dict[str, Any]:
    subject = "authority-subject:integration-seam-control:v1"
    atom_id = "atom:integration-seam-control:comparison:v1"
    span = list(coords["passage_span"])
    fields = {
        "lhs_entity": "fixture:left",
        "rhs_entity": "fixture:right",
        "comparison_direction": "greater_than",
    }
    required_fields = ["lhs_entity", "rhs_entity", "comparison_direction"]
    return {
        "case_id": "B-CAL-C-RC8J-SEAM-POSITIVE",
        "fixture_only": True,
        "fixture_semantic_values_inferred_from_text": False,
        "execution_state": "completed",
        "evidence_admitted": True,
        "authority_subject_id": subject,
        "raw_source_id": coords["source_id"],
        "authority_subject_source_id": coords["source_id"],
        "raw_bundle_id": coords["bundle_id"],
        "authority_subject_bundle_id": coords["bundle_id"],
        "raw_passage_id": coords["passage_id"],
        "authority_subject_passage_id": coords["passage_id"],
        "admitted_passage_span": span,
        "raw_claim_id": coords["claim_id"],
        "authority_subject_claim_id": coords["claim_id"],
        "target_atom_id": atom_id,
        "authority_subject_atom_id": atom_id,
        "proposal": {
            "family": "comparison",
            "source_span": span,
            "fields": fields,
            "extra_modifiers": [],
            "authority_subject_id": subject,
        },
        "assertion": {
            "state": "asserted",
            "scope_path": ["typed_fixture", "not_text_derived"],
            "authority_subject_id": subject,
        },
        "operator": {
            "operator_id": "operator:integration-seam-control:comparison:v1",
            "domain": "comparison",
            "applicability": "applicable",
            "governed_span": span,
            "jurisdiction_fields": required_fields,
            "authority_subject_id": subject,
        },
        "field_warrants": {
            field: {
                "status": "established",
                "value": value,
                "span": span,
                "authority_subject_id": subject,
            }
            for field, value in fields.items()
        },
        "required_fields": required_fields,
        "composition": {"required": False, "state": "not_applicable", "basis": []},
        "aperture": {"required": False, "state": "not_applicable"},
        "instrument_ids": ["typed-fixture-only"],
        "reader_agreement_count": 1,
    }


def _mutation_cases(base: dict[str, Any]) -> list[tuple[str, dict[str, Any], str, str]]:
    rows: list[tuple[str, dict[str, Any], str, str]] = []

    def add(case_id: str, mutate: Callable[[dict[str, Any]], None], status: str, reason: str) -> None:
        case = deepcopy(base)
        case["case_id"] = case_id
        mutate(case)
        rows.append((case_id, case, status, reason))

    add(
        "SOURCE-MISMATCH",
        lambda c: c.__setitem__("authority_subject_source_id", "source:other"),
        "REJECTED",
        "AUTHORITY_EVIDENCE_SOURCE_MISMATCH",
    )
    add(
        "BUNDLE-MISMATCH",
        lambda c: c.__setitem__("authority_subject_bundle_id", "bundle:other"),
        "REJECTED",
        "AUTHORITY_EVIDENCE_BUNDLE_MISMATCH",
    )
    add(
        "PASSAGE-MISMATCH",
        lambda c: c.__setitem__("authority_subject_passage_id", "passage:other"),
        "REJECTED",
        "AUTHORITY_EVIDENCE_PASSAGE_MISMATCH",
    )
    add(
        "CLAIM-MISMATCH",
        lambda c: c.__setitem__("authority_subject_claim_id", "claim:other"),
        "REJECTED",
        "AUTHORITY_CLAIM_MISMATCH",
    )
    add(
        "ATOM-MISMATCH",
        lambda c: c.__setitem__("authority_subject_atom_id", "atom:other"),
        "REJECTED",
        "AUTHORITY_ATOM_IDENTITY_MISMATCH",
    )
    add(
        "SEGMENT-BINDING-MISSING",
        lambda c: c.__setitem__("authority_subject_bundle_id", None),
        "UNRESOLVED",
        "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED",
    )

    def field_outside_admitted(c: dict[str, Any]) -> None:
        end = c["admitted_passage_span"][1]
        c["operator"]["governed_span"] = [c["admitted_passage_span"][0], end + 10]
        c["field_warrants"]["lhs_entity"]["span"] = [end + 1, end + 2]

    add(
        "FIELD-OUTSIDE-ADMITTED-PASSAGE",
        field_outside_admitted,
        "REJECTED",
        "FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:lhs_entity",
    )
    add(
        "FIELD-SUBJECT-MISMATCH",
        lambda c: c["field_warrants"]["lhs_entity"].__setitem__(
            "authority_subject_id", "authority-subject:other"
        ),
        "REJECTED",
        "AUTHORITY_SUBJECT_MISMATCH:field:lhs_entity",
    )
    add(
        "EXECUTION-FAILURE",
        lambda c: c.__setitem__("execution_state", "failed"),
        "NO_ASSESSMENT",
        "EXECUTION_FAILED",
    )
    add(
        "EVIDENCE-NOT-ADMITTED",
        lambda c: c.__setitem__("evidence_admitted", False),
        "REJECTED",
        "EVIDENCE_NOT_ADMITTED",
    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-output", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    args = parser.parse_args()

    run_output = args.run_output.resolve()
    rc8j_root = args.rc8j_root.resolve()
    evaluator = _load_rc8j(rc8j_root)

    real_text = _real_text_negative_control(run_output)
    coords = _validated_b_coordinates(run_output)
    positive = _typed_seam_control(coords)

    rows: list[dict[str, Any]] = []
    positive_result = consume_external_authority(positive, evaluator, fixture_only=True)
    if positive_result["authority"] != {
        "status": "WARRANTED",
        "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
        "research_dependency": positive_result["authority"]["research_dependency"],
    }:
        raise AssertionError(f"fully bound seam control was not warranted: {positive_result}")
    rows.append(
        {
            "case_id": positive["case_id"],
            "expected_status": "WARRANTED",
            "expected_reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
            "observed": positive_result,
        }
    )

    unsafe_warranted_mutations: list[str] = []
    for case_id, case, expected_status, expected_reason in _mutation_cases(positive):
        result = consume_external_authority(case, evaluator, fixture_only=True)
        status = result["authority"]["status"]
        reason = result["authority"]["reason"]
        if status != expected_status or reason != expected_reason:
            raise AssertionError(
                f"{case_id}: observed {status}/{reason}, expected {expected_status}/{expected_reason}"
            )
        if expected_status != "WARRANTED" and status == "WARRANTED":
            unsafe_warranted_mutations.append(case_id)
        rows.append(
            {
                "case_id": case_id,
                "expected_status": expected_status,
                "expected_reason": expected_reason,
                "observed": result,
            }
        )

    if unsafe_warranted_mutations:
        raise AssertionError(f"unsafe warranted seam mutations: {unsafe_warranted_mutations}")
    if any(row["observed"]["epistemic_use"]["may_strengthen_cal_conclusion"] for row in rows):
        raise AssertionError("authority seam result was allowed to strengthen CAL conclusion")
    if any(row["observed"]["epistemic_use"]["may_project_positive_contract_c"] for row in rows):
        raise AssertionError("authority seam result was allowed to project positive Contract C state")

    parent_receipt = json.loads((run_output / "RUN-RECEIPT.json").read_text(encoding="utf-8"))
    parent_case = next(
        row for row in parent_receipt["cases"] if row["case"] == "controlled-semantic-admitted"
    )
    if parent_case["shadow_contract_c"]["frozen_validator"] != "PASS":
        raise AssertionError("parent controlled shadow C no longer passes frozen validator")

    receipt = {
        "experiment": "B-CAL-C RC8J authority consumption seam RC1",
        "parent_shadow_head": "5d799218f54a97da80713727709563fe91cc9291",
        "rc8j": {
            "freeze_commit": RC8J_FREEZE_COMMIT,
            "candidate_path": RC8J_CANDIDATE_PATH,
            "candidate_blob": RC8J_CANDIDATE_BLOB,
            "verified": True,
        },
        "validated_contract_b_coordinates": coords,
        "real_text_negative_control": real_text,
        "typed_fixture": {
            "semantic_values_inferred_from_text": False,
            "purpose": "transport and binding seam only",
            "case_count": len(rows),
            "unsafe_warranted_mutations": unsafe_warranted_mutations,
            "rows": rows,
        },
        "contract_c": {
            "parent_shadow_frozen_validator": "PASS",
            "positive_rc8j_projection_attempted": False,
            "projection_rule_status": "not_established",
        },
        "terminal_disposition": (
            "RC8J_TYPED_AUTHORITY_SEAM_CONSUMED_WITH_EXACT_BINDING_REASONS; "
            "REAL_TEXT_REMAINS_PROPOSAL_ONLY; POSITIVE_C_PROJECTION_NOT_ESTABLISHED"
        ),
    }
    (run_output / "RC8J-CONSUMPTION-RECEIPT.json").write_bytes(canonical_bytes(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
