"""Run the RC0 pipeline through the current qualified Evidence Bundler boundary.

Research/integration apparatus only. This wrapper preserves the entity-scoped CAL
adapter while replacing the earlier pre-counterexample Evidence Bundler pin with
the exact qualified Draft PR #54 head. Contract B legacy compatibility values are
supplied only through the explicit qualification-only compatibility carrier.
"""
from __future__ import annotations

import json
import sys
from typing import Any

import entity_scoped_entrypoint as scoped  # noqa: F401
import run_pipeline as base

EB_QUALIFIED_HEAD = "dd4fb2b89f351fbdcd8b08e48dd9d7d1f10c2d05"
CARRIER_SCHEMA = "research-contract-b-1.2-compatibility-carrier-v1"

base.EB_HEAD = EB_QUALIFIED_HEAD
_ORIGINAL_EXECUTE = base.execute


def _execute_with_qualified_eb(args: Any) -> dict[str, Any]:
    eb_root = args.evidence_bundler_root.resolve()
    carrier_path = (
        eb_root
        / "research"
        / "cal_rc0_contract_b_handoff"
        / "fixtures"
        / "contract_b_compatibility_carrier.json"
    )
    carrier = json.loads(carrier_path.read_text(encoding="utf-8"))
    if carrier.get("schema") != CARRIER_SCHEMA:
        raise RuntimeError("qualified Evidence Bundler compatibility carrier schema mismatch")
    authority = carrier.get("authority", {})
    if authority.get("actual_upstream_contract") != "contract-a-v2.0.0":
        raise RuntimeError("qualified Evidence Bundler carrier upstream authority mismatch")
    if authority.get("semantic_use_authorized") is not False:
        raise RuntimeError("qualified Evidence Bundler carrier unexpectedly authorizes semantic use")

    sys.path.insert(0, str(eb_root))
    try:
        from research.cal_rc0_contract_b_handoff import qualified_handoff
    finally:
        sys.path.pop(0)

    original_build = qualified_handoff.build_all_contract_b_qualified

    def carrier_bound_build(
        *,
        cohort: dict[str, Any],
        receipt: dict[str, Any],
        profile: dict[str, Any],
        out_dir: Any,
    ) -> list[dict[str, Any]]:
        return original_build(
            cohort=cohort,
            receipt=receipt,
            profile=profile,
            compatibility_carrier=carrier,
            out_dir=out_dir,
        )

    qualified_handoff.build_all_contract_b_qualified = carrier_bound_build
    try:
        result = _ORIGINAL_EXECUTE(args)
    finally:
        qualified_handoff.build_all_contract_b_qualified = original_build

    result["pins"]["evidence_bundler_head"] = EB_QUALIFIED_HEAD
    result["evidence_bundler"]["contract_b_compatibility_carrier"] = {
        "schema": CARRIER_SCHEMA,
        "actual_upstream_contract": authority["actual_upstream_contract"],
        "semantic_use_authorized": False,
    }
    return result


base.execute = _execute_with_qualified_eb


if __name__ == "__main__":
    raise SystemExit(base.main())
