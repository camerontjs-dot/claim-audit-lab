from __future__ import annotations
import argparse, hashlib, importlib, json, os, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from .sealed_payload import load_payload, PAYLOAD_SHA256
from research.population_semantics_contract_rc5b.consumer import relation as frozen_relation

REQ={
 'only_permission':['entity','population','membership','predicate','only_population_may','explicit_permission'],
 'role_binding':['predicate','subject','object','polarity'],
 'quantifier':['population','predicate','quantifier','polarity'],
}
SEM={'established','semantic_unknown'}
BLOCK={'extraction_unresolved','insufficient_authority'}
STATUSES=SEM|BLOCK
UNKNOWN_CAP={('only_permission','membership'),('only_permission','explicit_permission')}
WARRANTS={
 'only_permission':{
  'entity':{'named_entity_reference'},'population':{'named_population_reference'},
  'membership':{'explicit_membership_assertion','explicit_nonmembership_assertion','explicit_unknown_assertion'},
  'predicate':{'permission_predicate_reference'},'only_population_may':{'necessary_permission_condition'},
  'explicit_permission':{'explicit_permission_grant','explicit_permission_denial','explicit_unknown_assertion'}},
 'role_binding':{
  'predicate':{'event_predicate_reference'},'subject':{'active_role_binding','passive_role_binding'},
  'object':{'active_role_binding','passive_role_binding'},'polarity':{'explicit_affirmation','explicit_negation'}},
 'quantifier':{
  'population':{'quantified_population'},'predicate':{'quantified_predicate'},
  'quantifier':{'universal_quantifier','empty_quantifier','existential_quantifier','nonuniversal_quantifier'},
  'polarity':{'explicit_affirmation'}},
}
VALUES={
 ('only_permission','membership'):{'member','non_member','unknown'},
 ('only_permission','only_population_may'):{True},
 ('only_permission','explicit_permission'):{'permitted','not_permitted','unknown'},
 ('role_binding','polarity'):{'positive','negative'},
 ('quantifier','quantifier'):{'every','none','some','not_every'},
 ('quantifier','polarity'):{'positive'},
}

def norm(v):
    if isinstance(v,bool) or v is None: return v
    s=unicodedata.normalize('NFKC',str(v)).lower().strip()
    s=re.sub(r'[\s\.,;:!?]+$','',s); s=re.sub(r'\s+',' ',s)
    s=re.sub(r'^(?:a|an|the)\s+','',s)
    return s

def project(family, fields, query):
    vals={k:norm(fields[k]['value']) if isinstance(fields[k]['value'],str) else fields[k]['value'] for k in REQ[family]}
    if family=='only_permission':
        auth={'entity':vals['entity'],'population':vals['population'],'membership':vals['membership'],'predicate':vals['predicate'],'only_population_may':vals['only_population_may'],'explicit_permission':vals['explicit_permission']}
    elif family=='role_binding':
        auth={'event':{'predicate':vals['predicate'],'roles':{'subject':vals['subject'],'object':vals['object']},'polarity':vals['polarity']}}
    else:
        auth={'population':vals['population'],'members':['e0','e1'],'predicate':vals['predicate'],'quantifier':vals['quantifier'],'polarity':vals['polarity']}
    return {'dimension':family,'authority':auth,'query':query}

def sentence_bounds(text,pos):
    starts=[0];
    for m in re.finditer(r'(?<=[.!?])\s+',text): starts.append(m.end())
    ends=[m.end() for m in re.finditer(r'[.!?](?:\s|$)',text)]
    start=max([x for x in starts if x<=pos],default=0)
    end=min([x for x in ends if x>=pos],default=len(text))
    return start,end

def span_eval(text,pred_span,anchors):
    out={'valid':False,'coverage':False,'disjoint':True,'ratio':0.0}
    if not isinstance(pred_span,dict): return out
    try: start,end=int(pred_span['start']),int(pred_span['end']); st=pred_span['text']
    except Exception: return out
    if not (0<=start<end<=len(text)) or text[start:end]!=st: return out
    out['valid']=True
    best=0.0; any_overlap=False
    for anchor in anchors:
        search=0
        while True:
            a=text.lower().find(anchor.lower(),search)
            if a<0: break
            b=a+len(anchor); inter=max(0,min(end,b)-max(start,a))
            if inter:
                any_overlap=True
                best=max(best, inter/max(1,len(anchor)))
                ps,pe=sentence_bounds(text,start); as_,ae=sentence_bounds(text,a)
                same_sentence=(ps,pe)==(as_,ae)
                if same_sentence and (start<=a and end>=b or best>=0.50): out['coverage']=True
            search=a+1
    out['disjoint']=not any_overlap; out['ratio']=best
    return out

def validate_obs(family,field,obs,text):
    errs=[]
    if not isinstance(obs,dict): return ['not_object']
    st=obs.get('status')
    if st not in STATUSES: errs.append('invalid_status'); return errs
    if st in SEM:
        if obs.get('value') is None: errs.append('missing_value')
        if st=='semantic_unknown':
            if (family,field) not in UNKNOWN_CAP: errs.append('illegal_semantic_unknown')
            if obs.get('value')!='unknown': errs.append('semantic_unknown_value')
        allowed=VALUES.get((family,field))
        if allowed is not None and obs.get('value') not in allowed: errs.append('invalid_value')
        if obs.get('warrant') not in WARRANTS[family][field]: errs.append('invalid_warrant')
        sp=obs.get('span')
        if not isinstance(sp,dict): errs.append('missing_span')
        else:
            try:
                s,e=sp['start'],sp['end']
                if not isinstance(s,int) or not isinstance(e,int) or not(0<=s<e<=len(text)) or text[s:e]!=sp.get('text'): errs.append('invalid_span')
            except Exception: errs.append('invalid_span')
    else:
        if obs.get('value') is not None or obs.get('span') is not None or obs.get('warrant') is not None: errs.append('blocking_state_carries_semantics')
    return errs

def invoke(fn,text,query):
    try:
        return fn(text,query),None
    except Exception as e:
        return None, f'{type(e).__name__}: {e}'

def score_case(item,pred,exc):
    row={'case_id':item['case_id'],'partition':item['partition'],'family':item['family'],'exception':exc,'prediction':pred,'gold':item['gold'],'gold_relation':item.get('gold_relation')}
    row.update({'unsafe':False,'invalid_output':False,'wrong_relation':False,'authorized':False,'pred_relation':None,'semantic_case_exact':False,'field_rows':[]})
    if exc is not None or not isinstance(pred,dict): row['invalid_output']=True; return row
    gold=item['gold']
    if gold['status']=='out_of_jurisdiction':
        if pred.get('status')=='out_of_jurisdiction':
            row['ood_correct']=pred.get('reason')==gold['reason']
        else:
            row['ood_correct']=False; row['unsafe']=True; row['jurisdiction_violation']=True
        return row
    if pred.get('status')=='out_of_jurisdiction':
        row['safe_miss']=True; return row
    if pred.get('status')!='receipt' or pred.get('family')!=gold['family'] or not isinstance(pred.get('fields'),dict):
        row['invalid_output']=True
        if pred.get('status')=='receipt': row['unsafe']=True
        return row
    family=gold['family']; pf=pred['fields']; all_semantic=True; semantic_exact=True; projection_valid=True
    for field in REQ[family]:
        gro=gold['fields'][field]; pro=pf.get(field)
        ferr=validate_obs(family,field,pro,item['text'])
        fr={'field':field,'gold_status':gro['status'],'gold_value':gro.get('value'),'pred_status':pro.get('status') if isinstance(pro,dict) else None,'pred_value':pro.get('value') if isinstance(pro,dict) else None,'validation_errors':ferr}
        if ferr: projection_valid=False
        pst=fr['pred_status']; gst=gro['status']
        if pst not in SEM: all_semantic=False
        fr['status_exact']=pst==gst
        fr['value_exact']=False; fr['warrant_exact']=False; fr['span_coverage']=False; fr['span_disjoint']=False
        if gst in SEM:
            if pst in SEM:
                fr['value_exact']=fr['status_exact'] and norm(fr['pred_value'])==norm(gro.get('value'))
                if not fr['value_exact']:
                    row['unsafe']=True; fr['unsafe_wrong_semantics']=True; semantic_exact=False
                else:
                    fr['warrant_exact']=pro.get('warrant') in set(gro.get('warrants') or [])
                    se=span_eval(item['text'],pro.get('span'),gro.get('anchors') or [])
                    fr['span_coverage']=se['coverage']; fr['span_disjoint']=se['disjoint']; fr['span_ratio']=se['ratio']; fr['span_valid']=se['valid']
                    if se['disjoint']:
                        row['unsafe']=True; fr['unsafe_ungrounded']=True
                    if not fr['warrant_exact'] or not fr['span_coverage'] or ferr: semantic_exact=False
            else:
                fr['safe_semantic_miss']=True; semantic_exact=False
        else:
            semantic_exact=False
            if pst in SEM:
                row['unsafe']=True; fr['unsafe_fabrication']=True
            elif pst=='insufficient_authority': fr['insufficient_exact']=True
            elif pst=='extraction_unresolved': fr['safe_diagnostic_mismatch']=True
        row['field_rows'].append(fr)
    if all_semantic and projection_valid:
        row['authorized']=True
        try: row['pred_relation']=frozen_relation(project(family,pf,item['query']))
        except Exception as e:
            row['consumer_error']=f'{type(e).__name__}: {e}'; row['unsafe']=True
        if item.get('gold_relation') is not None and row.get('pred_relation')!=item['gold_relation']:
            row['wrong_relation']=True; row['unsafe']=True
    row['semantic_case_exact']=bool(item.get('gold_relation') is not None and semantic_exact and row['authorized'] and not row['wrong_relation'])
    return row

def score_mutation(mut,fn):
    br=score_case(mut['before'],*invoke(fn,mut['before']['text'],mut['before']['query']))
    ar=score_case(mut['after'],*invoke(fn,mut['after']['text'],mut['after']['query']))
    def sig(row):
        p=row.get('prediction') or {}; fs=p.get('fields') or {}; fam=mut['family']
        return {f:(fs.get(f,{}).get('status'),norm(fs.get(f,{}).get('value'))) for f in REQ[fam]}
    bs,as_=sig(br),sig(ar)
    changed=sorted([f for f in REQ[mut['family']] if bs.get(f)!=as_.get(f)])
    passed=(not br['unsafe'] and not ar['unsafe'] and br['semantic_case_exact'] and ar['semantic_case_exact'] and changed==sorted(mut['expected_changed_fields']))
    return {'name':mut['name'],'family':mut['family'],'expected_changed_fields':mut['expected_changed_fields'],'observed_changed_fields':changed,'passed':passed,'before':br,'after':ar}

def summarize(rows,mrows):
    field_rows=[f for r in rows for f in r.get('field_rows',[])]
    semantic_gold=[f for f in field_rows if f['gold_status'] in SEM]
    insuff_gold=[f for f in field_rows if f['gold_status']=='insufficient_authority']
    sem_correct=[f for f in semantic_gold if f['value_exact']]
    semantic_cases=[r for r in rows if r.get('gold_relation') is not None]
    def rate(n,d): return n/d if d else None
    parts={}
    for p in sorted({r['partition'] for r in rows}):
        rs=[r for r in semantic_cases if r['partition']==p]
        parts[p]={'semantic_cases':len(rs),'authorized_correct':sum(1 for r in rs if r['semantic_case_exact']),'authorization_recovery':rate(sum(1 for r in rs if r['semantic_case_exact']),len(rs))}
    metrics={
      'case_count':len(rows),
      'unsafe_cases':sum(1 for r in rows if r['unsafe']),
      'wrong_authorized_relations':sum(1 for r in rows if r['wrong_relation']),
      'invalid_outputs_or_exceptions':sum(1 for r in rows if r['invalid_output']),
      'ood_correct':sum(1 for r in rows if r.get('ood_correct')),
      'ood_total':sum(1 for r in rows if r['gold']['status']=='out_of_jurisdiction'),
      'semantic_gold_fields':len(semantic_gold),
      'semantic_field_value_status_exact':sum(1 for f in semantic_gold if f['value_exact']),
      'semantic_field_recovery':rate(sum(1 for f in semantic_gold if f['value_exact']),len(semantic_gold)),
      'warrant_rule_recovery':rate(sum(1 for f in sem_correct if f['warrant_exact']),len(sem_correct)),
      'warrant_span_coverage':rate(sum(1 for f in sem_correct if f['span_coverage']),len(sem_correct)),
      'semantic_unknown_total':sum(1 for f in semantic_gold if f['gold_status']=='semantic_unknown'),
      'semantic_unknown_exact':sum(1 for f in semantic_gold if f['gold_status']=='semantic_unknown' and f['value_exact']),
      'semantic_unknown_recall':rate(sum(1 for f in semantic_gold if f['gold_status']=='semantic_unknown' and f['value_exact']),sum(1 for f in semantic_gold if f['gold_status']=='semantic_unknown')),
      'insufficient_gold_fields':len(insuff_gold),
      'insufficient_exact':sum(1 for f in insuff_gold if f.get('insufficient_exact')),
      'insufficient_classification_recall':rate(sum(1 for f in insuff_gold if f.get('insufficient_exact')),len(insuff_gold)),
      'semantic_cases':len(semantic_cases),
      'semantic_cases_exact_authorized':sum(1 for r in semantic_cases if r['semantic_case_exact']),
      'semantic_case_authorization_recovery':rate(sum(1 for r in semantic_cases if r['semantic_case_exact']),len(semantic_cases)),
      'mutations_total':len(mrows),'mutations_passed':sum(1 for m in mrows if m['passed']),
      'partitions':parts,
    }
    core=parts.get('construction',{}).get('authorization_recovery') or 0
    para=parts.get('paraphrase',{}).get('authorization_recovery') or 0
    hard_unsafe=metrics['unsafe_cases']>0 or metrics['wrong_authorized_relations']>0
    thresholds=(metrics['semantic_field_recovery']>=.90 and metrics['warrant_rule_recovery']>=.90 and metrics['warrant_span_coverage']>=.90 and metrics['semantic_unknown_recall']>=.90 and metrics['insufficient_classification_recall']>=.90 and metrics['semantic_case_authorization_recovery']>=.90 and core>=.95 and para>=.85 and metrics['mutations_passed']==metrics['mutations_total'] and metrics['ood_correct']==metrics['ood_total'] and metrics['invalid_outputs_or_exceptions']==0)
    if hard_unsafe: state='UNSAFE_INTERPRETATION'
    elif core>=.95 and para<.85: state='LINGUISTIC_GENERALIZATION_LIMITED'
    elif thresholds: state='SAFE_AND_RECOVERABLE'
    else: state='SAFE_BUT_INCOMPLETE'
    metrics['scientific_state']=state
    return metrics

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--implementation-module',required=True); ap.add_argument('--output-dir',required=True); args=ap.parse_args()
    mod=importlib.import_module(args.implementation_module); fn=getattr(mod,'interpret')
    payload=load_payload(); rows=[]
    for item in payload['cases']:
        pred,exc=invoke(fn,item['text'],item['query']); rows.append(score_case(item,pred,exc))
    mrows=[score_mutation(m,fn) for m in payload['mutations']]
    metrics=summarize(rows,mrows)
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    (out/'RESULTS.json').write_text(json.dumps({'payload_sha256':PAYLOAD_SHA256,'implementation_module':args.implementation_module,'metrics':metrics},indent=2,sort_keys=True)+'\n')
    (out/'PREDICTIONS.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
    (out/'MUTATIONS.json').write_text(json.dumps(mrows,indent=2,sort_keys=True)+'\n')
    (out/'COUNTEREXAMPLES.json').write_text(json.dumps({'unsafe':[r for r in rows if r['unsafe']],'safe_misses':[r for r in rows if r.get('safe_miss') or (r.get('gold_relation') is not None and not r['semantic_case_exact'])],'failed_mutations':[m for m in mrows if not m['passed']]},indent=2,sort_keys=True)+'\n')
    print(json.dumps(metrics,indent=2,sort_keys=True))
if __name__=='__main__': main()
