"""Namespace adapter for Contract-B -> CAL -> Decision RC0.

The CAL target declaration is keyed to the upstream research case identity,
while Contract B owns a separate immutable bundle_id. Those identities must not
be equated. The underlying runner already binds every target proposition to an
exact Contract B claim ID and Contract C binds the actual Contract B bundle ID
and hash.

This adapter preserves the existing target document validation against its own
declared case_id, then lets the Contract B bundle identity remain independent.
"""
from __future__ import annotations

from typing import Any

import run_evidence_bundle as runner

_ORIGINAL_TARGET_MAP = runner.base.target_map
_ORIGINAL_EXECUTE = runner.execute


def _target_map_across_namespaces(
    targets: dict[str, Any], _contract_b_bundle_id: str
) -> dict[str, dict[str, Any]]:
    case_id = targets.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError("CAL target declaration requires a non-empty upstream case_id")
    return _ORIGINAL_TARGET_MAP(targets, case_id)


runner.base.target_map = _target_map_across_namespaces


def _execute_with_namespace_receipt(args: Any) -> dict[str, Any]:
    receipt = _ORIGINAL_EXECUTE(args)
    targets = runner.base.load_json(args.targets.resolve())
    receipt["input_target_case_id"] = str(targets["case_id"])
    receipt["identity_namespaces"] = {
        "cal_target_case_id": "upstream_case_identity",
        "contract_b_bundle_id": "contract_b_immutable_bundle_identity",
        "binding_rule": (
            "Target proposition IDs must exist exactly in Contract B claims; "
            "Contract C and Decision bind the actual Contract B bundle_id and bundle_hash."
        ),
    }
    return receipt


runner.execute = _execute_with_namespace_receipt


if __name__ == "__main__":
    raise SystemExit(runner.main())
