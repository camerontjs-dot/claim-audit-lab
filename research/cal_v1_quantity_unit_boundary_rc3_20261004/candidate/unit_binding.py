"""Bounded quantity-unit and dimension binding for CAL #212 RC3.

This successor sits in front of the frozen RC2 comparator relation. Unit identity,
semantic dimension, measure, scope and exact conversions are explicit. A lexical
prefix or matching number is never sufficient unit authority.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

INSTRUMENT_ID = "quantity-unit-boundary-rc3-s1"

_NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_ARTICLE_RE = re.compile(r"^(?:the|a|an)\s+", re.I)
_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\s*,?\s*while\s+|\s*;\s*", re.I)

_PP_RE = re.compile(rf"(?P<value>{_NUM})\s*(?P<unit>percentage[- ]points?)\b", re.I)
_BP_RE = re.compile(rf"(?P<value>{_NUM})\s*(?P<unit>basis[- ]points?|bps?\b)", re.I)
_PP_ABBR_RE = re.compile(rf"(?P<value>{_NUM})\s+(?P<unit>pp)\b", re.I)
_PERCENT_RE = re.compile(rf"(?P<value>{_NUM})\s*(?P<unit>%|percent\b(?!age))", re.I)
_ENDPOINT_RE = re.compile(
    rf"(?:rose|increased|grew|moved|changed)\s+from\s+"
    rf"(?P<start>{_NUM})\s*(?:%|percent\b)\s+to\s+"
    rf"(?P<end>{_NUM})\s*(?:%|percent\b)",
    re.I,
)
_CHANGE_UP_RE = re.compile(r"\b(?:increase(?:d)?|rose|grew|rise|rising|up)\b", re.I)
_CHANGE_DOWN_RE = re.compile(r"\b(?:decrease(?:d)?|fell|declined|decline|drop(?:ped)?|down)\b", re.I)
_THRESHOLD_RE = re.compile(r"\b(?P<neg>not\s+)?(?P<word>less|fewer|lower|more|greater|higher)\s+than\b", re.I)
_EQUAL_RE = re.compile(r"\b(?:equal(?:led)?|unchanged|same|tied)\b", re.I)
_RELATIVE_CUE_RE = re.compile(r"\b(?:change|changed|increase|increased|decrease|decreased|rose|fell|grew|declined|growth)\b", re.I)

def _d(raw: str | Decimal) -> Decimal:
    if isinstance(raw, Decimal):
        return raw
    return Decimal(str(raw).replace(",", ""))

def _canon_number(value: Decimal | None) -> str | None:
    if value is None:
        return None
    n = value.normalize()
    text = format(n, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"

def _years(text: str) -> list[str]:
    return _YEAR_RE.findall(text)

def _norm_measure(raw: str) -> str | None:
    text = raw.casefold()
    text = _YEAR_RE.sub(" ", text)
    text = re.sub(r"['’]s\b", "", text)
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = _ARTICLE_RE.sub("", text)
    text = re.sub(r"\b(?:in|during|for)\s*$", "", text).strip()
    return text or None

def _measure_for_clause(clause: str) -> str | None:
    # Change form: "the unemployment rate rose by ..."
    m = re.search(
        r"^(?P<subject>.+?)\s+(?:increase(?:d)?|rose|grew|decrease(?:d)?|fell|declined|dropped|moved|changed)\b",
        clause,
        re.I,
    )
    if m:
        base = _norm_measure(m.group("subject"))
        if base:
            return base if base.endswith(" change") else base + " change"
    # Copular/threshold form: "the margin was less than ..."
    m = re.search(r"^(?P<subject>.+?)\s+(?:was|were|is|are|has been|had been)\b", clause, re.I)
    if m:
        return _norm_measure(m.group("subject"))
    return None

def _comparator(clause: str) -> str:
    m = _THRESHOLD_RE.search(clause)
    if m:
        word = m.group("word").casefold()
        gt = word in {"more", "greater", "higher"}
        if m.group("neg"):
            return "NOT_GT" if gt else "NOT_LT"
        return "GT" if gt else "LT"
    if _CHANGE_DOWN_RE.search(clause):
        return "DECREASE"
    if _CHANGE_UP_RE.search(clause):
        return "INCREASE"
    if _EQUAL_RE.search(clause):
        return "EQ"
    if re.search(r"\b(?:was|were|is|are)\b", clause, re.I):
        return "EQ"
    return "NA"

def _role_for_percent(clause: str, measure: str | None) -> str:
    if _RELATIVE_CUE_RE.search(clause):
        return "percent_relative_change"
    if measure and measure.endswith(" change"):
        return "percent_relative_change"
    return "percent_level"

def _fact(
    *,
    value: Decimal | None,
    unit: str,
    lexical_unit: str,
    measure: str | None,
    comparator: str,
    span: tuple[int, int],
    clause_span: tuple[int, int],
    years: list[str],
    conversion: str | None = None,
    derived: bool = False,
) -> dict[str, Any]:
    return {
        "value": _canon_number(value),
        "unit": unit,
        "lexical_unit": lexical_unit,
        "measure": measure,
        "comparator": comparator,
        "unit_span": [span[0], span[1]],
        "consumed_span": [clause_span[0], clause_span[1]],
        "years": years,
        "conversion": conversion,
        "derived": derived,
    }

def extract_facts(text: str) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    cursor = 0
    for piece in _SPLIT_RE.split(text):
        if not piece:
            continue
        idx = text.find(piece, cursor)
        if idx < 0:
            idx = cursor
        cursor = idx + len(piece)
        clause = piece.strip()
        left_trim = len(piece) - len(piece.lstrip())
        base = idx + left_trim
        cspan = (base, base + len(clause))
        measure = _measure_for_clause(clause)
        comp = _comparator(clause)
        years = _years(clause)

        endpoint = _ENDPOINT_RE.search(clause)
        endpoint_local_span = None
        if endpoint:
            endpoint_local_span = (endpoint.start(), endpoint.end())
            start = _d(endpoint.group("start"))
            end = _d(endpoint.group("end"))
            diff = end - start
            direction = "INCREASE" if diff > 0 else ("DECREASE" if diff < 0 else "EQ")
            rel = (diff / start * Decimal("100")) if start != 0 else None
            span = (base + endpoint.start(), base + endpoint.end())
            endpoint_measure = measure
            if endpoint_measure and not endpoint_measure.endswith(" change"):
                endpoint_measure += " change"
            facts.append(_fact(value=abs(diff), unit="percentage_point_change",
                               lexical_unit="derived:endpoints", measure=endpoint_measure,
                               comparator=direction, span=span, clause_span=cspan, years=years,
                               conversion="endpoints_to_pp", derived=True))
            if rel is not None:
                facts.append(_fact(value=abs(rel), unit="percent_relative_change",
                                   lexical_unit="derived:endpoints", measure=endpoint_measure,
                                   comparator=direction, span=span, clause_span=cspan, years=years,
                                   conversion="endpoints_to_relative_percent", derived=True))

        occupied: list[tuple[int, int]] = []
        for rx, unit_name in ((_PP_RE, "percentage_point_change"), (_BP_RE, "basis_point_change"), (_PP_ABBR_RE, "unknown")):
            for m in rx.finditer(clause):
                occupied.append((m.start(), m.end()))
                facts.append(_fact(value=_d(m.group("value")), unit=unit_name,
                                   lexical_unit=m.group("unit"), measure=measure,
                                   comparator=comp, span=(base+m.start(), base+m.end()),
                                   clause_span=cspan, years=years,
                                   conversion="bp_lexical_variant" if unit_name=="basis_point_change" and m.group("unit").casefold() in {"bp","bps"} else None))
        for m in _PERCENT_RE.finditer(clause):
            if any(a <= m.start() < b or a < m.end() <= b for a,b in occupied):
                continue
            if endpoint_local_span and endpoint_local_span[0] <= m.start() and m.end() <= endpoint_local_span[1]:
                continue
            role = _role_for_percent(clause, measure)
            facts.append(_fact(value=_d(m.group("value")), unit=role,
                               lexical_unit=m.group("unit"), measure=measure,
                               comparator=comp, span=(base+m.start(), base+m.end()),
                               clause_span=cspan, years=years))
    return facts

def _measure_compatible(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return a == b
    return a == b

def _convert(value: Decimal, src: str, dst: str) -> tuple[Decimal | None, str | None]:
    if src == dst:
        return value, None
    if src == "basis_point_change" and dst == "percentage_point_change":
        return value / Decimal("100"), "100bp=1pp"
    if src == "percentage_point_change" and dst == "basis_point_change":
        return value * Decimal("100"), "100bp=1pp"
    return None, None

def _opposite(a: str, b: str) -> bool:
    return {a,b} in ({"GT","LT"},{"NOT_GT","GT"},{"NOT_LT","LT"},{"INCREASE","DECREASE"})

def _select_pair(claim_facts: list[dict[str, Any]], evidence_facts: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str | None]:
    if not claim_facts:
        return None, None, "claim_no_quantity_unit"
    unknown_claim = next((f for f in claim_facts if f["unit"] == "unknown"), None)

    candidates: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    for cf in claim_facts:
        for ef in evidence_facts:
            score = 0
            if _measure_compatible(cf["measure"], ef["measure"]):
                score += 8
            if cf["unit"] == ef["unit"]:
                score += 6
            elif {cf["unit"],ef["unit"]} == {"basis_point_change","percentage_point_change"}:
                score += 5
            if cf["comparator"] == ef["comparator"]:
                score += 2
            if set(cf["years"]) == set(ef["years"]):
                score += 1
            candidates.append((score,cf,ef))
    if not candidates:
        return claim_facts[0], None, "evidence_no_quantity_unit"
    if unknown_claim is not None:
        compatible = sorted(
            ((8 if _measure_compatible(unknown_claim["measure"], ef["measure"]) else 0, ef) for ef in evidence_facts),
            key=lambda item: item[0],
            reverse=True,
        )
        return unknown_claim, (compatible[0][1] if compatible else None), "unknown_claim_unit"
    candidates.sort(key=lambda x:x[0], reverse=True)
    best_score,cf,ef=candidates[0]
    if len(candidates)>1 and candidates[1][0]==best_score:
        # If tied pairs differ materially, fail closed.
        _,cf2,ef2=candidates[1]
        if (cf["measure"],cf["unit"],ef["measure"],ef["unit"],ef["value"]) != (cf2["measure"],cf2["unit"],ef2["measure"],ef2["unit"],ef2["value"]):
            return cf, ef, "ambiguous_unit_binding"
    return cf,ef,None

def _relation(cf: dict[str, Any], ef: dict[str, Any]) -> tuple[str,str|None,str|None]:
    if cf["unit"]=="unknown" or ef["unit"]=="unknown":
        return "unresolved","unknown_unit",None
    if not _measure_compatible(cf["measure"],ef["measure"]):
        return "unresolved","measure_mismatch",None
    if set(cf["years"]) != set(ef["years"]):
        return "unresolved","time_mismatch",None
    cv=_d(cf["value"]) if cf["value"] is not None else None
    ev=_d(ef["value"]) if ef["value"] is not None else None
    if cv is None or ev is None:
        return "unresolved","quantity_unbound",None
    ev2,conversion=_convert(ev,ef["unit"],cf["unit"])
    if ev2 is None:
        return "unresolved","unit_dimension_mismatch",None

    cc,ec=cf["comparator"],ef["comparator"]
    if cc == "NA" or ec == "NA":
        return "unresolved","comparator_unbound",conversion
    if cc == ec:
        if cv == ev2:
            return "supports",None,conversion
        # Exact amounts with the same bounded measure/dimension assert different magnitudes.
        return "refutes","exact_magnitude_mismatch",conversion
    if _opposite(cc,ec):
        if cv == ev2:
            return "refutes",None,conversion
        return "unresolved","comparator_and_magnitude_differ",conversion
    # Equality versus a directional exact claim is a contradiction when magnitude is same.
    if "EQ" in {cc,ec} and cv == ev2:
        return "refutes",None,conversion
    return "unresolved","relation_family_mismatch",conversion

def analyze(claim: str, evidence: str) -> dict[str, Any]:
    cfacts=extract_facts(claim)
    efacts=extract_facts(evidence)
    if not cfacts:
        return {
            "status":"not_applicable","relation":"not_applicable",
            "claim_unit":"not_applicable","evidence_unit":"not_applicable",
            "claim_measure":None,"evidence_measure":None,
            "claim_years":_years(claim),"evidence_years":_years(evidence),
            "ambiguity":False,"claim_unit_spans":[],"evidence_unit_spans":[],
            "claim_value":None,"evidence_value":None,"conversion":None,
            "claim_comparator":"NA","evidence_comparator":"NA",
            "consumed_claim_spans":[],"consumed_evidence_spans":[],
            "abstention_cause":"no_quantity_unit","instrument_id":INSTRUMENT_ID,
            "claim_facts":[],"evidence_facts":efacts,
        }
    cf,ef,problem=_select_pair(cfacts,efacts)
    if cf is None:
        raise AssertionError("claim fact selection failed")
    if ef is None:
        relation="unresolved"; cause=problem or "evidence_no_quantity_unit"; conversion=None
        eunit="unknown"; emeasure=None; evalue=None; ecomp="NA"; espans=[]
    else:
        if problem:
            relation="unresolved"; cause=problem; conversion=None
        else:
            relation,cause,conversion=_relation(cf,ef)
        eunit=ef["unit"]; emeasure=ef["measure"]; evalue=ef["value"]; ecomp=ef["comparator"]; espans=[ef["unit_span"]]
    status="claimed" if relation in {"supports","refutes"} else "unresolved"
    return {
        "status":status,"relation":relation,
        "claim_unit":cf["unit"],"evidence_unit":eunit,
        "claim_measure":cf["measure"],"evidence_measure":emeasure,
        "claim_years":cf["years"] or _years(claim),"evidence_years":(ef["years"] if ef else _years(evidence)),
        "ambiguity":problem=="ambiguous_unit_binding",
        "claim_unit_spans":[cf["unit_span"]],"evidence_unit_spans":espans,
        "claim_value":cf["value"],"evidence_value":evalue,
        "conversion":conversion or cf.get("conversion") or (ef.get("conversion") if ef else None),
        "claim_comparator":cf["comparator"],"evidence_comparator":ecomp,
        "consumed_claim_spans":[cf["consumed_span"]],"consumed_evidence_spans":([ef["consumed_span"]] if ef else []),
        "abstention_cause":cause,"instrument_id":INSTRUMENT_ID,
        "claim_facts":cfacts,"evidence_facts":efacts,
    }

def _apply_rc2_fallback(receipt: dict[str, Any], envelope: dict[str, Any]) -> None:
    import sys
    binding_dir = (
        Path(__file__).resolve().parents[2]
        / "cal_v1_quantity_comparator_binding_rc2_20261004"
        / "candidate"
    )
    if str(binding_dir) not in sys.path:
        sys.path.insert(0, str(binding_dir))
    import quantity_binding as rc2_binding
    rc2_binding.apply_quantity_receipt(receipt, envelope)
    receipt["instrument_id"] = INSTRUMENT_ID + "+rc2-fallback"
    receipt["unit_boundary_fallback"] = True


def apply_quantity_receipt(receipt: dict[str, Any], envelope: dict[str, Any]) -> None:
    claim=str(envelope["claim"])
    passages=[str(item["text"]) for item in envelope["evidence"]]
    claim_facts=extract_facts(claim)
    if not claim_facts:
        _apply_rc2_fallback(receipt, envelope)
        return
    receipt["instrument_id"]=INSTRUMENT_ID
    receipt["binding"]={"claim_facts":claim_facts,"passages":[]}
    receipt["applicability"]="applicable"
    if not passages:
        receipt["conclusion"]="unresolved"
        receipt["abstention_cause"]="missing_evidence"
        return
    opinions=[]
    causes=[]
    for text in passages:
        row=analyze(claim,text)
        receipt["binding"]["passages"].append(row)
        if row["relation"]=="not_applicable":
            continue
        opinions.append(row["relation"])
        causes.append(row.get("abstention_cause"))
    if "supports" in opinions and "refutes" in opinions:
        receipt["conclusion"]="unresolved"
        receipt["abstention_cause"]="material_conflict"
        receipt["local_material_conflict"]=True
    elif "supports" in opinions:
        receipt["conclusion"]="supports"; receipt["abstention_cause"]=None
    elif "refutes" in opinions:
        receipt["conclusion"]="refutes"; receipt["abstention_cause"]=None
    else:
        receipt["conclusion"]="unresolved"
        receipt["abstention_cause"]=next((c for c in causes if c),"no_matching_passage")
