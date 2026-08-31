"""RC7D deterministic semantic-operator bank candidate.

Research-only apparatus. No production authorization.
All operators receive and preserve the exact raw source.
"""
from __future__ import annotations

import hashlib
import itertools
import re
from typing import Callable

VERSION = "rc7d-candidate-v1"

DIMENSIONS = (
    "permission",
    "role_binding",
    "quantifier",
    "exception",
    "temporal",
    "subclass",
    "probability",
    "quantitative",
)

BANK_ORDER = DIMENSIONS


def source_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _span(text: str, start: int, end: int) -> dict:
    return {"start": start, "end": end, "text": text[start:end]}


def _base(text: str, operator_id: str, dimension: str, status: str) -> dict:
    return {
        "operator_id": operator_id,
        "version": VERSION,
        "dimension": dimension,
        "status": status,
        "raw_source": text,
        "raw_source_sha256": source_sha(text),
        "spans": [],
        "atoms": [],
        "warrants": [],
        "composition_requirements": [],
    }


def _na(text: str, operator_id: str, dimension: str) -> dict:
    return _base(text, operator_id, dimension, "NOT_APPLICABLE")


def _unresolved(text: str, operator_id: str, dimension: str, span: tuple[int, int] | None = None) -> dict:
    out = _base(text, operator_id, dimension, "UNRESOLVED")
    if span:
        out["spans"].append(_span(text, *span))
    return out


def _claim(
    text: str,
    operator_id: str,
    dimension: str,
    matches: list[tuple[int, int]],
    atoms: list[dict],
    warrants: list[str],
    composition_requirements: list[str] | None = None,
) -> dict:
    out = _base(text, operator_id, dimension, "CLAIMED")
    out["spans"] = [_span(text, a, b) for a, b in matches]
    out["atoms"] = atoms
    out["warrants"] = warrants
    out["composition_requirements"] = composition_requirements or []
    return out


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip(" .,:;\t\n").lower())


# ---------------------------------------------------------------------------
# Permission specialist
# ---------------------------------------------------------------------------

_PERMISSION_PATTERNS = [
    (re.compile(r"\bonly\s+(?P<population>[a-z][a-z -]{1,40}?)\s+may\s+(?P<predicate>[a-z][a-z0-9 -]{1,60}?)(?:[.;]|$)", re.I), "necessary_permission_condition"),
    (re.compile(r"\bpermission\s+to\s+(?P<predicate>[a-z][a-z0-9 -]{1,60}?)\s+(?:is\s+)?(?:restricted|limited)\s+to\s+(?P<population>[a-z][a-z -]{1,40}?)(?:[.;]|$)", re.I), "necessary_permission_condition"),
]
_PERMISSION_GRANT = re.compile(r"\b(?P<entity>[A-Z][a-z]+)\s+(?:is|was)\s+(?P<neg>not\s+)?(?:authorized|permitted|allowed)\s+to\s+(?P<predicate>[a-z][a-z0-9 -]{1,60}?)(?:[.;]|$)")
_PERMISSION_UNKNOWN = re.compile(r"\b(?:whether\s+)?(?P<entity>[A-Z][a-z]+)\s+(?:is\s+)?(?:permitted|authorized|allowed)\s+to\s+(?P<predicate>[a-z][a-z0-9 -]{1,60}?)\s+is\s+unknown\b", re.I)
_MEMBER = re.compile(r"\b(?P<entity>[A-Z][a-z]+)\s+(?:is\s+)?(?P<neg>not\s+)?(?:a\s+)?(?:member\s+of|belongs\s+to)\s+(?P<population>[a-z][a-z -]{1,45}?)(?:[.;]|$)")
_MEMBER_UNKNOWN = re.compile(r"\b(?:it\s+is\s+unknown\s+whether|whether)\s+(?P<entity>[A-Z][a-z]+)\s+(?:is\s+)?(?:a\s+)?(?:member\s+of|belongs\s+to)\s+(?P<population>[a-z][a-z -]{1,45}?)(?:\s+is\s+unknown)?(?:[.;]|$)", re.I)


def permission_operator(text: str) -> dict:
    spans: list[tuple[int, int]] = []
    atoms: list[dict] = []
    warrants: list[str] = []

    for pat, warrant in _PERMISSION_PATTERNS:
        for m in pat.finditer(text):
            spans.append(m.span())
            atoms.append({"kind": "necessary_permission_condition", "population": _norm(m.group("population")), "predicate": _norm(m.group("predicate"))})
            warrants.append(warrant)

    for m in _PERMISSION_UNKNOWN.finditer(text):
        spans.append(m.span())
        atoms.append({"kind": "explicit_permission", "entity": _norm(m.group("entity")), "predicate": _norm(m.group("predicate")), "value": "unknown"})
        warrants.append("explicit_unknown_assertion")

    for m in _PERMISSION_GRANT.finditer(text):
        spans.append(m.span())
        atoms.append({"kind": "explicit_permission", "entity": _norm(m.group("entity")), "predicate": _norm(m.group("predicate")), "value": "not_permitted" if m.group("neg") else "permitted"})
        warrants.append("explicit_permission_denial" if m.group("neg") else "explicit_permission_grant")

    for m in _MEMBER_UNKNOWN.finditer(text):
        spans.append(m.span())
        atoms.append({"kind": "membership", "entity": _norm(m.group("entity")), "population": _norm(m.group("population")), "value": "unknown"})
        warrants.append("explicit_unknown_assertion")

    for m in _MEMBER.finditer(text):
        # Explicit unknown constructions are handled above and must not be double-read.
        if "unknown" in m.group(0).lower():
            continue
        spans.append(m.span())
        atoms.append({"kind": "membership", "entity": _norm(m.group("entity")), "population": _norm(m.group("population")), "value": "non_member" if m.group("neg") else "member"})
        warrants.append("explicit_nonmembership_assertion" if m.group("neg") else "explicit_membership_assertion")

    if not atoms:
        return _na(text, "permission-v1", "permission")
    return _claim(text, "permission-v1", "permission", spans, atoms, warrants)


# ---------------------------------------------------------------------------
# Role-binding specialist
# ---------------------------------------------------------------------------

_VERB_LEMMA = {
    "reviewed": "review",
    "inspected": "inspect",
    "approved": "approve",
    "signed": "sign",
    "released": "release",
}
_ROLE_ACTIVE = re.compile(r"\b(?P<subject>[A-Z][a-z]+|[Tt]he\s+[a-z][a-z -]{1,35}|[A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?P<neg>did\s+not\s+)?(?P<verb>reviewed|inspected|approved|signed|released)\s+(?P<object>[a-z][a-z0-9 -]{1,60}?)(?:[.;]|$)")
_ROLE_PASSIVE = re.compile(r"\b(?P<object>[A-Z]?[a-z][a-z0-9 -]{1,60}?)\s+(?:was|were)\s+(?P<neg>not\s+)?(?P<verb>reviewed|inspected|approved|signed|released)\s+by\s+(?P<subject>[A-Z][a-z]+)(?:[.;]|$)", re.I)


def role_binding_operator(text: str) -> dict:
    # Quantified class-event statements belong to quantifier semantics in this apparatus;
    # do not manufacture an individual semantic subject from the quantified population.
    if re.search(r"\b(?:every|all|each|no|none|some|not every|not all|most|majority|percent|%)\b", text, re.I):
        return _na(text, "role-binding-v1", "role_binding")

    ms = list(_ROLE_PASSIVE.finditer(text)) + list(_ROLE_ACTIVE.finditer(text))
    if not ms:
        return _na(text, "role-binding-v1", "role_binding")
    if len(ms) > 1:
        # Multiple independent events are beyond this bounded single-event receipt.
        return _unresolved(text, "role-binding-v1", "role_binding", ms[0].span())
    m = ms[0]
    atoms = [{
        "kind": "event",
        "predicate": _VERB_LEMMA[m.group("verb").lower()],
        "subject": _norm(m.group("subject")),
        "object": _norm(m.group("object")),
        "polarity": "negative" if m.group("neg") else "positive",
    }]
    warrant = "passive_role_binding" if " by " in m.group(0).lower() else "active_role_binding"
    return _claim(text, "role-binding-v1", "role_binding", [m.span()], atoms, [warrant])


# ---------------------------------------------------------------------------
# Quantifier specialists: two independent deterministic implementations.
# v1 is the bank authority candidate; v2 is an audit duplicate only.
# ---------------------------------------------------------------------------

_QUANT_MAP = {
    "every": "every", "all": "every", "each": "every",
    "no": "none", "none": "none", "not one": "none",
    "some": "some", "at least one": "some",
    "not every": "not_every", "not all": "not_every",
}
_QUANT_RE = re.compile(
    r"\b(?P<q>not\s+every|not\s+all|at\s+least\s+one|not\s+one|every|all|each|some|none|no)\s+"
    r"(?P<population>[a-z][a-z -]{1,35}?)\s+"
    r"(?P<verb>reviewed|inspected|approved|signed|released)\s+"
    r"(?P<object>[a-z][a-z0-9 -]{1,55}?)(?=\s+(?:except|save for|excluding|other than|before|after|prior to|following|probably|likely|unlikely)|[.;]|$)",
    re.I,
)


def quantifier_operator_v1(text: str) -> dict:
    ms = list(_QUANT_RE.finditer(text))
    if not ms:
        return _na(text, "quantifier-v1-regex", "quantifier")
    if len(ms) != 1:
        return _unresolved(text, "quantifier-v1-regex", "quantifier", ms[0].span())
    m = ms[0]
    atom = {
        "kind": "quantifier",
        "quantifier": _QUANT_MAP[_norm(m.group("q"))],
        "population": _norm(m.group("population")),
        "predicate": f"{_VERB_LEMMA[m.group('verb').lower()]} {_norm(m.group('object'))}",
    }
    return _claim(text, "quantifier-v1-regex", "quantifier", [m.span()], [atom], ["explicit_quantifier"])


def quantifier_operator_v2(text: str) -> dict:
    # Independently coded token scanner: find a quantifier token sequence, then a known event verb.
    low = text.lower()
    candidates = sorted(_QUANT_MAP, key=len, reverse=True)
    found: list[tuple[int, str]] = []
    for q in candidates:
        for m in re.finditer(r"(?<![a-z])" + re.escape(q) + r"(?![a-z])", low):
            found.append((m.start(), q))
    if not found:
        return _na(text, "quantifier-v1-token", "quantifier")
    found.sort()
    start, q = found[0]
    after = text[start + len(q):]
    vm = re.search(r"\b(reviewed|inspected|approved|signed|released)\b", after, re.I)
    if not vm:
        return _unresolved(text, "quantifier-v1-token", "quantifier", (start, start + len(q)))
    pop_raw = after[:vm.start()].strip(" ,")
    if not pop_raw or len(pop_raw.split()) > 6:
        return _unresolved(text, "quantifier-v1-token", "quantifier", (start, start + len(q)))
    obj_start_local = vm.end()
    tail = after[obj_start_local:]
    stop = re.search(r"\s+(?:except|save for|excluding|other than|before|after|prior to|following|probably|likely|unlikely)\b|[.;]", tail, re.I)
    obj_raw = tail[:stop.start() if stop else len(tail)].strip(" ,")
    if not obj_raw:
        return _unresolved(text, "quantifier-v1-token", "quantifier", (start, start + len(q)))
    end = start + len(q) + obj_start_local + (stop.start() if stop else len(tail))
    atom = {
        "kind": "quantifier",
        "quantifier": _QUANT_MAP[q],
        "population": _norm(pop_raw),
        "predicate": f"{_VERB_LEMMA[vm.group(1).lower()]} {_norm(obj_raw)}",
    }
    return _claim(text, "quantifier-v1-token", "quantifier", [(start, end)], [atom], ["explicit_quantifier"])


# ---------------------------------------------------------------------------
# Other specialists
# ---------------------------------------------------------------------------

_EXCEPTION_PATTERNS = [
    re.compile(r"\bexcept\s+(?P<x>[A-Z][a-z]+)\b"),
    re.compile(r"\bsave\s+for\s+(?P<x>[A-Z][a-z]+)\b", re.I),
    re.compile(r"\bwith\s+the\s+exception\s+of\s+(?P<x>[A-Z][a-z]+)\b", re.I),
    re.compile(r"\bexcluding\s+(?P<x>[A-Z][a-z]+)\b", re.I),
    re.compile(r"\bother\s+than\s+(?P<x>[A-Z][a-z]+)\b", re.I),
    re.compile(r"\bapart\s+from\s+(?P<x>[A-Z][a-z]+)\b", re.I),
]


def exception_operator(text: str) -> dict:
    ms = [m for p in _EXCEPTION_PATTERNS for m in p.finditer(text)]
    if not ms:
        return _na(text, "exception-v1", "exception")
    atoms = [{"kind": "exception", "excluded": _norm(m.group("x"))} for m in ms]
    return _claim(text, "exception-v1", "exception", [m.span() for m in ms], atoms, ["explicit_exclusion_exception"] * len(ms), ["requires_base_proposition"])


_TEMP_PATTERNS = [
    (re.compile(r"\bbefore\s+(?P<t>the\s+cutoff|the\s+deadline|[0-9]{4}-[0-9]{2}-[0-9]{2})\b", re.I), "before"),
    (re.compile(r"\bafter\s+(?P<t>the\s+cutoff|the\s+deadline|[0-9]{4}-[0-9]{2}-[0-9]{2})\b", re.I), "after"),
    (re.compile(r"\bprior\s+to\s+(?P<t>the\s+cutoff|the\s+deadline)\b", re.I), "before"),
    (re.compile(r"\bfollowing\s+(?P<t>the\s+cutoff|the\s+deadline)\b", re.I), "after"),
    (re.compile(r"\buntil\s+(?P<t>the\s+cutoff|the\s+deadline)\b", re.I), "until"),
    (re.compile(r"\bas\s+of\s+(?P<t>[0-9]{4}-[0-9]{2}-[0-9]{2})\b", re.I), "as_of"),
    (re.compile(r"\bduring\s+(?P<t>the\s+[a-z][a-z -]{1,30})\b", re.I), "during"),
]


def temporal_operator(text: str) -> dict:
    hits = [(m, rel) for p, rel in _TEMP_PATTERNS for m in p.finditer(text)]
    if not hits:
        return _na(text, "temporal-v1", "temporal")
    atoms = [{"kind": "temporal_scope", "relation": rel, "reference": _norm(m.group("t"))} for m, rel in hits]
    return _claim(text, "temporal-v1", "temporal", [m.span() for m, _ in hits], atoms, ["explicit_temporal_scope"] * len(hits), ["requires_base_proposition"])


_SUBCLASS_PATTERNS = [
    re.compile(r"\b(?P<child>[A-Z]?[a-z][a-z -]{1,35}?)\s+(?:are|is)\s+(?:a\s+)?(?:subclass|subset|type|kind)\s+of\s+(?P<parent>[a-z][a-z -]{1,35}?)(?:[.;]|$)", re.I),
    re.compile(r"\b(?P<child>[A-Z]?[a-z][a-z -]{1,35}?)\s+(?:sits|sit|falls|fall)\s+(?:within|under)\s+(?P<parent>[a-z][a-z -]{1,35}?)(?:[.;]|$)", re.I),
]


def subclass_operator(text: str) -> dict:
    ms = [m for p in _SUBCLASS_PATTERNS for m in p.finditer(text)]
    if not ms:
        return _na(text, "subclass-v1", "subclass")
    atoms = [{"kind": "subclass", "child": _norm(m.group("child")), "parent": _norm(m.group("parent"))} for m in ms]
    return _claim(text, "subclass-v1", "subclass", [m.span() for m in ms], atoms, ["explicit_subclass_relation"] * len(ms))


_PROB_PATTERNS = [
    (re.compile(r"\bprobably\b", re.I), "probable"),
    (re.compile(r"\blikely\b", re.I), "likely"),
    (re.compile(r"\bunlikely\b", re.I), "unlikely"),
    (re.compile(r"\bthere\s+is\s+(?:a\s+)?chance\b", re.I), "possible"),
    (re.compile(r"\bprobability\b", re.I), "probabilistic"),
]


def probability_operator(text: str) -> dict:
    hits = [(m, val) for p, val in _PROB_PATTERNS for m in p.finditer(text)]
    if not hits:
        return _na(text, "probability-v1", "probability")
    atoms = [{"kind": "epistemic_probability", "value": val} for m, val in hits]
    return _claim(text, "probability-v1", "probability", [m.span() for m, _ in hits], atoms, ["explicit_probability_marker"] * len(hits), ["requires_base_proposition"])


_NUMBER_WORDS = "one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
_QUANTITATIVE_PATTERNS = [
    (re.compile(r"\b(?P<n>\d{1,3})\s*%\b"), "percentage"),
    (re.compile(rf"\b(?P<n>{_NUMBER_WORDS})\s+percent\b", re.I), "percentage"),
    (re.compile(rf"\bexactly\s+(?P<n>\d+|{_NUMBER_WORDS})\b", re.I), "exact_count"),
    (re.compile(rf"\bat\s+least\s+(?P<n>\d+|two|three|four|five|six|seven|eight|nine|ten)\b", re.I), "minimum_count"),
    (re.compile(r"\b(?:a\s+)?majority\s+of\b", re.I), "majority"),
    (re.compile(r"\bmost\s+[a-z]", re.I), "most"),
    (re.compile(r"\bmany\s+[a-z]", re.I), "many"),
    (re.compile(r"\bfew\s+[a-z]", re.I), "few"),
]


def quantitative_operator(text: str) -> dict:
    hits = [(m, kind) for p, kind in _QUANTITATIVE_PATTERNS for m in p.finditer(text)]
    if not hits:
        return _na(text, "quantitative-v1", "quantitative")
    atoms = [{"kind": "quantitative_scope", "quantitative_kind": kind, "surface": _norm(m.group(0))} for m, kind in hits]
    return _claim(text, "quantitative-v1", "quantitative", [m.span() for m, _ in hits], atoms, ["explicit_quantitative_marker"] * len(hits), ["requires_base_proposition"])


OPERATORS: dict[str, Callable[[str], dict]] = {
    "permission": permission_operator,
    "role_binding": role_binding_operator,
    "quantifier": quantifier_operator_v1,
    "exception": exception_operator,
    "temporal": temporal_operator,
    "subclass": subclass_operator,
    "probability": probability_operator,
    "quantitative": quantitative_operator,
}


# ---------------------------------------------------------------------------
# Routing and governance
# ---------------------------------------------------------------------------

_ROUTE_SIGNATURES = {
    "permission": re.compile(r"\b(?:only\b.*\bmay\b|authorized\s+to|permitted\s+to|allowed\s+to|member\s+of|belongs\s+to|permission\s+to)\b", re.I),
    "role_binding": re.compile(r"\b(?:reviewed|inspected|approved|signed|released)\b", re.I),
    "quantifier": re.compile(r"\b(?:every|all|each|none|no|some|not every|not all|at least one)\b", re.I),
    "exception": re.compile(r"\b(?:except|save for|with the exception of|excluding|other than|apart from)\b", re.I),
    "temporal": re.compile(r"\b(?:before|after|prior to|following|until|as of|during)\b", re.I),
    "subclass": re.compile(r"\b(?:subclass|subset|type of|kind of|sits within|falls under)\b", re.I),
    "probability": re.compile(r"\b(?:probably|likely|unlikely|chance|probability)\b", re.I),
    "quantitative": re.compile(r"(?:\b\d{1,3}\s*%\b|\bpercent\b|\bexactly\s+\w+|\bat least\s+\d+|\bmajority\b|\bmost\b|\bmany\b|\bfew\b)", re.I),
}


def route_candidates(text: str) -> list[str]:
    return [d for d in BANK_ORDER if _ROUTE_SIGNATURES[d].search(text)]


def single_router(text: str) -> dict:
    candidates = route_candidates(text)
    chosen = candidates[0] if candidates else None
    receipts = [OPERATORS[chosen](text)] if chosen else []
    return govern(text, "single_router", receipts, invoked=1 if chosen else 0, fallback=False)


def broadcast_all(text: str, bank_size: int = 8) -> dict:
    dims = list(BANK_ORDER[:bank_size])
    receipts = [OPERATORS[d](text) for d in dims]
    return govern(text, "broadcast_all", receipts, invoked=len(dims), fallback=False)


def conservative_router_fallback(text: str) -> dict:
    candidates = route_candidates(text)
    # Multiple visible semantic signatures are itself evidence that single routing can
    # discard information. Zero candidates is also unsafe for a router-only path.
    fallback = len(candidates) != 1
    if fallback:
        receipts = [OPERATORS[d](text) for d in BANK_ORDER]
        invoked = len(BANK_ORDER)
    else:
        chosen = candidates[0]
        receipts = [OPERATORS[chosen](text)]
        invoked = 1
        # A claimed operator may still leave explicit high-risk residual markers.
        other_markers = [d for d in BANK_ORDER if d != chosen and _ROUTE_SIGNATURES[d].search(text)]
        if other_markers:
            fallback = True
            receipts = [OPERATORS[d](text) for d in BANK_ORDER]
            invoked = len(BANK_ORDER)
    return govern(text, "conservative_router_fallback", receipts, invoked=invoked, fallback=fallback)


# Pair governance. `compose` means an explicit bounded composition is authorized.
# `coexist` means preserve both semantic layers but do not derive a new combined atom.
# Anything absent is retained as unresolved composition, never silently combined.
_PAIR_RULES = {
    frozenset(("quantifier", "exception")): "compose",
    frozenset(("permission", "temporal")): "compose",
    frozenset(("permission", "exception")): "compose",
    frozenset(("role_binding", "temporal")): "compose",
    frozenset(("role_binding", "probability")): "coexist",
    frozenset(("quantifier", "probability")): "coexist",
    frozenset(("subclass", "permission")): "coexist",
    frozenset(("role_binding", "quantitative")): "coexist",
}


def _covered_intervals(receipts: list[dict]) -> list[tuple[int, int]]:
    spans = sorted((s["start"], s["end"]) for r in receipts if r["status"] == "CLAIMED" for s in r["spans"])
    merged: list[list[int]] = []
    for a, b in spans:
        if not merged or a > merged[-1][1]:
            merged.append([a, b])
        else:
            merged[-1][1] = max(merged[-1][1], b)
    return [(a, b) for a, b in merged]


def _surface_residue(text: str, receipts: list[dict]) -> list[dict]:
    covered = _covered_intervals(receipts)
    residues: list[dict] = []
    cursor = 0
    for a, b in covered:
        if a > cursor and text[cursor:a].strip(" .,:;\n\t"):
            residues.append(_span(text, cursor, a))
        cursor = max(cursor, b)
    if cursor < len(text) and text[cursor:].strip(" .,:;\n\t"):
        residues.append(_span(text, cursor, len(text)))
    return residues


def govern(text: str, architecture: str, receipts: list[dict], invoked: int, fallback: bool) -> dict:
    assert all(r["raw_source"] == text and r["raw_source_sha256"] == source_sha(text) for r in receipts)
    claimed = [r for r in receipts if r["status"] == "CLAIMED"]
    dimensions = sorted({r["dimension"] for r in claimed})
    pair_decisions = []
    for a, b in itertools.combinations(dimensions, 2):
        rule = _PAIR_RULES.get(frozenset((a, b)), "unresolved")
        pair_decisions.append({"dimensions": [a, b], "decision": rule})

    # Audit duplicate for quantifier. It never silently overrides v1.
    q_audit = quantifier_operator_v2(text)
    q_primary = next((r for r in receipts if r["dimension"] == "quantifier"), None)
    if q_primary is None:
        q_primary = quantifier_operator_v1(text)
    q_agree = None
    if q_primary["status"] == "CLAIMED" and q_audit["status"] == "CLAIMED":
        q_agree = q_primary["atoms"] == q_audit["atoms"]
    elif q_primary["status"] != q_audit["status"]:
        q_agree = False

    return {
        "architecture": architecture,
        "raw_source": text,
        "raw_source_sha256": source_sha(text),
        "receipts": receipts,
        "claimed_dimensions": dimensions,
        "pair_decisions": pair_decisions,
        "surface_residue": _surface_residue(text, receipts),
        "specialists_invoked": invoked,
        "fallback": fallback,
        "quantifier_audit": {
            "primary": q_primary,
            "audit": q_audit,
            "agreement": q_agree,
        },
    }


# ---------------------------------------------------------------------------
# Deliberately weak negative controls
# ---------------------------------------------------------------------------


def greedy_claim(text: str) -> dict:
    receipts = []
    low = text.lower()
    for dim in BANK_ORDER:
        out = OPERATORS[dim](text)
        if out["status"] == "NOT_APPLICABLE" and any(tok in low for tok in dim.replace("_", " ").split()):
            out = _claim(text, f"greedy-{dim}", dim, [(0, len(text))], [{"kind": "greedy_keyword_claim", "surface": dim}], ["weak_keyword_match"])
        receipts.append(out)
    return govern(text, "greedy_claim", receipts, invoked=8, fallback=False)


def union_without_composition_governor(text: str) -> dict:
    receipts = [OPERATORS[d](text) for d in BANK_ORDER]
    claimed = [r for r in receipts if r["status"] == "CLAIMED"]
    return {
        "architecture": "union_without_composition_governor",
        "raw_source": text,
        "raw_source_sha256": source_sha(text),
        "receipts": receipts,
        "claimed_dimensions": sorted({r["dimension"] for r in claimed}),
        "blind_union_atoms": [a for r in claimed for a in r["atoms"]],
        "specialists_invoked": 8,
    }
