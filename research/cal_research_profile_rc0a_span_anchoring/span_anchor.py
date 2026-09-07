"""Research-only exact entity-span anchoring candidate for CAL RC0A."""
from __future__ import annotations


def _is_token_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_"


def _exact_case_insensitive_match(text: str, start: int, surface: str) -> bool:
    end = start + len(surface)
    if end > len(text):
        return False
    return text[start:end].casefold() == surface.casefold()


def lexical_spans(text: str, surface: str) -> list[tuple[int, int]]:
    """Return all exact case-insensitive whole-surface lexical matches.

    Boundaries apply only when the corresponding edge of the requested surface
    is itself token-like. This keeps punctuation/multiword/possessive surfaces
    usable without allowing an alphanumeric surface to match inside a larger
    alphanumeric token.
    """
    needle = surface.strip()
    if not needle:
        return []

    spans: list[tuple[int, int]] = []
    first_token = _is_token_char(needle[0])
    last_token = _is_token_char(needle[-1])

    for start in range(0, len(text) - len(needle) + 1):
        if not _exact_case_insensitive_match(text, start, needle):
            continue
        end = start + len(needle)
        if first_token and start > 0 and _is_token_char(text[start - 1]):
            continue
        if last_token and end < len(text) and _is_token_char(text[end]):
            continue
        spans.append((start, end))
    return spans


def unique_lexical_span(text: str, surface: str) -> tuple[int, int] | None:
    spans = lexical_spans(text, surface)
    if len(spans) != 1:
        return None
    return spans[0]


def weak_parent_unique_substring_span(text: str, surface: str) -> tuple[int, int] | None:
    """Reproduce the frozen RC0 unique-substring behavior as a weak control."""
    needle = surface.strip()
    if not needle:
        return None
    lowered = text.casefold()
    target = needle.casefold()
    starts: list[int] = []
    pos = 0
    while True:
        found = lowered.find(target, pos)
        if found < 0:
            break
        starts.append(found)
        pos = found + 1
    if len(starts) != 1:
        return None
    start = starts[0]
    return start, start + len(needle)


def weak_first_lexical_span(text: str, surface: str) -> tuple[int, int] | None:
    """Deliberately unsafe control: choose the first eligible lexical match."""
    spans = lexical_spans(text, surface)
    return spans[0] if spans else None
