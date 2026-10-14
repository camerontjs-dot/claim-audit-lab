"""CAL #212 additive V2 receipt evaluator: exposed DEVELOPMENT cases ONLY.

This is a distinct research evaluator, not a revision of #213's frozen
unit_contract_tests.py. Neither --selftest nor --adapter is held-out scoring.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from copy import deepcopy
from pathlib import Path

VERSION = "cal-rc3-quantity-unit-receipt-evaluator-v2-prep1"
ROOT = Path(__file__).resolve().parent
DEFAULT_CASES = ROOT.parent / "cal_v1_quantity_unit_boundary_rc3_20261004" / "DEVELOPMENT_CASES.json"

# Explicit lexical gold derived exclusively from the 19 exposed development
# sentences, before any V2 candidate implementation. Case order is fixed.
LEX = {
    "U01_SYMBOL_WORD": (["%"], ["percent"]),
    "U02_PP_VS_PERCENT": (["percentage points"], ["percent"]),
    "U03_PERCENT_VS_PP": (["percent"], ["percentage points"]),
    "U04_PP_BP": (["percentage point"], ["basis points"]),
    "U05_BP_PP_HALF": (["basis points"], ["percentage points"]),
    "U06_PERCENT_CHANGE_VS_PP": (["percent"], ["percentage points"]),
    "U07_LEVEL_VS_CHANGE": (["percent"], ["percent"]),
    "U08_ENDPOINT_PP": (["percentage points"], ["percent", "percent"]),
    "U09_ENDPOINT_RELATIVE": (["percent"], ["percent", "percent"]),
    "U10_PREFIX_BOUNDARY": (["percentage points"], ["percent"]),
    "U11_PP_ABBREV": (["pp"], ["percentage points"]),
    "U12_BP_ABBREV": (["bp"], ["basis points"]),
    "U13_RATE_COUNT": (["percent"], ["percent"]),
    "U14_MEASURE_MISMATCH": (["percentage point"], ["basis points"]),
    "U15_YEAR_MISMATCH": (["percentage point"], ["basis points"]),
    "U16_MULTIPLE_UNITS": (["percentage points"], ["percent", "percentage point"]),
    "U17_NEGATED_COMPARATOR": (["percentage points"], ["percentage points"]),
    "U18_EVENT_ONLY": ([], []),
    "U19_EXPOSED_HOL14_SHAPE": (["percentage points"], ["%"]),
}
NUM = {
    "U01_SYMBOL_WORD": (["10"], ["10"]),
    "U02_PP_VS_PERCENT": (["10"], ["10"]),
    "U03_PERCENT_VS_PP": (["10"], ["10"]),
    "U04_PP_BP": (["1"], ["100"]),
    "U05_BP_PP_HALF": (["50"], ["0.5"]),
    "U06_PERCENT_CHANGE_VS_PP": (["2"], ["2"]),
    "U07_LEVEL_VS_CHANGE": (["5"], ["5"]),
    "U08_ENDPOINT_PP": (["2"], ["10", "12"]),
    "U09_ENDPOINT_RELATIVE": (["20"], ["10", "12"]),
    "U10_PREFIX_BOUNDARY": (["10"], ["10"]),
    "U11_PP_ABBREV": (["2"], ["2"]),
    "U12_BP_ABBREV": (["50"], ["50"]),
    "U13_RATE_COUNT": (["10"], ["10"]),
    "U14_MEASURE_MISMATCH": (["1"], ["100"]),
    "U15_YEAR_MISMATCH": (["1"], ["100"]),
    "U16_MULTIPLE_UNITS": (["2"], ["2", "1"]),
    "U17_NEGATED_COMPARATOR": (["10"], ["10"]),
    "U18_EVENT_ONLY": ([], []),
    "U19_EXPOSED_HOL14_SHAPE": (["10"], ["10"]),
}
CMP = {
    "U01_SYMBOL_WORD": ("level_eq", "level_eq"),
    "U02_PP_VS_PERCENT": ("less_than", "less_than"),
    "U03_PERCENT_VS_PP": ("less_than", "less_than"),
    "U04_PP_BP": ("increase", "increase"),
    "U05_BP_PP_HALF": ("increase", "increase"),
    "U06_PERCENT_CHANGE_VS_PP": ("increase", "increase"),
    "U07_LEVEL_VS_CHANGE": ("level_eq", "increase"),
    "U08_ENDPOINT_PP": ("increase", "increase_from_to"),
    "U09_ENDPOINT_RELATIVE": ("increase", "increase_from_to"),
    "U10_PREFIX_BOUNDARY": ("level_eq", "level_eq"),
    "U11_PP_ABBREV": ("increase", "increase"),
    "U12_BP_ABBREV": ("increase", "increase"),
    "U13_RATE_COUNT": ("increase", "increase"),
    "U14_MEASURE_MISMATCH": ("increase", "increase"),
    "U15_YEAR_MISMATCH": ("increase", "increase"),
    "U16_MULTIPLE_UNITS": ("increase", "increase"),
    "U17_NEGATED_COMPARATOR": ("less_than", "not_less_than"),
    "U18_EVENT_ONLY": ("not_applicable", "not_applicable"),
    "U19_EXPOSED_HOL14_SHAPE": ("less_than", "less_than"),
}
UNRESOLVED = {
    "U02_PP_VS_PERCENT": "unit_mismatch",
    "U03_PERCENT_VS_PP": "unit_mismatch",
    "U06_PERCENT_CHANGE_VS_PP": "unit_role_mismatch",
    "U07_LEVEL_VS_CHANGE": "unit_role_mismatch",
    "U10_PREFIX_BOUNDARY": "unit_mismatch",
    "U11_PP_ABBREV": "unknown_abbreviation",
    "U13_RATE_COUNT": "measure_mismatch",
    "U14_MEASURE_MISMATCH": "measure_mismatch",
    "U15_YEAR_MISMATCH": "year_scope_mismatch",
    "U19_EXPOSED_HOL14_SHAPE": "unit_mismatch",
}
APPLIED = {
    "U04_PP_BP": "100bp=1pp",
    "U05_BP_PP_HALF": "100bp=1pp",
    "U08_ENDPOINT_PP": "endpoints_to_pp",
    "U09_ENDPOINT_RELATIVE": "endpoints_to_relative_percent",
}
# On U16 the deciding evidence is the second measure, not the first score.
DECIDING_INDICES = {"U16_MULTIPLE_UNITS": {"evidence": [1]}}
IDENTITY = {
    "%": "percent", "percent": "percent",
    "percentage point": "percentage_point",
    "percentage points": "percentage_point",
    "basis point": "basis_point", "basis points": "basis_point",
    "bp": "basis_point", "bps": "basis_point",
    "pp": "unknown",
}


def spans_for(text: str, words: list[str], numeric: bool = False) -> list[list[int]]:
    """Find each preselected literal in source order; fail on absent gold."""
    out = []
    cursor = 0
    for word in words:
        if numeric:
            m = re.search(r"(?<!\d)" + re.escape(word) + r"(?!\d)", text[cursor:])
            if m is None:
                raise ValueError("missing exposed numeric oracle: " + word)
            lo = cursor + m.start()
        else:
            lo = text.find(word, cursor)
            if lo < 0:
                raise ValueError("missing exposed lexical oracle: " + word)
        hi = lo + len(word)
        out.append([lo, hi])
        cursor = hi
    return out


def expected_side(c: dict, side: str) -> dict:
    cid = c["id"]
    idx = 0 if side == "claim" else 1
    text = c[side]
    words = LEX[cid][idx]
    nums = NUM[cid][idx]
    return {
        "unit_tokens": [
            {"span": span, "normalized_identity": IDENTITY[word]}
            for word, span in zip(words, spans_for(text, words))
        ],
        "numeric_tokens": [
            {"span": span, "value": word}
            for word, span in zip(nums, spans_for(text, nums, numeric=True))
        ],
        "quantity_role": c[side + "_unit"],
        "measure": c.get("measure") if side == "claim" else c.get("evidence_measure", c.get("measure")),
        "comparator": CMP[cid][idx],
        "time_scope": c.get(side + "_years", []),
        # This is a syntactically legitimate but intentionally weak self-test
        # consumption reference. It is not proof of actual causal consumption.
        "consumed_spans": [] if cid == "U18_EVENT_ONLY" else [[0, len(text)]],
        "ambiguity_reason": "unregistered_pp" if cid == "U11_PP_ABBREV" and side == "claim" else None,
    }


def reference(c: dict) -> dict:
    rel = c["expected_relation"]
    return {
        "status": "not_applicable" if rel == "not_applicable" else ("unresolved" if rel == "unresolved" else "claimed"),
        "relation": rel,
        "claim_unit": c["claim_unit"],
        "evidence_unit": c["evidence_unit"],
        "claim_measure": c.get("measure"),
        "evidence_measure": c.get("evidence_measure", c.get("measure")),
        "claim_years": c.get("claim_years", []),
        "evidence_years": c.get("evidence_years", []),
        "conversion": c.get("conversion"),
        "ambiguity": rel == "unresolved",
        "receipt_v2": {
            "input_scope": {"claim": [0, len(c["claim"])], "evidence": [0, len(c["evidence"])]},
            "quantities": {
                "claim": expected_side(c, "claim"),
                "evidence": expected_side(c, "evidence"),
            },
            "unresolved_reason": UNRESOLVED.get(c["id"]),
            "conversion_rule": {
                "available": [c["conversion"]] if c.get("conversion") else [],
                "applied": APPLIED.get(c["id"]),
                "rejected_reason": (
                    "measure_mismatch" if c["id"] == "U14_MEASURE_MISMATCH"
                    else "year_scope_mismatch" if c["id"] == "U15_YEAR_MISMATCH"
                    else None
                ),
            },
        },
    }


def covers(windows: object, anchor: list[int], text: str) -> bool:
    if not isinstance(windows, list):
        return False
    for w in windows:
        if not isinstance(w, list) or len(w) != 2:
            return False
        start, end = w
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in (start, end)):
            return False
        if not (0 <= start < end <= len(text)):
            return False
    return any(w[0] <= anchor[0] and w[1] >= anchor[1] for w in windows)


def validate(receipt: object, c: dict) -> list[str]:
    """Named semantic failures; weak controls must fail at their intended gate."""
    if not isinstance(receipt, dict):
        return ["receipt_shape"]
    ref = reference(c)
    issues = []
    for field in ("status", "relation", "claim_unit", "evidence_unit",
                  "claim_measure", "evidence_measure", "claim_years", "evidence_years",
                  "conversion", "ambiguity"):
        if receipt.get(field) != ref[field]:
            issues.append(field + "_semantics")
    v = receipt.get("receipt_v2")
    if not isinstance(v, dict):
        return issues + ["receipt_v2_missing"]
    if v.get("input_scope") != ref["receipt_v2"]["input_scope"]:
        issues.append("input_scope_identity")
    if v.get("unresolved_reason") != ref["receipt_v2"]["unresolved_reason"]:
        issues.append("refusal_reason")
    if v.get("conversion_rule") != ref["receipt_v2"]["conversion_rule"]:
        issues.append("conversion_application")
    qs = v.get("quantities")
    if not isinstance(qs, dict):
        return issues + ["quantities_missing"]
    for side in ("claim", "evidence"):
        got = qs.get(side)
        if not isinstance(got, dict):
            issues.append(side + "_quantity_missing")
            continue
        exp = ref["receipt_v2"]["quantities"][side]
        text = c[side]
        for field, error in (
            ("unit_tokens", "lexical_unit_span_or_identity"),
            ("numeric_tokens", "numeric_binding"),
            ("quantity_role", "quantity_role"),
            ("measure", "measure_binding"),
            ("comparator", "comparator_negation"),
            ("time_scope", "time_scope"),
            ("ambiguity_reason", "local_ambiguity"),
        ):
            if got.get(field) != exp[field]:
                issues.append(side + "_" + error)
        windows = got.get("consumed_spans")
        if c["id"] == "U18_EVENT_ONLY":
            if windows != []:
                issues.append(side + "_event_consumption")
            continue
        if not isinstance(windows, list) or not windows:
            issues.append(side + "_consumed_missing")
            continue
        deciding = DECIDING_INDICES.get(c["id"], {}).get(side)
        for typ in ("unit_tokens", "numeric_tokens"):
            tokens = exp[typ]
            ids = deciding if deciding is not None else list(range(len(tokens)))
            for i in ids:
                if i >= len(tokens) or not covers(windows, tokens[i]["span"], text):
                    issues.append(side + "_consumed_anchor_missing")
                    break
    return sorted(set(issues))


def all_cases(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data["cases"]
    ids = [c["id"] for c in cases]
    if len(cases) != 19 or len(set(ids)) != 19 or set(ids) != set(LEX) or set(ids) != set(NUM):
        raise RuntimeError("19-case development cohort mismatch")
    return cases


def mutate(reference_receipt: dict, name: str) -> dict:
    x = deepcopy(reference_receipt)
    q = x["receipt_v2"]["quantities"]
    if name == "whole_sentence_unit":
        q["claim"]["unit_tokens"][0]["span"] = [0, 17]
    elif name == "percent_prefix_inside_percentage":
        start = "The margin was less than 10 percentage points.".index("percentage points")
        q["claim"]["unit_tokens"][0]["span"] = [start, start + len("percent")]
        q["claim"]["unit_tokens"][0]["normalized_identity"] = "percent"
    elif name == "missing_consumed_span":
        q["claim"]["consumed_spans"] = []
    elif name == "wrong_quantity_value":
        q["evidence"]["numeric_tokens"][1]["value"] = "2"
    elif name == "role_loss":
        q["claim"]["quantity_role"] = "percent_level"
    elif name == "measure_loss":
        q["evidence"]["measure"] = q["claim"]["measure"]
    elif name == "negation_loss":
        q["evidence"]["comparator"] = "less_than"
    elif name == "conversion_without_measure":
        x["receipt_v2"]["conversion_rule"]["applied"] = "100bp=1pp"
    elif name == "year_scope_loss":
        q["evidence"]["time_scope"] = ["2025"]
    elif name == "one_endpoint_not_consumed":
        # Structurally valid, but omits the second evidence endpoint.
        q["evidence"]["consumed_spans"] = [[0, 28]]
    else:
        raise ValueError("unknown control: " + name)
    return x


CONTROLS = {
    "whole_sentence_unit": ("U01_SYMBOL_WORD", "claim_lexical_unit_span_or_identity"),
    "percent_prefix_inside_percentage": ("U02_PP_VS_PERCENT", "claim_lexical_unit_span_or_identity"),
    "missing_consumed_span": ("U01_SYMBOL_WORD", "claim_consumed_missing"),
    "wrong_quantity_value": ("U16_MULTIPLE_UNITS", "evidence_numeric_binding"),
    "role_loss": ("U04_PP_BP", "claim_quantity_role"),
    "measure_loss": ("U14_MEASURE_MISMATCH", "evidence_measure_binding"),
    "negation_loss": ("U17_NEGATED_COMPARATOR", "evidence_comparator_negation"),
    "conversion_without_measure": ("U14_MEASURE_MISMATCH", "conversion_application"),
    "year_scope_loss": ("U15_YEAR_MISMATCH", "evidence_time_scope"),
    "one_endpoint_not_consumed": ("U08_ENDPOINT_PP", "evidence_consumed_anchor_missing"),
}


def main() -> int:
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--adapter", type=Path)
    p.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    a = p.parse_args()
    cases = all_cases(a.cases)
    by_id = {c["id"]: c for c in cases}
    if a.selftest:
        positive = {c["id"]: validate(reference(c), c) for c in cases}
        controls = {}
        for name, (cid, intended) in CONTROLS.items():
            problems = validate(mutate(reference(by_id[cid]), name), by_id[cid])
            controls[name] = {
                "case": cid, "intended": intended,
                "caught_for_intended_reason": intended in problems,
                "problems": problems,
            }
        passed = all(not e for e in positive.values()) and all(
            x["caught_for_intended_reason"] for x in controls.values()
        )
        report = {
            "version": VERSION, "evidence_class": "EXPOSED_EVALUATOR_SELFTEST_ONLY",
            "candidate_executed": False, "development_count": len(cases),
            "positive_errors": positive, "weak_controls": controls,
            "passed": passed,
            "non_claims": ["no actual-consumption proof", "no held-out qualification"],
        }
    else:
        spec = importlib.util.spec_from_file_location("rc3_v2_adapter", a.adapter.resolve())
        if spec is None or spec.loader is None:
            raise RuntimeError("invalid adapter path")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        results = {c["id"]: validate(mod.analyze(c["claim"], c["evidence"]), c) for c in cases}
        passed = all(not x for x in results.values())
        report = {
            "version": VERSION, "evidence_class": "EXPOSED_DEVELOPMENT_CONFORMANCE_ONLY",
            "cases": results, "passed": passed, "fresh_generalization": "NOT_ESTABLISHED",
        }
    print(json.dumps(report, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
