"""Contract-derived sentinel tests for the fresh extractor.

These cases are authored only from BOOTSTRAP.md and EXTRACTION_CONTRACT-v1.md.
They are not evaluator cases and intentionally cover only bounded constructions
implemented by the fresh reproduction.
"""

import unittest

from research.text_to_typed_authority_fresh_v1 import extract


class ContractSentinels(unittest.TestCase):
    def test_membership_rule_fact(self):
        self.assertEqual(
            extract(
                "Mira is a navigator. Navigators record arrivals.",
                "Does Mira record arrivals?",
            ),
            {
                "status": "resolved",
                "case": {
                    "dimension": "membership_rule",
                    "authority": {
                        "entity": "Mira",
                        "population": "Navigators",
                        "membership": "member",
                        "rule": {
                            "population": "Navigators",
                            "predicate": "record arrivals",
                            "modality": "fact",
                            "polarity": "positive",
                        },
                    },
                    "query": {
                        "kind": "behavior_positive",
                        "entity": "Mira",
                        "population": "Navigators",
                        "predicate": "record arrivals",
                    },
                },
            },
        )

    def test_membership_rule_negative_obligation(self):
        result = extract(
            "Mira is a navigator. Navigators must not record arrivals.",
            "Does Mira not record arrivals?",
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["case"]["authority"]["rule"]["modality"], "obligation")
        self.assertEqual(result["case"]["authority"]["rule"]["polarity"], "negative")
        self.assertEqual(result["case"]["query"]["kind"], "behavior_negative")

    def test_subclass_canonicalization(self):
        self.assertEqual(
            extract(
                "Every astronomer is a scientist. Lina is an astronomer.",
                "Is Lina a scientist?",
            ),
            {
                "status": "resolved",
                "case": {
                    "dimension": "subclass",
                    "authority": {
                        "entity": "Lina",
                        "membership_population": "A",
                        "membership": "member",
                        "subclass_edge": "A_sub_B",
                    },
                    "query": {
                        "kind": "membership",
                        "entity": "Lina",
                        "population": "B",
                    },
                },
            },
        )

    def test_only_permission_does_not_invent_grant(self):
        result = extract(
            "Only members of navigators may enter harbor. Mira is a navigator.",
            "May Mira enter harbor?",
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["case"]["dimension"], "only_permission")
        self.assertEqual(result["case"]["authority"]["membership"], "member")
        self.assertEqual(result["case"]["authority"]["explicit_permission"], "unknown")
        self.assertTrue(result["case"]["authority"]["only_population_may"])

    def test_quantifier_keeps_not_every_distinct(self):
        result = extract(
            "Not every navigator records arrivals.",
            "Some navigator records arrivals.",
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["case"]["dimension"], "quantifier")
        self.assertEqual(result["case"]["authority"]["quantifier"], "not_every")
        self.assertEqual(result["case"]["query"]["quantifier"], "some")

    def test_group_scope_does_not_collapse_to_named_member(self):
        result = extract(
            "The committee approved the charter.",
            "Did Mira approve the charter?",
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["case"]["dimension"], "group_scope")
        self.assertEqual(result["case"]["authority"]["event_scope"], "group")
        self.assertEqual(result["case"]["query"]["event_scope"], "member:Mira")

    def test_role_binding_preserves_passive_roles(self):
        result = extract(
            "Ava reviewed Ben.",
            "Was Ava reviewed by Ben?",
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["case"]["dimension"], "role_binding")
        self.assertEqual(
            result["case"]["authority"]["event"]["roles"],
            {"subject": "Ava", "object": "Ben"},
        )
        self.assertEqual(
            result["case"]["query"]["roles"],
            {"subject": "Ben", "object": "Ava"},
        )

    def test_temporal_membership_normalizes_boundary(self):
        result = extract(
            "Before handover, Mira was a navigator. "
            "After handover, Mira was not a navigator. "
            "Navigators record arrivals.",
            "Does Mira record arrivals after handover?",
        )
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["case"]["dimension"], "temporal_membership")
        self.assertEqual(result["case"]["authority"]["membership_window"], "before_only")
        self.assertEqual(result["case"]["authority"]["boundary"], "cutoff")
        self.assertEqual(result["case"]["query"]["time"], "after")

    def test_ontology_escape_for_unsupported_quantifier(self):
        self.assertEqual(
            extract(
                "Most navigators record arrivals.",
                "Do all navigators record arrivals?",
            ),
            {"status": "unknown", "reason": "ontology_escape"},
        )

    def test_insufficient_authority_for_suggestive_membership_language(self):
        self.assertEqual(
            extract(
                "Mira trained with navigators. Navigators record arrivals.",
                "Does Mira record arrivals?",
            ),
            {"status": "unknown", "reason": "insufficient_authority"},
        )

    def test_ambiguous_reference_for_pronoun_with_multiple_names(self):
        self.assertEqual(
            extract(
                "Ava met Ben. She reviewed Cara.",
                "Did Ava review Cara?",
            ),
            {"status": "unknown", "reason": "ambiguous_reference"},
        )

    def test_unparsed_for_unrecognized_construction(self):
        self.assertEqual(
            extract(
                "The weather changed.",
                "Is the statement supported?",
            ),
            {"status": "unknown", "reason": "unparsed"},
        )


if __name__ == "__main__":
    unittest.main()
