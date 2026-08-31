from __future__ import annotations
import argparse, json
from pathlib import Path

def load(path): return json.loads(Path(path).read_text())
def norm(v): return v.strip().lower() if isinstance(v,str) else v

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--a-results',required=True); ap.add_argument('--a-predictions',required=True); ap.add_argument('--a-mutations',required=True); ap.add_argument('--b-results',required=True); ap.add_argument('--b-predictions',required=True); ap.add_argument('--b-mutations',required=True); ap.add_argument('--output',required=True); args=ap.parse_args()
    ar=load(args.a_results); br=load(args.b_results); apreds=load(args.a_predictions); bpreds=load(args.b_predictions); am=load(args.a_mutations); bm=load(args.b_mutations)
    A={r['case_id']:r for r in apreds}; B={r['case_id']:r for r in bpreds}; ids=sorted(set(A)&set(B))
    sem_agree=sem_total=warr_agree=warr_total=auth_agree=rel_agree=rel_total=core_agree=core_total=0
    disagreement_gold_errors=agreement_gold_errors=disagreements=agreements=0
    for cid in ids:
        a,b=A[cid],B[cid]; pa=a.get('prediction') or {}; pb=b.get('prediction') or {}
        aa=bool(a.get('authorized')); ba=bool(b.get('authorized')); auth_agree += aa==ba
        fam=a['family'] if a['family']!='out_of_jurisdiction' else None
        case_dis=False
        if fam and pa.get('status')=='receipt' and pb.get('status')=='receipt' and pa.get('family')==pb.get('family')==fam:
            af=pa.get('fields') or {}; bf=pb.get('fields') or {}
            for f in set(af)&set(bf):
                sem_total+=1
                same=(af[f].get('status'),norm(af[f].get('value')))==(bf[f].get('status'),norm(bf[f].get('value')))
                sem_agree+=same; case_dis |= not same
                if af[f].get('status') in {'established','semantic_unknown'} and bf[f].get('status') in {'established','semantic_unknown'} and same:
                    warr_total+=1; warr_agree += af[f].get('warrant')==bf[f].get('warrant')
            if a['partition']=='construction': core_total+=1; core_agree += not case_dis
        else:
            case_dis=pa.get('status')!=pb.get('status') or pa.get('family')!=pb.get('family')
        if aa and ba:
            rel_total+=1; rel_agree += a.get('pred_relation')==b.get('pred_relation')
        def row_error(r):
            if r.get('gold_relation') is not None:
                return not r.get('semantic_case_exact',False)
            if (r.get('gold') or {}).get('status')=='out_of_jurisdiction':
                return not r.get('ood_correct',False)
            fr=r.get('field_rows') or []
            return r.get('unsafe',False) or r.get('invalid_output',False) or any(not f.get('status_exact',False) for f in fr)
        gold_error=row_error(a) or row_error(b)
        if case_dis:
            disagreements+=1; disagreement_gold_errors+=gold_error
        else:
            agreements+=1; agreement_gold_errors+=gold_error
    ma={m['name']:m['passed'] for m in am}; mb={m['name']:m['passed'] for m in bm}; mutation_both=sum(1 for k in set(ma)&set(mb) if ma[k] and mb[k]); mutation_total=len(set(ma)&set(mb))
    def rate(n,d): return n/d if d else None
    ametrics=ar['metrics']; bmetrics=br['metrics']
    pair={
      'case_overlap':len(ids),'semantic_field_status_value_agreement':rate(sem_agree,sem_total),'warrant_rule_agreement_given_same_semantics':rate(warr_agree,warr_total),'authorization_agreement':rate(auth_agree,len(ids)),'authorized_relation_agreement':rate(rel_agree,rel_total),'core_case_semantic_agreement':rate(core_agree,core_total),'mutations_passed_by_both':mutation_both,'mutation_total':mutation_total,'disagreement_cases':disagreements,'agreement_cases':agreements,'gold_error_rate_when_disagree':rate(disagreement_gold_errors,disagreements),'gold_error_rate_when_agree':rate(agreement_gold_errors,agreements)}
    unsafe=ametrics['scientific_state']=='UNSAFE_INTERPRETATION' or bmetrics['scientific_state']=='UNSAFE_INTERPRETATION'
    both_recoverable=ametrics['scientific_state']=='SAFE_AND_RECOVERABLE' and bmetrics['scientific_state']=='SAFE_AND_RECOVERABLE'
    both_safe=not unsafe
    coreA=ametrics['partitions'].get('construction',{}).get('authorization_recovery') or 0; coreB=bmetrics['partitions'].get('construction',{}).get('authorization_recovery') or 0
    paraA=ametrics['partitions'].get('paraphrase',{}).get('authorization_recovery') or 0; paraB=bmetrics['partitions'].get('paraphrase',{}).get('authorization_recovery') or 0
    if unsafe: state='UNSAFE_INTERPRETATION'
    elif both_recoverable and (pair['semantic_field_status_value_agreement'] or 0)>=.90 and (pair['warrant_rule_agreement_given_same_semantics'] or 0)>=.90 and (pair['authorization_agreement'] or 0)>=.95 and mutation_both==mutation_total:
        state='INTERPRETATION_AUTHORITY_REPRODUCED'
    elif both_safe and coreA>=.95 and coreB>=.95 and (paraA<.85 or paraB<.85):
        state='LINGUISTIC_GENERALIZATION_LIMITED'
    elif both_safe and coreA>=.90 and coreB>=.90 and (pair['core_case_semantic_agreement'] or 0)<.90:
        state='WARRANT_CONTRACT_INCOMPLETE'
    else: state='IMPLEMENTATION_DEPENDENT_INCONCLUSIVE'
    out={'cross_implementation_state':state,'implementation_a_state':ametrics['scientific_state'],'implementation_b_state':bmetrics['scientific_state'],'pairwise':pair}
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
