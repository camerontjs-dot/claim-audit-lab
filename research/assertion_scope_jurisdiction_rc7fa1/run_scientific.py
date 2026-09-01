"""Scientific runner for frozen RC7F-A1 candidate."""
from __future__ import annotations
import json
from pathlib import Path
from .cohort import CASES, COHORT_FREEZE_EXPECTED
from .scope_firewall import CANDIDATE_VERSION, classify
from .evaluator import score, validate_cohort

ROOT=Path(__file__).resolve().parent
RESULTS=ROOT/"results"

def main() -> None:
    validate_cohort(CASES)
    outputs=[classify(c["raw_source"],c["observation"]) for c in CASES]
    metrics=score(CASES,outputs)
    if metrics["unsafe_false_permits"]:
        state="SCOPE_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE"
    elif (metrics["direct_assertion_recall"]==1.0 and
          metrics["authority_eligibility_precision"]==1.0 and
          metrics["exact_scope_path_accuracy"]>=0.95 and
          metrics["punctuation_scope_stability"]==1.0 and
          metrics["meaning_changing_pair_accuracy"]==1.0):
        state="SCOPE_WARRANT_CANDIDATE_READY_FOR_HARDENING"
    else:
        state="MORE_SCOPE_RESEARCH_JUSTIFIED"
    payload={
        "experiment":"RC7F-A1",
        "candidate_version":CANDIDATE_VERSION,
        "cohort":COHORT_FREEZE_EXPECTED,
        "scientific_state":state,
        "metrics":metrics,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS/"RESULTS.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    report=[
        "# RC7F-A1 Scientific Result","",f"Terminal token: `{state}`","",
        f"- cases: {metrics['case_count']}",
        f"- unsafe false permits: {metrics['unsafe_false_permits']}",
        f"- direct assertion recall: {metrics['direct_assertion_recall']:.6f}",
        f"- authority eligibility precision: {metrics['authority_eligibility_precision']:.6f}",
        f"- exact scope-path accuracy: {metrics['exact_scope_path_accuracy']:.6f}",
        f"- scope membership precision: {metrics['scope_membership_precision']:.6f}",
        f"- scope membership recall: {metrics['scope_membership_recall']:.6f}",
        f"- punctuation scope stability: {metrics['punctuation_scope_stability']:.6f}",
        f"- meaning-changing pair accuracy: {metrics['meaning_changing_pair_accuracy']:.6f}","",
        "This is research evidence only. Observation remains distinct from semantic warrant; no operational authorization or production change is implied.",
    ]
    (RESULTS/"REPORT.md").write_text("\n".join(report)+"\n")
    print(json.dumps({"scientific_state":state,**{k:v for k,v in metrics.items() if k!="rows"}},indent=2))

if __name__=="__main__": main()
