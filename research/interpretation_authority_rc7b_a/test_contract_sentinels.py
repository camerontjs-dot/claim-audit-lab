import unittest

from research.interpretation_authority_rc7b_a.interpret import interpret


PERMISSION_QUERY = {
    "kind": "permission",
    "entity": "mira",
    "population": "licensed inspectors",
    "predicate": "release batch a",
}
EVENT_QUERY = {
    "kind": "event",
    "predicate": "review",
    "roles": {"subject": "dana", "object": "lee submission"},
    "polarity": "positive",
}
QUANT_QUERY = {
    "kind": "quantified",
    "population": "technicians",
    "predicate": "inspect vessel",
    "quantifier": "every",
}


class ContractSentinels(unittest.TestCase):
    def assert_valid_grounding(self, source, observation):
        if observation["status"] in {"established", "semantic_unknown"}:
            self.assertIsNotNone(observation["span"])
            span = observation["span"]
            self.assertGreaterEqual(span["start"], 0)
            self.assertGreater(span["end"], span["start"])
            self.assertLessEqual(span["end"], len(source))
            self.assertEqual(source[span["start"]:span["end"]], span["text"])
            self.assertIsNotNone(observation["warrant"])
        else:
            self.assertIsNone(observation["value"])
            self.assertIsNone(observation["span"])
            self.assertIsNone(observation["warrant"])

    def assert_receipt_grounded(self, source, receipt):
        self.assertEqual(receipt["status"], "receipt")
        for observation in receipt["fields"].values():
            self.assert_valid_grounding(source, observation)

    def test_only_permission_all_established(self):
        source = (
            "Only licensed inspectors may release batch a. "
            "Mira is a member of the licensed inspectors. "
            "Mira is authorized to release batch a."
        )
        got = interpret(source, PERMISSION_QUERY)
        self.assert_receipt_grounded(source, got)
        self.assertEqual(got["family"], "only_permission")
        expected = {
            "entity": ("established", "mira"),
            "population": ("established", "licensed inspectors"),
            "membership": ("established", "member"),
            "predicate": ("established", "release batch a"),
            "only_population_may": ("established", True),
            "explicit_permission": ("established", "permitted"),
        }
        self.assertEqual(set(got["fields"]), set(expected))
        for field, pair in expected.items():
            self.assertEqual((got["fields"][field]["status"], got["fields"][field]["value"]), pair)

    def test_semantic_unknown_is_explicit_only(self):
        source = (
            "Only licensed inspectors may release batch a. "
            "It is unknown whether Mira is a member of the licensed inspectors. "
            "Whether Mira is permitted to release batch a is unknown."
        )
        got = interpret(source, PERMISSION_QUERY)
        self.assert_receipt_grounded(source, got)
        membership = got["fields"]["membership"]
        permission = got["fields"]["explicit_permission"]
        self.assertEqual((membership["status"], membership["value"], membership["warrant"]),
                         ("semantic_unknown", "unknown", "explicit_unknown_assertion"))
        self.assertEqual((permission["status"], permission["value"], permission["warrant"]),
                         ("semantic_unknown", "unknown", "explicit_unknown_assertion"))

    def test_missing_authority_is_not_semantic_unknown(self):
        source = "Only licensed inspectors may release batch a. Mira works beside licensed inspectors."
        got = interpret(source, PERMISSION_QUERY)
        self.assert_receipt_grounded(source, got)
        self.assertEqual(got["fields"]["membership"]["status"], "insufficient_authority")
        self.assertEqual(got["fields"]["explicit_permission"]["status"], "insufficient_authority")

    def test_explicit_nonmembership_and_permission_denial(self):
        source = (
            "Only licensed inspectors may release batch a. "
            "Mira is not a member of the licensed inspectors. "
            "Mira is not permitted to release batch a."
        )
        got = interpret(source, PERMISSION_QUERY)
        self.assert_receipt_grounded(source, got)
        self.assertEqual(got["fields"]["membership"]["value"], "non_member")
        self.assertEqual(got["fields"]["explicit_permission"]["value"], "not_permitted")

    def test_supported_but_unrecovered_only_condition_abstains(self):
        source = "Release batch a may be performed solely by licensed inspectors. Mira works nearby."
        got = interpret(source, PERMISSION_QUERY)
        self.assert_receipt_grounded(source, got)
        self.assertEqual(got["fields"]["only_population_may"]["status"], "extraction_unresolved")
        self.assertNotEqual(got["fields"]["only_population_may"].get("value"), "unknown")

    def test_passive_roles_are_preserved(self):
        source = "Lee submission was reviewed by Dana."
        got = interpret(source, EVENT_QUERY)
        self.assert_receipt_grounded(source, got)
        self.assertEqual(got["family"], "role_binding")
        self.assertEqual(got["fields"]["subject"]["value"], "dana")
        self.assertEqual(got["fields"]["object"]["value"], "lee submission")
        self.assertEqual(got["fields"]["subject"]["warrant"], "passive_role_binding")
        self.assertEqual(got["fields"]["polarity"]["value"], "positive")

    def test_active_negation_does_not_swap_roles(self):
        source = "Dana did not review Lee submission."
        got = interpret(source, EVENT_QUERY)
        self.assert_receipt_grounded(source, got)
        self.assertEqual(got["fields"]["subject"]["value"], "dana")
        self.assertEqual(got["fields"]["object"]["value"], "lee submission")
        self.assertEqual(got["fields"]["polarity"]["value"], "negative")
        self.assertEqual(got["fields"]["polarity"]["warrant"], "explicit_negation")

    def test_role_binding_parser_limitation_is_unresolved(self):
        source = "Lee submission, Dana reviewed."
        got = interpret(source, EVENT_QUERY)
        self.assert_receipt_grounded(source, got)
        self.assertEqual(got["fields"]["predicate"]["status"], "established")
        self.assertEqual(got["fields"]["subject"]["status"], "extraction_unresolved")
        self.assertEqual(got["fields"]["object"]["status"], "extraction_unresolved")
        self.assertEqual(got["fields"]["polarity"]["status"], "extraction_unresolved")

    def test_mere_event_mentions_are_insufficient(self):
        source = "Dana and Lee submission appear in a note that mentions review."
        got = interpret(source, EVENT_QUERY)
        self.assert_receipt_grounded(source, got)
        self.assertEqual(got["fields"]["subject"]["status"], "insufficient_authority")
        self.assertEqual(got["fields"]["object"]["status"], "insufficient_authority")
        self.assertEqual(got["fields"]["polarity"]["status"], "insufficient_authority")

    def test_quantifier_each_normalizes_to_every(self):
        source = "Each technician inspected the vessel."
        got = interpret(source, QUANT_QUERY)
        self.assert_receipt_grounded(source, got)
        self.assertEqual(got["family"], "quantifier")
        self.assertEqual(got["fields"]["quantifier"]["value"], "every")
        self.assertEqual(got["fields"]["quantifier"]["warrant"], "universal_quantifier")
        self.assertEqual(got["fields"]["population"]["value"], "technician")
        self.assertEqual(got["fields"]["predicate"]["value"], "inspect vessel")
        self.assertEqual(got["fields"]["polarity"]["value"], "positive")

    def test_quantifier_supported_normalizations(self):
        cases = [
            ("No technicians inspected the vessel.", "none", "empty_quantifier"),
            ("Some technicians inspected the vessel.", "some", "existential_quantifier"),
            ("Not every technician inspected the vessel.", "not_every", "nonuniversal_quantifier"),
            ("Not all technicians inspected the vessel.", "not_every", "nonuniversal_quantifier"),
        ]
        for source, value, warrant in cases:
            with self.subTest(source=source):
                got = interpret(source, QUANT_QUERY)
                self.assert_receipt_grounded(source, got)
                self.assertEqual(got["fields"]["quantifier"]["value"], value)
                self.assertEqual(got["fields"]["quantifier"]["warrant"], warrant)

    def test_quantifier_parser_limitation_is_unresolved(self):
        source = "Technicians, each, inspected the vessel."
        got = interpret(source, QUANT_QUERY)
        self.assert_receipt_grounded(source, got)
        for field in ("population", "predicate", "quantifier", "polarity"):
            self.assertEqual(got["fields"][field]["status"], "extraction_unresolved")

    def test_unsupported_quantifier_is_out_of_jurisdiction(self):
        self.assertEqual(
            interpret("Most technicians inspected the vessel.", QUANT_QUERY),
            {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"},
        )
        self.assertEqual(
            interpret("Three technicians inspected the vessel.", QUANT_QUERY),
            {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"},
        )

    def test_modal_event_without_asserted_event_is_out_of_jurisdiction(self):
        got = interpret("Dana may review Lee submission.", EVENT_QUERY)
        self.assertEqual(got, {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"})

    def test_unknown_query_family(self):
        got = interpret("Text.", {"kind": "comparison"})
        self.assertEqual(got, {"status": "out_of_jurisdiction", "reason": "unsupported_family"})


if __name__ == "__main__":
    unittest.main()
