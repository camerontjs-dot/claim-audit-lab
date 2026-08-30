"""Execute frozen RC4 entity/population membership semantic discrimination."""
from __future__ import annotations
import argparse, hashlib, itertools, json
from collections import defaultdict
from pathlib import Path

import torch
from sklearn.metrics import f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from research.entity_population_membership_rc4.build_cohort import EXPECTED_SHA256, build, canonical_bytes
from research.entity_population_membership_rc4.mechanisms import decompose_for_nli, typed_relation
from research.nli_independent_calibration_rc2.run_calibration import MODELS, adverse_conservative, label_order, score_case

LABELS=("entailment","neutral","contradiction")
SYSTEMS=("S0_incumbent","S1_same_family_large","S2_long_context","S3_adverse_conservative","S4_decomposition_incumbent","S5_typed_membership")
CRITICAL_PROHIBITED_OUTPUT={
 "member_to_nonmember":"entailment", "subclass_reversal":"entailment",
 "only_necessary_to_sufficient":"entailment", "nonmember_to_member":"entailment",
 "some_to_all":"entailment", "none_to_some":"entailment",
 "not_every_to_every":"entailment", "every_to_some_not":"entailment",
 "group_to_every_member":"entailment", "role_swap":"entailment",
 "membership_absence_not_behavior":"contradiction", "temporal_membership_scope":"entailment",
}

def macro(targets,outputs):
    return float(f1_score(targets,outputs,labels=list(LABELS),average="macro",zero_division=0))

def confusion(targets,outputs):
    cols=list(LABELS)+["unresolved"]; m={t:{o:0 for o in cols} for t in LABELS}
    for t,o in zip(targets,outputs,strict=True): m[t][o]+=1
    return m

def system_metrics(cases,outputs):
    targets=[c["target"] for c in cases]; preds=[outputs[c["case_id"]] for c in cases]
    decided=[i for i,p in enumerate(preds) if p!="unresolved"]; correct=sum(p==t for p,t in zip(preds,targets,strict=True)); fam={}
    for f in sorted({c["family"] for c in cases}):
        sub=[c for c in cases if c["family"]==f]; ts=[c["target"] for c in sub]; ps=[outputs[c["case_id"]] for c in sub]
        fam[f]={"n":len(sub),"correct":sum(a==b for a,b in zip(ts,ps,strict=True)),"unresolved":sum(p=="unresolved" for p in ps),"false_adverse":sum(p=="contradiction" and t!="contradiction" for p,t in zip(ps,ts,strict=True))}
    return {"n":len(cases),"correct":correct,"accuracy":correct/len(cases),"coverage":len(decided)/len(cases),"selective_accuracy":sum(preds[i]==targets[i] for i in decided)/len(decided) if decided else None,"macro_f1_all_unresolved_wrong":macro(targets,preds),"wrong_decided":sum(preds[i]!=targets[i] for i in decided),"unresolved":len(cases)-len(decided),"false_adverse":sum(p=="contradiction" and t!="contradiction" for p,t in zip(preds,targets,strict=True)),"neutral_to_contradiction":sum(t=="neutral" and p=="contradiction" for p,t in zip(preds,targets,strict=True)),"entailment_to_contradiction":sum(t=="entailment" and p=="contradiction" for p,t in zip(preds,targets,strict=True)),"contradiction_to_entailment":sum(t=="contradiction" and p=="entailment" for p,t in zip(preds,targets,strict=True)),"confusion":confusion(targets,preds),"per_family":fam}

def critical_metrics(cases,outputs):
    result={}
    for typ in sorted({c.get("critical_error_type") for c in cases if c.get("critical_error_type")}):
        sub=[c for c in cases if c.get("critical_error_type")==typ]; prohibited=CRITICAL_PROHIBITED_OUTPUT.get(typ)
        wrong=[c["case_id"] for c in sub if outputs[c["case_id"]]!=c["target"]]
        sig=[c["case_id"] for c in sub if outputs[c["case_id"]]==prohibited and outputs[c["case_id"]]!=c["target"]] if prohibited else []
        result[typ]={"n":len(sub),"prohibited_output":prohibited,"any_incorrect":len(wrong),"any_incorrect_case_ids":wrong,"semantic_signature_error":len(sig),"semantic_signature_error_rate":len(sig)/len(sub),"semantic_signature_case_ids":sig}
    return result

def mutation_metrics(pairs,outputs):
    rows=[]; exact=0
    for pair in pairs:
        b=outputs[pair["before"]]; a=outputs[pair["after"]]; ok=b==pair["expected_before"] and a==pair["expected_after"]; exact+=int(ok)
        rows.append({**pair,"observed_before":b,"observed_after":a,"pair_consistent":ok})
    return {"n_pairs":len(pairs),"exact_consistent_pairs":exact,"mutation_consistency":exact/len(pairs),"pairs":rows}

def matched_metrics(cases,outputs):
    groups=defaultdict(list)
    for c in cases: groups[c["premise"]].append(c)
    gs=[g for g in groups.values() if len(g)>=2]; pairs=list(itertools.chain.from_iterable(itertools.combinations(g,2) for g in gs))
    return {"matched_groups":len(gs),"matched_groups_all_correct":sum(all(outputs[c["case_id"]]==c["target"] for c in g) for g in gs),"matched_pairs":len(pairs),"matched_pairs_consistent":sum(outputs[a["case_id"]]==a["target"] and outputs[b["case_id"]]==b["target"] for a,b in pairs)}

def disagreement_metrics(primary,measurements):
    unanimous=[]; disagreement=[]; polar=[]
    for c in primary:
        cid=c["case_id"]; votes=[measurements[name][cid]["predicted"] for name,_,_ in MODELS]
        (unanimous if len(set(votes))==1 else disagreement).append(c)
        if "entailment" in votes and "contradiction" in votes: polar.append(c)
    def err(sub):
        if not sub:return None
        return sum(measurements["incumbent_base"][c["case_id"]]["predicted"]!=c["target"] for c in sub)/len(sub)
    u=err(unanimous); d=err(disagreement)
    return {"n":len(primary),"unanimous_cases":len(unanimous),"disagreement_cases":len(disagreement),"model_disagreement_incidence":len(disagreement)/len(primary),"incumbent_error_rate_unanimous":u,"incumbent_error_rate_disagreement":d,"relative_error_risk_disagreement_vs_unanimity":d/u if d is not None and u not in (None,0) else None,"polar_conflict_cases":len(polar),"unanimous_error_case_ids":[c["case_id"] for c in unanimous if measurements["incumbent_base"][c["case_id"]]["predicted"]!=c["target"]],"disagreement_case_ids":[c["case_id"] for c in disagreement]}

def run(outdir:Path):
    cohort=build(); sha=hashlib.sha256(canonical_bytes(cohort)).hexdigest()
    if sha!=EXPECTED_SHA256: raise RuntimeError(f"frozen cohort mismatch {sha}")
    cases=cohort["cases"]; primary=[c for c in cases if c.get("primary") is True]; mutations=[c for c in cases if c["family"]=="mutation"]; ambiguous=[c for c in cases if c["target"] is None]
    if (len(primary),len(mutations),len(ambiguous))!=(84,20,6): raise RuntimeError("partition changed")
    torch.set_grad_enabled(False); torch.manual_seed(0); measurements={}; metadata={}; decomposition={}
    for name,model_id,revision in MODELS:
        tok=AutoTokenizer.from_pretrained(model_id,revision=revision); model=AutoModelForSequenceClassification.from_pretrained(model_id,revision=revision); model.eval(); order=label_order(model); scored={}
        for c in cases: scored[c["case_id"]]=score_case(model,tok,order,c["premise"],c["hypothesis"])
        for c in cases[:3]:
            again=score_case(model,tok,order,c["premise"],c["hypothesis"]); first=scored[c["case_id"]]
            if again["predicted"]!=first["predicted"] or any(abs(a-b)>1e-6 for a,b in zip(again["canonical_logits"],first["canonical_logits"],strict=True)): raise RuntimeError(f"{name}: nondeterministic sentinel")
        measurements[name]=scored; metadata[name]={"model_id":model_id,"revision":revision,"label_order_native":list(order)}
        if name=="incumbent_base":
            for c in cases:
                d=decompose_for_nli(c["premise"]); decomposition[c["case_id"]]={"decomposed_premise":d,"changed":d!=c["premise"],"measurement":score_case(model,tok,order,d,c["hypothesis"])}
    typed={}
    for c in cases:
        pred,reason,state=typed_relation(c["premise"],c["hypothesis"]); typed[c["case_id"]]={"predicted":pred,"reason":reason,"state":state}
    outputs={s:{} for s in SYSTEMS}
    for c in cases:
        cid=c["case_id"]; votes=[measurements[name][cid]["predicted"] for name,_,_ in MODELS]
        outputs["S0_incumbent"][cid]=measurements["incumbent_base"][cid]["predicted"]
        outputs["S1_same_family_large"][cid]=measurements["same_family_large"][cid]["predicted"]
        outputs["S2_long_context"][cid]=measurements["long_context_base"][cid]["predicted"]
        outputs["S3_adverse_conservative"][cid]=adverse_conservative(votes)
        outputs["S4_decomposition_incumbent"][cid]=decomposition[cid]["measurement"]["predicted"]
        outputs["S5_typed_membership"][cid]=typed[cid]["predicted"]
    result={"experiment":"entity_population_membership_rc4","cohort_sha256":sha,"model_metadata":metadata,"primary_metrics":{},"critical_semantic_failures":{},"mutation_metrics":{},"matched_metrics":{},"disagreement":disagreement_metrics(primary,measurements),"ambiguous_outputs":{},"systems":list(SYSTEMS)}
    for s in SYSTEMS:
        result["primary_metrics"][s]=system_metrics(primary,outputs[s]); result["critical_semantic_failures"][s]=critical_metrics(primary,outputs[s]); result["mutation_metrics"][s]=mutation_metrics(cohort["mutation_pairs"],outputs[s]); result["matched_metrics"][s]=matched_metrics(primary,outputs[s]); result["ambiguous_outputs"][s]={c["case_id"]:outputs[s][c["case_id"]] for c in ambiguous}
    per_case=[]
    for c in cases:
        cid=c["case_id"]; per_case.append({"case_id":cid,"family":c["family"],"primary":c["primary"],"target":c["target"],"critical_error_type":c.get("critical_error_type"),"outputs":{s:outputs[s][cid] for s in SYSTEMS},"model_probabilities":{name:measurements[name][cid]["probabilities"] for name,_,_ in MODELS},"typed_reason":typed[cid]["reason"]})
    measurements_obj={"cohort_sha256":sha,"model_metadata":metadata,"model_measurements":measurements,"decomposition_measurements":decomposition,"typed_measurements":typed,"per_case_outputs":per_case}
    outdir.mkdir(parents=True,exist_ok=True); (outdir/"MEASUREMENTS.json").write_text(json.dumps(measurements_obj,indent=2,sort_keys=True)+"\n"); (outdir/"RESULTS.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"cohort_sha256":sha,"primary_metrics":{s:{k:result["primary_metrics"][s][k] for k in ("accuracy","coverage","selective_accuracy","false_adverse")} for s in SYSTEMS},"mutation_consistency":{s:result["mutation_metrics"][s]["mutation_consistency"] for s in SYSTEMS}},indent=2,sort_keys=True)); return result

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,required=True); args=ap.parse_args(); run(args.output_dir)
if __name__=="__main__": main()
