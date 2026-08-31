"""RC7D-C evaluator with frozen semantic-equivalence scoring."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from collections import defaultdict

from research.semantic_operator_jurisdiction_rc7d import candidate
from research.semantic_operator_jurisdiction_rc7d_c import equivalence, validator_v2
from research.semantic_operator_jurisdiction_rc7d_c.cohort import CASES

EXPECTED = 68
assert len(CASES) == EXPECTED


def canon(atom: dict) -> str:
    return json.dumps(equivalence.canonical_atom(atom), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def proposed_atoms(output: dict) -> dict[str, list[dict]]:
    d: dict[str, list[dict]] = defaultdict(list)
    for r in output.get("receipts", []):
        if r.get("status") == "CLAIMED":
            d[r["dimension"]].extend(r.get("atoms", []))
    return dict(d)


def score(case: dict, atoms: dict[str, list[dict]]) -> dict:
    gold = {d: {canon(a) for a in xs} for d,xs in case["gold"].items()}
    pred = {d: {canon(a) for a in xs} for d,xs in atoms.items()}
    gd, pd = set(gold), set(pred)
    unsafe_rows=[]
    correct=missing=unsafe=0
    for d in sorted(gd|pd):
        gs, ps = gold.get(d,set()), pred.get(d,set())
        correct += len(gs & ps)
        missing += len(gs - ps)
        unsafe += len(ps - gs)
        for item in sorted(ps-gs):
            unsafe_rows.append({"dimension":d,"normalized_predicted":json.loads(item),"normalized_gold":[json.loads(x) for x in sorted(gs)]})
    return {
        "gold_dimensions":sorted(gd),
        "predicted_dimensions":sorted(pd),
        "correct_dimensions":len(gd&pd),
        "false_dimensions":sorted(pd-gd),
        "missing_dimensions":sorted(gd-pd),
        "gold_atom_count":sum(len(x) for x in gold.values()),
        "pred_atom_count":sum(len(x) for x in pred.values()),
        "correct_atom_count":correct,
        "missing_atom_count":missing,
        "unsafe_atom_count":unsafe,
        "unsafe_rows":unsafe_rows,
    }


def aggregate(rows: list[dict], key: str) -> dict:
    gd=sum(len(r[key]["gold_dimensions"]) for r in rows)
    pd=sum(len(r[key]["predicted_dimensions"]) for r in rows)
    cd=sum(r[key]["correct_dimensions"] for r in rows)
    fd=sum(len(r[key]["false_dimensions"]) for r in rows)
    ga=sum(r[key]["gold_atom_count"] for r in rows)
    pa=sum(r[key]["pred_atom_count"] for r in rows)
    ca=sum(r[key]["correct_atom_count"] for r in rows)
    ua=sum(r[key]["unsafe_atom_count"] for r in rows)
    mixed=[r for r in rows if len(r[key]["gold_dimensions"])>1]
    mg=sum(len(r[key]["gold_dimensions"]) for r in mixed)
    mc=sum(r[key]["correct_dimensions"] for r in mixed)
    return {
        "case_count":len(rows),
        "semantic_dimension_recall":cd/gd if gd else 1.0,
        "dimension_precision":(pd-fd)/pd if pd else 1.0,
        "false_dimension_count":fd,
        "typed_atom_recall":ca/ga if ga else 1.0,
        "typed_atom_precision":(pa-ua)/pa if pa else 1.0,
        "unsafe_atom_count":ua,
        "unsafe_case_rate":sum(r[key]["unsafe_atom_count"]>0 for r in rows)/len(rows),
        "mixed_semantic_dimension_recall":mc/mg if mg else 1.0,
        "mixed_correct_dimensions":mc,
        "mixed_gold_dimensions":mg,
    }


def lane(kind: str, bank_size: int=8):
    rows=[]
    for c in CASES:
        out = candidate.broadcast_all(c["text"], bank_size=bank_size) if kind=="broadcast" else candidate.single_router(c["text"])
        assert out["raw_source"]==c["text"]
        assert out["raw_source_sha256"]==hashlib.sha256(c["text"].encode()).hexdigest()
        gate=validator_v2.validate_architecture_output(out)
        prop=score(c,proposed_atoms(out))
        auth=score(c,gate["authorized_atoms"])
        rows.append({
            "case_id":c["case_id"],"group":c["group"],"raw_source":c["text"],
            "proposed":prop,"authorized":auth,
            "rejected_count":len(gate["rejected_proposals"]),
            "unresolved_count":len(gate["unresolved_proposals"]),
            "gate":gate,
        })
    return {"proposal":aggregate(rows,"proposed"),"authorized":aggregate(rows,"authorized"),"rows":rows}


def composition_oracle():
    total=correct=0; errors=[]
    for c in CASES:
        for row in c.get("composition",[]):
            total+=1
            observed=candidate._PAIR_RULES.get(frozenset(row["dimensions"]),"unresolved")
            if observed==row["expected"]: correct+=1
            else: errors.append({"case_id":c["case_id"],"expected":row,"observed":observed})
    return {"count":total,"correct":correct,"accuracy":correct/total if total else 1.0,"errors":errors}


def ceiling():
    mixed=[c for c in CASES if len(c["gold_dimensions"])>1]
    total=sum(len(c["gold_dimensions"]) for c in mixed)
    single=len(mixed)
    return {"mixed_cases":len(mixed),"gold_dimensions":total,"single_family_retained":single,"multi_operator_retained":total,"single_retention":single/total if total else 1.0,"multi_retention":1.0}


def qdiag():
    rows=[]
    for c in CASES:
        if "quantifier" not in c["gold"]: continue
        out=candidate.broadcast_all(c["text"])
        qa=out["quantifier_audit"]
        gold={canon(a) for a in c["gold"]["quantifier"]}
        def aset(r): return {canon(a) for a in r.get("atoms",[])} if r.get("status")=="CLAIMED" else set()
        p,a=aset(qa["primary"]),aset(qa["audit"])
        rows.append({"case_id":c["case_id"],"agreement":qa["agreement"],"primary_exact":p==gold,"audit_exact":a==gold,"both_correct":p==gold and a==gold})
    agree=[r for r in rows if r["agreement"] is True]; disagree=[r for r in rows if r["agreement"] is False]
    return {
        "case_count":len(rows),"agreement_count":len(agree),"disagreement_count":len(disagree),
        "error_rate_when_agree":sum(not r["both_correct"] for r in agree)/len(agree) if agree else None,
        "error_rate_when_disagree":sum(not r["both_correct"] for r in disagree)/len(disagree) if disagree else None,
        "agreement_only_unsafe_count":sum(not r["both_correct"] for r in agree),
        "rows":rows,
    }


def stress():
    ans=[]
    for n in (2,4,6,8):
        x=lane("broadcast",n)
        ans.append({"bank_size":n,"proposal":x["proposal"],"authorized":x["authorized"]})
    return ans


def group_metrics(rows, key):
    result={}
    for g in sorted({c["group"] for c in CASES}):
        subset=[r for r in rows if r["group"]==g]
        result[g]=aggregate(subset,key)
    return result


def state(b,s,comp,ceil,st):
    bp=b["proposal"]; ba=b["authorized"]; sa=s["authorized"]
    if comp["accuracy"]<1.0: return "COMPOSITION_DEFECT"
    if ba["unsafe_atom_count"]>0 or ba["false_dimension_count"]>0: return "AUTHORITY_VALIDATOR_STILL_UNSAFE"
    if bp["dimension_precision"]<0.97: return "SPECIALIST_DISCOVERY_OVERCLAIMS"
    if bp["semantic_dimension_recall"]<0.80: return "SPECIALIST_DISCOVERY_TOO_WEAK"
    if ba["semantic_dimension_recall"]<0.65: return "AUTHORITY_VALIDATOR_TOO_LOSSY"
    if not all(x["authorized"]["unsafe_case_rate"]==0 for x in st): return "AUTHORITY_VALIDATOR_STILL_UNSAFE"
    if ba["mixed_correct_dimensions"]<=sa["mixed_correct_dimensions"]: return "AUTHORITY_VALIDATOR_TOO_LOSSY"
    if ceil["multi_operator_retained"]<=ceil["single_family_retained"]: return "APPARATUS_INVALID"
    return "PROPOSAL_AUTHORITY_ARCHITECTURE_SUPPORTED_WITH_BOUNDS"


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",required=True); args=ap.parse_args()
    outdir=Path(args.output_dir); outdir.mkdir(parents=True,exist_ok=True)
    b=lane("broadcast"); s=lane("single"); comp=composition_oracle(); ceil=ceiling(); q=qdiag(); st=stress()
    terminal=state(b,s,comp,ceil,st)
    results={
        "scientific_state":terminal,
        "claim_boundary":{"context_free":False,"llm_used":False,"production_authorization":False},
        "case_count":len(CASES),
        "semantic_equivalence_version":equivalence.VERSION,
        "validator_version":validator_v2.VERSION,
        "broadcast":{"proposal":b["proposal"],"authorized":b["authorized"]},
        "single_router":{"proposal":s["proposal"],"authorized":s["authorized"]},
        "composition_oracle":comp,
        "routing_ceiling":ceil,
        "quantifier_duplicate":q,
        "operator_count_stress":[{"bank_size":x["bank_size"],"proposal":x["proposal"],"authorized":x["authorized"]} for x in st],
        "group_metrics":{"broadcast_proposal":group_metrics(b["rows"],"proposed"),"broadcast_authorized":group_metrics(b["rows"],"authorized")},
    }
    counter=[]
    for r in b["rows"]:
        if r["authorized"]["unsafe_atom_count"] or r["authorized"]["false_dimensions"] or r["authorized"]["missing_dimensions"]:
            counter.append({"case_id":r["case_id"],"group":r["group"],"raw_source":r["raw_source"],"proposal":r["proposed"],"authorized":r["authorized"],"rejected_count":r["rejected_count"]})
    (outdir/"RESULTS.json").write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
    (outdir/"BROADCAST_ROWS.json").write_text(json.dumps(b["rows"],indent=2,sort_keys=True)+"\n")
    (outdir/"SINGLE_ROWS.json").write_text(json.dumps(s["rows"],indent=2,sort_keys=True)+"\n")
    (outdir/"COUNTEREXAMPLES.json").write_text(json.dumps(counter,indent=2,sort_keys=True)+"\n")
    (outdir/"STRESS.json").write_text(json.dumps(st,indent=2,sort_keys=True)+"\n")
    report=f'''# RC7D-C Semantic Equivalence and Authority Retest\n\nScientific state: **`{terminal}`**\n\nNo LLM or learned router was used.\n\n## Broadcast proposals\n- semantic dimension recall: {b["proposal"]["semantic_dimension_recall"]:.3f}\n- dimension precision: {b["proposal"]["dimension_precision"]:.3f}\n- typed atom precision after semantic normalization: {b["proposal"]["typed_atom_precision"]:.3f}\n\n## Broadcast authorized\n- semantic dimension recall: {b["authorized"]["semantic_dimension_recall"]:.3f}\n- typed atom recall: {b["authorized"]["typed_atom_recall"]:.3f}\n- typed atom precision: {b["authorized"]["typed_atom_precision"]:.3f}\n- unsafe atoms: {b["authorized"]["unsafe_atom_count"]}\n- false authorized dimensions: {b["authorized"]["false_dimension_count"]}\n- mixed-semantic retention: {b["authorized"]["mixed_semantic_dimension_recall"]:.3f}\n\n## Validated single routing\n- semantic dimension recall: {s["authorized"]["semantic_dimension_recall"]:.3f}\n- mixed-semantic retention: {s["authorized"]["mixed_semantic_dimension_recall"]:.3f}\n- unsafe atoms: {s["authorized"]["unsafe_atom_count"]}\n\n## Oracle ceilings\n- perfect exclusive single-family: {ceil["single_family_retained"]}/{ceil["gold_dimensions"]}\n- perfect multi-operator: {ceil["multi_operator_retained"]}/{ceil["gold_dimensions"]}\n- oracle composition accuracy: {comp["accuracy"]:.3f}\n\n## Quantifier duplicate\n- agreement cases: {q["agreement_count"]}\n- disagreement cases: {q["disagreement_count"]}\n- error when agree: {q["error_rate_when_agree"]}\n- error when disagree: {q["error_rate_when_disagree"]}\n\n## Boundary\nPost-reveal bounded hardening only. No production authorization or independent-consumability claim.\n'''
    (outdir/"REPORT.md").write_text(report)
    print(json.dumps(results,indent=2,sort_keys=True))

if __name__=="__main__": main()
