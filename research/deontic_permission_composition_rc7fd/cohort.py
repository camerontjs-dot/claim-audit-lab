"""RC7F-D semantics-first permission + modifier held-out cohort."""
from __future__ import annotations
COHORT_FREEZE_EXPECTED="rc7fd-heldout-v1-semantics-first-20260831"
CASES=[]
POPS=["release stewards","quality delegates","field inspectors","audit reviewers","control analysts","senior operators","batch approvers","record custodians"]
PREDS=["approve packet u","release batch w","sign form j","review ledger c","archive dossier t","inspect sample v","verify permit q","process record m"]
NAMES=["Talia","Ravi","Mona","Ivo","Keira","Basil","Yara","Noel"]

def gold(pop,pred,exc=None,temp=None):
    return {"kind":"necessary_permission_condition","population":pop.lower(),"predicate":pred.lower(),"exception":exc,"temporal":temp}
def exc(name,cue): return {"excluded":name.lower(),"cue":cue}
def temp(rel,ref,cue=None): return {"relation":rel,"reference":ref.lower(),"cue":cue or ("as of" if rel=="as_of" else rel)}
def add(cid,family,text,g,*,pair_id=None,pair_relation=None,tags=()):
    CASES.append({"case_id":cid,"family":family,"raw_source":text,"gold":g,"pair_id":pair_id,"pair_relation":pair_relation,"tags":list(tags)})

# Exception composition across both permission surfaces and all supported cues.
EXC=["except","excluding","apart from","save for","with the exception of"]
for i in range(10):
    pop=POPS[i%len(POPS)]; pred=PREDS[i%len(PREDS)]; name=NAMES[i%len(NAMES)]; cue=EXC[i%len(EXC)]
    if i%2==0: text=f"Only {pop} may {pred}, {cue} {name}."
    else: text=f"Permission to {pred} is restricted to {pop}, {cue} {name}."
    add(f"EX{i:02d}","permission_exception",text,gold(pop,pred,exc(name,cue)))

# Meaning-changing exception entity pairs.
for i in range(4):
    pop=POPS[(i+2)%len(POPS)]; pred=PREDS[(i+3)%len(PREDS)]; n1=NAMES[i]; n2=NAMES[i+4]; pid=f"exc-entity-{i}"
    add(f"EA{i:02d}","exception_entity_a",f"Only {pop} may {pred}, except {n1}.",gold(pop,pred,exc(n1,"except")),pair_id=pid,pair_relation="meaning_changing")
    add(f"EB{i:02d}","exception_entity_b",f"Only {pop} may {pred}, except {n2}.",gold(pop,pred,exc(n2,"except")),pair_id=pid,pair_relation="meaning_changing")

# Temporal composition across both core surfaces.
TEMP=[("before","the deadline"),("after","the cutoff"),("until","the review date"),("as_of","2027-03-15")]
for i in range(12):
    pop=POPS[(i+1)%len(POPS)]; pred=PREDS[(i+2)%len(PREDS)]; rel,ref=TEMP[i%len(TEMP)]; cue="as of" if rel=="as_of" else rel
    if i%2==0: text=f"Only {pop} may {pred} {cue} {ref}."
    else: text=f"Permission to {pred} is restricted to {pop} {cue} {ref}."
    add(f"TM{i:02d}","permission_temporal",text,gold(pop,pred,None,temp(rel,ref,cue)))

# Meaning-changing temporal direction pairs.
for i in range(4):
    pop=POPS[(i+4)%len(POPS)]; pred=PREDS[(i+5)%len(PREDS)]; pid=f"temp-dir-{i}"
    add(f"TB{i:02d}","temporal_before",f"Only {pop} may {pred} before the checkpoint.",gold(pop,pred,None,temp("before","the checkpoint")),pair_id=pid,pair_relation="meaning_changing")
    add(f"TA{i:02d}","temporal_after",f"Only {pop} may {pred} after the checkpoint.",gold(pop,pred,None,temp("after","the checkpoint")),pair_id=pid,pair_relation="meaning_changing")

# Bare permission regression controls, paired across core surfaces as meaning-preserving.
for i in range(6):
    pop=POPS[(i+5)%len(POPS)]; pred=PREDS[(i+6)%len(PREDS)]; pid=f"surface-{i}"
    g=gold(pop,pred)
    add(f"OM{i:02d}","only_may",f"Only {pop} may {pred}.",g,pair_id=pid,pair_relation="meaning_preserving")
    add(f"RT{i:02d}","restricted_to",f"Permission to {pred} is restricted to {pop}.",g,pair_id=pid,pair_relation="meaning_preserving")

# Negative/domain traps and unsupported ambiguity. No operational inference is scored.
NEG=[
 "Talia may review ledger c.",
 "Talia may have reviewed ledger c.",
 "The permission column is blue.",
 "The permissions table is archived.",
 "Everyone except Talia signed form j.",
 "The exception field names Mona.",
 "The batch expires after the cutoff.",
 "Before the deadline, the folder was empty.",
 "The as of label appears in the footer.",
 "Only yesterday did Talia review ledger c.",
 "Permission data may be stale.",
 "The restricted-to field is optional.",
 "If inspectors are available, they may review packet u.",
 "Inspectors can review packet u when assigned.",
]
for i,text in enumerate(NEG): add(f"N{i:02d}","negative_or_unsupported",text,None)

assert len(CASES)==64, len(CASES)
