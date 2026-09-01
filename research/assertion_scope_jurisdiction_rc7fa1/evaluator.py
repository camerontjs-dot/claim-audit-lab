"""Frozen evaluator for RC7F-A1."""
from __future__ import annotations
from collections import Counter


def validate_cohort(cases: list[dict]) -> None:
    seen_ids=set(); source_gold={}
    for c in cases:
        cid=c["case_id"]
        assert cid not in seen_ids; seen_ids.add(cid)
        text=c["raw_source"]
        obs=c["observation"]
        assert isinstance(text,str) and text
        assert 0 <= obs["start"] < obs["end"] <= len(text)
        assert isinstance(c["gold_scope_path"],list)
        assert isinstance(c["gold_authority_eligible"],bool)
        norm=" ".join(text.lower().split())
        signature=(tuple(c["gold_scope_path"]),c["gold_authority_eligible"],obs.get("polarity","positive"))
        if norm in source_gold:
            assert source_gold[norm]==signature, f"incompatible duplicate gold for {norm!r}"
        source_gold[norm]=signature


def score(cases: list[dict], outputs: list[dict]) -> dict:
    assert len(cases)==len(outputs)
    rows=[]
    false_permits=0; direct_gold=0; direct_hits=0; eligible_pred=0; eligible_correct=0
    exact_path=0; gold_members=0; pred_members=0; member_tp=0; unresolved=0
    pair_groups={}
    punct_supported=0; punct_stable=0
    for c,o in zip(cases,outputs):
        gp=c["gold_scope_path"]; ge=c["gold_authority_eligible"]
        pp=o["scope_path"]; pe=o["authority_eligible"]
        if pe and not ge: false_permits += 1
        if ge:
            direct_gold += 1
            if pe: direct_hits += 1
        if pe:
            eligible_pred += 1
            if ge: eligible_correct += 1
        if pp==gp: exact_path += 1
        gc=Counter(gp); pc=Counter(pp)
        gold_members += sum(gc.values()); pred_members += sum(pc.values())
        member_tp += sum((gc & pc).values())
        if o["scope_status"]=="UNRESOLVED": unresolved += 1
        pid=c.get("pair_id")
        if pid: pair_groups.setdefault(pid,[]).append((c,o))
        if "punctuation_transform" in c.get("tags",[]):
            punct_supported += 1
            if pp==gp and pe==ge: punct_stable += 1
        rows.append({"case_id":c["case_id"],"family":c["family"],"gold_scope_path":gp,"pred_scope_path":pp,"gold_eligible":ge,"pred_eligible":pe,"correct_path":pp==gp})
    meaning_pairs=0; meaning_pairs_correct=0
    for items in pair_groups.values():
        if len(items)!=2: continue
        if items[0][0].get("pair_relation") != "meaning_changing": continue
        meaning_pairs += 1
        if all(o["scope_path"]==c["gold_scope_path"] and o["authority_eligible"]==c["gold_authority_eligible"] for c,o in items):
            meaning_pairs_correct += 1
    prec=eligible_correct/eligible_pred if eligible_pred else 1.0
    return {
        "case_count":len(cases),
        "unsafe_false_permits":false_permits,
        "direct_assertion_recall":direct_hits/direct_gold if direct_gold else 1.0,
        "authority_eligibility_precision":prec,
        "exact_scope_path_accuracy":exact_path/len(cases) if cases else 0.0,
        "scope_membership_precision":member_tp/pred_members if pred_members else 1.0,
        "scope_membership_recall":member_tp/gold_members if gold_members else 1.0,
        "unresolved_rate":unresolved/len(cases) if cases else 0.0,
        "punctuation_scope_stability":punct_stable/punct_supported if punct_supported else 1.0,
        "meaning_changing_pair_accuracy":meaning_pairs_correct/meaning_pairs if meaning_pairs else 1.0,
        "rows":rows,
    }
