"""Focused no-inference checks for the preregistered A1 ``neg`` trial."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.e3_a1_aux_prefix_trial as _aux_module
import scripts.e3_a1_negative_prefix_trial as _neg_module
import scripts.e3_a1_secondary_predicate_trial as _sec_module
import scripts.simple_logic_gold_structured_lane as _lane_module
from claim_audit_lab.v1.config import load_default_audit_config
from scripts.e3_a1_negative_prefix_trial import (
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


def test_negative_imperatives_and_declaratives_follow_fixed_canaries() -> None:
    assert candidate_sentence_type("Never release the batch.") == "imperative"
    assert candidate_sentence_type("Do not release the batch.") == "declarative"
    assert candidate_sentence_type("Not all valves passed inspection.") == "declarative"
    assert candidate_sentence_type("No release occurred.") == "declarative"
    assert candidate_sentence_type("The batch was not released.") == "declarative"


def test_complete_canary_set_preserves_do_not_failure() -> None:
    report = canary_report()
    assert report["denominator"] == 13
    assert report["matching"] == 12
    assert report["failures"] == [
        {
            "claim": "Do not release the batch.",
            "expected": "imperative",
            "observed": "declarative",
        }
    ]


def test_replays_are_identical_to_prior_improvement_but_candidate_iterates() -> None:
    summary, candidate_suite = build_trial_payload(_PROJECT)
    assert summary["criteria"] == {
        "canaries": False,
        "e3_candidate_byte_identity": True,
        "pilot_dev_replay_identity": True,
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


def test_trial_writes_repeatable_absent_or_identical_artifacts(tmp_path: Path) -> None:
    first = run_trial(_PROJECT, tmp_path)
    summary_bytes = (tmp_path / "trial-summary.json").read_bytes()
    suite_bytes = (tmp_path / "e3-candidate-suite.json").read_bytes()
    second = run_trial(_PROJECT, tmp_path)
    assert first == second
    assert (tmp_path / "trial-summary.json").read_bytes() == summary_bytes
    assert (tmp_path / "e3-candidate-suite.json").read_bytes() == suite_bytes
    assert json.loads(summary_bytes)["all_criteria_pass"] is False
