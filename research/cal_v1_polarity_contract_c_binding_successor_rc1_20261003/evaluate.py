from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from claim_audit_lab.production_v1 import SEMANTIC_IMPLEMENTATION_SHA
from claim_audit_lab.production_v1.parent_bound import (
    CONTRACT_C_CANDIDATE_BLOB,
    CONTRACT_C_FREEZE_COMMIT,
    RESOLVER_AUTHORITY_COMMIT,
    RESOLVER_BLOB,
    run_parent_bound_pipeline,
    verify_external_authorities,
)

EXPECTED_SEMANTIC = "caa0048f8f511ec3c4aa1ce713766f2219a04bc1"
EXPECTED_CONTRACT_C_COMMIT = "c183d2d12306ee30c509169a58db55e7430fe8c5"
EXPECTED_CONTRACT_C_BLOB = "aeb50dee8d24bda5f62eb879654e80437a50912d"
EXPECTED_RESOLVER_COMMIT = "292168222f83c67a24190b4846eebe84392e3d04"
EXPECTED_RESOLVER_BLOB = "b9297ba06beefe1de8488bc25a4c424b0e10e58b"
EXPECTED_PARENTS = {
    "PIPE01": "supported",
    "PIPE02": "contradicted",
    "PIPE03": "not_checkable",
    "PIPE04": "contradicted",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_frozen_fixture_module(root: Path) -> Any:
    path = root / "tests/research/test_cal_v1_a2_eb_b_parent_integration_rc0.py"
    spec = importlib.util.spec_from_file_location(
        "polarity_successor_frozen_parent_fixture_generator", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen fixture generator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _rejected(fn: Callable[[], Any]) -> tuple[bool, str]:
    try:
        fn()
    except Exception as exc:
        return True, f"{type(exc).__name__}: {exc}"
    return False, "accepted"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out = Path(args.out).resolve()
    if out.exists():
        raise RuntimeError(f"refusing to overwrite result: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)

    fixture_cal_root = Path(os.environ["FROZEN_FIXTURE_CAL_ROOT"]).resolve()
    eb_root = Path(os.environ["EB_ROOT"]).resolve()
    contract_c_root = Path(os.environ["CONTRACT_C_ROOT"]).resolve()
    rc2_root = Path(os.environ["RC2_ROOT"]).resolve()
    resolver_root = Path(os.environ["RESOLVER_ROOT"]).resolve()
    old_contract_c_root = Path(os.environ["OLD_CONTRACT_C_ROOT"]).resolve()
    old_resolver_root = Path(os.environ["OLD_RESOLVER_ROOT"]).resolve()

    os.environ["CAL_EB_INTEGRATION_REPO"] = str(eb_root)
    os.environ["EB_ROOT"] = str(eb_root)

    controls: dict[str, bool] = {}
    observations: dict[str, Any] = {}

    controls["semantic_identity_exact"] = SEMANTIC_IMPLEMENTATION_SHA == EXPECTED_SEMANTIC
    controls["contract_c_commit_exact"] = CONTRACT_C_FREEZE_COMMIT == EXPECTED_CONTRACT_C_COMMIT
    controls["contract_c_blob_exact"] = CONTRACT_C_CANDIDATE_BLOB == EXPECTED_CONTRACT_C_BLOB
    controls["resolver_commit_exact"] = RESOLVER_AUTHORITY_COMMIT == EXPECTED_RESOLVER_COMMIT
    controls["resolver_blob_exact"] = RESOLVER_BLOB == EXPECTED_RESOLVER_BLOB

    verify_external_authorities(
        contract_c_root=contract_c_root,
        rc2_root=rc2_root,
        resolver_root=resolver_root,
    )
    controls["successor_external_authority_verifies"] = True

    old_candidate_rejects, old_candidate_detail = _rejected(
        lambda: verify_external_authorities(
            contract_c_root=old_contract_c_root,
            rc2_root=rc2_root,
            resolver_root=resolver_root,
        )
    )
    controls["predecessor_contract_c_root_rejected"] = old_candidate_rejects
    observations["predecessor_contract_c_root"] = old_candidate_detail

    old_resolver_rejects, old_resolver_detail = _rejected(
        lambda: verify_external_authorities(
            contract_c_root=contract_c_root,
            rc2_root=rc2_root,
            resolver_root=old_resolver_root,
        )
    )
    controls["predecessor_resolver_root_rejected"] = old_resolver_rejects
    observations["predecessor_resolver_root"] = old_resolver_detail

    integration = _load_frozen_fixture_module(fixture_cal_root)

    with tempfile.TemporaryDirectory(prefix="cal-polarity-c-binding-qual-") as raw:
        root = Path(raw)
        for case in integration.CASES:
            case_id = str(case.case_id)
            fixture_root = root / "fixture"
            fixture = integration._execute_case(case, fixture_root)
            case_dir = fixture_root / case_id
            contract_a_path = case_dir / "contract-a.json"
            _write_json(contract_a_path, fixture["contract_a"])
            bundle_dir = case_dir / "eb" / "contract_b"
            child_targets = {
                "C1": case_dir / "C1.target.json",
                "C2": case_dir / "C2.target.json",
            }

            first_dir = root / "first" / case_id
            second_dir = root / "second" / case_id
            first_manifest = run_parent_bound_pipeline(
                contract_a_path=contract_a_path,
                bundle_dir=bundle_dir,
                child_targets=child_targets,
                out_dir=first_dir,
                contract_c_root=contract_c_root,
                rc2_root=rc2_root,
                resolver_root=resolver_root,
            )
            second_manifest = run_parent_bound_pipeline(
                contract_a_path=contract_a_path,
                bundle_dir=bundle_dir,
                child_targets=child_targets,
                out_dir=second_dir,
                contract_c_root=contract_c_root,
                rc2_root=rc2_root,
                resolver_root=resolver_root,
            )

            parent = _read_json(first_dir / "parent-result.json")
            manifest = _read_json(first_dir / "manifest.json")
            c1_manifest = _read_json(first_dir / "children" / "C1" / "manifest.json")
            c2_manifest = _read_json(first_dir / "children" / "C2" / "manifest.json")

            expected_parent = EXPECTED_PARENTS[case_id]
            observed_parent = str(parent["parent_conclusion"])
            controls[f"{case_id}:parent_conclusion"] = observed_parent == expected_parent
            controls[f"{case_id}:parent_semantic_identity"] = (
                parent["semantic_implementation_sha"] == EXPECTED_SEMANTIC
            )
            controls[f"{case_id}:manifest_semantic_identity"] = (
                manifest["semantic_implementation_sha"] == EXPECTED_SEMANTIC
            )
            controls[f"{case_id}:child_semantic_identity"] = (
                c1_manifest["semantic_implementation_sha"] == EXPECTED_SEMANTIC
                and c2_manifest["semantic_implementation_sha"] == EXPECTED_SEMANTIC
            )
            controls[f"{case_id}:deterministic_parent"] = (
                (first_dir / "parent-result.json").read_bytes()
                == (second_dir / "parent-result.json").read_bytes()
            )
            controls[f"{case_id}:deterministic_contract_c"] = (
                (first_dir / "contract-c.json").read_bytes()
                == (second_dir / "contract-c.json").read_bytes()
            )
            controls[f"{case_id}:deterministic_manifest"] = (
                (first_dir / "manifest.json").read_bytes()
                == (second_dir / "manifest.json").read_bytes()
                and first_manifest == second_manifest
            )

            observations[case_id] = {
                "expected_parent": expected_parent,
                "observed_parent": observed_parent,
                "contract_c_sha256": _sha256(first_dir / "contract-c.json"),
                "parent_result_sha256": _sha256(first_dir / "parent-result.json"),
                "manifest_sha256": _sha256(first_dir / "manifest.json"),
                "semantic_implementation_sha": manifest["semantic_implementation_sha"],
            }

    failed = sorted(name for name, passed in controls.items() if not passed)
    result = {
        "schema": "cal-v1-polarity-contract-c-authority-binding-successor-qualification-v1",
        "issue": 198,
        "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
        "contract_c_authority": {
            "commit": CONTRACT_C_FREEZE_COMMIT,
            "candidate_blob": CONTRACT_C_CANDIDATE_BLOB,
            "resolver_commit": RESOLVER_AUTHORITY_COMMIT,
            "resolver_blob": RESOLVER_BLOB,
        },
        "controls": controls,
        "observations": observations,
        "failed_controls": failed,
        "status": (
            "QUALIFIED_POLARITY_CONTRACT_C_AUTHORITY_BINDING_SUCCESSOR"
            if not failed
            else "FALSIFIED_POLARITY_CONTRACT_C_INTEGRATION_REGRESSION"
        ),
    }
    out.write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
