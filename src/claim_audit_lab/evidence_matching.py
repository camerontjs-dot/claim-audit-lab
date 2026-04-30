"""Transparent evidence-candidate matching."""

from __future__ import annotations

import re
from dataclasses import dataclass

from claim_audit_lab.models import AuditConfig, Claim, EvidenceBundle, EvidenceCandidate

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?%?\b")
_DATE_RE = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{4})\b")

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "from",
    "for",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "when",
    "with",
}

_LIMITATION_TERMS = {
    "ambiguous",
    "incomplete",
    "known",
    "limitation",
    "miss",
    "not",
    "tested",
}

_SCOPE_TERMS = {
    "across",
    "all",
    "any",
    "entire",
    "every",
    "throughout",
    "universal",
}

_PREDICTION_TERMS = {
    "always",
    "ensures",
    "guarantees",
    "never",
    "prevent",
    "should",
    "will",
}

_COMPARISON_TERMS = {
    "better",
    "compared",
    "faster",
    "higher",
    "lower",
    "manual",
    "more",
    "reduced",
    "slower",
    "than",
    "worse",
}


@dataclass(frozen=True)
class _ScoreSignals:
    score: float
    matched_numbers: tuple[str, ...]
    missing_claim_numbers: tuple[str, ...]
    matched_dates: tuple[str, ...]
    overlapping_terms: tuple[str, ...]
    limitation_signal: bool


def match_evidence(
    claim: Claim,
    evidence_bundle: EvidenceBundle,
    config: AuditConfig | None = None,
) -> list[EvidenceCandidate]:
    """Return deterministic candidate evidence links for one claim."""
    active_config = config or AuditConfig()
    candidates: list[EvidenceCandidate] = []

    for source in evidence_bundle.sources:
        for excerpt in source.excerpts:
            signals = _score_pair(claim.text, excerpt.text)
            if signals.score < active_config.min_overlap_score:
                continue

            candidates.append(
                EvidenceCandidate(
                    source_id=source.id,
                    excerpt_id=excerpt.id,
                    score=signals.score,
                    rationale=_build_rationale(signals, source.reliability),
                    source_reliability=source.reliability,
                    source_date=source.date,
                )
            )

    return sorted(
        candidates,
        key=lambda candidate: (-candidate.score, candidate.source_id, candidate.excerpt_id),
    )[: active_config.max_candidate_evidence]


def match_claims_to_evidence(
    claims: list[Claim],
    evidence_bundle: EvidenceBundle,
    config: AuditConfig | None = None,
) -> dict[str, list[EvidenceCandidate]]:
    """Return evidence candidates keyed by claim ID."""
    return {claim.id: match_evidence(claim, evidence_bundle, config) for claim in claims}


def _score_pair(claim_text: str, excerpt_text: str) -> _ScoreSignals:
    claim_numbers = _numbers(claim_text)
    excerpt_numbers = _numbers(excerpt_text)
    matched_numbers = tuple(sorted(claim_numbers & excerpt_numbers, key=_number_sort_key))
    missing_claim_numbers = tuple(sorted(claim_numbers - excerpt_numbers, key=_number_sort_key))

    claim_dates = _dates(claim_text)
    excerpt_dates = _dates(excerpt_text)
    matched_dates = tuple(sorted(claim_dates & excerpt_dates))

    claim_terms = _terms(claim_text)
    excerpt_terms = _terms(excerpt_text)
    claim_term_set = set(claim_terms)
    excerpt_term_set = set(excerpt_terms)
    overlapping_terms = tuple(sorted(claim_term_set & excerpt_term_set))

    term_score = _term_score(claim_term_set, excerpt_term_set, overlapping_terms)
    phrase_score = _phrase_score(claim_terms, excerpt_terms)
    number_score = _number_score(claim_numbers, matched_numbers)
    date_score = 0.08 if matched_dates else 0.0
    limitation_score = _limitation_score(claim_term_set, excerpt_term_set, overlapping_terms)
    limitation_signal = limitation_score > 0.0
    comparison_score = _comparison_score(claim_term_set, excerpt_term_set, overlapping_terms)

    score = term_score + phrase_score + number_score + date_score + limitation_score
    score += comparison_score

    if claim_numbers and not matched_numbers and overlapping_terms:
        score = min(score, 0.69)

    return _ScoreSignals(
        score=round(min(max(score, 0.0), 1.0), 4),
        matched_numbers=matched_numbers,
        missing_claim_numbers=missing_claim_numbers if claim_numbers and overlapping_terms else (),
        matched_dates=matched_dates,
        overlapping_terms=overlapping_terms,
        limitation_signal=limitation_signal,
    )


def _terms(text: str) -> tuple[str, ...]:
    terms: list[str] = []
    for token in _TOKEN_RE.findall(text.lower()):
        if token in _STOPWORDS or _NUMBER_RE.fullmatch(token):
            continue
        terms.append(_light_stem(token))
    return tuple(terms)


def _numbers(text: str) -> set[str]:
    return {_normalize_number(match) for match in _NUMBER_RE.findall(text.lower())}


def _dates(text: str) -> set[str]:
    return set(_DATE_RE.findall(text.lower()))


def _normalize_number(number: str) -> str:
    return number.rstrip("%")


def _number_sort_key(number: str) -> tuple[int, float | str]:
    try:
        return (0, float(number))
    except ValueError:
        return (1, number)


def _term_score(
    claim_terms: set[str],
    excerpt_terms: set[str],
    overlapping_terms: tuple[str, ...],
) -> float:
    if not claim_terms or not excerpt_terms or not overlapping_terms:
        return 0.0

    coverage = len(overlapping_terms) / len(claim_terms)
    jaccard = len(overlapping_terms) / len(claim_terms | excerpt_terms)
    return (0.35 * coverage) + (0.1 * jaccard)


def _number_score(claim_numbers: set[str], matched_numbers: tuple[str, ...]) -> float:
    if not claim_numbers or not matched_numbers:
        return 0.0

    match_ratio = len(matched_numbers) / len(claim_numbers)
    return 0.46 + (0.12 * match_ratio)


def _phrase_score(claim_terms: tuple[str, ...], excerpt_terms: tuple[str, ...]) -> float:
    claim_phrases = _phrases(claim_terms)
    excerpt_phrases = _phrases(excerpt_terms)
    if not claim_phrases or not excerpt_phrases:
        return 0.0

    overlap_count = len(claim_phrases & excerpt_phrases)
    return min(0.12, overlap_count * 0.04)


def _phrases(terms: tuple[str, ...]) -> set[tuple[str, ...]]:
    phrases: set[tuple[str, ...]] = set()
    for length in (2, 3):
        for index in range(0, len(terms) - length + 1):
            phrases.add(terms[index : index + length])
    return phrases


def _limitation_score(
    claim_terms: set[str],
    excerpt_terms: set[str],
    overlapping_terms: tuple[str, ...],
) -> float:
    if not overlapping_terms:
        return 0.0

    excerpt_has_limitation = bool(excerpt_terms & _LIMITATION_TERMS)
    claim_has_scope = bool(claim_terms & _SCOPE_TERMS)
    claim_has_prediction = bool(claim_terms & _PREDICTION_TERMS)
    if not excerpt_has_limitation or not (claim_has_scope or claim_has_prediction):
        return 0.0

    score = 0.18
    if claim_has_prediction and "miss" in excerpt_terms:
        score += 0.12
    if claim_has_scope and "test" in excerpt_terms:
        score += 0.08
    return score


def _comparison_score(
    claim_terms: set[str],
    excerpt_terms: set[str],
    overlapping_terms: tuple[str, ...],
) -> float:
    if not overlapping_terms:
        return 0.0

    claim_has_comparison = bool(claim_terms & _COMPARISON_TERMS)
    excerpt_has_comparison = bool(excerpt_terms & _COMPARISON_TERMS)
    return 0.12 if claim_has_comparison and excerpt_has_comparison else 0.0


def _build_rationale(signals: _ScoreSignals, source_reliability: str) -> str:
    parts: list[str] = []
    if signals.matched_numbers:
        parts.append(f"matched numbers: {', '.join(signals.matched_numbers)}")
    if signals.missing_claim_numbers:
        parts.append(
            f"claim numbers not found in excerpt: {', '.join(signals.missing_claim_numbers)}"
        )
    if signals.matched_dates:
        parts.append(f"matched dates: {', '.join(signals.matched_dates)}")
    if signals.overlapping_terms:
        terms = ", ".join(signals.overlapping_terms[:6])
        parts.append(f"overlapping terms: {terms}")
    if signals.limitation_signal:
        parts.append("limitation wording overlaps with broad or future-facing claim")
    parts.append(f"source reliability: {source_reliability}")
    return "; ".join(parts)


def _light_stem(token: str) -> str:
    if token.endswith("ies") and len(token) > 4:
        return f"{token[:-3]}y"
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and not token.endswith("ss") and len(token) > 3:
        return token[:-1]
    return token


__all__ = ["match_claims_to_evidence", "match_evidence"]
