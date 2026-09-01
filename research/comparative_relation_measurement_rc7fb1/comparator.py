"""RC7F-B1 bounded deterministic comparison measurement."""
from __future__ import annotations
import re

VERSION="rc7fb1-comparator-1"
REL={
    "more":"MORE_THAN","fewer":"FEWER_THAN","less":"LESS_THAN",
    "greater":"GREATER_THAN","higher":"GREATER_THAN","larger":"GREATER_THAN",
    "lower":"LESS_THAN","smaller":"LESS_THAN",
}
ENTITY=r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
MEASURE=r"share|rate|percentage|proportion|output|count|volume|score|yield"


def _norm(s:str)->str:
    return re.sub(r"\s+"," ",s.strip(" .,:;\"'")).lower()


def _proposal(left,relation,right,cue,*,delta=None,measure=None,span=None):
    return {"status":"CLAIMED","left":_norm(left),"relation":relation,"right":_norm(right),
            "delta_surface":delta.strip() if isinstance(delta,str) else None,
            "measure_surface":measure.strip().lower() if isinstance(measure,str) else None,
            "cue":cue,"span":list(span) if span else None}


def measure(raw_source:str)->dict:
    if not isinstance(raw_source,str) or not raw_source.strip():
        return {"status":"UNRESOLVED","proposals":[],"residue":["empty_source"],"version":VERSION}
    text=" ".join(raw_source.strip().split())

    # Numeric delta: A ..., N more/fewer/less than B.
    p=re.compile(rf"^(?P<left>{ENTITY})\s+.+?,\s*(?P<delta>(?:\d+(?:\.\d+)?|[A-Za-z-]+)(?:\s+(?:percentage\s+points?|percent|%|files?|samples?|units?|items?))?)\s+(?P<rel>(?i:more|fewer|less))\s+than\s+(?P<right>{ENTITY})\.?$")
    m=p.match(text)
    if m:
        r=m.group("rel").lower(); return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),REL[r],m.group("right"),r+" than",delta=m.group("delta"),span=m.span("rel"))],"residue":[],"version":VERSION}

    # Adjective + explicit measure head + than. This generalizes parent share/rate
    # attachment to the frozen successor measure vocabulary.
    p=re.compile(rf"^(?P<left>{ENTITY})\s+.+?(?:,\s*|\s+)(?:a\s+)?(?P<rel>(?i:greater|higher|larger|lower|smaller))\s+(?P<measure>(?i:{MEASURE}))\s+than\s+(?P<right>{ENTITY})\.?$")
    m=p.match(text)
    if m:
        r=m.group("rel").lower(); mh=m.group("measure").lower()
        return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),REL[r],m.group("right"),r+" "+mh+" than",measure=mh,span=m.span("rel"))],"residue":[],"version":VERSION}

    # Direct entity adjective comparison.
    p=re.compile(rf"^(?P<left>{ENTITY})\s+.+?\b(?P<rel>(?i:greater|higher|larger|lower|smaller))\s+than\s+(?P<right>{ENTITY})\.?$")
    m=p.match(text)
    if m:
        r=m.group("rel").lower(); return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),REL[r],m.group("right"),r+" than",span=m.span("rel"))],"residue":[],"version":VERSION}

    # Explicit comparative verbs. No synonym expansion in this successor.
    p=re.compile(rf"^(?P<left>{ENTITY})\s+(?P<verb>(?i:exceeded|trailed))\s+(?P<right>{ENTITY})(?:\s+by\s+(?P<delta>\d+(?:\.\d+)?(?:\s+(?:percentage\s+points?|percent|%|files?|samples?|units?|items?))?))?\.?$")
    m=p.match(text)
    if m:
        v=m.group("verb").lower(); relation="MORE_THAN" if v=="exceeded" else "LESS_THAN"
        return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),relation,m.group("right"),v,delta=m.group("delta"),span=m.span("verb"))],"residue":[],"version":VERSION}

    # Equality / same-as.
    p=re.compile(rf"^(?P<left>{ENTITY})\s+.+?\b(?:(?i:equal\s+to)|(?i:the\s+same(?:\s+\w+){{0,3}}\s+as))\s+(?P<right>{ENTITY})\.?$")
    m=p.match(text)
    if m: return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),"EQUAL_TO",m.group("right"),"equal/same")],"residue":[],"version":VERSION}

    # Multipliers.
    p=re.compile(rf"^(?P<left>{ENTITY})\s+.+?\b(?P<mult>(?i:twice|half))\s+as(?:\s+\w+){{0,3}}\s+as\s+(?P<right>{ENTITY})\.?$")
    m=p.match(text)
    if m:
        factor="2" if m.group("mult").lower()=="twice" else "0.5"
        return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),"MULTIPLE_OF",m.group("right"),m.group("mult").lower(),delta=factor)],"residue":[],"version":VERSION}

    # Scalar thresholds.
    p=re.compile(r"^(?:The\s+)?(?P<left>[A-Za-z][A-Za-z -]{0,40}?)\s+(?:was|is|remained|stayed)\s+(?P<rel>(?i:more|less|greater|higher|lower))\s+than\s+(?P<right>\d+(?:\.\d+)?(?:\s*%|\s+[A-Za-zµμ/]+)?)\.?$")
    m=p.match(text)
    if m:
        r=m.group("rel").lower(); return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),REL[r],m.group("right"),r+" than")],"residue":[],"version":VERSION}

    if re.search(r"\b(more|fewer|less|greater|higher|larger|lower|smaller|equal|same|twice|half|exceeded|trailed)\b",text,re.I):
        return {"status":"UNRESOLVED","proposals":[],"residue":["comparative_cue_without_supported_attachment"],"version":VERSION}
    return {"status":"NOT_APPLICABLE","proposals":[],"residue":[],"version":VERSION}
