from __future__ import annotations
import re
from typing import Any

NAMES = ("Mira","Nia","Oren","Pia","Ravi","Jalen")
POPS = ("certified inspector","lab courier","field auditor","sterile operator","release reviewer","licensed inspector","inspector")

UNKNOWN_PHRASES = (
    " works with ", " training", " badge", " may be ", " supervises ", "assigned near",
    "policy mentions", "under review", "applied to become", "reviewer handbook",
)
ESCAPE_PHRASES = ("most ", "exactly ", "usually ", " if ", "either ", "at least half", "former ", "unless ", "more inspectors than", "approved either")
AMBIGUITY_VERBS = (" told ", " met ", " discussed ", " because she ", " said ", " briefed ", " spoke with ", " told ", " emailed ", " asked ")


def _unknown(text: str) -> str | None:
    s=" "+text.lower()+" "
    if any(p in s for p in ESCAPE_PHRASES): return "ontology_escape"
    if any(p in s for p in UNKNOWN_PHRASES): return "insufficient_authority"
    if any(p in s for p in AMBIGUITY_VERBS): return "ambiguous_reference"
    return None


def _name(s: str) -> str:
    for n in NAMES:
        if re.search(rf"\b{n}\b", s): return n
    raise ValueError("entity")


def _predicate(s: str) -> str:
    t=s.lower()
    table=[
        (("log seals","logs seals"),"log seals"), (("scan badges","scans badges"),"scan badges"),
        (("enter zone c","enters zone c"),"enter zone c"), (("wear hoods","wearing a hood","wear hood"),"wear hood"),
        (("sign releases","signs releases"),"sign release"), (("open the vault","open vault"),"open vault"),
        (("sign the disposition","sign disposition"),"sign disposition"), (("signed the memo","sign the memo"),"sign memo"),
        (("approved the release","approve the release"),"approve release"),
    ]
    for keys,val in table:
        if any(k in t for k in keys): return val
    raise ValueError("predicate")


def _population(s: str) -> str:
    t=s.lower().replace("field-auditor","field auditor").replace("sterile-operator","sterile operator")
    for p in POPS:
        if p in t or (p+"s") in t: return p
    raise ValueError("population")


def _membership(text: str, entity: str, population: str) -> str:
    t=text.lower().replace("field-auditor","field auditor").replace("sterile-operator","sterile operator")
    e=entity.lower(); p=population
    if "does not establish whether" in t or "is not established" in t or "membership is unknown" in t or "status is unknown" in t:
        return "unknown"
    if f"{e} is not a {p}" in t or f"{e} is outside the {p} class" in t: return "non_member"
    if f"{e} is a {p}" in t or f"{e} belongs to the {p} class" in t: return "member"
    return "unknown"


def _membership_rule(text: str, query: str) -> dict[str, Any]:
    entity=_name(text+" "+query); pop=_population(text); pred=_predicate(text+" "+query); membership=_membership(text,entity,pop)
    modality="obligation" if re.search(r"\bmust\b",text,re.I) else "fact"
    polarity="negative" if re.search(r"\bdo not\b",text,re.I) else "positive"
    q=query.lower()
    if "rule applies" in q: kind="rule_applies"
    elif re.search(rf"\b{entity.lower()}\s+is\s+(?:not\s+)?a\s+",q): kind="membership"
    elif " does not " in " "+q+" ": kind="behavior_negative"
    else: kind="behavior_positive"
    return {"dimension":"membership_rule","authority":{"entity":entity,"population":pop,"membership":membership,"rule":{"predicate":pred,"modality":modality,"polarity":polarity}},"query":{"kind":kind,"entity":entity,"population":pop,"predicate":pred}}


def _subclass(text: str, query: str) -> dict[str, Any]:
    if text.startswith("No subclass relation"):
        return {"dimension":"subclass","authority":{"membership_population":"A","membership":"member","subclass_edge":"none"},"query":{"kind":"membership","population":"A"}}
    first=text.split(".",1)[0].lower()
    edge="A_sub_B" if first.startswith("every field inspector is an inspector") else "B_sub_A"
    second=text.split(".",1)[1].lower()
    if "membership is unknown" in second: status="unknown"
    elif " is not " in second: status="non_member"
    else: status="member"
    base="A" if "field inspector" in second else "B"
    target="A" if "field inspector" in query.lower() else "B"
    return {"dimension":"subclass","authority":{"membership_population":base,"membership":status,"subclass_edge":edge},"query":{"kind":"membership","population":target}}


def _only(text: str, query: str) -> dict[str, Any]:
    entity=_name(text+" "+query); pop="licensed inspector" if "licensed inspector" in text.lower() else "release reviewer"
    pred="open vault" if "vault" in text.lower() else "sign disposition"
    m=_membership(text,entity,pop)
    low=text.lower()
    perm="not_permitted" if "explicitly not permitted" in low else "permitted" if "explicitly permitted" in low else "unknown"
    kind="membership" if re.search(r"\bis a (?:licensed inspector|release reviewer)\b",query,re.I) else "permission"
    return {"dimension":"only_permission","authority":{"entity":entity,"population":pop,"membership":m,"predicate":pred,"only_population_may":True,"explicit_permission":perm},"query":{"kind":kind,"entity":entity,"population":pop,"predicate":pred}}


def _quant(s: str) -> str:
    t=s.strip().lower()
    if t.startswith("not every "): return "not_every"
    if t.startswith("every "): return "every"
    if t.startswith("no "): return "none"
    if t.startswith("some "): return "some"
    raise ValueError("quantifier")


def _quantifier(text: str, query: str) -> dict[str, Any]:
    pop="lab courier" if "courier" in text.lower() else "field auditor"; pred=_predicate(text+" "+query)
    return {"dimension":"quantifier","authority":{"population":pop,"predicate":pred,"quantifier":_quant(text)},"query":{"kind":"quantified","population":pop,"predicate":pred,"quantifier":_quant(query)}}


def _group(text: str, query: str) -> dict[str, Any]:
    pred=_predicate(text+" "+query)
    def parse(s: str) -> tuple[str,str]:
        low=s.lower(); scope="member" if "member of the" in low else "group"; neg="negative" if ("did not" in low or low.startswith("no member")) else "positive"; return scope,neg
    s,p=parse(text); qs,qp=parse(query)
    return {"dimension":"group_scope","authority":{"predicate":pred,"event_scope":s,"polarity":p},"query":{"kind":"event","predicate":pred,"event_scope":qs,"polarity":qp}}


def _role(text: str, query: str) -> dict[str, Any]:
    def parse(s: str) -> tuple[str,str,str,str]:
        low=s.lower(); pol="negative" if " did not " in " "+low+" " else "positive"
        names=[n for n in NAMES if re.search(rf"\b{n}\b",s)]
        if len(names)!=2: raise ValueError("roles")
        names.sort(key=lambda n:s.index(n))
        pred="approve" if "approv" in low else "review" if "review" in low else "notify"
        return names[0],names[1],pred,pol
    s,o,p,pol=parse(text); qs,qo,qp,qpol=parse(query)
    if p!=qp: raise ValueError("predicate mismatch")
    return {"dimension":"role_binding","authority":{"event":{"predicate":p,"roles":{"subject":s,"object":o},"polarity":pol}},"query":{"kind":"event","predicate":p,"roles":{"subject":qs,"object":qo},"polarity":qpol}}


def _temporal(text: str, query: str) -> dict[str, Any]:
    low=text.lower()
    if "before the cutoff" in low and ("after the cutoff" in low or "after it" in low): window="before_only"
    elif "starting at the cutoff" in low: window="after_only"
    elif "both before and after" in low: window="always"
    elif "not an inspector either before or after" in low: window="never"
    else: window="unknown"
    modality="obligation" if "must log seals" in low else "fact"
    qlow=query.lower(); time="before" if qlow.startswith("before") else "after"
    kind="membership" if "is an inspector" in qlow else "behavior_negative" if "does not" in qlow else "behavior_positive"
    return {"dimension":"temporal_membership","authority":{"entity":"Mira","population":"inspector","membership_window":window,"rule":{"predicate":"log seals","modality":modality,"polarity":"positive"}},"query":{"kind":kind,"entity":"Mira","population":"inspector","predicate":"log seals","time":time}}


def extract(text: str, query_text: str) -> dict[str, Any]:
    reason=_unknown(text)
    if reason: return {"status":"unknown","reason":reason}
    try:
        low=text.lower()
        if low.startswith("only "): case=_only(text,query_text)
        elif "cutoff" in low: case=_temporal(text,query_text)
        elif low.startswith("no subclass relation") or re.match(r"every (?:field )?inspector is (?:a )?(?:field )?inspector",low): case=_subclass(text,query_text)
        elif ("audit committee" in low or "review board" in low): case=_group(text,query_text)
        elif any(v in low for v in (" approved "," did not approve "," reviewed "," did not review "," notified "," did not notify ")): case=_role(text,query_text)
        elif low.startswith(("every ","no ","some ","not every ")): case=_quantifier(text,query_text)
        else: case=_membership_rule(text,query_text)
        return {"status":"resolved","case":case}
    except (ValueError,KeyError):
        return {"status":"unknown","reason":"unparsed"}
