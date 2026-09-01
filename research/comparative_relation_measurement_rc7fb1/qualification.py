"""RC7F-B1 pre-held-out qualification."""
from __future__ import annotations
import json
from pathlib import Path
from .comparator import measure
ROOT=Path(__file__).resolve().parent; RESULTS=ROOT/"results"

def atom(left,relation,right): return {"left":left.lower(),"relation":relation,"right":right.lower()}
PROBES=[
 ("measure-higher","Sector M recorded a higher output than Sector N.",atom("Sector M","GREATER_THAN","Sector N")),
 ("measure-greater","Sector M recorded a greater output than Sector N.",atom("Sector M","GREATER_THAN","Sector N")),
 ("measure-lower","Sector M recorded a lower count than Sector N.",atom("Sector M","LESS_THAN","Sector N")),
 ("measure-smaller","Sector M reported a smaller volume than Sector N.",atom("Sector M","LESS_THAN","Sector N")),
 ("verb-exceed","Sector M exceeded Sector N by 4 units.",atom("Sector M","MORE_THAN","Sector N")),
 ("verb-trail","Sector M trailed Sector N by 4 units.",atom("Sector M","LESS_THAN","Sector N")),
 ("delta-more","Sector M processed 30 units, 4 more than Sector N.",atom("Sector M","MORE_THAN","Sector N")),
 ("share-higher","Sector M posted 40%, a higher share than Sector N.",atom("Sector M","GREATER_THAN","Sector N")),
 ("equal","Sector M produced a total equal to Sector N.",atom("Sector M","EQUAL_TO","Sector N")),
 ("twice","Sector M produced twice as many units as Sector N.",atom("Sector M","MULTIPLE_OF","Sector N")),
]
NEG=[
 "The higher folder contains comparison notes.",
 "The greater-than symbol appears in the manual.",
 "The exceeded flag is archived.",
 "The trailed column is hidden.",
 "Sector M processed 12 units and Sector N processed 9 units.",
]

def _matches(out,gold):
    if len(out["proposals"])!=1: return False
    p=out["proposals"][0]
    return all(p[k]==v for k,v in gold.items())

def main():
    RESULTS.mkdir(exist_ok=True); rows=[]; failures=[]
    for name,text,gold in PROBES:
        out=measure(text); ok=_matches(out,gold); row={"name":name,"text":text,"gold":gold,"observed":out,"ok":ok}; rows.append(row)
        if not ok: failures.append(row)
    neg=[]
    for text in NEG:
        out=measure(text); ok=not out["proposals"]; neg.append({"text":text,"observed":out,"ok":ok})
        if not ok: failures.append(neg[-1])
    payload={"qualification_version":"rc7fb1-q1","positive":rows,"negative":neg,"failure_count":len(failures)}
    (RESULTS/"QUALIFICATION.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"positive":len(rows),"negative":len(neg),"failure_count":len(failures)},indent=2))
    if failures: raise SystemExit(1)
if __name__=="__main__": main()
