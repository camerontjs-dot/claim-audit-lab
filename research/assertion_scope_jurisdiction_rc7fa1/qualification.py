"""Pre-held-out qualification for RC7F-A1."""
from __future__ import annotations
import json
from pathlib import Path
from .scope_firewall import classify

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

def obs(text: str, clause: str, polarity: str = "positive") -> dict:
    start = text.index(clause)
    return {"predicate":"inspect","subject":"lena","object":"batch r","polarity":polarity,"start":start,"end":start+len(clause)}

PROBES = [
    ("direct", "Lena inspected batch r.", "Lena inspected batch r.", "positive", [], True),
    ("negative", "Lena did not inspect batch r.", "Lena did not inspect batch r.", "negative", [], True),
    ("supposed-comma", "Supposedly, Lena inspected batch r.", "Lena inspected batch r.", "positive", ["UNRESOLVED_EVIDENTIAL"], False),
    ("supposed-colon", "Supposedly: Lena inspected batch r.", "Lena inspected batch r.", "positive", ["UNRESOLVED_EVIDENTIAL"], False),
    ("purported-comma", "Purportedly, Lena inspected batch r.", "Lena inspected batch r.", "positive", ["UNRESOLVED_EVIDENTIAL"], False),
    ("reported-comma", "Reportedly, Lena inspected batch r.", "Lena inspected batch r.", "positive", ["UNRESOLVED_EVIDENTIAL"], False),
    ("alleged-comma", "Allegedly, Lena inspected batch r.", "Lena inspected batch r.", "positive", ["UNRESOLVED_EVIDENTIAL"], False),
    ("domain-trap", "The supposedly field is archived. Lena inspected batch r.", "Lena inspected batch r.", "positive", [], True),
    ("substring-trap", "The purportedlyNamed column is archived. Lena inspected batch r.", "Lena inspected batch r.", "positive", [], True),
    ("quoted", 'Omar said, "Lena inspected batch r."', "Lena inspected batch r.", "positive", ["ATTRIBUTED"], False),
    ("reported", "Omar reported that Lena inspected batch r.", "Lena inspected batch r.", "positive", ["ATTRIBUTED"], False),
    ("if-ant", "If Lena inspects batch r, Omar signs form z.", "Lena inspects batch r", "positive", ["CONDITIONAL_ANTECEDENT"], False),
    ("if-cons", "If Omar signs form z, Lena inspects batch r.", "Lena inspects batch r.", "positive", ["CONDITIONAL_CONSEQUENT"], False),
    ("nested-cond-attr", "If Omar reported that Lena inspected batch r, Nia signs form z.", "Lena inspected batch r", "positive", ["CONDITIONAL_ANTECEDENT","ATTRIBUTED"], False),
    ("nested-attr-epi", "Omar reported that Lena probably inspected batch r.", "Lena probably inspected batch r.", "positive", ["ATTRIBUTED","EPISTEMIC"], False),
    ("nested-cond-epi", "If Lena probably inspected batch r, Omar signs form z.", "Lena probably inspected batch r", "positive", ["CONDITIONAL_ANTECEDENT","EPISTEMIC"], False),
    ("deontic", "Only inspectors may inspect batch r.", "inspectors may inspect batch r.", "positive", ["DEONTIC"], False),
    ("quantified", "Every inspector inspected batch r.", "inspector inspected batch r.", "positive", ["QUANTIFIED"], False),
    ("whether", "Whether Lena inspected batch r remains disputed.", "Lena inspected batch r", "positive", ["UNRESOLVED_EVIDENTIAL"], False),
]

def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    rows=[]; failures=[]
    for name,text,clause,polarity,path,eligible in PROBES:
        out=classify(text,obs(text,clause,polarity))
        ok=out["scope_path"]==path and out["authority_eligible"]==eligible
        row={"name":name,"text":text,"expected_path":path,"expected_eligible":eligible,"observed":out,"ok":ok}
        rows.append(row)
        if not ok: failures.append(row)
    controls={
        "case_id_not_input":"case_id" not in classify.__code__.co_varnames,
        "unknown_anchor_abstains":classify("abc",{"start":9,"end":10,"polarity":"positive"})["scope_status"]=="UNRESOLVED",
        "empty_scope_is_only_eligibility_path":all((not r["observed"]["scope_path"]) == r["observed"]["authority_eligible"] for r in rows),
    }
    if not all(controls.values()): failures.append({"controls":controls})
    payload={"qualification_version":"rc7fa1-q1","probe_count":len(rows),"rows":rows,"controls":controls,"failure_count":len(failures)}
    (RESULTS/"QUALIFICATION.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"probe_count":len(rows),"failure_count":len(failures),"controls":controls},indent=2))
    if failures: raise SystemExit(1)

if __name__=="__main__": main()
