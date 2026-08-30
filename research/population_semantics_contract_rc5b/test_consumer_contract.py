from __future__ import annotations

import unittest

from .consumer import relation


def subclass_case(edge: str, base: str, status: str, target: str) -> dict:
    return {
        "case_id": "fixture",
        "dimension": "subclass",
        "authority": {"entity": "e0", "membership_population": base, "membership": status, "subclass_edge": edge},
        "query": {"kind": "membership", "entity": "e0", "population": target},
    }


class SubclassContractTests(unittest.TestCase):
    def test_negative_inheritance_a_subset_b(self) -> None:
        self.assertEqual(relation(subclass_case("A_sub_B", "B", "non_member", "A")), "contradiction")

    def test_negative_inheritance_b_subset_a(self) -> None:
        self.assertEqual(relation(subclass_case("B_sub_A", "A", "non_member", "B")), "contradiction")

    def test_nonmember_subclass_does_not_imply_nonmember_superclass(self) -> None:
        self.assertEqual(relation(subclass_case("A_sub_B", "A", "non_member", "B")), "neutral")

    def test_member_superclass_does_not_imply_member_subclass(self) -> None:
        self.assertEqual(relation(subclass_case("A_sub_B", "B", "member", "A")), "neutral")


if __name__ == "__main__":
    unittest.main()
