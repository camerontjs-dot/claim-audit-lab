"""Self-authored sentinels for Interpretation Authority Contract v1.

These tests are derived only from the public contract and Appendix A.
"""
from __future__ import annotations

import os
import sys
import unittest

HERE = os.path.dirname(__file__)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from interpret import interpret  # noqa: E402


FAMILY_FIELDS = {
    "only_permission": {
        "entity",
        "population",
        "membership",
        "predicate",
        "only_population_may",
        "explicit_permission",
    },
    "role_binding": {"predicate", "subject", "object", "polarity"},
    "quantifier": {"population", "predicate", "quantifier", "polarity"},
}


class ReceiptAssertions(unittest.TestCase):
    def assert_valid_receipt(self, source, receipt):
        self.assertEqual(receipt["status"], "receipt")
        self.assertIn(receipt["family"], FAMILY_FIELDS)
        self.assertEqual(set(receipt["fields"]), FAMILY_FIELDS[receipt["family"]])
        for name, observation in receipt["fields"].items():
            self.assertIn(
                observation["status"],
                {
                    "established",
                    "semantic_unknown",
                    "extraction_unresolved",
                    "insufficient_authority",
                },
            )
            if observation["status"] in {"established", "semantic_unknown"}:
                self.assertIsNotNone(observation["value"], name)
                self.assertIsNotNone(observation["span"], name)
                self.assertIsNotNone(observation["warrant"], name)
                span = observation["span"]
                self.assertGreaterEqual(span["start"], 0)
                self.assertGreater(span["end"], span["start"])
                self.assertLessEqual(span["end"], len(source))
                self.assertEqual(source[span["start"]:span["end"]], span["text"])
            else:
                self.assertIsNone(observation["value"], name)
                self.assertIsNone(observation["span"], name)
                self.assertIsNone(observation["warrant"], name)

            if observation["status"] == "semantic_unknown":
                self.assertEqual(receipt["family"], "only_permission")
                self.assertIn(name, {"membership", "explicit_permission"})
                self.assertEqual(observation["value"], "unknown")
                self.assertEqual(observation["warrant"], "explicit_unknown_assertion")


class PermissionSentinels(ReceiptAssertions):
    QUERY = {
        "kind": "permission",
        "entity": "mira",
        "population": "licensed inspectors",
        "predicate": "release batch a",
    }

    def test_established_appendix_construction(self):
        source = (
            "Only licensed inspectors may release batch a. "
            "Mira is a member of the licensed inspectors. "
            "Mira is authorized to release batch a."
        )
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        fields = receipt["fields"]
        self.assertEqual(fields["entity"]["value"], "mira")
        self.assertEqual(fields["population"]["value"], "licensed inspectors")
        self.assertEqual(fields["membership"]["value"], "member")
        self.assertEqual(fields["predicate"]["value"], "release batch a")
        self.assertIs(fields["only_population_may"]["value"], True)
        self.assertEqual(fields["explicit_permission"]["value"], "permitted")

    def test_explicit_unknown_is_semantic_unknown(self):
        source = (
            "Only licensed inspectors may release batch a. "
            "It is unknown whether Mira is a member of the licensed inspectors. "
            "Whether Mira is permitted to release batch a is unknown."
        )
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        self.assertEqual(
            receipt["fields"]["membership"]["status"], "semantic_unknown"
        )
        self.assertEqual(
            receipt["fields"]["explicit_permission"]["status"], "semantic_unknown"
        )

    def test_absence_is_insufficient_not_unknown(self):
        source = (
            "Only licensed inspectors may release batch a. "
            "Mira works beside licensed inspectors."
        )
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        self.assertEqual(
            receipt["fields"]["membership"]["status"], "insufficient_authority"
        )
        self.assertEqual(
            receipt["fields"]["explicit_permission"]["status"],
            "insufficient_authority",
        )

    def test_necessary_condition_is_not_permission_grant(self):
        source = "Only licensed inspectors may release batch a. Mira is a licensed inspector."
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        self.assertEqual(receipt["fields"]["membership"]["value"], "member")
        self.assertEqual(
            receipt["fields"]["explicit_permission"]["status"],
            "insufficient_authority",
        )

    def test_explicit_denials(self):
        source = (
            "Only licensed inspectors may release batch a. "
            "Mira is not a licensed inspector. "
            "Mira is not authorized to release batch a."
        )
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        self.assertEqual(receipt["fields"]["membership"]["value"], "non_member")
        self.assertEqual(
            receipt["fields"]["explicit_permission"]["value"], "not_permitted"
        )


class RoleBindingSentinels(ReceiptAssertions):
    QUERY = {
        "kind": "event",
        "predicate": "review",
        "roles": {"subject": "dana", "object": "lee submission"},
        "polarity": "positive",
    }

    def test_passive_preserves_roles(self):
        source = "Lee submission was reviewed by Dana."
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        fields = receipt["fields"]
        self.assertEqual(fields["predicate"]["value"], "review")
        self.assertEqual(fields["subject"]["value"], "dana")
        self.assertEqual(fields["object"]["value"], "lee submission")
        self.assertEqual(fields["polarity"]["value"], "positive")
        self.assertEqual(fields["subject"]["warrant"], "passive_role_binding")
        self.assertEqual(fields["object"]["warrant"], "passive_role_binding")

    def test_active_negative_preserves_roles(self):
        source = "Dana did not review Lee submission."
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        fields = receipt["fields"]
        self.assertEqual(fields["subject"]["value"], "dana")
        self.assertEqual(fields["object"]["value"], "lee submission")
        self.assertEqual(fields["polarity"]["value"], "negative")
        self.assertEqual(fields["polarity"]["warrant"], "explicit_negation")

    def test_unrecovered_binding_is_extraction_unresolved(self):
        source = "Dana reviewed, in full, Lee submission."
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        self.assertEqual(receipt["fields"]["predicate"]["status"], "established")
        self.assertEqual(
            receipt["fields"]["subject"]["status"], "extraction_unresolved"
        )
        self.assertEqual(
            receipt["fields"]["object"]["status"], "extraction_unresolved"
        )
        self.assertEqual(
            receipt["fields"]["polarity"]["status"], "extraction_unresolved"
        )

    def test_merely_missing_role_authority_is_insufficient(self):
        source = "A review occurred. Dana and Lee submission were mentioned separately."
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        self.assertEqual(
            receipt["fields"]["subject"]["status"], "insufficient_authority"
        )


class QuantifierSentinels(ReceiptAssertions):
    QUERY = {
        "kind": "quantified",
        "population": "technicians",
        "predicate": "inspect vessel",
        "quantifier": "every",
    }

    def test_each_normalizes_to_every(self):
        source = "Each technician inspected the vessel."
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        fields = receipt["fields"]
        self.assertEqual(fields["population"]["value"], "technicians")
        self.assertEqual(fields["predicate"]["value"], "inspect vessel")
        self.assertEqual(fields["quantifier"]["value"], "every")
        self.assertEqual(fields["polarity"]["value"], "positive")

    def test_supported_quantifier_normalizations(self):
        cases = {
            "All technicians inspected the vessel.": "every",
            "No technicians inspected the vessel.": "none",
            "Some technicians inspected the vessel.": "some",
            "Not all technicians inspected the vessel.": "not_every",
            "At least one technician inspected the vessel.": "some",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                receipt = interpret(source, self.QUERY)
                self.assert_valid_receipt(source, receipt)
                self.assertEqual(receipt["fields"]["quantifier"]["value"], expected)
                self.assertEqual(receipt["fields"]["polarity"]["value"], "positive")

    def test_missing_quantifier_authority_is_insufficient(self):
        source = "Technicians inspected the vessel."
        receipt = interpret(source, self.QUERY)
        self.assert_valid_receipt(source, receipt)
        self.assertEqual(
            receipt["fields"]["quantifier"]["status"], "insufficient_authority"
        )

    def test_most_is_out_of_jurisdiction(self):
        source = "Most technicians inspected the vessel."
        self.assertEqual(
            interpret(source, self.QUERY),
            {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"},
        )

    def test_exact_count_is_out_of_jurisdiction(self):
        source = "Exactly 3 technicians inspected the vessel."
        self.assertEqual(
            interpret(source, self.QUERY),
            {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"},
        )

    def test_conditional_is_out_of_jurisdiction(self):
        source = "If scheduled, every technician inspected the vessel."
        self.assertEqual(
            interpret(source, self.QUERY),
            {"status": "out_of_jurisdiction", "reason": "unsupported_composition"},
        )


class JurisdictionSentinels(unittest.TestCase):
    def test_unknown_kind(self):
        self.assertEqual(
            interpret("Something happened.", {"kind": "other"}),
            {"status": "out_of_jurisdiction", "reason": "unsupported_family"},
        )


if __name__ == "__main__":
    unittest.main()
