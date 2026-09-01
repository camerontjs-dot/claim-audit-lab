"""RC7F-B1 semantics-first held-out comparison cohort."""
from __future__ import annotations
COHORT_FREEZE_EXPECTED="rc7fb1-heldout-v1-semantics-first-20260831"
CASES=[]
ENTITIES=["Sector A","Sector B","Depot C","Depot D","Team E","Team F","Group G","Group H","Unit J","Unit K","Site L","Site M"]
MEASURES=["output","count","volume","score","yield","rate","share","percentage","proportion"]

def atom(l,r,rr): return {"left":l.lower(),"relation":r,"right":rr.lower()}
def add(cid,family,text,gold,*,pair_id=None,pair_relation=None,tags=()):
    CASES.append({"case_id":cid,"family":family,"raw_source":text,"gold":gold,"pair_id":pair_id,"pair_relation":pair_relation,"tags":list(tags)})

def ents(i): return ENTITIES[(2*i)%len(ENTITIES)],ENTITIES[(2*i+1)%len(ENTITIES)]

# Parent-supported numeric delta. Direction pairs share the same entity pair.
for i in range(6):
    l,r=ents(i); n=20+i; d=3+i
    pid=f"delta-dir-{i}"
    add(f"DM{i:02d}","delta_more",f"{l} processed {n} units, {d} more than {r}.",atom(l,"MORE_THAN",r),pair_id=pid,pair_relation="meaning_changing")
    add(f"DF{i:02d}","delta_fewer",f"{l} processed {n} units, {d} fewer than {r}.",atom(l,"FEWER_THAN",r),pair_id=pid,pair_relation="meaning_changing")

# New measure-head adjective family. Higher/greater are meaning-preserving.
for i in range(6):
    l,r=ents(i+1); m=MEASURES[i%len(MEASURES)]; pid=f"measure-par-{i}"
    add(f"MH{i:02d}","measure_head_higher",f"{l} recorded a higher {m} than {r}.",atom(l,"GREATER_THAN",r),pair_id=pid,pair_relation="meaning_preserving")
    add(f"MG{i:02d}","measure_head_greater",f"{l} recorded a greater {m} than {r}.",atom(l,"GREATER_THAN",r),pair_id=pid,pair_relation="meaning_preserving")
for i in range(4):
    l,r=ents(i+3); m=MEASURES[(i+3)%len(MEASURES)]; pid=f"measure-dir-{i}"
    add(f"ML{i:02d}","measure_head_lower",f"{l} reported a lower {m} than {r}.",atom(l,"LESS_THAN",r),pair_id=pid,pair_relation="meaning_changing")
    add(f"MR{i:02d}","measure_head_larger",f"{l} reported a larger {m} than {r}.",atom(l,"GREATER_THAN",r),pair_id=pid,pair_relation="meaning_changing")

# New comparative verbs.
for i in range(6):
    l,r=ents(i+2); d=2+i; pid=f"verb-dir-{i}"
    add(f"VX{i:02d}","verb_exceeded",f"{l} exceeded {r} by {d} units.",atom(l,"MORE_THAN",r),pair_id=pid,pair_relation="meaning_changing")
    add(f"VT{i:02d}","verb_trailed",f"{l} trailed {r} by {d} units.",atom(l,"LESS_THAN",r),pair_id=pid,pair_relation="meaning_changing")

# Equality, multiplier, and scalar threshold regression controls.
for i in range(4):
    l,r=ents(i+4)
    add(f"EQ{i:02d}","equality",f"{l} produced a total equal to {r}.",atom(l,"EQUAL_TO",r))
for i in range(4):
    l,r=ents(i+5)
    add(f"TW{i:02d}","multiplier",f"{l} produced twice as many units as {r}.",atom(l,"MULTIPLE_OF",r))
for i in range(4):
    label=["Pressure","Temperature","Volume","Score"][i]; value=30+i
    add(f"TH{i:02d}","scalar_threshold",f"{label} was more than {value} units.",atom(label,"MORE_THAN",f"{value} units"))

# Negative/domain traps and deliberately unsupported forms. Gold None means no
# supported comparison object should be emitted.
NEG=[
 "The higher folder contains archived notes.",
 "The greater-than symbol appears in the manual.",
 "The lower shelf contains twelve files.",
 "The smaller label is blue.",
 "The exceeded flag is archived.",
 "The trailed column is hidden.",
 "Sector A processed 12 units and Sector B processed 9 units.",
 "Sector A and Sector B are listed in the comparison table.",
 "Sector A surpassed Sector B by four units.",
 "Sector A lagged behind Sector B.",
 "Sector A was roughly comparable to Sector B.",
 "More documentation is available in Sector A.",
]
for i,text in enumerate(NEG): add(f"N{i:02d}","negative_or_unsupported",text,None)

assert len(CASES)==64, len(CASES)
