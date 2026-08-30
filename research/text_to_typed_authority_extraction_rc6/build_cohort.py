from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any


def _c(case_id: str, family: str, text: str, query: str, expected_case: dict[str, Any] | None, expected_relation: str | None, partition: str = "in_schema") -> dict[str, Any]:
    return {"case_id":case_id,"partition":partition,"family":family,"text":text,"query_text":query,"expected_status":"resolved" if expected_case is not None else "unknown","expected_case":expected_case,"expected_relation":expected_relation}


def membership_case(entity: str, population: str, membership: str, predicate: str, modality: str, polarity: str, kind: str) -> dict[str, Any]:
    return {"dimension":"membership_rule","authority":{"entity":entity,"population":population,"membership":membership,"rule":{"predicate":predicate,"modality":modality,"polarity":polarity}},"query":{"kind":kind,"entity":entity,"population":population,"predicate":predicate}}


def subclass_case(status: str, base: str, target: str, edge: str) -> dict[str, Any]:
    return {"dimension":"subclass","authority":{"membership_population":base,"membership":status,"subclass_edge":edge},"query":{"kind":"membership","population":target}}


def only_case(entity: str, population: str, membership: str, predicate: str, explicit_permission: str) -> dict[str, Any]:
    return {"dimension":"only_permission","authority":{"entity":entity,"population":population,"membership":membership,"predicate":predicate,"only_population_may":True,"explicit_permission":explicit_permission},"query":{"kind":"permission","entity":entity,"population":population,"predicate":predicate}}


def quant_case(population: str, predicate: str, aq: str, qq: str) -> dict[str, Any]:
    return {"dimension":"quantifier","authority":{"population":population,"predicate":predicate,"quantifier":aq},"query":{"kind":"quantified","population":population,"predicate":predicate,"quantifier":qq}}


def group_case(predicate: str, event_scope: str, polarity: str, q_scope: str, q_polarity: str) -> dict[str, Any]:
    return {"dimension":"group_scope","authority":{"predicate":predicate,"event_scope":event_scope,"polarity":polarity},"query":{"kind":"event","predicate":predicate,"event_scope":q_scope,"polarity":q_polarity}}


def role_case(subject: str, obj: str, predicate: str, polarity: str, q_subject: str, q_obj: str, q_polarity: str) -> dict[str, Any]:
    return {"dimension":"role_binding","authority":{"event":{"predicate":predicate,"roles":{"subject":subject,"object":obj},"polarity":polarity}},"query":{"kind":"event","predicate":predicate,"roles":{"subject":q_subject,"object":q_obj},"polarity":q_polarity}}


def temporal_case(entity: str, population: str, window: str, predicate: str, modality: str, polarity: str, q_time: str, q_kind: str) -> dict[str, Any]:
    return {"dimension":"temporal_membership","authority":{"entity":entity,"population":population,"membership_window":window,"rule":{"predicate":predicate,"modality":modality,"polarity":polarity}},"query":{"kind":q_kind,"entity":entity,"population":population,"predicate":predicate,"time":q_time}}


def build_cases() -> list[dict[str, Any]]:
    C: list[dict[str, Any]]=[]
    specs=[
        ("Mira","certified inspector","member","log seals","fact","positive","membership","Mira is a certified inspector. Certified inspectors log seals.","Mira is a certified inspector."),
        ("Mira","certified inspector","non_member","log seals","fact","positive","membership","Mira is not a certified inspector. Certified inspectors log seals.","Mira is a certified inspector."),
        ("Mira","certified inspector","unknown","log seals","fact","positive","membership","The record does not establish whether Mira is a certified inspector. Certified inspectors log seals.","Mira is a certified inspector."),
        ("Nia","lab courier","member","scan badges","fact","positive","behavior_positive","Nia is a lab courier. Lab couriers scan badges.","Nia scans badges."),
        ("Nia","lab courier","member","scan badges","obligation","positive","behavior_positive","Nia is a lab courier. Lab couriers must scan badges.","Nia scans badges."),
        ("Oren","field auditor","member","enter zone c","fact","negative","behavior_positive","Oren is a field auditor. Field auditors do not enter zone C.","Oren enters zone C."),
        ("Oren","field auditor","member","enter zone c","fact","negative","behavior_negative","Oren belongs to the field-auditor class. Field auditors do not enter zone C.","Oren does not enter zone C."),
        ("Pia","sterile operator","non_member","wear hood","fact","positive","rule_applies","Pia is outside the sterile-operator class. Sterile operators wear hoods.","The sterile-operator rule applies to Pia wearing a hood."),
        ("Pia","sterile operator","member","wear hood","fact","positive","rule_applies","Pia belongs to the sterile-operator class. Sterile operators wear hoods.","The sterile-operator rule applies to Pia wearing a hood."),
        ("Ravi","release reviewer","unknown","sign release","obligation","positive","behavior_positive","Whether Ravi is a release reviewer is not established. Release reviewers must sign releases.","Ravi signs releases."),
    ]
    for i,s in enumerate(specs,1):
        e,p,m,pred,mod,pol,kind,text,q=s; case=membership_case(e,p,m,pred,mod,pol,kind)
        rel={"member":"entailment","non_member":"contradiction","unknown":"neutral"}[m] if kind in {"membership","rule_applies"} else None
        if kind.startswith("behavior"):
            if m!="member" or mod!="fact": rel="neutral"
            else: rel="entailment" if ((pol=="positive")== (kind=="behavior_positive")) else "contradiction"
        C.append(_c(f"MR-{i:02d}","membership_rule",text,q,case,rel))

    sub_specs=[
        ("member","A","B","A_sub_B","Every field inspector is an inspector. Nia is a field inspector.","Nia is an inspector.","entailment"),
        ("member","B","A","A_sub_B","Every field inspector is an inspector. Nia is an inspector.","Nia is a field inspector.","neutral"),
        ("non_member","B","A","A_sub_B","Every field inspector is an inspector. Nia is not an inspector.","Nia is a field inspector.","contradiction"),
        ("non_member","A","B","A_sub_B","Every field inspector is an inspector. Nia is not a field inspector.","Nia is an inspector.","neutral"),
        ("unknown","A","B","A_sub_B","Every field inspector is an inspector. Nia's field-inspector membership is unknown.","Nia is an inspector.","neutral"),
        ("member","B","A","B_sub_A","Every inspector is a field inspector. Nia is an inspector.","Nia is a field inspector.","entailment"),
        ("non_member","A","B","B_sub_A","Every inspector is a field inspector. Nia is not a field inspector.","Nia is an inspector.","contradiction"),
        ("member","A","B","B_sub_A","Every inspector is a field inspector. Nia is a field inspector.","Nia is an inspector.","neutral"),
        ("non_member","B","A","B_sub_A","Every inspector is a field inspector. Nia is not an inspector.","Nia is a field inspector.","neutral"),
        ("member","A","A","none","No subclass relation is stated. Nia is in class A.","Nia is in class A.","entailment"),
    ]
    for i,(st,b,t,e,text,q,rel) in enumerate(sub_specs,1): C.append(_c(f"SC-{i:02d}","subclass",text,q,subclass_case(st,b,t,e),rel))

    only_specs=[
        ("member","unknown","Only licensed inspectors may open the vault. Nia is a licensed inspector.","Nia may open the vault.","neutral"),
        ("non_member","unknown","Only licensed inspectors may open the vault. Nia is not a licensed inspector.","Nia may open the vault.","contradiction"),
        ("unknown","unknown","Only licensed inspectors may open the vault. Nia's inspector status is unknown.","Nia may open the vault.","neutral"),
        ("member","permitted","Only licensed inspectors may open the vault. Nia is a licensed inspector. Nia is explicitly permitted to open the vault.","Nia may open the vault.","entailment"),
        ("non_member","not_permitted","Only licensed inspectors may open the vault. Nia is not a licensed inspector. Nia is explicitly not permitted to open the vault.","Nia may open the vault.","contradiction"),
        ("member","not_permitted","Only licensed inspectors may open the vault. Nia is a licensed inspector. Nia is explicitly not permitted to open the vault.","Nia may open the vault.","contradiction"),
        ("unknown","permitted","Only licensed inspectors may open the vault. Nia is explicitly permitted to open the vault.","Nia is a licensed inspector.","entailment"),
        ("member","unknown","Only release reviewers may sign the disposition. Ravi is a release reviewer.","Ravi may sign the disposition.","neutral"),
        ("non_member","unknown","Only release reviewers may sign the disposition. Ravi is not a release reviewer.","Ravi may sign the disposition.","contradiction"),
        ("member","permitted","Only release reviewers may sign the disposition. Ravi is a release reviewer. Ravi is explicitly permitted to sign the disposition.","Ravi may sign the disposition.","entailment"),
    ]
    for i,(m,perm,text,q,rel) in enumerate(only_specs,1):
        pop="licensed inspector" if "vault" in text else "release reviewer"; pred="open vault" if "vault" in text else "sign disposition"; entity="Nia" if "Nia" in text else "Ravi"; case=only_case(entity,pop,m,pred,perm)
        if q.endswith("inspector."): case["query"]["kind"]="membership"
        C.append(_c(f"ON-{i:02d}","only_permission",text,q,case,rel))

    qspec=[
        ("every","some","Every lab courier scans badges.","Some lab courier scans badges.","entailment"),
        ("every","not_every","Every lab courier scans badges.","Not every lab courier scans badges.","contradiction"),
        ("none","some","No lab courier scans badges.","Some lab courier scans badges.","contradiction"),
        ("none","not_every","No lab courier scans badges.","Not every lab courier scans badges.","entailment"),
        ("some","every","Some lab courier scans badges.","Every lab courier scans badges.","neutral"),
        ("not_every","every","Not every lab courier scans badges.","Every lab courier scans badges.","contradiction"),
        ("some","none","Some field auditor enters zone C.","No field auditor enters zone C.","contradiction"),
        ("none","every","No field auditor enters zone C.","Every field auditor enters zone C.","contradiction"),
        ("not_every","some","Not every field auditor enters zone C.","Some field auditor enters zone C.","neutral"),
        ("every","every","Every field auditor enters zone C.","Every field auditor enters zone C.","entailment"),
    ]
    for i,(aq,qq,text,q,rel) in enumerate(qspec,1):
        pop="lab courier" if "courier" in text else "field auditor"; pred="scan badges" if "scan" in text else "enter zone c"; C.append(_c(f"QU-{i:02d}","quantifier",text,q,quant_case(pop,pred,aq,qq),rel))

    gspec=[
        ("group","positive","group","positive","The audit committee signed the memo.","The audit committee signed the memo.","entailment"),
        ("group","positive","member","positive","The audit committee signed the memo.","Every member of the audit committee signed the memo.","neutral"),
        ("member","positive","group","positive","Every member of the audit committee signed the memo.","The audit committee signed the memo.","neutral"),
        ("member","positive","member","positive","Every member of the audit committee signed the memo.","Every member of the audit committee signed the memo.","entailment"),
        ("group","negative","group","positive","The audit committee did not sign the memo.","The audit committee signed the memo.","contradiction"),
        ("member","negative","member","positive","No member of the audit committee signed the memo.","Every member of the audit committee signed the memo.","contradiction"),
        ("group","positive","group","negative","The review board approved the release.","The review board did not approve the release.","contradiction"),
        ("member","positive","group","positive","Every member of the review board approved the release.","The review board approved the release.","neutral"),
        ("group","positive","member","positive","The review board approved the release.","Every member of the review board approved the release.","neutral"),
        ("member","negative","group","negative","No member of the review board approved the release.","The review board did not approve the release.","neutral"),
    ]
    for i,(s,p,qs,qp,text,q,rel) in enumerate(gspec,1):
        pred="sign memo" if "memo" in text else "approve release"; C.append(_c(f"GR-{i:02d}","group_scope",text,q,group_case(pred,s,p,qs,qp),rel))

    rspec=[
        ("Mira","Jalen","approve","positive","Mira","Jalen","positive","Mira approved Jalen.","Mira approved Jalen.","entailment"),
        ("Mira","Jalen","approve","positive","Jalen","Mira","positive","Mira approved Jalen.","Jalen approved Mira.","neutral"),
        ("Mira","Jalen","approve","negative","Mira","Jalen","positive","Mira did not approve Jalen.","Mira approved Jalen.","contradiction"),
        ("Mira","Jalen","approve","negative","Mira","Jalen","negative","Mira did not approve Jalen.","Mira did not approve Jalen.","entailment"),
        ("Nia","Oren","review","positive","Nia","Oren","positive","Nia reviewed Oren.","Nia reviewed Oren.","entailment"),
        ("Nia","Oren","review","positive","Oren","Nia","positive","Nia reviewed Oren.","Oren reviewed Nia.","neutral"),
        ("Nia","Oren","review","positive","Nia","Oren","negative","Nia reviewed Oren.","Nia did not review Oren.","contradiction"),
        ("Ravi","Pia","notify","negative","Ravi","Pia","positive","Ravi did not notify Pia.","Ravi notified Pia.","contradiction"),
        ("Ravi","Pia","notify","negative","Pia","Ravi","negative","Ravi did not notify Pia.","Pia did not notify Ravi.","neutral"),
        ("Ravi","Pia","notify","positive","Ravi","Pia","positive","Ravi notified Pia.","Ravi notified Pia.","entailment"),
    ]
    for i,(s,o,p,pol,qs,qo,qpol,text,q,rel) in enumerate(rspec,1): C.append(_c(f"RB-{i:02d}","role_binding",text,q,role_case(s,o,p,pol,qs,qo,qpol),rel))

    tspec=[
        ("before_only","before","membership","Before the cutoff, Mira is an inspector; after the cutoff, Mira is not an inspector.","Before the cutoff, Mira is an inspector.","entailment"),
        ("before_only","after","membership","Before the cutoff, Mira is an inspector; after the cutoff, Mira is not an inspector.","After the cutoff, Mira is an inspector.","contradiction"),
        ("after_only","after","membership","Starting at the cutoff, Mira is an inspector.","After the cutoff, Mira is an inspector.","entailment"),
        ("after_only","before","membership","Starting at the cutoff, Mira is an inspector.","Before the cutoff, Mira is an inspector.","contradiction"),
        ("always","before","membership","Mira is an inspector both before and after the cutoff.","Before the cutoff, Mira is an inspector.","entailment"),
        ("never","after","membership","Mira is not an inspector either before or after the cutoff.","After the cutoff, Mira is an inspector.","contradiction"),
        ("unknown","after","membership","The record does not establish when Mira is an inspector relative to the cutoff.","After the cutoff, Mira is an inspector.","neutral"),
        ("before_only","before","behavior_positive","Before the cutoff, Mira is an inspector; after it, she is not. Inspectors log seals.","Before the cutoff, Mira logs seals.","entailment"),
        ("before_only","after","behavior_positive","Before the cutoff, Mira is an inspector; after it, she is not. Inspectors log seals.","After the cutoff, Mira logs seals.","neutral"),
        ("after_only","after","behavior_positive","Starting at the cutoff, Mira is an inspector. Inspectors must log seals.","After the cutoff, Mira logs seals.","neutral"),
    ]
    for i,(w,t,k,text,q,rel) in enumerate(tspec,1):
        mod="obligation" if "must" in text else "fact"; C.append(_c(f"TM-{i:02d}","temporal_membership",text,q,temporal_case("Mira","inspector",w,"log seals",mod,"positive",t,k),rel))

    ambiguous=[
        ("Mira told Nia that she is an inspector.","Mira is an inspector."),("Oren met Ravi after he became a reviewer.","Oren is a reviewer."),("The supervisor discussed the courier with the inspector who was certified.","The courier is certified."),("Nia notified Pia because she was a release reviewer.","Nia is a release reviewer."),("Mira said the auditor reviewed her report.","Mira is the auditor."),("Ravi briefed Oren while he was acting as inspector.","Ravi is an inspector."),("The committee spoke with the board members after they approved the release.","The committee approved the release."),("Pia told Mira that her inspector status changed.","Pia is an inspector."),("Nia emailed Oren about the courier who was exempt.","Oren is exempt."),("Mira asked Ravi whether he remained a field auditor.","Mira is a field auditor."),
    ]
    for i,(text,q) in enumerate(ambiguous,1): C.append(_c(f"UA-{i:02d}","ambiguous_reference",text,q,None,None,"extraction_unknown"))
    underspecified=[
        ("Mira works with certified inspectors.","Mira is a certified inspector."),("Nia completed inspector training.","Nia is an inspector."),("Oren wears a courier badge.","Oren is a courier."),("Pia may be a release reviewer.","Pia is a release reviewer."),("Ravi supervises field auditors.","Ravi is a field auditor."),("Mira is assigned near the sterile operators.","Mira is a sterile operator."),("The policy mentions Nia in its inspector section.","Nia is an inspector."),("Oren's membership status is under review.","Oren is an inspector."),("Pia previously applied to become a courier.","Pia is a courier."),("Ravi has access to the reviewer handbook.","Ravi is a release reviewer."),
    ]
    for i,(text,q) in enumerate(underspecified,1): C.append(_c(f"UU-{i:02d}","insufficient_authority",text,q,None,None,"extraction_unknown"))
    escape=[
        ("Most lab couriers scan badges.","Every lab courier scans badges."),("Exactly three inspectors entered zone C.","Some inspector entered zone C."),("Inspectors usually log seals.","Every inspector logs seals."),("Inspectors scan badges if a supervisor is present.","Inspectors scan badges."),("Either inspectors or couriers may open the vault.","Inspectors may open the vault."),("At least half of field auditors approved the release.","Some field auditor approved the release."),("Former inspectors may retain archive access.","Inspectors may retain archive access."),("Inspectors may enter zone C unless an alarm is active.","Inspectors may enter zone C."),("Each inspector approved either Mira or Nia.","Every inspector approved Mira."),("There are more inspectors than couriers.","Some inspector is a courier."),
    ]
    for i,(text,q) in enumerate(escape,1): C.append(_c(f"UE-{i:02d}","ontology_escape",text,q,None,None,"ontology_escape"))
    return C


MUTATION_PAIRS=[
    {"pair_id":"P01","a":"MR-01","b":"MR-02","expected":"membership_polarity_flip"},{"pair_id":"P02","a":"MR-04","b":"MR-05","expected":"fact_to_obligation"},{"pair_id":"P03","a":"SC-01","b":"SC-02","expected":"subclass_direction"},{"pair_id":"P04","a":"SC-03","b":"SC-04","expected":"negative_subclass_direction"},{"pair_id":"P05","a":"ON-01","b":"ON-02","expected":"only_member_to_nonmember"},{"pair_id":"P06","a":"QU-01","b":"QU-02","expected":"query_quantifier_flip"},{"pair_id":"P07","a":"GR-01","b":"GR-02","expected":"group_to_member_scope"},{"pair_id":"P08","a":"RB-01","b":"RB-02","expected":"role_swap"},{"pair_id":"P09","a":"RB-01","b":"RB-03","expected":"event_polarity_flip"},{"pair_id":"P10","a":"TM-01","b":"TM-02","expected":"temporal_boundary"},{"pair_id":"P11","a":"UA-01","b":"UA-02","expected":"unknown_invariant"},{"pair_id":"P12","a":"UE-01","b":"UE-06","expected":"ontology_escape_invariant"},
]


def materialize() -> dict[str, Any]: return {"schema_version":"rc6-v1","cases":build_cases(),"mutation_pairs":MUTATION_PAIRS}

def canonical_bytes(data: dict[str, Any]) -> bytes: return (json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode()

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--output",required=True); args=p.parse_args(); data=materialize(); raw=canonical_bytes(data); out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(raw)
    print(json.dumps({"cases":len(data["cases"]),"resolved":sum(c["expected_status"]=="resolved" for c in data["cases"]),"unknown":sum(c["expected_status"]=="unknown" for c in data["cases"]),"mutation_pairs":len(MUTATION_PAIRS),"sha256":hashlib.sha256(raw).hexdigest()},sort_keys=True))

if __name__=="__main__": main()
