import unittest

from run_experiment import critical_metrics, mutation_metrics, system_metrics


class EvaluatorTests(unittest.TestCase):
    def test_system_metrics_unresolved(self):
        cases = [
            {"case_id": "a", "target": "entailment", "family": "f"},
            {"case_id": "b", "target": "neutral", "family": "f"},
        ]
        metrics = system_metrics(cases, {"a": "entailment", "b": "unresolved"})
        self.assertEqual(metrics["correct"], 1)
        self.assertEqual(metrics["coverage"], 0.5)
        self.assertEqual(metrics["selective_accuracy"], 1.0)

    def test_signature_error(self):
        cases = [
            {
                "case_id": "x",
                "target": "neutral",
                "family": "f",
                "critical_error_type": "some_to_all",
            }
        ]
        metrics = critical_metrics(cases, {"x": "entailment"})
        self.assertEqual(metrics["some_to_all"]["semantic_signature_error"], 1)

    def test_mutation_exact_pair(self):
        pairs = [
            {
                "pair_id": "M",
                "before": "a",
                "after": "b",
                "expected_before": "neutral",
                "expected_after": "entailment",
            }
        ]
        self.assertEqual(
            mutation_metrics(pairs, {"a": "neutral", "b": "entailment"})[
                "exact_consistent_pairs"
            ],
            1,
        )


if __name__ == "__main__":
    unittest.main()
