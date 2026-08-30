"""Model-free unit tests for frozen RC3 candidate mechanisms.

These fixtures are not members of COHORT.json and are used only to verify the
predeclared grammar/invariants before any cohort execution.
"""

from __future__ import annotations

import unittest

from mechanisms import decompose_for_nli, typed_relation


class ScopedRuleMechanismTests(unittest.TestCase):
    def test_bare_exception_does_not_become_negation(self) -> None:
        premise = "All pharmacists must badge in, except Kira."
        relation, reason, state = typed_relation(
            premise, "Kira must not badge in."
        )
        self.assertEqual(relation, "neutral")
        self.assertIn("exclusion", reason)
        self.assertTrue(state["exclusions"])

    def test_explicit_opposite_is_distinct(self) -> None:
        premise = "All pharmacists must badge in, except Kira, who must not badge in."
        relation, _, _ = typed_relation(premise, "Kira must not badge in.")
        self.assertEqual(relation, "entailment")
        relation, _, _ = typed_relation(premise, "Kira must badge in.")
        self.assertEqual(relation, "contradiction")

    def test_alternate_process_defeats_no_process(self) -> None:
        premise = (
            "All specimens follow Route A, except Lot K, which follows Route B."
        )
        relation, _, state = typed_relation(premise, "Lot K follows no route.")
        self.assertEqual(relation, "contradiction")
        self.assertTrue(state["alternate_processes"])

    def test_narrow_exemption_does_not_broaden(self) -> None:
        premise = "Priority parcels are exempt from scan logging."
        relation, _, _ = typed_relation(
            premise, "Priority parcels are exempt from temperature control."
        )
        self.assertEqual(relation, "neutral")

    def test_only_permission_excludes_known_nonmember(self) -> None:
        premise = "Only directors may open the safe. Kira is not a director."
        relation, _, _ = typed_relation(premise, "Kira may open the safe.")
        self.assertEqual(relation, "contradiction")
        relation, _, _ = typed_relation(premise, "Kira may not open the safe.")
        self.assertEqual(relation, "entailment")

    def test_decomposition_surfaces_scope_without_opposite(self) -> None:
        premise = "All pharmacists must badge in, except Kira."
        decomposed = decompose_for_nli(premise)
        self.assertIn("outside the scope", decomposed)
        self.assertNotIn("Kira must not badge in", decomposed)

    def test_unsupported_text_is_unresolved(self) -> None:
        relation, reason, state = typed_relation(
            "The room felt unusually quiet.",
            "Kira is exempt from a rule.",
        )
        self.assertEqual(relation, "unresolved")
        self.assertFalse(state["recognized_reasons"])
        self.assertIn("no frozen", reason)


if __name__ == "__main__":
    unittest.main()
