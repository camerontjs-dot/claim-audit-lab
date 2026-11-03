"""Ordinary informed development review controls, not independent qualification.

These controls were written after reading the candidate and exposed receipt
contract. They use newly authored strings and no evaluation data or labels.
Failures are deliberately retained as ordinary test failures.
"""
from __future__ import annotations

import hashlib
import json

from candidate import analyze


def main() -> int:
    failures = []
    probes = 0

    def check(name, condition, details):
        nonlocal probes
        probes += 1
        if not condition:
            failures.append({"name": name, **details})

    def relation(name, claim, evidence, expected, reason=None):
        result = analyze(claim, evidence)
        check(name, result["relation"] == expected and result["abstention_cause"] == reason,
              {"claim": claim, "evidence": evidence,
               "expected": {"relation": expected, "reason": reason},
               "actual": {"relation": result["relation"], "reason": result["abstention_cause"]}})
        return result

    # Source observations are source-local even when the compatibility view varies.
    level = "The rate was 5 percent."
    change = "The rate increased by 5 percent."
    for claim, evidence in ((level, change), (change, level)):
        result = relation("property_aspect_mismatch", claim, evidence, "unresolved", "unit_role_mismatch")
        check("declared_legacy_projection",
              result["receipt_projection"]["measure_style"] == "common_property_with_distinct_aspects"
              and result["receipt_projection"]["source_observations_unchanged"] is True,
              {"actual": result["receipt_projection"]})
    original = analyze(change, change)["source_observations"]["evidence"]
    for claim in (level, change, "The rate increased by 5 percentage points.", "The count was 5 percent."):
        actual = analyze(claim, change)["source_observations"]["evidence"]
        check("evidence_source_conservation", actual == original,
              {"claim": claim, "expected": original, "actual": actual})
    check("source_aspect_preserved", original[0]["measure"] == "rate change"
          and original[0]["property_name"] == "rate"
          and original[0]["measurement_aspect"] == "change",
          {"actual": original})
    relation("literal_change_property_not_collapsed", change,
             "The rate change increased by 5 percent.", "unresolved", "measure_mismatch")

    # The endpoint exposes both change families; a contradiction in either is material.
    endpoint = "The share rose from 10 percent to 12 percent"
    contradictory = "the share increased by 10 percent"
    for clauses in ((endpoint, contradictory), (contradictory, endpoint)):
        evidence = "; ".join(clauses) + "."
        for claim in ("The share increased by 2 percentage points.", "The share increased by 20 percent."):
            relation("cross_family_conflict", claim, evidence, "unresolved", "material_conflict")
    relation("consistent_endpoint_and_relative", "The share increased by 2 percentage points.",
             endpoint + "; the share increased by 20 percent.", "supports")

    # A stronger converted bound is decisive even when it is the second clause.
    claim = "The margin was more than 2 percentage points."
    constraints = ("The margin was more than 1 percentage point", "the margin was more than 200 basis points")
    for clauses in (constraints, constraints[::-1]):
        evidence = "; ".join(clauses) + "."
        result = relation("converted_bound_support", claim, evidence, "supports")
        conversion = result["receipt_v2"]["conversion_rule"]
        check("all_decisive_conversions_recorded",
              "100bp=1pp" in conversion["available"] and conversion["applied"] == "100bp=1pp",
              {"claim": claim, "evidence": evidence, "actual": conversion})

    # Bound against bound checks add strictness and overlap cases beyond point tests.
    for name, claim_bound, evidence_bound, expected, reason in (
        ("strict_subset", "more than 2", "more than 3", "supports", None),
        ("strict_boundary_overlap", "more than 2", "at least 2", "unresolved", "overlapping_bounds"),
        ("closed_open_disjoint", "at most 2", "more than 2", "refutes", None),
        ("negated_bound", "not at most 2", "more than 3", "supports", None),
    ):
        relation(name, f"The margin was {claim_bound} percentage points.",
                 f"The margin was {evidence_bound} percentage points.", expected, reason)
    relation("exact_decimal_conversion", "The rate increased by 0.10000000000000001 percentage points.",
             "The rate increased by 10.000000000000001 basis points.", "supports")
    relation("adjacent_decimal_not_equal", "The rate increased by 0.10000000000000001 percentage points.",
             "The rate increased by 10 basis points.", "refutes")

    # Same-frame contradictions and duplicates cannot be resolved by clause order.
    for clauses in (("The rate increased by 1 percentage point", "the rate increased by 200 basis points"),
                    ("The rate increased by 200 basis points", "the rate increased by 1 percentage point")):
        relation("same_family_conflict", "The rate increased by 1 percentage point.",
                 "; ".join(clauses) + ".", "unresolved", "material_conflict")
    relation("duplicate_consistent", change, change + " " + change, "supports")
    relation("distinct_year_binding", "In 2025, the rate increased by 1 percentage point.",
             "In 2024, the rate increased by 100 basis points.", "unresolved", "year_scope_mismatch")
    relation("modal_claim_abstains", "The rate might have increased by 5 percent.", change,
             "unresolved", "unsupported_or_compound_claim")
    relation("unparsed_evidence_abstains", change, change + " The source is uncertain.",
             "unresolved", "unsupported_or_missing_evidence")

    # Original Unicode text, including unrelated clauses, must keep honest inventory.
    claim = "The café rate increased by 0.5 percentage points."
    evidence = "The score increased by 9 percent; the café rate increased by 50 basis points."
    result = relation("unicode_measure_and_distractor", claim, evidence, "supports")
    for side, text in (("claim", claim), ("evidence", evidence)):
        qty = result["receipt_v2"]["quantities"][side]
        check("original_input_hash", result["input_identity"][side] == hashlib.sha256(text.encode("utf-8")).hexdigest(),
              {"side": side, "actual": result["input_identity"][side]})
        check("original_number_spans", all(text[n["span"][0]:n["span"][1]] == n["value"] for n in qty["numeric_tokens"]),
              {"side": side, "actual": qty["numeric_tokens"]})
    basis = result["receipt_v3"]["deciding_basis_spans"]["evidence"]
    check("irrelevant_clause_not_decisive", len(basis) == 1 and "café rate" in evidence[basis[0][0]:basis[0][1]]
          and "score" not in evidence[basis[0][0]:basis[0][1]], {"actual": basis})

    report = {"evidence_class": "INFORMED_REVIEW_DEVELOPMENT_CONTROLS_NOT_QUALIFICATION",
              "probes": probes, "failures": failures, "passed": not failures}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
