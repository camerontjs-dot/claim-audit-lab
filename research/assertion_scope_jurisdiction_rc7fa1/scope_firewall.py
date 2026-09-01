"""RC7F-A1 stacked scope / semantic-warrant candidate.

Research-only. Input is an already-observed local event plus its exact source span.
Observation is not authority: any detected enclosing non-assertive scope fails closed.
"""
from __future__ import annotations

import re

CANDIDATE_VERSION = "rc7fa1-stacked-scope-2"

PATH_TYPES = {
    "UNRESOLVED_EVIDENTIAL", "ATTRIBUTED", "CONDITIONAL_ANTECEDENT",
    "CONDITIONAL_CONSEQUENT", "DEONTIC", "EPISTEMIC", "QUANTIFIED",
}
REPORTING_VERBS = (
    "said", "says", "reported", "reports", "claimed", "claims", "alleged",
    "alleges", "denied", "denies", "stated", "states", "announced", "announces",
    "believed", "believes", "argued", "argues", "asserted", "asserts", "confirmed", "confirms",
)
EVIDENTIAL_ADVERBS = ("supposedly", "purportedly", "reportedly", "allegedly")
EPISTEMIC_PATTERNS = (
    r"\blikely\b", r"\bunlikely\b", r"\bprobably\b", r"\bpossibly\b", r"\bpossible\b",
    r"\bperhaps\b", r"\bmight\b", r"\bcould\b", r"\ba chance\b", r"\bappears? to\b", r"\bseems? to\b",
)
DEONTIC_PATTERNS = (
    r"\bonly\b.{0,80}\bmay\b", r"\bpermitted to\b", r"\ballowed to\b", r"\bauthorized to\b",
    r"\brequired to\b", r"\bmust\b", r"\bshall\b", r"\bprohibited from\b", r"\bforbidden to\b",
)
QUANTIFIER_PATTERNS = (
    r"^\s*all\b", r"^\s*every\b", r"^\s*some\b", r"^\s*no\b", r"^\s*not all\b",
    r"^\s*at least one\b", r"^\s*at most one\b",
    r"^\s*exactly\s+(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
    r"^\s*\d+(?:\.\d+)?%\s+of\b", r"^\s*(?:a|the)\s+majority\s+of\b", r"^\s*few\b", r"^\s*many\b",
)
CONDITIONAL_PREFIXES = ("if ", "unless ", "provided that ", "provided ", "assuming that ")


def _quote_ranges(text: str) -> list[tuple[int, int]]:
    ranges=[]; stack=None
    for i,ch in enumerate(text):
        if ch == "“":
            if stack is None: stack=i
        elif ch == "”":
            if stack is not None: ranges.append((stack,i+1)); stack=None
        elif ch == '"':
            if stack is None: stack=i
            else: ranges.append((stack,i+1)); stack=None
    return ranges


def _evidential_prefix(lower: str, start: int) -> tuple[int, str] | None:
    prefix=lower[:start]
    for word in EVIDENTIAL_ADVERBS:
        m=re.search(rf"(?:^|[.!?]\s+)({word})\b\s*(?:[,;:]|[-–—])?\s*$",prefix)
        if m: return m.start(1),word
    return None


def classify(raw_source: str, observation: dict) -> dict:
    start=observation.get("start"); end=observation.get("end")
    if not isinstance(raw_source,str) or not isinstance(start,int) or not isinstance(end,int):
        return _result("UNRESOLVED",[],["invalid_input"])
    if start < 0 or end <= start or end > len(raw_source) or not raw_source[start:end].strip():
        return _result("UNRESOLVED",[],["invalid_anchor"])
    lower=raw_source.lower(); detections=[]; seq=0

    ev=_evidential_prefix(lower,start)
    if ev: detections.append((ev[0],seq,"UNRESOLVED_EVIDENTIAL",f"evidential:{ev[1]}")); seq+=1
    pre=lower[:start]
    if re.search(r"(?:^|[.!?]\s+)whether\s*$",pre):
        detections.append((max(0,start-8),seq,"UNRESOLVED_EVIDENTIAL","whether")); seq+=1
    if "according to " in pre[max(0,start-120):]:
        p=pre.rfind("according to "); detections.append((p,seq,"UNRESOLVED_EVIDENTIAL","according_to")); seq+=1
    if "it is disputed whether " in pre[max(0,start-120):]:
        p=pre.rfind("it is disputed whether "); detections.append((p,seq,"UNRESOLVED_EVIDENTIAL","disputed_whether")); seq+=1

    stripped_offset=len(raw_source)-len(raw_source.lstrip()); stripped=lower.lstrip()
    if any(stripped.startswith(p) for p in CONDITIONAL_PREFIXES):
        comma=raw_source.find(",")
        if comma < 0: detections.append((stripped_offset,seq,"UNRESOLVED_EVIDENTIAL","conditional_boundary_unresolved")); seq+=1
        elif end <= comma+1: detections.append((stripped_offset,seq,"CONDITIONAL_ANTECEDENT","conditional_anchor_before_comma")); seq+=1
        elif start > comma: detections.append((stripped_offset,seq,"CONDITIONAL_CONSEQUENT","conditional_anchor_after_comma")); seq+=1

    for q0,q1 in _quote_ranges(raw_source):
        if start >= q0 and end <= q1:
            detections.append((q0,seq,"ATTRIBUTED","anchor_inside_quote")); seq+=1; break
    that_pos=lower.rfind(" that ",0,start+1)
    if that_pos >= 0:
        prefix=lower[:that_pos]; hits=[]
        for v in REPORTING_VERBS:
            hits.extend((m.start(),v) for m in re.finditer(rf"\b{re.escape(v)}\b",prefix))
        if hits:
            p,v=max(hits); detections.append((p,seq,"ATTRIBUTED",f"reporting_verb:{v}")); seq+=1

    # Pre-held-out qualification D01 showed that an epistemic/deontic cue can be
    # inside the anchored local-clause span. It is still enclosing semantic scope.
    # Therefore supported cues count when they begin before the anchor ends, not
    # only before the anchor starts.
    for path_type,patterns in (("DEONTIC",DEONTIC_PATTERNS),("EPISTEMIC",EPISTEMIC_PATTERNS)):
        for pat in patterns:
            for m in re.finditer(pat,lower):
                if m.start() < end:
                    detections.append((m.start(),seq,path_type,f"{path_type.lower()}:{pat}")); seq+=1
                    break

    for pat in QUANTIFIER_PATTERNS:
        m=re.search(pat,lower)
        if m and m.start() < end:
            detections.append((m.start(),seq,"QUANTIFIED",f"quantifier:{pat}")); seq+=1; break

    detections.sort(key=lambda x:(x[0],x[1])); path=[]; basis=[]; seen=set()
    for pos,_,typ,why in detections:
        key=(pos,typ)
        if key in seen: continue
        seen.add(key); path.append(typ); basis.append(why)
    polarity=str(observation.get("polarity","positive")).lower()
    if polarity not in {"positive","negative"}:
        return _result("UNRESOLVED",path,basis+[f"unsupported_polarity:{polarity}"])
    if path:
        legacy="UNRESOLVED" if path[0]=="UNRESOLVED_EVIDENTIAL" else path[0]
        return _result(legacy,path,basis)
    return _result("ASSERTED_NEGATIVE" if polarity=="negative" else "ASSERTED",[],basis)


def _result(scope_status: str, scope_path: list[str], basis: list[str]) -> dict:
    for item in scope_path: assert item in PATH_TYPES
    return {
        "scope_status":scope_status,
        "scope_path":scope_path,
        "authority_eligible":not scope_path and scope_status in {"ASSERTED","ASSERTED_NEGATIVE"},
        "basis":basis,
        "limitations":[],
    }
