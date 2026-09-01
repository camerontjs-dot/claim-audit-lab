"""Frozen RC7F-B1 evaluator."""
from __future__ import annotations

def validate_cohort(cases):
    ids=set(); sig={}
    for c in cases:
        assert c["case_id"] not in ids; ids.add(c["case_id"])
        text=c["raw_source"]; assert isinstance(text,str) and text
        norm=" ".join(text.lower().split()); gold=c.get("gold")
        signature=None if gold is None else (gold["left"],gold["relation"],gold["right"])
        if norm in sig: assert sig[norm]==signature, f"incompatible duplicate gold: {norm}"
        sig[norm]=signature

def _key(p): return (p["left"],p["relation"],p["right"])

def score(cases,outputs):
    tp=fp=fn=0; dir_ok=dir_n=attach_ok=attach_n=0; neg_fp=0; unresolved=0; rows=[]; groups={}
    for c,o in zip(cases,outputs):
        gold=c.get("gold"); props=o["proposals"]
        if o["status"]=="UNRESOLVED": unresolved+=1
        if gold is None:
            fp += len(props); neg_fp += len(props)
            correct=not props
        else:
            g=(gold["left"],gold["relation"],gold["right"])
            matches=[p for p in props if _key(p)==g]
            if matches: tp+=1; correct=True
            else: fn+=1; fp+=len(props); correct=False
            if props:
                dir_n+=1; attach_n+=1
                dir_ok += int(props[0]["relation"]==gold["relation"])
                attach_ok += int(props[0]["left"]==gold["left"] and props[0]["right"]==gold["right"])
        pid=c.get("pair_id")
        if pid: groups.setdefault(pid,[]).append((c,o,correct))
        rows.append({"case_id":c["case_id"],"family":c["family"],"gold":gold,"proposals":props,"correct":correct})
    pair_states={"stable_correct":0,"stable_abstention":0,"stable_wrong":0,"meaning_changing_correct":0,"meaning_changing_total":0}
    for items in groups.values():
        if len(items)!=2: continue
        rel=items[0][0].get("pair_relation")
        if rel=="meaning_preserving":
            if all(x[2] for x in items): pair_states["stable_correct"]+=1
            elif all(not x[1]["proposals"] for x in items): pair_states["stable_abstention"]+=1
            else: pair_states["stable_wrong"]+=1
        elif rel=="meaning_changing":
            pair_states["meaning_changing_total"]+=1
            if all(x[2] for x in items): pair_states["meaning_changing_correct"]+=1
    precision=tp/(tp+fp) if tp+fp else 1.0
    recall=tp/(tp+fn) if tp+fn else 1.0
    return {"case_count":len(cases),"true_positives":tp,"false_proposals":fp,"misses":fn,
            "typed_precision":precision,"typed_recall":recall,"direction_accuracy":dir_ok/dir_n if dir_n else 1.0,
            "attachment_accuracy":attach_ok/attach_n if attach_n else 1.0,"false_proposals_on_negative":neg_fp,
            "unresolved_rate":unresolved/len(cases) if cases else 0.0,"pair_states":pair_states,"rows":rows}
