"""RC7D-D held-out deterministic multi-reader cohort.

Authored only after candidate/validator freeze 300efc0ef3961f7d8dcc0ad651f4faf060377793.
No reader or validator may be changed after seeing these cases for this run.
"""
from __future__ import annotations

CANDIDATE_FREEZE="300efc0ef3961f7d8dcc0ad651f4faf060377793"
CASES=[]

def add(cid,text,gold,group,*,novel=False,composition=None):
    CASES.append({"case_id":cid,"text":text,"gold":gold,"gold_dimensions":sorted(gold),"group":group,"novel_surface":novel,"composition":composition or []})

def q(qv,pop,pred): return {"kind":"quantifier","quantifier":qv,"population":pop,"predicate":pred}
def ex(x): return {"kind":"exception","excluded":x}
def prob(v): return {"kind":"epistemic_probability","value":v}
def npc(pop,pred): return {"kind":"necessary_permission_condition","population":pop,"predicate":pred}
def evt(pred,subj,obj,pol="positive"): return {"kind":"event","predicate":pred,"subject":subj,"object":obj,"polarity":pol}
def sub(c,p): return {"kind":"subclass","child":c,"parent":p}
def quant(k,s): return {"kind":"quantitative_scope","quantitative_kind":k,"surface":s}
def temp(r,ref): return {"kind":"temporal_scope","relation":r,"reference":ref}

# Quantifier + exception: 12. First half targets alternate readers; second half
# deliberately uses unseen surfaces to test whether deterministic diversity really generalizes.
_qe=[
("All of the technicians inspected the vessel aside from Mira.","every","technicians","inspect vessel","mira",False),
("Every one of the reviewers approved the packet bar Hugo.","every","reviewers","approve packet","hugo",False),
("Some of the auditors signed the release, Ada excepted.","some","auditors","sign release","ada",False),
("None of the inspectors reviewed the record with Rowan left out.","none","inspectors","review record","rowan",False),
("At least one of the analysts approved the sample but not Nia.","some","analysts","approve sample","nia",False),
("Not all of the reviewers signed the certificate, Hugo being the exception.","not_every","reviewers","sign certificate","hugo",False),
("The entirety of the technicians inspected the vessel, Mira omitted.","every","technicians","inspect vessel","mira",True),
("Reviewers without Hugo all approved the packet.","every","reviewers","approve packet","hugo",True),
("There was at least one auditor signing the release, other than Ada.","some","auditors","sign release","ada",True),
("Zero inspectors reviewed the record, Rowan aside.","none","inspectors","review record","rowan",True),
("A technician or more inspected the vessel, with Mira carved out.","some","technicians","inspect vessel","mira",True),
("It was not the case that all reviewers signed the certificate; Hugo was exempt.","not_every","reviewers","sign certificate","hugo",True),
]
for i,(t,qv,p,pred,x,n) in enumerate(_qe,1): add(f"D-QE-{i:02d}",t,{"quantifier":[q(qv,p,pred)],"exception":[ex(x)]},"quantifier_exception",novel=n,composition=[("exception","quantifier","compose")])

_qp=[
("Perhaps all of the technicians inspected the vessel.","every","technicians","inspect vessel","possible",False),
("Every one of the reviewers quite likely approved the packet.","every","reviewers","approve packet","likely",False),
("Some of the auditors probably signed the release.","some","auditors","sign release","probable",False),
("Not all of the inspectors conceivably reviewed the record.","not_every","inspectors","review record","possible",False),
("None of the analysts were likely to have approved the sample.","none","analysts","approve sample","likely",False),
("There is a real chance that every one of the reviewers signed the certificate.","every","reviewers","sign certificate","possible",False),
("Plausibly every technician inspected the vessel.","every","technician","inspect vessel","possible",True),
("Odds favor all reviewers approving the packet.","every","reviewers","approve packet","likely",True),
("Some auditors may well have signed the release.","some","auditors","sign release","possible",True),
("It seems doubtful that every inspector reviewed the record.","not_every","inspector","review record","unlikely",True),
("No analyst apparently approved the sample.","none","analyst","approve sample","probable",True),
("Every reviewer, by all indications, signed the certificate.","every","reviewer","sign certificate","probable",True),
]
for i,(t,qv,p,pred,pv,n) in enumerate(_qp,1): add(f"D-QP-{i:02d}",t,{"quantifier":[q(qv,p,pred)],"probability":[prob(pv)]},"quantifier_probability",novel=n,composition=[("probability","quantifier","coexist")])

_pe=[
("Inspectors alone may release batch a, aside from Mira.","inspectors","release batch a","mira",False),
("Approve the packet is reserved for reviewers, bar Hugo.","reviewers","approve the packet","hugo",False),
("Release stewards alone may sign the certificate, Ada excepted.","release stewards","sign the certificate","ada",False),
("Approve the dossier is reserved for auditors, Rowan being the exception.","auditors","approve the dossier","rowan",False),
("Inspectors alone may sign the record with Nia left out.","inspectors","sign the record","nia",False),
("The exclusive privilege to release batch a belongs to inspectors, except Mira.","inspectors","release batch a","mira",True),
("Reviewers hold sole approval rights for the packet, Hugo excluded.","reviewers","approve the packet","hugo",True),
("Signing the certificate is the preserve of release stewards, except Ada.","release stewards","sign the certificate","ada",True),
("Auditors have exclusive dossier approval authority, except Rowan.","auditors","approve the dossier","rowan",True),
("Record-signing rights belong solely to inspectors, Nia exempt.","inspectors","sign the record","nia",True),
]
for i,(t,p,pred,x,n) in enumerate(_pe,1): add(f"D-PE-{i:02d}",t,{"permission":[npc(p,pred)],"exception":[ex(x)]},"permission_exception",novel=n,composition=[("exception","permission","compose")])

_pt=[
("Only release stewards may sign the certificate. Nia is a member of the release stewards before the cutoff.","release stewards","sign the certificate","before","the cutoff",False),
("Inspectors alone may release batch a. Hugo has permission to release batch a after the deadline.","inspectors","release batch a","after","the deadline",False),
("Approve the packet is reserved for reviewers. Ada falls within reviewers prior to the cutoff.","reviewers","approve the packet","before","the cutoff",False),
("Only auditors may sign the release. Rowan is not a member of auditors following the deadline.","auditors","sign the release","after","the deadline",False),
("Release officers alone may approve the dossier. Nia has permission to approve the dossier until the cutoff.","release officers","approve the dossier","until","the cutoff",False),
("Only reviewers may sign the record. Hugo is a member of reviewers as of 2026-08-31.","reviewers","sign the record","as_of","2026-08-31",False),
("The certificate-signing privilege is exclusive to release stewards. Nia belonged to them earlier than the cutoff.","release stewards","sign the certificate","before","the cutoff",True),
("Release authority rests solely with inspectors. Hugo gained that authority later than the deadline.","inspectors","release batch a","after","the deadline",True),
("Packet approval belongs exclusively to reviewers. Ada entered that class ahead of the cutoff.","reviewers","approve the packet","before","the cutoff",True),
("Only auditors may sign the release. Rowan ceased to belong once the deadline passed.","auditors","sign the release","after","the deadline",True),
]
for i,(t,p,pred,r,ref,n) in enumerate(_pt,1): add(f"D-PT-{i:02d}",t,{"permission":[npc(p,pred)],"temporal":[temp(r,ref)]},"permission_temporal",novel=n,composition=[("permission","temporal","compose")])

_sp=[
("Release stewards are a subtype of reviewers. Only reviewers may approve the packet.","release stewards","reviewers","reviewers","approve the packet",False),
("Lab auditors are nested beneath inspectors. Inspectors alone may release batch a.","lab auditors","inspectors","inspectors","release batch a",False),
("Release officers belong to a narrower class than reviewers. Only reviewers may sign the certificate.","release officers","reviewers","reviewers","sign the certificate",False),
("Auditors are contained within inspectors. Approve the dossier is reserved for inspectors.","auditors","inspectors","inspectors","approve the dossier",False),
("Release stewards form a narrower category of reviewers. Only reviewers may approve the packet.","release stewards","reviewers","reviewers","approve the packet",True),
("Lab auditors occupy a child category under inspectors. Only inspectors may release batch a.","lab auditors","inspectors","inspectors","release batch a",True),
("Release officers sit one taxonomic level below reviewers. Only reviewers may sign the certificate.","release officers","reviewers","reviewers","sign the certificate",True),
("Auditors are encompassed by the inspector category. Only inspectors may approve the dossier.","auditors","inspectors","inspectors","approve the dossier",True),
]
for i,(t,c,p,pop,pred,n) in enumerate(_sp,1): add(f"D-SP-{i:02d}",t,{"subclass":[sub(c,p)],"permission":[npc(pop,pred)]},"subclass_permission",novel=n,composition=[("permission","subclass","coexist")])

_qr=[
("Roughly three quarters of auditors signed the release.","proportion","roughly three quarters of","auditors","sign","the release",False),
("Two thirds of technicians inspected the vessel.","proportion","two thirds of","technicians","inspect","the vessel",False),
("A small minority of reviewers approved the packet.","minority","a small minority of","reviewers","approve","the packet",False),
("Fewer than three inspectors reviewed the record.","maximum_count","fewer than three","inspectors","review","the record",False),
("Roughly half of analysts approved the sample.","proportion","roughly half of","analysts","approve","the sample",False),
("About three quarters of auditors signed the release.","proportion","about three quarters of","auditors","sign","the release",True),
("Approximately two in three technicians inspected the vessel.","proportion","approximately two in three","technicians","inspect","the vessel",True),
("Only a sliver of reviewers approved the packet.","minority","only a sliver of","reviewers","approve","the packet",True),
("Under three inspectors reviewed the record.","maximum_count","under three","inspectors","review","the record",True),
("Close to half the analysts approved the sample.","proportion","close to half","analysts","approve","the sample",True),
]
for i,(t,k,s,subj,pred,obj,n) in enumerate(_qr,1): add(f"D-QR-{i:02d}",t,{"quantitative":[quant(k,s)],"role_binding":[evt(pred,subj,obj)]},"quantitative_role",novel=n,composition=[("quantitative","role_binding","coexist")])

_roles=[
("Dana never reviewed the dossier.",evt("review","dana","the dossier","negative"),False),
("At no point did Hugo sign the certificate.",evt("sign","hugo","the certificate","negative"),False),
("The packet was approved by Mira.",evt("approve","mira","the packet"),False),
("Rowan did not inspect the vessel.",evt("inspect","rowan","the vessel","negative"),False),
("Dana failed to review the dossier.",evt("review","dana","the dossier","negative"),True),
("Hugo refrained from signing the certificate.",evt("sign","hugo","the certificate","negative"),True),
("Approval of the packet came from Mira.",evt("approve","mira","the packet"),True),
("The vessel went uninspected by Rowan.",evt("inspect","rowan","the vessel","negative"),True),
]
for i,(t,a,n) in enumerate(_roles,1): add(f"D-RL-{i:02d}",t,{"role_binding":[a]},"role_binding",novel=n)

# Contradictory same-dimension assertions. Preserve both readings; composition policy
# must mark the pair as conflict rather than silently selecting one.
_conf=[
("Dana reviewed the dossier. Dana did not review the dossier.",[evt("review","dana","the dossier"),evt("review","dana","the dossier","negative")]),
("Hugo signed the certificate. Hugo never signed the certificate.",[evt("sign","hugo","the certificate"),evt("sign","hugo","the certificate","negative")]),
("Mira approved the packet. The packet was not approved by Mira.",[evt("approve","mira","the packet"),evt("approve","mira","the packet","negative")]),
("Rowan inspected the vessel. At no point did Rowan inspect the vessel.",[evt("inspect","rowan","the vessel"),evt("inspect","rowan","the vessel","negative")]),
]
for i,(t,atoms) in enumerate(_conf,1): add(f"D-CF-{i:02d}",t,{"role_binding":atoms},"internal_conflict",novel=True,composition=[("role_binding","role_binding","conflict")])

_traps=[
"The probability notebook contains reviewer names.",
"The likely folder was archived yesterday.",
"The exception report lists Mira as an owner.",
"The subclass field is blank in the schema.",
"The permission label is blue.",
"The quantitative dashboard was refreshed.",
"The temporal file has a new checksum.",
"The role binding documentation is incomplete.",
]
for i,t in enumerate(_traps,1): add(f"D-NA-{i:02d}",t,{},"no_authority",novel=True)

assert len(CASES)==84, len(CASES)
assert sum(1 for c in CASES if len(c["gold_dimensions"])>1)==64
assert sum(1 for c in CASES if len(c["gold_dimensions"])>1 and c["novel_surface"])>=32
