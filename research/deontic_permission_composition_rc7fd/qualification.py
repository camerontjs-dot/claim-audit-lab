from __future__ import annotations
import json
from pathlib import Path
from .permission_compose import measure
ROOT=Path(__file__).resolve().parent; RESULTS=ROOT/'results'
def core(pop,pred,exc=None,temp=None):
    return {'kind':'necessary_permission_condition','population':pop,'predicate':pred,'exception':exc,'temporal':temp}
PROBES=[
 ('except','Only release reviewers may approve protocol q, except Mira.',core('release reviewers','approve protocol q',{'excluded':'mira','cue':'except'})),
 ('excluding','Permission to release shipment k is restricted to quality deputies, excluding Hugo.',core('quality deputies','release shipment k',{'excluded':'hugo','cue':'excluding'})),
 ('apart','Only inspectors may sign release note, apart from Nia.',core('inspectors','sign release note',{'excluded':'nia','cue':'apart from'})),
 ('save','Permission to review control sheet is restricted to auditors, save for Ada.',core('auditors','review control sheet',{'excluded':'ada','cue':'save for'})),
 ('exception-of','Only stewards may sign form x with the exception of Ivo.',core('stewards','sign form x',{'excluded':'ivo','cue':'with the exception of'})),
 ('before','Only stewards may sign form x before the deadline.',core('stewards','sign form x',None,{'relation':'before','reference':'the deadline','cue':'before'})),
 ('after','Permission to release batch y is restricted to inspectors after the cutoff.',core('inspectors','release batch y',None,{'relation':'after','reference':'the cutoff','cue':'after'})),
 ('until','Only reviewers may approve packet z until the deadline.',core('reviewers','approve packet z',None,{'relation':'until','reference':'the deadline','cue':'until'})),
 ('asof','Permission to review sheet m is restricted to deputies as of 2027-01-15.',core('deputies','review sheet m',None,{'relation':'as_of','reference':'2027-01-15','cue':'as of'})),
 ('bare','Only auditors may review ledger c.',core('auditors','review ledger c')),
]
NEG=['Dana may review ledger c.','The permission column is blue.','The before label is archived.','Everyone except Mira signed form x.','The permit expires after the cutoff.']
def projected(p): return {k:p[k] for k in ('kind','population','predicate','exception','temporal')}
def main():
    RESULTS.mkdir(exist_ok=True); rows=[]; failures=[]
    for n,t,g in PROBES:
        o=measure(t); ok=len(o['proposals'])==1 and projected(o['proposals'][0])==g; r={'name':n,'text':t,'gold':g,'observed':o,'ok':ok}; rows.append(r)
        if not ok: failures.append(r)
    neg=[]
    for t in NEG:
        o=measure(t); ok=not o['proposals']; r={'text':t,'observed':o,'ok':ok}; neg.append(r)
        if not ok: failures.append(r)
    p={'qualification_version':'rc7fd-q1','positive':rows,'negative':neg,'failure_count':len(failures)}; (RESULTS/'QUALIFICATION.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'positive':len(rows),'negative':len(neg),'failure_count':len(failures)},indent=2))
    if failures: raise SystemExit(1)
if __name__=='__main__': main()
