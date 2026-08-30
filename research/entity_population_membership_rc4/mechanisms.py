"""Frozen RC4 candidate mechanisms for entity/population scope and membership.

Research-only. These functions accept only premise/hypothesis text. They never see
case IDs, family names, targets, rationales, or evaluator metadata.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, asdict
from typing import Literal

Relation = Literal["entailment","neutral","contradiction","unresolved"]

def norm(s:str)->str:
    s=s.lower().replace("‑","-").replace("–","-").replace("—","-")
    s=re.sub(r"\s+"," ",s)
    return s.strip(" .")

def singular(s:str)->str:
    s=norm(s)
    if s.endswith("ies"): return s[:-3]+"y"
    if s.endswith("ers"): return s[:-1]
    if s.endswith("s") and not s.endswith("ss"): return s[:-1]
    return s

@dataclass(frozen=True)
class State:
    memberships: tuple[tuple[str,str,str],...]=()
    subclass: tuple[tuple[str,str],...]=()
    universal_rules: tuple[tuple[str,str,str],...]=()
    only_permissions: tuple[tuple[str,str],...]=()
    quantified_facts: tuple[tuple[str,str,str],...]=()
    group_events: tuple[tuple[str,str],...]=()
    roles: tuple[tuple[str,str,str],...]=()
    temporal_memberships: tuple[tuple[str,str,str,str],...]=()
    explicit_events: tuple[str,...]=()
    recognized: tuple[str,...]=()
    def to_dict(self): return asdict(self)


def parse(premise:str)->State:
    memberships=[]; subclass=[]; rules=[]; only=[]; qfacts=[]; groups=[]; roles=[]; temporal=[]; events=[]; why=[]
    sents=[x.strip() for x in re.split(r"(?<=[.!?])\s+",premise.strip()) if x.strip()]
    for sent in sents:
        low=norm(sent)
        m=re.match(r"(.+?) is not (?:an? )?(.+?) before (.+)$",low)
        if m:
            temporal.append((m.group(1),m.group(2),m.group(3),"enter")); why.append("temporal_enter_negative"); continue
        m=re.match(r"from (.+?) onward, (.+?) is (?:an? )?(.+)$",low)
        if m:
            temporal.append((m.group(2),m.group(3),m.group(1),"enter")); why.append("temporal_enter_positive"); continue
        m=re.match(r"(.+?) is (?:an? )?(.+?) through (.+)$",low)
        if m:
            temporal.append((m.group(1),m.group(2),m.group(3),"leave")); why.append("temporal_leave_positive"); continue
        m=re.match(r"(?:from|after) (.+?) onward, (.+?) is not (?:an? )?(.+)$",low)
        if m:
            temporal.append((m.group(2),m.group(3),m.group(1),"leave")); why.append("temporal_leave_negative"); continue
        m=re.match(r"([a-z][a-z-]*) is not (?:an? )?(.+)$",low)
        if m and not any(tok in low for tok in ("governed by","outside","required","allowed")):
            memberships.append((m.group(1),singular(m.group(2)),"nonmember")); why.append("nonmembership"); continue
        m=re.match(r"([a-z][a-z-]*) is (?:an? )?(.+)$",low)
        if m and len(m.group(2).split())<=4 and not any(tok in low for tok in ("approver of","reviewer of","recipient of","assignee of","sender of")):
            memberships.append((m.group(1),singular(m.group(2)),"member")); why.append("membership"); continue
        m=re.match(r"(?:all|every|each) (.+?) (?:are|is) (.+)$",low)
        if m and not any(x in low for x in ("must ","may ","sign ","use ","carry ","does not")):
            subclass.append((singular(m.group(1)),singular(m.group(2)))); why.append("subclass"); continue
        m=re.match(r"(?:all|every|each) (.+?) must (.+)$",low)
        if m:
            rules.append((singular(m.group(1)),"obligation",m.group(2))); why.append("universal_obligation"); continue
        m=re.match(r"(.+?) must be (.+?) by every (.+)$",low)
        if m:
            rules.append((singular(m.group(3)),"obligation",f"{m.group(2)} {m.group(1)}")); why.append("passive_universal"); continue
        m=re.match(r"only (.+?) may (.+)$",low)
        if m:
            only.append((singular(m.group(1)),m.group(2))); why.append("only_permission"); continue
        for prefix,q in (("some ","some"),("no ","none"),("not every ","not_every"),("every ","every"),("all ","every")):
            if low.startswith(prefix):
                rest=low[len(prefix):]
                vm=re.match(r"(.+?) (carry|carries|use|uses|sign|signs|does not use|do not use) (.+)$",rest)
                if vm:
                    qfacts.append((q,singular(vm.group(1)),f"{vm.group(2)} {vm.group(3)}")); why.append("quantified_fact")
                    break
        else:
            gm=re.match(r"the (.+? (?:team|committee|panel|unit)) (submitted|approved|selected|issued) (.+)$",low)
            if gm:
                groups.append((gm.group(1),f"{gm.group(2)} {gm.group(3)}")); why.append("group_event"); continue
            rm=re.match(r"([a-z][a-z-]*) approved ([a-z][a-z-]*)'s request",low)
            if rm:
                roles += [("approve","approver",rm.group(1)),("approve","request_owner",rm.group(2))]; events.append(low); why.append("approve_roles"); continue
            rm=re.match(r"([a-z][a-z-]*) assigned the deviation ticket to ([a-z][a-z-]*)",low)
            if rm:
                roles += [("assign","assigner",rm.group(1)),("assign","assignee",rm.group(2))]; events.append(low); why.append("assign_roles"); continue
            rm=re.match(r"([a-z][a-z-]*) reviewed ([a-z][a-z-]*)'s batch record",low)
            if rm:
                roles += [("review","reviewer",rm.group(1)),("review","record_owner",rm.group(2))]; events.append(low); why.append("review_roles"); continue
            rm=re.match(r"([a-z][a-z-]*) sent the calibration file to ([a-z][a-z-]*)",low)
            if rm:
                roles += [("send","sender",rm.group(1)),("send","recipient",rm.group(2))]; events.append(low); why.append("send_roles"); continue
            events.append(low)
    def uniq(xs): return tuple(dict.fromkeys(xs))
    return State(uniq(memberships),uniq(subclass),uniq(rules),uniq(only),uniq(qfacts),uniq(groups),uniq(roles),uniq(temporal),uniq(events),uniq(why))


def closure_membership(state:State):
    mem={(e,c):v for e,c,v in state.memberships}
    changed=True
    while changed:
        changed=False
        for sub,sup in state.subclass:
            for (e,c),v in list(mem.items()):
                if c==sub and v=="member" and (e,sup) not in mem:
                    mem[(e,sup)]="member"; changed=True
    return mem

def action_match(action:str,h:str)->bool:
    def toks(x):
        out=set()
        for t in re.findall(r"[a-z0-9]+",norm(x)):
            if t in {"the","a","an","to","before","in","must","may","not","every","all","some","no","at","least","one"}: continue
            if t.endswith("ies"): t=t[:-3]+"y"
            elif t.endswith("s") and len(t)>3: t=t[:-1]
            out.add(t)
        return out
    a=toks(action); b=toks(h)
    return bool(a) and len(a & b)/len(a) >= .65

def subject(h:str)->str:
    m=re.match(r"(?:on [^,]+, )?([a-z][a-z-]*)\b",norm(h)); return m.group(1) if m else ""

def typed_relation(premise:str,hypothesis:str)->tuple[Relation,str,dict]:
    st=parse(premise); h=norm(hypothesis); p=norm(premise); mem=closure_membership(st); subj=subject(h)
    if h in p: return "entailment","explicit text",st.to_dict()
    rolemap={(pred,role):ent for pred,role,ent in st.roles}
    if "approver of" in h and "request" in h and rolemap.get(("approve","approver"))==subj: return "entailment","preserved approver role",st.to_dict()
    if "assignee of the deviation ticket" in h and rolemap.get(("assign","assignee"))==subj: return "entailment","preserved assignee role",st.to_dict()
    if "reviewer of" in h and rolemap.get(("review","reviewer"))==subj: return "entailment","preserved reviewer role",st.to_dict()
    if "recipient of the calibration file" in h and rolemap.get(("send","recipient"))==subj: return "entailment","preserved recipient role",st.to_dict()
    if st.roles:
        if any(tok in h for tok in (" approved "," assigned "," reviewed "," sent ")):
            if " did not " in f" {h} ": return "contradiction","negates explicit role-bound event",st.to_dict()
            return "neutral","role-swapped event not licensed",st.to_dict()
    for grp,ev in st.group_events:
        if action_match(ev,h):
            if f"{grp} did not" in h: return "contradiction","negates explicit group event",st.to_dict()
            if f"by the {grp}" in h or h.startswith("the "+grp): return "entailment","group event paraphrase",st.to_dict()
            member_of_group = any(e==subj and v=="member" and set(grp.replace("-"," ").split()).issubset(set(c.replace("-"," ").split())) for (e,c),v in mem.items()) if subj else False
            if member_of_group: return "neutral","group event does not identify member actor",st.to_dict()
    for cls,act in st.only_permissions:
        if action_match(act,h) and subj:
            status=mem.get((subj,cls),"unknown")
            if "may not" in h:
                if status=="nonmember": return "entailment","known nonmember excluded by only-condition",st.to_dict()
                return "neutral","only-condition does not deny member permission",st.to_dict()
            if re.search(r"\bmay\b",h):
                if status=="nonmember": return "contradiction","permission violates necessary class condition",st.to_dict()
                if status=="member": return "neutral","necessary class condition is not sufficient permission",st.to_dict()
    if subj and st.temporal_memberships:
        def time_value(text):
            m=re.search(r"day (\d+)",text)
            if m: return ("day",int(m.group(1)))
            months={"may":5,"june":6,"august":8,"september":9}
            m=re.search(r"(may|june|august|september) (\d+)",text)
            if m: return ("date",months[m.group(1)]*100+int(m.group(2)))
            return None
        hv=time_value(h)
        for ent,cls,bound,direction in st.temporal_memberships:
            if ent!=subj: continue
            bv=time_value(bound)
            if not hv or not bv or hv[0]!=bv[0]: continue
            inside = hv[1]>=bv[1] if direction=="enter" else hv[1]<=bv[1]
            for rcls,mod,act in st.universal_rules:
                if rcls==singular(cls) and action_match(act,h):
                    if inside and ("must" in h or "governed by" in h or "rule applies" in h): return "entailment","inside temporal membership window",st.to_dict()
                    if not inside and ("governed by" in h or "rule applies" in h or "remains governed" in h): return "contradiction","outside temporal membership window",st.to_dict()
                    if not inside: return "neutral","outside membership does not determine actual behavior",st.to_dict()
    if subj:
        for cls,mod,act in st.universal_rules:
            if action_match(act,h):
                status=mem.get((subj,cls),"unknown")
                if "must" in h:
                    if status=="member": return "entailment","known member inherits universal obligation",st.to_dict()
                    return "neutral","class rule alone does not establish named applicability",st.to_dict()
                if any(x in h for x in ("outside the population","outside the class","not governed by","does not apply")) and status=="member": return "contradiction","known member conflicts with claimed exclusion",st.to_dict()
                if any(x in h for x in ("filed ","wore ","enjoys ","countersigned ","uses ","records ")): return "neutral","obligation does not entail observed behavior",st.to_dict()
    for sub,sup in st.subclass:
        if h.startswith("all ") or h.startswith("every "):
            if singular(sub) in h and singular(sup) in h:
                pos_sub=h.find(singular(sub)); pos_sup=h.find(singular(sup))
                if pos_sup < pos_sub: return "neutral","subclass relation is directional",st.to_dict()
    for q,pop,pred in st.quantified_facts:
        if not action_match(pred,h): continue
        if q=="some":
            if h.startswith("at least one"): return "entailment","some entails at least one",st.to_dict()
            if h.startswith("every"): return "neutral","existential does not entail universal",st.to_dict()
            if h.startswith("no "): return "contradiction","some conflicts with none",st.to_dict()
        if q=="none":
            if h.startswith("every") and ("does not" in h or "do not" in h): return "entailment","none paraphrased as universal negation",st.to_dict()
            if h.startswith("at least one") and "use" in h: return "contradiction","none conflicts with existence",st.to_dict()
            return "neutral","unrelated population assertion",st.to_dict()
        if q=="not_every":
            if h.startswith("at least one") and "does not" in h: return "entailment","not every entails at least one counterexample",st.to_dict()
            if h.startswith("every"): return "contradiction","not every contradicts every",st.to_dict()
            return "neutral","not every does not license majority",st.to_dict()
        if q=="every":
            if h.startswith("all "): return "entailment","every/all paraphrase",st.to_dict()
            if h.startswith("some ") and "does not" in h: return "contradiction","universal conflicts with counterexample",st.to_dict()
            return "neutral","individual identity not established",st.to_dict()
    return "unresolved","typed authority not sufficient",st.to_dict()


def decompose_for_nli(premise:str)->str:
    st=parse(premise); add=[]
    for e,c,v in st.memberships:
        add.append(f"Membership statement: {e} is {'a member of' if v=='member' else 'not a member of'} class {c}.")
    for sub,sup in st.subclass:
        add.append(f"Subclass statement: every {sub} is a {sup}; the reverse implication is not stated.")
    for cls,act in st.only_permissions:
        add.append(f"Necessary-condition statement: permission to {act} requires membership in class {cls}; membership alone does not state permission.")
    for q,pop,pred in st.quantified_facts:
        add.append(f"Population statement: quantifier={q}; population={pop}; predicate={pred}.")
    for grp,ev in st.group_events:
        add.append(f"Group-scope statement: group {grp} {ev}; no particular member actor is identified unless separately stated.")
    if not add: return premise
    return premise.rstrip()+" "+" ".join(add)
