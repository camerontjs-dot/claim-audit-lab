"""Tests for the model-free RC3 cohort validator."""

from __future__ import annotations

import unittest

from build_cohort import frozen_sha256
from validate_cohort import EXPECTED_SHA256, load_and_validate


class CohortFreezeTests(unittest.TestCase):
    def test_exact_frozen_hash(self) -> None:
        self.assertEqual(frozen_sha256(), EXPECTED_SHA256)

    def test_schema_and_balancing(self) -> None:
        data = load_and_validate()
        primary = [case for case in data["cases"] if case["primary"]]
        self.assertEqual(len(primary), 84)
        self.assertEqual(len(data["mutation_pairs"]), 10)


if __name__ == "__main__":
    unittest.main()
