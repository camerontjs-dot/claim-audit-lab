"""RC7F-C pre-held-out qualification."""
from __future__ import annotations
import json
from pathlib import Path
from .event_order import measure
ROOT=Path(__file__).resolve().parent; RESULTS=ROOT/"results"
def e(s,p,o,pol="positive"): return {"subject":s.lower(),"predicate":p,"object":o.lower(),"polarity":pol}
PROBES=[
 ("before","Nora reviewed packet q before Ivan signed form k.",e("Nora","review","packet q"),"BEFORE",e("Ivan","sign","form k")),
 ("after","Nora reviewed packet q after Ivan signed form k.",e("Nora","review","packet q"),"AFTER",e("Ivan","sign","form k")),
 ("neg-left","Nora did not review packet q before Ivan signed form k.",e("Nora","review","packet q","negative"),"BEFORE",e("Ivan","sign","form k")),
 ("neg-right","Nora reviewed packet q after Ivan did not sign form k.",e("Nora","review","packet q"),"AFTER",e("Ivan","sign","form k","negative")),
 ("irrelevant-prefix","The ledger is blue. Nora inspected batch r before Ivan approved permit z.",e("Nora","inspect","batch r"),"BEFORE",e("Ivan","approve","permit z")),
]
NEG=["The before column is blue.","The after label is archived.","Review before submission.","Nora reviewed packet q. Ivan signed form k.","Before 2025, the registry was empty."]
def key(p): return (p["left_event"],p["relation"],p["right_event"])
def main():
    RESULTS.mkdir(exist_ok=True); rows=[]; failures=[]
    for name,text,l,r,rr in PROBES:
        out=measure(text); exp=(l,r,rr); ok=len(out["proposals"])==1 and key(out["proposals"][0])==exp
        row={"name":name,"text":text,"expected":exp,"observed":out,"ok":ok}; rows.append(row)
        if not ok: failures.append(row)
    neg=[]
    for text in NEG:
        out=measure(text); ok=not out["proposals"]; neg.append({"text":text,"observed":out,"ok":ok})
        if not ok: failures.append(neg[-1])
    payload={"qualification_version":"rc7fc-q1","positive":rows,"negative":neg,"failure_count":len(failures)}
    (RESULTS/"QUALIFICATION.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"positive":len(rows),"negative":len(neg),"failure_count":len(failures)},indent=2))
    if failures: raise SystemExit(1)
if __name__=="__main__": main()
