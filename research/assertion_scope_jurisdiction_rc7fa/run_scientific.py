"""Scientific runner for RC7F-A."""
from __future__ import annotations
import json
from pathlib import Path
from .scope_firewall import classify
from .evaluator import score, validate_cohort
from .cohort import CASES, COHORT_FREEZE_EXPECTED

ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/"results"
RULES=["attribution","conditional","deontic","epistemic","quantifier","ambiguous"]

def run(disabled=()):
    return {c["case_id"]: classify(c["raw_source"], c["observation"], disabled_rules=disabled) for c in CASES}

def pair_metrics(outputs):
    pairs={}
    for c in CASES:
        pid=c.get("pair_id")
        if pid:
            pairs.setdefault(pid,[]).append(c)
    meaning_change_total=meaning_change_correct=stable_total=stable_correct=0
    rows=[]
    for pid,items in sorted(pairs.items()):
        if len(items)!=2:
            continue
        a,b=items
        oa,ob=outputs[a["case_id"]],outputs[b["case_id"]]
        relation=a.get("pair_relation") or b.get("pair_relation")
        if relation=="meaning_changing":
            meaning_change_total+=1
            ok=(oa["scope_status"]!=ob["scope_status"] or oa["authority_eligible"]!=ob["authority_eligible"])
            meaning_change_correct+=int(ok)
        elif relation=="meaning_preserving":
            stable_total+=1
            ok=(oa["scope_status"]==ob["scope_status"] and oa["authority_eligible"]==ob["authority_eligible"])
            stable_correct+=int(ok)
        else:
            continue
        rows.append({"pair_id":pid,"relation":relation,"ok":ok,
                     "a":a["case_id"],"b":b["case_id"],
                     "a_status":oa["scope_status"],"b_status":ob["scope_status"]})
    return {
      "meaning_changing_total":meaning_change_total,
      "meaning_changing_accuracy": meaning_change_correct/meaning_change_total if meaning_change_total else 1.0,
      "meaning_preserving_total":stable_total,
      "meaning_preserving_stability": stable_correct/stable_total if stable_total else 1.0,
      "rows":rows,
    }

def main():
    RESULTS.mkdir(exist_ok=True)
    validate_cohort(CASES)
    outputs=run()
    candidate=score(CASES, outputs)
    baseline_outputs={c["case_id"]:{"scope_status":"ASSERTED","authority_eligible":True,"basis":["allow_all_baseline"],"limitations":[]} for c in CASES}
    baseline=score(CASES, baseline_outputs)
    ablations={}
    for rule in RULES:
        out=run({rule})
        ablations[rule]=score(CASES,out)
    pairs=pair_metrics(outputs)
    ready=(
        candidate["unsafe_false_permits"]==0
        and candidate["authority_eligibility_precision"]==1.0
        and candidate["direct_assertion_recall"]>=0.90
        and pairs["meaning_changing_accuracy"]==1.0
    )
    if ready:
        state="SCOPE_FIREWALL_CANDIDATE_READY_FOR_HARDENING"
    elif candidate["unsafe_false_permits"] < baseline["unsafe_false_permits"]:
        state="MORE_SCOPE_RESEARCH_JUSTIFIED"
    else:
        state="SCOPE_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE"
    payload={
        "experiment":"RC7F-A assertion status and semantic scope jurisdiction",
        "runner_version":"rc7fa-r1",
        "cohort_freeze_expected":COHORT_FREEZE_EXPECTED,
        "scientific_state":state,
        "candidate":candidate,
        "allow_all_baseline":baseline,
        "pair_metrics":pairs,
        "ablations":ablations,
        "outputs":outputs,
    }
    (RESULTS/"RESULTS.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=[
      "# RC7F-A Scientific Report","",
      f"- state: `{state}`",
      f"- cases: `{candidate['case_count']}`",
      f"- candidate false permits: `{candidate['unsafe_false_permits']}`",
      f"- candidate direct-assertion recall: `{candidate['direct_assertion_recall']:.6f}`",
      f"- candidate eligibility precision: `{candidate['authority_eligibility_precision']:.6f}`",
      f"- scope-status accuracy: `{candidate['scope_status_accuracy']:.6f}`",
      f"- unresolved rate: `{candidate['unresolved_rate']:.6f}`",
      f"- allow-all false permits: `{baseline['unsafe_false_permits']}`",
      f"- meaning-changing accuracy: `{pairs['meaning_changing_accuracy']:.6f}`",
      f"- meaning-preserving stability: `{pairs['meaning_preserving_stability']:.6f}`",
      "","## Rule ablations","",
    ]
    for rule,m in ablations.items():
        lines.append(f"- `{rule}` removed: false permits `{m['unsafe_false_permits']}`, recall `{m['direct_assertion_recall']:.3f}`")
    (RESULTS/"REPORT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"scientific_state":state,**{k:candidate[k] for k in ["unsafe_false_permits","direct_assertion_recall","authority_eligibility_precision","scope_status_accuracy","unresolved_rate"]}},indent=2))

if __name__=="__main__":
    main()
