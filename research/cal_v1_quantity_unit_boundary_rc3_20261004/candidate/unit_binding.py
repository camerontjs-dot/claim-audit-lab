"""CAL #212 RC3 quantity-unit and dimension binding, successor s2.

Unit identity, semantic dimension, comparator, subject/measure, scope and exact
conversions are explicit. This remains a bounded research instrument.
"""
from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import Any

INSTRUMENT_ID = "quantity-unit-boundary-rc3-s5"

_NUM = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_SPLIT = re.compile(r"(?<!a\.m\.)(?<!p\.m\.)(?<!e\.g\.)(?<!i\.e\.)(?<!u\.s\.)(?<=[.!?])\s+|\s*,?\s*while\s+|\s+but\s+|\s*;\s*", re.I)
_PP = re.compile(rf"(?P<value>{_NUM})\s*(?P<unit>percentage[- ]points?)\b", re.I)
_BP = re.compile(rf"(?P<value>{_NUM})\s*(?P<unit>basis[- ]points?|bps?\b)", re.I)
_PP_ABBR = re.compile(rf"(?P<value>{_NUM})\s+(?P<unit>pp)\b", re.I)
_PERCENT = re.compile(rf"(?P<value>{_NUM})\s*(?P<unit>%|percent\b(?!age))", re.I)
_ENDPOINT = re.compile(
    rf"(?:rose|increased|grew|moved|changed)\s+from\s+(?P<start>{_NUM})\s*(?:%|percent\b)"
    rf"\s+to\s+(?P<end>{_NUM})\s*(?:%|percent\b)",
    re.I,
)
_RANGE = re.compile(
    rf"(?:range(?:d|s)?\s+from\s+)?(?P<start>{_NUM})\s+to\s+(?P<end>{_NUM})\s*"
    rf"(?P<unit>percentage[- ]points?|basis[- ]points?|%|percent\b)",
    re.I,
)
_CHANGE_UP = re.compile(r"\b(?:increase(?:d)?|rise|rose|grew|growth|moved up|revised up|additional)\b", re.I)
_CHANGE_DOWN = re.compile(r"\b(?:decrease(?:d)?|fell|declined|drop(?:ped)?|moved down|revised down)\b", re.I)
_THRESHOLD = re.compile(r"\b(?P<neg>not\s+)?(?P<word>less|fewer|lower|more|greater|higher)\s+than\b", re.I)
_AFTER_COMP = re.compile(
    r"\b(?P<word>higher|lower|more|less|greater|fewer)"
    r"(?:\s+in\s+(?:19|20)\d{2})?\s+than\b|\b(?P<simple>above|below)\b",
    re.I,
)
_BEFORE_COMP = re.compile(r"\b(?P<word>over|under|above|below|more than|less than|greater than|fewer than)\s*$", re.I)
_EQUAL = re.compile(r"\b(?:equal(?:led)?|unchanged|same|tied)\b", re.I)
_RELATIVE = re.compile(r"\b(?:change|changed|increase|increased|decrease|decreased|rose|fell|grew|growth|declined)\b", re.I)
_PAREN_ACRONYM = re.compile(r"\s*\([A-Z][A-Z0-9&/-]{1,12}\)\s*")
_EM_QUAL = re.compile(r"—[^—]{0,120}—")
_STOPWORDS = {"the","a","an","of","in","for","by","to","as","about","approximately","nearly","around","today","indeed","we","find","that"}

def _dec(v: str | Decimal) -> Decimal:
    return v if isinstance(v, Decimal) else Decimal(str(v).replace(",", ""))

def _num(v: Decimal | None) -> str | None:
    if v is None:
        return None
    s=format(v.normalize(),"f")
    if "." in s:
        s=s.rstrip("0").rstrip(".")
    return s or "0"

def _years(text: str) -> list[str]:
    return _YEAR.findall(text)

def _clean_text(raw: str) -> str:
    s=_EM_QUAL.sub(" ",raw)
    s=_PAREN_ACRONYM.sub(" ",s)
    s=re.sub(r"\b(?:in|during)\s+(?:19|20)\d{2},?\s*"," ",s,flags=re.I)
    s=re.sub(r"[’']s\b","",s)
    s=re.sub(r"[^a-zA-Z0-9\s-]"," ",s)
    s=re.sub(r"\s+"," ",s).strip().casefold()
    s=re.sub(r"^(?:by contrast|today|indeed)\s+","",s)
    s=re.sub(r"^(?:the|a|an)\s+","",s)
    return s or ""

def _tokens(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {x for x in _clean_text(raw).split() if x not in _STOPWORDS and len(x)>1}

def _compatible_text(a: str | None,b: str | None) -> bool:
    if not a or not b:
        return a==b
    aa,bb=_tokens(a),_tokens(b)
    if not aa or not bb:
        return False
    if aa==bb:
        return True
    small,big=(aa,bb) if len(aa)<=len(bb) else (bb,aa)
    return len(small)>=1 and small.issubset(big) and len(small & big)>=min(2,len(small))

def _unit_role(raw: str, clause: str, subject: str | None) -> str:
    u=raw.casefold()
    if u.startswith("percentage"):
        return "percentage_point_change"
    if u.startswith("basis") or u in {"bp","bps"}:
        return "basis_point_change"
    if u=="pp":
        return "unknown"
    if _RELATIVE.search(clause) or (subject and subject.endswith(" change")):
        return "percent_relative_change"
    return "percent_level"

def _subject_before(clause: str, marker_start: int) -> str | None:
    prefix=clause[:marker_start]
    # relation frames
    frames=[
        r"^(?P<s>.+?)\s+(?:increased|decreased|rose|fell|grew|declined|dropped)(?:\s+by)?\s*$",
        r"^(?P<s>.+?)\s+(?:accounts?|accounted)\s+for\s+(?:over|under|about|nearly|around|approximately)?\s*$",
        r"^(?P<s>.+?)\s+(?:was|were|is|are|has been|had been)\s+(?:projected\s+to\s+be\s+)?(?:about\s+)?$",
        r"^(?P<s>.+?)\s+(?:traded|stood|sits?)\s+(?:about\s+)?$",
        r"^(?P<s>.+?)\s+(?:has been |had been |was |were )?(?:revised\s+(?:up|down)\s+by|increased\s+by|decreased\s+by|rose\s+by|fell\s+by|grew\s+by|declined\s+by|subject to an additional)\s*$",
        r"^(?P<s>.+?)\s+(?:cited as an obstacle by)\s*$",
    ]
    cleaned=_EM_QUAL.sub(" ",prefix)
    cleaned=_PAREN_ACRONYM.sub(" ",cleaned)
    for pat in frames:
        m=re.search(pat,cleaned,re.I)
        if m:
            return _clean_text(m.group("s"))
    # "78 percent of X" has no subject before the number.
    return None

def _after_of(clause: str, end: int) -> tuple[str | None,str | None]:
    tail=clause[end:]
    m=re.match(r"\s+of\s+(?P<obj>[^,.;]+)",tail,re.I)
    if not m:
        return None,None
    obj=m.group("obj")
    # Preserve time condition but remove a neutral occurrence verb.
    obj=re.sub(r"\b(?:occurs?|occurred)\b"," ",obj,flags=re.I)
    obj=re.sub(r"\s+"," ",obj).strip()
    return _clean_text(obj),_clean_text(obj)

def _measure_subject(clause: str,start: int,end: int) -> tuple[str|None,str|None]:
    prefix=clause[:start]
    range_subject=re.search(
        r"(?:^|,)\s*(?:with\s+)?(?P<s>[^,]{1,80}?)\s+(?:range(?:d|s)?|ranging)\s+from\s*$",
        prefix,
        re.I,
    )
    if range_subject:
        label=_clean_text(range_subject.group("s"))
        if label:
            return label,label
    subj=_subject_before(clause,start)
    after_subj,after_measure=_after_of(clause,end)
    if subj:
        # "accounts for N of measure": subject plus distinct measure
        if re.search(r"\baccounts?\s+for\b",clause[:start],re.I) and after_measure:
            return subj,after_measure
        if re.search(r"\b(?:increase|increased|decrease|decreased|rose|fell|grew|declined|revised)\b",clause[:start],re.I):
            return subj, (subj if subj.endswith(" change") else subj+" change")
        return subj,subj
    if after_subj:
        return after_subj,after_measure
    # table/list label immediately before the number
    prev=clause[:start]
    prev=re.split(r"[%)]\s*|,\s*|;\s*",prev)[-1]
    prev=re.sub(r"^(?:percent|percentage of businesses)\s+","",prev,flags=re.I)
    label=_clean_text(prev)
    if label and len(label.split())<=8:
        return label,label
    return None,None

def _comp_for(clause: str,start: int,end: int) -> str:
    before=clause[max(0,start-90):start]
    after=clause[end:min(len(clause),end+100)]
    m=_THRESHOLD.search(before)
    if m:
        word=m.group("word").casefold(); gt=word in {"more","greater","higher"}
        if m.group("neg"):
            return "NOT_GT" if gt else "NOT_LT"
        return "GT" if gt else "LT"
    m=_BEFORE_COMP.search(before)
    if m:
        w=m.group("word").casefold()
        return "GT" if w in {"over","above","more than","greater than"} else "LT"
    m=_AFTER_COMP.search(after)
    if m:
        w=(m.group("word") or m.group("simple")).casefold()
        return "GT" if w in {"higher","more","greater","above"} else "LT"
    if _CHANGE_DOWN.search(before):
        return "DECREASE"
    if _CHANGE_UP.search(before):
        return "INCREASE"
    if _EQUAL.search(clause):
        return "EQ"
    if re.search(r"\b(?:was|were|is|are)\b",before,re.I):
        return "EQ"
    # Bare percentage levels/tables are exact level assertions.
    return "EQ"

def _fact(value:Decimal|None,unit:str,lexical:str,subject:str|None,measure:str|None,comp:str,
          span:tuple[int,int],cspan:tuple[int,int],years:list[str],**extra:Any)->dict[str,Any]:
    row={"value":_num(value),"unit":unit,"lexical_unit":lexical,"subject":subject,"measure":measure,
         "comparator":comp,"unit_span":[*span],"consumed_span":[*cspan],"years":years,
         "conversion":extra.pop("conversion",None),"derived":extra.pop("derived",False)}
    row.update(extra); return row

def extract_facts(text:str)->list[dict[str,Any]]:
    facts=[]
    cursor=0
    for piece in _SPLIT.split(text):
        if not piece: continue
        idx=text.find(piece,cursor); idx=cursor if idx<0 else idx; cursor=idx+len(piece)
        clause=piece.strip(); trim=len(piece)-len(piece.lstrip()); base=idx+trim
        cspan=(base,base+len(clause)); years=_years(clause)
        occupied=[]

        # Generic "X accounts for N% of M, followed by Y (N%), Z (N%)..." list.
        account=re.search(rf"(?P<s>.+?)\s+accounts?\s+for\s+(?P<v>{_NUM})\s*(?P<u>%|percent\b)\s+of\s+(?P<m>[^,]+)",clause,re.I)
        inherited_measure=None
        if account:
            subj=_clean_text(account.group("s")); inherited_measure=_clean_text(account.group("m"))
            span=(base+account.start("v"),base+account.end("u")); occupied.append((account.start("v"),account.end("u")))
            facts.append(_fact(_dec(account.group("v")),"percent_level",account.group("u"),subj,inherited_measure,"EQ",span,cspan,years))
            tail=clause[account.end():]
            for lm in re.finditer(rf"(?P<s>[A-Za-z][A-Za-z -]{{1,40}})\s*\(\s*(?P<v>{_NUM})\s*(?P<u>%|percent\b)\s*\)",tail,re.I):
                subj2=_clean_text(lm.group("s"))
                local_start=account.end()+lm.start("v"); local_end=account.end()+lm.end("u")
                occupied.append((local_start,local_end))
                facts.append(_fact(_dec(lm.group("v")),"percent_level",lm.group("u"),subj2,inherited_measure,"EQ",
                                   (base+local_start,base+local_end),cspan,years))

        ep=_ENDPOINT.search(clause)
        if ep:
            start,end=_dec(ep.group("start")),_dec(ep.group("end")); diff=end-start
            direction="INCREASE" if diff>0 else "DECREASE" if diff<0 else "EQ"
            subj,measure=_measure_subject(clause,ep.start(),ep.end())
            if measure and not measure.endswith(" change"): measure += " change"
            span=(base+ep.start(),base+ep.end()); occupied.append((ep.start(),ep.end()))
            facts.append(_fact(abs(diff),"percentage_point_change","derived:endpoints",subj,measure,direction,span,cspan,years,
                               conversion="endpoints_to_pp",derived=True))
            if start!=0:
                facts.append(_fact(abs(diff/start*Decimal("100")),"percent_relative_change","derived:endpoints",subj,measure,direction,span,cspan,years,
                                   conversion="endpoints_to_relative_percent",derived=True))

        rg=_RANGE.search(clause)
        if rg:
            unit=_unit_role(rg.group("unit"),clause,None); subj,measure=_measure_subject(clause,rg.start(),rg.end())
            span=(base+rg.start(),base+rg.end()); occupied.append((rg.start(),rg.end()))
            facts.append(_fact(_dec(rg.group("end")),unit,rg.group("unit"),subj,measure,"RANGE",span,cspan,years,
                               range_min=_num(_dec(rg.group("start"))),range_max=_num(_dec(rg.group("end")))))

        for rx in (_PP,_BP,_PP_ABBR,_PERCENT):
            for m in rx.finditer(clause):
                if any(a<=m.start() and m.end()<=b for a,b in occupied): continue
                unit=_unit_role(m.group("unit"),clause,None)
                subj,measure=_measure_subject(clause,m.start(),m.end())
                # Re-evaluate percent role after measure is known.
                unit=_unit_role(m.group("unit"),clause,measure)
                comp=_comp_for(clause,m.start(),m.end())
                facts.append(_fact(_dec(m.group("value")),unit,m.group("unit"),subj,measure,comp,
                                   (base+m.start(),base+m.end()),cspan,years,
                                   conversion="bp_lexical_variant" if m.group("unit").casefold() in {"bp","bps"} else None))
    return facts

def _convert(v:Decimal,src:str,dst:str)->tuple[Decimal|None,str|None]:
    if src==dst: return v,None
    if src=="basis_point_change" and dst=="percentage_point_change": return v/Decimal("100"),"100bp=1pp"
    if src=="percentage_point_change" and dst=="basis_point_change": return v*Decimal("100"),"100bp=1pp"
    return None,None

def _context_ok(a:dict[str,Any],b:dict[str,Any])->bool:
    if a.get("subject") and b.get("subject") and not _compatible_text(a["subject"],b["subject"]):
        return False
    if a.get("measure") and b.get("measure") and not _compatible_text(a["measure"],b["measure"]):
        return False
    return True

def _select_pair(cf:list[dict[str,Any]],ef:list[dict[str,Any]])->tuple[dict[str,Any]|None,dict[str,Any]|None,str|None]:
    if not cf: return None,None,"claim_no_quantity_unit"
    scores=[]
    for a in cf:
        for b in ef:
            score=0
            if _context_ok(a,b): score+=12
            if a["unit"]==b["unit"]: score+=8
            elif {a["unit"],b["unit"]}=={"basis_point_change","percentage_point_change"}: score+=7
            if a["comparator"]==b["comparator"]: score+=4
            if a["value"]==b["value"]: score+=4
            if set(a["years"])==set(b["years"]): score+=1
            if b.get("derived"): score+=1
            scores.append((score,a,b))
    if not scores: return cf[0],None,"evidence_no_quantity_unit"
    scores.sort(key=lambda x:x[0],reverse=True)
    best=scores[0]
    if len(scores)>1 and scores[1][0]==best[0]:
        x,y=scores[0],scores[1]
        sig=lambda z:(z[1].get("subject"),z[1].get("measure"),z[1]["unit"],z[2].get("subject"),z[2].get("measure"),z[2]["unit"],z[2]["value"])
        if sig(x)!=sig(y): return best[1],best[2],"ambiguous_unit_binding"
    if best[1]["unit"]=="unknown": return best[1],best[2],"unknown_claim_unit"
    return best[1],best[2],None

def _opposite(a:str,b:str)->bool:
    return {a,b} in ({"GT","LT"},{"NOT_GT","GT"},{"NOT_LT","LT"},{"INCREASE","DECREASE"})

def _relation(a:dict[str,Any],b:dict[str,Any])->tuple[str,str|None,str|None]:
    if a["unit"]=="unknown" or b["unit"]=="unknown": return "unresolved","unknown_unit",None
    if not _context_ok(a,b): return "unresolved","measure_or_subject_mismatch",None
    if set(a["years"])!=set(b["years"]): return "unresolved","time_mismatch",None
    if a["comparator"]=="RANGE" or b["comparator"]=="RANGE":
        if a["comparator"]==b["comparator"] and a["unit"]==b["unit"] and a.get("range_min")==b.get("range_min") and a.get("range_max")==b.get("range_max"):
            return "supports",None,None
        return "unresolved","range_mismatch",None
    av,bv=_dec(a["value"]),_dec(b["value"])
    bv2,conv=_convert(bv,b["unit"],a["unit"])
    if bv2 is None: return "unresolved","unit_dimension_mismatch",None
    ac,bc=a["comparator"],b["comparator"]
    if ac=="NA" or bc=="NA": return "unresolved","comparator_unbound",conv
    if ac==bc:
        return ("supports",None,conv) if av==bv2 else ("refutes","exact_magnitude_mismatch",conv)
    if _opposite(ac,bc):
        return ("refutes",None,conv) if av==bv2 else ("unresolved","comparator_and_magnitude_differ",conv)
    if "EQ" in {ac,bc} and av==bv2: return "refutes",None,conv
    return "unresolved","relation_family_mismatch",conv

def analyze(claim:str,evidence:str)->dict[str,Any]:
    cf,ef=extract_facts(claim),extract_facts(evidence)
    if not cf:
        return {"status":"not_applicable","relation":"not_applicable","claim_unit":"not_applicable","evidence_unit":"not_applicable",
                "claim_measure":None,"evidence_measure":None,"claim_years":_years(claim),"evidence_years":_years(evidence),
                "ambiguity":False,"claim_unit_spans":[],"evidence_unit_spans":[],"claim_value":None,"evidence_value":None,
                "conversion":None,"claim_comparator":"NA","evidence_comparator":"NA","consumed_claim_spans":[],"consumed_evidence_spans":[],
                "abstention_cause":"no_quantity_unit","instrument_id":INSTRUMENT_ID,"claim_facts":[],"evidence_facts":ef}
    a,b,problem=_select_pair(cf,ef)
    assert a is not None
    if b is None:
        rel,cause,conv="unresolved",problem or "evidence_no_quantity_unit",None
        eu,em,ev,ec,esp="unknown",None,None,"NA",[]
    elif problem:
        rel,cause,conv="unresolved",problem,None
        eu,em,ev,ec,esp=b["unit"],b.get("measure"),b["value"],b["comparator"],[b["unit_span"]]
    else:
        rel,cause,conv=_relation(a,b)
        eu,em,ev,ec,esp=b["unit"],b.get("measure"),b["value"],b["comparator"],[b["unit_span"]]
    return {"status":"claimed" if rel in {"supports","refutes"} else "unresolved","relation":rel,
            "claim_unit":a["unit"],"evidence_unit":eu,"claim_measure":a.get("measure"),"evidence_measure":em,
            "claim_subject":a.get("subject"),"evidence_subject":b.get("subject") if b else None,
            "claim_years":a["years"] or _years(claim),"evidence_years":(b["years"] if b else _years(evidence)),
            "ambiguity":problem=="ambiguous_unit_binding","claim_unit_spans":[a["unit_span"]],"evidence_unit_spans":esp,
            "claim_value":a["value"],"evidence_value":ev,"conversion":conv or a.get("conversion") or (b.get("conversion") if b else None),
            "claim_comparator":a["comparator"],"evidence_comparator":ec,"consumed_claim_spans":[a["consumed_span"]],
            "consumed_evidence_spans":[b["consumed_span"]] if b else [],"abstention_cause":cause,"instrument_id":INSTRUMENT_ID,
            "claim_facts":cf,"evidence_facts":ef}

def _apply_rc2_fallback(receipt:dict[str,Any],envelope:dict[str,Any])->None:
    import sys
    d=Path(__file__).resolve().parents[2]/"cal_v1_quantity_comparator_binding_rc2_20261004"/"candidate"
    if str(d) not in sys.path: sys.path.insert(0,str(d))
    import quantity_binding as rc2
    rc2.apply_quantity_receipt(receipt,envelope)
    receipt["instrument_id"]=INSTRUMENT_ID+"+rc2-fallback"
    receipt["unit_boundary_fallback"]=True

def apply_quantity_receipt(receipt:dict[str,Any],envelope:dict[str,Any])->None:
    claim=str(envelope["claim"]); passages=[str(x["text"]) for x in envelope["evidence"]]
    cf=extract_facts(claim)
    if not cf:
        _apply_rc2_fallback(receipt,envelope); return
    receipt["instrument_id"]=INSTRUMENT_ID
    receipt["binding"]={"claim_facts":cf,"passages":[]}
    receipt["applicability"]="applicable"
    if not passages:
        receipt["conclusion"]="unresolved"; receipt["abstention_cause"]="missing_evidence"; return
    opinions=[]; causes=[]
    for text in passages:
        row=analyze(claim,text); receipt["binding"]["passages"].append(row)
        if row["relation"]!="not_applicable": opinions.append(row["relation"]); causes.append(row.get("abstention_cause"))
    if "supports" in opinions and "refutes" in opinions:
        receipt["conclusion"]="unresolved"; receipt["abstention_cause"]="material_conflict"; receipt["local_material_conflict"]=True
    elif "supports" in opinions:
        receipt["conclusion"]="supports"; receipt["abstention_cause"]=None
    elif "refutes" in opinions:
        receipt["conclusion"]="refutes"; receipt["abstention_cause"]=None
    else:
        receipt["conclusion"]="unresolved"; receipt["abstention_cause"]=next((c for c in causes if c),"no_matching_passage")
