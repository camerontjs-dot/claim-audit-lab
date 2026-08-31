"""RC7D-D alternate deterministic semantic readers.

Frozen before the held-out RC7D-D cohort. All readers receive and preserve the
exact source text. Alternate readers are discovery instruments only; their
outputs require separate authority validation.
"""
from __future__ import annotations

import re
from research.semantic_operator_jurisdiction_rc7d import candidate as base

VERSION = "rc7d-d-multi-reader-v1"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip(" .,:;\t\n").lower())


def _na(text: str, reader: str, dim: str) -> dict:
    out = base._base(text, reader, dim, "NOT_APPLICABLE")
    out["reader_version"] = VERSION
    return out


def _claim(text: str, reader: str, dim: str, spans, atoms, warrants, requirements=None) -> dict:
    out = base._claim(text, reader, dim, spans, atoms, warrants, requirements or [])
    out["reader_version"] = VERSION
    return out

_VERBS = {"reviewed":"review", "inspected":"inspect", "approved":"approve", "signed":"sign", "released":"release"}

# Quantifier alternate: scanner/grammar emphasizing determiner phrases and
# punctuation rather than the original single regex.
_QFORMS = [
    (r"not\s+(?:every|all)(?:\s+one\s+of\s+the|\s+of\s+the)?", "not_every"),
    (r"(?:every\s+one|each\s+one)\s+of\s+the", "every"),
    (r"(?:all|every|each)(?:\s+of\s+the)?", "every"),
    (r"(?:none|no)(?:\s+of\s+the)?", "none"),
    (r"at\s+least\s+one(?:\s+of\s+the)?", "some"),
    (r"some(?:\s+of\s+the)?", "some"),
]

def quantifier_reader_alt(text: str) -> dict:
    for qpat, qval in _QFORMS:
        m = re.search(rf"\b(?P<q>{qpat})\s+(?P<pop>[a-z][a-z -]{{1,42}}?)\s+(?P<verb>reviewed|inspected|approved|signed|released)\s+(?P<obj>[a-z][a-z0-9 -]{{1,58}}?)(?=\s*(?:[,.;]|except\b|excluding\b|other than\b|save for\b|apart from\b|aside from\b|bar\b|probably\b|likely\b|unlikely\b|perhaps\b|possibly\b|conceivably\b|$))", text, re.I)
        if m:
            atom = {"kind":"quantifier", "quantifier":qval, "population":_norm(m.group("pop")), "predicate":f"{_VERBS[m.group('verb').lower()]} {_norm(m.group('obj'))}"}
            return _claim(text, "quantifier-alt-grammar", "quantifier", [m.span()], [atom], ["explicit_quantifier_alt"])
    return _na(text, "quantifier-alt-grammar", "quantifier")

# Exception alternate: entity-first and punctuation variants.
_EXCEPTION = [
    re.compile(r"\b(?:aside\s+from|bar|apart\s+from|but\s+not)\s+(?P<x>[A-Z][a-z]+)\b", re.I),
    re.compile(r"\b(?P<x>[A-Z][a-z]+)\s+(?:excepted|excluded)\b", re.I),
    re.compile(r"\b(?P<x>[A-Z][a-z]+)\s+being\s+the\s+exception\b", re.I),
    re.compile(r"\bwith\s+(?P<x>[A-Z][a-z]+)\s+(?:left|kept)\s+out\b", re.I),
]

def exception_reader_alt(text: str) -> dict:
    ms = [m for p in _EXCEPTION for m in p.finditer(text)]
    if not ms:
        return _na(text, "exception-alt-entity", "exception")
    return _claim(text, "exception-alt-entity", "exception", [m.span() for m in ms], [{"kind":"exception", "excluded":_norm(m.group("x"))} for m in ms], ["explicit_exception_alt"]*len(ms), ["requires_base_proposition"])

# Probability alternate: modality lexicon plus clause-shaped chance forms.
_PROB = [
    (re.compile(r"\b(?:perhaps|possibly|conceivably)\b", re.I), "possible"),
    (re.compile(r"\b(?:in\s+all\s+likelihood|quite\s+likely|likely)\b", re.I), "likely"),
    (re.compile(r"\b(?:probably|in\s+all\s+probability)\b", re.I), "probable"),
    (re.compile(r"\b(?:unlikely|improbably)\b", re.I), "unlikely"),
    (re.compile(r"\b(?:there\s+is|there's)\s+(?:a\s+)?(?:reasonable\s+|real\s+)?chance\s+(?:that|of)\b", re.I), "possible"),
]

def probability_reader_alt(text: str) -> dict:
    for p, val in _PROB:
        m = p.search(text)
        if m:
            return _claim(text, "probability-alt-lexicon", "probability", [m.span()], [{"kind":"epistemic_probability", "value":val}], ["epistemic_modality_alt"])
    return _na(text, "probability-alt-lexicon", "probability")

# Permission alternate: different surface grammar from original reader.
_PERMISSION = [
    (re.compile(r"\b(?P<pop>[A-Z]?[a-z][a-z -]{1,42}?)\s+alone\s+may\s+(?P<pred>[a-z][a-z0-9 -]{1,60}?)(?=[.;,]|$)", re.I), "necessary"),
    (re.compile(r"\b(?P<pred>[A-Za-z][a-z0-9 -]{1,60}?)\s+is\s+reserved\s+for\s+(?P<pop>[a-z][a-z -]{1,42}?)(?=[.;,]|$)", re.I), "necessary"),
]
_GRANT = re.compile(r"\b(?P<ent>[A-Z][a-z]+)\s+(?P<neg>lacks\s+permission|has\s+permission)\s+to\s+(?P<pred>[a-z][a-z0-9 -]{1,60}?)(?=[.;,]|$)")
_MEMBER = re.compile(r"\b(?P<ent>[A-Z][a-z]+)\s+(?P<neg>does\s+not\s+fall|falls)\s+within\s+(?P<pop>[a-z][a-z -]{1,42}?)(?=[.;,]|$)")

def permission_reader_alt(text: str) -> dict:
    spans=[]; atoms=[]; warrants=[]
    for p, _ in _PERMISSION:
        for m in p.finditer(text):
            spans.append(m.span()); atoms.append({"kind":"necessary_permission_condition", "population":_norm(m.group("pop")), "predicate":_norm(m.group("pred"))}); warrants.append("necessary_permission_alt")
    for m in _GRANT.finditer(text):
        spans.append(m.span()); atoms.append({"kind":"explicit_permission", "entity":_norm(m.group("ent")), "predicate":_norm(m.group("pred")), "value":"not_permitted" if m.group("neg").lower().startswith("lacks") else "permitted"}); warrants.append("explicit_permission_alt")
    for m in _MEMBER.finditer(text):
        spans.append(m.span()); atoms.append({"kind":"membership", "entity":_norm(m.group("ent")), "population":_norm(m.group("pop")), "value":"non_member" if m.group("neg").lower().startswith("does") else "member"}); warrants.append("membership_alt")
    return _claim(text, "permission-alt-grammar", "permission", spans, atoms, warrants) if atoms else _na(text, "permission-alt-grammar", "permission")

# Role alternate: negation paraphrases and event extraction under quantitative
# subjects. The latter is a distinct proposal, not automatic authority.
def role_reader_alt(text: str) -> dict:
    patterns = [
        (re.compile(r"\b(?P<s>[A-Z][a-z]+)\s+never\s+(?P<v>reviewed|inspected|approved|signed|released)\s+(?P<o>[a-z][a-z0-9 -]{1,55}?)(?=[.;]|$)", re.I), "negative"),
        (re.compile(r"\bat\s+no\s+point\s+did\s+(?P<s>[A-Z][a-z]+)\s+(?P<v>review|inspect|approve|sign|release)\s+(?P<o>[a-z][a-z0-9 -]{1,55}?)(?=[.;]|$)", re.I), "negative"),
        (re.compile(r"\b(?P<s>(?:exactly|at\s+least|fewer\s+than)\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+[a-z][a-z -]{1,32}|(?:\d{1,3}\s*%|[a-z]+\s+percent|a\s+(?:small\s+)?minority\s+of|a\s+majority\s+of|roughly\s+(?:half|three\s+quarters)|two\s+thirds\s+of)\s+(?:the\s+)?[a-z][a-z -]{1,32})\s+(?P<v>reviewed|inspected|approved|signed|released)\s+(?P<o>[a-z][a-z0-9 -]{1,55}?)(?=[.;]|$)", re.I), "positive"),
    ]
    for p, pol in patterns:
        m=p.search(text)
        if m:
            verb=m.group("v").lower(); lemma={**_VERBS, "review":"review","inspect":"inspect","approve":"approve","sign":"sign","release":"release"}[verb]
            atom={"kind":"event","predicate":lemma,"subject":_norm(m.group("s")),"object":_norm(m.group("o")),"polarity":pol}
            return _claim(text,"role-binding-alt-structure","role_binding",[m.span()],[atom],["role_binding_alt"])
    return _na(text,"role-binding-alt-structure","role_binding")

_SUBCLASS = [
    re.compile(r"\b(?P<c>[A-Z]?[a-z][a-z -]{1,38}?)\s+(?:are|is)\s+(?:a\s+)?subtype\s+of\s+(?P<p>[a-z][a-z -]{1,38}?)(?=[.;]|$)", re.I),
    re.compile(r"\b(?P<c>[A-Z]?[a-z][a-z -]{1,38}?)\s+(?:are|is)\s+nested\s+beneath\s+(?P<p>[a-z][a-z -]{1,38}?)(?=[.;]|$)", re.I),
    re.compile(r"\b(?P<c>[A-Z]?[a-z][a-z -]{1,38}?)\s+belong\s+to\s+a\s+narrower\s+class\s+than\s+(?P<p>[a-z][a-z -]{1,38}?)(?=[.;]|$)", re.I),
    re.compile(r"\b(?P<c>[A-Z]?[a-z][a-z -]{1,38}?)\s+(?:are|is)\s+contained\s+within\s+(?P<p>[a-z][a-z -]{1,38}?)(?=[.;]|$)", re.I),
]

def subclass_reader_alt(text: str) -> dict:
    for p in _SUBCLASS:
        m=p.search(text)
        if m:
            return _claim(text,"subclass-alt-taxonomy","subclass",[m.span()],[{"kind":"subclass","child":_norm(m.group("c")),"parent":_norm(m.group("p"))}],["explicit_subclass_alt"])
    return _na(text,"subclass-alt-taxonomy","subclass")

_QUANTITATIVE = [
    (re.compile(r"\b(?P<s>roughly\s+three\s+quarters(?:\s+of)?)\b",re.I),"proportion"),
    (re.compile(r"\b(?P<s>two\s+thirds\s+of)\b",re.I),"proportion"),
    (re.compile(r"\b(?P<s>roughly\s+half(?:\s+of)?)\b",re.I),"proportion"),
    (re.compile(r"\b(?P<s>a\s+(?:small\s+)?minority\s+of)\b",re.I),"minority"),
    (re.compile(r"\b(?P<s>fewer\s+than\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten))\b",re.I),"maximum_count"),
]

def quantitative_reader_alt(text: str) -> dict:
    for p,k in _QUANTITATIVE:
        m=p.search(text)
        if m:
            return _claim(text,"quantitative-alt-forms","quantitative",[m.span()],[{"kind":"quantitative_scope","quantitative_kind":k,"surface":_norm(m.group("s"))}],["quantitative_alt"])
    return _na(text,"quantitative-alt-forms","quantitative")

ORIGINAL_READERS = {
    "permission": base.permission_operator,
    "role_binding": base.role_binding_operator,
    "quantifier": base.quantifier_operator_v1,
    "exception": base.exception_operator,
    "temporal": base.temporal_operator,
    "subclass": base.subclass_operator,
    "probability": base.probability_operator,
    "quantitative": base.quantitative_operator,
}
ALT_READERS = {
    "permission": permission_reader_alt,
    "role_binding": role_reader_alt,
    "quantifier": quantifier_reader_alt,
    "exception": exception_reader_alt,
    "subclass": subclass_reader_alt,
    "probability": probability_reader_alt,
    "quantitative": quantitative_reader_alt,
}

def run_single(text: str) -> dict:
    receipts=[fn(text) for fn in ORIGINAL_READERS.values()]
    return {"raw_source":text,"raw_source_sha256":base.source_sha(text),"receipts":receipts}

def run_multi(text: str) -> dict:
    receipts=[fn(text) for fn in ORIGINAL_READERS.values()]
    receipts += [fn(text) for fn in ALT_READERS.values()]
    return {"raw_source":text,"raw_source_sha256":base.source_sha(text),"receipts":receipts}
