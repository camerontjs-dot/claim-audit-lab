def validate_cohort(cases):
    ids=set(); sig={}
    for c in cases:
        assert c['case_id'] not in ids; ids.add(c['case_id']); n=' '.join(c['raw_source'].lower().split()); g=str(c.get('gold'))
        if n in sig: assert sig[n]==g
        sig[n]=g

def _proj(p): return {k:p[k] for k in ('kind','population','predicate','exception','temporal')}
def score(cases,outs):
    tp=fp=fn=negfp=exc_n=exc_ok=temp_n=temp_ok=0; rows=[]; groups={}
    for c,o in zip(cases,outs):
        g=c.get('gold'); ps=o['proposals']; correct=False
        if g is None:
            fp+=len(ps); negfp+=len(ps); correct=not ps
        else:
            if ps:
                p=_proj(ps[0]); correct=p==g
                if g.get('exception') is not None: exc_n+=1; exc_ok+=int(p.get('exception')==g['exception'])
                if g.get('temporal') is not None: temp_n+=1; temp_ok+=int(p.get('temporal')==g['temporal'])
            if correct: tp+=1
            else: fn+=1; fp+=len(ps)
        if c.get('pair_id'): groups.setdefault(c['pair_id'],[]).append(correct)
        rows.append({'case_id':c['case_id'],'family':c['family'],'gold':g,'proposals':ps,'correct':correct})
    pair_total=pair_ok=0
    for v in groups.values():
        if len(v)==2: pair_total+=1; pair_ok+=int(all(v))
    return {'case_count':len(cases),'true_positives':tp,'false_proposals':fp,'misses':fn,
      'typed_precision':tp/(tp+fp) if tp+fp else 1.0,'typed_recall':tp/(tp+fn) if tp+fn else 1.0,
      'composition_exact_accuracy':tp/(tp+fn) if tp+fn else 1.0,
      'exception_attachment_accuracy':exc_ok/exc_n if exc_n else 1.0,'temporal_attachment_accuracy':temp_ok/temp_n if temp_n else 1.0,
      'false_proposals_on_negative':negfp,'meaning_changing_pair_accuracy':pair_ok/pair_total if pair_total else 1.0,'rows':rows}
