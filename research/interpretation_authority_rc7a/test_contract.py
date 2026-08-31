from __future__ import annotations

import unittest

from . import gate, oracle
from .build_corpus import build


class ContractTests(unittest.TestCase):
    def test_oracle_and_gate_agree(self):
        for item in build()["cases"]:
            self.assertEqual(oracle.evaluate(item["receipt"]), gate.evaluate(item["receipt"]), item["case_id"])

    def test_invalid_cases_rejected(self):
        for item in build()["invalid_cases"]:
            with self.assertRaises(Exception, msg=item["case_id"]):
                oracle.evaluate(item["receipt"])
            with self.assertRaises(Exception, msg=item["case_id"]):
                gate.evaluate(item["receipt"])

    def test_semantic_unknown_is_not_extraction_failure(self):
        muts = {m["name"]: m for m in build()["mutations"]}
        self.assertEqual(oracle.evaluate(muts["only_membership_to_semantic_unknown"]["after"])["authorization"], "AUTHORIZED")
        self.assertEqual(oracle.evaluate(muts["only_membership_to_extraction_unresolved"]["after"])["authorization"], "NOT_AUTHORIZED")
        self.assertEqual(oracle.evaluate(muts["only_membership_to_insufficient_authority"]["after"])["authorization"], "NOT_AUTHORIZED")


if __name__ == "__main__":
    unittest.main()
