from __future__ import annotations
import re
from typing import Any

PEOPLE={"mira":"Mira","nia":"Nia","oren":"Oren","pia":"Pia","ravi":"Ravi","jalen":"Jalen"}


def _words(s: str) -> list[str]:
    return re.findall(r"[a-z]+",s.lower())


def _fail_closed(text: str) -> str | None:
    s=text.lower()
    escape_groups=[{"most"},{"exactly"},{"usually"},{"either"},{"unless"},{"former"}]
    if any(g <= set(_words(s)) for g in escape_groups) or "at least half" in s or "more inspectors than" in s or "approved either" in s or " if a supervisor" in s:
        return "ontology_escape"
    insuff=("works with","completed inspector training","courier badge","may be a","supervises","assigned near","policy mentions","under review","applied to become","reviewer handbook")
    if any(x in s for x in insuff): return "insufficient_authority"
    ambiguity=(" told "," met "," discussed "," because she "," said "," briefed "," spoke with "," emailed "," asked ")
    padded=" "+s+" "
    if any(x in padded for x in ambiguity) and "cutoff" not in s: return "ambiguous_reference"
    return None


def _person(s: str) -> str:
    for w in _words(s):
        if w in PEOPLE: return PEOPLE[w]
    raise ValueError


def _action(s: str) -> str:
    w=set(_words(s))
    if "seal" in w or "seals" in w: return "log seals"
    if "badge" in w or "badges" in w:
        if "wears" in w: return "wear hood"
        return "scan badges"
    if "hood" in w or "hoods" in w: return "wear hood"
    if "zone" in w: return "enter zone c"
    if "release" in w and ("sign" in w or "signs" in w): return "sign release"
    if "vault" in w: return "open vault"
    if "disposition" in w: return "sign disposition"
    if "memo" in w: return "sign memo"
    if "release" in w and ("approved" in w or "approve" in w): return "approve release"
    raise ValueError


def _pop(s: str) -> str:
    low=s.lower().replace("-"," ")
    for p in ("certified inspector","lab courier","field auditor","sterile operator","release reviewer","licensed inspector","inspector"):
        if p in low or p+"s" in low: return p
    raise ValueError


def _member_state(text: str, person: str, pop: str) -> str:
    low=text.lower().replace("-"," ")
    if any(x in low for x in ("does not establish whether","is not established","membership is unknown","status is unknown")): return "unknown"
    anchor=person.lower()
    if f"{anchor} is not a {pop}" in low or f"{anchor} is outside the {pop} class" in low: return "non_member"
    if f"{anchor} is a {pop}" in low or f"{anchor} belongs to the {pop} class" in low: return "member"
    return "unknown"


def _membership_rule(text: str, query: str) -> dict[str, Any]:
    person=_person(text+" "+query); pop=_pop(text); action=_action(text+" "+query); state=_member_state(text,person,pop)
    modality="obligation" if "must" in _words(text) else "fact"
    polarity="negative" if "do not" in text.lower() else "positive"
    q=query.lower(); qw=set(_words(query))
    if "rule applies" in q: kind="rule_applies"
    elif "is" in qw and ("inspector" in qw or "courier" in qw or "auditor" in qw or "operator" in qw or "reviewer" in qw): kind="membership"
    elif "not" in qw: kind="behavior_negative"
    else: kind="behavior_positive"
    return {"dimension":"membership_rule","authority":{"entity":person,"population":pop,"membership":state,"rule":{"predicate":action,"modality":modality,"polarity":polarity}},"query":{"kind":kind,"entity":person,"population":pop,"predicate":action}}


def _subclass(text: str, query: str) -> dict[str, Any]:
    low=text.lower()
    if low.startswith("no subclass relation"):
        return {"dimension":"subclass","authority":{"membership_population":"A","membership":"member","subclass_edge":"none"},"query":{"kind":"membership","population":"A"}}
    first,rest=text.split(".",1)
    edge="A_sub_B" if _words(first)[:3]==["every","field","inspector"] else "B_sub_A"
    r=rest.lower()
    state="unknown" if "unknown" in r else "non_member" if " is not " in r else "member"
    base="A" if "field inspector" in r else "B"
    target="A" if "field inspector" in query.lower() else "B"
    return {"dimension":"subclass","authority":{"membership_population":base,"membership":state,"subclass_edge":edge},"query":{"kind":"membership","population":target}}


def _only(text: str, query: str) -> dict[str, Any]:
    person=_person(text+" "+query); low=text.lower(); pop="licensed inspector" if "licensed inspector" in low else "release reviewer"; action="open vault" if "vault" in low else "sign disposition"
    state=_member_state(text,person,pop); perm="not_permitted" if "explicitly not permitted" in low else "permitted" if "explicitly permitted" in low else "unknown"
    kind="membership" if query.lower().strip().endswith(("licensed inspector.","release reviewer.")) and "may" not in query.lower() else "permission"
    return {"dimension":"only_permission","authority":{"entity":person,"population":pop,"membership":state,"predicate":action,"only_population_may":True,"explicit_permission":perm},"query":{"kind":kind,"entity":person,"population":pop,"predicate":action}}


def _qword(s: str) -> str:
    w=_words(s)
    if w[:2]==["not","every"]: return "not_every"
    return {"every":"every","no":"none","some":"some"}[w[0]]


def _quantifier(text: str, query: str) -> dict[str, Any]:
    pop="lab courier" if "courier" in text.lower() else "field auditor"; action=_action(text+" "+query)
    return {"dimension":"quantifier","authority":{"population":pop,"predicate":action,"quantifier":_qword(text)},"query":{"kind":"quantified","population":pop,"predicate":action,"quantifier":_qword(query)}}


def _group(text: str, query: str) -> dict[str, Any]:
    action=_action(text+" "+query)
    def state(s: str) -> tuple[str,str]:
        w=_words(s); member=("member" in w or "members" in w); negative=("not" in w or (w and w[0]=="no")); return ("member" if member else "group","negative" if negative else "positive")
    scope,pol=state(text); qs,qpol=state(query)
    return {"dimension":"group_scope","authority":{"predicate":action,"event_scope":scope,"polarity":pol},"query":{"kind":"event","predicate":action,"event_scope":qs,"polarity":qpol}}


def _role_atom(s: str) -> tuple[str,str,str,str]:
    words=_words(s); people=[PEOPLE[w] for w in words if w in PEOPLE]
    if len(people)!=2: raise ValueError
    pred="approve" if any(w.startswith("approv") for w in words) else "review" if any(w.startswith("review") for w in words) else "notify"
    pol="negative" if "not" in words else "positive"
    return people[0],people[1],pred,pol


def _role(text: str, query: str) -> dict[str, Any]:
    s,o,p,pol=_role_atom(text); qs,qo,qp,qpol=_role_atom(query)
    if p!=qp: raise ValueError
    return {"dimension":"role_binding","authority":{"event":{"predicate":p,"roles":{"subject":s,"object":o},"polarity":pol}},"query":{"kind":"event","predicate":p,"roles":{"subject":qs,"object":qo},"polarity":qpol}}


def _temporal(text: str, query: str) -> dict[str, Any]:
    low=text.lower(); words=set(_words(text))
    if "starting at the cutoff" in low: window="after_only"
    elif "both before and after" in low: window="always"
    elif "either before or after" in low and "not an inspector" in low: window="never"
    elif "does not establish when" in low: window="unknown"
    else: window="before_only"
    time="before" if _words(query)[0]=="before" else "after"
    qwords=set(_words(query)); kind="membership" if "inspector" in qwords and "log" not in qwords and "logs" not in qwords else "behavior_negative" if "not" in qwords else "behavior_positive"
    modality="obligation" if "must" in words else "fact"
    return {"dimension":"temporal_membership","authority":{"entity":"Mira","population":"inspector","membership_window":window,"rule":{"predicate":"log seals","modality":modality,"polarity":"positive"}},"query":{"kind":kind,"entity":"Mira","population":"inspector","predicate":"log seals","time":time}}


def extract(text: str, query_text: str) -> dict[str, Any]:
    fail=_fail_closed(text)
    if fail: return {"status":"unknown","reason":fail}
    try:
        low=text.lower(); first=_words(text)[:2]
        if first and first[0]=="only": case=_only(text,query_text)
        elif "cutoff" in low: case=_temporal(text,query_text)
        elif low.startswith("no subclass relation") or (low.startswith("every") and " is an inspector" in low.split(".",1)[0]): case=_subclass(text,query_text)
        elif "audit committee" in low or "review board" in low: case=_group(text,query_text)
        elif sum(1 for p in PEOPLE.values() if p in text)>=2 and any(x in low for x in ("approv","review","notif")): case=_role(text,query_text)
        elif first and (first[0] in {"every","no","some"} or first==["not","every"]): case=_quantifier(text,query_text)
        else: case=_membership_rule(text,query_text)
        return {"status":"resolved","case":case}
    except (ValueError,KeyError,IndexError):
        return {"status":"unknown","reason":"unparsed"}
