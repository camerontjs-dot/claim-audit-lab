"""RC7D-D deterministic multi-reader evaluator.

Frozen after the held-out cohort and before scientific execution. The evaluator
compares proposal discovery, separately validated authority, agreement-only
behavior, reader-count stress, and oracle composition.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

from research.semantic_operator_jurisdiction_rc7d_c.equivalence import canonical_atom
from research.semantic_operator_jurisdiction_rc7d_d import cohort_final as cohort
from research.semantic_operator_jurisdiction_rc7d_d import multi_readers as readers
from research.semantic_operator_jurisdiction_rc7d_d import role_reader_v2
from research.semantic_operator_jurisdiction_rc7d_d import validator_v3_final as validator

PREREG="b2573ed031109215622796287312ee7699270363"
CANDIDATE_FREEZE="300efc0ef3961f7d8dcc0ad651f4faf060377793"
COHORT_FREEZE="ae11de6da6a7346e6cf2d9dbfbfd3d636676156a"

def key(atom:dict)->str:
    return json.dumps(canonical_atom(atom),sort_keys=True,separators=(",",":"))

def gold_sets(case):
    return {d:{key(a) for a in atoms} for d,atoms in case["gold"].items()}

def output_for(text:str,multi:bool,extra_limit:int|None=None):
    if not multi:
        return readers.run_single(text)
    base=readers.run_single(text)
    extras=[fn(text) for fn in readers.ALT_READERS.values()]+[role_reader_v2.read(text)]
    if extra_limit is not None: extras=extras[:extra_limit]
    base["receipts"].extend(extras)
    return base

def proposal_sets(output):
    out={}
    for r in output["receipts"]:
        if r.get("status")!="CLAIMED": continue
        for a in r.get("atoms",[]): out.setdefault(r["dimension"],set()).add(key(a))
    return out

def authorized_sets(validated):
    return {d:{key(a) for a in atoms} for d,atoms in validated["authorized_atoms"].items()}

def metric_from_sets(cases,sets_by_case):
    gd=pd=cd=ga=pa=ca=unsafe=false_dims=mixed_g=mixed_c=0
    unsafe_rows=[]
    for case,pred in zip(cases,sets_by_case):
        gold=gold_sets(case); gdim=set(gold); pdim=set(pred)
        gd+=len(gdim); pd+=len(pdim); cd+=len(gdim&pdim); false_dims+=len(pdim-gdim)
        for d,atoms in gold.items(): ga+=len(atoms)
        for d,atoms in pred.items():
            pa+=len(atoms); good=gold.get(d,set()); ca+=len(atoms&good)
            bad=atoms-good; unsafe+=len(bad)
            for b in sorted(bad): unsafe_rows.append({"case_id":case["case_id"],"group":case["group"],"dimension":d,"atom":json.loads(b),"raw_source":case["text"]})
        if len(gdim)>1:
            mixed_g+=len(gdim); mixed_c+=len(gdim&pdim)
    return {
        "case_count":len(cases),
        "semantic_dimension_recall":cd/gd if gd else 1.0,
        "dimension_precision":cd/pd if pd else (1.0 if gd==0 else 0.0),
        "typed_atom_recall":ca/ga if ga else 1.0,
        "typed_atom_precision":ca/pa if pa else (1.0 if ga==0 else 0.0),
        "unsafe_atom_count":unsafe,"false_dimension_count":false_dims,
        "mixed_semantic_dimension_recall":mixed_c/mixed_g if mixed_g else 1.0,
        "unsafe_rows":unsafe_rows,
    }

def raw_preserved(output,text):
    sha=hashlib.sha256(text.encode()).hexdigest()
    if output.get("raw_source")!=text or output.get("raw_source_sha256")!=sha: return False
    return all(r.get("raw_source")==text and r.get("raw_source_sha256")==sha for r in output.get("receipts",[]))

def agreement_audit(case,output,validated):
    gold=gold_sets(case); proposed={}; authorized={}
    for r in output["receipts"]:
        if r.get("status")=="CLAIMED" and r.get("atoms"):
            proposed.setdefault(r["dimension"],{})[r["operator_id"]]={key(a) for a in r["atoms"]}
    for rec in validated["validation_receipts"]:
        aset={key(av["atom"]) for av in rec.get("atom_validations",[]) if av["status"]=="AUTHORIZED"}
        if aset: authorized.setdefault(rec["dimension"],{})[rec["operator_id"]]=aset
    rows=[]; agreement_auth={}
    for d,by_reader in proposed.items():
        if len(by_reader)<2: continue
        vals=list(by_reader.values()); agree=all(v==vals[0] for v in vals[1:])
        union=set().union(*vals); err=bool(union-gold.get(d,set()))
        rows.append({"case_id":case["case_id"],"dimension":d,"agreement":agree,"error":err,"reader_atoms":{k:sorted(v) for k,v in by_reader.items()}})
    for d,by_reader in authorized.items():
        counts={}
        for rid,atoms in by_reader.items():
            for a in atoms: counts.setdefault(a,set()).add(rid)
        for a,rids in counts.items():
            if len(rids)>=2: agreement_auth.setdefault(d,set()).add(a)
    return rows,agreement_auth

_ALLOWED={
    tuple(sorted(("exception","quantifier"))):"compose",
    tuple(sorted(("probability","quantifier"))):"coexist",
    tuple(sorted(("exception","permission"))):"compose",
    tuple(sorted(("permission","temporal"))):"compose",
    tuple(sorted(("permission","subclass"))):"coexist",
    tuple(sorted(("quantitative","role_binding"))):"coexist",
    ("role_binding","role_binding"):"conflict",
}
def composition_result(a,b): return _ALLOWED.get(tuple(sorted((a,b))),"reject")

def evaluate(outdir:Path):
    cases=cohort.CASES
    if len(cases)!=84: raise RuntimeError("cohort_count")
    single_outputs=[]; multi_outputs=[]; single_valid=[]; multi_valid=[]; all_agreement=[]; agreement_sets=[]; raw_ok=True
    for c in cases:
        s=output_for(c["text"],False); m=output_for(c["text"],True)
        sv=validator.validate_output(s); mv=validator.validate_output(m)
        single_outputs.append(s); multi_outputs.append(m); single_valid.append(sv); multi_valid.append(mv)
        raw_ok=raw_ok and raw_preserved(s,c["text"]) and raw_preserved(m,c["text"])
        ar,aset=agreement_audit(c,m,mv); all_agreement.extend(ar); agreement_sets.append(aset)
    single_prop=metric_from_sets(cases,[proposal_sets(x) for x in single_outputs])
    multi_prop=metric_from_sets(cases,[proposal_sets(x) for x in multi_outputs])
    single_auth=metric_from_sets(cases,[authorized_sets(x) for x in single_valid])
    multi_auth=metric_from_sets(cases,[authorized_sets(x) for x in multi_valid])
    agree_auth=metric_from_sets(cases,agreement_sets)
    zero=metric_from_sets(cases,[{} for _ in cases])

    agreements=[r for r in all_agreement if r["agreement"]]; disagreements=[r for r in all_agreement if not r["agreement"]]
    agree_err=sum(r["error"] for r in agreements)/(len(agreements) or 1)
    disagree_err=sum(r["error"] for r in disagreements)/(len(disagreements) or 1)

    comp=[]
    for c in cases:
        for a,b,expected in c["composition"]:
            got=composition_result(a,b); comp.append({"case_id":c["case_id"],"dimensions":[a,b],"expected":expected,"got":got,"correct":got==expected})
    comp_acc=sum(x["correct"] for x in comp)/(len(comp) or 1)

    stress=[]
    for n in (0,2,4,6,8):
        os=[]; vs=[]
        for c in cases:
            o=output_for(c["text"],True,extra_limit=n); os.append(o); vs.append(validator.validate_output(o))
        stress.append({"extra_readers":n,"total_readers":8+n,"proposal":metric_from_sets(cases,[proposal_sets(x) for x in os]),"authorized":metric_from_sets(cases,[authorized_sets(x) for x in vs])})
        stress[-1]["proposal"].pop("unsafe_rows",None); stress[-1]["authorized"].pop("unsafe_rows",None)

    prop_gain=multi_prop["semantic_dimension_recall"]-single_prop["semantic_dimension_recall"]
    auth_gain=multi_auth["semantic_dimension_recall"]-single_auth["semantic_dimension_recall"]
    apparatus_invalid=not raw_ok
    if apparatus_invalid: state="APPARATUS_INVALID"
    elif multi_auth["unsafe_atom_count"] or multi_auth["false_dimension_count"]: state="MULTI_READER_OVERCLAIM"
    elif agree_auth["unsafe_atom_count"] or agree_auth["false_dimension_count"]: state="AGREEMENT_GATE_UNSAFE"
    elif prop_gain<0.08 or auth_gain<0.08: state="MULTI_READER_NO_COVERAGE_GAIN"
    elif multi_prop["semantic_dimension_recall"]<0.82 or multi_auth["semantic_dimension_recall"]<0.68: state="MULTI_READER_DISCOVERY_STILL_INSUFFICIENT"
    elif not (multi_prop["dimension_precision"]>=0.97 and multi_auth["typed_atom_precision"]>=0.99 and multi_auth["mixed_semantic_dimension_recall"]>single_auth["mixed_semantic_dimension_recall"] and comp_acc==1.0): state="MULTI_READER_DISCOVERY_STILL_INSUFFICIENT"
    else: state="DETERMINISTIC_MULTI_READER_SUPPORTED_WITH_BOUNDS"

    def clean(m):
        z=dict(m); z.pop("unsafe_rows",None); return z
    results={
        "scientific_state":state,"case_count":len(cases),"raw_source_preservation":1.0 if raw_ok else 0.0,
        "single_reader":{"proposal":clean(single_prop),"authorized":clean(single_auth)},
        "multi_reader":{"proposal":clean(multi_prop),"authorized":clean(multi_auth),"proposal_recall_gain":prop_gain,"authorized_recall_gain":auth_gain},
        "agreement_only":{"authorized":clean(agree_auth),"agreement_cases":len(agreements),"disagreement_cases":len(disagreements),"error_rate_when_agree":agree_err,"error_rate_when_disagree":disagree_err},
        "zero_authority":clean(zero),"composition_oracle":{"count":len(comp),"accuracy":comp_acc},"reader_count_stress":stress,
        "claim_boundary":{"context_free":False,"llm_used":False,"learned_model_used":False,"production_authorization":False},
        "identities":{"preregistration":PREREG,"candidate_freeze":CANDIDATE_FREEZE,"cohort_freeze":COHORT_FREEZE},
    }
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"RESULTS.json").write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
    (outdir/"DISAGREEMENTS.json").write_text(json.dumps(all_agreement,indent=2,sort_keys=True)+"\n")
    counter={"single_authorized":single_auth["unsafe_rows"],"multi_authorized":multi_auth["unsafe_rows"],"agreement_authorized":agree_auth["unsafe_rows"]}
    (outdir/"COUNTEREXAMPLES.json").write_text(json.dumps(counter,indent=2,sort_keys=True)+"\n")
    (outdir/"COMPOSITION.json").write_text(json.dumps(comp,indent=2,sort_keys=True)+"\n")
    report=f"""# RC7D-D Deterministic Multi-Reader Results\n\nScientific state: **`{state}`**\n\nNo LLM or learned model was used.\n\n## Single reader\n- proposal dimension recall: {single_prop['semantic_dimension_recall']:.3f}\n- authorized dimension recall: {single_auth['semantic_dimension_recall']:.3f}\n- authorized atom precision: {single_auth['typed_atom_precision']:.3f}\n- unsafe authorized atoms: {single_auth['unsafe_atom_count']}\n\n## Multi reader\n- proposal dimension recall: {multi_prop['semantic_dimension_recall']:.3f}\n- proposal dimension precision: {multi_prop['dimension_precision']:.3f}\n- authorized dimension recall: {multi_auth['semantic_dimension_recall']:.3f}\n- authorized atom precision: {multi_auth['typed_atom_precision']:.3f}\n- unsafe authorized atoms: {multi_auth['unsafe_atom_count']}\n- false authorized dimensions: {multi_auth['false_dimension_count']}\n- proposal recall gain: {prop_gain:.3f}\n- authorized recall gain: {auth_gain:.3f}\n- mixed-semantic authorized retention: {multi_auth['mixed_semantic_dimension_recall']:.3f}\n\n## Agreement audit\n- agreement case-dimensions: {len(agreements)}\n- disagreement case-dimensions: {len(disagreements)}\n- error when agree: {agree_err:.3f}\n- error when disagree: {disagree_err:.3f}\n- agreement-only unsafe authorized atoms: {agree_auth['unsafe_atom_count']}\n\n## Composition\n- oracle component composition accuracy: {comp_acc:.3f} ({sum(x['correct'] for x in comp)}/{len(comp)})\n\n## Boundary\nPost-reveal deterministic hardening only. No independent-consumability or production claim.\n"""
    (outdir/"REPORT.md").write_text(report)
    print(json.dumps(results,sort_keys=True))
    return results

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",required=True); args=ap.parse_args(); evaluate(Path(args.output_dir))
if __name__=="__main__": main()
