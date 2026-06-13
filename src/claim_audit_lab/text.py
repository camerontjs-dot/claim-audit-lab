"""Shared deterministic text normalization helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable

TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?%?\b")
DATE_RE = re.compile(r"\b(?:\d{4}-\d{2}-\d{2}|\d{4})\b")

STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "can",
        "for",
        "from",
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
)


def normalize_text(text: str) -> str:
    """Normalize text to lowercase space-separated tokens."""
    return " ".join(TOKEN_RE.findall(text.lower()))


def light_stem(token: str) -> str:
    """Apply CAL's deliberately small deterministic stemmer."""
    if token.endswith("ies") and len(token) > 4:
        return f"{token[:-3]}y"
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and not token.endswith("ss") and len(token) > 3:
        return token[:-1]
    return token


def terms(text: str) -> tuple[str, ...]:
    """Return normalized content terms in source order."""
    return tuple(
        light_stem(token)
        for token in TOKEN_RE.findall(text.lower())
        if token not in STOPWORDS
        and not NUMBER_RE.fullmatch(token)
        and not DATE_RE.fullmatch(token)
    )


def term_set(text: str) -> set[str]:
    """Return normalized content terms as a set."""
    return set(terms(text))


def numbers(text: str) -> set[str]:
    """Return normalized numeric tokens, ignoring percent suffixes."""
    return {normalize_number(match) for match in NUMBER_RE.findall(text.lower())}


def dates(text: str) -> set[str]:
    """Return ISO-like dates and four-digit years."""
    return set(DATE_RE.findall(text.lower()))


def normalize_number(number: str) -> str:
    """Normalize one numeric token for equality checks."""
    return number.rstrip("%")


def number_sort_key(number: str) -> tuple[int, float | str]:
    """Sort numeric strings numerically before non-numeric fallbacks."""
    try:
        return (0, float(number))
    except ValueError:
        return (1, number)


def normalize_vocabulary(
    values: Iterable[str],
    *,
    drop_stopwords: bool = True,
) -> frozenset[str]:
    """Normalize governed trigger vocabularies through the shared token path."""
    normalized: set[str] = set()
    for value in values:
        for token in TOKEN_RE.findall(value.lower()):
            if drop_stopwords and token in STOPWORDS:
                continue
            normalized.add(light_stem(token))
    return frozenset(normalized)


__all__ = [
    "DATE_RE",
    "NUMBER_RE",
    "STOPWORDS",
    "TOKEN_RE",
    "dates",
    "light_stem",
    "normalize_number",
    "normalize_text",
    "normalize_vocabulary",
    "number_sort_key",
    "numbers",
    "term_set",
    "terms",
]
