from __future__ import annotations

import re
import unicodedata
from typing import Dict, Iterable, Optional, Tuple


REQUIRED_ONLY_PERMISSION_FIELDS = (
    "entity",
    "population",
    "membership",
    "predicate",
    "only_population_may",
    "explicit_permission",
)


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower().strip()
    value = re.sub(r"[.?!]+$", "", value).strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"^(?:a|an|the)\s+", "", value)
    return value


def _span(text: str, match: re.Match[str]) -> dict:
    start, end = match.span()
    return {"start": start, "end": end, "text": text[start:end]}


def _null_field(status: str = "insufficient_authority") -> dict:
    return {"status": status, "value": None, "span": None, "warrant": None}


def _value_field(value, span: dict, warrant: str, status: str = "established") -> dict:
    return {"status": status, "value": value, "span": span, "warrant": warrant}


def jurisdiction_gate(text: str) -> dict:
    """Classify only semantic jurisdiction. Never recover semantic field values."""
    t = unicodedata.normalize("NFKC", text)
    low = t.lower()

    detectors = [
        (
            "conditional",
            [
                r"\bif\b",
                r"\bprovided\s+that\b",
                r"\bassuming\s+that\b",
                r"\bon\s+condition\s+that\b",
                r"\bcontingent\s+on\b",
            ],
        ),
        (
            "exception",
            [
                r"\bexcept\b",
                r"\bwith\s+the\s+exception\s+of\b",
                r"\bother\s+than\b",
                r"\bexcluding\b",
                r"\bunless\b",
            ],
        ),
        (
            "temporal",
            [
                r"\bbefore\s+(?:the\s+)?(?:cutoff|deadline|date|time)\b",
                r"\bafter\s+(?:the\s+)?(?:cutoff|deadline|date|time)\b",
                r"\bprior\s+to\s+(?:the\s+)?(?:cutoff|deadline|date|time)\b",
                r"\bfollowing\s+(?:the\s+)?(?:cutoff|deadline|date|time)\b",
                r"\buntil\s+(?:the\s+)?(?:cutoff|deadline|date|time)\b",
                r"\bas\s+of\s+\d{4}-\d{2}-\d{2}\b",
            ],
        ),
        (
            "subclass",
            [
                r"\bsubclass\s+of\b",
                r"\bsubset\s+of\b",
                r"\bproper\s+subset\s+of\b",
                r"\bis\s+a\s+kind\s+of\b",
                r"\bare\s+a\s+kind\s+of\b",
                r"\bis\s+a\s+type\s+of\b",
                r"\bare\s+a\s+type\s+of\b",
            ],
        ),
        (
            "quantitative",
            [
                r"\b\d+(?:\.\d+)?\s*%\b",
                r"\b\d+(?:\.\d+)?\s+percent\b",
                r"\b(?:exactly|precisely)\s+\d+\b",
                r"\b(?:most|many|few|majority\s+of)\b",
                r"\bat\s+least\s+\d+\b",
                r"\bat\s+most\s+\d+\b",
            ],
        ),
        (
            "probabilistic",
            [
                r"\bprobably\b",
                r"\blikely\b",
                r"\bunlikely\b",
                r"\bprobability\b",
                r"\bchance\b",
                r"\bmay\s+have\b",
            ],
        ),
    ]

    for category, patterns in detectors:
        for pattern in patterns:
            if re.search(pattern, low):
                return {
                    "status": "out_of_jurisdiction",
                    "reason": "unsupported_semantics",
                    "category": category,
                }

    permission_hint = bool(
        re.search(r"\bonly\b.{0,80}\bmay\b", low)
        or re.search(r"\bpermission\b|\bpermitted\b|\bauthorized\b|\ballowed\b|\bforbid", low)
    )
    quantifier_hint = bool(
        re.search(r"\b(?:every|each|all|none|no|some|not\s+every|not\s+all|not\s+one|at\s+least\s+one)\b", low)
    )
    role_hint = bool(
        re.search(r"\b(?:reviewed|approved|signed|inspected|audited)\s+by\b", low)
        or re.search(r"\b(?:reviewed|approved|signed|inspected|audited)\b", low)
        and bool(re.search(r"\b(?:did\s+not|was\s+not|were\s+not)\b", low))
    )
    family_hints = sum((permission_hint, quantifier_hint, role_hint))
    if family_hints >= 2:
        return {
            "status": "out_of_jurisdiction",
            "reason": "unsupported_composition",
            "category": "cross_family",
        }

    return {"status": "supported", "category": None}


def _first_match(text: str, patterns: Iterable[Tuple[str, str]], flags=re.IGNORECASE) -> Optional[Tuple[re.Match[str], str]]:
    for pattern, warrant in patterns:
        m = re.search(pattern, text, flags)
        if m:
            return m, warrant
    return None


def _phrase_pattern(phrase: str) -> str:
    words = [re.escape(w) for w in _norm(phrase).split()]
    return r"\s+".join(words)


def interpret_only_permission(text: str, query: dict) -> dict:
    if query.get("kind") != "permission":
        return {"status": "out_of_jurisdiction", "reason": "unsupported_family"}

    gate = jurisdiction_gate(text)
    if gate["status"] == "out_of_jurisdiction":
        return {"status": "out_of_jurisdiction", "reason": gate["reason"]}

    entity = _norm(str(query.get("entity", "")))
    population = _norm(str(query.get("population", "")))
    predicate = _norm(str(query.get("predicate", "")))
    ep = _phrase_pattern(entity)
    pp = _phrase_pattern(population)
    vp = _phrase_pattern(predicate)

    fields: Dict[str, dict] = {name: _null_field() for name in REQUIRED_ONLY_PERMISSION_FIELDS}

    # Source identity fields must be independently mentioned.
    m = re.search(rf"\b{ep}\b", text, re.IGNORECASE)
    if m:
        fields["entity"] = _value_field(entity, _span(text, m), "named_entity_reference")

    m = re.search(rf"\b{pp}\b", text, re.IGNORECASE)
    if m:
        fields["population"] = _value_field(population, _span(text, m), "named_population_reference")

    m = re.search(rf"\b{vp}\b", text, re.IGNORECASE)
    if m:
        fields["predicate"] = _value_field(predicate, _span(text, m), "permission_predicate_reference")

    only_patterns = [
        (rf"Only\s+{pp}\s+may\s+{vp}", "necessary_permission_condition"),
        (rf"Permission\s+to\s+{vp}\s+is\s+(?:restricted|limited)\s+to\s+{pp}", "necessary_permission_condition"),
        (rf"Anyone\s+permitted\s+to\s+{vp}\s+must\s+belong\s+to\s+(?:the\s+)?{pp}", "necessary_permission_condition"),
        (rf"To\s+be\s+permitted\s+to\s+{vp},?\s+(?:a\s+person|someone)\s+must\s+belong\s+to\s+(?:the\s+)?{pp}", "necessary_permission_condition"),
        (rf"(?:The\s+)?{pp}\s+(?:are|is)\s+(?:a\s+)?necessary\s+(?:class|condition)\s+for\s+permission\s+to\s+{vp}", "necessary_permission_condition"),
        (rf"Permission\s+to\s+{vp}\s+requires\s+membership\s+in\s+(?:the\s+)?{pp}", "necessary_permission_condition"),
    ]
    found = _first_match(text, only_patterns)
    if found:
        m, warrant = found
        fields["only_population_may"] = _value_field(True, _span(text, m), warrant)

    membership_unknown_patterns = [
        (rf"It\s+is\s+unknown\s+whether\s+{ep}\s+is\s+(?:a\s+)?member\s+of\s+(?:the\s+)?{pp}", "explicit_unknown_assertion"),
        (rf"Whether\s+{ep}\s+belongs\s+to\s+(?:the\s+)?{pp}\s+is\s+unknown", "explicit_unknown_assertion"),
        (rf"(?:The\s+)?record\s+leaves\s+{ep}(?:'s)?\s+membership\s+in\s+(?:the\s+)?{pp}\s+unknown", "explicit_unknown_assertion"),
    ]
    found = _first_match(text, membership_unknown_patterns)
    if found:
        m, warrant = found
        fields["membership"] = _value_field("unknown", _span(text, m), warrant, "semantic_unknown")
    else:
        negative_patterns = [
            (rf"{ep}\s+is\s+not\s+(?:a\s+)?member\s+of\s+(?:the\s+)?{pp}", "explicit_nonmembership_assertion"),
            (rf"{ep}\s+does\s+not\s+belong\s+to\s+(?:the\s+)?{pp}", "explicit_nonmembership_assertion"),
            (rf"{ep}(?:'s)?\s+non-membership\s+in\s+(?:the\s+)?{pp}\s+is\s+confirmed", "explicit_nonmembership_assertion"),
            (rf"(?:The\s+)?record\s+excludes\s+{ep}\s+from\s+(?:the\s+)?{pp}", "explicit_nonmembership_assertion"),
        ]
        found = _first_match(text, negative_patterns)
        if found:
            m, warrant = found
            fields["membership"] = _value_field("non_member", _span(text, m), warrant)
        else:
            positive_patterns = [
                (rf"{ep}\s+is\s+(?:a\s+)?member\s+of\s+(?:the\s+)?{pp}", "explicit_membership_assertion"),
                (rf"{ep}\s+belongs\s+to\s+(?:the\s+)?{pp}", "explicit_membership_assertion"),
                (rf"{ep}(?:'s)?\s+membership\s+in\s+(?:the\s+)?{pp}\s+is\s+confirmed", "explicit_membership_assertion"),
                (rf"(?:The\s+)?record\s+places\s+{ep}\s+in\s+(?:the\s+)?{pp}", "explicit_membership_assertion"),
            ]
            found = _first_match(text, positive_patterns)
            if found:
                m, warrant = found
                fields["membership"] = _value_field("member", _span(text, m), warrant)

    permission_unknown_patterns = [
        (rf"Whether\s+{ep}\s+is\s+permitted\s+to\s+{vp}\s+is\s+unknown", "explicit_unknown_assertion"),
        (rf"Permission\s+for\s+{ep}\s+to\s+{vp}\s+is\s+unknown", "explicit_unknown_assertion"),
        (rf"(?:The\s+)?record\s+leaves\s+{ep}(?:'s)?\s+permission\s+to\s+{vp}\s+unknown", "explicit_unknown_assertion"),
    ]
    found = _first_match(text, permission_unknown_patterns)
    if found:
        m, warrant = found
        fields["explicit_permission"] = _value_field("unknown", _span(text, m), warrant, "semantic_unknown")
    else:
        denial_patterns = [
            (rf"{ep}\s+is\s+not\s+(?:permitted|authorized|allowed)\s+to\s+{vp}", "explicit_permission_denial"),
            (rf"{ep}\s+does\s+not\s+have\s+permission\s+to\s+{vp}", "explicit_permission_denial"),
            (rf"Permission\s+for\s+{ep}\s+to\s+{vp}\s+is\s+denied", "explicit_permission_denial"),
            (rf"(?:The\s+)?record\s+explicitly\s+forbids\s+{ep}\s+from\s+{vp}", "explicit_permission_denial"),
        ]
        found = _first_match(text, denial_patterns)
        if found:
            m, warrant = found
            fields["explicit_permission"] = _value_field("not_permitted", _span(text, m), warrant)
        else:
            grant_patterns = [
                (rf"{ep}\s+is\s+(?:permitted|authorized|allowed)\s+to\s+{vp}", "explicit_permission_grant"),
                (rf"{ep}\s+has\s+permission\s+to\s+{vp}", "explicit_permission_grant"),
                (rf"Permission\s+for\s+{ep}\s+to\s+{vp}\s+is\s+granted", "explicit_permission_grant"),
                (rf"(?:The\s+)?record\s+explicitly\s+allows\s+{ep}\s+to\s+{vp}", "explicit_permission_grant"),
            ]
            found = _first_match(text, grant_patterns)
            if found:
                m, warrant = found
                fields["explicit_permission"] = _value_field("permitted", _span(text, m), warrant)

    return {"status": "receipt", "family": "only_permission", "fields": fields}
