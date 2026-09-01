"""Scientific runner for RC7F-B1."""
from __future__ import annotations
import json
from pathlib import Path
from .cohort import CASES, COHORT_FREEZE_EXPECTED
from .comparator import VERSION, measure
from .evaluator import validate_cohort, score
ROOT=Path(__file__).resolve().parent; RESULTS=ROOT/"results"
def main():
    validate_cohort(CASES); outputs=[measure(c["raw_source"]) for c in CASES]; m=score(CASES,outputs)
    ps=m["pair_states"]; mc=ps["meaning_changing_correct"]/ps["meaning_changing_total"] if ps["meaning_changing_total"] else 1.0
    if m["false_proposals_on_negative"] or m["typed_precision"]<1.0 or ps["stable_wrong"]:
        state="COMPARISON_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE"
    elif m["typed_recall"]>=0.95 and m["direction_accuracy"]==1.0 and m["attachment_accuracy"]==1.0 and mc==1.0:
        state="COMPARISON_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING"
    else: state="MORE_COMPARISON_RESEARCH_JUSTIFIED"
    payload={"experiment":"RC7F-B1","candidate_version":VERSION,"cohort":COHORT_FREEZE_EXPECTED,"scientific_state":state,"metrics":m}
    RESULTS.mkdir(exist_ok=True); (RESULTS/"RESULTS.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    (RESULTS/"REPORT.md").write_text("\n".join(["# RC7F-B1 Scientific Result","",f"Terminal token: `{state}`","",f"- precision: {m['typed_precision']:.6f}",f"- recall: {m['typed_recall']:.6f}",f"- false proposals: {m['false_proposals']}",f"- negative-control false proposals: {m['false_proposals_on_negative']}",f"- direction accuracy: {m['direction_accuracy']:.6f}",f"- attachment accuracy: {m['attachment_accuracy']:.6f}",f"- pair states: `{ps}`","","Measurement only. No semantic or operational authority is granted."])+"\n")
    print(json.dumps({"scientific_state":state,**{k:v for k,v in m.items() if k!="rows"}},indent=2))
if __name__=="__main__": main()
