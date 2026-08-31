"""Scientific RC7E runner. Apparatus must be frozen before cohort import."""
from __future__ import annotations

import json
import statistics
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any

from research.language_instrument_ablation_rc7e.authority import validate_common_receipt, validate_union
from research.language_instrument_ablation_rc7e.contract import make_receipt, source_sha
from research.language_instrument_ablation_rc7e.equivalence import atom_key
from research.language_instrument_ablation_rc7e.evaluator import score_cases,unique_contributions,pairwise_overlap_and_error,evaluator_controls,gold_sets,proposal_sets
from research.language_instrument_ablation_rc7e.instruments import RC7DBaseline,QuantulumInstrument,StanzaFamily,CoreNLPFamily,SuParSDP,DebertaNLI,OWLRLReasoner,instrument_identities
from research.language_instrument_ablation_rc7e.cohort import CASES, COHORT_FREEZE_EXPECTED

OUT=Path("research/language_instrument_ablation_rc7e/results")
ORDER=["rc7d_deterministic","quantulum3","stanza_ud","corenlp_openie","corenlp_natlog","corenlp_sutime","stanza_constituency","corenlp_coref_quote","supar_sdp","deberta_nli","owlrl_reasoner"]
FAMILY={"rc7d_deterministic":"deterministic","quantulum3":"quantitative","stanza_ud":"stanza","stanza_constituency":"stanza","corenlp_openie":"corenlp","corenlp_natlog":"corenlp","corenlp_sutime":"corenlp","corenlp_coref_quote":"corenlp","supar_sdp":"supar","deberta_nli":"nli","owlrl_reasoner":"symbolic_reasoner"}


def agreement_receipt(raw:str, receipts:list[dict[str,Any]]) -> dict[str,Any]:
    by_key=defaultdict(list); row_by_key={}
    for r in receipts:
        if r["instrument_id"] in {"deberta_nli","owlrl_reasoner"}: continue
        for row in r.get("candidate_atoms",[]):
            if not row.get("scorable") or not isinstance(row.get("atom"),dict):continue
            k=atom_key(row["dimension"],row["atom"]);by_key[k].append(FAMILY.get(r["instrument_id"],r["instrument_id"]));row_by_key[k]=row
    agreed=[]
    for k,fams in by_key.items():
        if len(set(fams))>=2:agreed.append(row_by_key[k])
    dims=sorted({r["dimension"] for r in agreed})
    return make_receipt(raw,instrument_id="agreement_only",instrument_identity={"version":"rc7e-v1","rule":"same canonical typed atom from >=2 runtime families"},measurement_principle="cross-family proposal agreement control",status="CLAIMED" if agreed else "NOT_APPLICABLE",proposed_dimensions=dims,candidate_atoms=agreed,jurisdiction=[],limitations=["agreement is not truth and does not itself authorize"],residue=[])


def run_case(case:dict[str,Any], stanza:StanzaFamily, core:CoreNLPFamily, supar:SuParSDP, nli:DebertaNLI, owl:OWLRLReasoner):
    raw=case["text"]
    rec=[]
    rec.append(RC7DBaseline().run(raw)); rec.append(QuantulumInstrument().run(raw))
    rec.append(stanza.ud_receipt(raw)); rec.append(core.openie_receipt(raw)); rec.append(core.natlog_receipt(raw)); rec.append(core.sutime_receipt(raw)); rec.append(stanza.constituency_receipt(raw)); rec.append(core.coref_quote_receipt(raw)); rec.append(supar.run(raw))
    typed=[row for r in rec for row in r.get("candidate_atoms",[]) if row.get("scorable")]
    nli_r=nli.measure(raw,typed); rec.append(nli_r)
    base_auth=[validate_common_receipt(r) for r in rec if r["instrument_id"] not in {"deberta_nli","owlrl_reasoner"}]
    union_auth=validate_union(raw,[r for r in rec if r["instrument_id"]!="deberta_nli"])
    owl_r=owl.infer(raw,union_auth.get("authorized_atoms",{})); rec.append(owl_r)
    owl_a=validate_common_receipt(owl_r)
    all_auth=base_auth+[owl_a]
    agr=agreement_receipt(raw,rec); agr_auth=validate_common_receipt(agr)
    return rec,all_auth,union_auth,agr,agr_auth


def subset_score(cases, by_inst, names, union_authority=True):
    receipt_by_case={}
    auth_by_case={}
    for c in cases:
        cid=c["case_id"]; rs=[by_inst[n][cid] for n in names if cid in by_inst.get(n,{})]
        receipt_by_case[cid]=rs
        auth_by_case[cid]=[validate_union(c["text"],rs)] if union_authority and rs else []
    return score_cases(cases,receipt_by_case,auth_by_case)


def nli_diagnostic(cases, by_inst):
    correct=[];wrong=[]
    for c in cases:
        _,gat=gold_sets(c); nr=by_inst.get("deberta_nli",{}).get(c["case_id"])
        if not nr:continue
        for item in nr.get("native_output",[]):
            k=atom_key(item["proposal_dimension"],item["proposal_atom"]); score=float(item["scores"].get("entailment",0.0))
            (correct if k in gat else wrong).append(score)
    return {"correct_count":len(correct),"wrong_count":len(wrong),"mean_entailment_correct":statistics.mean(correct) if correct else None,"mean_entailment_wrong":statistics.mean(wrong) if wrong else None,"note":"diagnostic relation measurement only; no threshold grants authority"}


def report_markdown(results:dict[str,Any]) -> str:
    lines=["# RC7E Semantic-Instrument Portfolio Map","","Research-only. No production authorization.","",f"**Scientific state:** `{results['scientific_state']}`",""]
    lines += ["## Headline",f"- Cases: {results['case_count']}",f"- Raw-source preservation: {results['raw_source_preservation']:.3f}",f"- Baseline proposal dimension recall: {results['baseline']['proposal']['semantic_dimension_recall']:.3f}",f"- Complete union proposal dimension recall: {results['complete_union']['proposal']['semantic_dimension_recall']:.3f}",f"- Complete union authorized dimension recall: {results['complete_union']['authorized']['semantic_dimension_recall']:.3f}",f"- Complete union authorized typed-atom precision: {results['complete_union']['authorized']['typed_atom_precision']:.3f}",f"- Unsafe authorized atoms: {results['complete_union']['authorized']['unsafe_atom_count']}",f"- False authorized dimensions: {results['complete_union']['authorized']['false_dimension_count']}",""]
    lines += ["## Instrument status"]
    for iid,row in results["instrument_runtime"].items(): lines.append(f"- `{iid}`: {row['load_status']} / proposals on {row['claimed_cases']} cases / failures {row['failed_cases']}")
    lines += ["","## Unique correct dimension contributions"]
    for iid,row in results["unique_contribution"].items():lines.append(f"- `{iid}`: {row['unique_correct_dimensions']} dimensions; {row['unique_correct_atoms']} scorable atoms")
    lines += ["","## Residue",f"Residual semantic dimensions after complete proposal union: **{results['complete_union']['proposal']['residual_dimension_count']}**."]
    for dim,count in sorted(results["residual_by_dimension"].items(),key=lambda x:(-x[1],x[0])):lines.append(f"- `{dim}`: {count}")
    lines += ["","## Strongest shared failures"]
    for row in results["strongest_shared_failures"][:12]:lines.append(f"- `{row['case_id']}` `{row['dimension']}` missed by {row['missed_by']} instruments")
    lines += ["","## Apparatus notes"]
    for note in results.get("apparatus_notes",[]):lines.append(f"- {note}")
    lines += ["","## Bounded conclusion",results["bounded_conclusion"],"",f"Terminal research decision token: `{results['scientific_state']}`"]
    return "\n".join(lines)+"\n"


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    controls=evaluator_controls()
    if not controls["all_passed"]:raise SystemExit("evaluator controls failed before scientific execution")
    stanza=StanzaFamily();core=CoreNLPFamily();supar=SuParSDP();nli=DebertaNLI();owl=OWLRLReasoner()
    by_inst=defaultdict(dict); union_auth={}; agr_rec={};agr_auth={}
    raw_ok=True
    try:
        for case in CASES:
            recs,auths,ua,ar,aa=run_case(case,stanza,core,supar,nli,owl)
            cid=case["case_id"]
            for r in recs:by_inst[r["instrument_id"]][cid]=r;raw_ok &= r["raw_source"]==case["text"] and r["raw_source_sha256"]==source_sha(case["text"])
            union_auth[cid]=ua;agr_rec[cid]=ar;agr_auth[cid]=aa
    finally:core.close()
    all_names=[n for n in ORDER if n in by_inst]
    receipt_union={c["case_id"]:[by_inst[n][c["case_id"]] for n in all_names if c["case_id"] in by_inst[n]] for c in CASES}
    auth_union={c["case_id"]:[union_auth[c["case_id"]]] for c in CASES}
    complete=score_cases(CASES,receipt_union,auth_union)
    baseline=subset_score(CASES,by_inst,["rc7d_deterministic"])
    individual={n:subset_score(CASES,by_inst,[n]) for n in all_names}
    cumulative={};prefix=[]
    for n in all_names:
        prefix.append(n);cumulative[str(len(prefix))]={"instruments":list(prefix),"metrics":subset_score(CASES,by_inst,prefix)}
    leave_out={n:subset_score(CASES,by_inst,[x for x in all_names if x!=n]) for n in all_names}
    pairs={}
    for a,b in [("stanza_ud","corenlp_openie"),("stanza_ud","supar_sdp"),("corenlp_openie","supar_sdp"),("corenlp_sutime","stanza_ud"),("quantulum3","stanza_ud"),("corenlp_natlog","rc7d_deterministic"),("corenlp_coref_quote","corenlp_openie"),("deberta_nli","stanza_ud")]:
        if a in by_inst and b in by_inst:pairs[f"{a}+{b}"]=subset_score(CASES,by_inst,[a,b])
    agreement=score_cases(CASES,{cid:[agr_rec[cid]] for cid in agr_rec},{cid:[agr_auth[cid]] for cid in agr_auth})
    zero=score_cases(CASES,receipt_union,{c["case_id"]:[] for c in CASES})
    unique=unique_contributions(CASES,by_inst,all_names)
    pairwise=pairwise_overlap_and_error(CASES,by_inst,all_names)
    residual=Counter();shared=[]
    for c in CASES:
        pdim,_=proposal_sets(receipt_union[c["case_id"]]);gdim,_=gold_sets(c)
        for d in gdim-pdim:
            residual[d]+=1
            missed=sum(1 for n in all_names if d not in by_inst[n][c["case_id"]].get("proposed_dimensions",[]))
            shared.append({"case_id":c["case_id"],"dimension":d,"missed_by":missed})
    shared.sort(key=lambda x:(-x["missed_by"],x["case_id"],x["dimension"]))
    runtime={}
    for n in all_names:
        rs=list(by_inst[n].values());runtime[n]={"load_status":"FAILED_PRESENT" if any(r.get("runtime",{}).get("load_status")=="FAILED" for r in rs) else "OK","claimed_cases":sum(r["status"]=="CLAIMED" for r in rs),"failed_cases":sum(r.get("runtime",{}).get("load_status")=="FAILED" for r in rs),"latency_s_total":sum(float(r.get("runtime",{}).get("latency_s",0) or 0) for r in rs)}
    gain=complete["proposal"]["semantic_dimension_recall"]-baseline["proposal"]["semantic_dimension_recall"]
    strict_safe=complete["authorized"]["unsafe_atom_count"]==0 and complete["authorized"]["false_dimension_count"]==0
    major_fail=sum(v["failed_cases"] for v in runtime.values())>0
    if not controls["all_passed"] or not raw_ok:state="ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE";conclusion="Evaluator or source-preservation controls failed; scientific interpretation is blocked."
    elif strict_safe and gain>=0.10 and not major_fail:state="PORTFOLIO_CANDIDATE_READY_FOR_HARDENING";conclusion="The heterogeneous proposal portfolio materially reduced residue beyond RC7D while the frozen separate authority layer produced no unsafe authorized atoms or false authorized dimensions. This supports hardening the smallest Pareto subset, not production promotion."
    elif major_fail:state="ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE";conclusion="At least one preregistered instrument had runtime failures on held-out execution. Results are preserved but the full portfolio claim is technically inconclusive; surviving lanes may still be analyzed as bounded partial evidence."
    elif gain>0:state="MORE_NON_LLM_INSTRUMENT_RESEARCH_JUSTIFIED";conclusion="Heterogeneous measurements added information, but the preregistered safety/coverage conditions for a hardening candidate were not met. Residue and/or unsafe authority requires a smaller discriminating non-LLM follow-up before any LLM lane is justified."
    else:state="ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE";conclusion="The tested heterogeneous portfolio did not produce material semantic-dimension gain beyond the frozen deterministic baseline under the preregistered apparatus."
    results={"experiment":"RC7E","case_count":len(CASES),"cohort_freeze_expected":COHORT_FREEZE_EXPECTED,"evaluator_controls":controls,"raw_source_preservation":1.0 if raw_ok else 0.0,"identities":instrument_identities(),"order":all_names,"baseline":baseline,"individual":individual,"cumulative":cumulative,"leave_one_out":leave_out,"pairings":pairs,"complete_union":complete,"agreement_only":agreement,"preserve_all_authorize_none":zero,"oracle_dimension_ceiling":1.0,"oracle_composition_accuracy":1.0 if all(c.get("composition_oracle",True) for c in CASES) else None,"unique_contribution":unique,"pairwise":pairwise,"nli_diagnostic":nli_diagnostic(CASES,by_inst),"instrument_runtime":runtime,"residual_by_dimension":dict(residual),"strongest_shared_failures":shared,"scientific_state":state,"bounded_conclusion":conclusion,"apparatus_notes":["No production src/ path is imported or modified by RC7E.","CoreNLP logical lanes share one runtime family and are not counted as independent by annotator name alone.","SuPar SDP uses independent raw-source preprocessing via Stanza because the pretrained BiLSTM SDP model requires lemma/POS; this dependency is explicit.","NLI measures source↔typed-proposal relation only and cannot originate or authorize semantic atoms.","OWL-RL operates only on already-authorized subclass premises."]}
    (OUT/"RESULTS.json").write_text(json.dumps(results,indent=2,sort_keys=True),encoding="utf-8")
    (OUT/"REPORT.md").write_text(report_markdown(results),encoding="utf-8")
    (OUT/"RECEIPTS.json").write_text(json.dumps({n:by_inst[n] for n in all_names},indent=2,sort_keys=True),encoding="utf-8")
    print(json.dumps({"scientific_state":state,"baseline_proposal_recall":baseline["proposal"]["semantic_dimension_recall"],"union_proposal_recall":complete["proposal"]["semantic_dimension_recall"],"authorized_recall":complete["authorized"]["semantic_dimension_recall"],"unsafe_authorized_atoms":complete["authorized"]["unsafe_atom_count"],"false_authorized_dimensions":complete["authorized"]["false_dimension_count"],"residual_by_dimension":dict(residual)},indent=2))

if __name__=="__main__":main()
