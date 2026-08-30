from __future__ import annotations

from itertools import product
from typing import Any, Iterable


def _relation(values: Iterable[bool]) -> str:
    vals = tuple(values)
    if not vals:
        raise ValueError("authority admits no possible worlds")
    if all(vals):
        return "entailment"
    if not any(vals):
        return "contradiction"
    return "neutral"


def _membership_worlds(status: str) -> tuple[bool, ...]:
    if status == "member": return (True,)
    if status == "non_member": return (False,)
    if status == "unknown": return (False, True)
    raise ValueError(status)


def _event_truth(polarity: str) -> bool:
    if polarity == "positive": return True
    if polarity == "negative": return False
    raise ValueError(polarity)


def _oracle_membership_rule(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    worlds: list[bool] = []
    for member in _membership_worlds(a["membership"]):
        same_entity = q["entity"] == a["entity"]
        same_population = q.get("population") == a["population"]
        rule = a["rule"]
        same_predicate = q.get("predicate") == rule["predicate"]
        if q["kind"] == "membership":
            worlds.append(member) if same_entity and same_population else worlds.extend((False, True))
            continue
        if q["kind"] == "rule_applies":
            worlds.append(member) if same_entity and same_population and same_predicate else worlds.extend((False, True))
            continue
        if not (same_entity and same_population and same_predicate):
            worlds.extend((False, True)); continue
        for behavior in (False, True):
            if member and rule["modality"] == "fact" and behavior != _event_truth(rule["polarity"]):
                continue
            if q["kind"] == "behavior_positive": worlds.append(behavior)
            elif q["kind"] == "behavior_negative": worlds.append(not behavior)
            else: raise ValueError(q["kind"])
    return _relation(worlds)


def _oracle_subclass(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    worlds: list[bool] = []
    for base_member in _membership_worlds(a["membership"]):
        for member_a, member_b in product((False, True), repeat=2):
            if a["membership_population"] == "A" and member_a != base_member: continue
            if a["membership_population"] == "B" and member_b != base_member: continue
            if a["subclass_edge"] == "A_sub_B" and member_a and not member_b: continue
            if a["subclass_edge"] == "B_sub_A" and member_b and not member_a: continue
            worlds.append(member_a if q["population"] == "A" else member_b)
    return _relation(worlds)


def _oracle_only(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    worlds: list[bool] = []
    for member in _membership_worlds(a["membership"]):
        perm_domain = {"permitted": (True,), "not_permitted": (False,), "unknown": (False, True)}[a["explicit_permission"]]
        for permitted in perm_domain:
            if a["only_population_may"] and permitted and not member: continue
            if q["entity"] != a["entity"] or q.get("predicate") != a["predicate"]:
                worlds.extend((False, True)); continue
            if q["kind"] == "membership":
                worlds.append(member) if q["population"] == a["population"] else worlds.extend((False, True))
            elif q["kind"] == "permission": worlds.append(permitted)
            else: raise ValueError(q["kind"])
    return _relation(worlds)


def _q_value(q: str, vals: tuple[bool, ...]) -> bool:
    if q == "every": return all(vals)
    if q == "none": return not any(vals)
    if q == "some": return any(vals)
    if q == "not_every": return not all(vals)
    raise ValueError(q)


def _oracle_quantifier(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    members = tuple(a["members"])
    worlds: list[bool] = []
    for p_vals in product((False, True), repeat=len(members)):
        if not _q_value(a["quantifier"], p_vals): continue
        if q["population"] != a["population"]:
            worlds.extend((False, True)); continue
        if q["predicate"] == a["predicate"]:
            worlds.append(_q_value(q["quantifier"], p_vals))
        else:
            for other_vals in product((False, True), repeat=len(members)):
                worlds.append(_q_value(q["quantifier"], other_vals))
    return _relation(worlds)


def _oracle_group(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    atoms = [(scope, pred) for scope in ("group", "member:e0", "member:e1") for pred in ("P", "Q")]
    known = (a["event_scope"], a["predicate"]); known_truth = _event_truth(a["polarity"])
    q_atom = (q["event_scope"], q["predicate"])
    worlds: list[bool] = []
    for bits in product((False, True), repeat=len(atoms)):
        world = dict(zip(atoms, bits, strict=True))
        if world[known] != known_truth: continue
        val = world[q_atom]
        worlds.append(not val if q["polarity"] == "negative" else val)
    return _relation(worlds)


def _oracle_role(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    entities = ("e0", "e1")
    atoms = [(pred, s, o) for pred in ("reviews", "approves") for s in entities for o in entities if s != o]
    ev = a["event"]
    known = (ev["predicate"], ev["roles"]["subject"], ev["roles"]["object"]); known_truth = _event_truth(ev["polarity"])
    q_atom = (q["predicate"], q["roles"]["subject"], q["roles"]["object"])
    worlds: list[bool] = []
    for bits in product((False, True), repeat=len(atoms)):
        world = dict(zip(atoms, bits, strict=True))
        if world[known] != known_truth: continue
        val = world[q_atom]
        worlds.append(not val if q["polarity"] == "negative" else val)
    return _relation(worlds)


def _time_membership(window: str, time: str) -> tuple[bool, ...]:
    if window == "always": return (True,)
    if window == "never": return (False,)
    if window == "unknown": return (False, True)
    if window == "before_only": return (time == "before",)
    if window == "after_only": return (time == "after",)
    raise ValueError(window)


def _oracle_temporal(case: dict[str, Any]) -> str:
    a, q = case["authority"], case["query"]
    worlds: list[bool] = []
    for member in _time_membership(a["membership_window"], q["time"]):
        rule = a["rule"]
        if q["kind"] in {"membership", "rule_applies"}:
            worlds.append(member); continue
        for behavior in (False, True):
            if member and rule["modality"] == "fact" and behavior != _event_truth(rule["polarity"]): continue
            worlds.append(behavior if q["kind"] == "behavior_positive" else not behavior)
    return _relation(worlds)


def relation(case: dict[str, Any]) -> str:
    dim = case["dimension"]
    if dim == "membership_rule": return _oracle_membership_rule(case)
    if dim == "subclass": return _oracle_subclass(case)
    if dim == "only_permission": return _oracle_only(case)
    if dim == "quantifier": return _oracle_quantifier(case)
    if dim == "group_scope": return _oracle_group(case)
    if dim == "role_binding": return _oracle_role(case)
    if dim == "temporal_membership": return _oracle_temporal(case)
    raise ValueError(dim)
