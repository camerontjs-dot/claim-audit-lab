"""Focused no-inference checks for the preregistered E3 A1 craft trial."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.e3_a1_aux_prefix_trial as _aux_module
import scripts.e3_a1_negative_prefix_trial as _neg_module
import scripts.e3_a1_secondary_predicate_trial as _sec_module
import scripts.simple_logic_gold_structured_lane as _lane_module
from claim_audit_lab.v1.config import load_default_audit_config
from scripts.e3_a1_secondary_predicate_trial import (
    build_trial_payload,
    canary_report,
    candidate_sentence_type,
    run_trial,
)

_PROJECT = Path(__file__).resolve().parents[3]
_V15_RULES_SHA = "99be5382f0e058a4a514bda96c532f28ad43c11c272864e643b9ccbb8e7d6251"


@pytest.fixture(autouse=True)
def _pin_v15_contract_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replay the preserved v1.5-baseline evidence under its era-correct config.

    The A1 trials preregistered their E3/PILOT replays against the v1.5
    default config. The landed ``cal-rules-v1.6.0`` guard changed only
    ``rules_file_sha``, so swapping the preserved SHA back in reproduces every
    recorded request/config hash exactly.
    """
    v15 = load_default_audit_config().model_copy(update={"rules_file_sha": _V15_RULES_SHA})
    for module in (_aux_module, _neg_module, _sec_module, _lane_module):
        monkeypatch.setattr(module, "load_default_audit_config", lambda: v15, raising=False)


def test_candidate_recovers_declared_false_imperatives_and_v2_shape() -> None:
    assert (
        candidate_sentence_type(
            "The guidance links annual reviews to statistical process control and trend analysis."
        )
        == "declarative"
    )
    assert (
        candidate_sentence_type(
            "Change control systems must document impacts and involve the quality unit."
        )
        == "declarative"
    )
    assert candidate_sentence_type("Valve V1 passed inspection.") == "declarative"
    assert candidate_sentence_type("Valve V2 passed inspection.") == "declarative"
    assert candidate_sentence_type("Valve V3 passed inspection.") == "declarative"


def test_candidate_preserves_positive_imperatives_but_records_fixed_negative_canary_failure() -> (
    None
):
    assert candidate_sentence_type("Validate the system before release.") == "imperative"
    assert candidate_sentence_type("Please validate the system before release.") == "imperative"
    assert candidate_sentence_type("Kindly validate the system before release.") == "imperative"
    assert candidate_sentence_type("Never release the batch.") == "declarative"
    report = canary_report()
    assert report["matching"] == 8
    assert report["denominator"] == 9
    assert report["failures"] == [
        {
            "claim": "Never release the batch.",
            "expected": "imperative",
            "observed": "declarative",
        }
    ]


def test_recorded_trace_replays_meet_e3_and_pilot_diagnostics_but_trial_iterates() -> None:
    summary, candidate_suite = build_trial_payload(_PROJECT)
    assert summary["criteria"] == {
        "canaries": False,
        "e3_replay": True,
        "pilot_dev_replay": True,
    }
    assert summary["recommended_verdict"] == "iterate"
    assert summary["e3"]["baseline_scores"]["frozen_semantic_targets"]["matching"] == 14
    assert summary["e3"]["baseline_scores"]["runtime_construction_atoms"]["matching"] == 18
    assert summary["e3"]["baseline_scores"]["frozen_parents"]["matching"] == 9
    assert summary["pilot_001_dev"]["candidate_metrics"]["exact_agree"] == 64
    assert summary["pilot_001_dev"]["diff_summary"]["regressed"] == 0
    assert candidate_suite["wording_variants"]["frozen_semantic_targets"]["matching"] == 3


def test_trial_writes_absent_or_identical_deterministic_artifacts(tmp_path: Path) -> None:
    first = run_trial(_PROJECT, tmp_path)
    first_summary_bytes = (tmp_path / "trial-summary.json").read_bytes()
    first_suite_bytes = (tmp_path / "e3-candidate-suite.json").read_bytes()
    second = run_trial(_PROJECT, tmp_path)
    assert first == second
    assert (tmp_path / "trial-summary.json").read_bytes() == first_summary_bytes
    assert (tmp_path / "e3-candidate-suite.json").read_bytes() == first_suite_bytes
    assert json.loads(first_summary_bytes)["all_criteria_pass"] is False
