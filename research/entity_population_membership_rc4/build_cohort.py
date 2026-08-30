"""Build the frozen RC4 entity/population scope and membership cohort."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

EXPECTED_SHA256 = "c34aa64fe2a4ffad3eae6396cfd0f4ac400009065d0c7296229d15573e85200b"
LABELS = ("entailment", "neutral", "contradiction")


def case(cid, family, premise, hypothesis, target, rationale, *, critical=None, primary=True, semantic=None, tags=None):
    return {
        "case_id": cid,
        "family": family,
        "premise": premise,
        "hypothesis": hypothesis,
        "target": target,
        "semantic_rationale": rationale,
        "critical_error_type": critical,
        "primary": primary,
        "semantic": semantic or {},
        "tags": tags or [],
    }


def triad(prefix, family, premise, ent, neu, con, sem, *, neutral_critical=None, contradiction_critical=None):
    return [
        case(prefix+"E", family, premise, ent[0], "entailment", ent[1], semantic=sem),
        case(prefix+"N", family, premise, neu[0], "neutral", neu[1], critical=neutral_critical, semantic=sem),
        case(prefix+"C", family, premise, con[0], "contradiction", con[1], critical=contradiction_critical, semantic=sem),
    ]


def primary_cases():
    out=[]
    seeds=[
      ("A01","Every batch inspector must file Form A before release. Mira is a batch inspector.","Mira must file Form A before release.","Mira filed Form A yesterday.","Mira is outside the population governed by the Form A requirement.","Mira","batch inspector","file Form A before release"),
      ("A02","All laboratory couriers must wear badge Q in the sterile corridor. Tessa is a laboratory courier.","Tessa must wear badge Q in the sterile corridor.","Tessa wore badge Q last Tuesday.","Tessa is not governed by the badge-Q corridor rule.","Tessa","laboratory courier","wear badge Q in the sterile corridor"),
      ("A03","Each archive clerk must index closed files in Register C. Omar is an archive clerk.","Omar must index closed files in Register C.","Omar enjoys working with Register C.","Omar is outside the class governed by the Register-C indexing rule.","Omar","archive clerk","index closed files in Register C"),
      ("A04","Every release reviewer must countersign the final checklist. Vela is a release reviewer.","Vela must countersign the final checklist.","Vela countersigned a checklist last month.","The final-checklist countersignature rule does not apply to Vela.","Vela","release reviewer","countersign the final checklist"),
    ]
    for p,pr,e,n,c,ent,cls,pred in seeds:
        out += triad(p,"direct_membership_rule",pr,(e,"Known class membership inherits the universal obligation."),(n,"An obligation does not establish that the behavior occurred."),(c,"Known membership conflicts with a claim that the governing class rule does not apply."),{"memberships":[[ent,cls,"member"]],"quantifier":"all","predicate":pred,"modality":"obligation"}, contradiction_critical="member_to_nonmember")

    subclass_seeds=[
      ("B01","Every sterile-room worker must wear badge Q. All aseptic couriers are sterile-room workers. Lio is an aseptic courier.","Lio must wear badge Q.","All sterile-room workers are aseptic couriers.","Lio is outside the population of sterile-room workers.","Lio","aseptic courier","sterile-room worker","wear badge Q"),
      ("B02","All controlled-area staff must complete annual fit testing. Every isolator technician is controlled-area staff. Bea is an isolator technician.","Bea must complete annual fit testing.","Every controlled-area staff member is an isolator technician.","Bea is not governed by the annual fit-testing requirement.","Bea","isolator technician","controlled-area staff","complete annual fit testing"),
      ("B03","Each trained reviewer must sign the disposition record. All senior auditors are trained reviewers. Neri is a senior auditor.","Neri must sign the disposition record.","All trained reviewers are senior auditors.","Neri is outside the trained-reviewer class.","Neri","senior auditor","trained reviewer","sign the disposition record"),
      ("B04","Every cold-chain operator must record probe calibration. All vaccine couriers are cold-chain operators. Sumi is a vaccine courier.","Sumi must record probe calibration.","Every cold-chain operator is a vaccine courier.","The probe-calibration rule does not apply to Sumi.","Sumi","vaccine courier","cold-chain operator","record probe calibration"),
    ]
    for p,pr,e,n,c,ent,sub,sup,pred in subclass_seeds:
        out += triad(p,"subclass_inheritance",pr,(e,"Membership in the subclass plus subclass inclusion licenses inheritance."),(n,"Subclass inclusion is directional and does not license reversing the class relation."),(c,"The inherited superclass membership conflicts with exclusion from the governing class."),{"memberships":[[ent,sub,"member"]],"subclass":[[sub,sup]],"quantifier":"all","predicate":pred,"modality":"obligation"}, neutral_critical="subclass_reversal", contradiction_critical="member_to_nonmember")

    only_seeds=[
      ("C01","Only licensed inspectors may release lots. Niko is a licensed inspector. Pia is not a licensed inspector.","Pia may not release lots.","Niko may release lots.","Pia may release lots.","licensed inspectors","release lots","Niko","Pia"),
      ("C02","Only trained pharmacists may approve sterile formulas. Eren is a trained pharmacist. Kato is not a trained pharmacist.","Kato may not approve sterile formulas.","Eren may approve sterile formulas.","Kato may approve sterile formulas.","trained pharmacists","approve sterile formulas","Eren","Kato"),
      ("C03","Only badge-Q supervisors may unlock the vault. Mara is a badge-Q supervisor. Ivo is not a badge-Q supervisor.","Ivo may not unlock the vault.","Mara may unlock the vault.","Ivo may unlock the vault.","badge-Q supervisors","unlock the vault","Mara","Ivo"),
      ("C04","Only certified dispatchers may authorize emergency routing. Taro is a certified dispatcher. Una is not a certified dispatcher.","Una may not authorize emergency routing.","Taro may authorize emergency routing.","Una may authorize emergency routing.","certified dispatchers","authorize emergency routing","Taro","Una"),
    ]
    for p,pr,e,n,c,cls,act,member,nonmember in only_seeds:
        out += triad(p,"only_necessary_condition",pr,(e,"Only-class permission excludes a known non-member."),(n,"Only supplies a necessary class condition; membership alone is not sufficient permission."),(c,"Known non-membership conflicts with permission under an only-class rule."),{"memberships":[[member,cls,"member"],[nonmember,cls,"nonmember"]],"quantifier":"only","predicate":act,"modality":"permission","necessary_condition":cls,"sufficient_condition":"unknown"}, neutral_critical="only_necessary_to_sufficient", contradiction_critical="nonmember_to_member")

    quantifier_rows=[
      ("D01","Some field auditors carry a red card.","At least one field auditor carries a red card.","Every field auditor carries a red card.","No field auditors carry a red card.","some","field auditors","carry a red card","some_to_all"),
      ("D02","No archive clerks use the orange ledger.","Every archive clerk does not use the orange ledger.","Some records are stored in the orange ledger.","At least one archive clerk uses the orange ledger.","none","archive clerks","use the orange ledger","none_to_some"),
      ("D03","Not every laboratory courier uses pouch B.","At least one laboratory courier does not use pouch B.","Most laboratory couriers do not use pouch B.","Every laboratory courier uses pouch B.","not_every","laboratory couriers","use pouch B","not_every_to_every"),
      ("D04","Every release analyst signs Form R.","All release analysts sign Form R.","At least one named release analyst is Mira.","Some release analyst does not sign Form R.","every","release analysts","sign Form R","every_to_some_not"),
    ]
    for p,pr,e,n,c,q,pop,pred,crit in quantifier_rows:
        out += triad(p,"quantifier_scope",pr,(e,"The hypothesis is a licensed logical restatement of the frozen quantifier."),(n,"The premise does not establish the stronger/different population claim."),(c,"The hypothesis is incompatible with the stated population quantifier."),{"population":pop,"quantifier":q,"predicate":pred,"modality":"fact"}, neutral_critical=("some_to_all" if q=="some" else None), contradiction_critical=crit)

    group_rows=[
      ("E01","The Delta review team submitted the incident report. Rhea is a member of the Delta review team.","The incident report was submitted by the Delta review team.","Rhea submitted the incident report.","The Delta review team did not submit the incident report.","Delta review team","Rhea","submitted the incident report"),
      ("E02","The North shift committee approved the revised roster. Sol is a member of the North shift committee.","The revised roster was approved by the North shift committee.","Sol approved the revised roster.","The North shift committee did not approve the revised roster.","North shift committee","Sol","approved the revised roster"),
      ("E03","The calibration panel selected probe 7. Bea is a member of the calibration panel.","Probe 7 was selected by the calibration panel.","Bea selected probe 7.","The calibration panel did not select probe 7.","calibration panel","Bea","selected probe 7"),
      ("E04","The response unit issued the evacuation notice. Ivo is a member of the response unit.","The evacuation notice was issued by the response unit.","Ivo issued the evacuation notice.","The response unit did not issue the evacuation notice.","response unit","Ivo","issued the evacuation notice"),
    ]
    for p,pr,e,n,c,grp,member,pred in group_rows:
        out += triad(p,"group_vs_member",pr,(e,"The group-level predicate is preserved by passive paraphrase."),(n,"A group-level act does not identify every or any particular member as the actor."),(c,"Explicit negation contradicts the asserted group-level act."),{"memberships":[[member,grp,"member"]],"population":grp,"quantifier":"group_entity","predicate":pred,"scope":"group"}, neutral_critical="group_to_every_member")

    role_rows=[
      ("F01","Rhea approved Sol's request.","Rhea is the approver of Sol's request.","Sol approved Rhea's request.","Rhea did not approve Sol's request.",["Rhea","approver"],["Sol","request_owner"],"approve"),
      ("F02","Mara assigned the deviation ticket to Ivo.","Ivo is the assignee of the deviation ticket.","Ivo assigned the deviation ticket to Mara.","Mara did not assign the deviation ticket to Ivo.",["Mara","assigner"],["Ivo","assignee"],"assign"),
      ("F03","Tessa reviewed Omar's batch record.","Tessa is the reviewer of Omar's batch record.","Omar reviewed Tessa's batch record.","Tessa did not review Omar's batch record.",["Tessa","reviewer"],["Omar","record_owner"],"review"),
      ("F04","Neri sent the calibration file to Bea.","Bea is the recipient of the calibration file sent by Neri.","Bea sent the calibration file to Neri.","Neri did not send the calibration file to Bea.",["Neri","sender"],["Bea","recipient"],"send"),
    ]
    for p,pr,e,n,c,r1,r2,pred in role_rows:
        out += triad(p,"role_binding",pr,(e,"The hypothesis preserves the predicate's argument roles."),(n,"Swapping subject/object or actor/recipient is not licensed by the original relation."),(c,"The hypothesis directly negates the asserted role-bound event."),{"roles":[r1,r2],"predicate":pred,"scope":"event"}, neutral_critical="role_swap")

    temporal_rows=[
      ("G01","Juno is not an audit-team member before June 1. From June 1 onward, Juno is an audit-team member. Every audit-team member must use Form R.","On June 10, Juno must use Form R.","On May 20, Juno uses Form R.","On May 20, Juno is governed by the audit-team Form-R requirement.","Juno","audit-team member","June 1","use Form R","enter"),
      ("G02","Kira is a vault-reviewer through August 31. From September 1 onward, Kira is not a vault-reviewer. Every vault-reviewer must countersign Log V.","On August 20, Kira must countersign Log V.","On September 10, Kira countersigns Log V.","On September 10, Kira is governed by the vault-reviewer countersignature rule.","Kira","vault-reviewer","September 1","countersign Log V","leave"),
      ("G03","Oren is not a cold-chain operator before day 30. From day 30 onward, Oren is a cold-chain operator. All cold-chain operators must record probe checks.","On day 45, Oren must record probe checks.","On day 10, Oren records probe checks.","On day 10, the cold-chain operator rule applies to Oren.","Oren","cold-chain operator","day 30","record probe checks","enter"),
      ("G04","Vela is a release reviewer through day 60. After day 60, Vela is not a release reviewer. Every release reviewer must sign Form D.","On day 40, Vela must sign Form D.","On day 75, Vela signs Form D.","On day 75, Vela remains governed by the release-reviewer Form-D rule.","Vela","release reviewer","day 60","sign Form D","leave"),
    ]
    for p,pr,e,n,c,ent,cls,bound,pred,direction in temporal_rows:
        out += triad(p,"temporal_membership",pr,(e,"The queried time lies inside explicit class membership, so the class rule applies."),(n,"Outside class membership, actual behavior remains unspecified rather than prohibited."),(c,"The queried time lies outside explicit class membership, so class-rule applicability is contradicted."),{"entity":ent,"class":cls,"boundary":bound,"direction":direction,"predicate":pred,"modality":"obligation"}, neutral_critical="membership_absence_not_behavior", contradiction_critical="temporal_membership_scope")
    return out


def mutation_cases():
    rows=[]; pairs=[]
    def add(pid, transformation, before, after, expected_before, expected_after):
        b=dict(before); a=dict(after)
        b["case_id"]=f"RC4-M{pid}A"; a["case_id"]=f"RC4-M{pid}B"; b["primary"]=False; a["primary"]=False
        rows.extend([b,a]); pairs.append({"pair_id":f"M{pid}","before":b["case_id"],"after":a["case_id"],"transformation":transformation,"expected_before":expected_before,"expected_after":expected_after})
    def m(fam,p,h,t,r,crit=None): return case("",fam,p,h,t,r,critical=crit,primary=False)
    add("01","add_explicit_membership",m("mutation","Every inspector must file Form A.","Mira must file Form A.","neutral","No membership fact."),m("mutation","Every inspector must file Form A. Mira is an inspector.","Mira must file Form A.","entailment","Membership added."),"neutral","entailment")
    add("02","membership_true_to_false",m("mutation","Every inspector must file Form A. Mira is an inspector.","Mira must file Form A.","entailment","Member."),m("mutation","Every inspector must file Form A. Mira is not an inspector.","Mira must file Form A.","neutral","Known nonmembership means this class rule does not impose the obligation."),"entailment","neutral")
    add("03","subclass_direction_reverse",m("mutation","All couriers are controlled-area staff. Mira is a courier.","Mira is controlled-area staff.","entailment","Forward subclass inheritance."),m("mutation","All controlled-area staff are couriers. Mira is a courier.","Mira is controlled-area staff.","neutral","Reverse implication is not licensed."),"entailment","neutral")
    add("04","some_to_all",m("mutation","Some auditors carry red cards.","Every auditor carries a red card.","neutral","Existential does not imply universal.","some_to_all"),m("mutation","Every auditor carries a red card.","Every auditor carries a red card.","entailment","Universal explicit."),"neutral","entailment")
    add("05","only_member_to_nonmember",m("mutation","Only licensed inspectors may release lots. Niko is a licensed inspector.","Niko may release lots.","neutral","Only is necessary not sufficient.","only_necessary_to_sufficient"),m("mutation","Only licensed inspectors may release lots. Niko is not a licensed inspector.","Niko may release lots.","contradiction","Known nonmember violates necessary condition.","nonmember_to_member"),"neutral","contradiction")
    add("06","group_to_member",m("mutation","The Delta team submitted the report. Rhea is a Delta-team member.","Rhea submitted the report.","neutral","Group act does not identify member.","group_to_every_member"),m("mutation","The Delta team submitted the report. Rhea is a Delta-team member. Rhea submitted the report.","Rhea submitted the report.","entailment","Member act added explicitly."),"neutral","entailment")
    add("07","role_swap",m("mutation","Rhea approved Sol's request.","Sol approved Rhea's request.","neutral","Swapped roles unsupported.","role_swap"),m("mutation","Sol approved Rhea's request.","Sol approved Rhea's request.","entailment","Swapped event is now explicit."),"neutral","entailment")
    add("08","temporal_boundary",m("mutation","Juno is not an audit-team member before June 1. From June 1 onward, Juno is an audit-team member. All audit-team members must use Form R.","On May 20, Juno is governed by the Form-R rule.","contradiction","Outside membership window."),m("mutation","Juno is not an audit-team member before June 1. From June 1 onward, Juno is an audit-team member. All audit-team members must use Form R.","On June 20, Juno is governed by the Form-R rule.","entailment","Inside membership window."),"contradiction","entailment")
    add("09","entity_swap_invariant",m("mutation","Every analyst must sign Form R. Mira is an analyst.","Mira must sign Form R.","entailment","Member inherits rule."),m("mutation","Every analyst must sign Form R. Taro is an analyst.","Taro must sign Form R.","entailment","Entity renaming should preserve logic."),"entailment","entailment")
    add("10","clause_movement_invariant",m("mutation","Every analyst must sign Form R. Mira is an analyst.","Mira must sign Form R.","entailment","Canonical order."),m("mutation","Mira is an analyst. Form R must be signed by every analyst.","Mira must sign Form R.","entailment","Equivalent clause movement/passive form."),"entailment","entailment")
    return rows,pairs


def ambiguous_cases():
    amb=[
      ("AMB01","Alex told Jordan that they must sign Form A.","Alex must sign Form A.","Pronoun attachment is underdetermined."),
      ("AMB02","The reviewers told the couriers that they were exempt.","The reviewers were exempt.","Plural pronoun attachment is underdetermined."),
      ("AMB03","Only managers who reviewed the file may approve it. Mira is a manager.","Mira may approve the file.","Whether Mira reviewed the file is unstated."),
      ("AMB04","A member of Team Delta signed the report. Rhea is a Team Delta member.","Rhea signed the report.","Existential member is not identified."),
      ("AMB05","Most auditors use badge Q.","Mira uses badge Q.","No membership/individual witness licenses a unique relation."),
      ("AMB06","The committee approved the plan through its chair.","The chair personally approved the plan.","Institutional act versus personal act is not uniquely specified."),
    ]
    return [case("RC4-"+cid,"evaluator_ambiguous",p,h,None,r,primary=False,semantic={"unknown":"evaluator_ambiguous"}) for cid,p,h,r in amb]


def build():
    primary=primary_cases(); mutations,pairs=mutation_cases(); ambiguous=ambiguous_cases()
    return {"experiment":"entity_population_membership_rc4","version":"rc4","cases":primary+mutations+ambiguous,"mutation_pairs":pairs,"authority":"research_only","primary_target_labels":list(LABELS)}


def canonical_bytes(data):
    return (json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode()


def validate(data):
    problems=[]; cases=data["cases"]; primary=[c for c in cases if c["primary"] is True]
    if len(primary)!=84: problems.append(f"expected 84 primary, got {len(primary)}")
    fams=sorted(set(c["family"] for c in primary))
    if len(fams)!=7: problems.append(f"expected 7 primary families, got {fams}")
    for fam in fams:
        subset=[c for c in primary if c["family"]==fam]
        counts={l:sum(c["target"]==l for c in subset) for l in LABELS}
        if len(subset)!=12 or set(counts.values())!={4}: problems.append(f"{fam}: bad balance {counts}")
    totals={l:sum(c["target"]==l for c in primary) for l in LABELS}
    if len(set(totals.values()))!=1: problems.append(f"overall target imbalance {totals}")
    ids=[c["case_id"] for c in cases]
    if len(ids)!=len(set(ids)): problems.append("duplicate case ids")
    muts=[c for c in cases if c["family"]=="mutation"]
    if len(muts)!=20 or len(data["mutation_pairs"])!=10: problems.append("mutation partition mismatch")
    amb=[c for c in cases if c["target"] is None]
    if len(amb)!=6: problems.append("ambiguous partition mismatch")
    return problems


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,required=True); args=ap.parse_args()
    data=build(); problems=validate(data)
    if problems: raise RuntimeError("; ".join(problems))
    raw=canonical_bytes(data); sha=hashlib.sha256(raw).hexdigest()
    if sha!=EXPECTED_SHA256: raise RuntimeError(f"cohort sha mismatch {sha}")
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_bytes(raw)
    print(json.dumps({"cases":len(data["cases"]),"primary":84,"mutation_pairs":10,"ambiguous":6,"cohort_sha256":sha},sort_keys=True))
if __name__=="__main__": main()
