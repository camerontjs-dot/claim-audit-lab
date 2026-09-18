from __future__ import annotations

import importlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUBJECTS = ROOT / "research" / "semantic_family_unseen_pressure_rc2" / "subjects.json"


def test_subject_pins_are_exact_terminal_authority_candidates() -> None:
    subjects = json.loads(SUBJECTS.read_text())
    assert (
        subjects["event_occurrence"]["sha"]
        == "7cd54f9fb28afa6f5fc0fa2d1e9905cd916e0efe"
    )
    assert (
        subjects["direct_event_order"]["sha"]
        == "b163f0faf58c8fe7e2c74e8d9e8618aa2147a359"
    )


def test_frozen_evaluator_discriminates_weak_recombination_strategies() -> None:
    evaluator = importlib.import_module(
        "research.occurrence_order_binding_discriminator_rc0.evaluator"
    )
    observed = evaluator.weak_failures()
    assert all(observed.values())
    assert any(item.startswith("OU01:") for item in observed["field_only"])
    assert any(
        item.startswith("OU04:") or item.startswith("OU05:")
        for item in observed["binding_only"]
    )
    assert any(
        item.startswith("OU02:") or item.startswith("OU03:")
        for item in observed["ignore_warrant"]
    )
    assert any(item.startswith("OB03:") for item in observed["call_order"])
