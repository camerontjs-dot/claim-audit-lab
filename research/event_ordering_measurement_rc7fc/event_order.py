"""RC7F-C bounded explicit event-ordering measurement."""
from __future__ import annotations
import re
VERSION="rc7fc-event-order-1"
SUBJ=r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
PAST={"reviewed":"review","signed":"sign","inspected":"inspect","released":"release","approved":"approve","archived":"archive","processed":"process","verified":"verify","recorded":"record"}
BASE="|".join(sorted(set(PAST.values())))
PAST_RE="|".join(PAST)

def _norm(s): return re.sub(r"\s+"," ",s.strip(" .,:;\"'")).lower()
def _event(subject,predicate,obj,polarity="positive"):
    return {"subject":_norm(subject),"predicate":predicate,"object":_norm(obj),"polarity":polarity}

def _parse_at_end(segment:str):
    p=re.compile(rf"(?P<s>{SUBJ})\s+(?:did\s+not\s+(?P<neg>{BASE})|(?P<pos>{PAST_RE}))\s+(?P<o>[A-Za-z0-9][A-Za-z0-9 -]{{0,60}}?)\.?$",re.I)
    m=p.search(segment.strip())
    if not m:return None
    if m.group("neg"): pred=m.group("neg").lower(); pol="negative"
    else: pred=PAST[m.group("pos").lower()]; pol="positive"
    return _event(m.group("s"),pred,m.group("o"),pol)

def _parse_at_start(segment:str):
    p=re.compile(rf"^(?P<s>{SUBJ})\s+(?:did\s+not\s+(?P<neg>{BASE})|(?P<pos>{PAST_RE}))\s+(?P<o>[A-Za-z0-9][A-Za-z0-9 -]{{0,60}}?)(?:\.|$)",re.I)
    m=p.match(segment.strip())
    if not m:return None
    if m.group("neg"): pred=m.group("neg").lower(); pol="negative"
    else: pred=PAST[m.group("pos").lower()]; pol="positive"
    return _event(m.group("s"),pred,m.group("o"),pol)

def measure(raw_source:str)->dict:
    if not isinstance(raw_source,str) or not raw_source.strip():
        return {"status":"UNRESOLVED","proposals":[],"residue":["empty_source"],"version":VERSION}
    matches=list(re.finditer(r"\b(before|after)\b",raw_source,re.I))
    if len(matches)!=1:
        return {"status":"UNRESOLVED" if matches else "NOT_APPLICABLE","proposals":[],"residue":["ordering_cue_cardinality"] if matches else [],"version":VERSION}
    m=matches[0]; left=_parse_at_end(raw_source[:m.start()]); right=_parse_at_start(raw_source[m.end():])
    if not left or not right:
        return {"status":"UNRESOLVED","proposals":[],"residue":["ordering_cue_without_two_supported_events"],"version":VERSION}
    rel=m.group(1).upper()
    return {"status":"CLAIMED","proposals":[{"left_event":left,"relation":rel,"right_event":right,"cue":m.group(1).lower(),"span":[m.start(),m.end()]}],"residue":[],"version":VERSION}
