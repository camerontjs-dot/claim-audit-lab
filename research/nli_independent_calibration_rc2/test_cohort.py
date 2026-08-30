from collections import Counter

from research.nli_independent_calibration_rc2.build_cohort import build, validate


def test_cohort_is_balanced_and_valid() -> None:
    cohort = build()
    assert validate(cohort) == []
    rows = cohort["cases"]
    assert len(rows) == 72
    assert Counter(row["target"] for row in rows) == {
        "entailment": 24,
        "neutral": 24,
        "contradiction": 24,
    }
    assert Counter(row["split"] for row in rows) == {
        "calibration": 36,
        "evaluation": 36,
    }


def test_every_family_is_balanced_across_split_and_label() -> None:
    rows = build()["cases"]
    families = sorted({row["family"] for row in rows})
    assert len(families) == 6
    for family in families:
        subset = [row for row in rows if row["family"] == family]
        assert len(subset) == 12
        assert Counter(row["target"] for row in subset) == {
            "entailment": 4,
            "neutral": 4,
            "contradiction": 4,
        }
        assert Counter(row["split"] for row in subset) == {
            "calibration": 6,
            "evaluation": 6,
        }
