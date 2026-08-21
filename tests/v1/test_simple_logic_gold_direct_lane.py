"""Portable contract tests for Simple Logic Gold's direct CAL diagnostic lane."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from claim_audit_lab.v1.config import load_default_audit_config
from scripts.simple_logic_gold_direct_lane import (
    _defect_route,
    _map_cal_verdict,
    _write_absent_or_identical,
    run_direct_lane,
)


def _frozen(*, retrieval_gap: bool = False) -> dict[str, Any]:
    cases = []
    for number in range(1, 13):
        relation = "retrieval_gap" if retrieval_gap and number == 12 else "supports"
        parent = "pending" if relation == "retrieval_gap" else "supported"
        cases.append(
            {
                "base_case_id": f"SLG-{number:02d}",
                "operator": "single",
                "facts": [{"fact_id": f"f-{number}", "text": f"Fact {number}."}],
                "atoms": [
                    {
                        "atom_id": f"a-{number}",
                        "claim": f"Claim {number}.",
                        "relation": relation,
                    }
                ],
                "parent_verdict": parent,
            }
        )
    atom_counts = {"supports": 12} if not retrieval_gap else {"retrieval_gap": 1, "supports": 11}
    parent_counts = {"supported": 12} if not retrieval_gap else {"pending": 1, "supported": 11}
    return {
        "schema_version": "simple-logic-gold-frozen-dev-v0.1",
        "status": "frozen_approved_dev_not_validation_or_gate_evidence",
        "freeze_version": "v0.1-frozen-fixture",
        "freeze_identifier": "simple-logic-gold-v0.1-frozen-fixture",
        "manifest_version": "v0.1-draft-fixture",
        "manifest_sha256": "sha256:manifest",
        "derived_gold_sha256": "sha256:derived",
        "world_count": 12,
        "atom_relation_counts": atom_counts,
        "parent_verdict_counts": parent_counts,
        "frozen_cases": cases,
    }


def _write_frozen(path: Path, frozen: dict[str, Any]) -> bytes:
    raw = json.dumps(frozen, sort_keys=True).encode("utf-8")
    path.write_bytes(raw)
    return raw


def _runner(request: Any) -> Any:
    verdict = SimpleNamespace(
        support_verdict="supported",
        support_verdict_reason=None,
        audit_flags=[],
    )
    return SimpleNamespace(
        verdict=verdict,
        model_dump=lambda *, mode: {
            "claim_id": request.claim_id,
            "audit_config_hash": "sha256:stub-config",
        },
    )


def test_direct_lane_binds_exact_frozen_bytes_and_derives_parents(tmp_path: Path) -> None:
    frozen_path = tmp_path / "frozen.json"
    raw = _write_frozen(frozen_path, _frozen())

    result = run_direct_lane(
        frozen_path,
        config_loader=load_default_audit_config,
        audit_runner=_runner,
    )

    assert result["frozen_freeze_version"] == "v0.1-frozen-fixture"
    assert result["frozen_freeze_identifier"] == "simple-logic-gold-v0.1-frozen-fixture"
    assert result["frozen_file_sha256"] == f"sha256:{hashlib.sha256(raw).hexdigest()}"
    assert result["summary"] == {
        "atoms": 12,
        "comparable_atoms": 12,
        "matching_comparable_atoms": 12,
        "named_missing_material_noncomparable": 0,
        "parents": 12,
        "comparable_atom_derived_parents": 12,
        "matching_atom_derived_parents": 12,
        "noncomparable_atom_derived_parents": 0,
    }
    parents = result["atom_derived_parent_diagnostics"]
    assert all(parent["atom_derived_cal_parent_verdict"] == "supported" for parent in parents)
    assert all("CAL did not natively" in parent["label"] for parent in parents)


def test_direct_lane_marks_named_missing_parent_noncomparable(tmp_path: Path) -> None:
    frozen_path = tmp_path / "frozen.json"
    _write_frozen(frozen_path, _frozen(retrieval_gap=True))

    result = run_direct_lane(
        frozen_path,
        config_loader=load_default_audit_config,
        audit_runner=_runner,
    )

    atom = result["atoms"][-1]
    parent = result["atom_derived_parent_diagnostics"][-1]
    assert atom["comparable"] is False
    assert parent["comparable"] is False
    assert parent["atom_derived_cal_parent_verdict"] is None
    assert "named missing material" in parent["noncomparable_reason"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda frozen: frozen.pop("freeze_version"),
        lambda frozen: frozen.update({"freeze_identifier": ""}),
        lambda frozen: frozen.update({"world_count": 11}),
        lambda frozen: frozen["frozen_cases"][0]["atoms"][0].update({"relation": "invalid"}),
    ],
)
def test_direct_lane_fails_closed_on_malformed_frozen_contract(tmp_path: Path, mutate: Any) -> None:
    frozen = _frozen()
    mutate(frozen)
    frozen_path = tmp_path / "frozen.json"
    _write_frozen(frozen_path, frozen)

    with pytest.raises(ValueError):
        run_direct_lane(
            frozen_path,
            config_loader=load_default_audit_config,
            audit_runner=_runner,
        )


def test_direct_lane_output_is_absent_or_identical(tmp_path: Path) -> None:
    out = tmp_path / "run.json"
    payload = {"stable": ["output"]}
    _write_absent_or_identical(out, payload)
    _write_absent_or_identical(out, payload)
    with pytest.raises(FileExistsError):
        _write_absent_or_identical(out, {"stable": ["changed"]})


def test_direct_lane_maps_only_comparable_cal_verdicts() -> None:
    assert _map_cal_verdict("supported") == "supports"
    assert _map_cal_verdict("contradicted") == "refutes"
    assert _map_cal_verdict("not_checkable") == "insufficient"
    assert _map_cal_verdict("unsupported") is None


def test_direct_lane_routes_mismatches_without_tuning_gold() -> None:
    assert _defect_route("supports", "supports", True) == "no mismatch"
    assert "without tuning gold" in _defect_route("supports", "insufficient", True)
    assert "not comparable" in _defect_route("retrieval_gap", "insufficient", False)
