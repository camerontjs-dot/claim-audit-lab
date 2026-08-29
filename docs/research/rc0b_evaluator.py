#!/usr/bin/env python3
"""Frozen RC0B behavioral evaluator. No candidate code is imported."""
from __future__ import annotations
import argparse, json
from pathlib import Path

REQUIRED = tuple("ABCDEFGHIJK")
ARCH_RELEVANT = set("ADEGHIJK")

def _same(xs):
    return all(x == xs[0] for x in xs[1:]) if xs else True

def evaluate(c):
    r = {}
    # A: materially distinct causes represented.
    causes = set(c.get("distinguishable_causes", []))
    required_causes = {"support","refutation","abstention","exclusion","unresolved","execution_failure"}
    r["A"] = required_causes <= causes

    # B/I: nomination-role-only mutation leaves measurement invariant.
    nom = c.get("nomination_mutation", {})
    ms = [nom.get(k, {}).get("measurement") for k in ("support","counter")]
    r["B"] = len(ms) == 2 and None not in ms and _same(ms)
    r["I"] = r["B"]

    # C: suppressed/nondeciding evidence remains retained.
    ev = c.get("evidence_retention", {})
    r["C"] = bool(ev.get("suppressed_retained")) and bool(ev.get("nondeciding_retained"))

    # D: typed participation states are representable.
    parts = set(c.get("participation_states", []))
    r["D"] = {"retained","deciding","residual","excluded","unresolved"} <= parts

    # E: assessment execution ladder is explicit and noncollapsed.
    states = set(c.get("assessment_execution_states", []))
    r["E"] = {
        "performed-positive","performed-adverse","performed-unknown",
        "not-performed","not-applicable","failed"
    } <= states and not c.get("infers_positive_from_absence", False)

    # F: execution failures are not encoded only as epistemic insufficiency.
    ex = c.get("execution_controls", {})
    r["F"] = (
        ex.get("completed_assessed") == "completed"
        and ex.get("completed_not_checkable") == "completed"
        and ex.get("assessment_failed") == "assessment-failed"
        and ex.get("incomplete") == "incomplete"
        and ex.get("parser_rule_model_failed") == "execution-failed"
    )

    # G: exact causal basis requires actual replay.
    causal = c.get("causal", {})
    if causal.get("claims_exact_basis"):
        r["G"] = bool(causal.get("replay_performed")) and bool(causal.get("classification_derived_from_replay"))
    else:
        r["G"] = causal.get("classification") in {"unavailable","unknown"}

    # H: strong counterfactual changes derived behavior with evidence/measurement invariant.
    p = c.get("policy_counterfactual", {})
    r["H"] = (
        p.get("evidence_hash_a") == p.get("evidence_hash_b")
        and p.get("measurement_hash_a") == p.get("measurement_hash_b")
        and p.get("policy_a") != p.get("policy_b")
        and (
            p.get("participation_a") != p.get("participation_b")
            or p.get("terminal_a") != p.get("terminal_b")
        )
    )

    # J: trust fact and proposition assessment are separate fields and no shortcut.
    trust = c.get("trust_separation", {})
    r["J"] = (
        bool(trust.get("source_fact_separate"))
        and bool(trust.get("assessment_state_separate"))
        and not trust.get("trust_implies_assessment", False)
    )

    # K: distributed partial evidence retained without unsupported composition.
    agg = c.get("distributed", {})
    r["K"] = (
        set(agg.get("retained", [])) == {"P-part-a","P-part-b"}
        and agg.get("aggregation_state") == "unresolved"
        and agg.get("composition_rule") is None
    )
    return r

def clears(result):
    return all(result.get(k) is True for k in REQUIRED)

def weak_controls():
    good = {
      "distinguishable_causes":["support","refutation","abstention","exclusion","unresolved","execution_failure"],
      "nomination_mutation":{"support":{"measurement":"M"},"counter":{"measurement":"M"}},
      "evidence_retention":{"suppressed_retained":True,"nondeciding_retained":True},
      "participation_states":["retained","deciding","residual","excluded","unresolved"],
      "assessment_execution_states":["performed-positive","performed-adverse","performed-unknown","not-performed","not-applicable","failed"],
      "infers_positive_from_absence":False,
      "execution_controls":{"completed_assessed":"completed","completed_not_checkable":"completed","assessment_failed":"assessment-failed","incomplete":"incomplete","parser_rule_model_failed":"execution-failed"},
      "causal":{"claims_exact_basis":False,"classification":"unavailable"},
      "policy_counterfactual":{"evidence_hash_a":"E","evidence_hash_b":"E","measurement_hash_a":"M","measurement_hash_b":"M","policy_a":"P1","policy_b":"P2","participation_a":"deciding","participation_b":"residual","terminal_a":"contradicted","terminal_b":"not_checkable"},
      "trust_separation":{"source_fact_separate":True,"assessment_state_separate":True,"trust_implies_assessment":False},
      "distributed":{"retained":["P-part-a","P-part-b"],"aggregation_state":"unresolved","composition_rule":None},
    }
    import copy
    w={}
    w["W1"]=copy.deepcopy(good); w["W1"]["distinguishable_causes"]=["abstention"]
    w["W1"]["participation_states"]=[]
    w["W1"]["assessment_execution_states"]=[]
    w["W2"]=copy.deepcopy(good); w["W2"]["participation_states"]=[]; w["W2"]["assessment_execution_states"]=[]
    w["W3"]=copy.deepcopy(good); w["W3"]["trust_separation"]["trust_implies_assessment"]=True; w["W3"]["assessment_execution_states"]=["performed-positive","performed-adverse"]
    w["W4"]=copy.deepcopy(good); w["W4"]["causal"]={"claims_exact_basis":True,"replay_performed":False,"classification_derived_from_replay":False}
    w["W5"]=copy.deepcopy(good); w["W5"]["policy_counterfactual"]["participation_b"]="deciding"; w["W5"]["policy_counterfactual"]["terminal_b"]="contradicted"
    return w

def self_test():
    out={}
    for name,c in weak_controls().items():
        res=evaluate(c)
        out[name]={"result":res,"clears":clears(res),"arch_failures":[k for k in ARCH_RELEVANT if not res.get(k)]}
        assert not out[name]["clears"], name
        assert out[name]["arch_failures"], name
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("candidate", nargs="?")
    ap.add_argument("--self-test", action="store_true")
    args=ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True)); return
    if not args.candidate:
        ap.error("candidate JSON required unless --self-test")
    c=json.loads(Path(args.candidate).read_text())
    res=evaluate(c)
    print(json.dumps({"candidate":c.get("name"),"properties":res,"clears":clears(res)}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
