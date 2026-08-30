from __future__ import annotations

from typing import Any


def _known(status: str) -> str:
    return {"member": "entailment", "non_member": "contradiction", "unknown": "neutral"}[status]


def _membership_rule(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    same_entity = q["entity"] == a["entity"]
    same_population = q.get("population") == a["population"]
    same_predicate = q.get("predicate") == a["rule"]["predicate"]
    if q["kind"] == "membership":
        return _known(a["membership"]) if same_entity and same_population else "neutral"
    if q["kind"] == "rule_applies":
        return _known(a["membership"]) if same_entity and same_population and same_predicate else "neutral"
    if not (same_entity and same_population and same_predicate): return "neutral"
    if a["membership"] != "member" or a["rule"]["modality"] != "fact": return "neutral"
    positive = a["rule"]["polarity"] == "positive"
    query_positive = q["kind"] == "behavior_positive"
    return "entailment" if positive == query_positive else "contradiction"


def _subclass(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    base, target, status = a["membership_population"], q["population"], a["membership"]
    if target == base: return _known(status)
    if status != "member": return "neutral"
    if a["subclass_edge"] == "A_sub_B" and base == "A" and target == "B": return "entailment"
    if a["subclass_edge"] == "B_sub_A" and base == "B" and target == "A": return "entailment"
    return "neutral"


def _only(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    if q["entity"] != a["entity"] or q.get("predicate") != a["predicate"]: return "neutral"
    if q["kind"] == "membership":
        if q["population"] != a["population"]: return "neutral"
        if a["explicit_permission"] == "permitted" and a["only_population_may"]: return "entailment"
        return _known(a["membership"])
    perm = a["explicit_permission"]
    if perm == "permitted": return "entailment"
    if perm == "not_permitted": return "contradiction"
    if a["only_population_may"] and a["membership"] == "non_member": return "contradiction"
    return "neutral"


def _quantifier(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    if q["population"] != a["population"] or q["predicate"] != a["predicate"]: return "neutral"
    aq, qq = a["quantifier"], q["quantifier"]
    if aq == qq: return "entailment"
    entails = {"every": {"some"}, "none": {"not_every"}, "some": set(), "not_every": set()}
    contradictions = {"every": {"none", "not_every"}, "none": {"every", "some"}, "some": {"none"}, "not_every": {"every"}}
    if qq in entails[aq]: return "entailment"
    if qq in contradictions[aq]: return "contradiction"
    return "neutral"


def _group(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    if a["event_scope"] != q["event_scope"] or a["predicate"] != q["predicate"]: return "neutral"
    return "entailment" if a["polarity"] == q["polarity"] else "contradiction"


def _role(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    ev = a["event"]
    same_atom = ev["predicate"] == q["predicate"] and ev["roles"]["subject"] == q["roles"]["subject"] and ev["roles"]["object"] == q["roles"]["object"]
    if not same_atom: return "neutral"
    return "entailment" if ev["polarity"] == q["polarity"] else "contradiction"


def _temporal_status(window: str, time: str) -> str:
    if window == "unknown": return "unknown"
    if window == "always": return "member"
    if window == "never": return "non_member"
    if window == "before_only": return "member" if time == "before" else "non_member"
    if window == "after_only": return "member" if time == "after" else "non_member"
    raise ValueError(window)


def _temporal(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    status = _temporal_status(a["membership_window"], q["time"])
    if q["kind"] in {"membership", "rule_applies"}: return _known(status)
    if status != "member" or a["rule"]["modality"] != "fact": return "neutral"
    positive = a["rule"]["polarity"] == "positive"
    query_positive = q["kind"] == "behavior_positive"
    return "entailment" if positive == query_positive else "contradiction"


def relation(case: dict[str, Any]) -> str:
    return {"membership_rule": _membership_rule, "subclass": _subclass, "only_permission": _only,
            "quantifier": _quantifier, "group_scope": _group, "role_binding": _role,
            "temporal_membership": _temporal}[case["dimension"]](case)
