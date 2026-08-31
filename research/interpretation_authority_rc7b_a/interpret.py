"""Clean-room Interpretation Authority Contract v1 receipt producer."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Optional

_FIELD_NULL = {"value": None, "span": None, "warrant": None}


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower().strip()
    value = re.sub(r"[\s]+", " ", value)
    value = re.sub(r"[\s]*[.!?,;:]+$", "", value).strip()
    value = re.sub(r"^(?:a|an|the)\s+", "", value)
    return value


def _status(name: str) -> dict:
    return {"status": name, **_FIELD_NULL}


def _observation(status: str, value, text: str, start: int, end: int, warrant: str) -> dict:
    return {
        "status": status,
        "value": value,
        "span": {"start": start, "end": end, "text": text[start:end]},
        "warrant": warrant,
    }


def _boundary(pattern: str) -> str:
    return rf"(?<!\w)(?:{pattern})(?!\w)"


def _tokens(value: str) -> list[str]:
    return re.findall(r"[^\W_]+(?:[-'][^\W_]+)*", _normalize(value), flags=re.UNICODE)


def _literal_pattern(value: str, *, optional_leading_article: bool = False) -> str:
    tokens = _tokens(value)
    if not tokens:
        return r"(?!)"
    body = r"\s+".join(re.escape(t) for t in tokens)
    if optional_leading_article:
        body = rf"(?:(?:a|an|the)\s+)?{body}"
    return _boundary(body)


def _find_literal(text: str, value: str, *, optional_leading_article: bool = False) -> Optional[re.Match]:
    return re.search(_literal_pattern(value, optional_leading_article=optional_leading_article), text, re.I)


def _singular_candidates(value: str) -> list[str]:
    norm = _normalize(value)
    out = [norm]
    words = norm.split()
    if not words:
        return out
    last = words[-1]
    variants = []
    if last.endswith("ies") and len(last) > 3:
        variants.append(last[:-3] + "y")
    if last.endswith("ses") and len(last) > 3:
        variants.append(last[:-2])
    if last.endswith("s") and not last.endswith("ss") and len(last) > 1:
        variants.append(last[:-1])
    for variant in variants:
        candidate = " ".join(words[:-1] + [variant])
        if candidate not in out:
            out.append(candidate)
    return out


def _noun_pattern(value: str, *, allow_singular: bool = False) -> str:
    candidates = _singular_candidates(value) if allow_singular else [_normalize(value)]
    parts = []
    for candidate in candidates:
        toks = _tokens(candidate)
        if toks:
            parts.append(r"\s+".join(re.escape(t) for t in toks))
    if not parts:
        return r"(?!)"
    return _boundary("|".join(parts))


def _verb_forms(verb: str) -> list[str]:
    verb = _normalize(verb)
    forms = {verb}
    if not verb:
        return []
    if verb.endswith("e"):
        forms.add(verb + "d")
        forms.add(verb[:-1] + "ing")
    elif len(verb) > 1 and verb.endswith("y") and verb[-2] not in "aeiou":
        forms.add(verb[:-1] + "ied")
        forms.add(verb[:-1] + "ies")
        forms.add(verb + "ing")
    else:
        forms.add(verb + "ed")
        forms.add(verb + "ing")
        forms.add(verb + "s")
    # A deliberately small irregular set supports ordinary contract constructions
    # without importing a general NLP lexicon.
    irregular = {
        "be": {"am", "is", "are", "was", "were", "been"},
        "do": {"does", "did", "done"},
        "have": {"has", "had"},
    }
    forms.update(irregular.get(verb, set()))
    return sorted(forms, key=len, reverse=True)


def _predicate_pattern(value: str, *, base_only: bool = False) -> str:
    toks = _tokens(value)
    if not toks:
        return r"(?!)"
    verb = toks[0]
    verb_parts = [re.escape(verb)] if base_only else [re.escape(v) for v in _verb_forms(verb)]
    first = rf"(?:{'|'.join(verb_parts)})"
    if len(toks) == 1:
        return _boundary(first)
    rest = r"\s+".join(re.escape(t) for t in toks[1:])
    # Articles may surface before an object NP even when absent from the canonical query.
    return _boundary(rf"{first}\s+(?:a\s+|an\s+|the\s+)?{rest}")


def _find_predicate(text: str, value: str, *, base_only: bool = False) -> Optional[re.Match]:
    return re.search(_predicate_pattern(value, base_only=base_only), text, re.I)


def _sentence_spans(text: str) -> Iterable[tuple[int, int, str]]:
    start = 0
    for match in re.finditer(r"[.!?;]+(?:\s+|$)", text):
        end = match.start()
        if end > start:
            yield start, end, text[start:end]
        start = match.end()
    if start < len(text):
        yield start, len(text), text[start:]


def _sentences_with(text: str, *patterns: str) -> Iterable[tuple[int, int, str]]:
    for start, end, sentence in _sentence_spans(text):
        if all(re.search(p, sentence, re.I) for p in patterns):
            yield start, end, sentence


def _match_in_sentence(text: str, sentence_start: int, sentence: str, pattern: str) -> Optional[re.Match]:
    return re.search(pattern, sentence, re.I)


def _obs_from_match(status: str, value, text: str, match: re.Match, warrant: str, group=0, base: int = 0) -> dict:
    start = base + match.start(group)
    end = base + match.end(group)
    return _observation(status, value, text, start, end, warrant)


def _unsupported_common(text: str) -> bool:
    patterns = [
        r"\bif\b", r"\bunless\b", r"\bexcept(?:ion| for)?\b",
        r"\bprovided that\b", r"\bon condition that\b",
        r"\bprobably\b", r"\bpossibly\b", r"\blikely\b", r"\bchance\b",
        r"\bbefore\b", r"\bafter\b", r"\buntil\b", r"\bwhile\b",
        r"\beither\b", r"\bdepending on\b",
        r"\b\d+(?:\.\d+)?\s*%\b", r"\bpercent\b",
    ]
    return any(re.search(p, text, re.I) for p in patterns)


def _unsupported_quantifier(text: str) -> bool:
    if _unsupported_common(text):
        return True
    if re.search(r"\b(?:most|many|few|majority|minority|roughly|approximately)\b", text, re.I):
        return True
    if re.search(r"(?<!\w)\d+(?!\w)", text):
        return True
    if re.search(r"\b(?:two|three|four|five|six|seven|eight|nine|ten|dozen)\b", text, re.I):
        return True
    return False


def _receipt(family: str, fields: dict) -> dict:
    return {"status": "receipt", "family": family, "fields": fields}


def _permission_membership(text: str, entity: str, population: str) -> dict:
    ep = _literal_pattern(entity)
    pp = _noun_pattern(population, allow_singular=False)
    singulars = _singular_candidates(population)[1:]
    singular_alt = "|".join(
        r"\s+".join(re.escape(t) for t in _tokens(s)) for s in singulars if _tokens(s)
    )
    member_core = rf"{ep}\s+(?:is|was)\s+(?:a\s+)?member\s+of\s+(?:the\s+)?{pp}"
    belongs_core = rf"{ep}\s+(?:belongs|belonged)\s+to\s+(?:the\s+)?{pp}"
    direct_core = rf"{ep}\s+(?:is|was)\s+(?:a|an)\s+(?:{singular_alt})" if singular_alt else r"(?!)"
    positive = rf"(?:{member_core}|{belongs_core}|{direct_core})"
    negative = rf"(?:{ep}\s+(?:is|was)\s+not\s+(?:a\s+)?member\s+of\s+(?:the\s+)?{pp}|{ep}\s+(?:does|did)\s+not\s+belong\s+to\s+(?:the\s+)?{pp}"
    if singular_alt:
        negative += rf"|{ep}\s+(?:is|was)\s+not\s+(?:a|an)\s+(?:{singular_alt})"
    negative += ")"

    for s_start, _, sentence in _sentences_with(text, ep):
        if not re.search(pp, sentence, re.I) and not (singular_alt and re.search(singular_alt, sentence, re.I)):
            continue
        unknown_cues = re.search(r"\bunknown\b", sentence, re.I) and re.search(r"\bwhether\b", sentence, re.I)
        if unknown_cues and (re.search(positive, sentence, re.I) or re.search(negative, sentence, re.I)):
            return _observation(
                "semantic_unknown", "unknown", text, s_start, s_start + len(sentence),
                "explicit_unknown_assertion",
            )
        m = re.search(negative, sentence, re.I)
        if m:
            return _obs_from_match("established", "non_member", text, m, "explicit_nonmembership_assertion", base=s_start)
        m = re.search(positive, sentence, re.I)
        if m:
            return _obs_from_match("established", "member", text, m, "explicit_membership_assertion", base=s_start)
    return _status("insufficient_authority")


def _permission_explicit(text: str, entity: str, predicate: str) -> dict:
    ep = _literal_pattern(entity)
    pred = _predicate_pattern(predicate, base_only=True)
    positive = rf"{ep}\s+(?:is|was)\s+(?:explicitly\s+)?(?:permitted|authorized|allowed)\s+to\s+{pred}"
    negative = rf"{ep}\s+(?:is|was)\s+not\s+(?:permitted|authorized|allowed)\s+to\s+{pred}"
    grant = rf"permission\s+for\s+{ep}\s+to\s+{pred}\s+(?:is|was)\s+granted"
    denial = rf"permission\s+for\s+{ep}\s+to\s+{pred}\s+(?:is|was)\s+denied"

    for s_start, _, sentence in _sentences_with(text, ep):
        if not re.search(pred, sentence, re.I):
            continue
        if re.search(r"\bunknown\b", sentence, re.I) and re.search(r"\bwhether\b", sentence, re.I):
            permission_words = re.search(r"\b(?:permitted|authorized|allowed|permission)\b", sentence, re.I)
            if permission_words:
                return _observation(
                    "semantic_unknown", "unknown", text, s_start, s_start + len(sentence),
                    "explicit_unknown_assertion",
                )
        for pattern in (negative, denial):
            m = re.search(pattern, sentence, re.I)
            if m:
                return _obs_from_match("established", "not_permitted", text, m, "explicit_permission_denial", base=s_start)
        for pattern in (positive, grant):
            m = re.search(pattern, sentence, re.I)
            if m:
                return _obs_from_match("established", "permitted", text, m, "explicit_permission_grant", base=s_start)
    return _status("insufficient_authority")


def _only_condition(text: str, population: str, predicate: str) -> dict:
    pp = _noun_pattern(population)
    pred_any = _predicate_pattern(predicate)
    pred_base = _predicate_pattern(predicate, base_only=True)
    patterns = [
        rf"\bonly\s+(?:the\s+)?{pp}\s+(?:may|can)\s+{pred_base}",
        rf"\bonly\s+(?:the\s+)?{pp}\s+(?:are|were)\s+(?:permitted|authorized|allowed)\s+to\s+{pred_base}",
        rf"{pred_any}\s+(?:is|was)\s+restricted\s+to\s+(?:the\s+)?{pp}",
        rf"permission\s+to\s+{pred_base}\s+(?:is|was)\s+(?:limited|restricted)\s+to\s+(?:the\s+)?{pp}",
    ]
    for s_start, _, sentence in _sentence_spans(text):
        for pattern in patterns:
            m = re.search(pattern, sentence, re.I)
            if m:
                return _obs_from_match("established", True, text, m, "necessary_permission_condition", base=s_start)

    if _find_literal(text, population) and _find_predicate(text, predicate):
        if re.search(r"\b(?:only|solely|exclusively|restricted|limited)\b", text, re.I):
            return _status("extraction_unresolved")
    return _status("insufficient_authority")


def _interpret_permission(text: str, query: dict) -> dict:
    if _unsupported_common(text):
        return {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"}

    entity = _normalize(str(query.get("entity", "")))
    population = _normalize(str(query.get("population", "")))
    predicate = _normalize(str(query.get("predicate", "")))

    em = _find_literal(text, entity)
    pm = _find_literal(text, population)
    predm = _find_predicate(text, predicate)

    fields = {
        "entity": _obs_from_match("established", entity, text, em, "named_entity_reference") if em else _status("insufficient_authority"),
        "population": _obs_from_match("established", population, text, pm, "named_population_reference") if pm else _status("insufficient_authority"),
        "membership": _permission_membership(text, entity, population),
        "predicate": _obs_from_match("established", predicate, text, predm, "permission_predicate_reference") if predm else _status("insufficient_authority"),
        "only_population_may": _only_condition(text, population, predicate),
        "explicit_permission": _permission_explicit(text, entity, predicate),
    }
    return _receipt("only_permission", fields)


def _event_relation(text: str, predicate: str, subject: str, obj: str) -> Optional[tuple[str, re.Match, int]]:
    sp = _literal_pattern(subject)
    op = _literal_pattern(obj, optional_leading_article=True)
    pred_inflected = _predicate_pattern(predicate)
    pred_base = _predicate_pattern(predicate, base_only=True)
    toks = _tokens(predicate)
    # These patterns intentionally cover direct active/passive clauses. More
    # elaborate supported syntax fails closed as extraction_unresolved.
    active_negative = rf"{sp}\s+(?:did|does|do)\s+(?P<neg>not)\s+{pred_base}\s+(?:the\s+)?{op}"
    active_positive = rf"{sp}\s+(?:\w+\s+){{0,2}}?{pred_inflected}\s+(?:the\s+)?{op}"
    passive = rf"{op}\s+(?:was|were|is|are|has\s+been|have\s+been)\s+(?P<neg>not\s+)?{pred_inflected}\s+by\s+{sp}"
    for s_start, _, sentence in _sentence_spans(text):
        m = re.search(passive, sentence, re.I)
        if m:
            return ("passive", m, s_start)
        m = re.search(active_negative, sentence, re.I)
        if m:
            return ("active_negative", m, s_start)
        m = re.search(active_positive, sentence, re.I)
        if m:
            return ("active", m, s_start)
    return None


def _interpret_event(text: str, query: dict) -> dict:
    predicate = _normalize(str(query.get("predicate", "")))
    roles = query.get("roles") if isinstance(query.get("roles"), dict) else {}
    subject = _normalize(str(roles.get("subject", "")))
    obj = _normalize(str(roles.get("object", "")))

    pred_base_pattern = _predicate_pattern(predicate, base_only=True)
    modal_relation = (
        rf"{_literal_pattern(subject)}\s+"
        rf"(?:may|might|could|should|must|intends?\s+to|plans?\s+to)\s+"
        rf"{pred_base_pattern}"
    )
    if re.search(modal_relation, text, re.I):
        return {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"}

    relation = _event_relation(text, predicate, subject, obj)

    if relation is None:
        predm = _find_predicate(text, predicate)
        sm = _find_literal(text, subject)
        om = _find_literal(text, obj, optional_leading_article=True)
        if predm and re.search(r"\b(?:may|might|could|should|must|intends?\s+to|plans?\s+to|possibly|probably)\b", text, re.I):
            return {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"}
        if _unsupported_common(text):
            return {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"}

        predicate_field = (
            _obs_from_match("established", predicate, text, predm, "event_predicate_reference")
            if predm else _status("insufficient_authority")
        )
        if predm and sm and om:
            surface = _normalize(predm.group(0))
            base_pred = _normalize(predicate)
            looks_assertive = surface != base_pred
            if looks_assertive:
                unresolved = _status("extraction_unresolved")
                return _receipt("role_binding", {
                    "predicate": predicate_field,
                    "subject": unresolved.copy(),
                    "object": unresolved.copy(),
                    "polarity": unresolved.copy(),
                })
        return _receipt("role_binding", {
            "predicate": predicate_field,
            "subject": _status("insufficient_authority"),
            "object": _status("insufficient_authority"),
            "polarity": _status("insufficient_authority"),
        })

    if _unsupported_common(text):
        return {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"}

    kind, m, base = relation
    clause_start = base + m.start()
    clause_end = base + m.end()
    clause_span = lambda status, value, warrant: _observation(
        status, value, text, clause_start, clause_end, warrant
    )
    predm = _find_predicate(text[clause_start:clause_end], predicate)
    if predm:
        predicate_field = _observation(
            "established", predicate, text,
            clause_start + predm.start(), clause_start + predm.end(),
            "event_predicate_reference",
        )
    else:
        predicate_field = _status("extraction_unresolved")

    passive = kind == "passive"
    neg = kind == "active_negative" or bool(m.groupdict().get("neg"))
    role_warrant = "passive_role_binding" if passive else "active_role_binding"
    polarity = "negative" if neg else "positive"
    polarity_warrant = "explicit_negation" if neg else "explicit_affirmation"
    if neg:
        neg_text = m.groupdict().get("neg") or "not"
        local = re.search(r"\bnot\b", text[clause_start:clause_end], re.I)
        polarity_field = (
            _observation("established", polarity, text, clause_start + local.start(), clause_start + local.end(), polarity_warrant)
            if local else clause_span("established", polarity, polarity_warrant)
        )
    else:
        polarity_field = clause_span("established", polarity, polarity_warrant)

    return _receipt("role_binding", {
        "predicate": predicate_field,
        "subject": clause_span("established", subject, role_warrant),
        "object": clause_span("established", obj, role_warrant),
        "polarity": polarity_field,
    })


def _interpret_quantifier(text: str, query: dict) -> dict:
    if _unsupported_quantifier(text):
        return {"status": "out_of_jurisdiction", "reason": "unsupported_semantics"}

    population = _normalize(str(query.get("population", "")))
    predicate = _normalize(str(query.get("predicate", "")))
    popp = _noun_pattern(population, allow_singular=True)
    predp = _predicate_pattern(predicate)
    quant = (
        r"(?P<q>not\s+every|not\s+all|at\s+least\s+one|not\s+one|"
        r"every|each|all|none|no|some)"
    )
    patterns = [
        rf"{quant}\s+(?:of\s+(?:the\s+)?)?(?P<pop>{popp})\s+(?P<pred>{predp})",
    ]
    mapping = {
        "every": ("every", "universal_quantifier"),
        "all": ("every", "universal_quantifier"),
        "each": ("every", "universal_quantifier"),
        "no": ("none", "empty_quantifier"),
        "none": ("none", "empty_quantifier"),
        "not one": ("none", "empty_quantifier"),
        "some": ("some", "existential_quantifier"),
        "at least one": ("some", "existential_quantifier"),
        "not every": ("not_every", "nonuniversal_quantifier"),
        "not all": ("not_every", "nonuniversal_quantifier"),
    }

    for s_start, _, sentence in _sentence_spans(text):
        for pattern in patterns:
            m = re.search(pattern, sentence, re.I)
            if not m:
                continue
            q_surface = _normalize(m.group("q"))
            quant_value, quant_warrant = mapping[q_surface]
            pop_surface = _normalize(m.group("pop"))
            # Preserve source singular/plural form as required by normalization.
            return _receipt("quantifier", {
                "population": _obs_from_match("established", pop_surface, text, m, "quantified_population", group="pop", base=s_start),
                "predicate": _obs_from_match("established", predicate, text, m, "quantified_predicate", group="pred", base=s_start),
                "quantifier": _obs_from_match("established", quant_value, text, m, quant_warrant, group="q", base=s_start),
                "polarity": _observation("established", "positive", text, s_start + m.start(), s_start + m.end(), "explicit_affirmation"),
            })

    popm = re.search(popp, text, re.I)
    predm = re.search(predp, text, re.I)
    qm = re.search(r"\b(?:every|each|all|none|no|some|not\s+every|not\s+all|at\s+least\s+one|not\s+one)\b", text, re.I)
    if popm and predm and qm:
        unresolved = _status("extraction_unresolved")
        return _receipt("quantifier", {
            "population": unresolved.copy(),
            "predicate": unresolved.copy(),
            "quantifier": unresolved.copy(),
            "polarity": unresolved.copy(),
        })

    return _receipt("quantifier", {
        "population": _status("insufficient_authority"),
        "predicate": _status("insufficient_authority"),
        "quantifier": _status("insufficient_authority"),
        "polarity": _status("insufficient_authority"),
    })


def interpret(text: str, query: dict) -> dict:
    """Return a field-level source-authority receipt for the supported contract."""
    if not isinstance(text, str) or not isinstance(query, dict):
        return {"status": "out_of_jurisdiction", "reason": "unsupported_family"}

    kind = query.get("kind")
    if kind == "permission":
        return _interpret_permission(text, query)
    if kind == "event":
        return _interpret_event(text, query)
    if kind == "quantified":
        return _interpret_quantifier(text, query)
    return {"status": "out_of_jurisdiction", "reason": "unsupported_family"}
