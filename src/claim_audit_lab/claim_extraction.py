"""Conservative candidate-claim extraction."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator

from claim_audit_lab.classifiers import classify_claim_text
from claim_audit_lab.models import Claim, DraftDocument
from claim_audit_lab.text import TOKEN_RE, normalize_text, term_set

_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")
_MARKDOWN_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+")


def extract_claims(document: DraftDocument) -> list[Claim]:
    """Extract conservative candidate claims from a draft document."""
    claims: list[Claim] = []
    seen_normalized_texts: set[str] = set()
    seen_token_sets: list[set[str]] = []

    for paragraph_index, paragraph in _iter_prose_paragraphs(document.content):
        for sentence_index, sentence in _iter_sentences(paragraph):
            if _should_skip_sentence(sentence):
                continue
            claim_type = classify_claim_text(sentence)
            if claim_type == "unclassified":
                continue

            normalized_text = normalize_text(sentence)
            dedupe_tokens = _dedupe_tokens(normalized_text)
            if _is_duplicate(
                normalized_text,
                dedupe_tokens,
                seen_normalized_texts,
                seen_token_sets,
            ):
                continue

            seen_normalized_texts.add(normalized_text)
            seen_token_sets.append(dedupe_tokens)
            claims.append(
                Claim(
                    id=_claim_id(document.id, normalized_text),
                    text=sentence,
                    claim_type=claim_type,
                    location=f"paragraph:{paragraph_index}:sentence:{sentence_index}",
                )
            )

    return claims


def _iter_prose_paragraphs(content: str) -> Iterator[tuple[int, str]]:
    paragraph_index = 0
    for raw_paragraph in re.split(r"\n\s*\n", content):
        lines: list[str] = []
        for line in raw_paragraph.splitlines():
            stripped = line.strip()
            if not stripped or _MARKDOWN_HEADING_RE.match(stripped):
                continue
            lines.append(stripped)

        if not lines:
            continue

        paragraph_index += 1
        yield paragraph_index, " ".join(lines)


def _iter_sentences(paragraph: str) -> Iterator[tuple[int, str]]:
    for sentence_index, sentence in enumerate(_SENTENCE_BOUNDARY_RE.split(paragraph), start=1):
        stripped = sentence.strip()
        if stripped:
            yield sentence_index, stripped


def _should_skip_sentence(sentence: str) -> bool:
    stripped = sentence.strip()
    if not stripped or stripped.endswith("?"):
        return True

    token_count = len(TOKEN_RE.findall(stripped.lower()))
    return token_count < 4


def _claim_id(document_id: str, normalized_text: str) -> str:
    digest = hashlib.sha256(f"{document_id}:{normalized_text}".encode()).hexdigest()
    return f"claim-{digest[:12]}"


def _dedupe_tokens(normalized_text: str) -> set[str]:
    return term_set(normalized_text)


def _is_duplicate(
    normalized_text: str,
    dedupe_tokens: set[str],
    seen_normalized_texts: set[str],
    seen_token_sets: list[set[str]],
) -> bool:
    if normalized_text in seen_normalized_texts:
        return True

    return any(_is_near_duplicate(dedupe_tokens, seen_tokens) for seen_tokens in seen_token_sets)


def _is_near_duplicate(current_tokens: set[str], seen_tokens: set[str]) -> bool:
    if not current_tokens or not seen_tokens:
        return False

    overlap = len(current_tokens & seen_tokens)
    union_size = len(current_tokens | seen_tokens)
    smaller_size = min(len(current_tokens), len(seen_tokens))

    jaccard = overlap / union_size
    smaller_overlap = overlap / smaller_size
    token_count_difference = abs(len(current_tokens) - len(seen_tokens))
    return jaccard >= 0.8 or (smaller_overlap >= 0.9 and token_count_difference <= 2)


__all__ = ["extract_claims"]
