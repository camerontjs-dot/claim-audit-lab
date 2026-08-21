"""Classify tests that need local research artifacts excluded from public releases."""

from pathlib import Path

import pytest

_RESEARCH_ARTIFACT_MODULES = frozenset(
    {
        "test_d6_aperture_replay.py",
        "test_decision_model_replay.py",
        "test_e3_a1_aux_prefix_trial.py",
        "test_e3_a1_negative_prefix_trial.py",
        "test_e3_a1_secondary_predicate_trial.py",
        "test_negative_existential_packet_replay.py",
        "test_simple_logic_gold_structured_lane.py",
        "test_slg_entailer_bakeoff.py",
    }
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark replay tests whose inputs are intentionally not distributed publicly."""
    marker = pytest.mark.research_artifact
    for item in items:
        if Path(item.fspath).name in _RESEARCH_ARTIFACT_MODULES:
            item.add_marker(marker)
