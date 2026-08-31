"""RC7D-D authority validator v3.

Frozen before the held-out RC7D-D cohort. Extends validator v2 only with
predeclared generic constructions from RC7D-C evidence. Proposals remain
preserved even when rejected.
"""
from __future__ import annotations

import re
from research.semantic_operator_jurisdiction_rc7d_c import validator_v2 as v2

VERSION = "rc7d-d-validator-v3"

_VERB_SURFACE={"review":"reviewed","inspect":"inspected","approve":"approved","sign":"signed","release":"released"}

def _ok(pattern: str, raw: str) -> bool:
    return bool(re.search(pattern, raw, re.I))

def _validate_alt(raw: str, atom: dict) -> tuple[str,str] | None:
    kind=atom.get("kind")
    if kind=="exception":
        x=re.escape(str(atom.get("excluded","")))
        if x and _ok(rf"(?:\b(?:aside\s+from|bar|apart\s+from|but\s+not)\s+{x}\b|\b{x}\s+(?:excepted|excluded)\b|\b{x}\s+being\s+the\s+exception\b|\bwith\s+{x}\s+(?:left|kept)\s+out\b)",raw):
            return "AUTHORIZED","v3_explicit_exception_surface"
    elif kind=="epistemic_probability":
        val=atom.get("value")
        # Domain-word traps never establish epistemic modality.
        if _ok(r"\b(?:probability|likely|possible|chance|odds)\s+(?:notebook|file|folder|column|label|field|token|project|report)\b",raw):
            return "REJECTED","v3_non_epistemic_domain_vocabulary"
        forms={
            "possible":r"\b(?:perhaps|possibly|conceivably|there\s+(?:is|'s)\s+(?:a\s+)?(?:reasonable\s+|real\s+)?chance\s+(?:that|of))\b",
            "likely":r"\b(?:in\s+all\s+likelihood|quite\s+likely|likely)\b",
            "probable":r"\b(?:probably|in\s+all\s+probability)\b",
            "unlikely":r"\b(?:unlikely|improbably)\b",
        }.get(val)
        if forms and _ok(forms,raw): return "AUTHORIZED","v3_epistemic_modality_surface"
    elif kind=="necessary_permission_condition":
        pop=re.escape(str(atom.get("population",""))); pred=re.escape(str(atom.get("predicate","")))
        if pop and pred and (_ok(rf"\b{pop}\s+alone\s+may\s+{pred}(?=\s*[,.;]|$)",raw) or _ok(rf"\b{pred}\s+is\s+reserved\s+for\s+{pop}(?=\s*[,.;]|$)",raw)):
            return "AUTHORIZED","v3_necessary_permission_surface"
    elif kind=="explicit_permission":
        ent=re.escape(str(atom.get("entity",""))); pred=re.escape(str(atom.get("predicate",""))); val=atom.get("value")
        if val=="permitted" and _ok(rf"\b{ent}\s+has\s+permission\s+to\s+{pred}(?=\s*[,.;]|$)",raw): return "AUTHORIZED","v3_explicit_grant_surface"
        if val=="not_permitted" and _ok(rf"\b{ent}\s+lacks\s+permission\s+to\s+{pred}(?=\s*[,.;]|$)",raw): return "AUTHORIZED","v3_explicit_denial_surface"
    elif kind=="membership":
        ent=re.escape(str(atom.get("entity",""))); pop=re.escape(str(atom.get("population",""))); val=atom.get("value")
        if val=="member" and _ok(rf"\b{ent}\s+falls\s+within\s+{pop}(?=\s*[,.;]|$)",raw): return "AUTHORIZED","v3_membership_surface"
        if val=="non_member" and _ok(rf"\b{ent}\s+does\s+not\s+fall\s+within\s+{pop}(?=\s*[,.;]|$)",raw): return "AUTHORIZED","v3_nonmembership_surface"
    elif kind=="subclass":
        c=re.escape(str(atom.get("child",""))); p=re.escape(str(atom.get("parent","")))
        forms=[rf"\b{c}\s+(?:are|is)\s+(?:a\s+)?subtype\s+of\s+{p}\b",rf"\b{c}\s+(?:are|is)\s+nested\s+beneath\s+{p}\b",rf"\b{c}\s+belong\s+to\s+a\s+narrower\s+class\s+than\s+{p}\b",rf"\b{c}\s+(?:are|is)\s+contained\s+within\s+{p}\b"]
        if c and p and any(_ok(x,raw) for x in forms): return "AUTHORIZED","v3_subclass_surface"
    elif kind=="quantitative_scope":
        k=atom.get("quantitative_kind"); surf=re.escape(str(atom.get("surface","")))
        checks={"proportion":r"\b(?:roughly\s+(?:three\s+quarters|half)(?:\s+of)?|two\s+thirds\s+of)\b","minority":r"\ba\s+(?:small\s+)?minority\s+of\b","maximum_count":r"\bfewer\s+than\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b"}
        if surf and k in checks and _ok(checks[k],raw) and _ok(surf,raw): return "AUTHORIZED","v3_quantitative_surface"
    elif kind=="quantifier":
        q=atom.get("quantifier"); pop=re.escape(str(atom.get("population",""))); pred=str(atom.get("predicate",""))
        if not pop or " " not in pred: return None
        lemma,obj=pred.split(" ",1); verb=_VERB_SURFACE.get(lemma); obj=re.escape(obj)
        qforms={"every":r"(?:every\s+one|each\s+one)\s+of\s+the|(?:all|every|each)\s+of\s+the","none":r"(?:none|no)\s+of\s+the","some":r"(?:some|at\s+least\s+one)\s+of\s+the","not_every":r"not\s+(?:every|all)(?:\s+one\s+of\s+the|\s+of\s+the)?"}.get(q)
        if verb and qforms and _ok(rf"\b(?:{qforms})\s+{pop}\s+{verb}\s+{obj}(?=\s*[,.;]|\s+(?:except|excluding|other than|apart from|aside from|bar|probably|likely|unlikely|perhaps|possibly|conceivably)\b|$)",raw):
            return "AUTHORIZED","v3_quantifier_determiner_phrase"
    elif kind=="event":
        pred=atom.get("predicate"); verb=_VERB_SURFACE.get(pred); subj=re.escape(str(atom.get("subject",""))); obj=re.escape(str(atom.get("object",""))); pol=atom.get("polarity")
        if not verb or not subj or not obj: return None
        if pol=="negative" and (_ok(rf"\b{subj}\s+never\s+{verb}\s+{obj}(?=\s*[.;]|$)",raw) or _ok(rf"\bat\s+no\s+point\s+did\s+{subj}\s+{pred}\s+{obj}(?=\s*[.;]|$)",raw)):
            return "AUTHORIZED","v3_negative_role_surface"
        if pol=="positive" and _ok(rf"\b{subj}\s+{verb}\s+{obj}(?=\s*[.;]|$)",raw):
            # This supports event extraction under quantitative subjects only when the exact event clause is present.
            return "AUTHORIZED","v3_exact_event_under_scope"
    return None

def validate_receipt(raw: str, proposal: dict) -> dict:
    rec=v2.validate_receipt(raw,proposal)
    if proposal.get("status")!="CLAIMED":
        rec["validator_v3"]=VERSION; return rec
    revised=[]
    for av in rec.get("atom_validations",[]):
        row=dict(av)
        if row.get("status")!="AUTHORIZED":
            alt=_validate_alt(raw,row.get("atom",{}))
            if alt is not None:
                row["status"],row["reason"]=alt
        revised.append(row)
    rec["atom_validations"]=revised
    statuses={x["status"] for x in revised}
    rec["receipt_status"]="AUTHORIZED" if revised and statuses=={"AUTHORIZED"} else ("REJECTED" if "REJECTED" in statuses else "UNRESOLVED")
    rec["validator_v3"]=VERSION
    return rec

def validate_output(output: dict) -> dict:
    raw=output["raw_source"]; vals=[validate_receipt(raw,p) for p in output.get("receipts",[])]
    auth={}; rejected=[]; unresolved=[]
    for rec in vals:
        for av in rec.get("atom_validations",[]):
            row={"dimension":rec.get("dimension"),"operator_id":rec.get("operator_id"),**av}
            if av["status"]=="AUTHORIZED": auth.setdefault(rec["dimension"],[]).append(av["atom"])
            elif av["status"]=="REJECTED": rejected.append(row)
            else: unresolved.append(row)
    return {"raw_source":raw,"raw_source_sha256":output["raw_source_sha256"],"proposal_receipts":output.get("receipts",[]),"validation_receipts":vals,"authorized_atoms":auth,"authorized_dimensions":sorted(auth),"rejected_proposals":rejected,"unresolved_proposals":unresolved}
