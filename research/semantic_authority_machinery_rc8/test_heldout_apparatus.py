from collections import Counter

from .heldout_cohort import build_heldout_cases


def test_heldout_structure_without_running_candidate() -> None:
    cases = build_heldout_cases()
    ids = [c["case_id"] for c in cases]
    assert len(cases) == 68
    assert len(ids) == len(set(ids))
    counts = Counter(c["family"] for c in cases)
    assert set(counts) == {"population_membership", "comparison", "event_ordering", "permission_composition"}
    assert all(counts[f] >= 15 for f in counts)
    states = Counter(c["expected_authority"] for c in cases)
    assert states["WARRANTED"] > 0
    assert states["REJECTED"] > 0
    assert states["UNRESOLVED"] > 0
    assert states["NO_ASSESSMENT"] == 1


def test_heldout_monotonicity_pairs_exist() -> None:
    by_id = {c["case_id"]: c for c in build_heldout_cases()}
    for family in ("population_membership", "comparison", "event_ordering", "permission_composition"):
        base = f"H-{family}-BASE"
        assert by_id[base]["expected_authority"] == by_id[f"{base}-BANK8"]["expected_authority"] == "WARRANTED"
        assert by_id[f"{base}-APPUNK"]["expected_authority"] == by_id[f"{base}-APPUNK-BANK8"]["expected_authority"] == "UNRESOLVED"
