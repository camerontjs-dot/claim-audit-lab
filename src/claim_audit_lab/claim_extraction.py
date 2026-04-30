"""Conservative candidate-claim extraction."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator
from re import Pattern

from claim_audit_lab.models import Claim, ClaimType, DraftDocument

_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")
_MARKDOWN_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+")
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")

_CLAIM_TYPE_PATTERNS: tuple[tuple[ClaimType, tuple[Pattern[str], ...]], ...] = (
    (
        "prediction",
        (
            re.compile(r"\b(will|would|should|always|never|guarantees?|ensures?)\b"),
            re.compile(r"\b(future|predicts?|expected to|likely to)\b"),
        ),
    ),
    (
        "scope",
        (
            re.compile(r"\b(all|every|across|throughout|universal|any|entire|broad)\b"),
            re.compile(r"\b(multi step|enterprise|organization wide)\b"),
        ),
    ),
    (
        "causal",
        (
            re.compile(r"\b(causes?|caused|because|after|prevents?|reduced?|reduces?)\b"),
            re.compile(r"\b(leads? to|led to|fell from|eliminates?|resulted in|due to)\b"),
        ),
    ),
    (
        "comparative",
        (
            re.compile(r"\b(more|less|better|worse|stronger|weaker|higher|lower)\b"),
            re.compile(r"\b(faster|slower|compared with|compared to|than)\b"),
        ),
    ),
    (
        "credential",
        (
            re.compile(r"\b(certified|certification|degree|bachelor|master|phd|doctorate)\b"),
            re.compile(r"\b(licensed|licence|license|years? of experience|worked at)\b"),
            re.compile(r"\b(employer|published|publication|author|manager|director)\b"),
            re.compile(r"\b(technician|specialist|officer|role)\b"),
        ),
    ),
    (
        "capability",
        (
            re.compile(r"\b(can|could|supports?|detects?|allows?|enables?|handles?)\b"),
            re.compile(r"\b(is able to|are able to|capable of|generates?|extracts?)\b"),
        ),
    ),
    ("numeric", (re.compile(r"\b\d+(?:\.\d+)?%?\b"),)),
    (
        "interpretive",
        (
            re.compile(r"\b(clear|clearly|robust|credible|important|strong|weak)\b"),
            re.compile(r"\b(useful|effective|meaningful|material|significant)\b"),
        ),
    ),
)

_DEDUPE_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "was",
    "were",
    "with",
}


def extract_claims(document: DraftDocument) -> list[Claim]:
    """Extract conservative candidate claims from a draft document."""
    claims: list[Claim] = []
    seen_normalized_texts: set[str] = set()
    seen_token_sets: list[set[str]] = []

    for paragraph_index, paragraph in _iter_prose_paragraphs(document.content):
        for sentence_index, sentence in _iter_sentences(paragraph):
            claim_type = _classify_claim(sentence)
            if claim_type is None:
                continue

            normalized_text = _normalize_text(sentence)
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


def _classify_claim(sentence: str) -> ClaimType | None:
    if _should_skip_sentence(sentence):
        return None

    normalized_sentence = _normalize_text(sentence)
    for claim_type, patterns in _CLAIM_TYPE_PATTERNS:
        if any(pattern.search(normalized_sentence) for pattern in patterns):
            return claim_type
    return None


def _should_skip_sentence(sentence: str) -> bool:
    stripped = sentence.strip()
    if not stripped or stripped.endswith("?"):
        return True

    token_count = len(_TOKEN_RE.findall(stripped.lower()))
    return token_count < 4


def _claim_id(document_id: str, normalized_text: str) -> str:
    digest = hashlib.sha256(f"{document_id}:{normalized_text}".encode()).hexdigest()
    return f"claim-{digest[:12]}"


def _normalize_text(text: str) -> str:
    tokens = _TOKEN_RE.findall(text.lower())
    return " ".join(tokens)


def _dedupe_tokens(normalized_text: str) -> set[str]:
    return {
        _light_stem(token) for token in normalized_text.split() if token not in _DEDUPE_STOPWORDS
    }


def _light_stem(token: str) -> str:
    if token.endswith("ies") and len(token) > 4:
        return f"{token[:-3]}y"
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and len(token) > 3:
        return token[:-1]
    return token


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
