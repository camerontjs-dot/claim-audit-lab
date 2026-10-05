"""Frozen development evaluator for CAL #212 quantity-unit boundary."""
from __future__ import annotations
import argparse, importlib.util, io, json, sys, unittest
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CASES=json.loads((ROOT/"DEVELOPMENT_CASES.json").read_text())["cases"]
BY={(c["claim"],c["evidence"]):c for c in CASES}

def expected(c):
    return {
        "status":"not_applicable" if c["expected_relation"]=="not_applicable" else ("unresolved" if c["expected_relation"]=="unresolved" else "claimed"),
        "relation":c["expected_relation"],
        "claim_unit":c["claim_unit"],
        "evidence_unit":c["evidence_unit"],
        "claim_measure":c.get("measure"),
        "evidence_measure":c.get("evidence_measure",c.get("measure")),
        "conversion":c.get("conversion"),
        "claim_years":c.get("claim_years",[]),
        "evidence_years":c.get("evidence_years",[]),
        "ambiguity":c["expected_relation"]=="unresolved",
        "claim_unit_spans":[] if c["claim_unit"]=="not_applicable" else [[0,len(c["claim"])]],
        "evidence_unit_spans":[] if c["evidence_unit"]=="not_applicable" else [[0,len(c["evidence"])]],
    }

class Oracle:
    @staticmethod
    def analyze(claim,evidence):
        return deepcopy(expected(BY[(claim,evidence)]))

ADAPTER=Oracle

class Contract(unittest.TestCase):
    def out(self,cid):
        c=next(x for x in CASES if x["id"]==cid)
        v=ADAPTER.analyze(c["claim"],c["evidence"])
        self.assertIsInstance(v,dict)
        return v

    def test_exact_relations(self):
        for c in CASES:
            with self.subTest(c=c["id"]):
                self.assertEqual(ADAPTER.analyze(c["claim"],c["evidence"])["relation"],c["expected_relation"])

    def test_percent_lexical_equivalence(self):
        self.assertEqual(self.out("U01_SYMBOL_WORD")["relation"],"supports")

    def test_percentage_points_not_percent(self):
        for cid in ("U02_PP_VS_PERCENT","U03_PERCENT_VS_PP","U10_PREFIX_BOUNDARY","U19_EXPOSED_HOL14_SHAPE"):
            self.assertEqual(self.out(cid)["relation"],"unresolved")

    def test_basis_point_registered_conversions(self):
        u04=self.out("U04_PP_BP")
        self.assertEqual(u04["relation"],"supports")
        self.assertEqual(u04["claim_unit"],"percentage_point_change")
        self.assertEqual(u04["evidence_unit"],"basis_point_change")
        u05=self.out("U05_BP_PP_HALF")
        self.assertEqual(u05["relation"],"supports")
        self.assertEqual(u05["claim_unit"],"basis_point_change")
        self.assertEqual(u05["evidence_unit"],"percentage_point_change")

    def test_relative_percent_not_pp(self):
        self.assertEqual(self.out("U06_PERCENT_CHANGE_VS_PP")["relation"],"unresolved")

    def test_level_not_change(self):
        self.assertEqual(self.out("U07_LEVEL_VS_CHANGE")["relation"],"unresolved")

    def test_endpoint_roles(self):
        self.assertEqual(self.out("U08_ENDPOINT_PP")["relation"],"supports")
        self.assertEqual(self.out("U09_ENDPOINT_RELATIVE")["relation"],"supports")

    def test_unknown_pp_fails_closed(self):
        self.assertEqual(self.out("U11_PP_ABBREV")["relation"],"unresolved")

    def test_bp_variant(self):
        self.assertEqual(self.out("U12_BP_ABBREV")["relation"],"supports")

    def test_rate_count_mismatch(self):
        self.assertEqual(self.out("U13_RATE_COUNT")["relation"],"unresolved")

    def test_conversion_preserves_measure(self):
        self.assertEqual(self.out("U14_MEASURE_MISMATCH")["relation"],"unresolved")

    def test_conversion_preserves_year(self):
        self.assertEqual(self.out("U15_YEAR_MISMATCH")["relation"],"unresolved")

    def test_multiple_units_bind_measure(self):
        self.assertEqual(self.out("U16_MULTIPLE_UNITS")["relation"],"refutes")

    def test_negated_comparator(self):
        self.assertEqual(self.out("U17_NEGATED_COMPARATOR")["relation"],"refutes")

    def test_event_not_applicable(self):
        self.assertEqual(self.out("U18_EVENT_ONLY")["relation"],"not_applicable")

class PrefixPercent(Oracle):
    @staticmethod
    def analyze(claim,evidence):
        o=Oracle.analyze(claim,evidence)
        if "percent" in claim.lower(): o["claim_unit"]="percent_level"
        if "percent" in evidence.lower(): o["evidence_unit"]="percent_level"
        if o["claim_unit"]==o["evidence_unit"] and o["status"]!="not_applicable": o["relation"]="supports"
        return o

class NumericOnly(Oracle):
    @staticmethod
    def analyze(claim,evidence):
        o=Oracle.analyze(claim,evidence)
        if any(x.isdigit() for x in claim) and any(x.isdigit() for x in evidence) and o["status"]!="not_applicable":
            o["relation"]="supports"
        return o

class StripUnits(NumericOnly):
    pass

class PointsCollapse(PrefixPercent):
    pass

class BasisCollapse(Oracle):
    @staticmethod
    def analyze(claim,evidence):
        o=Oracle.analyze(claim,evidence)
        if "basis point" in claim.lower(): o["claim_unit"]="percent_level"
        if "basis point" in evidence.lower(): o["evidence_unit"]="percent_level"
        return o

class RateCountCollapse(Oracle):
    @staticmethod
    def analyze(claim,evidence):
        o=Oracle.analyze(claim,evidence)
        if BY[(claim,evidence)]["id"]=="U13_RATE_COUNT": o["relation"]="supports"
        return o

class FirstUnitWins(Oracle):
    @staticmethod
    def analyze(claim,evidence):
        o=Oracle.analyze(claim,evidence)
        if BY[(claim,evidence)]["id"]=="U16_MULTIPLE_UNITS": o["relation"]="unresolved"
        return o

class LastUnitWins(Oracle):
    @staticmethod
    def analyze(claim,evidence):
        o=Oracle.analyze(claim,evidence)
        if BY[(claim,evidence)]["id"]=="U16_MULTIPLE_UNITS": o["relation"]="supports"
        return o

class ConversionNoMeasure(Oracle):
    @staticmethod
    def analyze(claim,evidence):
        o=Oracle.analyze(claim,evidence)
        if BY[(claim,evidence)]["id"]=="U14_MEASURE_MISMATCH": o["relation"]="supports"
        return o

def run(adapter):
    global ADAPTER
    ADAPTER=adapter
    r=unittest.TextTestRunner(stream=io.StringIO(),verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Contract)
    )
    return {
        "tests":r.testsRun,
        "failures":[t._testMethodName for t,_ in r.failures],
        "errors":[t._testMethodName for t,_ in r.errors],
        "skips":len(r.skipped),
    }

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest",action="store_true")
    g.add_argument("--adapter",type=Path)
    a=p.parse_args()

    if a.selftest:
        good=run(Oracle)
        mutants={
            PrefixPercent:"test_percentage_points_not_percent",
            NumericOnly:"test_percentage_points_not_percent",
            StripUnits:"test_percentage_points_not_percent",
            PointsCollapse:"test_percentage_points_not_percent",
            BasisCollapse:"test_basis_point_registered_conversions",
            RateCountCollapse:"test_rate_count_mismatch",
            FirstUnitWins:"test_multiple_units_bind_measure",
            LastUnitWins:"test_multiple_units_bind_measure",
            ConversionNoMeasure:"test_conversion_preserves_measure",
        }
        controls={}
        for cls,intended in mutants.items():
            rr=run(cls)
            controls[cls.__name__]={
                "intended_test":intended,
                "caught":intended in rr["failures"] or intended in rr["errors"],
                "result":rr,
            }
        ok=not good["failures"] and not good["errors"] and all(x["caught"] for x in controls.values())
        report={
            "evidence_class":"EVALUATOR_SELFTEST_ONLY",
            "candidate_executed":False,
            "oracle":good,
            "weak_controls":controls,
            "passed":ok,
        }
    else:
        spec=importlib.util.spec_from_file_location("candidate_adapter",a.adapter.resolve())
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load adapter")
        mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=mod
        spec.loader.exec_module(mod)
        rr=run(mod)
        ok=not rr["failures"] and not rr["errors"] and not rr["skips"]
        report={
            "evidence_class":"EXPOSED_DEVELOPMENT_CONFORMANCE_ONLY",
            "result":rr,
            "passed":ok,
            "fresh_generalization":"NOT_ESTABLISHED",
        }

    print(json.dumps(report,sort_keys=True))
    return 0 if ok else 1

if __name__=="__main__":
    raise SystemExit(main())
