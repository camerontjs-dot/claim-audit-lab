"""Run the preregistered Simple Logic Gold entailer bake-off offline.

This is an additive DEV-only measurement runner.  It swaps only the in-memory
entailer revision supplied to the existing v1 pipeline; it never writes a CAL
rule, config, gold artifact, or production source file.  PILOT-001 is consumed
only after the frozen direct contract clears.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.calibrate import (
    compute_calibration,
    crosswalk_gold,
    load_gold,
    run_calibration,
)
from claim_audit_lab.v1.config import hash_audit_config, load_default_audit_config
from claim_audit_lab.v1.models import AuditConfig, AuditTrace, ModelRevision
from claim_audit_lab.v1.runner import run_default_audit

try:
    from scripts.pilot001_floor_sweep import load_traces
    from scripts.simple_logic_gold_direct_lane import run_direct_lane
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from pilot001_floor_sweep import load_traces  # type: ignore[no-redef]
    from simple_logic_gold_direct_lane import run_direct_lane  # type: ignore[no-redef]

_BASELINE = (
    "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
    "6f5cf0a2b59cabb106aca4c287eed12e357e90eb",
)
_CANDIDATE = (
    "cross-encoder/nli-MiniLM2-L6-H768",
    "b95119ce93d3e065de6214e38cd4a97b0f2f2c6d",
)
_FREEZE_SHA = "cc78b39075d25e331d5905d065870b5382bfdefe1a384f548837a1fd790be1f1"
_DIRECT_SHA = "a5588e803efe802be916f2f7336631852ae286dffef8a4406022b7dabb1cf25e"
_RULES_SHA = "99be5382f0e058a4a514bda96c532f28ad43c11c272864e643b9ccbb8e7d6251"
_PILOT_GOLD_SHA = "31a1451b6e2633d4e948fe5e1cccbea85491fce96683d200633bda2e21f0930b"
_PILOT_PACKET_TREE_SHA = "3e95b31c02ddac3455660de24fccc40a8162a34cdac5546fbff410ac0e4a888b"
_PILOT_TRACE_TREE_SHA = "a507dc2ddb9ab823cc4739ffc4ab35eafd25128b691e5ec86c64a5f186448089"
_AUDIT_CONFIG_SHA = "sha256:98c6609c0b540ab477e9855342806b45ed5650a2b6e6e9745b5bdf12a9a0dbd5"
_KNOWN_REFUTATIONS = ("SLG-02-a1", "SLG-05-a1", "SLG-08-a2")
_TARGET_ATOM = "SLG-09-a2"
_PILOT_EXACT_FLOOR = 62
_PILOT_WEIGHTED_KAPPA_FLOOR = 0.23192019950125634


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(candidate for candidate in path.rglob("*") if candidate.is_file())
    if not files:
        raise ValueError(f"expected non-empty tree: {path}")
    for file_path in files:
        digest.update(file_path.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_absent_or_identical(path: Path, payload: dict[str, Any]) -> None:
    content = _canonical_bytes(payload)
    if path.exists():
        if path.read_bytes() != content:
            raise FileExistsError(f"refusing to overwrite non-identical bake-off receipt: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _require_offline() -> None:
    required = {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    missing = [name for name, expected in required.items() if os.environ.get(name) != expected]
    if missing:
        raise ValueError(f"offline contract requires {', '.join(missing)}=1")


def _config_for(model_id: str, revision: str) -> AuditConfig:
    base = load_default_audit_config()
    if (base.entailer.model_id, base.entailer.hf_revision_sha) != _BASELINE:
        raise ValueError(
            "current entailer model revision does not match the preregistered baseline"
        )
    return base.model_copy(
        update={"entailer": ModelRevision(model_id=model_id, hf_revision_sha=revision)}
    )


def _run_direct(frozen: Path, model_id: str, revision: str) -> dict[str, Any]:
    config = _config_for(model_id, revision)
    output = run_direct_lane(
        frozen,
        config_loader=lambda: config,
        audit_runner=run_default_audit,
    )
    return output


def evaluate_direct_contract(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    deterministic: bool,
    baseline_reproduces_preserved_run_02: bool,
) -> dict[str, Any]:
    """Apply the locked direct stop rule without case-specific repair."""
    baseline_atoms = {atom["atom_id"]: atom for atom in baseline["atoms"]}
    candidate_atoms = {atom["atom_id"]: atom for atom in candidate["atoms"]}
    if set(baseline_atoms) != set(candidate_atoms):
        raise ValueError("baseline/candidate direct atom IDs differ")
    baseline_correct = sorted(
        atom_id for atom_id, atom in baseline_atoms.items() if atom["match"] is True
    )
    lost_correct = sorted(
        atom_id for atom_id in baseline_correct if candidate_atoms[atom_id]["match"] is not True
    )
    missing_refutations = sorted(
        atom_id
        for atom_id in _KNOWN_REFUTATIONS
        if candidate_atoms.get(atom_id, {}).get("cal_observed_relation") != "refutes"
    )
    target_corrected = candidate_atoms.get(_TARGET_ATOM, {}).get("match") is True
    baseline_matches = baseline["summary"]["matching_comparable_atoms"]
    candidate_matches = candidate["summary"]["matching_comparable_atoms"]
    passed = (
        deterministic
        and baseline_reproduces_preserved_run_02
        and baseline_matches == 13
        and candidate_matches > baseline_matches
        and target_corrected
        and not lost_correct
        and not missing_refutations
    )
    return {
        "baseline_matching_comparable_atoms": baseline_matches,
        "candidate_matching_comparable_atoms": candidate_matches,
        "target_atom": _TARGET_ATOM,
        "target_corrected": target_corrected,
        "baseline_correct_atom_ids": baseline_correct,
        "lost_currently_correct_atom_ids": lost_correct,
        "known_refutations": list(_KNOWN_REFUTATIONS),
        "missing_known_refutations": missing_refutations,
        "deterministic": deterministic,
        "baseline_reproduces_preserved_run_02": baseline_reproduces_preserved_run_02,
        "passed": passed,
        "stop_before_pilot": not passed,
    }


def _gold_degree_map(gold: Any) -> dict[str, str]:
    return {
        claim.claim_id: crosswalk_gold(claim.gold_verdict, claim.gold_flags).support_verdict
        for claim in gold.claims
    }


def evaluate_pilot_contract(
    baseline: dict[str, AuditTrace],
    candidate: dict[str, AuditTrace],
    gold: Any,
    baseline_config: AuditConfig,
    candidate_config: AuditConfig,
    *,
    deterministic: bool,
) -> dict[str, Any]:
    """Apply the preregistered conditional PILOT-001 floors and safety checks."""
    baseline_result = compute_calibration(baseline, gold, baseline_config)
    candidate_result = compute_calibration(candidate, gold, candidate_config)
    gold_by_id = _gold_degree_map(gold)
    if set(candidate) != set(gold_by_id) or set(baseline) != set(gold_by_id):
        raise ValueError("PILOT traces and gold do not align")
    new_supported_to_contradicted = sorted(
        claim_id
        for claim_id, gold_degree in gold_by_id.items()
        if gold_degree == "supported"
        and baseline[claim_id].verdict.support_verdict != "contradicted"
        and candidate[claim_id].verdict.support_verdict == "contradicted"
    )
    lost_correct_contradictions = sorted(
        claim_id
        for claim_id, gold_degree in gold_by_id.items()
        if gold_degree == "contradicted"
        and baseline[claim_id].verdict.support_verdict == "contradicted"
        and candidate[claim_id].verdict.support_verdict != "contradicted"
    )
    agreement = candidate_result.agreement
    passed = (
        deterministic
        and agreement.n_agree >= _PILOT_EXACT_FLOOR
        and agreement.weighted_kappa >= _PILOT_WEIGHTED_KAPPA_FLOOR
        and not new_supported_to_contradicted
        and not lost_correct_contradictions
    )
    return {
        "baseline_metrics": baseline_result.model_dump(mode="json"),
        "candidate_metrics": candidate_result.model_dump(mode="json"),
        "exact_floor": _PILOT_EXACT_FLOOR,
        "weighted_kappa_floor": _PILOT_WEIGHTED_KAPPA_FLOOR,
        "new_gold_supported_to_cal_contradicted": new_supported_to_contradicted,
        "lost_correct_contradictions": lost_correct_contradictions,
        "deterministic": deterministic,
        "passed": passed,
    }


def _runtime_metadata() -> dict[str, Any]:
    packages = ("torch", "transformers", "sentence-transformers")
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "packages": {name: importlib.metadata.version(name) for name in packages},
        "workbench_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip(),
    }


def _validate_inputs(
    frozen: Path,
    direct_baseline: Path,
    pilot_gold: Path,
    pilot_packet: Path,
    pilot_traces: Path,
) -> dict[str, Any]:
    if _sha256(frozen) != _FREEZE_SHA:
        raise ValueError("frozen-gold.json SHA-256 does not match the preregistered contract")
    if _sha256(direct_baseline) != _DIRECT_SHA:
        raise ValueError("direct run-02 SHA-256 does not match the preregistered contract")
    if _sha256(pilot_gold) != _PILOT_GOLD_SHA:
        raise ValueError("PILOT-001 gold SHA-256 does not match the preregistered contract")
    if _tree_sha256(pilot_packet) != _PILOT_PACKET_TREE_SHA:
        raise ValueError("PILOT-001 packet tree SHA-256 does not match the preregistered contract")
    if _tree_sha256(pilot_traces) != _PILOT_TRACE_TREE_SHA:
        raise ValueError("PILOT-001 trace tree SHA-256 does not match the preregistered contract")
    config = load_default_audit_config()
    if config.rules_file_sha != _RULES_SHA:
        raise ValueError("current rules SHA does not match the preregistered v1.5 baseline")
    if hash_audit_config(config) != _AUDIT_CONFIG_SHA:
        raise ValueError("current audit config hash does not match the preregistered contract")
    if (config.entailer.model_id, config.entailer.hf_revision_sha) != _BASELINE:
        raise ValueError(
            "current entailer model revision does not match the preregistered baseline"
        )
    return {
        "frozen_gold_sha256": _sha256(frozen),
        "direct_baseline_sha256": _sha256(direct_baseline),
        "pilot_gold_sha256": _sha256(pilot_gold),
        "pilot_packet_tree_sha256": _tree_sha256(pilot_packet),
        "pilot_trace_tree_sha256": _tree_sha256(pilot_traces),
        "audit_config_hash": hash_audit_config(config),
        "rules_file_sha256": config.rules_file_sha,
        "baseline": {"model_id": _BASELINE[0], "hf_revision_sha": _BASELINE[1]},
        "candidate": {"model_id": _CANDIDATE[0], "hf_revision_sha": _CANDIDATE[1]},
    }


def run_bakeoff(
    *,
    frozen: Path,
    direct_baseline: Path,
    pilot_packet: Path,
    pilot_gold: Path,
    pilot_traces: Path,
    out_dir: Path,
    direct_runner: Callable[[Path, str, str], dict[str, Any]] = _run_direct,
) -> dict[str, Any]:
    """Run the locked trial, stopping before PILOT-001 when direct criteria fail."""
    _require_offline()
    inputs = _validate_inputs(frozen, direct_baseline, pilot_gold, pilot_packet, pilot_traces)
    baseline_one = direct_runner(frozen, *_BASELINE)
    baseline_two = direct_runner(frozen, *_BASELINE)
    candidate_one = direct_runner(frozen, *_CANDIDATE)
    candidate_two = direct_runner(frozen, *_CANDIDATE)
    for filename, payload in (
        ("direct-baseline-run-01.json", baseline_one),
        ("direct-baseline-run-02.json", baseline_two),
        ("direct-minilm-run-01.json", candidate_one),
        ("direct-minilm-run-02.json", candidate_two),
    ):
        _write_absent_or_identical(out_dir / filename, payload)
    historic = json.loads(direct_baseline.read_text(encoding="utf-8"))
    baseline_reproduces = baseline_one == historic and baseline_two == historic
    direct = evaluate_direct_contract(
        baseline_one,
        candidate_one,
        deterministic=(
            _canonical_bytes(baseline_one) == _canonical_bytes(baseline_two)
            and _canonical_bytes(candidate_one) == _canonical_bytes(candidate_two)
        ),
        baseline_reproduces_preserved_run_02=baseline_reproduces,
    )
    receipt: dict[str, Any] = {
        "schema_version": "slg-entailer-bakeoff-v0.1",
        "label": (
            "DEV craft evidence only; not validation, representative accuracy, or gate evidence"
        ),
        "inputs": inputs,
        "runtime": _runtime_metadata(),
        "direct": direct,
        "pilot001": {"authorized": direct["passed"], "executed": False},
    }
    if direct["passed"]:
        candidate_config = _config_for(*_CANDIDATE)
        gold = load_gold(pilot_gold)
        pilot_one_result, pilot_one = run_calibration(
            pilot_packet,
            gold,
            candidate_config,
            auditor=run_default_audit,
            deviations_dir=out_dir / "pilot-minilm-run-01-deviations",
        )
        pilot_two_result, pilot_two = run_calibration(
            pilot_packet,
            gold,
            candidate_config,
            auditor=run_default_audit,
            deviations_dir=out_dir / "pilot-minilm-run-02-deviations",
        )
        pilot_one_payload = {
            "result": pilot_one_result.model_dump(mode="json"),
            "traces": {
                key: value.model_dump(mode="json") for key, value in sorted(pilot_one.items())
            },
        }
        pilot_two_payload = {
            "result": pilot_two_result.model_dump(mode="json"),
            "traces": {
                key: value.model_dump(mode="json") for key, value in sorted(pilot_two.items())
            },
        }
        _write_absent_or_identical(out_dir / "pilot-minilm-run-01.json", pilot_one_payload)
        _write_absent_or_identical(out_dir / "pilot-minilm-run-02.json", pilot_two_payload)
        pilot = evaluate_pilot_contract(
            load_traces(pilot_traces),
            pilot_one,
            gold,
            load_default_audit_config(),
            candidate_config,
            deterministic=(
                _canonical_bytes(pilot_one_payload) == _canonical_bytes(pilot_two_payload)
            ),
        )
        pilot["executed"] = True
        receipt["pilot001"] = pilot
    _write_absent_or_identical(out_dir / "receipt.json", receipt)
    return receipt


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, required=True)
    parser.add_argument("--direct-baseline", type=Path, required=True)
    parser.add_argument("--pilot-packet", type=Path, required=True)
    parser.add_argument("--pilot-gold", type=Path, required=True)
    parser.add_argument("--pilot-traces", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = run_bakeoff(**vars(args))
    except (FileExistsError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(
        json.dumps({"direct": receipt["direct"], "pilot001": receipt["pilot001"]}, sort_keys=True)
    )


if __name__ == "__main__":
    _main()
