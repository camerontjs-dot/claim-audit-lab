"""Final frozen RC7D-D validator wrapper.

Adds one pre-cohort structural guard to validator_v3: a quantitative scope
must not be smuggled into an event subject, while a separately proposed base
population event may be authorized when its exact scoped clause is present.
"""
from __future__ import annotations
import re
from research.semantic_operator_jurisdiction_rc7d_d import validator_v3 as v3

VERSION="rc7d-d-validator-v3-final"
Q=r"(?:exactly|at\s+least|fewer\s+than)\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)|(?:\d{1,3}\s*%|[a-z]+\s+percent|a\s+(?:small\s+)?minority\s+of|a\s+majority\s+of|roughly\s+(?:half|three\s+quarters)(?:\s+of)?|two\s+thirds\s+of)"
VERB={"review":"reviewed","inspect":"inspected","approve":"approved","sign":"signed","release":"released"}

def validate_receipt(raw:str, proposal:dict)->dict:
    rec=v3.validate_receipt(raw,proposal)
    revised=[]
    for av in rec.get("atom_validations",[]):
        row=dict(av); atom=row.get("atom",{})
        if atom.get("kind")=="event":
            subj=str(atom.get("subject","")); obj=str(atom.get("object","")); pred=atom.get("predicate"); pol=atom.get("polarity")
            if re.match(rf"^(?:{Q})\b",subj,re.I):
                row["status"]="REJECTED"; row["reason"]="v3_quantitative_scope_not_participant_identity"
            elif row.get("status")!="AUTHORIZED" and pol=="positive" and pred in VERB and subj and obj:
                # Allow a base-population event only when the complete event relation is visibly
                # nested under an explicit quantitative scope in the untouched source.
                pat=rf"\b(?:{Q})\s+(?:the\s+)?{re.escape(subj)}\s+{VERB[pred]}\s+{re.escape(obj)}(?=\s*[.;]|$)"
                if re.search(pat,raw,re.I):
                    row["status"]="AUTHORIZED"; row["reason"]="v3_exact_base_event_under_quantitative_scope"
        revised.append(row)
    rec["atom_validations"]=revised
    statuses={x["status"] for x in revised}
    rec["receipt_status"]="AUTHORIZED" if revised and statuses=={"AUTHORIZED"} else ("REJECTED" if "REJECTED" in statuses else "UNRESOLVED")
    rec["validator_v3_final"]=VERSION
    return rec

def validate_output(output:dict)->dict:
    raw=output["raw_source"]; vals=[validate_receipt(raw,p) for p in output.get("receipts",[])]
    auth={}; rejected=[]; unresolved=[]
    for rec in vals:
        for av in rec.get("atom_validations",[]):
            row={"dimension":rec.get("dimension"),"operator_id":rec.get("operator_id"),**av}
            if av["status"]=="AUTHORIZED": auth.setdefault(rec["dimension"],[]).append(av["atom"])
            elif av["status"]=="REJECTED": rejected.append(row)
            else: unresolved.append(row)
    return {"raw_source":raw,"raw_source_sha256":output["raw_source_sha256"],"proposal_receipts":output.get("receipts",[]),"validation_receipts":vals,"authorized_atoms":auth,"authorized_dimensions":sorted(auth),"rejected_proposals":rejected,"unresolved_proposals":unresolved}
