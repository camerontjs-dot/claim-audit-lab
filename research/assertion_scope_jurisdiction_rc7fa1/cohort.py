"""RC7F-A1 frozen semantics-first held-out cohort.

Formal wrapper type establishes gold before the candidate is executed. Surface
names/events are deterministic renderings. Candidate output never establishes gold.
"""
from __future__ import annotations

COHORT_FREEZE_EXPECTED="rc7fa1-heldout-v1-semantics-first-20260831"
CASES=[]
NAMES=["Talia","Ravi","Mona","Ivo","Keira","Basil","Yara","Noel","Sumi","Galen","Vera","Oren"]
OBJECTS=["packet u","ledger c","batch w","form j","sample v","permit q","record m","dossier t"]
VERBS=["reviewed","signed","inspected","released","approved","archived"]

def ev(i:int,negative:bool=False)->str:
    s=NAMES[i%len(NAMES)]; v=VERBS[i%len(VERBS)]; o=OBJECTS[i%len(OBJECTS)]
    if negative:
        base={"reviewed":"review","signed":"sign","inspected":"inspect","released":"release","approved":"approve","archived":"archive"}[v]
        return f"{s} did not {base} {o}."
    return f"{s} {v} {o}."

def add(cid,family,text,clause,path,eligible,polarity="positive",tags=(),pair_id=None,pair_relation=None):
    start=text.index(clause)
    CASES.append({"case_id":cid,"family":family,"raw_source":text,
      "observation":{"predicate":"event","subject":"entity","object":"object","polarity":polarity,"start":start,"end":start+len(clause)},
      "gold_scope_path":list(path),"gold_authority_eligible":bool(eligible),"tags":list(tags),
      "pair_id":pair_id,"pair_relation":pair_relation})

# Direct assertions. First four pair with comma evidentials below.
for i in range(8):
    t=ev(i); add(f"DP{i:02d}","direct_positive",t,t,[],True,pair_id=f"direct-evid-{i}" if i<4 else None,pair_relation="meaning_changing" if i<4 else None)
for i in range(8):
    t=ev(i+8,True); add(f"DN{i:02d}","direct_negative",t,t,[],True,"negative")

# Evidential adverbs. Parenthetical framing is deliberately in the preregistered held-out family.
words=["Supposedly","Purportedly","Reportedly","Allegedly"]
forms=[("comma",lambda w,c:f"{w}, {c}"),("colon",lambda w,c:f"{w}: {c}"),("dash",lambda w,c:f"{w} — {c}"),("parenthetical",lambda w,c:f"({w}) {c}")]
k=0
for wi,w in enumerate(words):
    for fi,(label,render) in enumerate(forms):
        clause=ev(k+20); text=render(w,clause)
        pair=f"direct-evid-{wi}" if label=="comma" else None
        add(f"EV{k:02d}",f"evidential_{label}",text,clause,["UNRESOLVED_EVIDENTIAL"],False,tags=("punctuation_transform",),pair_id=pair,pair_relation="meaning_changing" if pair else None)
        k+=1

# Lexical/domain traps must not scope an unrelated following observation.
traps=["The supposedly field is blue.","The purportedlyNamed column is archived.","The reportedly flag is disabled.","The allegedly-tagged folder is empty."]
for i,prefix in enumerate(traps):
    clause=ev(i+40); add(f"TR{i:02d}","evidential_domain_trap",prefix+" "+clause,clause,[],True)

# Attribution: quoted and reporting complement.
for i in range(4):
    clause=ev(i+44); speaker=NAMES[(i+3)%len(NAMES)]
    add(f"AQ{i:02d}","attribution_quote",f'{speaker} said, "{clause}"',clause,["ATTRIBUTED"],False)
for i in range(4):
    clause=ev(i+48); speaker=NAMES[(i+4)%len(NAMES)]
    add(f"AR{i:02d}","attribution_report",f"{speaker} claimed that {clause}",clause,["ATTRIBUTED"],False)

# Conditional antecedent/consequent.
for i in range(4):
    clause=ev(i+52).rstrip("."); other=ev(i+60)
    text=f"If {clause}, {other}"; add(f"CA{i:02d}","conditional_antecedent",text,clause,["CONDITIONAL_ANTECEDENT"],False)
for i in range(4):
    other=ev(i+56).rstrip("."); clause=ev(i+64)
    text=f"If {other}, {clause}"; add(f"CC{i:02d}","conditional_consequent",text,clause,["CONDITIONAL_CONSEQUENT"],False)

# Epistemic, deontic, quantified single scopes.
for i in range(8):
    base=ev(i+68); s=base[:-1]; parts=s.split(" ",1); clause=f"{parts[0]} probably {parts[1]}."
    add(f"EP{i:02d}","epistemic",clause,clause,["EPISTEMIC"],False)
for i in range(8):
    obj=OBJECTS[(i+2)%len(OBJECTS)]; text=f"Only reviewers may inspect {obj}."; clause=f"reviewers may inspect {obj}."
    add(f"DE{i:02d}","deontic",text,clause,["DEONTIC"],False)
for i in range(8):
    obj=OBJECTS[(i+3)%len(OBJECTS)]; text=f"Every reviewer inspected {obj}."; clause=f"reviewer inspected {obj}."
    add(f"QU{i:02d}","quantified",text,clause,["QUANTIFIED"],False)

# Nested formal wrappers.
for i in range(4):
    clause=ev(i+80).rstrip("."); speaker=NAMES[(i+5)%len(NAMES)]; other=ev(i+90)
    text=f"If {speaker} reported that {clause}, {other}"
    add(f"NA{i:02d}","nested_conditional_attribution",text,clause,["CONDITIONAL_ANTECEDENT","ATTRIBUTED"],False,tags=("nested_scope",))
for i in range(4):
    base=ev(i+84); parts=base[:-1].split(" ",1); clause=f"{parts[0]} probably {parts[1]}."; speaker=NAMES[(i+7)%len(NAMES)]
    text=f"{speaker} reported that {clause}"
    add(f"NE{i:02d}","nested_attribution_epistemic",text,clause,["ATTRIBUTED","EPISTEMIC"],False,tags=("nested_scope",))
for i in range(4):
    base=ev(i+88).rstrip("."); parts=base.split(" ",1); clause=f"{parts[0]} probably {parts[1]}"; speaker=NAMES[(i+8)%len(NAMES)]; other=ev(i+96)
    text=f"If {speaker} reported that {clause}, {other}"
    add(f"NT{i:02d}","nested_three_layer",text,clause,["CONDITIONAL_ANTECEDENT","ATTRIBUTED","EPISTEMIC"],False,tags=("nested_scope",))

# Explicit unresolved frames.
for i in range(4):
    clause=ev(i+100).rstrip("."); text=f"Whether {clause} remains disputed."
    add(f"UN{i:02d}","unresolved_whether",text,clause,["UNRESOLVED_EVIDENTIAL"],False)

assert len(CASES)==92, len(CASES)
