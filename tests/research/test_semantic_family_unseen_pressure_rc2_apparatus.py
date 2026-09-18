from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research" / "semantic_family_unseen_pressure_rc2"


def test_exactly_nine_subjects() -> None:
    subjects = json.loads((BASE / "subjects.json").read_text())
    assert len(subjects) == 9
    assert all(re.fullmatch(r"[0-9a-f]{40}", spec["sha"]) for spec in subjects.values())


def test_unique_cases_and_nine_controls() -> None:
    subjects = json.loads((BASE / "subjects.json").read_text())
    cases = json.loads((BASE / "cases.json").read_text())
    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))
    canonical = [case for case in cases if case["class"] == "canonical"]
    assert len(canonical) == 9
    assert sorted(case["allowed"][0] for case in canonical) == sorted(subjects)


def test_pressure_requires_atomic_silence() -> None:
    cases = json.loads((BASE / "cases.json").read_text())
    pressure = [case for case in cases if case["class"] != "canonical"]
    assert len(pressure) >= 45
    assert all(case["allowed"] == [] for case in pressure)
