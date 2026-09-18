from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research" / "semantic_family_unseen_pressure_rc1"


def test_exactly_nine_frozen_subjects() -> None:
    subjects = json.loads((BASE / "subjects.json").read_text())
    assert len(subjects) == 9
    for spec in subjects.values():
        assert re.fullmatch(r"[0-9a-f]{40}", spec["sha"])


def test_case_ids_are_unique() -> None:
    cases = json.loads((BASE / "cases.json").read_text())
    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))


def test_nine_single_owner_canonical_controls() -> None:
    subjects = json.loads((BASE / "subjects.json").read_text())
    cases = json.loads((BASE / "cases.json").read_text())
    canonical = [case for case in cases if case["class"] == "canonical"]
    assert len(canonical) == 9
    owners = [case["allowed"][0] for case in canonical]
    assert sorted(owners) == sorted(subjects)


def test_all_pressure_cases_require_atomic_silence() -> None:
    cases = json.loads((BASE / "cases.json").read_text())
    pressure = [case for case in cases if case["class"] != "canonical"]
    assert len(pressure) >= 45
    assert all(case["allowed"] == [] for case in pressure)
