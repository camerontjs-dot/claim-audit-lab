"""Model-free falsifier for naive RC8J -> Contract C projections.

This runner does not invent a positive CAL conclusion. It verifies that Contract C
already has assessed-conclusion capacity, rejects two tempting direct authority
encodings, and records that the frozen RC8J authority result does not itself
supply the proposition-relative/causal fields required to construct an assessed
Contract-C conclusion.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


C_AUTHORITY_SHA = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
C_SPEC_BLOB = "8c15f2e5f4047ccd17e204fb23aee1168781b9d5"
C_CANONICAL_FIXTURE_BLOB = "38b2271fc31ffa7683c09a486a8919572fc2f1a4"
PARENT_SEAM_HEAD = "dcddb6a08d2e68052edee7a74b014a2632fdc6cf"

_REQUIRED_CONCLUSION_INFORMATION = {
    "reported_verdict",
    "terminal_branch",
    "causal_form",
    "basis_members",
    "residual_contribution_ids",
    "rule_roles",
}


def _load_registered_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def _git_blob(root: Path, path: str) -> str:
    import subprocess

    return subprocess.check_output(
        ["git", "-C", str(root), "hash-object", path], text=True
    ).strip()


def _reidentify(c_validator: Any, value: dict[str, Any]) -> bytes:
    updated = c_validator.with_result_set_identity(value)
    return c_validator.canonical_bytes(updated)


def _validate(c_validator: Any, raw: bytes, index: dict[str, Any]) -> list[str]:
    return c_validator.validate_contract_c_bytes(raw, contract_b_index=index)


def _find_positive_seam_row(receipt: dict[str, Any]) -> dict[str, Any]:
    for row in receipt["typed_fixture"]["rows"]:
        if row["case_id"] == "B-CAL-C-RC8J-SEAM-POSITIVE":
            return row
    raise AssertionError("accepted RC8J seam receipt lacks positive control")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-output", type=Path, required=True)
    parser.add_argument("--apparatus-c", type=Path, required=True)
    args = parser.parse_args()

    run_output = args.run_output.resolve()
    apparatus_c = args.apparatus_c.resolve()

    if _git_blob(apparatus_c, "contract-c-v1.0.0.md") != C_SPEC_BLOB:
        raise AssertionError("frozen Contract C normative spec blob mismatch")
    if (
        _git_blob(apparatus_c, "fixtures/contract-c/1.0.0/valid-canonical.json")
        != C_CANONICAL_FIXTURE_BLOB
    ):
        raise AssertionError("frozen Contract C canonical fixture blob mismatch")

    c_validator = _load_registered_module(
        apparatus_c / "validators" / "contract_c.py", "projection_falsifier_contract_c"
    )

    case_dir = run_output / "cases" / "controlled-semantic-admitted"
    shadow_raw = (case_dir / "shadow-contract-c.json").read_bytes()
    shadow = json.loads(shadow_raw)
    shadow_index = json.loads((case_dir / "contract-b-index.json").read_text(encoding="utf-8"))
    baseline_errors = _validate(c_validator, shadow_raw, shadow_index)
    if baseline_errors:
        raise AssertionError(f"parent shadow C is no longer valid: {baseline_errors}")

    # F1: exact-version Contract C does not accept producer-private authority fields.
    f1 = deepcopy(shadow)
    f1["propositions"][0]["authority"] = {
        "status": "WARRANTED",
        "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
    }
    f1_errors = _validate(c_validator, _reidentify(c_validator, f1), shadow_index)
    if not f1_errors:
        raise AssertionError("Contract C unexpectedly accepted an unknown authority field")

    # F2: there is no generic performed-positive assessment-stage token in C 1.0.
    f2 = deepcopy(shadow)
    f2["propositions"][0]["assessments"]["semantic_validity"] = {
        "state": "performed",
        "value": "positive",
    }
    f2_errors = _validate(c_validator, _reidentify(c_validator, f2), shadow_index)
    if not f2_errors:
        raise AssertionError("Contract C unexpectedly accepted performed/positive semantic_validity")

    # F3: nevertheless C 1.0 already contains valid completed assessed conclusions.
    canonical_path = apparatus_c / "fixtures" / "contract-c" / "1.0.0" / "valid-canonical.json"
    canonical_index_path = apparatus_c / "fixtures" / "contract-c" / "1.0.0" / "contract-b-index.json"
    canonical_raw = canonical_path.read_bytes()
    canonical = json.loads(canonical_raw)
    canonical_index = json.loads(canonical_index_path.read_text(encoding="utf-8"))
    canonical_errors = _validate(c_validator, canonical_raw, canonical_index)
    if canonical_errors:
        raise AssertionError(f"frozen canonical Contract C fixture failed validation: {canonical_errors}")

    assessed_rows = [
        prop
        for prop in canonical["propositions"]
        if prop["execution"].get("completion") == "assessed"
    ]
    assessed_verdicts = [prop["conclusion"]["reported_verdict"] for prop in assessed_rows]
    if not assessed_rows or any(verdict == "not_checkable" for verdict in assessed_verdicts):
        raise AssertionError("frozen Contract C fixture lacks the expected assessed conclusion control")
    if not all(
        prop["assessments"]["semantic_validity"] == {"state": "not_performed"}
        for prop in assessed_rows
    ):
        raise AssertionError("canonical assessed control unexpectedly depends on a positive stage token")

    # F4: RC8J authority output does not contain the fields needed to select/build a C conclusion.
    seam_receipt = json.loads(
        (run_output / "RC8J-CONSUMPTION-RECEIPT.json").read_text(encoding="utf-8")
    )
    positive = _find_positive_seam_row(seam_receipt)
    observed_authority = positive["observed"]["authority"]
    if observed_authority["status"] != "WARRANTED":
        raise AssertionError("projection falsifier lost its warranted seam control")
    supplied = set(observed_authority)
    missing_conclusion_information = sorted(_REQUIRED_CONCLUSION_INFORMATION - supplied)
    if set(missing_conclusion_information) != _REQUIRED_CONCLUSION_INFORMATION:
        raise AssertionError("authority output unexpectedly acquired Contract-C conclusion semantics")

    # F5: safe current projection remains the unchanged valid not_checkable shape.
    current_verdicts = [prop["conclusion"]["reported_verdict"] for prop in shadow["propositions"]]
    if any(verdict != "not_checkable" for verdict in current_verdicts):
        raise AssertionError(f"parent safe projection was unexpectedly strengthened: {current_verdicts}")

    result = {
        "experiment": "RC8J -> Contract C projection falsifier RC1",
        "parent_seam_head": PARENT_SEAM_HEAD,
        "contract_c": {
            "authority_commit": C_AUTHORITY_SHA,
            "spec_blob": C_SPEC_BLOB,
            "canonical_fixture_blob": C_CANONICAL_FIXTURE_BLOB,
        },
        "falsifiers": {
            "direct_authority_field": {
                "expected": "REJECTED_BY_FROZEN_C",
                "observed": "REJECTED_BY_FROZEN_C",
                "error_count": len(f1_errors),
                "errors": f1_errors,
            },
            "performed_positive_semantic_validity": {
                "expected": "REJECTED_BY_FROZEN_C",
                "observed": "REJECTED_BY_FROZEN_C",
                "error_count": len(f2_errors),
                "errors": f2_errors,
            },
        },
        "existing_c_capacity_control": {
            "frozen_fixture_validator": "PASS",
            "assessed_proposition_count": len(assessed_rows),
            "assessed_reported_verdicts": assessed_verdicts,
            "semantic_validity_states": [
                prop["assessments"]["semantic_validity"] for prop in assessed_rows
            ],
            "generic_positive_stage_token_required": False,
        },
        "rc8j_authority_result": {
            "status": observed_authority["status"],
            "reason": observed_authority["reason"],
            "missing_contract_c_conclusion_information": missing_conclusion_information,
            "status_is_itself_reported_verdict": False,
        },
        "safe_parent_projection": {
            "frozen_validator": "PASS",
            "reported_verdicts": current_verdicts,
            "positive_projection_attempted": False,
        },
        "contract_c_successor_justified": False,
        "next_blocker": "CAL_INTERNAL_AUTHORITY_TO_PROPOSITION_CONCLUSION_SEMANTICS",
        "terminal_disposition": (
            "CONTRACT_C_1_0_HAS_ASSESSED_CONCLUSION_CAPACITY; "
            "RC8J_STATUS_ALONE_IS_NOT_A_PROPOSITION_CONCLUSION; "
            "NEXT_BLOCKER_IS_CAL_INTERNAL_AUTHORITY_TO_CONCLUSION_SEMANTICS"
        ),
    }
    out = run_output / "RC8J-C-PROJECTION-FALSIFIER.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
