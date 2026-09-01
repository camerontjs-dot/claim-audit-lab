from __future__ import annotations
import json
from pathlib import Path
from .cohort import CASES,COHORT_FREEZE_EXPECTED
from .permission_compose import VERSION,measure
from .evaluator import validate_cohort,score
ROOT=Path(__file__).resolve().parent; RESULTS=ROOT/'results'
def main():
    validate_cohort(CASES); m=score(CASES,[measure(c['raw_source']) for c in CASES])
    if m['false_proposals_on_negative'] or m['typed_precision']<1.0: state='DEONTIC_COMPOSITION_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE'
    elif m['typed_recall']>=.95 and m['composition_exact_accuracy']>=.95 and m['exception_attachment_accuracy']==1 and m['temporal_attachment_accuracy']==1 and m['meaning_changing_pair_accuracy']==1: state='DEONTIC_COMPOSITION_CANDIDATE_READY_FOR_HARDENING'
    else: state='MORE_DEONTIC_COMPOSITION_RESEARCH_JUSTIFIED'
    p={'experiment':'RC7F-D','candidate_version':VERSION,'cohort':COHORT_FREEZE_EXPECTED,'scientific_state':state,'metrics':m}; RESULTS.mkdir(exist_ok=True)
    (RESULTS/'RESULTS.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n'); (RESULTS/'REPORT.md').write_text(f"# RC7F-D Result\n\n`{state}`\n\nprecision={m['typed_precision']:.6f} recall={m['typed_recall']:.6f} composition={m['composition_exact_accuracy']:.6f}\n\nSemantic permission observation only; no execution authority.\n")
    print(json.dumps({'scientific_state':state,**{k:v for k,v in m.items() if k!='rows'}},indent=2))
if __name__=='__main__': main()
