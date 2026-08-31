"""Evaluator for RC7F-A."""
from __future__ import annotations
from collections import Counter, defaultdict
import re

def normalize_source(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())

def validate_cohort(cases: list[dict]) -> None:
    seen={}
    for case in cases:
        key=normalize_source(case["raw_source"])
        gold=(case["gold_scope_status"], bool(case["gold_authority_eligible"]))
        if key in seen and seen[key] != gold:
            raise ValueError(f"incompatible_gold_for_duplicate_source:{key!r}:{seen[key]}!={gold}")
        seen[key]=gold

def score(cases: list[dict], outputs: dict[str,dict]) -> dict:
    validate_cohort(cases)
    false_permits=false_rejects=correct_status=unresolved=0
    eligible_gold=eligible_pred=eligible_tp=0
    by_family=defaultdict(lambda: Counter(total=0,false_permit=0,false_reject=0,status_correct=0))
    confusion=Counter()
    for case in cases:
        out=outputs[case["case_id"]]
        gold_e=bool(case["gold_authority_eligible"])
        pred_e=bool(out["authority_eligible"])
        gold_s=case["gold_scope_status"]
        pred_s=out["scope_status"]
        fam=case["family"]
        by_family[fam]["total"] += 1
        if pred_e and not gold_e:
            false_permits += 1; by_family[fam]["false_permit"] += 1
        if gold_e and not pred_e:
            false_rejects += 1; by_family[fam]["false_reject"] += 1
        if gold_s == pred_s:
            correct_status += 1; by_family[fam]["status_correct"] += 1
        if pred_s == "UNRESOLVED":
            unresolved += 1
        eligible_gold += int(gold_e)
        eligible_pred += int(pred_e)
        eligible_tp += int(gold_e and pred_e)
        confusion[(gold_s,pred_s)] += 1
    precision = eligible_tp / eligible_pred if eligible_pred else (1.0 if eligible_gold == 0 else 0.0)
    recall = eligible_tp / eligible_gold if eligible_gold else 1.0
    return {
        "case_count": len(cases),
        "unsafe_false_permits": false_permits,
        "safe_false_rejects": false_rejects,
        "authority_eligibility_precision": precision,
        "direct_assertion_recall": recall,
        "scope_status_accuracy": correct_status/len(cases) if cases else 0.0,
        "unresolved_rate": unresolved/len(cases) if cases else 0.0,
        "by_family": {k:dict(v) for k,v in sorted(by_family.items())},
        "confusion": [{"gold":g,"pred":p,"count":n} for (g,p),n in sorted(confusion.items())],
    }
