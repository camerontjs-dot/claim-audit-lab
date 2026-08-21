"""Focused no-inference checks for the run-06 A1 landing verification script."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import scripts.pilot001_a1_landing_run06 as run06
from claim_audit_lab.v1.config import load_default_audit_config

_PROTOTYPE_AGREEMENT = {
    "cohens_kappa": 0.21433624145248756,
    "exact_agreement": 0.6530612244897959,
    "gwet_ac2": 0.9530972403174212,
    "kappa_ci_high": 0.4277499446909906,
    "kappa_ci_low": 0.0009225382139844973,
    "n_agree": 64,
    "n_total": 98,
    "on_scale_n": 72,
    "weighted_kappa": 0.2336719883889784,
}


def _expected_rows() -> list[dict[str, Any]]:
    return [
        {"claim_id": claim_id, **expected} for claim_id, expected in run06._EXPECTED_CHANGES.items()
    ]


def _summary() -> dict[str, Any]:
    return {
        "recovered": 2,
        "regressed": 0,
        "changed_but_still_miss": 0,
        "new_gold_supported_to_cal_contradicted": 0,
    }


def _prototype_result(tmp_path: Path) -> Path:
    path = tmp_path / "calibration-result.json"
    path.write_text(
        json.dumps({"agreement": _PROTOTYPE_AGREEMENT}, sort_keys=True), encoding="utf-8"
    )
    return path


def test_verify_landing_accepts_the_exact_prototype_shape(tmp_path: Path) -> None:
    receipt = run06.verify_landing(
        _expected_rows(),
        _summary(),
        _prototype_result(tmp_path),
        {"agreement": _PROTOTYPE_AGREEMENT},
    )
    assert any("exact prototype match" in line for line in receipt)


def test_verify_landing_rejects_an_extra_changed_claim(tmp_path: Path) -> None:
    rows = [*_expected_rows(), {"claim_id": "rsh-extra-c001"}]
    with pytest.raises(ValueError, match="changed-claim set"):
        run06.verify_landing(rows, _summary(), _prototype_result(tmp_path), {})


def test_verify_landing_rejects_a_verdict_deviation(tmp_path: Path) -> None:
    rows = _expected_rows()
    rows[0] = {**rows[0], "candidate_verdict": "contradicted"}
    with pytest.raises(ValueError, match="candidate_verdict"):
        run06.verify_landing(rows, _summary(), _prototype_result(tmp_path), {})


def test_verify_landing_rejects_an_f4_case(tmp_path: Path) -> None:
    summary = {**_summary(), "new_gold_supported_to_cal_contradicted": 1}
    with pytest.raises(ValueError, match="new_gold_supported_to_cal_contradicted"):
        run06.verify_landing(_expected_rows(), summary, _prototype_result(tmp_path), {})


def test_verify_landing_rejects_metric_drift(tmp_path: Path) -> None:
    drifted = {"agreement": {**_PROTOTYPE_AGREEMENT, "n_agree": 63}}
    with pytest.raises(ValueError, match="agreement metrics differ"):
        run06.verify_landing(_expected_rows(), _summary(), _prototype_result(tmp_path), drifted)


# The run-06 receipt is bound to the v1.6.0 surface it verified. The package
# has since moved to cal-rules-v1.7.0 (negation consistency), so the guard is
# exercised under its era-correct pin — same convention as the A1 trial and
# entailer-bakeoff era pins.
_V16_RULES_SHA = "eaf8b463294c1f71a24fc9bd4c0719985c12650d605c0d7390c17abc89f63305"


def test_landed_surface_guard_accepts_v16_era_and_rejects_v15_pin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        run06,
        "load_rules_file",
        lambda: ({"rules_version": "cal-rules-v1.6.0"}, _V16_RULES_SHA),
    )
    config = load_default_audit_config().model_copy(update={"rules_file_sha": _V16_RULES_SHA})
    run06._assert_landed_surface(config)

    stale = config.model_copy(update={"rules_file_sha": run06._V15_RULES_SHA})
    with pytest.raises(ValueError, match="nothing landed"):
        run06._assert_landed_surface(stale)


def test_landed_surface_guard_rejects_a_moved_on_package() -> None:
    # Under the current v1.7.0 surface the run-06 verifier must refuse to run:
    # its receipt binds the v1.6.0 landing, not whatever ships now.
    with pytest.raises(ValueError, match="is not 'cal-rules-v1.6.0'"):
        run06._assert_landed_surface(load_default_audit_config())


def test_v15_baseline_guard_rejects_foreign_trace_hashes() -> None:
    config = load_default_audit_config()

    class _FakeTrace:
        audit_config_hash = "sha256:" + "0" * 64

    with pytest.raises(ValueError, match="not the v1.5 contract"):
        run06._assert_v15_baseline({"c-1": _FakeTrace()}, config)  # type: ignore[dict-item]
