from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from types import ModuleType
from typing import Any

from claim_audit_lab.production_v1.execution import (
    run_contract_b_bundle,
    validate_contract_b_bundle,
)
from claim_audit_lab.production_v1.targeting import (
    TargetAuthoringError,
    TargetConformanceError,
    author_target,
    author_target_from_bundle,
    canonical_target_bytes,
    validate_target_conformance,
)

BASE_SHA = "ddaf94551e38663920593cab89f9c60d43c1555f"
FROZEN_CAL_SHA = "e24e405f5336ee024674f39dba97255bb58a2dd9"
SEMANTIC_IMPLEMENTATION_SHA = "847cc970642bb648dc994b929c2053b5c9d4648c"
DECOMPOSITION_BLOB = "268d0dc4dd22ddde3848141d62b7d719e48d374d"
EB_SHA = "4e1f6fe00e7c350b28f52bfea14f1f8988847884"


def _tagged(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _load_frozen_fixture() -> ModuleType:
    root = Path(os.environ["FROZEN_CAL_ROOT"]).resolve()
    path = root / "tests/research/test_cal_v1_a2_eb_b_parent_integration_rc0.py"
    spec = importlib.util.spec_from_file_location("frozen_target_oracle", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen target oracle")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): _tagged(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _write_json(path: Path, value: dict[str, Any], *, pretty: bool = False) -> None:
    if pretty:
        text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    else:
        text = json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")


def _build_bundle(module: ModuleType, root: Path) -> Path:
    case = module.CASES[0]
    initial = module._initial_package()
    package = module.build_package(
        contract_a=module._contract_a(),
        config=module.INTEGRATION_CONFIG,
        admission=module._admission(case, initial),
    )
    receipt = module.project_contract_b(
        package=package,
        compatibility_carrier=module._carrier(),
        out_dir=root / "eb",
    )
    assert receipt["contract_b_authority"]["version"] == "1.2.0"
    return root / "eb" / "contract_b"


def _mutation_cases(module: ModuleType) -> list[tuple[str, dict[str, Any]]]:
    c1 = module._target("C1")
    c2 = module._target("C2")
    cases: list[tuple[str, dict[str, Any]]] = []

    missing = deepcopy(c1)
    del missing["proposition"]["fields"]["rhs_entity"]
    cases.append(("strict_missing_required_family_field", missing))

    sideways = deepcopy(c1)
    sideways["proposition"]["fields"]["comparison_direction"] = "SIDEWAYS"
    cases.append(("strict_unsupported_direction", sideways))

    extra = deepcopy(c1)
    extra["proposition"]["fields"]["time_scope"] = "2025"
    cases.append(("strict_extra_ignored_semantics", extra))

    direction = deepcopy(c1)
    direction["proposition"]["fields"]["comparison_direction"] = "LESS_THAN"
    cases.append(("strict_direction_disagrees_with_claim", direction))

    orientation = deepcopy(c1)
    fields = orientation["proposition"]["fields"]
    fields["lhs_entity"], fields["rhs_entity"] = fields["rhs_entity"], fields["lhs_entity"]
    cases.append(("strict_entity_orientation_disagrees_with_claim", orientation))

    inactive = deepcopy(c1)
    inactive["proposition"]["semantic_family"] = "permission_exception"
    cases.append(("inactive_family", inactive))

    temporal = deepcopy(c2)
    temporal["proposition"]["fields"]["temporal_relation"] = "AFTER"
    cases.append(("event_relation_disagrees_with_claim", temporal))

    event_extra = deepcopy(c2)
    event_extra["proposition"]["fields"]["time_scope"] = "2025"
    cases.append(("event_extra_ignored_semantics", event_extra))

    return cases


def main() -> None:
    result_path = Path(os.environ["QUALIFICATION_RESULT"]).resolve()
    work = result_path.parent / "target-authoring-conformance-work"
    work.mkdir(parents=True, exist_ok=True)

    module = _load_frozen_fixture()
    bundle_dir = _build_bundle(module, work)

    trusted_equivalence: list[dict[str, Any]] = []
    for claim_id in ("C1", "C2"):
        trusted = module._target(claim_id)
        authored = author_target_from_bundle(bundle_dir, claim_id)
        assert authored == trusted

        trusted_path = work / f"{claim_id}.trusted.target.json"
        authored_path = work / f"{claim_id}.authored.target.json"
        module._write_target(trusted_path, claim_id)
        authored_path.write_bytes(canonical_target_bytes(authored))
        assert trusted_path.read_bytes() == authored_path.read_bytes()

        trusted_receipt = validate_target_conformance(bundle_dir, trusted_path)
        authored_receipt = validate_target_conformance(bundle_dir, authored_path)
        assert trusted_receipt["canonical_authored_target_sha256"] == (
            authored_receipt["canonical_authored_target_sha256"]
        )

        trusted_run = work / f"{claim_id}.trusted.run"
        authored_run = work / f"{claim_id}.authored.run"
        run_contract_b_bundle(bundle_dir, trusted_path, trusted_run)
        run_contract_b_bundle(bundle_dir, authored_path, authored_run)
        assert _snapshot(trusted_run) == _snapshot(authored_run)

        record = json.loads((authored_run / "result.json").read_text(encoding="utf-8"))
        assert record["result"]["conclusion"] == "supported"
        trusted_equivalence.append(
            {
                "claim_id": claim_id,
                "semantic_family": authored["proposition"]["semantic_family"],
                "target_sha256": _tagged(authored_path.read_bytes()),
                "byte_identical_to_frozen_trusted_target": True,
                "native_run_byte_identical": True,
                "conclusion": record["result"]["conclusion"],
            }
        )

    pretty_target = module._target("C1")
    pretty_path = work / "C1.pretty.target.json"
    _write_json(pretty_path, pretty_target, pretty=True)
    pretty_receipt = validate_target_conformance(bundle_dir, pretty_path)
    compact_path = work / "C1.authored.target.json"
    assert pretty_receipt["status"] == "CONFORMANT"
    assert pretty_receipt["input_target_sha256"] != _tagged(compact_path.read_bytes())

    weak_control_rows: list[dict[str, Any]] = []
    for name, mutated in _mutation_cases(module):
        path = work / f"{name}.target.json"
        _write_json(path, mutated)

        validate_contract_b_bundle(bundle_dir, path)

        rejected = False
        detail = ""
        try:
            validate_target_conformance(bundle_dir, path)
        except (TargetAuthoringError, TargetConformanceError) as exc:
            rejected = True
            detail = str(exc)
        assert rejected, name
        weak_control_rows.append(
            {
                "case": name,
                "existing_structural_validator": "ACCEPTED",
                "new_conformer": "REJECTED",
                "detail": detail,
            }
        )

    authoring_refusals = (
        "Alpha had a higher rate than Beta in 2025.",
        "alice had a higher rate than Beta.",
        "Alice did not review dossier before Bob archived dossier.",
        "Alice reviewed dossier while Bob archived dossier.",
        "The archive contains unrelated maintenance notes.",
    )
    for index, claim_text in enumerate(authoring_refusals, start=1):
        try:
            author_target(f"NEG-{index}", claim_text)
        except TargetAuthoringError:
            continue
        raise AssertionError(f"out-of-aperture claim was authored: {claim_text}")

    result = {
        "schema": "cal-v1-target-authoring-conformance-qualification-rc0",
        "result": "PASS",
        "research_question": (
            "Can a deterministic bounded authoring/conformance path produce trusted CAL targets "
            "for the two active semantic families while rejecting PR #182 semantic-drift cases "
            "before frozen CAL execution?"
        ),
        "subject": {
            "cal_base": BASE_SHA,
            "frozen_cal_oracle": FROZEN_CAL_SHA,
            "semantic_implementation": SEMANTIC_IMPLEMENTATION_SHA,
            "decomposition_blob": DECOMPOSITION_BLOB,
            "evidence_bundler": EB_SHA,
            "contract_b": "1.2.0",
        },
        "trusted_target_equivalence": trusted_equivalence,
        "formatting_invariance": {
            "pretty_json_conforms": True,
            "raw_target_identity_changes": True,
        },
        "weak_control_discrimination": {
            "existing_structural_validator_accepted": len(weak_control_rows),
            "new_conformer_rejected": len(weak_control_rows),
            "cases": weak_control_rows,
        },
        "out_of_aperture_authoring_refusals": len(authoring_refusals),
        "protected_boundaries": {
            "frozen_semantic_runtime_modified": False,
            "decomposition_composer_modified": False,
            "contract_c_consumed_or_modified": False,
            "run_bundle_behavior_modified": False,
        },
        "non_claims": [
            "This does not establish unrestricted natural-language target authoring.",
            "This does not change or requalify frozen CAL semantic behavior.",
            "This does not promote or version the authoring/conformance path.",
            "This does not move parent-bound Contract C into CAL.",
        ],
    }
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
