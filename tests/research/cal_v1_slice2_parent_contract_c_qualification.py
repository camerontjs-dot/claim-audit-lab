from __future__ import annotations

import copy
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from claim_audit_lab.production_v1.parent_bound import (
    ParentBoundPipelineError,
    build_parent_bound_contract_c,
)

CONTRACT_C_ROOT = Path(os.environ["CONTRACT_C_ROOT"]).resolve()
RC2_ROOT = Path(os.environ["RC2_ROOT"]).resolve()
RESOLVER_ROOT = Path(os.environ["RESOLVER_ROOT"]).resolve()
FROZEN_CAL_ROOT = Path(os.environ["FROZEN_CAL_ROOT"]).resolve()
EB_ROOT = Path(os.environ["EB_ROOT"]).resolve()
OUT = Path(os.environ.get("QUALIFICATION_RESULT", "cal-v1-slice2-qualification.json")).resolve()

EXPECTED = {
    "PIPE01": "supported",
    "PIPE02": "contradicted",
    "PIPE03": "not_checkable",
    "PIPE04": "contradicted",
}


def _load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _reject(fn: Any) -> bool:
    try:
        fn()
    except Exception:
        return True
    return False


def _evidence_index(package: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (str(row["source_id"]), str(row["passage_id"]))
        for row in package["candidates"]
    }


def _candidate_modules() -> tuple[Any, Any]:
    candidate = _load(
        CONTRACT_C_ROOT
        / "research/contract_c_cal_v1_parent_recomposition_rc0_20260919/candidate_rc0.py",
        "slice2_contract_c_candidate",
    )
    rc2 = _load(
        RC2_ROOT / "validators/contract_c_rc2.py",
        "slice2_contract_c_rc2",
    )
    return candidate, rc2


def main() -> None:
    os.environ["CAL_ROOT"] = str(FROZEN_CAL_ROOT)
    os.environ["EB_ROOT"] = str(EB_ROOT)
    os.environ["CAL_EB_INTEGRATION_REPO"] = str(EB_ROOT)
    os.environ["C2_ROOT"] = str(RC2_ROOT)
    os.environ["RESOLVER_JSON"] = str(
        RESOLVER_ROOT
        / "research/contract_c2_current_cal_resolver_successor_rc0/RESOLVER.json"
    )

    frozen_eval = _load(
        CONTRACT_C_ROOT
        / "research/contract_c_cal_v1_parent_recomposition_rc0_20260919/evaluate.py",
        "slice2_frozen_producer_evaluator",
    )
    integration = frozen_eval._load_integration_module()
    resolver = json.loads(
        (
            RESOLVER_ROOT
            / "research/contract_c2_current_cal_resolver_successor_rc0/RESOLVER.json"
        ).read_text(encoding="utf-8")
    )
    candidate, rc2 = _candidate_modules()

    observations: dict[str, Any] = {}
    controls: dict[str, bool] = {}
    built: dict[str, tuple[Any, dict[str, Any], dict[str, Any]]] = {}

    with tempfile.TemporaryDirectory(prefix="cal-v1-slice2-qual-") as raw:
        root = Path(raw)
        for case in integration.CASES:
            result = integration._execute_case(case, root / "producer")
            oracle, oracle_authority = frozen_eval._build_case(result, resolver)

            child_bytes = (result["c1_bytes"], result["c2_bytes"])
            produced = build_parent_bound_contract_c(
                contract_a=result["contract_a"],
                child_result_bytes=child_bytes,
                evidence_index=_evidence_index(result["package"]),
                contract_c_root=CONTRACT_C_ROOT,
                rc2_root=RC2_ROOT,
                resolver_root=RESOLVER_ROOT,
            )
            oracle_bytes = candidate.canonical_bytes(oracle, rc2_validator=rc2)
            case_id = case.case_id
            observations[case_id] = {
                "expected_parent": EXPECTED[case_id],
                "observed_parent": produced.parent.conclusion.value,
                "byte_identical_to_frozen_producer": produced.contract_c_bytes
                == oracle_bytes,
                "authority_identical_to_frozen_producer": produced.recomposition_authority
                == oracle_authority,
                "contract_c_sha256": produced.contract_c_sha256,
                "decomposition_receipt_id": produced.parent.receipt.receipt_id,
            }
            controls[f"{case_id}:expected_parent"] = (
                produced.parent.conclusion.value == EXPECTED[case_id]
            )
            controls[f"{case_id}:producer_byte_identity"] = (
                produced.contract_c_bytes == oracle_bytes
            )
            controls[f"{case_id}:producer_authority_identity"] = (
                produced.recomposition_authority == oracle_authority
            )

            replay = build_parent_bound_contract_c(
                contract_a=result["contract_a"],
                child_result_bytes=child_bytes,
                evidence_index=_evidence_index(result["package"]),
                contract_c_root=CONTRACT_C_ROOT,
                rc2_root=RC2_ROOT,
                resolver_root=RESOLVER_ROOT,
            )
            controls[f"{case_id}:deterministic_replay"] = (
                replay.contract_c_bytes == produced.contract_c_bytes
                and replay.contract_c_sha256 == produced.contract_c_sha256
                and replay.parent.receipt == produced.parent.receipt
            )

            reversed_children = build_parent_bound_contract_c(
                contract_a=result["contract_a"],
                child_result_bytes=tuple(reversed(child_bytes)),
                evidence_index=_evidence_index(result["package"]),
                contract_c_root=CONTRACT_C_ROOT,
                rc2_root=RC2_ROOT,
                resolver_root=RESOLVER_ROOT,
            )
            controls[f"{case_id}:supplied_child_order_invariant"] = (
                reversed_children.contract_c_bytes == produced.contract_c_bytes
            )
            built[case_id] = (produced, result, oracle_authority)

        base, result, authority = built["PIPE01"]

        controls["child_omission_rejected"] = _reject(
            lambda: build_parent_bound_contract_c(
                contract_a=result["contract_a"],
                child_result_bytes=(result["c1_bytes"],),
                evidence_index=_evidence_index(result["package"]),
                contract_c_root=CONTRACT_C_ROOT,
                rc2_root=RC2_ROOT,
                resolver_root=RESOLVER_ROOT,
            )
        )

        sequence_mutated = copy.deepcopy(result["contract_a"])
        sequence_mutated["decomposition"]["children"][0]["sequence"] = 2
        sequence_mutated["decomposition"]["children"][1]["sequence"] = 1
        controls["declared_sequence_mutation_rejected"] = _reject(
            lambda: build_parent_bound_contract_c(
                contract_a=sequence_mutated,
                child_result_bytes=(result["c1_bytes"], result["c2_bytes"]),
                evidence_index=_evidence_index(result["package"]),
                contract_c_root=CONTRACT_C_ROOT,
                rc2_root=RC2_ROOT,
                resolver_root=RESOLVER_ROOT,
            )
        )

        substituted_record = json.loads(result["c2_bytes"])
        substituted_record["input"]["contract_b"]["bundle_hash"] = "sha256:" + "9" * 64
        substituted_bytes = (
            json.dumps(substituted_record, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode()
        controls["contract_b_world_substitution_rejected"] = _reject(
            lambda: build_parent_bound_contract_c(
                contract_a=result["contract_a"],
                child_result_bytes=(result["c1_bytes"], substituted_bytes),
                evidence_index=_evidence_index(result["package"]),
                contract_c_root=CONTRACT_C_ROOT,
                rc2_root=RC2_ROOT,
                resolver_root=RESOLVER_ROOT,
            )
        )

        stale = copy.deepcopy(base.contract_c_object)
        stale["recomposition"]["decomposition_receipt_id"] = "0" * 64
        stale.pop("result_set_id", None)
        stale = candidate.seal(stale)
        controls["stale_decomposition_receipt_rejected"] = _reject(
            lambda: candidate.verify_recomposition_authority(
                stale,
                exact_recomposition=authority,
                rc2_validator=rc2,
            )
        )

        native_sub = copy.deepcopy(base.contract_c_object)
        native_sub["recomposition"]["ordered_children"][0][
            "native_result_sha256"
        ] = "sha256:" + "1" * 64
        native_sub.pop("result_set_id", None)
        native_sub = candidate.seal(native_sub)
        candidate.validate_object(native_sub, rc2_validator=rc2)
        controls["native_child_result_substitution_rejected"] = _reject(
            lambda: candidate.verify_recomposition_authority(
                native_sub,
                exact_recomposition=authority,
                rc2_validator=rc2,
            )
        )
        controls["coherent_reseal_rejected_by_fixed_authority"] = _reject(
            lambda: candidate.verify_external_authority(
                native_sub,
                expected_whole_object_sha256=base.contract_c_sha256,
                rc2_validator=rc2,
            )
        )

        replay_base, replay_result, replay_authority = built["PIPE01"]
        replay_source, _, _ = built["PIPE03"]
        cross_run = copy.deepcopy(replay_base.contract_c_object)
        source_child = replay_source.recomposition_authority["ordered_children"][0]
        target_child = cross_run["recomposition"]["ordered_children"][0]
        target_child["native_result_sha256"] = source_child["native_result_sha256"]
        target_child["cal_result_id"] = source_child["cal_result_id"]
        cross_run.pop("result_set_id", None)
        cross_run = candidate.seal(cross_run)
        candidate.validate_object(cross_run, rc2_validator=rc2)
        controls["cross_run_replay_rejected_by_fixed_authority"] = _reject(
            lambda: candidate.verify_recomposition_authority(
                cross_run,
                exact_recomposition=replay_authority,
                rc2_validator=rc2,
            )
        )

        controls["wrong_contract_c_authority_checkout_rejected"] = _reject(
            lambda: build_parent_bound_contract_c(
                contract_a=replay_result["contract_a"],
                child_result_bytes=(
                    replay_result["c1_bytes"],
                    replay_result["c2_bytes"],
                ),
                evidence_index=_evidence_index(replay_result["package"]),
                contract_c_root=RC2_ROOT,
                rc2_root=RC2_ROOT,
                resolver_root=RESOLVER_ROOT,
            )
        )

    failures = sorted(name for name, ok in controls.items() if not ok)
    disposition = (
        "QUALIFIED_FOR_CONTROLLED_LOCAL_PIPELINE_PARENT_BOUND_RUNS"
        if not failures
        else "FALSIFIED_PRODUCTION_PARENT_PATH"
    )
    payload = {
        "schema": "cal-v1-slice2-parent-contract-c-qualification-v1",
        "disposition": disposition,
        "exact_authorities": {
            "slice1_base": "61cab64149cb6119e4dbe1fe18496f3ccf89002f",
            "cal_freeze": "e24e405f5336ee024674f39dba97255bb58a2dd9",
            "semantic_source": "7cf0d2e50562ec4ce4082d1e1c058a11025b1a48",
            "semantic_implementation": "847cc970642bb648dc994b929c2053b5c9d4648c",
            "decomposition_blob": "268d0dc4dd22ddde3848141d62b7d719e48d374d",
            "contract_c_freeze": "c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec",
            "contract_c_candidate_blob": "df6b6ed410f52cafaeadfe1578d770f480a34b09",
            "rc2_authority": "b42c827acb0a9fe65353354d709add0e27bab307",
            "resolver_authority": "1d33e0612befcf8016816197c90c062373796df9",
        },
        "observations": observations,
        "controls": controls,
        "failures": failures,
        "cal_semantics_changed": False,
        "contract_c_semantics_changed": False,
        "target_authoring_qualified": False,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    if failures:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
