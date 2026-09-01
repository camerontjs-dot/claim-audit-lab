"""Bounded deterministic comparative-relation measurement for RC7F-B."""
from __future__ import annotations
import re

VERSION = "rc7fb-comparator-1"
REL = {
    "more": "MORE_THAN", "fewer": "FEWER_THAN", "less": "LESS_THAN",
    "greater": "GREATER_THAN", "higher": "GREATER_THAN", "larger": "GREATER_THAN",
    "lower": "LESS_THAN", "smaller": "LESS_THAN",
}
ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip(" .,:;\"'" )).lower()


def _proposal(left, relation, right, cue, *, delta=None, measure=None, span=None):
    return {
        "status": "CLAIMED", "left": _norm(left), "relation": relation, "right": _norm(right),
        "delta_surface": delta.strip() if isinstance(delta,str) else None,
        "measure_surface": measure.strip() if isinstance(measure,str) else None,
        "cue": cue, "span": list(span) if span else None,
    }


def measure(raw_source: str) -> dict:
    if not isinstance(raw_source, str) or not raw_source.strip():
        return {"status":"UNRESOLVED","proposals":[],"residue":["empty_source"],"version":VERSION}
    text=" ".join(raw_source.strip().split())

    # Entity-to-entity numeric delta.
    pat = re.compile(
        rf"^(?P<left>{ENTITY})\s+.+?,\s*(?P<delta>(?:\d+(?:\.\d+)?|[A-Za-z-]+)(?:\s+(?:percentage\s+points?|percent|%|files?|samples?|units?|items?))?)\s+(?P<rel>(?i:more|fewer|less))\s+than\s+(?P<right>{ENTITY})\.?$"
    )
    m=pat.match(text)
    if m:
        r=m.group("rel").lower()
        return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),REL[r],m.group("right"),r+" than",delta=m.group("delta"),span=m.span("rel"))],"residue":[],"version":VERSION}

    # Share/rate/percentage comparisons.
    pat = re.compile(
        rf"^(?P<left>{ENTITY})\s+.+?(?:,\s*|\s+)(?:a\s+)?(?P<rel>(?i:greater|higher|larger|lower|smaller))\s+(?P<measure>(?i:share|rate|percentage|proportion))\s+than\s+(?P<right>{ENTITY})\.?$"
    )
    m=pat.match(text)
    if m:
        r=m.group("rel").lower(); measure=m.group("measure").lower()
        return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),REL[r],m.group("right"),r+" "+measure+" than",measure=measure,span=m.span("rel"))],"residue":[],"version":VERSION}

    # Direct entity comparison.
    pat = re.compile(
        rf"^(?P<left>{ENTITY})\s+.+?\b(?P<rel>(?i:greater|higher|larger|lower|smaller))\s+than\s+(?P<right>{ENTITY})\.?$"
    )
    m=pat.match(text)
    if m:
        r=m.group("rel").lower()
        return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),REL[r],m.group("right"),r+" than",span=m.span("rel"))],"residue":[],"version":VERSION}

    # Equality / same-as.
    pat = re.compile(rf"^(?P<left>{ENTITY})\s+.+?\b(?:(?i:equal\s+to)|(?i:the\s+same(?:\s+\w+){{0,3}}\s+as))\s+(?P<right>{ENTITY})\.?$")
    m=pat.match(text)
    if m:
        return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),"EQUAL_TO",m.group("right"),"equal/same")],"residue":[],"version":VERSION}

    # Multipliers.
    pat = re.compile(rf"^(?P<left>{ENTITY})\s+.+?\b(?P<mult>(?i:twice|half))\s+as(?:\s+\w+){{0,3}}\s+as\s+(?P<right>{ENTITY})\.?$")
    m=pat.match(text)
    if m:
        factor="2" if m.group("mult").lower()=="twice" else "0.5"
        return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),"MULTIPLE_OF",m.group("right"),m.group("mult").lower(),delta=factor)],"residue":[],"version":VERSION}

    # Scalar thresholds.
    pat = re.compile(r"^(?:The\s+)?(?P<left>[A-Za-z][A-Za-z -]{0,40}?)\s+(?:was|is|remained|stayed)\s+(?P<rel>(?i:more|less|greater|higher|lower))\s+than\s+(?P<right>\d+(?:\.\d+)?(?:\s*%|\s+[A-Za-zµμ/]+)?)\.?$")
    m=pat.match(text)
    if m:
        r=m.group("rel").lower()
        return {"status":"CLAIMED","proposals":[_proposal(m.group("left"),REL[r],m.group("right"),r+" than")],"residue":[],"version":VERSION}

    if re.search(r"\b(more|fewer|less|greater|higher|larger|lower|smaller|equal|same|twice|half)\b", text, re.I):
        return {"status":"UNRESOLVED","proposals":[],"residue":["comparative_cue_without_supported_attachment"],"version":VERSION}
    return {"status":"NOT_APPLICABLE","proposals":[],"residue":[],"version":VERSION}
