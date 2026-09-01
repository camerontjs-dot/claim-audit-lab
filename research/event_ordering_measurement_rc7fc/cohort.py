"""RC7F-C semantics-first explicit event-ordering cohort."""
from __future__ import annotations
COHORT_FREEZE_EXPECTED="rc7fc-heldout-v1-semantics-first-20260831"
CASES=[]
NAMES=["Talia","Ravi","Mona","Ivo","Keira","Basil","Yara","Noel","Sumi","Galen","Vera","Oren"]
OBJECTS=["packet u","ledger c","batch w","form j","sample v","permit q","record m","dossier t"]
VERBS=[("reviewed","review"),("signed","sign"),("inspected","inspect"),("released","release"),("approved","approve"),("archived","archive"),("processed","process"),("verified","verify"),("recorded","record")]

def event(i,negative=False):
    s=NAMES[i%len(NAMES)]; past,base=VERBS[i%len(VERBS)]; o=OBJECTS[i%len(OBJECTS)]
    text=f"{s} did not {base} {o}" if negative else f"{s} {past} {o}"
    gold={"subject":s.lower(),"predicate":base,"object":o.lower(),"polarity":"negative" if negative else "positive"}
    return text,gold

def add(cid,family,text,gold,*,pair_id=None,pair_relation=None,tags=()):
    CASES.append({"case_id":cid,"family":family,"raw_source":text,"gold":gold,"pair_id":pair_id,"pair_relation":pair_relation,"tags":list(tags)})

def ordering(left,relation,right): return {"left_event":left,"relation":relation,"right_event":right}

# Direction-changing pairs.
for i in range(10):
    lt,lg=event(i); rt,rg=event(i+17); pid=f"dir-{i}"
    add(f"BF{i:02d}","before",f"{lt} before {rt}.",ordering(lg,"BEFORE",rg),pair_id=pid,pair_relation="meaning_changing")
    add(f"AF{i:02d}","after",f"{lt} after {rt}.",ordering(lg,"AFTER",rg),pair_id=pid,pair_relation="meaning_changing")

# Polarity cases.
for i in range(6):
    lt,lg=event(i+25,True); rt,rg=event(i+31)
    add(f"NL{i:02d}","negative_left",f"{lt} before {rt}.",ordering(lg,"BEFORE",rg))
for i in range(6):
    lt,lg=event(i+37); rt,rg=event(i+43,True)
    add(f"NR{i:02d}","negative_right",f"{lt} after {rt}.",ordering(lg,"AFTER",rg))

# Irrelevant sentence prefix around otherwise supported ordering.
for i in range(6):
    lt,lg=event(i+49); rt,rg=event(i+55)
    prefix=["The dashboard is blue.","The archive is complete.","A note appears above."][i%3]
    add(f"IR{i:02d}","irrelevant_prefix",f"{prefix} {lt} before {rt}.",ordering(lg,"BEFORE",rg),tags=("irrelevant_prose",))

# Further positive controls with varied bounded predicates.
for i in range(6):
    lt,lg=event(i+61); rt,rg=event(i+70)
    rel="BEFORE" if i%2==0 else "AFTER"; cue=rel.lower()
    add(f"VX{i:02d}","varied_event",f"{lt} {cue} {rt}.",ordering(lg,rel,rg))

# Negative / unsupported temporal language: outside the explicit before/after two-event jurisdiction.
NEG=[
 "The before column is blue.",
 "The after label is archived.",
 "Review before submission.",
 "Before 2025, the registry was empty.",
 "After lunch, the office reopened.",
 "Talia reviewed packet u. Ravi signed ledger c.",
 "Talia reviewed packet u earlier than expected.",
 "Ravi signed ledger c later that day.",
 "Mona inspected batch w and then Ivo released form j.",
 "Keira approved sample v subsequently.",
 "The process before/after flag is false.",
 "The word before appears twice before this clause.",
 "Basil reviewed record m during the afternoon.",
 "Yara archived dossier t while Noel signed form j.",
 "Sumi reviewed packet u prior to approval.",
 "Galen signed form j following inspection.",
]
for i,text in enumerate(NEG): add(f"N{i:02d}","negative_or_unsupported",text,None)

assert len(CASES)==60, len(CASES)
