"""Independent RC7D-D role reader for events under quantitative scope.

Authored before the held-out cohort. It deliberately separates a quantitative
scope marker from the base event participant rather than treating the whole
quantified noun phrase as a new entity.
"""
from __future__ import annotations
import re
from research.semantic_operator_jurisdiction_rc7d import candidate as base

VERBS={"reviewed":"review","inspected":"inspect","approved":"approve","signed":"sign","released":"release"}
Q=r"(?:exactly|at\s+least|fewer\s+than)\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)|(?:\d{1,3}\s*%|[a-z]+\s+percent|a\s+(?:small\s+)?minority\s+of|a\s+majority\s+of|roughly\s+(?:half|three\s+quarters)(?:\s+of)?|two\s+thirds\s+of)"
PAT=re.compile(rf"\b(?P<q>{Q})\s+(?:the\s+)?(?P<s>[a-z][a-z -]{{1,28}}?)\s+(?P<v>reviewed|inspected|approved|signed|released)\s+(?P<o>[a-z][a-z0-9 -]{{1,50}}?)(?=[.;]|$)",re.I)

def norm(s:str)->str:
    return re.sub(r"\s+"," ",s.strip(" .,:;\t\n").lower())

def read(text:str)->dict:
    m=PAT.search(text)
    if not m:
        return base._base(text,"role-binding-alt-base-pop","role_binding","NOT_APPLICABLE")
    atom={"kind":"event","predicate":VERBS[m.group("v").lower()],"subject":norm(m.group("s")),"object":norm(m.group("o")),"polarity":"positive"}
    out=base._claim(text,"role-binding-alt-base-pop","role_binding",[m.span()],[atom],["event_under_quantitative_scope"])
    out["reader_version"]="rc7d-d-role-base-pop-v1"
    return out
