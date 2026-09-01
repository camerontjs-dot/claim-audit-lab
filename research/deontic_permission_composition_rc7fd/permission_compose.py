"""RC7F-D bounded permission + modifier semantic measurement."""
from __future__ import annotations
import re
VERSION="rc7fd-permission-composition-1"
EXC_CUES=("with the exception of","apart from","excluding","save for","except")
TEMP_CUES=("as of","before","after","until")

def _norm(s): return re.sub(r"\s+"," ",s.strip(" .,:;\"'")).lower()

def _split_tail(text:str):
    s=text.strip().rstrip('.').strip(); low=s.lower(); hits=[]
    for cue in EXC_CUES+TEMP_CUES:
        m=re.search(rf"(?:,\s*|\s+)({re.escape(cue)})\s+(.+)$",s,re.I)
        if m: hits.append((m.start(),cue,m.group(2)))
    if not hits: return s,None
    pos,cue,value=min(hits,key=lambda x:x[0])
    return s[:pos].strip().rstrip(','), (cue.lower(),value.strip())

def measure(raw_source:str)->dict:
    if not isinstance(raw_source,str) or not raw_source.strip():
        return {"status":"UNRESOLVED","proposals":[],"residue":["empty_source"],"version":VERSION}
    text=" ".join(raw_source.strip().split())
    permission_surface=None; population=None; predicate=None; tail=None
    m=re.match(r"^Only\s+(?P<pop>[A-Za-z][A-Za-z -]{0,80}?)\s+may\s+(?P<rest>.+)$",text,re.I)
    if m:
        permission_surface="only_may"; population=m.group('pop'); predicate,tail=_split_tail(m.group('rest'))
    else:
        m=re.match(r"^Permission\s+to\s+(?P<pred>.+?)\s+is\s+restricted\s+to\s+(?P<rest>.+)$",text,re.I)
        if m:
            permission_surface="restricted_to"; predicate=m.group('pred'); population,tail=_split_tail(m.group('rest'))
    if not permission_surface:
        if re.search(r"\b(permission|may|except|excluding|before|after|until|as of)\b",text,re.I):
            return {"status":"UNRESOLVED","proposals":[],"residue":["deontic_or_scope_cue_outside_supported_surface"],"version":VERSION}
        return {"status":"NOT_APPLICABLE","proposals":[],"residue":[],"version":VERSION}
    proposal={"kind":"necessary_permission_condition","surface":permission_surface,
              "population":_norm(population),"predicate":_norm(predicate),"exception":None,"temporal":None}
    if tail:
        cue,value=tail
        if cue in EXC_CUES:
            proposal["exception"]={"excluded":_norm(value),"cue":cue}
        elif cue in TEMP_CUES:
            proposal["temporal"]={"relation":"as_of" if cue=="as of" else cue,"reference":_norm(value),"cue":cue}
    return {"status":"CLAIMED","proposals":[proposal],"residue":[],"version":VERSION}
