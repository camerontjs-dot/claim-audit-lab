"""Competing proposal instruments for Population Measurement Machinery RC0."""

from __future__ import annotations

import importlib
import re
from typing import Any

from .cohort import (
    ALICE,
    BOB,
    GROUP_A,
    QUALIFIED_PERSONNEL,
    QUALIFIED_TECHNICIANS,
    REVIEWERS,
    STERILE_TECHNICIANS,
    TRAINED_PERSONNEL,
    MembershipAtom,
    MembershipStatus,
    Observation,
    Status,
    SubsetAtom,
)

_ENTITY = {
    "alice": ALICE,
    "bob": BOB,
}

_POPULATION = {
    "qualified technician": QUALIFIED_TECHNICIANS,
    "qualified technicians": QUALIFIED_TECHNICIANS,
    "sterile technician": STERILE_TECHNICIANS,
    "sterile technicians": STERILE_TECHNICIANS,
    "trained personnel": TRAINED_PERSONNEL,
    "reviewer": REVIEWERS,
    "reviewers": REVIEWERS,
    "qualified personnel": QUALIFIED_PERSONNEL,
    "group a": GROUP_A,
}

_MEMBERSHIP_CUES = re.compile(
    r"\b(is|are|member|technician|technicians|reviewer|reviewers|personnel|group|subset)\b",
    re.IGNORECASE,
)

_REPORTING = re.compile(
    r"\b(report|study|article|author)\b.*\b(says?|said|states?|reported|claims?)\b",
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    compact = " ".join(text.strip().split())
    return compact[:-1] if compact.endswith(".") else compact


def _entity(value: str) -> str | None:
    return _ENTITY.get(value.casefold().strip())


def _population(value: str) -> str | None:
    return _POPULATION.get(value.casefold().strip())


def _hazard(text: str) -> str | None:
    low = text.casefold()
    if _REPORTING.search(text) is not None:
        return "reporting scope"
    if re.search(r"\b(some|most|only|no)\b", low):
        return "unsupported quantifier/direction"
    if re.search(r"\b(was|were|may|might)\b", low):
        return "temporal/modal membership"
    if " worked with " in f" {low} ":
        return "association is not membership"
    if " joined " in f" {low} ":
        return "join event is not timeless membership"
    if " or " in f" {low} " or " not only " in f" {low} ":
        return "unsupported role composition"
    if re.fullmatch(r"Alice is qualified", text, re.IGNORECASE):
        return "attribute state neighbor"
    return None


def direct_grammar(text: str) -> Observation:
    """Narrow membership/subset grammar with explicit quantifier/scope refusal."""

    compact = _clean(text)
    hazard = _hazard(compact)
    if hazard is not None:
        return Observation.unresolved(hazard)

    explicit_member = re.fullmatch(
        r"(?P<entity>Alice|Bob)\s+is\s+(?P<neg>not\s+)?a\s+member\s+of\s+"
        r"(?P<population>Group A)",
        compact,
        re.IGNORECASE,
    )
    if explicit_member is not None:
        entity = _entity(explicit_member.group("entity"))
        population = _population(explicit_member.group("population"))
        assert entity is not None and population is not None
        status = (
            MembershipStatus.NON_MEMBER
            if explicit_member.group("neg") is not None
            else MembershipStatus.MEMBER
        )
        return Observation.claimed(MembershipAtom(entity, population, status))

    simple_member = re.fullmatch(
        r"(?P<entity>Alice|Bob)\s+is\s+(?P<neg>not\s+)?a\s+"
        r"(?P<population>qualified technician|reviewer)",
        compact,
        re.IGNORECASE,
    )
    if simple_member is not None:
        entity = _entity(simple_member.group("entity"))
        population = _population(simple_member.group("population"))
        assert entity is not None and population is not None
        status = (
            MembershipStatus.NON_MEMBER
            if simple_member.group("neg") is not None
            else MembershipStatus.MEMBER
        )
        return Observation.claimed(MembershipAtom(entity, population, status))

    plural_subset = re.fullmatch(
        r"(?P<child>Sterile technicians|Reviewers)\s+are\s+"
        r"(?P<parent>trained personnel|qualified personnel)",
        compact,
        re.IGNORECASE,
    )
    if plural_subset is not None:
        child = _population(plural_subset.group("child"))
        parent = _population(plural_subset.group("parent"))
        assert child is not None and parent is not None
        return Observation.claimed(SubsetAtom(child, parent))

    all_subset = re.fullmatch(
        r"All\s+(?P<child>sterile technicians)\s+are\s+"
        r"(?P<parent>trained personnel)",
        compact,
        re.IGNORECASE,
    )
    if all_subset is not None:
        child = _population(all_subset.group("child"))
        parent = _population(all_subset.group("parent"))
        assert child is not None and parent is not None
        return Observation.claimed(SubsetAtom(child, parent))

    every_subset = re.fullmatch(
        r"Every\s+(?P<child>sterile technician)\s+is\s+"
        r"(?P<parent>trained personnel)",
        compact,
        re.IGNORECASE,
    )
    if every_subset is not None:
        child = _population(every_subset.group("child"))
        parent = _population(every_subset.group("parent"))
        assert child is not None and parent is not None
        return Observation.claimed(SubsetAtom(child, parent))

    if _MEMBERSHIP_CUES.search(compact) is not None:
        return Observation.unresolved("membership cue outside bounded grammar")
    return Observation.not_applicable("no population-membership cue")


_NLP: Any | None = None


def _nlp() -> Any:
    global _NLP
    if _NLP is None:
        spacy = importlib.import_module("spacy")
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _known_population_from_text(text: str) -> str | None:
    low = text.casefold()
    for phrase in sorted(_POPULATION, key=len, reverse=True):
        if phrase in low:
            return _POPULATION[phrase]
    return None


def spacy_dependency(text: str) -> Observation:
    """Broad copular/dependency extractor used to expose overreach."""

    compact = _clean(text)
    direct = direct_grammar(compact)
    if direct.status is Status.CLAIMED:
        return direct

    doc = _nlp()(compact)
    low = compact.casefold()

    # Diagnostic lexical extensions.
    belongs = re.fullmatch(r"(?P<entity>Alice|Bob) belongs to Group A", compact, re.IGNORECASE)
    if belongs is not None:
        entity = _entity(belongs.group("entity"))
        assert entity is not None
        return Observation.claimed(
            MembershipAtom(entity, GROUP_A, MembershipStatus.MEMBER)
        )

    among = re.fullmatch(
        r"(?P<entity>Alice|Bob) is among the qualified technicians",
        compact,
        re.IGNORECASE,
    )
    if among is not None:
        entity = _entity(among.group("entity"))
        assert entity is not None
        return Observation.claimed(
            MembershipAtom(entity, QUALIFIED_TECHNICIANS, MembershipStatus.MEMBER)
        )

    include = re.fullmatch(
        r"Qualified technicians include (?P<entity>Alice|Bob)",
        compact,
        re.IGNORECASE,
    )
    if include is not None:
        entity = _entity(include.group("entity"))
        assert entity is not None
        return Observation.claimed(
            MembershipAtom(entity, QUALIFIED_TECHNICIANS, MembershipStatus.MEMBER)
        )

    subset_match = re.fullmatch(
        r"Sterile technicians form a subset of trained personnel",
        compact,
        re.IGNORECASE,
    )
    if subset_match is not None:
        return Observation.claimed(
            SubsetAtom(STERILE_TECHNICIANS, TRAINED_PERSONNEL)
        )

    each = re.fullmatch(
        r"Each sterile technician is trained personnel",
        compact,
        re.IGNORECASE,
    )
    if each is not None:
        return Observation.claimed(
            SubsetAtom(STERILE_TECHNICIANS, TRAINED_PERSONNEL)
        )

    serves = re.fullmatch(
        r"(?P<entity>Alice|Bob) serves as a reviewer",
        compact,
        re.IGNORECASE,
    )
    if serves is not None:
        entity = _entity(serves.group("entity"))
        assert entity is not None
        return Observation.claimed(MembershipAtom(entity, REVIEWERS, MembershipStatus.MEMBER))

    # Broad dependency/cue behavior. It deliberately does not enforce the RC0
    # quantifier, tense, modality, attribution, or disjunction safety envelope.
    if any(token.lemma_.casefold() in {"be", "say"} for token in doc):
        entity = ALICE if "alice" in low else BOB if "bob" in low else None
        population = _known_population_from_text(compact)
        if entity is not None and population is not None:
            negated = " not " in f" {low} "
            status = MembershipStatus.NON_MEMBER if negated else MembershipStatus.MEMBER
            return Observation.claimed(MembershipAtom(entity, population, status))

    if "technicians" in low and "trained personnel" in low:
        return Observation.claimed(
            SubsetAtom(STERILE_TECHNICIANS, TRAINED_PERSONNEL)
        )

    if _MEMBERSHIP_CUES.search(compact) is not None:
        return Observation.unresolved("population cue unresolved by dependency path")
    return Observation.not_applicable("no population cue")


def _safe_diagnostic_surface(text: str) -> bool:
    compact = _clean(text)
    patterns = (
        r"(Alice|Bob) belongs to Group A",
        r"(Alice|Bob) is among the qualified technicians",
        r"Qualified technicians include (Alice|Bob)",
        r"Sterile technicians form a subset of trained personnel",
        r"Each sterile technician is trained personnel",
        r"(Alice|Bob) serves as a reviewer",
    )
    return any(re.fullmatch(pattern, compact, re.IGNORECASE) for pattern in patterns)


def conservative_hybrid(text: str) -> Observation:
    """Use the broad parser only behind an explicit safe-extension surface gate."""

    direct = direct_grammar(text)
    if direct.status is Status.CLAIMED:
        return direct
    if _hazard(_clean(text)) is not None:
        return direct
    if _safe_diagnostic_surface(text):
        return spacy_dependency(text)
    return direct


INSTRUMENTS = {
    "direct_grammar": direct_grammar,
    "spacy_dependency": spacy_dependency,
    "conservative_hybrid": conservative_hybrid,
}
