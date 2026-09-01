"""Frozen RC7F-C evaluator."""
def validate_cohort(cases):
    ids=set(); sig={}
    for c in cases:
        assert c['case_id'] not in ids; ids.add(c['case_id']); n=' '.join(c['raw_source'].lower().split())
        g=c.get('gold'); s=None if g is None else (str(g['left_event']),g['relation'],str(g['right_event']))
        if n in sig: assert sig[n]==s
        sig[n]=s

def _same_event(a,b): return a==b
def score(cases,outs):
    tp=fp=fn=negfp=dirn=dirok=attn=attok=poln=polok=0; groups={}; rows=[]
    for c,o in zip(cases,outs):
        g=c.get('gold'); ps=o['proposals']; correct=False
        if g is None:
            fp+=len(ps); negfp+=len(ps); correct=not ps
        else:
            if ps:
                p=ps[0]; dirn+=1; attn+=1; poln+=2
                dirok+=int(p['relation']==g['relation'])
                attok+=int(_same_event(p['left_event'],g['left_event']) and _same_event(p['right_event'],g['right_event']))
                polok+=int(p['left_event']['polarity']==g['left_event']['polarity'])+int(p['right_event']['polarity']==g['right_event']['polarity'])
                correct=p['relation']==g['relation'] and p['left_event']==g['left_event'] and p['right_event']==g['right_event']
            if correct: tp+=1
            else: fn+=1; fp+=max(0,len(ps)-int(correct))
        if c.get('pair_id'): groups.setdefault(c['pair_id'],[]).append(correct)
        rows.append({'case_id':c['case_id'],'family':c['family'],'gold':g,'proposals':ps,'correct':correct})
    pair_total=pair_ok=0
    for v in groups.values():
        if len(v)==2: pair_total+=1; pair_ok+=int(all(v))
    return {'case_count':len(cases),'true_positives':tp,'false_proposals':fp,'misses':fn,
      'typed_precision':tp/(tp+fp) if tp+fp else 1.0,'typed_recall':tp/(tp+fn) if tp+fn else 1.0,
      'direction_accuracy':dirok/dirn if dirn else 1.0,'attachment_accuracy':attok/attn if attn else 1.0,
      'polarity_accuracy':polok/poln if poln else 1.0,'false_proposals_on_negative':negfp,
      'meaning_changing_pair_accuracy':pair_ok/pair_total if pair_total else 1.0,'rows':rows}
