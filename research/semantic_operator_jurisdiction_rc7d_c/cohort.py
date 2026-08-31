"""RC7D-C held-out cohort authored after equivalence + validator-v2 freeze."""
from __future__ import annotations

CASES: list[dict] = []


def add(cid, text, gold, composition=None, group=""):
    CASES.append({
        "case_id": cid,
        "text": text,
        "gold": gold,
        "gold_dimensions": sorted(gold),
        "composition": [
            {"dimensions": sorted([a, b]), "expected": expected}
            for a, b, expected in (composition or [])
        ],
        "group": group,
    })

# Quantifier + exception. First six use known surfaces; final four are held-out variants.
qe = [
    ("Every technician inspected the vessel except Mira.", "every", "technician", "inspect vessel", "mira"),
    ("All reviewers approved the packet, excluding Hugo.", "every", "reviewers", "approve packet", "hugo"),
    ("Each auditor signed the release other than Ada.", "every", "auditor", "sign release", "ada"),
    ("Some inspectors reviewed the record save for Rowan.", "some", "inspectors", "review record", "rowan"),
    ("No analysts approved the sample apart from Nia.", "none", "analysts", "approve sample", "nia"),
    ("Not every reviewer signed the certificate with the exception of Hugo.", "not_every", "reviewer", "sign certificate", "hugo"),
    ("Every technician inspected the vessel bar Mira.", "every", "technician", "inspect vessel", "mira"),
    ("All reviewers aside from Hugo approved the packet.", "every", "reviewers", "approve packet", "hugo"),
    ("Each auditor, Ada excepted, signed the release.", "every", "auditor", "sign release", "ada"),
    ("Some inspectors reviewed the record, Rowan being the lone exception.", "some", "inspectors", "review record", "rowan"),
]
for i,(text,q,pop,pred,x) in enumerate(qe,1):
    add(f"C-QE-{i:02d}",text,{"quantifier":[{"kind":"quantifier","quantifier":q,"population":pop,"predicate":pred}],"exception":[{"kind":"exception","excluded":x}]},[("quantifier","exception","compose")],"quantifier_exception")

# Quantifier + epistemic probability/modality.
qp = [
    ("Probably every technician inspected the vessel.","every","technician","inspect vessel","probable"),
    ("Every reviewer likely approved the packet.","every","reviewer","approve packet","likely"),
    ("Some auditors probably signed the release.","some","auditors","sign release","probable"),
    ("There is a chance that every inspector reviewed the record.","every","inspector","review record","possible"),
    ("Every technician is unlikely to have inspected the vessel.","every","technician","inspect vessel","unlikely"),
    ("Every technician conceivably inspected the vessel.","every","technician","inspect vessel","possible"),
    ("Perhaps all reviewers approved the packet.","every","reviewers","approve packet","possible"),
    ("Apparently some auditors signed the release.","some","auditors","sign release","possible"),
    ("Every inspector presumably reviewed the record.","every","inspector","review record","probable"),
    ("There is a reasonable chance every reviewer approved the packet.","every","reviewer","approve packet","possible"),
]
for i,(text,q,pop,pred,pv) in enumerate(qp,1):
    add(f"C-QP-{i:02d}",text,{"quantifier":[{"kind":"quantifier","quantifier":q,"population":pop,"predicate":pred}],"probability":[{"kind":"epistemic_probability","value":pv}]},[("quantifier","probability","coexist")],"quantifier_probability")

# Permission + temporal.
pt = [
    ("Only release stewards may sign the certificate. Nia is a member of the release stewards before the cutoff.", [{"kind":"necessary_permission_condition","population":"release stewards","predicate":"sign certificate"},{"kind":"membership","entity":"nia","population":"release stewards","value":"member"}], {"kind":"temporal_scope","relation":"before","reference":"cutoff"}),
    ("Only inspectors may release batch a. Hugo was authorized to release batch a after the deadline.", [{"kind":"necessary_permission_condition","population":"inspectors","predicate":"release batch a"},{"kind":"explicit_permission","entity":"hugo","predicate":"release batch a","value":"permitted"}], {"kind":"temporal_scope","relation":"after","reference":"deadline"}),
    ("Permission to approve the packet is limited to reviewers. Ada is a member of reviewers prior to the cutoff.", [{"kind":"necessary_permission_condition","population":"reviewers","predicate":"approve packet"},{"kind":"membership","entity":"ada","population":"reviewers","value":"member"}], {"kind":"temporal_scope","relation":"before","reference":"cutoff"}),
    ("Only auditors may sign the release. Rowan is not a member of auditors following the deadline.", [{"kind":"necessary_permission_condition","population":"auditors","predicate":"sign release"},{"kind":"membership","entity":"rowan","population":"auditors","value":"non_member"}], {"kind":"temporal_scope","relation":"after","reference":"deadline"}),
    ("Only reviewers may sign the record. As of 2026-08-31, Hugo is a member of reviewers.", [{"kind":"necessary_permission_condition","population":"reviewers","predicate":"sign record"},{"kind":"membership","entity":"hugo","population":"reviewers","value":"member"}], {"kind":"temporal_scope","relation":"as_of","reference":"2026-08-31"}),
    ("Only release officers may approve the dossier. Nia was permitted to approve the dossier until the cutoff.", [{"kind":"necessary_permission_condition","population":"release officers","predicate":"approve dossier"},{"kind":"explicit_permission","entity":"nia","predicate":"approve dossier","value":"permitted"}], {"kind":"temporal_scope","relation":"until","reference":"cutoff"}),
    ("Only release stewards may sign the certificate. Nia belonged to the release stewards ahead of the cutoff.", [{"kind":"necessary_permission_condition","population":"release stewards","predicate":"sign certificate"},{"kind":"membership","entity":"nia","population":"release stewards","value":"member"}], {"kind":"temporal_scope","relation":"before","reference":"cutoff"}),
    ("Only inspectors may release batch a. Hugo's authorization took effect subsequent to the deadline.", [{"kind":"necessary_permission_condition","population":"inspectors","predicate":"release batch a"},{"kind":"explicit_permission","entity":"hugo","predicate":"release batch a","value":"permitted"}], {"kind":"temporal_scope","relation":"after","reference":"deadline"}),
]
for i,(text,pa,ta) in enumerate(pt,1):
    add(f"C-PT-{i:02d}",text,{"permission":pa,"temporal":[ta]},[("permission","temporal","compose")],"permission_temporal")

# Permission + exception.
pe = [
    ("Only inspectors may release batch a except Mira.","inspectors","release batch a","mira"),
    ("Permission to approve the packet is restricted to reviewers, excluding Hugo.","reviewers","approve packet","hugo"),
    ("Only release stewards may sign the certificate other than Ada.","release stewards","sign certificate","ada"),
    ("Only auditors may approve the dossier save for Rowan.","auditors","approve dossier","rowan"),
    ("Only inspectors may sign the record apart from Nia.","inspectors","sign record","nia"),
    ("Only reviewers may approve the packet bar Hugo.","reviewers","approve packet","hugo"),
    ("Only auditors may release the batch aside from Ada.","auditors","release batch","ada"),
    ("Only release officers may sign the certificate, Nia excepted.","release officers","sign certificate","nia"),
]
for i,(text,pop,pred,x) in enumerate(pe,1):
    add(f"C-PE-{i:02d}",text,{"permission":[{"kind":"necessary_permission_condition","population":pop,"predicate":pred}],"exception":[{"kind":"exception","excluded":x}]},[("permission","exception","compose")],"permission_exception")

# Subclass + permission.
sp = [
    ("Release stewards are a subset of reviewers. Only reviewers may approve the packet.","release stewards","reviewers","reviewers","approve packet"),
    ("Lab auditors are a subclass of inspectors. Only inspectors may release batch a.","lab auditors","inspectors","inspectors","release batch a"),
    ("Release officers are a type of reviewers. Only reviewers may sign the certificate.","release officers","reviewers","reviewers","sign certificate"),
    ("Auditors are a kind of inspectors. Permission to approve the dossier is limited to inspectors.","auditors","inspectors","inspectors","approve dossier"),
    ("Release stewards sit within the reviewer class. Only reviewers may approve the packet.","release stewards","reviewer class","reviewers","approve packet"),
    ("Lab auditors fall under inspectors. Only inspectors may release batch a.","lab auditors","inspectors","inspectors","release batch a"),
    ("Release officers are nested beneath reviewers. Only reviewers may sign the certificate.","release officers","reviewers","reviewers","sign certificate"),
    ("Auditors belong to a narrower class than inspectors. Only inspectors may approve the dossier.","auditors","inspectors","inspectors","approve dossier"),
]
for i,(text,ch,pa,pop,pred) in enumerate(sp,1):
    add(f"C-SP-{i:02d}",text,{"subclass":[{"kind":"subclass","child":ch,"parent":pa}],"permission":[{"kind":"necessary_permission_condition","population":pop,"predicate":pred}]},[("subclass","permission","coexist")],"subclass_permission")

# Quantitative + event content.
qr = [
    ("Exactly four auditors signed the release.","exact_count","sign","auditors","release"),
    ("70% of the technicians inspected the vessel.","percentage","inspect","technicians","vessel"),
    ("Seventy percent of reviewers approved the packet.","percentage","approve","reviewers","packet"),
    ("At least 3 inspectors approved the record.","minimum_count","approve","inspectors","record"),
    ("A majority of lab analysts inspected the sample.","majority","inspect","lab analysts","sample"),
    ("Most release stewards reviewed the dossier.","most","review","release stewards","dossier"),
    ("Roughly three quarters of auditors signed the release.","proportion","sign","auditors","release"),
    ("A small minority of inspectors approved the record.","minority","approve","inspectors","record"),
]
for i,(text,qk,pred,subj,obj) in enumerate(qr,1):
    add(f"C-QR-{i:02d}",text,{"quantitative":[{"kind":"quantitative_scope","quantitative_kind":qk}],"role_binding":[{"kind":"event","predicate":pred,"subject":subj,"object":obj,"polarity":"positive"}]},[("quantitative","role_binding","coexist")],"quantitative_role")

# Role binding controls including unsupported paraphrases that should fail closed rather than invert semantics.
rl = [
    ("Dana reviewed the dossier.","review","dana","dossier","positive"),
    ("Dana did not review the dossier.","review","dana","dossier","negative"),
    ("The packet was approved by Mira.","approve","mira","packet","positive"),
    ("The packet was not approved by Mira.","approve","mira","packet","negative"),
    ("Hugo signed the certificate.","sign","hugo","certificate","positive"),
    ("Hugo did not sign the certificate.","sign","hugo","certificate","negative"),
    ("Dana never reviewed the dossier.","review","dana","dossier","negative"),
    ("At no point did Hugo sign the certificate.","sign","hugo","certificate","negative"),
]
for i,(text,p,s,o,pol) in enumerate(rl,1):
    add(f"C-RL-{i:02d}",text,{"role_binding":[{"kind":"event","predicate":p,"subject":s,"object":o,"polarity":pol}]},group="role_binding")

# No-authority domain-vocabulary traps.
na = [
    "The probability notebook is stored on shelf two.",
    "The likely label is printed in the header.",
    "Exception is the name of a database field.",
    "The temporal folder contains old exports.",
    "Subclass is a column in the schema.",
    "Permission is written on the tab.",
    "Every is the first word in the quoted example.",
    "Review is the title of the worksheet.",
]
for i,text in enumerate(na,1):
    add(f"C-NA-{i:02d}",text,{},group="no_authority")

assert len(CASES) == 68, len(CASES)
