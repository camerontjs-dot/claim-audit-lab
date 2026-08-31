"""Independent Interpretation Authority Contract v1 receipt producer.

This module is intentionally bounded. It recognizes a conservative set of
source constructions and fails closed when source authority or extraction
confidence is absent.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable


_FIELD_ORDERS = {
    "only_permission": (
        "entity",
        "population",
        "membership",
        "predicate",
        "only_population_may",
        "explicit_permission",
    ),
    "role_binding": ("predicate", "subject", "object", "polarity"),
    "quantifier": ("population", "predicate", "quantifier", "polarity"),
}

_TERMINAL_PUNCTUATION = " \t\r\n.,;:!?\"'”’)]}"

_UNSUPPORTED_COMMON = (
    (r"\b(?:most|many|few)\b", "unsupported_semantics"),
    (r"\b\d+(?:\.\d+)?\s*%", "unsupported_semantics"),
    (r"\b(?:probabl(?:e|y|ity)|likely|unlikely)\b", "unsupported_semantics"),
    (r"\b(?:unless|except(?:ing|ion)?|provided that)\b", "unsupported_composition"),
    (r"\b(?:either\b.+\bor\b|neither\b.+\bnor\b)", "unsupported_composition"),
)
_TEMPORAL_OR_CONDITIONAL = re.compile(
    r"\b(?:if|whenever|before|after|until|while)\b", re.IGNORECASE
)


def _normalize(value: str, *, remove_leading_article: bool = True) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.lower().strip()
    value = value.rstrip(_TERMINAL_PUNCTUATION)
    value = re.sub(r"\s+", " ", value).strip()
    if remove_leading_article:
        value = re.sub(r"^(?:a|an|the)\s+", "", value)
    return value


def _normalize_predicate(value: str) -> str:
    return _normalize(value, remove_leading_article=False)


def _null_field(status: str) -> dict[str, Any]:
    return {"status": status, "value": None, "span": None, "warrant": None}


def _field(value: Any, start: int, end: int, text: str, warrant: str,
           status: str = "established") -> dict[str, Any]:
    return {
        "status": status,
        "value": value,
        "span": {"start": start, "end": end, "text": text[start:end]},
        "warrant": warrant,
    }


def _receipt(family: str, fields: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "receipt",
        "family": family,
        "fields": {name: fields[name] for name in _FIELD_ORDERS[family]},
    }


def _out(reason: str) -> dict[str, str]:
    return {"status": "out_of_jurisdiction", "reason": reason}


def _sentences(text: str) -> list[tuple[int, int, str]]:
    # Clause-sized sentence splitting without altering source offsets.
    parts: list[tuple[int, int, str]] = []
    start = 0
    for match in re.finditer(r"[.!?](?:\s+|$)", text):
        end = match.start() + 1
        if text[start:end].strip():
            parts.append((start, end, text[start:end]))
        start = match.end()
    if start < len(text) and text[start:].strip():
        parts.append((start, len(text), text[start:]))
    return parts


def _literal_pattern(phrase: str, *, optional_leading_article: bool = True) -> str:
    norm = _normalize(phrase)
    tokens = norm.split()
    if not tokens:
        return r"(?!)"
    body = r"\s+".join(re.escape(tok) for tok in tokens)
    if optional_leading_article:
        return r"(?:a\s+|an\s+|the\s+)?" + body
    return body


def _literal_matches(text: str, phrase: str) -> list[re.Match[str]]:
    pattern = re.compile(
        r"(?<![\w])" + _literal_pattern(phrase) + r"(?![\w])",
        re.IGNORECASE,
    )
    return list(pattern.finditer(text))


def _verb_forms(verb: str) -> list[str]:
    verb = verb.lower()
    forms = {verb}
    if verb.endswith("e"):
        forms.add(verb + "d")
        forms.add(verb[:-1] + "ing")
    else:
        forms.add(verb + "ed")
        forms.add(verb + "ing")
    if verb.endswith("y") and len(verb) > 1 and verb[-2] not in "aeiou":
        forms.add(verb[:-1] + "ies")
        forms.add(verb[:-1] + "ied")
    else:
        forms.add(verb + "s")
    if verb.endswith(("s", "x", "z", "ch", "sh", "o")):
        forms.add(verb + "es")
    return sorted(forms, key=len, reverse=True)


def _predicate_pattern(predicate: str, *, participle_only: bool = False) -> str:
    norm = _normalize_predicate(predicate)
    tokens = norm.split()
    if not tokens:
        return r"(?!)"
    verb = tokens[0]
    forms = _verb_forms(verb)
    if participle_only:
        forms = [f for f in forms if f.endswith(("ed", "ied", "d"))] or forms
    verb_pat = "(?:" + "|".join(re.escape(f) for f in forms) + ")"
    if len(tokens) == 1:
        return verb_pat
    rest = r"\s+".join(re.escape(tok) for tok in tokens[1:])
    return verb_pat + r"\s+(?:a\s+|an\s+|the\s+)?" + rest


def _predicate_matches(text: str, predicate: str) -> list[re.Match[str]]:
    return list(
        re.finditer(
            r"(?<![\w])" + _predicate_pattern(predicate) + r"(?![\w])",
            text,
            re.IGNORECASE,
        )
    )


def _first_unique(matches: Iterable[re.Match[str]]) -> re.Match[str] | None:
    seq = list(matches)
    return seq[0] if seq else None


def _unsupported_reason(text: str, family: str) -> str | None:
    for pattern, reason in _UNSUPPORTED_COMMON:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            return reason

    # Numeric exact-count language is unsupported, but "at least one" and
    # "not one" are contract-supported quantifier wording.
    scrubbed = re.sub(r"\b(?:at least|not)\s+one\b", "", text, flags=re.IGNORECASE)
    if re.search(r"\b(?:exactly\s+)?\d+\b", scrubbed, re.IGNORECASE):
        return "unsupported_semantics"
    if re.search(
        r"\b(?:exactly\s+(?:one|two|three|four|five|six|seven|eight|nine|ten))\b",
        scrubbed,
        re.IGNORECASE,
    ):
        return "unsupported_semantics"

    if _TEMPORAL_OR_CONDITIONAL.search(text):
        return "unsupported_composition"

    if family == "role_binding":
        # Possibility, intention, or obligation without an asserted actual
        # event is outside this family.
        if re.search(
            r"\b(?:might|could|should|must|plans? to|intends? to|is to|was to)\b",
            text,
            re.IGNORECASE,
        ):
            return "unsupported_semantics"

    return None


def _reference_field(text: str, phrase: str, warrant: str) -> dict[str, Any]:
    match = _first_unique(_literal_matches(text, phrase))
    if match is None:
        return _null_field("insufficient_authority")
    return _field(_normalize(phrase), match.start(), match.end(), text, warrant)


def _predicate_reference(text: str, predicate: str, warrant: str) -> dict[str, Any]:
    match = _first_unique(_predicate_matches(text, predicate))
    if match is None:
        return _null_field("insufficient_authority")
    return _field(_normalize_predicate(predicate), match.start(), match.end(), text, warrant)


def _singular_candidates(population: str) -> list[str]:
    norm = _normalize(population)
    candidates = [norm]
    if norm.endswith("ies") and len(norm) > 3:
        candidates.append(norm[:-3] + "y")
    elif norm.endswith("s") and not norm.endswith("ss"):
        candidates.append(norm[:-1])
    return list(dict.fromkeys(candidates))


def _clause_field(
    text: str, value: Any, match: re.Match[str], warrant: str,
    *, status: str = "established"
) -> dict[str, Any]:
    return _field(value, match.start(), match.end(), text, warrant, status=status)


def _select_semantic_match(
    text: str,
    candidates: list[tuple[str, re.Match[str], str]],
) -> dict[str, Any] | None:
    """Return a unique semantic candidate or extraction_unresolved on conflict."""
    if not candidates:
        return None
    values = {value for value, _, _ in candidates}
    if len(values) != 1:
        return _null_field("extraction_unresolved")
    value, match, warrant = candidates[0]
    return _clause_field(text, value, match, warrant)


def _permission_membership(
    text: str, entity: str, population: str
) -> dict[str, Any]:
    ep = _literal_pattern(entity)
    pp = _literal_pattern(population)
    singulars = _singular_candidates(population)
    singular_pat = "(?:" + "|".join(_literal_pattern(x) for x in singulars) + ")"

    unknown_patterns = [
        rf"\bit\s+is\s+unknown\s+whether\s+{ep}\s+is\s+(?:a\s+member\s+of\s+{pp}|{singular_pat})",
        rf"\bwhether\s+{ep}\s+is\s+(?:a\s+member\s+of\s+{pp}|{singular_pat})\s+is\s+unknown\b",
        rf"\b{ep}(?:'s|’s)\s+membership\s+in\s+{pp}\s+is\s+unknown\b",
    ]
    unknown_matches = [
        m for p in unknown_patterns for m in re.finditer(p, text, re.IGNORECASE)
    ]
    if unknown_matches:
        m = unknown_matches[0]
        return _field(
            "unknown", m.start(), m.end(), text,
            "explicit_unknown_assertion", status="semantic_unknown"
        )

    candidates: list[tuple[str, re.Match[str], str]] = []
    positive = [
        rf"\b{ep}\s+is\s+(?:a\s+|an\s+)?member\s+of\s+{pp}\b",
        rf"\b{ep}\s+belongs\s+to\s+{pp}\b",
        rf"\b{ep}\s+is\s+(?:a\s+|an\s+)?{singular_pat}\b",
    ]
    negative = [
        rf"\b{ep}\s+is\s+not\s+(?:a\s+|an\s+)?member\s+of\s+{pp}\b",
        rf"\b{ep}\s+does\s+not\s+belong\s+to\s+{pp}\b",
        rf"\b{ep}\s+is\s+not\s+(?:a\s+|an\s+)?{singular_pat}\b",
    ]
    for p in positive:
        for m in re.finditer(p, text, re.IGNORECASE):
            candidates.append(("member", m, "explicit_membership_assertion"))
    for p in negative:
        for m in re.finditer(p, text, re.IGNORECASE):
            candidates.append(("non_member", m, "explicit_nonmembership_assertion"))

    selected = _select_semantic_match(text, candidates)
    if selected is not None:
        return selected

    # Same-clause entity/population plus membership-like language indicates a
    # supported construction the implementation failed to recover uniquely.
    for _, _, sentence in _sentences(text):
        if (
            _literal_matches(sentence, entity)
            and _literal_matches(sentence, population)
            and re.search(r"\b(?:member|membership|belong|include|part of)\b", sentence, re.IGNORECASE)
        ):
            return _null_field("extraction_unresolved")
    return _null_field("insufficient_authority")


def _permission_condition(
    text: str, population: str, predicate: str
) -> tuple[dict[str, Any], re.Match[str] | None]:
    pp = _literal_pattern(population)
    pred = _predicate_pattern(predicate)
    patterns = [
        rf"\bonly\s+{pp}\s+may\s+{pred}\b",
        rf"\bonly\s+{pp}\s+(?:are\s+)?(?:permitted|authorized|allowed)\s+to\s+{pred}\b",
        rf"\b{pred}\s+is\s+restricted\s+to\s+{pp}\b",
        rf"\bpermission\s+to\s+{pred}\s+is\s+limited\s+to\s+{pp}\b",
    ]
    matches = [m for p in patterns for m in re.finditer(p, text, re.IGNORECASE)]
    if not matches:
        return _null_field("insufficient_authority"), None
    m = matches[0]
    return _field(True, m.start(), m.end(), text, "necessary_permission_condition"), m


def _explicit_permission(
    text: str, entity: str, predicate: str, condition_match: re.Match[str] | None
) -> dict[str, Any]:
    ep = _literal_pattern(entity)
    pred = _predicate_pattern(predicate)

    unknown_patterns = [
        rf"\bit\s+is\s+unknown\s+whether\s+{ep}\s+is\s+(?:permitted|authorized|allowed)\s+to\s+{pred}\b",
        rf"\bwhether\s+{ep}\s+is\s+(?:permitted|authorized|allowed)\s+to\s+{pred}\s+is\s+unknown\b",
        rf"\b{ep}(?:'s|’s)\s+permission\s+to\s+{pred}\s+is\s+unknown\b",
    ]
    unknown_matches = [
        m for p in unknown_patterns for m in re.finditer(p, text, re.IGNORECASE)
    ]
    if unknown_matches:
        m = unknown_matches[0]
        return _field(
            "unknown", m.start(), m.end(), text,
            "explicit_unknown_assertion", status="semantic_unknown"
        )

    candidates: list[tuple[str, re.Match[str], str]] = []
    positive = [
        rf"\b{ep}\s+is\s+(?:explicitly\s+)?(?:permitted|authorized|allowed)\s+to\s+{pred}\b",
        rf"\b{ep}\s+has\s+permission\s+to\s+{pred}\b",
    ]
    negative = [
        rf"\b{ep}\s+is\s+not\s+(?:permitted|authorized|allowed)\s+to\s+{pred}\b",
        rf"\b{ep}\s+does\s+not\s+have\s+permission\s+to\s+{pred}\b",
    ]
    for p in positive:
        for m in re.finditer(p, text, re.IGNORECASE):
            if condition_match is None or not (
                condition_match.start() <= m.start() and m.end() <= condition_match.end()
            ):
                candidates.append(("permitted", m, "explicit_permission_grant"))
    for p in negative:
        for m in re.finditer(p, text, re.IGNORECASE):
            candidates.append(("not_permitted", m, "explicit_permission_denial"))

    selected = _select_semantic_match(text, candidates)
    if selected is not None:
        return selected

    # If the entity and predicate co-occur with permission vocabulary but no
    # supported direct grant/denial/unknown form was extracted, abstain as an
    # extraction limitation rather than claiming missing source authority.
    for _, _, sentence in _sentences(text):
        if (
            _literal_matches(sentence, entity)
            and _predicate_matches(sentence, predicate)
            and re.search(r"\b(?:permission|permitted|authorized|allowed)\b", sentence, re.IGNORECASE)
        ):
            return _null_field("extraction_unresolved")
    return _null_field("insufficient_authority")


def _interpret_permission(text: str, query: dict[str, Any]) -> dict[str, Any]:
    entity = query.get("entity")
    population = query.get("population")
    predicate = query.get("predicate")
    if not all(isinstance(x, str) and x.strip() for x in (entity, population, predicate)):
        return _out("unsupported_family")

    reason = _unsupported_reason(text, "only_permission")
    if reason:
        return _out(reason)

    entity_field = _reference_field(text, entity, "named_entity_reference")
    population_field = _reference_field(text, population, "named_population_reference")
    predicate_field = _predicate_reference(text, predicate, "permission_predicate_reference")
    membership = _permission_membership(text, entity, population)
    condition, condition_match = _permission_condition(text, population, predicate)
    permission = _explicit_permission(text, entity, predicate, condition_match)

    return _receipt(
        "only_permission",
        {
            "entity": entity_field,
            "population": population_field,
            "membership": membership,
            "predicate": predicate_field,
            "only_population_may": condition,
            "explicit_permission": permission,
        },
    )


def _entity_pattern(value: str) -> str:
    return _literal_pattern(value)


def _active_negative_pattern(subject: str, object_: str, predicate: str) -> str:
    sp = _entity_pattern(subject)
    op = _entity_pattern(object_)
    tokens = _normalize_predicate(predicate).split()
    verb = re.escape(tokens[0])
    if len(tokens) > 1:
        rest = r"\s+(?:a\s+|an\s+|the\s+)?" + r"\s+".join(
            re.escape(t) for t in tokens[1:]
        )
    else:
        rest = ""
    return rf"\b{sp}\s+(?:did|does|do)\s+not\s+{verb}{rest}\s+{op}\b"


def _interpret_event(text: str, query: dict[str, Any]) -> dict[str, Any]:
    predicate = query.get("predicate")
    roles = query.get("roles")
    if (
        not isinstance(predicate, str)
        or not isinstance(roles, dict)
        or not isinstance(roles.get("subject"), str)
        or not isinstance(roles.get("object"), str)
    ):
        return _out("unsupported_family")
    subject = roles["subject"]
    object_ = roles["object"]

    reason = _unsupported_reason(text, "role_binding")
    if reason:
        return _out(reason)

    pred_ref = _predicate_reference(text, predicate, "event_predicate_reference")

    sp = _entity_pattern(subject)
    op = _entity_pattern(object_)
    base_pred = _predicate_pattern(predicate)
    part_pred = _predicate_pattern(predicate, participle_only=True)

    patterns: list[tuple[str, str, str]] = [
        (
            "negative",
            "active_role_binding",
            _active_negative_pattern(subject, object_, predicate),
        ),
        (
            "negative",
            "passive_role_binding",
            rf"\b{op}\s+(?:was|were|is|are|has\s+been|have\s+been)\s+not\s+{part_pred}\s+by\s+{sp}\b",
        ),
        (
            "positive",
            "passive_role_binding",
            rf"\b{op}\s+(?:was|were|is|are|has\s+been|have\s+been)\s+{part_pred}\s+by\s+{sp}\b",
        ),
        (
            "positive",
            "active_role_binding",
            rf"\b{sp}\s+{base_pred}\s+{op}\b",
        ),
    ]
    matches: list[tuple[str, str, re.Match[str]]] = []
    for polarity, warrant, pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append((polarity, warrant, match))

    if len({p for p, _, _ in matches}) > 1:
        subject_field = object_field = polarity_field = _null_field("extraction_unresolved")
    elif matches:
        polarity, warrant, match = matches[0]
        subject_field = _field(
            _normalize(subject), match.start(), match.end(), text, warrant
        )
        object_field = _field(
            _normalize(object_), match.start(), match.end(), text, warrant
        )
        polarity_field = _field(
            polarity,
            match.start(),
            match.end(),
            text,
            "explicit_negation" if polarity == "negative" else "explicit_affirmation",
        )
    else:
        subject_present = bool(_literal_matches(text, subject))
        object_present = bool(_literal_matches(text, object_))
        pred_present = bool(_predicate_matches(text, predicate))

        unresolved_event_clause = False
        verb = _normalize_predicate(predicate).split()[0] if _normalize_predicate(predicate).split() else ""
        inflected_forms = [f for f in _verb_forms(verb) if f != verb]
        inflected_pat = (
            r"(?<![\w])(?:" + "|".join(re.escape(f) for f in inflected_forms) + r")(?![\w])"
            if inflected_forms
            else r"(?!)"
        )
        for _, _, sentence in _sentences(text):
            if (
                _literal_matches(sentence, subject)
                and _literal_matches(sentence, object_)
                and re.search(inflected_pat, sentence, re.IGNORECASE)
            ):
                unresolved_event_clause = True
                break

        if subject_present and object_present and pred_present and unresolved_event_clause:
            # The source appears to assert the target event in one clause, but
            # this conservative extractor did not recover the role binding.
            subject_field = object_field = polarity_field = _null_field(
                "extraction_unresolved"
            )
        else:
            # Mere co-mention of entities and predicate is not role authority.
            subject_field = _null_field("insufficient_authority")
            object_field = _null_field("insufficient_authority")
            polarity_field = _null_field("insufficient_authority")

    return _receipt(
        "role_binding",
        {
            "predicate": pred_ref,
            "subject": subject_field,
            "object": object_field,
            "polarity": polarity_field,
        },
    )


def _quantifier_clause(
    text: str, population: str, predicate: str
) -> tuple[str, str, re.Match[str]] | None:
    pp = _literal_pattern(population)
    singulars = _singular_candidates(population)
    singular_pat = "(?:" + "|".join(_literal_pattern(x) for x in singulars) + ")"
    pred = _predicate_pattern(predicate)

    patterns = [
        ("not_every", "nonuniversal_quantifier", rf"\bnot\s+every\s+{singular_pat}\s+{pred}\b"),
        ("not_every", "nonuniversal_quantifier", rf"\bnot\s+all\s+{pp}\s+{pred}\b"),
        ("none", "empty_quantifier", rf"\bnone\s+of\s+{pp}\s+{pred}\b"),
        ("none", "empty_quantifier", rf"\bnot\s+one\s+{singular_pat}\s+{pred}\b"),
        ("none", "empty_quantifier", rf"\bno\s+(?:{pp}|{singular_pat})\s+{pred}\b"),
        ("some", "existential_quantifier", rf"\bat\s+least\s+one\s+{singular_pat}\s+{pred}\b"),
        ("some", "existential_quantifier", rf"\bsome\s+(?:{pp}|{singular_pat})\s+{pred}\b"),
        ("every", "universal_quantifier", rf"(?<!not )\b(?:every|each)\s+{singular_pat}\s+{pred}\b"),
        ("every", "universal_quantifier", rf"(?<!not )\ball\s+{pp}\s+{pred}\b"),
    ]
    matches: list[tuple[str, str, re.Match[str]]] = []
    for value, warrant, pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append((value, warrant, match))
    if not matches:
        return None
    if len({value for value, _, _ in matches}) != 1:
        return ("__conflict__", "", matches[0][2])
    return matches[0]


def _interpret_quantifier(text: str, query: dict[str, Any]) -> dict[str, Any]:
    population = query.get("population")
    predicate = query.get("predicate")
    if not isinstance(population, str) or not isinstance(predicate, str):
        return _out("unsupported_family")

    reason = _unsupported_reason(text, "quantifier")
    if reason:
        return _out(reason)

    clause = _quantifier_clause(text, population, predicate)
    population_matches = _literal_matches(text, population)
    if not population_matches:
        for candidate in _singular_candidates(population):
            population_matches.extend(_literal_matches(text, candidate))
    if population_matches:
        pm = population_matches[0]
        population_ref = _field(
            _normalize(population), pm.start(), pm.end(), text, "quantified_population"
        )
    else:
        population_ref = _null_field("insufficient_authority")
    predicate_ref = _predicate_reference(text, predicate, "quantified_predicate")

    if clause is None:
        quantifier = _null_field("insufficient_authority")
        polarity = _null_field("insufficient_authority")
        # If supported quantifier language and both target references are
        # present but the clause was not extracted, this is parser limitation.
        if (
            re.search(
                r"\b(?:every|all|each|no|none|some|at least one|not every|not all|not one)\b",
                text,
                re.IGNORECASE,
            )
            and population_ref["status"] == "established"
            and predicate_ref["status"] == "established"
        ):
            quantifier = _null_field("extraction_unresolved")
            polarity = _null_field("extraction_unresolved")
    elif clause[0] == "__conflict__":
        quantifier = _null_field("extraction_unresolved")
        polarity = _null_field("extraction_unresolved")
    else:
        value, warrant, match = clause
        quantifier = _field(value, match.start(), match.end(), text, warrant)
        polarity = _field(
            "positive", match.start(), match.end(), text, "explicit_affirmation"
        )

    return _receipt(
        "quantifier",
        {
            "population": population_ref,
            "predicate": predicate_ref,
            "quantifier": quantifier,
            "polarity": polarity,
        },
    )


def interpret(text: str, query: dict) -> dict:
    """Produce a bounded interpretation-authority receipt.

    The structured query selects the supported semantic family but is never
    used as source authority: established values require matching source text.
    """
    if not isinstance(text, str) or not isinstance(query, dict):
        return _out("unsupported_family")

    kind = query.get("kind")
    if kind == "permission":
        return _interpret_permission(text, query)
    if kind == "event":
        return _interpret_event(text, query)
    if kind == "quantified":
        return _interpret_quantifier(text, query)
    return _out("unsupported_family")
