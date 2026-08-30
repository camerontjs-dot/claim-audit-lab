import unittest
from collections import Counter

from research.nli_independent_calibration_rc2.build_cohort import build, validate


class CohortValidationTests(unittest.TestCase):
    def test_cohort_is_balanced_and_valid(self) -> None:
        cohort = build()
        self.assertEqual(validate(cohort), [])
        rows = cohort["cases"]
        self.assertEqual(len(rows), 72)
        self.assertEqual(
            Counter(row["target"] for row in rows),
            Counter({"entailment": 24, "neutral": 24, "contradiction": 24}),
        )
        self.assertEqual(
            Counter(row["split"] for row in rows),
            Counter({"calibration": 36, "evaluation": 36}),
        )

    def test_every_family_is_balanced_across_split_and_label(self) -> None:
        rows = build()["cases"]
        families = sorted({row["family"] for row in rows})
        self.assertEqual(len(families), 6)
        for family in families:
            subset = [row for row in rows if row["family"] == family]
            self.assertEqual(len(subset), 12)
            self.assertEqual(
                Counter(row["target"] for row in subset),
                Counter({"entailment": 4, "neutral": 4, "contradiction": 4}),
            )
            self.assertEqual(
                Counter(row["split"] for row in subset),
                Counter({"calibration": 6, "evaluation": 6}),
            )


if __name__ == "__main__":
    unittest.main()
