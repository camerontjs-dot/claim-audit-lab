"""RC7F-B held-out semantics-first comparison cohort.

Formal comparison atoms precede deterministic rendering. Created only after
apparatus freeze d331fe6cbd6ce5ec56c446bd3a8a572b33c3457f.
"""
from __future__ import annotations

COHORT_FREEZE_EXPECTED="rc7fb-heldout-v1-semantics-first-20260831"
APPARATUS_FREEZE="d331fe6cbd6ce5ec56c446bd3a8a572b33c3457f"
QUALIFICATION_RUN=33453159594
QUALIFICATION_ARTIFACT=9780474015
QUALIFICATION_DIGEST="sha256:7eafa20c8bf91fef9ad1f9b516d8543a05de0cae95564635cf6219db978423a7"

CASES=[]
_seen={}

def atom(left,relation,right,delta=None):
    d={"left":left.lower(),"relation":relation,"right":right.lower()}
    if delta is not None: d["delta_surface"]=str(delta)
    return d

def add(cid,family,text,gold,*,pair_id=None,pair_relation=None,tags=()):
    assert cid not in {c['case_id'] for c in CASES}
    norm=" ".join(text.strip().split()).lower()
    gold_key=None if gold is None else (gold['left'],gold['relation'],gold['right'],gold.get('delta_surface'))
    if norm in _seen and _seen[norm]!=gold_key: raise AssertionError("duplicate source incompatible gold")
    _seen[norm]=gold_key
    CASES.append({"case_id":cid,"family":family,"raw_source":text,"gold":gold,"pair_id":pair_id,"pair_relation":pair_relation,"tags":list(tags)})

entities=[("Division K","Depot F"),("Center H","Lab Z"),("Branch Q","Region V"),("Sector J","Hub W"),("Office P","Node L"),("Zone T","Bay C")]
verbs=["catalogued","sealed","verified","reconciled","dispatched","archived"]
objects=["records","modules","packets","samples","files","permits"]

# Delta direction pairs, formal relation differs while the rest is held constant.
for i in range(4):
    left,right=entities[i]; verb=verbs[i]; obj=objects[i]; n=["seven","four","nine","six"][i]
    add(f"DM{i+1:02d}","delta",f"{left} {verb} 42 {obj}, {n} more than {right}.",atom(left,"MORE_THAN",right,n),pair_id=f"delta-dir-{i+1}",pair_relation="meaning_changing")
    add(f"DF{i+1:02d}","delta",f"{left} {verb} 42 {obj}, {n} fewer than {right}.",atom(left,"FEWER_THAN",right,n),pair_id=f"delta-dir-{i+1}",pair_relation="meaning_changing")

for i in range(4,8):
    left,right=entities[i%len(entities)]; verb=verbs[i%len(verbs)]; obj=objects[i%len(objects)]; n=str(3+i)
    rel="MORE_THAN" if i%2==0 else "LESS_THAN"; word="more" if i%2==0 else "less"
    add(f"DX{i+1:02d}","delta",f"{left} {verb} 31 {obj}, {n} {word} than {right}.",atom(left,rel,right,n),tags=("numeric_delta",))

# Share/rate direction pairs.
for i in range(4):
    left,right=entities[(i+1)%len(entities)]; measure=["share","rate","percentage","proportion"][i]
    add(f"SG{i+1:02d}","share_rate",f"{left} verified 47% of packets, a greater {measure} than {right}.",atom(left,"GREATER_THAN",right),pair_id=f"share-dir-{i+1}",pair_relation="meaning_changing")
    add(f"SL{i+1:02d}","share_rate",f"{left} verified 47% of packets, a lower {measure} than {right}.",atom(left,"LESS_THAN",right),pair_id=f"share-dir-{i+1}",pair_relation="meaning_changing")

# Meaning-preserving comparative paraphrases.
for i in range(4):
    left,right=entities[(i+2)%len(entities)]
    add(f"PH{i+1:02d}","direct",f"{left} had a higher output than {right}.",atom(left,"GREATER_THAN",right),pair_id=f"direct-para-{i+1}",pair_relation="meaning_preserving")
    add(f"PG{i+1:02d}","direct",f"{left} had a greater output than {right}.",atom(left,"GREATER_THAN",right),pair_id=f"direct-para-{i+1}",pair_relation="meaning_preserving",tags=("paraphrase",))

# Equality.
for i in range(3):
    left,right=entities[(i+3)%len(entities)]
    add(f"EQ{i+1:02d}","equality",f"{left} produced a total equal to {right}.",atom(left,"EQUAL_TO",right))
for i in range(3):
    left,right=entities[i]
    add(f"ES{i+1:02d}","equality",f"{left} recorded the same total as {right}.",atom(left,"EQUAL_TO",right))

# Multipliers.
for i in range(3):
    left,right=entities[(i+1)%len(entities)]
    add(f"TW{i+1:02d}","multiplier",f"{left} processed twice as many records as {right}.",atom(left,"MULTIPLE_OF",right,"2"))
for i in range(3):
    left,right=entities[(i+2)%len(entities)]
    add(f"HF{i+1:02d}","multiplier",f"{left} processed half as many records as {right}.",atom(left,"MULTIPLE_OF",right,"0.5"))

# Scalar thresholds.
thresholds=[
 ("temperature","lower","LESS_THAN","8 C"),("pressure","higher","GREATER_THAN","12 kPa"),
 ("humidity","more","MORE_THAN","60 %"),("latency","less","LESS_THAN","25 ms"),
 ("voltage","greater","GREATER_THAN","9 V"),("mass","lower","LESS_THAN","14 kg"),
 ("density","more","MORE_THAN","4 g/ml"),("duration","less","LESS_THAN","30 s"),
]
for i,(left,word,rel,right) in enumerate(thresholds):
    add(f"TH{i+1:02d}","threshold",f"The {left} was {word} than {right}.",atom(left,rel,right))

# Known unsupported but semantically clear comparative paraphrases: safe misses are evidence.
add("US01","unsupported_paraphrase","Division K exceeded Depot F by seven records.",atom("Division K","MORE_THAN","Depot F","seven"),tags=("unseen_construction",))
add("US02","unsupported_paraphrase","Center H trailed Lab Z by four modules.",atom("Center H","LESS_THAN","Lab Z","four"),tags=("unseen_construction",))

# Negative/domain traps. No comparison atom is warranted.
negative=[
 "The Greater Than report was archived in cabinet C.",
 "The lower panel contains the calibration controls.",
 "The comparison column is hidden from the dashboard.",
 "More records were archived yesterday.",
 "Division K logged 22 files and Depot F logged 18 files.",
 "Center H listed 40% while Lab Z listed 30%.",
 "The label says higher but provides no compared entity.",
 "Half the archive was indexed before noon.",
 "Branch Q was more or less aligned with Region V.",
 "The same reviewer signed both records.",
]
for i,text in enumerate(negative): add(f"NEG{i+1:02d}","negative_control",text,None)

assert len(CASES)==60, len(CASES)
