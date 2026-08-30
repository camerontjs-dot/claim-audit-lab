from __future__ import annotations

import argparse, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from research.text_to_typed_authority_extraction_rc6.build_cohort import canonical_bytes, materialize
from research.text_to_typed_authority_extraction_rc6 import extractor_regex, extractor_tokens
from research.population_semantics_contract_rc5b.consumer import relation

EXPECTED_COHORT_SHA256 = "820b5a64cf4187998f2c4b416293c8fd0a577b564cab31be22dddd4ace822d23"


def _json_key(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _diff_paths(expected: Any, actual: Any, prefix: str = "") -> list[str]:
    if type(expected) is not type(actual): return [prefix or "$type"]
    if isinstance(expected, dict):
        out=[]
        for k in sorted(set(expected) | set(actual)):
            p=f"{prefix}.{k}" if prefix else k
            if k not in expected or k not in actual: out.append(p)
            else: out.extend(_diff_paths(expected[k], actual[k], p))
        return out
    if isinstance(expected, list):
        if len(expected)!=len(actual): return [prefix or "$list"]
        out=[]
        for i,(e,a) in enumerate(zip(expected,actual)): out.extend(_diff_paths(e,a,f"{prefix}[{i}]"))
        return out
    return [] if expected==actual else [prefix or "$value"]


def _system_result(name: str, fn: Callable[[str,str], dict[str,Any]], cases: list[dict[str,Any]]) -> tuple[dict[str,Any], list[dict[str,Any]]]:
    rows=[]; family=defaultdict(lambda: Counter(total=0)); field_fail=Counter()
    resolved_expected=[c for c in cases if c["expected_status"]=="resolved"]
    unknown_expected=[c for c in cases if c["expected_status"]=="unknown"]
    neutral_expected=[c for c in resolved_expected if c["expected_relation"]=="neutral"]
    for c in cases:
        out=fn(c["text"],c["query_text"])
        status=out.get("status")
        pred_case=out.get("case") if status=="resolved" else None
        pred_relation=None
        consumer_error=None
        if status=="resolved":
            try: pred_relation=relation(pred_case)
            except Exception as exc: consumer_error=f"{type(exc).__name__}:{exc}"
        expected_unknown=c["expected_status"]=="unknown"
        status_correct=(status==c["expected_status"])
        object_exact=(pred_case==c["expected_case"]) if not expected_unknown and status=="resolved" else False
        relation_correct=(pred_relation==c["expected_relation"]) if not expected_unknown and status=="resolved" and consumer_error is None else False
        fabrication=expected_unknown and status=="resolved"
        false_unknown=(not expected_unknown) and status!="resolved"
        reason_correct=expected_unknown and status=="unknown" and out.get("reason")==c["family"]
        diffs=[]
        if not expected_unknown and status=="resolved" and not object_exact:
            diffs=_diff_paths(c["expected_case"],pred_case)
            field_fail.update(diffs)
        f=family[c["family"]]; f["total"]+=1; f["status_correct"]+=int(status_correct); f["object_exact"]+=int(object_exact); f["relation_correct"]+=int(relation_correct); f["fabrication"]+=int(fabrication); f["false_unknown"]+=int(false_unknown)
        rows.append({"case_id":c["case_id"],"family":c["family"],"expected_status":c["expected_status"],"expected_relation":c["expected_relation"],"predicted":out,"predicted_relation":pred_relation,"consumer_error":consumer_error,"status_correct":status_correct,"object_exact":object_exact,"relation_correct":relation_correct,"fabrication":fabrication,"false_unknown":false_unknown,"reason_correct":reason_correct,"field_diff_paths":diffs})
    summary={
        "name":name,
        "n_cases":len(cases),
        "status_accuracy":sum(r["status_correct"] for r in rows)/len(cases),
        "resolved_object_exact":sum(r["object_exact"] for r in rows)/len(resolved_expected),
        "resolved_relation_accuracy_all":sum(r["relation_correct"] for r in rows)/len(resolved_expected),
        "resolved_coverage":sum(r["expected_status"]=="resolved" and r["predicted"].get("status")=="resolved" for r in rows)/len(resolved_expected),
        "fabrication_rate_unknown":sum(r["fabrication"] for r in rows)/len(unknown_expected),
        "false_unknown_rate_in_schema":sum(r["false_unknown"] for r in rows)/len(resolved_expected),
        "neutral_resolution_rate":sum(r["case_id"] in {c["case_id"] for c in neutral_expected} and r["predicted"].get("status")=="resolved" for r in rows)/len(neutral_expected),
        "neutral_relation_accuracy":sum(r["case_id"] in {c["case_id"] for c in neutral_expected} and r["relation_correct"] for r in rows)/len(neutral_expected),
        "unknown_reason_accuracy":sum(r["reason_correct"] for r in rows)/len(unknown_expected),
        "consumer_errors":sum(r["consumer_error"] is not None for r in rows),
        "field_failure_counts":dict(field_fail.most_common()),
        "family":{k:dict(v) for k,v in sorted(family.items())},
    }
    return summary,rows


def _consensus(a: dict[str,Any], b: dict[str,Any]) -> dict[str,Any]:
    if a.get("status")=="resolved" and b.get("status")=="resolved" and _json_key(a.get("case"))==_json_key(b.get("case")):
        return {"status":"resolved","case":a["case"]}
    if a.get("status")=="unknown" and b.get("status")=="unknown":
        reason=a.get("reason") if a.get("reason")==b.get("reason") else "extractor_disagreement"
        return {"status":"unknown","reason":reason}
    return {"status":"unknown","reason":"extractor_disagreement"}


def _mutation_score(rows: list[dict[str,Any]], pairs: list[dict[str,Any]]) -> dict[str,Any]:
    by={r["case_id"]:r for r in rows}; details=[]; passed=0
    for p in pairs:
        ra,rb=by[p["a"]],by[p["b"]]
        pa=ra["status_correct"] and (ra["expected_status"]=="unknown" or (ra["object_exact"] and ra["relation_correct"]))
        pb=rb["status_correct"] and (rb["expected_status"]=="unknown" or (rb["object_exact"] and rb["relation_correct"]))
        ok=bool(pa and pb); passed+=ok; details.append({**p,"pass":ok})
    return {"passed":passed,"total":len(pairs),"details":details}


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",required=True); args=ap.parse_args(); out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    data=materialize(); raw=canonical_bytes(data); sha=hashlib.sha256(raw).hexdigest(); assert sha==EXPECTED_COHORT_SHA256
    cases=data["cases"]
    # Gold-object sanity: the unchanged RC5B consumer must reproduce the preregistered relation from the gold typed object.
    gold_disagreements=[]
    for c in cases:
        if c["expected_status"]=="resolved":
            got=relation(c["expected_case"])
            if got!=c["expected_relation"]: gold_disagreements.append({"case_id":c["case_id"],"expected":c["expected_relation"],"consumer":got})
    if gold_disagreements: raise AssertionError({"gold_consumer_disagreements":gold_disagreements})

    a_summary,a_rows=_system_result("regex",extractor_regex.extract,cases)
    b_summary,b_rows=_system_result("tokens",extractor_tokens.extract,cases)
    amap={r["case_id"]:r for r in a_rows}; bmap={r["case_id"]:r for r in b_rows}
    def cons_fn(text: str,query: str) -> dict[str,Any]: return _consensus(extractor_regex.extract(text,query),extractor_tokens.extract(text,query))
    c_summary,c_rows=_system_result("consensus",cons_fn,cases)
    authority_disagree=0; strict_disagree=0; disagreement_cases=[]
    for c in cases:
        ar=amap[c["case_id"]]["predicted"]; br=bmap[c["case_id"]]["predicted"]
        strict=(_json_key(ar)!=_json_key(br))
        authority=(ar.get("status")!=br.get("status") or (ar.get("status")=="resolved" and _json_key(ar.get("case"))!=_json_key(br.get("case"))))
        strict_disagree+=strict; authority_disagree+=authority
        if authority: disagreement_cases.append(c["case_id"])
    mut={"regex":_mutation_score(a_rows,data["mutation_pairs"]),"tokens":_mutation_score(b_rows,data["mutation_pairs"]),"consensus":_mutation_score(c_rows,data["mutation_pairs"])}
    measurements={"cohort_sha256":sha,"systems":{"regex":{"summary":a_summary,"rows":a_rows},"tokens":{"summary":b_summary,"rows":b_rows},"consensus":{"summary":c_summary,"rows":c_rows}},"extractor_disagreement":{"authority_disagreements":authority_disagree,"strict_output_disagreements":strict_disagree,"n_cases":len(cases),"case_ids":disagreement_cases},"mutations":mut}
    results={"cohort_sha256":sha,"n_cases":len(cases),"n_in_schema":70,"n_expected_unknown":30,"gold_consumer_disagreements":0,"systems":{k:v["summary"] if isinstance(v,dict) and "summary" in v else v for k,v in measurements["systems"].items()},"extractor_disagreement":measurements["extractor_disagreement"],"mutations":{k:{"passed":v["passed"],"total":v["total"]} for k,v in mut.items()}}
    # Preserve every incorrect scientific case.
    counter=[]
    for name,rows in (("regex",a_rows),("tokens",b_rows),("consensus",c_rows)):
        for r in rows:
            ok=r["status_correct"] and (r["expected_status"]=="unknown" or (r["object_exact"] and r["relation_correct"]))
            if not ok: counter.append({"system":name,**r})
    for name,obj in (("MEASUREMENTS.json",measurements),("RESULTS.json",results),("COUNTEREXAMPLES.json",counter)):
        (out/name).write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print(json.dumps(results,indent=2,sort_keys=True))

if __name__=="__main__": main()
