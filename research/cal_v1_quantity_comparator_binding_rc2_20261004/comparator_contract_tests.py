"""Research evaluator for CAL #210 quantity-comparator binding.

Self-test validates evaluator discrimination only. A candidate adapter must export:
    analyze(claim: str, evidence: str) -> dict

Required result fields:
    status: claimed | unresolved | not_applicable
    relation: supports | refutes | unresolved | not_applicable
    claim_comparator: string
    evidence_comparator: string
    claim_measure: string | null
    evidence_measure: string | null
    claim_years: list[str]
    evidence_years: list[str]
    ambiguity: bool
    consumed_claim_spans: list[[start,end]]
    consumed_evidence_spans: list[[start,end]]

This interface is a bounded research contract, not a production schema.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CASES = json.loads((ROOT / "DEVELOPMENT_CASES.json").read_text(encoding="utf-8"))["cases"]
BY_TEXT = {(c["claim"], c["evidence"]): c for c in CASES}


def expected_output(case: dict[str, Any]) -> dict[str, Any]:
    status = "not_applicable" if case["expected_relation"] == "not_applicable" else (
        "unresolved" if case["expected_relation"] == "unresolved" else "claimed"
    )
    years_claim = [x for x in ("2024", "2025") if x in case["claim"]]
    years_evidence = [x for x in ("2024", "2025") if x in case["evidence"]]
    return {
        "status": status,
        "relation": case["expected_relation"],
        "claim_comparator": case["required_claim_comparator"],
        "evidence_comparator": case["required_evidence_comparator"],
        "claim_measure": case["measure"],
        "evidence_measure": case["measure"],
        "claim_years": years_claim,
        "evidence_years": years_evidence,
        "ambiguity": case["required_evidence_comparator"] == "AMBIGUOUS",
        "consumed_claim_spans": [[0, len(case["claim"])]] if status != "not_applicable" else [],
        "consumed_evidence_spans": [[0, len(case["evidence"])]] if status != "not_applicable" else [],
    }


class Oracle:
    @staticmethod
    def analyze(claim: str, evidence: str) -> dict[str, Any]:
        return expected_output(BY_TEXT[(claim, evidence)])


ADAPTER: Any = Oracle


class Contract(unittest.TestCase):
    def out(self, cid: str) -> dict[str, Any]:
        case = next(c for c in CASES if c["id"] == cid)
        value = ADAPTER.analyze(case["claim"], case["evidence"])
        self.assertIsInstance(value, dict)
        return value

    def test_all_cases_have_exact_relation(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertEqual(ADAPTER.analyze(case["claim"], case["evidence"])["relation"], case["expected_relation"])

    def test_required_fields_and_vocab(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                out = ADAPTER.analyze(case["claim"], case["evidence"])
                for field in ("status", "relation", "claim_comparator", "evidence_comparator", "claim_measure", "evidence_measure", "claim_years", "evidence_years", "ambiguity", "consumed_claim_spans", "consumed_evidence_spans"):
                    self.assertIn(field, out)
                self.assertIn(out["status"], {"claimed", "unresolved", "not_applicable"})
                self.assertIn(out["relation"], {"supports", "refutes", "unresolved", "not_applicable"})
                self.assertIsInstance(out["ambiguity"], bool)

    def test_parenthetical_comparator_bound(self):
        a = self.out("D01_PARENTHESES_OPPOSITE")
        b = self.out("D02_PARENTHESES_SAME")
        self.assertEqual((a["claim_comparator"], a["evidence_comparator"]), ("GT", "LT"))
        self.assertEqual((b["claim_comparator"], b["evidence_comparator"]), ("LT", "LT"))
        self.assertNotEqual(a["relation"], b["relation"])

    def test_faster_slower_bound(self):
        a = self.out("D03_GROWTH_FASTER_SLOWER")
        b = self.out("D04_GROWTH_FASTER_SAME")
        self.assertEqual(a["evidence_comparator"], "LT_RATE")
        self.assertEqual(b["evidence_comparator"], "GT_RATE")
        self.assertEqual(a["relation"], "refutes")
        self.assertEqual(b["relation"], "supports")

    def test_higher_lower_and_greater_less(self):
        self.assertEqual(self.out("D05_HIGHER_LOWER")["relation"], "refutes")
        self.assertEqual(self.out("D06_GREATER_LESS")["relation"], "refutes")

    def test_equality_is_not_directional_support(self):
        out = self.out("D07_EQUALITY")
        self.assertEqual(out["evidence_comparator"], "EQ")
        self.assertEqual(out["relation"], "refutes")

    def test_not_more_does_not_become_less(self):
        out = self.out("D08_NOT_MORE_NOT_LESS")
        self.assertEqual(out["evidence_comparator"], "NOT_GT")
        self.assertEqual(out["relation"], "unresolved")

    def test_side_swap_plus_inverse(self):
        self.assertEqual(self.out("D09_SIDE_SWAP")["relation"], "supports")

    def test_multiple_cues_fail_closed(self):
        out = self.out("D10_MULTIPLE_CUES")
        self.assertTrue(out["ambiguity"])
        self.assertEqual(out["relation"], "unresolved")

    def test_comparator_bound_to_requested_measure(self):
        out = self.out("D11_OTHER_CLAUSE")
        self.assertEqual(out["evidence_comparator"], "EQ")
        self.assertEqual(out["relation"], "refutes")

    def test_measure_mismatch_unresolved(self):
        self.assertEqual(self.out("D12_MEASURE_MISMATCH")["relation"], "unresolved")

    def test_unit_dimension_mismatch_unresolved(self):
        self.assertEqual(self.out("D13_PERCENT_POINTS")["relation"], "unresolved")

    def test_year_mismatch_unresolved_and_preserved(self):
        out = self.out("D14_YEAR_MISMATCH")
        self.assertEqual(out["relation"], "unresolved")
        self.assertEqual(out["claim_years"], ["2025"])
        self.assertEqual(out["evidence_years"], ["2024"])

    def test_increase_decrease_refutes(self):
        self.assertEqual(self.out("D15_INCREASE_DECREASE")["relation"], "refutes")

    def test_event_only_not_applicable(self):
        out = self.out("D16_EVENT_ONLY")
        self.assertEqual(out["status"], "not_applicable")
        self.assertEqual(out["relation"], "not_applicable")

    def test_spans_are_in_bounds_when_applicable(self):
        for case in CASES:
            out = ADAPTER.analyze(case["claim"], case["evidence"])
            if out["status"] == "not_applicable":
                continue
            self.assertTrue(out["consumed_claim_spans"])
            self.assertTrue(out["consumed_evidence_spans"])
            for a, b in out["consumed_claim_spans"]:
                self.assertGreaterEqual(a, 0); self.assertLessEqual(b, len(case["claim"])); self.assertLess(a, b)
            for a, b in out["consumed_evidence_spans"]:
                self.assertGreaterEqual(a, 0); self.assertLessEqual(b, len(case["evidence"])); self.assertLess(a, b)


class QuantityOnly(Oracle):
    @staticmethod
    def analyze(claim, evidence):
        out = Oracle.analyze(claim, evidence)
        if out["status"] != "not_applicable" and any(ch.isdigit() for ch in claim) and any(ch.isdigit() for ch in evidence):
            out["relation"] = "supports"
        return out

class SharedVerb(Oracle):
    @staticmethod
    def analyze(claim, evidence):
        out = Oracle.analyze(claim, evidence)
        if "grew" in claim and "grew" in evidence:
            out["relation"] = "supports"; out["evidence_comparator"] = out["claim_comparator"]
        return out

class CueNoRole(Oracle):
    @staticmethod
    def analyze(claim, evidence):
        out = Oracle.analyze(claim, evidence)
        if "score" in evidence and "rate" in evidence:
            out["ambiguity"] = False; out["relation"] = "supports"; out["evidence_comparator"] = "GT"
        return out

class FirstWins(CueNoRole):
    pass

class LastWins(Oracle):
    @staticmethod
    def analyze(claim, evidence):
        out = Oracle.analyze(claim, evidence)
        if "score" in evidence and "rate" in evidence:
            out["ambiguity"] = False; out["relation"] = "supports"; out["evidence_comparator"] = "LT"
        return out

class ParentheticalLoss(Oracle):
    @staticmethod
    def analyze(claim, evidence):
        out = Oracle.analyze(claim, evidence)
        if "(3%)" in evidence:
            out["evidence_comparator"] = out["claim_comparator"]; out["relation"] = "supports"
        return out

class NegationCollapse(Oracle):
    @staticmethod
    def analyze(claim, evidence):
        out = Oracle.analyze(claim, evidence)
        if "did not have more" in evidence:
            out["evidence_comparator"] = "LT"; out["relation"] = "supports"
        return out

class MeasureBlind(Oracle):
    @staticmethod
    def analyze(claim, evidence):
        out = Oracle.analyze(claim, evidence)
        if "asthma" in claim and "COPD" in evidence:
            out["evidence_measure"] = out["claim_measure"]; out["relation"] = "supports"
        return out


def run(adapter: Any) -> dict[str, Any]:
    global ADAPTER
    ADAPTER = adapter
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contract))
    return {
        "tests": result.testsRun,
        "failures": [t._testMethodName for t, _ in result.failures],
        "errors": [t._testMethodName for t, _ in result.errors],
        "skips": len(result.skipped),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--adapter", type=Path)
    args = p.parse_args()
    if args.selftest:
        good = run(Oracle)
        expected = {
            "QuantityOnly": "test_parenthetical_comparator_bound",
            "SharedVerb": "test_faster_slower_bound",
            "CueNoRole": "test_multiple_cues_fail_closed",
            "FirstWins": "test_multiple_cues_fail_closed",
            "LastWins": "test_multiple_cues_fail_closed",
            "ParentheticalLoss": "test_parenthetical_comparator_bound",
            "NegationCollapse": "test_not_more_does_not_become_less",
            "MeasureBlind": "test_measure_mismatch_unresolved",
        }
        mutants = [QuantityOnly, SharedVerb, CueNoRole, FirstWins, LastWins, ParentheticalLoss, NegationCollapse, MeasureBlind]
        controls = {}
        for mutant in mutants:
            r = run(mutant)
            controls[mutant.__name__] = {"intended_test": expected[mutant.__name__], "caught": expected[mutant.__name__] in r["failures"] or expected[mutant.__name__] in r["errors"], "result": r}
        ok = not good["failures"] and not good["errors"] and all(v["caught"] for v in controls.values())
        report = {"evidence_class":"EVALUATOR_SELFTEST_ONLY","candidate_executed":False,"oracle":good,"weak_controls":controls,"passed":ok}
    else:
        spec = importlib.util.spec_from_file_location("candidate_adapter", args.adapter.resolve())
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load adapter")
        module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
        r = run(module)
        ok = not r["failures"] and not r["errors"] and not r["skips"]
        report = {"evidence_class":"EXPOSED_DEVELOPMENT_CONFORMANCE_ONLY","result":r,"passed":ok,"fresh_generalization":"NOT_ESTABLISHED"}
    print(json.dumps(report, sort_keys=True))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
