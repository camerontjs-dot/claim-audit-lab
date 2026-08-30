"""Model-free tests for the post-freeze RC3 evaluator."""

from __future__ import annotations

import unittest

from research.exception_scoped_rule_semantics_rc3.run_experiment import (
    critical_error_metrics,
    matched_pair_metrics,
    mutation_metrics,
    system_metrics,
)
from research.nli_independent_calibration_rc2.run_calibration import adverse_conservative


class RC3EvaluatorTests(unittest.TestCase):
    def test_rc1_adverse_rule_is_unchanged(self) -> None:
        self.assertEqual(
            adverse_conservative(["contradiction", "contradiction", "contradiction"]),
            "contradiction",
        )
        self.assertEqual(
            adverse_conservative(["entailment", "entailment", "neutral"]),
            "entailment",
        )
        self.assertEqual(
            adverse_conservative(["neutral", "neutral", "entailment"]),
            "neutral",
        )
        self.assertEqual(
            adverse_conservative(["contradiction", "neutral", "neutral"]),
            "unresolved",
        )

    def test_system_metrics_preserve_false_adverse(self) -> None:
        cases = [
            {"case_id": "a", "target": "neutral", "family": "f"},
            {"case_id": "b", "target": "contradiction", "family": "f"},
            {"case_id": "c", "target": "entailment", "family": "f"},
        ]
        metrics = system_metrics(
            cases,
            {"a": "contradiction", "b": "neutral", "c": "entailment"},
        )
        self.assertEqual(metrics["correct"], 1)
        self.assertEqual(metrics["false_adverse"], 1)
        self.assertEqual(metrics["neutral_to_contradiction"], 1)
        self.assertEqual(metrics["contradiction_to_neutral"], 1)

    def test_critical_signature_is_specific(self) -> None:
        cases = [
            {
                "case_id": "x",
                "target": "neutral",
                "family": "f",
                "critical_error_type": "exception_not_negation",
            }
        ]
        bad = critical_error_metrics(cases, {"x": "entailment"})
        other_wrong = critical_error_metrics(cases, {"x": "contradiction"})
        self.assertEqual(
            bad["exception_not_negation"]["semantic_signature_error"], 1
        )
        self.assertEqual(
            other_wrong["exception_not_negation"]["semantic_signature_error"], 0
        )
        self.assertEqual(other_wrong["exception_not_negation"]["any_incorrect"], 1)

    def test_mutation_requires_both_expected_relations(self) -> None:
        pairs = [
            {
                "pair_id": "m",
                "before": "a",
                "after": "b",
                "expected_before": "neutral",
                "expected_after": "entailment",
                "transformation": "test",
            }
        ]
        good = mutation_metrics(pairs, {"a": "neutral", "b": "entailment"})
        bad = mutation_metrics(pairs, {"a": "neutral", "b": "neutral"})
        self.assertEqual(good["mutation_consistency"], 1.0)
        self.assertEqual(bad["mutation_consistency"], 0.0)

    def test_matched_pair_requires_both_gold_relations(self) -> None:
        cases = [
            {"case_id": "a", "premise": "same", "target": "neutral"},
            {"case_id": "b", "premise": "same", "target": "contradiction"},
        ]
        good = matched_pair_metrics(cases, {"a": "neutral", "b": "contradiction"})
        bad = matched_pair_metrics(cases, {"a": "neutral", "b": "neutral"})
        self.assertEqual(good["matched_pair_consistency"], 1.0)
        self.assertEqual(bad["matched_pair_consistency"], 0.0)


if __name__ == "__main__":
    unittest.main()
