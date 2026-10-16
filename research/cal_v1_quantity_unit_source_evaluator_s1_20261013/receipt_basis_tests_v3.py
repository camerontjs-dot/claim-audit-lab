"""CAL #212 exposed development-only V3 *deciding-basis* evaluator successor.

V2 checked lexical tokens and reported consumption anchors but accepted
whole-sentence consumed windows. V3 keeps V2 intact and checks a new
*declared decisive semantic basis*, distinct from available input and
actual analyzer reads. This is not a causal-consumption certificate.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

import receipt_contract_tests_v2 as v2

VERSION = "cal-rc3-quantity-basis-evaluator-v3-prep1"
# Explicit bounded basis texts, adjudicated against exposed cases only.
# A basis contains the applicable measure, direction, number/unit and material
# qualifiers. It excludes unrelated score clauses, articles, and punctuation.
BASIS_TEXT = {
    "U01_SYMBOL_WORD": ("rate was 10%", "rate was 10 percent"),
    "U02_PP_VS_PERCENT": ("margin was less than 10 percentage points", "margin was less than 10 percent"),
    "U03_PERCENT_VS_PP": ("margin was less than 10 percent", "margin was less than 10 percentage points"),
    "U04_PP_BP": ("rate increased by 1 percentage point", "rate increased by 100 basis points"),
    "U05_BP_PP_HALF": ("rate increased by 50 basis points", "rate increased by 0.5 percentage points"),
    "U06_PERCENT_CHANGE_VS_PP": ("share increased by 2 percent", "share increased by 2 percentage points"),
    "U07_LEVEL_VS_CHANGE": ("rate was 5 percent", "rate increased by 5 percent"),
    "U08_ENDPOINT_PP": ("share increased by 2 percentage points", "share rose from 10 percent to 12 percent"),
    "U09_ENDPOINT_RELATIVE": ("share increased by 20 percent", "share rose from 10 percent to 12 percent"),
    "U10_PREFIX_BOUNDARY": ("change was 10 percentage points", "change was 10 percent"),
    "U11_PP_ABBREV": ("rate rose by 2 pp", "rate rose by 2 percentage points"),
    "U12_BP_ABBREV": ("rate rose by 50 bp", "rate rose by 50 basis points"),
    "U13_RATE_COUNT": ("rate increased by 10 percent", "count increased by 10 percent"),
    "U14_MEASURE_MISMATCH": ("unemployment rate rose by 1 percentage point", "inflation rate rose by 100 basis points"),
    "U15_YEAR_MISMATCH": ("In 2025, the rate rose by 1 percentage point", "In 2024, the rate rose by 100 basis points"),
    "U16_MULTIPLE_UNITS": ("margin rose by 2 percentage points", "margin rose by 1 percentage point"),
    "U17_NEGATED_COMPARATOR": ("change was less than 10 percentage points", "change was not less than 10 percentage points"),
    "U18_EVENT_ONLY": (None, None),
    "U19_EXPOSED_HOL14_SHAPE": ("interest was less than 10 percentage points", "interest was less than 10%"),
}


def gold_basis(c: dict, side: str) -> list[list[int]]:
    text = BASIS_TEXT[c["id"]][0 if side == "claim" else 1]
    if text is None:
        return []
    at = c[side].find(text)
    if at < 0 or c[side].find(text, at + 1) != -1:
        raise AssertionError("ambiguous or absent exposed basis for " + c["id"])
    return [[at, at + len(text)]]


def reference(c: dict) -> dict:
    o = deepcopy(v2.reference(c))
    o["receipt_v3"] = {
        "version": VERSION,
        "basis_kind": "DECLARED_DECISIVE_TEXT_NOT_OBSERVED_CAUSAL_CONSUMPTION",
        "deciding_basis_spans": {s: gold_basis(c, s) for s in ("claim", "evidence")},
        "consumption_independence": "NOT_ESTABLISHED",
    }
    return o


def validate(receipt: object, c: dict) -> list[str]:
    issues = v2.validate(receipt, c)
    if not isinstance(receipt, dict):
        return sorted(set(issues + ["v3_missing"]))
    v = receipt.get("receipt_v3")
    if not isinstance(v, dict):
        return sorted(set(issues + ["v3_missing"]))
    if v.get("version") != VERSION:
        issues.append("v3_version")
    if v.get("basis_kind") != "DECLARED_DECISIVE_TEXT_NOT_OBSERVED_CAUSAL_CONSUMPTION":
        issues.append("basis_kind")
    if v.get("consumption_independence") != "NOT_ESTABLISHED":
        issues.append("consumption_independence_overclaim")
    spans = v.get("deciding_basis_spans")
    if not isinstance(spans, dict):
        return sorted(set(issues + ["deciding_basis_missing"]))
    for side in ("claim", "evidence"):
        expected = gold_basis(c, side)
        received = spans.get(side)
        if received != expected:
            issues.append(side + "_deciding_basis_identity")
        if not expected:
            continue
        q = receipt.get("receipt_v2", {}).get("quantities", {}).get(side, {})
        consumed = q.get("consumed_spans") if isinstance(q, dict) else None
        if not v2.covers(consumed, expected[0], c[side]):
            issues.append(side + "_basis_not_within_declared_consumption")
    return sorted(set(issues))


MUTATION_PLAN = {
    "whole_sentence_basis": ("U01_SYMBOL_WORD", "claim_deciding_basis_identity"),
    "wrong_measure_clause": ("U16_MULTIPLE_UNITS", "evidence_deciding_basis_identity"),
    "missing_negation": ("U17_NEGATED_COMPARATOR", "evidence_deciding_basis_identity"),
    "missing_year_qualifier": ("U15_YEAR_MISMATCH", "claim_deciding_basis_identity"),
    "one_endpoint_omitted": ("U08_ENDPOINT_PP", "evidence_deciding_basis_identity"),
    "numeric_only_basis": ("U01_SYMBOL_WORD", "claim_deciding_basis_identity"),
    "empty_basis": ("U04_PP_BP", "claim_deciding_basis_identity"),
    "basis_claim_evidence_swap": ("U02_PP_VS_PERCENT", "evidence_deciding_basis_identity"),
    "false_consumption_certainty": ("U01_SYMBOL_WORD", "consumption_independence_overclaim"),
    "decisive_basis_outside_consumed": ("U16_MULTIPLE_UNITS", "evidence_basis_not_within_declared_consumption"),
}


def mutate(c: dict, name: str) -> dict:
    o = reference(c)
    spans = o["receipt_v3"]["deciding_basis_spans"]
    if name == "whole_sentence_basis":
        spans["claim"] = [[0, len(c["claim"])]]
    elif name == "wrong_measure_clause":
        s = "score rose by 2 percent"
        lo = c["evidence"].index(s)
        spans["evidence"] = [[lo, lo + len(s)]]
    elif name == "missing_negation":
        s = "less than 10 percentage points"
        lo = c["evidence"].index(s)
        spans["evidence"] = [[lo, lo + len(s)]]
    elif name == "missing_year_qualifier":
        s = "rate rose by 1 percentage point"
        lo = c["claim"].index(s)
        spans["claim"] = [[lo, lo + len(s)]]
    elif name == "one_endpoint_omitted":
        s = "share rose from 10 percent"
        lo = c["evidence"].index(s)
        spans["evidence"] = [[lo, lo + len(s)]]
    elif name == "numeric_only_basis":
        s = "10"
        lo = c["claim"].index(s)
        spans["claim"] = [[lo, lo + len(s)]]
    elif name == "empty_basis":
        spans["claim"] = []
    elif name == "basis_claim_evidence_swap":
        spans["evidence"] = deepcopy(spans["claim"])
    elif name == "false_consumption_certainty":
        o["receipt_v3"]["consumption_independence"] = "OBSERVED"
    elif name == "decisive_basis_outside_consumed":
        # The numeric and lexical unit anchors remain covered (V2 passes),
        # but the measure \"margin\" is omitted from the claimed consumed text.
        text = "rose by 1 percentage point"
        lo = c["evidence"].index(text)
        o["receipt_v2"]["quantities"]["evidence"]["consumed_spans"] = [[lo, lo + len(text)]]
    else:
        raise ValueError(name)
    return o


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--selftest", action="store_true")
    group.add_argument("--adapter", type=Path)
    parser.add_argument("--cases", type=Path, default=v2.DEFAULT_CASES)
    args = parser.parse_args()
    cases = v2.all_cases(args.cases)
    assert set(BASIS_TEXT) == {c["id"] for c in cases}
    by_id = {c["id"]: c for c in cases}
    if args.selftest:
        positives = {c["id"]: validate(reference(c), c) for c in cases}
        controls = {}
        for name, (cid, intended) in MUTATION_PLAN.items():
            problems = validate(mutate(by_id[cid], name), by_id[cid])
            controls[name] = {
                "case_id": cid,
                "failures": problems,
                "intended": intended,
                "caught_for_intended_reason": problems == [intended],
            }
        good = all(not p for p in positives.values()) and all(c["caught_for_intended_reason"] for c in controls.values())
        result = {
            "evidence_class": "EXPOSED_DEV_EVALUATOR_SELFTEST_ONLY",
            "candidate_executed": False,
            "version": VERSION,
            "positive_cases": len(cases),
            "positive_failures": positives,
            "mutant_count": len(controls),
            "mutants": controls,
            "passed": good,
            "limits": [
                "declared basis is not observed causal consumption",
                "exact synthetic basis is not universal natural-language gold",
                "no heldout labels, sources or candidate observed",
            ],
        }
    else:
        spec = importlib.util.spec_from_file_location("rc3_candidate_development", args.adapter.resolve())
        if spec is None or spec.loader is None:
            raise RuntimeError("invalid adapter")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        errors = {c["id"]: validate(mod.analyze(c["claim"], c["evidence"]), c) for c in cases}
        good = all(not x for x in errors.values())
        result = {
            "evidence_class": "EXPOSED_DEVELOPMENT_ONLY",
            "fresh_generalization": "NOT_ESTABLISHED",
            "version": VERSION, "candidate_executed": True,
            "errors": errors, "passed": good,
        }
    print(json.dumps(result, sort_keys=True))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
