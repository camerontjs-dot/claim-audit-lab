"""Pre-held-out qualification for RC7F-A."""
from __future__ import annotations
import json
from pathlib import Path
from .scope_firewall import classify

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

def obs(text: str, clause: str, polarity: str = "positive"):
    start = text.index(clause)
    return {"predicate": "inspect", "subject": "lena", "object": "batch r",
            "polarity": polarity, "start": start, "end": start + len(clause)}

PROBES = [
    ("direct", "Lena inspected batch r.", "Lena inspected batch r.", "positive", "ASSERTED", True),
    ("negative", "Lena did not inspect batch r.", "Lena did not inspect batch r.", "negative", "ASSERTED_NEGATIVE", True),
    ("quoted", 'Omar said, "Lena inspected batch r."', "Lena inspected batch r.", "positive", "ATTRIBUTED", False),
    ("reported", "Omar reported that Lena inspected batch r.", "Lena inspected batch r.", "positive", "ATTRIBUTED", False),
    ("denied", "Omar denied that Lena inspected batch r.", "Lena inspected batch r.", "positive", "ATTRIBUTED", False),
    ("if-ant", "If Lena inspects batch r, Omar signs form z.", "Lena inspects batch r", "positive", "CONDITIONAL_ANTECEDENT", False),
    ("if-cons", "If Omar signs form z, Lena inspects batch r.", "Lena inspects batch r.", "positive", "CONDITIONAL_CONSEQUENT", False),
    ("unless-ant", "Unless Lena inspects batch r, Omar signs form z.", "Lena inspects batch r", "positive", "CONDITIONAL_ANTECEDENT", False),
    ("epistemic", "Lena probably inspected batch r.", "Lena probably inspected batch r.", "positive", "EPISTEMIC", False),
    ("possibility", "It is possible that Lena inspected batch r.", "Lena inspected batch r.", "positive", "EPISTEMIC", False),
    ("deontic-only-may", "Only inspectors may inspect batch r.", "inspectors may inspect batch r.", "positive", "DEONTIC", False),
    ("deontic-permit", "Lena is permitted to inspect batch r.", "Lena is permitted to inspect batch r.", "positive", "DEONTIC", False),
    ("quant-every", "Every inspector inspected batch r.", "inspector inspected batch r.", "positive", "QUANTIFIED", False),
    ("quant-percent", "40% of inspectors inspected batch r.", "inspectors inspected batch r.", "positive", "QUANTIFIED", False),
    ("ambiguous-whether", "Whether Lena inspected batch r remains disputed.", "Lena inspected batch r", "positive", "UNRESOLVED", False),
]

def main():
    RESULTS.mkdir(exist_ok=True)
    rows=[]
    failures=[]
    for name,text,clause,polarity,status,eligible in PROBES:
        out=classify(text, obs(text,clause,polarity))
        ok=out["scope_status"]==status and out["authority_eligible"]==eligible
        row={"name":name,"text":text,"expected_status":status,"expected_eligible":eligible,"observed":out,"ok":ok}
        rows.append(row)
        if not ok:
            failures.append(row)

    controls = {
        "case_id_not_input": "case_id" not in classify.__code__.co_varnames,
        "unknown_anchor_abstains": classify("abc", {"start": 9, "end": 10, "polarity":"positive"})["scope_status"] == "UNRESOLVED",
        "irrelevant_noun_invariance": (
            classify("Lena inspected reactor.", {"start":0,"end":23,"polarity":"positive"})["scope_status"] ==
            classify("Lena inspected protocol.", {"start":0,"end":24,"polarity":"positive"})["scope_status"]
        ),
    }
    if not all(controls.values()):
        failures.append({"controls":controls})
    payload={"qualification_version":"rc7fa-q1","probe_count":len(rows),"rows":rows,"controls":controls,"failure_count":len(failures)}
    (RESULTS/"QUALIFICATION.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"probe_count":len(rows),"failure_count":len(failures),"controls":controls},indent=2))
    if failures:
        raise SystemExit(1)

if __name__=="__main__":
    main()
