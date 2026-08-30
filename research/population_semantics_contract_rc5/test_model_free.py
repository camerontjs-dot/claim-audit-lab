from __future__ import annotations

import unittest

from .build_corpus import build, sha256


class FreezeTests(unittest.TestCase):
    def test_unique_case_ids(self) -> None:
        ids = [c["case_id"] for c in build()["cases"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_dimensions_present(self) -> None:
        self.assertEqual({c["dimension"] for c in build()["cases"]},
                         {"membership_rule", "subclass", "only_permission", "quantifier", "group_scope", "role_binding", "temporal_membership"})

    def test_ablation_fields_unique(self) -> None:
        fields = [w["field"] for w in build()["ablation_witnesses"]]
        self.assertEqual(len(fields), len(set(fields)))
        self.assertEqual(len(fields), 13)

    def test_metamorphic_pairs(self) -> None:
        self.assertEqual(len(build()["metamorphic_pairs"]), 8)

    def test_frozen_hash(self) -> None:
        self.assertEqual(sha256(), "9b5ce098f92061b310e812e2681ff4a7b710f05c8f3d777395a75c87ef8fa92a")


if __name__ == "__main__": unittest.main()
