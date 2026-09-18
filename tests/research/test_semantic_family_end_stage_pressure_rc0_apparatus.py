from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research" / "semantic_family_end_stage_pressure_rc0"


def test_exactly_nine_frozen_subjects() -> None:
    subjects = json.loads((BASE / "subjects.json").read_text())
    assert len(subjects) == 9
    for spec in subjects.values():
        assert re.fullmatch(r"[0-9a-f]{40}", spec["sha"])
        assert spec["branch"].startswith("research/")


def test_case_ids_are_unique_and_canonical_owners_are_singletons() -> None:
    cases = json.loads((BASE / "cases.json").read_text())
    ids = [case["case_id"] for case in cases]
    assert len(ids) == len(set(ids))
    canonical = [case for case in cases if case["class"] == "canonical"]
    assert len(canonical) == 9
    assert all(len(case["allowed"]) == 1 for case in canonical)


def test_noncanonical_pressure_cases_have_no_atomic_warrant_allowlist() -> None:
    cases = json.loads((BASE / "cases.json").read_text())
    attacked = [case for case in cases if case["class"] != "canonical"]
    assert attacked
    assert all(case["allowed"] == [] for case in attacked)


def test_each_family_owns_one_canonical_case() -> None:
    subjects = json.loads((BASE / "subjects.json").read_text())
    cases = json.loads((BASE / "cases.json").read_text())
    owners = [
        case["allowed"][0]
        for case in cases
        if case["class"] == "canonical"
    ]
    assert sorted(owners) == sorted(subjects)
