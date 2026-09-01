"""Evaluator for RC7F-B comparison measurement."""
from __future__ import annotations
import re
from collections import Counter, defaultdict


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())


def key(atom: dict) -> tuple[str,str,str]:
    return (norm(atom["left"]), str(atom["relation"]).upper(), norm(atom["right"]))


def validate_cohort(cases: list[dict]) -> None:
    seen={}
    for c in cases:
        src=norm(c["raw_source"])
        gold=key(c["gold"]) if c.get("gold") else None
        if src in seen and seen[src] != gold:
            raise ValueError(f"incompatible_gold_for_duplicate_source:{src!r}")
        seen[src]=gold


def score(cases: list[dict], outputs: dict[str,dict]) -> dict:
    validate_cohort(cases)
    tp=fp=fn=resolved=direction_ok=attachment_ok=delta_total=delta_ok=0
    by_family=defaultdict(Counter)
    rows=[]
    for c in cases:
        gold=c.get("gold")
        proposals=outputs[c["case_id"]].get("proposals",[])
        proposal=proposals[0] if proposals else None
        fam=c["family"]; by_family[fam]["total"]+=1
        if proposal: resolved+=1
        exact=False
        if gold and proposal:
            g=key(gold); p=key(proposal)
            direction_ok += int(g[1]==p[1])
            attachment_ok += int(g[0]==p[0] and g[2]==p[2])
            exact=(g==p)
            if exact: tp+=1; by_family[fam]["tp"]+=1
            else: fp+=1; fn+=1; by_family[fam]["wrong"]+=1
            if gold.get("delta_surface") is not None:
                delta_total+=1
                if norm(gold["delta_surface"])==norm(proposal.get("delta_surface")):
                    delta_ok+=1
        elif gold and not proposal:
            fn+=1; by_family[fam]["miss"]+=1
        elif not gold and proposal:
            fp+=1; by_family[fam]["false_proposal"]+=1
        else:
            by_family[fam]["safe_negative"]+=1
        rows.append({"case_id":c["case_id"],"family":fam,"gold":gold,"proposal":proposal,"exact":exact})
    precision=tp/(tp+fp) if tp+fp else 1.0
    recall=tp/(tp+fn) if tp+fn else 1.0
    return {
        "case_count":len(cases),"tp":tp,"fp":fp,"fn":fn,
        "typed_precision":precision,"typed_recall":recall,
        "resolved_count":resolved,
        "direction_accuracy_resolved_gold":direction_ok/max(1,sum(1 for c in cases if c.get('gold') and outputs[c['case_id']].get('proposals'))),
        "attachment_accuracy_resolved_gold":attachment_ok/max(1,sum(1 for c in cases if c.get('gold') and outputs[c['case_id']].get('proposals'))),
        "delta_accuracy":delta_ok/delta_total if delta_total else 1.0,
        "false_proposals_on_negative":sum(v.get("false_proposal",0) for v in by_family.values()),
        "unresolved_count":sum(1 for c in cases if outputs[c['case_id']].get('status')=='UNRESOLVED'),
        "by_family":{k:dict(v) for k,v in sorted(by_family.items())},
        "rows":rows,
    }
