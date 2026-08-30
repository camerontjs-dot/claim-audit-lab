import hashlib
import unittest

from build_cohort import EXPECTED_SHA256, build, canonical_bytes, validate
from mechanisms import decompose_for_nli, typed_relation


class FreezeTests(unittest.TestCase):
    def test_cohort_hash_and_balance(self):
        data = build()
        self.assertEqual(validate(data), [])
        self.assertEqual(hashlib.sha256(canonical_bytes(data)).hexdigest(), EXPECTED_SHA256)

    def test_mechanism_falsifier_sentinels(self):
        sentinels = [
            ("Every inspector must file Form A. Mira is an inspector.", "Mira must file Form A.", "entailment"),
            ("Only licensed inspectors may release lots. Niko is a licensed inspector.", "Niko may release lots.", "neutral"),
            ("Only licensed inspectors may release lots. Niko is not a licensed inspector.", "Niko may release lots.", "contradiction"),
            ("Some auditors carry red cards.", "Every auditor carries a red card.", "neutral"),
            ("The Delta team submitted the report. Rhea is a Delta-team member.", "Rhea submitted the report.", "neutral"),
            ("Rhea approved Sol's request.", "Sol approved Rhea's request.", "neutral"),
        ]
        for premise, hypothesis, target in sentinels:
            self.assertEqual(typed_relation(premise, hypothesis)[0], target)

    def test_decomposition_does_not_use_labels(self):
        premise = "Only licensed inspectors may release lots. Niko is a licensed inspector."
        decomposed = decompose_for_nli(premise)
        self.assertIn("Necessary-condition statement", decomposed)
        self.assertNotIn("entailment", decomposed)


if __name__ == "__main__":
    unittest.main()
