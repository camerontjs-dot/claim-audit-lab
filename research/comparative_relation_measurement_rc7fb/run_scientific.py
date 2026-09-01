"""Scientific runner for RC7F-B."""
from __future__ import annotations
import json
from pathlib import Path
from .comparator import measure
from .evaluator import score, validate_cohort, key
from .cohort import CASES, COHORT_FREEZE_EXPECTED

ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/"results"

def pair_metrics(outputs):
    grouped={}
    for c in CASES:
        if c.get("pair_id"):
            grouped.setdefault(c["pair_id"],[]).append(c)
    change_total=change_ok=stable_total=stable_ok=0; rows=[]
    for pid,items in sorted(grouped.items()):
        if len(items)!=2: continue
        a,b=items; oa=outputs[a["case_id"]]; ob=outputs[b["case_id"]]
        pa=oa.get("proposals",[]); pb=ob.get("proposals",[])
        ka=key(pa[0]) if pa else None; kb=key(pb[0]) if pb else None
        relation=a.get("pair_relation") or b.get("pair_relation")
        if relation=="meaning_changing":
            change_total+=1; ok=ka!=kb; change_ok+=int(ok)
        elif relation=="meaning_preserving":
            stable_total+=1; ok=ka==kb; stable_ok+=int(ok)
        else: continue
        rows.append({"pair_id":pid,"relation":relation,"ok":ok,"a":a["case_id"],"b":b["case_id"],"a_key":ka,"b_key":kb})
    return {
      "direction_change_total":change_total,
      "direction_change_accuracy":change_ok/change_total if change_total else 1.0,
      "paraphrase_total":stable_total,
      "paraphrase_stability":stable_ok/stable_total if stable_total else 1.0,
      "rows":rows,
    }

def main():
    RESULTS.mkdir(exist_ok=True); validate_cohort(CASES)
    outputs={c["case_id"]:measure(c["raw_source"]) for c in CASES}
    metrics=score(CASES,outputs); pairs=pair_metrics(outputs)
    ready=(metrics["typed_precision"]==1.0 and metrics["typed_recall"]>=0.90 and
           metrics["direction_accuracy_resolved_gold"]==1.0 and metrics["attachment_accuracy_resolved_gold"]==1.0 and
           metrics["false_proposals_on_negative"]==0 and pairs["direction_change_accuracy"]==1.0)
    if ready: state="COMPARISON_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING"
    elif metrics["typed_precision"]>=0.95 or metrics["typed_recall"]>0:
        state="MORE_COMPARISON_RESEARCH_JUSTIFIED"
    else: state="COMPARISON_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE"
    payload={"experiment":"RC7F-B comparative relation measurement","runner_version":"rc7fb-r1","cohort_freeze_expected":COHORT_FREEZE_EXPECTED,"scientific_state":state,"metrics":metrics,"pair_metrics":pairs,"outputs":outputs}
    (RESULTS/"RESULTS.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=["# RC7F-B Scientific Report","",f"- state: `{state}`",f"- cases: `{metrics['case_count']}`",f"- typed precision: `{metrics['typed_precision']:.6f}`",f"- typed recall: `{metrics['typed_recall']:.6f}`",f"- direction accuracy: `{metrics['direction_accuracy_resolved_gold']:.6f}`",f"- attachment accuracy: `{metrics['attachment_accuracy_resolved_gold']:.6f}`",f"- false proposals on negatives: `{metrics['false_proposals_on_negative']}`",f"- unresolved: `{metrics['unresolved_count']}`",f"- direction-change accuracy: `{pairs['direction_change_accuracy']:.6f}`",f"- paraphrase stability: `{pairs['paraphrase_stability']:.6f}`"]
    (RESULTS/"REPORT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"scientific_state":state,"typed_precision":metrics['typed_precision'],"typed_recall":metrics['typed_recall'],"false_proposals_on_negative":metrics['false_proposals_on_negative'],"direction_accuracy":metrics['direction_accuracy_resolved_gold'],"attachment_accuracy":metrics['attachment_accuracy_resolved_gold']},indent=2))

if __name__=="__main__": main()
