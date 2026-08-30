from __future__ import annotations

import unittest

from .build_corpus import build


class RC5AFreezeTests(unittest.TestCase):
    def test_corrected_case_count(self) -> None:
        self.assertEqual(len(build()["cases"]), 460)

    def test_no_known_impossible_only_authority(self) -> None:
        for case in build()["cases"]:
            if case["dimension"] != "only_permission":
                continue
            a = case["authority"]
            self.assertFalse(
                a["only_population_may"] is True
                and a["membership"] == "non_member"
                and a["explicit_permission"] == "permitted"
            )

    def test_witnesses_preserved(self) -> None:
        self.assertEqual(len(build()["ablation_witnesses"]), 13)
        self.assertEqual(len(build()["metamorphic_pairs"]), 8)

    def test_unique_case_ids(self) -> None:
        ids = [case["case_id"] for case in build()["cases"]]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
