"""Fresh deterministic extractor for typed-authority contract v1."""

from __future__ import annotations

import re
from typing import Optional

_REASONS = {"ambiguous_reference", "insufficient_authority", "ontology_escape", "unparsed"}
_COLLECTIVES = {"group", "team", "committee", "crew", "panel", "board", "delegation", "unit", "squad", "council", "jury", "staff"}
_IRREG = {
    "was": "be", "were": "be", "did": "do", "done": "do", "had": "have",
    "went": "go", "gone": "go", "made": "make", "took": "take", "taken": "take",
    "gave": "give", "given": "give", "wrote": "write", "written": "write",
    "met": "meet", "saw": "see", "seen": "see", "led": "lead", "sent": "send",
    "brought": "bring", "bought": "buy", "taught": "teach", "found": "find",
    "held": "hold", "left": "leave", "read": "read", "became": "become",
}

def _unknown(reason: str) -> dict:
    return {"status": "unknown", "reason": reason}

def _resolved(dimension: str, authority: dict, query: dict) -> dict:
    return {"status": "resolved", "case": {"dimension": dimension, "authority": authority, "query": query}}

def _space(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def _clean(s: str) -> str:
    return _space(re.sub(r'^[\s"“”‘’\'()[\]{}]+|[\s"“”‘’\'()[\]{}.,;:!?]+$', "", _space(s)))

def _sentences(text: str) -> list[str]:
    if not _space(text):
        return []
    return [_clean(x) for x in re.split(r"(?<=[.!?;])\s+|\s*;\s*", _space(text.replace("—", "-"))) if _clean(x)]

def _cmp(s: str) -> str:
    s = _clean(s).lower()
    s = re.sub(r"^(?:the|a|an)\s+", "", s)
    s = re.sub(r"^members?\s+(?:of|in)\s+(?:the\s+)?", "", s)
    return _space(re.sub(r"[^a-z0-9' -]+", "", s))

def _singular(s: str) -> str:
    w = _cmp(s).split()
    if not w:
        return ""
    x = w[-1]
    if len(x) > 4 and x.endswith("ies"):
        x = x[:-3] + "y"
    elif len(x) > 4 and x.endswith(("ches", "shes", "xes", "zes")):
        x = x[:-2]
    elif len(x) > 3 and x.endswith("s") and not x.endswith(("ss", "us", "is")):
        x = x[:-1]
    w[-1] = x
    return " ".join(w)

def _same_class(a: str, b: str) -> bool:
    return _singular(a) == _singular(b)

def _base(word: str) -> str:
    w = word.lower()
    if w in _IRREG:
        return _IRREG[w]
    if len(w) > 4 and w.endswith(("ied", "ies")):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith("ing"):
        x = w[:-3]
        if len(x) > 2 and x[-1] == x[-2]:
            x = x[:-1]
        return x + "e" if x.endswith("v") else x
    if len(w) > 3 and w.endswith("ed"):
        x = w[:-2]
        if x.endswith("i"):
            return x[:-1] + "y"
        if len(x) > 2 and x[-1] == x[-2]:
            x = x[:-1]
        return x + "e" if x.endswith(("at", "it", "iz", "ov", "ur")) else x
    if len(w) > 4 and w.endswith("es"):
        return w[:-2] if w.endswith(("ches", "shes", "xes", "zes", "oes")) else w[:-1]
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
        return w[:-1]
    return w

def _predicate(s: str) -> str:
    s = _clean(re.sub(r"^to\s+", "", _clean(s), flags=re.I))
    if not s:
        return ""
    words = s.split()
    words[0] = _base(words[0])
    return " ".join(words)

def _escape(text: str, query: str) -> bool:
    joined = f" {text} {query} ".lower()
    pats = [
        r"\b\d+(?:\.\d+)?\s*%", r"\b(?:percent|percentage|majority|minority|most|many|few|several)\b",
        r"\b(?:probable|probably|probability|likely|unlikely|chance|odds)\b",
        r"\b(?:exactly|at least|at most)\s+\d+\b", r"\b(?:more|fewer|less)\s+than\b",
        r"\b(?:unless|except(?:ing)?|provided that|only if|if and only if)\b",
        r"\bif\b.+\bthen\b", r"\beither\b.+\bor\b",
    ]
    return any(re.search(p, joined, re.I) for p in pats)

def _ambiguous(text: str, query: str) -> bool:
    if not re.search(r"\b(?:he|she|they|them|their|his|her|it|its)\b", f"{text} {query}", re.I):
        return False
    names = [x for x in re.findall(r"\b[A-Z][a-z]+\b", text) if x not in {"Only", "Every", "All", "Some", "No", "Not", "Before", "After", "The", "It"}]
    return len(set(names)) >= 2

def _memberships(text: str) -> list[tuple[str, str, str]]:
    out = []
    for s in _sentences(text):
        m = re.fullmatch(r"(?:it is )?unknown whether (?P<e>.+?) (?:is|was) (?:a |an |a member of (?:the )?|one of (?:the )?)(?P<p>.+)", s, re.I)
        if m:
            out.append((_clean(m["e"]), _clean(m["p"]), "unknown")); continue
        m = re.fullmatch(r"(?P<e>.+?)(?:'s|’s) membership in (?:the )?(?P<p>.+?) (?:is|was) unknown", s, re.I)
        if m:
            out.append((_clean(m["e"]), _clean(m["p"]), "unknown")); continue
        m = re.fullmatch(r"(?P<e>.+?) (?:is|was|remains?|remained) (?P<n>not )?(?:a |an |a member of (?:the )?|one of (?:the )?)(?P<p>.+)", s, re.I)
        if m and not re.match(r"(?:permitted|allowed|authorized|required)\b", m["p"], re.I):
            out.append((_clean(m["e"]), _clean(m["p"]), "non_member" if m["n"] else "member")); continue
        m = re.fullmatch(r"(?P<e>.+?) (?P<n>does not |doesn't |did not |didn't )?(?:belong|belongs|belonged) to (?:the )?(?P<p>.+)", s, re.I)
        if m:
            out.append((_clean(m["e"]), _clean(m["p"]), "non_member" if m["n"] else "member"))
    uniq = []
    for x in out:
        if x not in uniq:
            uniq.append(x)
    return uniq

def _q_membership(query: str) -> Optional[tuple[str, str]]:
    q = _clean(query)
    pats = [
        r"(?:is|was) (?P<e>.+?) (?:a |an |a member of (?:the )?|one of (?:the )?)(?P<p>.+)",
        r"(?:does|did) (?P<e>.+?) belong to (?:the )?(?P<p>.+)",
        r"(?P<e>.+?) (?:is|was) (?:a |an |a member of (?:the )?|one of (?:the )?)(?P<p>.+)",
    ]
    for p in pats:
        m = re.fullmatch(p, q, re.I)
        if m:
            return _clean(m["e"]), _clean(m["p"])
    return None

def _rule(text: str, pop_hint: str) -> Optional[dict]:
    for s in _sentences(text):
        if re.match(r"^(?:only|every|all|some|no|none|not every|not all)\b", s, re.I):
            continue
        if re.search(r"\b(?:member of|belongs? to|subclass|kind of|type of)\b", s, re.I):
            continue
        words = s.split()
        for i in range(1, min(6, len(words) - 1) + 1):
            subject, rest = " ".join(words[:i]), " ".join(words[i:])
            if not _same_class(subject, pop_hint):
                continue
            modality, polarity = "fact", "positive"
            if re.match(r"^(?:must|shall) not\b", rest, re.I):
                modality, polarity = "obligation", "negative"
                rest = re.sub(r"^(?:must|shall) not\s+", "", rest, flags=re.I)
            elif re.match(r"^(?:must|shall)\b", rest, re.I):
                modality = "obligation"
                rest = re.sub(r"^(?:must|shall)\s+", "", rest, flags=re.I)
            elif re.match(r"^are required to\b", rest, re.I):
                modality = "obligation"
                rest = re.sub(r"^are required to\s+", "", rest, flags=re.I)
            elif re.match(r"^(?:do|does) not\b", rest, re.I):
                polarity = "negative"
                rest = re.sub(r"^(?:do|does) not\s+", "", rest, flags=re.I)
            pred = _predicate(rest)
            if pred and pred.split()[0] not in {"is", "are", "was", "were"}:
                return {"population": _clean(subject), "predicate": pred, "modality": modality, "polarity": polarity}
    return None

def _q_behavior(query: str, entity: str, pred: str) -> Optional[str]:
    q = _clean(query)
    pats = [
        r"(?:does|did|will|must|shall) (?P<e>.+?) (?P<n>not )?(?P<p>.+)",
        r"(?P<e>.+?) (?P<n>does not |did not |will not |must not |shall not )?(?P<p>.+)",
    ]
    for p in pats:
        m = re.fullmatch(p, q, re.I)
        if m and _cmp(m["e"]) == _cmp(entity) and _cmp(_predicate(m["p"])) == _cmp(pred):
            return "behavior_negative" if m["n"] else "behavior_positive"
    return None

def _q_rule(query: str, entity: str) -> bool:
    q = _clean(query)
    return bool(re.fullmatch(rf"(?:does|did) (?:the )?.*rule apply to {re.escape(entity)}", q, re.I)
                or re.fullmatch(rf"(?:the )?.*rule applies to {re.escape(entity)}", q, re.I))

def _membership_rule(text: str, query: str) -> Optional[dict]:
    found = []
    for entity, pop0, membership in _memberships(text):
        rule = _rule(text, pop0)
        if not rule:
            continue
        qm = _q_membership(query)
        if qm and _cmp(qm[0]) == _cmp(entity) and _same_class(qm[1], rule["population"]):
            kind = "membership"
        elif _q_rule(query, entity):
            kind = "rule_applies"
        else:
            kind = _q_behavior(query, entity, rule["predicate"])
        if kind:
            auth = {"entity": entity, "population": rule["population"], "membership": membership, "rule": rule}
            qobj = {"kind": kind, "entity": entity, "population": rule["population"], "predicate": rule["predicate"]}
            found.append(_resolved("membership_rule", auth, qobj))
    return _one(found)

def _temporal(text: str, query: str) -> Optional[dict]:
    facts = {"before": [], "after": []}
    entity = pop = window = boundary = None
    for s in _sentences(text):
        m = re.fullmatch(r"(?P<e>.+?) (?:is|was) (?:a |an |a member of (?:the )?)(?P<p>.+?) only (?P<side>before|after) (?P<b>.+)", s, re.I)
        if m:
            entity, pop, boundary = _clean(m["e"]), _clean(m["p"]), _cmp(m["b"])
            window = "before_only" if m["side"].lower() == "before" else "after_only"
            break
        m = re.fullmatch(r"(?P<e>.+?) (?:is|was) (?:a |an |a member of (?:the )?)(?P<p>.+?) (?:both )?before and after (?P<b>.+)", s, re.I)
        if m:
            entity, pop, boundary, window = _clean(m["e"]), _clean(m["p"]), _cmp(m["b"]), "always"
            break
        m = re.fullmatch(r"(?P<e>.+?) (?:is|was) never (?:a |an |a member of (?:the )?)(?P<p>.+?) (?:before or after|either before or after) (?P<b>.+)", s, re.I)
        if m:
            entity, pop, boundary, window = _clean(m["e"]), _clean(m["p"]), _cmp(m["b"]), "never"
            break
        m = re.fullmatch(r"(?P<side>before|after) (?P<b>.+?),? (?P<e>[A-Z][A-Za-z' -]*?) (?:is|was) (?P<n>not )?(?:a |an |a member of (?:the )?)(?P<p>.+)", s, re.I)
        if m:
            facts[m["side"].lower()].append((_clean(m["e"]), _clean(m["p"]), bool(m["n"]), _cmp(m["b"])))
            continue
        m = re.fullmatch(r"(?P<e>[A-Z][A-Za-z' -]*?) (?:is|was) (?P<n>not )?(?:a |an |a member of (?:the )?)(?P<p>.+?) (?P<side>before|after) (?P<b>.+)", s, re.I)
        if m:
            facts[m["side"].lower()].append((_clean(m["e"]), _clean(m["p"]), bool(m["n"]), _cmp(m["b"])))
    if not window and len(facts["before"]) == len(facts["after"]) == 1:
        b, a = facts["before"][0], facts["after"][0]
        if _cmp(b[0]) == _cmp(a[0]) and _same_class(b[1], a[1]) and b[3] == a[3]:
            entity, pop, boundary = b[0], b[1], b[3]
            window = "before_only" if not b[2] and a[2] else "after_only" if b[2] and not a[2] else "always" if not b[2] and not a[2] else "never"
    if not all([entity, pop, window, boundary]):
        return None
    rule = _rule(text, pop)
    if not rule:
        return None
    q = _clean(query)
    tm = re.search(r"\b(before|after)\b", q, re.I)
    if not tm:
        return None
    side = tm.group(1).lower()
    q0 = re.sub(r"^(?:before|after)\b[^,]*,\s*", "", q, flags=re.I)
    q0 = _space(re.sub(r"\b(?:before|after)\b\s+.+$", "", q0, flags=re.I))
    qm = _q_membership(q0)
    if qm and _cmp(qm[0]) == _cmp(entity) and _same_class(qm[1], rule["population"]):
        kind = "membership"
    elif _q_rule(q0, entity):
        kind = "rule_applies"
    else:
        kind = _q_behavior(q0, entity, rule["predicate"])
    if not kind:
        return None
    auth = {"entity": entity, "population": rule["population"], "membership_window": window, "boundary": "cutoff", "rule": rule}
    qobj = {"kind": kind, "entity": entity, "population": rule["population"], "predicate": rule["predicate"], "time": side}
    return _resolved("temporal_membership", auth, qobj)

def _only_clause(text: str) -> Optional[tuple[str, str]]:
    for s in _sentences(text):
        m = re.fullmatch(r"only (?:(?:members?|people) (?:of|in) (?:the )?|the )?(?P<p>.+?) (?:may|can|are permitted to|are allowed to|are authorized to) (?P<v>.+)", s, re.I)
        if m:
            return _clean(m["p"]), _predicate(m["v"])
    return None

def _q_permission(query: str, pred: str) -> Optional[str]:
    for p in [
        r"(?:may|can) (?P<e>.+?) (?P<v>.+)",
        r"(?:is|was) (?P<e>.+?) (?:permitted|allowed|authorized) to (?P<v>.+)",
        r"(?P<e>.+?) (?:may|can) (?P<v>.+)",
    ]:
        m = re.fullmatch(p, _clean(query), re.I)
        if m and _cmp(_predicate(m["v"])) == _cmp(pred):
            return _clean(m["e"])
    return None

def _explicit_permission(text: str, entity: str, pred: str) -> str:
    vals = set()
    for s in _sentences(text):
        if not re.match(rf"^{re.escape(entity)}\b", s, re.I):
            continue
        tail = re.sub(rf"^{re.escape(entity)}\s+", "", s, flags=re.I)
        for status, p in [
            ("not_permitted", r"(?:may|can) not (?P<v>.+)"),
            ("not_permitted", r"(?:is|was) not (?:permitted|allowed|authorized) to (?P<v>.+)"),
            ("permitted", r"(?:may|can) (?P<v>.+)"),
            ("permitted", r"(?:is|was) (?:permitted|allowed|authorized) to (?P<v>.+)"),
        ]:
            m = re.fullmatch(p, tail, re.I)
            if m and _cmp(_predicate(m["v"])) == _cmp(pred):
                vals.add(status)
    return next(iter(vals)) if len(vals) == 1 else "unknown"

def _only_permission(text: str, query: str) -> Optional[dict]:
    clause = _only_clause(text)
    if not clause:
        return None
    pop, pred = clause
    qm, qp = _q_membership(query), _q_permission(query, pred)
    if qm and _same_class(qm[1], pop):
        entity, kind = qm[0], "membership"
    elif qp:
        entity, kind = qp, "permission"
    else:
        return None
    matches = [m for m in _memberships(text) if _cmp(m[0]) == _cmp(entity) and _same_class(m[1], pop)]
    if len({m[2] for m in matches}) > 1:
        return None
    membership = matches[0][2] if matches else "unknown"
    auth = {"entity": entity, "population": pop, "membership": membership, "predicate": pred,
            "only_population_may": True, "explicit_permission": _explicit_permission(text, entity, pred)}
    qobj = {"kind": kind, "entity": entity, "population": pop, "predicate": pred}
    return _resolved("only_permission", auth, qobj)

def _quant(sentence: str) -> Optional[tuple[str, str, str]]:
    s = _clean(sentence)
    for q, p in [
        ("not_every", r"it is false that (?:every|all) (?P<x>.+)"),
        ("not_every", r"(?:not every|not all) (?P<x>.+)"),
        ("every", r"(?:every|all) (?P<x>.+)"),
        ("none", r"(?:no|none of the) (?P<x>.+)"),
        ("some", r"(?:some|at least one) (?P<x>.+)"),
    ]:
        m = re.fullmatch(p, s, re.I)
        if not m:
            continue
        words = _clean(m["x"]).split()
        if len(words) < 2:
            return None
        vi = None
        verbish = {"is", "are", "was", "were", "record", "records", "review", "reviews", "approve", "approves",
                   "enter", "enters", "file", "files", "carry", "carries", "wear", "wears", "submit", "submits",
                   "report", "reports", "inspect", "inspects", "sign", "signs", "attend", "attends", "vote", "votes",
                   "serve", "serves", "work", "works", "teach", "teaches", "write", "writes", "read", "reads"}
        for i in range(1, len(words)):
            w = re.sub(r"[^A-Za-z']", "", words[i]).lower()
            if w in verbish or w in _IRREG or w.endswith(("ed", "ing")):
                vi = i; break
        vi = 1 if vi is None else vi
        return _clean(" ".join(words[:vi])), _predicate(" ".join(words[vi:])), q
    return None

def _quantifier(text: str, query: str) -> Optional[dict]:
    auths = [x for s in _sentences(text) if (x := _quant(s))]
    qq = _quant(query)
    if len(auths) != 1 or not qq:
        return None
    ap, av, aq = auths[0]
    qp, qv, qquant = qq
    if not _same_class(ap, qp) or _cmp(av) != _cmp(qv):
        return None
    auth = {"population": ap, "predicate": av, "quantifier": aq, "polarity": "positive"}
    qobj = {"kind": "quantified", "population": ap, "predicate": av, "quantifier": qquant, "polarity": "positive"}
    return _resolved("quantifier", auth, qobj)

def _sub_clause(s: str) -> Optional[tuple[str, str, str]]:
    s = _clean(s)
    m = re.fullmatch(r"(?:there is no subclass (?:edge|relation) between|no subclass (?:edge|relation) exists between) (?P<a>.+?) and (?P<b>.+)", s, re.I)
    if m:
        return _clean(m["a"]), _clean(m["b"]), "none"
    for p in [
        r"(?:every|all) (?P<a>.+?) (?:is|are) (?:a |an )?(?P<b>.+)",
        r"(?P<a>.+?) (?:is|are) (?:a )?(?:subclass of|kind of|type of) (?P<b>.+)",
    ]:
        m = re.fullmatch(p, s, re.I)
        if m:
            return _clean(m["a"]), _clean(m["b"]), "edge"
    return None

def _subclass(text: str, query: str) -> Optional[dict]:
    edges = [x for s in _sentences(text) if (x := _sub_clause(s))]
    qm = _q_membership(query)
    if len(edges) != 1 or not qm:
        return None
    c1, c2, mode = edges[0]
    k1, k2 = _singular(c1), _singular(c2)
    if not k1 or not k2 or k1 == k2:
        return None
    order = sorted([k1, k2])
    lab = {order[0]: "A", order[1]: "B"}
    qk = _singular(qm[1])
    if qk not in lab:
        return None
    mems = [m for m in _memberships(text) if _cmp(m[0]) == _cmp(qm[0]) and _singular(m[1]) in lab]
    if len(mems) != 1:
        return None
    mem = mems[0]
    edge = "none" if mode == "none" else f"{lab[k1]}_sub_{lab[k2]}"
    auth = {"entity": qm[0], "membership_population": lab[_singular(mem[1])], "membership": mem[2], "subclass_edge": edge}
    qobj = {"kind": "membership", "entity": qm[0], "population": lab[qk]}
    return _resolved("subclass", auth, qobj)

def _unary(s: str) -> Optional[tuple[str, str, str]]:
    s = _clean(s)
    m = re.fullmatch(r"(?:did|does|do) (?P<s>.+?) (?P<n>not )?(?P<v>.+)", s, re.I)
    if m:
        return _clean(m["s"]), _predicate(m["v"]), "negative" if m["n"] else "positive"
    m = re.fullmatch(r"(?i:the) (?P<h>[A-Za-z]+) (?P<n>(?i:did not|does not) )?(?P<v>.+)", s)
    if m and m["h"].lower() in _COLLECTIVES:
        return f"The {m['h']}", _predicate(m["v"]), "negative" if m["n"] else "positive"
    m = re.fullmatch(r"(?P<s>[A-Z][A-Za-z']*) (?P<n>did not |does not )?(?P<v>.+)", s)
    if m:
        return _clean(m["s"]), _predicate(m["v"]), "negative" if m["n"] else "positive"
    return None

def _scope(subject: str) -> Optional[str]:
    words = _cmp(subject).split()
    if words and words[-1] in _COLLECTIVES:
        return "group"
    if re.match(r"^[A-Z]", subject):
        return f"member:{_clean(subject)}"
    return None

def _group_scope(text: str, query: str) -> Optional[dict]:
    events = []
    for s in _sentences(text):
        if re.search(r"\b(?:member of|belongs? to|only .* may|every |all |some |no |subclass)\b", s, re.I):
            continue
        x = _unary(s)
        if x and _scope(x[0]):
            events.append(x)
    q = _unary(query)
    if len(events) != 1 or not q or _cmp(events[0][1]) != _cmp(q[1]):
        return None
    a, b = _scope(events[0][0]), _scope(q[0])
    if not a or not b or (a.startswith("member:") and b.startswith("member:")):
        return None
    return _resolved("group_scope",
                     {"event_scope": a, "predicate": events[0][1], "polarity": events[0][2]},
                     {"kind": "event", "event_scope": b, "predicate": events[0][1], "polarity": q[2]})

def _binary(s: str) -> Optional[tuple[str, str, str, str]]:
    s = _clean(s)
    m = re.fullmatch(r"(?i:was|is|were|are) (?P<o>[A-Z][A-Za-z']*) (?P<n>(?i:not) )?(?P<v>[A-Za-z]+(?:ed|en)) (?i:by) (?P<s>[A-Z][A-Za-z']*)", s)
    if not m:
        m = re.fullmatch(r"(?P<o>[A-Z][A-Za-z']*) (?i:was|is|were|are) (?P<n>(?i:not) )?(?P<v>[A-Za-z]+(?:ed|en)) (?i:by) (?P<s>[A-Z][A-Za-z']*)", s)
    if m:
        return _clean(m["s"]), _predicate(m["v"]), _clean(m["o"]), "negative" if m["n"] else "positive"
    m = re.fullmatch(r"(?i:did|does|do) (?P<s>[A-Z][A-Za-z' -]*?) (?P<n>(?i:not) )?(?P<v>[A-Za-z]+) (?P<o>[A-Z][A-Za-z']*)", s)
    if m:
        return _clean(m["s"]), _predicate(m["v"]), _clean(m["o"]), "negative" if m["n"] else "positive"
    m = re.fullmatch(r"(?P<s>[A-Z][A-Za-z' -]*?) (?P<n>did not |does not )?(?P<v>[A-Za-z]+) (?P<o>[A-Z][A-Za-z']*)", s)
    if m:
        return _clean(m["s"]), _predicate(m["v"]), _clean(m["o"]), "negative" if m["n"] else "positive"
    return None

def _role_binding(text: str, query: str) -> Optional[dict]:
    events = [x for s in _sentences(text) if (x := _binary(s))]
    q = _binary(query)
    if len(events) != 1 or not q or _cmp(events[0][1]) != _cmp(q[1]):
        return None
    a = events[0]
    return _resolved("role_binding",
        {"event": {"predicate": a[1], "roles": {"subject": a[0], "object": a[2]}, "polarity": a[3]}},
        {"kind": "event", "predicate": a[1], "roles": {"subject": q[0], "object": q[2]}, "polarity": q[3]})

def _one(xs: list[dict]) -> Optional[dict]:
    uniq = []
    for x in xs:
        if x not in uniq:
            uniq.append(x)
    return uniq[0] if len(uniq) == 1 else None

def _domain_relevant(text: str, query: str) -> bool:
    joined = f" {text} {query} ".lower()
    markers = [" member", " belong", " every ", " all ", " some ", " no ", " none ", " only ", " may ",
               " permitted", " allowed", " subclass", " kind of ", " type of ", " before ", " after ",
               " must ", " shall ", " required ", " trained ", " works with ", " work with ", " employed ",
               " associated ", " applied ", " intends ", " capable ", " nearby ", " near "]
    return any(x in joined for x in markers)

def extract(text: str, query_text: str) -> dict:
    """Return one resolved typed object, otherwise a contract unknown state."""
    if not isinstance(text, str) or not isinstance(query_text, str):
        return _unknown("unparsed")
    text, query_text = _space(text), _space(query_text)
    if not text or not query_text:
        return _unknown("insufficient_authority")
    if _escape(text, query_text):
        return _unknown("ontology_escape")
    if _ambiguous(text, query_text):
        return _unknown("ambiguous_reference")

    candidates = []
    for parser in (_temporal, _only_permission, _subclass, _quantifier, _membership_rule, _role_binding, _group_scope):
        x = parser(text, query_text)
        if x:
            candidates.append(x)
    chosen = _one(candidates)
    if chosen:
        return chosen
    if len(candidates) > 1:
        return _unknown("ambiguous_reference")
    return _unknown("insufficient_authority" if _domain_relevant(text, query_text) else "unparsed")
