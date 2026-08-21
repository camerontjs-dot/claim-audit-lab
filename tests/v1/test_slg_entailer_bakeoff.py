"""Focused contracts for the preregistered entailer bake-off stop rule."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import scripts.slg_entailer_bakeoff as bakeoff

_ATOM_IDS = (
    "SLG-01-a1",
    "SLG-02-a1",
    "SLG-03-a1",
    "SLG-04-a1",
    "SLG-05-a1",
    "SLG-06-a1",
    "SLG-07-a1",
    "SLG-08-a2",
    "SLG-09-a2",
    "SLG-10-a1",
    "SLG-11-a1",
    "SLG-12-a1",
    "SLG-03-a2",
    "SLG-04-a2",
    "SLG-06-a2",
)
_REFUTATIONS = {"SLG-02-a1", "SLG-05-a1", "SLG-08-a2"}


def _run(*, target: bool, extra_match: bool, refutes: bool = True) -> dict[str, Any]:
    atoms: list[dict[str, Any]] = []
    for atom_id in _ATOM_IDS:
        match = atom_id not in {"SLG-09-a2", "SLG-12-a1"}
        if atom_id == "SLG-09-a2":
            match = target
        if atom_id == "SLG-12-a1":
            match = extra_match
        relation = "refutes" if atom_id in _REFUTATIONS and refutes else "supports"
        atoms.append({"atom_id": atom_id, "match": match, "cal_observed_relation": relation})
    return {
        "atoms": atoms,
        "summary": {"matching_comparable_atoms": sum(atom["match"] for atom in atoms)},
    }


def test_direct_contract_allows_pilot_only_after_every_frozen_condition_passes() -> None:
    baseline = _run(target=False, extra_match=False)
    candidate = _run(target=True, extra_match=False)

    result = bakeoff.evaluate_direct_contract(
        baseline, candidate, deterministic=True, baseline_reproduces_preserved_run_02=True
    )

    assert result["passed"] is True
    assert result["stop_before_pilot"] is False


@pytest.mark.parametrize("reproduces, deterministic", [(False, True), (True, False)])
def test_direct_contract_stops_on_baseline_nonreproduction_or_nondeterminism(
    reproduces: bool, deterministic: bool
) -> None:
    result = bakeoff.evaluate_direct_contract(
        _run(target=False, extra_match=False),
        _run(target=True, extra_match=False),
        deterministic=deterministic,
        baseline_reproduces_preserved_run_02=reproduces,
    )

    assert result["passed"] is False
    assert result["stop_before_pilot"] is True


def test_direct_contract_stops_on_a_lost_currently_correct_relation() -> None:
    candidate = _run(target=True, extra_match=False)
    candidate["atoms"][0]["match"] = False

    result = bakeoff.evaluate_direct_contract(
        _run(target=False, extra_match=False),
        candidate,
        deterministic=True,
        baseline_reproduces_preserved_run_02=True,
    )

    assert result["passed"] is False
    assert "SLG-01-a1" in result["lost_currently_correct_atom_ids"]


def test_direct_contract_stops_on_missing_true_refutation() -> None:
    result = bakeoff.evaluate_direct_contract(
        _run(target=False, extra_match=False),
        _run(target=True, extra_match=False, refutes=False),
        deterministic=True,
        baseline_reproduces_preserved_run_02=True,
    )

    assert result["passed"] is False
    assert result["missing_known_refutations"] == ["SLG-02-a1", "SLG-05-a1", "SLG-08-a2"]


def test_validate_inputs_fails_closed_on_preregistered_hash_mismatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    frozen = tmp_path / "frozen.json"
    frozen.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(bakeoff, "_FREEZE_SHA", "not-the-file-hash")

    with pytest.raises(ValueError, match="frozen-gold"):
        bakeoff._validate_inputs(frozen, tmp_path / "direct.json", tmp_path, tmp_path, tmp_path)


def _v15_contract_config() -> Any:
    # The bake-off contract is preregistered against the v1.5 baseline. The
    # v1.5-era default config differs from the current package default only in
    # `rules_file_sha` (cal-rules-v1.6.0 changed FEATURE logic, no thresholds
    # or model revisions), so swapping the preserved SHA back in reproduces the
    # preregistered `_AUDIT_CONFIG_SHA` exactly.
    from claim_audit_lab.v1.config import load_default_audit_config

    return load_default_audit_config().model_copy(update={"rules_file_sha": bakeoff._RULES_SHA})


def test_validate_inputs_binds_all_frozen_preregistered_artifacts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bakeoff, "load_default_audit_config", _v15_contract_config)
    project = Path(__file__).resolve().parents[3]
    artifacts = project / "outputs"
    bound = bakeoff._validate_inputs(
        artifacts / "simple-logic-gold/v0.1-frozen-rev01-2026-07-15/frozen-gold.json",
        artifacts / "simple-logic-gold/v0.1-frozen-rev01-2026-07-15/direct-cal-run-02.json",
        artifacts / "pilot-001-dev-calibration/run-04-premise-granularity-2026-07-10/gold.dev.yaml",
        project.parent
        / "scaffold-claims-study/workbench/reproduce/build/pilot-001-v2-audit/bundles",
        artifacts
        / "pilot-001-dev-calibration/run-04-premise-granularity-2026-07-10/baseline-v1.5/traces",
    )

    assert bound["frozen_gold_sha256"] == bakeoff._FREEZE_SHA
    assert bound["direct_baseline_sha256"] == bakeoff._DIRECT_SHA
    assert bound["pilot_gold_sha256"] == bakeoff._PILOT_GOLD_SHA
    assert bound["pilot_packet_tree_sha256"] == bakeoff._PILOT_PACKET_TREE_SHA
    assert bound["pilot_trace_tree_sha256"] == bakeoff._PILOT_TRACE_TREE_SHA
    assert bound["audit_config_hash"] == bakeoff._AUDIT_CONFIG_SHA


def test_validate_inputs_fails_closed_on_current_rules_drift() -> None:
    # Under the landed cal-rules-v1.6.0 package the preregistered v1.5 re-run
    # guard must refuse to execute: the KILLED bake-off cannot be accidentally
    # re-run against a drifted candidate. See log.md § 2026-07-15 (bake-off
    # KILL — "do not re-run without new hypothesis").
    project = Path(__file__).resolve().parents[3]
    artifacts = project / "outputs"

    run_04 = artifacts / "pilot-001-dev-calibration/run-04-premise-granularity-2026-07-10"
    with pytest.raises(ValueError, match="preregistered v1.5 baseline"):
        bakeoff._validate_inputs(
            artifacts / "simple-logic-gold/v0.1-frozen-rev01-2026-07-15/frozen-gold.json",
            artifacts / "simple-logic-gold/v0.1-frozen-rev01-2026-07-15/direct-cal-run-02.json",
            run_04 / "gold.dev.yaml",
            project.parent
            / "scaffold-claims-study/workbench/reproduce/build/pilot-001-v2-audit/bundles",
            run_04 / "baseline-v1.5/traces",
        )


def test_run_bakeoff_stops_before_pilot_and_is_repeat_identical(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    baseline = _run(target=False, extra_match=False)
    candidate = _run(target=False, extra_match=False)
    direct_baseline = tmp_path / "direct-baseline.json"
    direct_baseline.write_text(
        json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(bakeoff, "_validate_inputs", lambda *_: {"bound": True})

    def runner(_: Path, model_id: str, __: str) -> dict[str, Any]:
        return baseline if model_id == bakeoff._BASELINE[0] else candidate

    kwargs = {
        "frozen": tmp_path / "frozen.json",
        "direct_baseline": direct_baseline,
        "pilot_packet": tmp_path,
        "pilot_gold": tmp_path / "gold.yaml",
        "pilot_traces": tmp_path,
        "out_dir": tmp_path / "out",
        "direct_runner": runner,
    }
    first = bakeoff.run_bakeoff(**kwargs)
    second = bakeoff.run_bakeoff(**kwargs)

    assert first == second
    assert first["pilot001"] == {"authorized": False, "executed": False}
    assert not (tmp_path / "out" / "pilot-minilm-run-01.json").exists()
