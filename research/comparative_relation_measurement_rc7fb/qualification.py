"""Pre-held-out qualification for RC7F-B."""
from __future__ import annotations
import json
from pathlib import Path
from .comparator import measure
from .evaluator import key

ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/"results"

PROBES=[
 ("delta-more","Team A reviewed 30 files, five more than Team B.",{"left":"team a","relation":"MORE_THAN","right":"team b","delta_surface":"five"}),
 ("delta-fewer","Group C inspected 12 samples, three fewer than Group D.",{"left":"group c","relation":"FEWER_THAN","right":"group d","delta_surface":"three"}),
 ("share-greater","Site X approved 40% of packets, a greater share than Site Y.",{"left":"site x","relation":"GREATER_THAN","right":"site y"}),
 ("rate-lower","Plant R had a lower rate than Plant S.",{"left":"plant r","relation":"LESS_THAN","right":"plant s"}),
 ("equal","Group C produced a total equal to Group D.",{"left":"group c","relation":"EQUAL_TO","right":"group d"}),
 ("twice","Unit M processed twice as many files as Unit N.",{"left":"unit m","relation":"MULTIPLE_OF","right":"unit n","delta_surface":"2"}),
 ("threshold","The pressure was more than 12 kPa.",{"left":"pressure","relation":"MORE_THAN","right":"12 kpa"}),
 ("direction-a","Team A reviewed 30 files, five more than Team B.",{"left":"team a","relation":"MORE_THAN","right":"team b"}),
 ("direction-b","Team A reviewed 30 files, five fewer than Team B.",{"left":"team a","relation":"FEWER_THAN","right":"team b"}),
 ("trap-word","The Greater Than report was archived.",None),
 ("dual-quantity","Team A processed 20 files and Team B processed 15 files.",None),
 ("ambiguous","Team A was more or less aligned with Team B.",None),
]

def main():
    RESULTS.mkdir(exist_ok=True)
    rows=[]; failures=[]
    for name,text,gold in PROBES:
        out=measure(text); p=out["proposals"][0] if out.get("proposals") else None
        ok=(p is None) if gold is None else (p is not None and key(p)==key(gold))
        if ok and gold and gold.get("delta_surface") is not None:
            ok=str(p.get("delta_surface")).lower()==str(gold["delta_surface"]).lower()
        row={"name":name,"text":text,"gold":gold,"output":out,"ok":ok}; rows.append(row)
        if not ok: failures.append(row)
    controls={
      "empty_abstains":measure("")["status"]=="UNRESOLVED",
      "domain_trap_no_proposal":not measure("The comparison dashboard has a lower panel.")["proposals"],
      "two_quantities_no_comparison":not measure("Zone A logged 14 files; Zone B logged 9 files.")["proposals"],
    }
    if not all(controls.values()): failures.append({"controls":controls})
    payload={"qualification_version":"rc7fb-q1","probe_count":len(rows),"failure_count":len(failures),"controls":controls,"rows":rows}
    (RESULTS/"QUALIFICATION.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"probe_count":len(rows),"failure_count":len(failures),"controls":controls},indent=2))
    if failures: raise SystemExit(1)

if __name__=="__main__": main()
