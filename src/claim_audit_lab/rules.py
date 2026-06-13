"""Rule checks for overclaiming, missing support, and audit readiness."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date as Date

from claim_audit_lab.models import (
    AuditConfig,
    Claim,
    ClaimAssessment,
    EvidenceBundle,
    EvidenceCandidate,
    EvidenceExcerpt,
    EvidenceSource,
    RiskLabel,
    RuleFlag,
    SupportLabel,
)
from claim_audit_lab.scoring import (
    DIRECT_DATE_SCORE,
    DIRECT_NUMERIC_SCORE,
    DIRECT_TERM_COVERAGE,
    DIRECT_TEXT_SCORE,
)
from claim_audit_lab.text import (
    dates,
    normalize_text,
    normalize_vocabulary,
    number_sort_key,
    numbers,
    term_set,
)

_DIRECT_SUPPORT_TRIGGER_WORDS = normalize_vocabulary(
    {
        "all",
        "always",
        "any",
        "can",
        "clearly",
        "eliminate",
        "eliminates",
        "entire",
        "every",
        "guarantee",
        "guarantees",
        "never",
        "will",
    },
    drop_stopwords=False,
)

_ADVERSE_LIMITATION_PATTERNS = (
    re.compile(r"\bnot tested\b"),
    re.compile(r"\bknown limitation\b"),
    re.compile(r"\bmiss(?:es|ed|ing)?\b"),
    re.compile(r"\bincomplete\b"),
    re.compile(r"\bambiguous\b"),
)

_COMPARISON_TERMS = normalize_vocabulary(
    {
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
)

_PUBLIC_LINK_TERMS = normalize_vocabulary(
    {
        "available",
        "github",
        "link",
        "linkedin",
        "portfolio",
        "public",
        "published",
        "repo",
        "repository",
        "url",
        "website",
    }
)

_DATE_SOURCE_TERMS = normalize_vocabulary({"deadline", "due", "expires", "since", "until"})

_OVERCONFIDENT_PATTERNS = (
    (re.compile(r"\bclearly\s+eliminates?\b"), "clearly eliminates"),
    (re.compile(r"\balways\b"), "always"),
    (re.compile(r"\bnever\b"), "never"),
    (re.compile(r"\bguarantees?\b"), "guarantees"),
    (re.compile(r"\beliminates?\b"), "eliminates"),
)

_FUTURE_CERTAINTY_PATTERNS = (
    (re.compile(r"\bwill\s+always\b"), "will always"),
    (re.compile(r"\bwill\s+never\b"), "will never"),
    (re.compile(r"\bwill\s+guarantee\b"), "will guarantee"),
    (re.compile(r"\bguarantees?\b"), "guarantees"),
)

_SCOPE_PATTERNS = (
    (re.compile(r"\bacross\s+every\b"), "across every"),
    (re.compile(r"\bacross\s+all\b"), "across all"),
    (re.compile(r"\bevery\b"), "every"),
    (re.compile(r"\ball\b"), "all"),
    (re.compile(r"\bany\b"), "any"),
    (re.compile(r"\bmulti\s+step\b"), "multi step"),
    (re.compile(r"\bworkflow(?:s)?\b"), "workflows"),
)


@dataclass(frozen=True)
class _EvidenceContext:
    candidate: EvidenceCandidate
    source: EvidenceSource | None
    excerpt: EvidenceExcerpt | None


def assess_claim_support(
    claim: Claim,
    evidence_bundle: EvidenceBundle,
    candidate_evidence: list[EvidenceCandidate],
    config: AuditConfig | None = None,
) -> ClaimAssessment:
    """Assess one claim against supplied evidence candidates and deterministic rules."""
    active_config = config or AuditConfig()
    if claim.claim_type == "unclassified":
        return ClaimAssessment(
            claim=claim,
            support_label="not_checkable",
            risk_label="low",
            candidate_evidence=candidate_evidence,
            explanation="The claim does not match a governed semantic claim type.",
            limitations=["No deterministic rule family applies to this claim."],
        )
    if not evidence_bundle.sources:
        return ClaimAssessment(
            claim=claim,
            support_label="needs_source",
            risk_label="medium",
            candidate_evidence=candidate_evidence,
            explanation="No evidence sources were supplied, so the claim still needs a source.",
            limitations=["No supplied evidence was available for rule assessment."],
        )

    contexts = _build_contexts(candidate_evidence, evidence_bundle)
    direct_contexts = [context for context in contexts if _is_direct_support(claim, context)]
    flags = _build_rule_flags(claim, contexts, direct_contexts, evidence_bundle, active_config)
    support_label = _support_label(claim, contexts, direct_contexts, flags)
    risk_label = _risk_label(support_label, flags)

    return ClaimAssessment(
        claim=claim,
        support_label=support_label,
        risk_label=risk_label,
        candidate_evidence=candidate_evidence,
        rule_flags=flags,
        explanation=_explanation(support_label, flags, bool(direct_contexts)),
        limitations=_limitations(flags),
    )


def _build_contexts(
    candidates: list[EvidenceCandidate],
    evidence_bundle: EvidenceBundle,
) -> list[_EvidenceContext]:
    sources_by_id = {source.id: source for source in evidence_bundle.sources}
    excerpts_by_key = {
        (source.id, excerpt.id): excerpt
        for source in evidence_bundle.sources
        for excerpt in source.excerpts
    }

    return [
        _EvidenceContext(
            candidate=candidate,
            source=sources_by_id.get(candidate.source_id),
            excerpt=excerpts_by_key.get((candidate.source_id, candidate.excerpt_id)),
        )
        for candidate in candidates
    ]


def _build_rule_flags(
    claim: Claim,
    contexts: list[_EvidenceContext],
    direct_contexts: list[_EvidenceContext],
    evidence_bundle: EvidenceBundle,
    config: AuditConfig,
) -> list[RuleFlag]:
    flags: list[RuleFlag] = []
    claim_numbers = numbers(claim.text)
    if claim_numbers and not _has_numeric_direct_support(claim, contexts):
        flags.append(
            _flag(
                claim,
                "numeric_mismatch",
                ",".join(sorted(claim_numbers, key=number_sort_key)),
                "The claim's numeric value was not found in the supplied evidence.",
                "high",
            )
        )

    if _is_causal_overreach(claim, direct_contexts):
        flags.append(
            _flag(
                claim,
                "causal_overreach",
                _first_causal_trigger(claim.text),
                "The evidence supports a change, but not the causal strength of the wording.",
                "medium",
            )
        )

    if _is_comparison_missing(claim, contexts):
        flags.append(
            _flag(
                claim,
                "comparison_missing",
                "comparative",
                "The comparative claim needs comparison evidence.",
                "medium",
            )
        )

    if claim.claim_type == "credential" and not direct_contexts:
        flags.append(
            _flag(
                claim,
                "credential_missing_source",
                "credential",
                "The credential claim needs a supporting source.",
                "medium",
            )
        )

    if _is_public_link_claim(claim) and not _has_candidate_url(contexts):
        flags.append(
            _flag(
                claim,
                "public_link_missing_source",
                "public_link",
                "The public-link claim needs supplied source URL metadata.",
                "medium",
            )
        )

    for trigger in _matching_triggers(claim.text, _OVERCONFIDENT_PATTERNS):
        if _overconfidence_needs_flag(claim, contexts, direct_contexts):
            flags.append(
                _flag(
                    claim,
                    "overconfident_wording",
                    trigger,
                    "The claim wording is stronger than the supplied evidence supports.",
                    "high",
                )
            )
            break

    if direct_contexts and all(
        context.candidate.source_reliability in {"low", "unknown"} for context in direct_contexts
    ):
        flags.append(
            _flag(
                claim,
                "low_reliability_only",
                ",".join(sorted(context.candidate.source_id for context in direct_contexts)),
                "The only direct support comes from low or unknown reliability sources.",
                "medium",
            )
        )

    stale_contexts = _stale_contexts(direct_contexts, config)
    if direct_contexts and stale_contexts and len(stale_contexts) == len(direct_contexts):
        flags.append(
            _flag(
                claim,
                "stale_source",
                ",".join(
                    sorted(
                        f"{context.candidate.source_id}:{context.candidate.source_date}"
                        for context in stale_contexts
                    )
                ),
                "The only direct support is older than the configured freshness window.",
                "medium",
            )
        )

    if _has_date_or_deadline_claim(claim) and not _has_date_direct_support(claim, contexts):
        flags.append(
            _flag(
                claim,
                "date_missing_support",
                "date",
                "The date or deadline claim needs matching supplied evidence.",
                "medium",
            )
        )

    for trigger in _matching_triggers(claim.text, _FUTURE_CERTAINTY_PATTERNS):
        flags.append(
            _flag(
                claim,
                "future_certainty",
                trigger,
                "The future-facing certainty claim needs a narrower caveat.",
                "high",
            )
        )
        break

    scope_trigger = _scope_trigger(claim)
    if scope_trigger and _scope_needs_flag(claim, contexts, direct_contexts, evidence_bundle):
        flags.append(
            _flag(
                claim,
                "scope_overreach",
                scope_trigger,
                "The claim generalizes beyond the supplied evidence.",
                "high",
            )
        )

    return sorted(flags, key=lambda flag: (flag.code, flag.id))


def _support_label(
    claim: Claim,
    contexts: list[_EvidenceContext],
    direct_contexts: list[_EvidenceContext],
    flags: list[RuleFlag],
) -> SupportLabel:
    codes = {flag.code for flag in flags}
    if "credential_missing_source" in codes or "public_link_missing_source" in codes:
        return "needs_source"
    if "date_missing_support" in codes:
        return "needs_source"
    if "comparison_missing" in codes and not contexts:
        return "needs_source"
    if "numeric_mismatch" in codes:
        return "unsupported"
    if {"future_certainty", "overconfident_wording", "scope_overreach"} & codes:
        return "overstated"
    if direct_contexts and codes:
        return "partially_supported"
    if direct_contexts:
        return "supported"
    if contexts:
        return "partially_supported" if claim.claim_type == "comparative" else "unsupported"
    return "unsupported"


def _risk_label(support_label: SupportLabel, flags: list[RuleFlag]) -> RiskLabel:
    if any(flag.risk == "high" for flag in flags):
        return "high"
    if flags or support_label in {"partially_supported", "unsupported", "needs_source"}:
        return "medium"
    return "low"


def _is_direct_support(claim: Claim, context: _EvidenceContext) -> bool:
    if context.excerpt is None:
        return False
    if numbers(claim.text):
        return _numeric_direct_support(claim, context)
    if _has_date_or_deadline_claim(claim):
        return _date_direct_support(claim, context)
    return _text_direct_support(claim, context)


def _has_numeric_direct_support(claim: Claim, contexts: list[_EvidenceContext]) -> bool:
    return any(_numeric_direct_support(claim, context) for context in contexts)


def _numeric_direct_support(claim: Claim, context: _EvidenceContext) -> bool:
    if context.excerpt is None or context.candidate.score < DIRECT_NUMERIC_SCORE:
        return False
    claim_numbers = numbers(claim.text)
    if not claim_numbers:
        return False
    excerpt_numbers = numbers(_evidence_text(context))
    return claim_numbers <= excerpt_numbers


def _has_date_direct_support(claim: Claim, contexts: list[_EvidenceContext]) -> bool:
    return any(_date_direct_support(claim, context) for context in contexts)


def _date_direct_support(claim: Claim, context: _EvidenceContext) -> bool:
    if context.excerpt is None or context.candidate.score < DIRECT_DATE_SCORE:
        return False
    claim_dates = dates(claim.text)
    if not claim_dates:
        return False
    return claim_dates <= dates(_evidence_text(context))


def _text_direct_support(claim: Claim, context: _EvidenceContext) -> bool:
    if context.excerpt is None or context.candidate.score < DIRECT_TEXT_SCORE:
        return False
    if _has_adverse_limitation(_evidence_text(context)):
        return False
    return _core_term_coverage(claim.text, _evidence_text(context)) >= DIRECT_TERM_COVERAGE


def _is_causal_overreach(claim: Claim, direct_contexts: list[_EvidenceContext]) -> bool:
    if claim.claim_type != "causal" or not direct_contexts:
        return False
    return not any(
        _has_strong_causal_evidence(_evidence_text(context)) for context in direct_contexts
    )


def _has_strong_causal_evidence(text: str) -> bool:
    normalized = normalize_text(text)
    return any(
        phrase in normalized
        for phrase in (
            "because of",
            "caused by",
            "causal",
            "randomized",
            "controlled trial",
            "attributable to",
        )
    )


def _first_causal_trigger(text: str) -> str:
    normalized = normalize_text(text)
    for trigger in ("because", "after", "prevents", "reduced", "fell from", "due to"):
        if trigger in normalized:
            return trigger
    return "causal"


def _is_comparison_missing(claim: Claim, contexts: list[_EvidenceContext]) -> bool:
    if claim.claim_type != "comparative":
        return False
    return not any(_has_comparison_evidence(context) for context in contexts)


def _has_comparison_evidence(context: _EvidenceContext) -> bool:
    return bool(term_set(_evidence_text(context)) & _COMPARISON_TERMS)


def _is_public_link_claim(claim: Claim) -> bool:
    claim_terms = term_set(claim.text)
    return bool(claim_terms & _PUBLIC_LINK_TERMS)


def _has_candidate_url(contexts: list[_EvidenceContext]) -> bool:
    return any(
        context.candidate.source_url or (context.source and context.source.url)
        for context in contexts
    )


def _overconfidence_needs_flag(
    claim: Claim,
    contexts: list[_EvidenceContext],
    direct_contexts: list[_EvidenceContext],
) -> bool:
    return True


def _stale_contexts(
    direct_contexts: list[_EvidenceContext],
    config: AuditConfig,
) -> list[_EvidenceContext]:
    if config.reference_date is None:
        return []
    return [
        context
        for context in direct_contexts
        if context.candidate.source_date is not None
        and _age_days(context.candidate.source_date, config.reference_date) > config.freshness_days
    ]


def _age_days(source_date: Date, reference_date: Date) -> int:
    return (reference_date - source_date).days


def _has_date_or_deadline_claim(claim: Claim) -> bool:
    claim_terms = term_set(claim.text)
    return bool(dates(claim.text)) or bool(claim_terms & _DATE_SOURCE_TERMS)


def _scope_trigger(claim: Claim) -> str | None:
    if claim.claim_type != "scope":
        return None
    return next(iter(_matching_triggers(claim.text, _SCOPE_PATTERNS)), "scope")


def _scope_needs_flag(
    claim: Claim,
    contexts: list[_EvidenceContext],
    direct_contexts: list[_EvidenceContext],
    evidence_bundle: EvidenceBundle,
) -> bool:
    if not evidence_bundle.sources:
        return False
    if not contexts or not direct_contexts:
        return True
    return any(_has_adverse_limitation(_evidence_text(context)) for context in contexts)


def _flag(
    claim: Claim,
    code: str,
    trigger_context: str,
    message: str,
    risk: RiskLabel,
) -> RuleFlag:
    normalized_trigger = normalize_text(trigger_context)
    digest = hashlib.sha256(f"{claim.id}:{code}:{normalized_trigger}".encode()).hexdigest()
    return RuleFlag(
        id=f"flag-{digest[:12]}",
        claim_id=claim.id,
        code=code,
        message=message,
        risk=risk,
    )


def _matching_triggers(
    text: str,
    patterns: tuple[tuple[re.Pattern[str], str], ...],
) -> tuple[str, ...]:
    normalized = normalize_text(text)
    return tuple(trigger for pattern, trigger in patterns if pattern.search(normalized))


def _evidence_text(context: _EvidenceContext) -> str:
    if context.excerpt is None:
        return ""
    notes = context.excerpt.notes or ""
    return f"{context.excerpt.text} {notes}".strip()


def _has_adverse_limitation(text: str) -> bool:
    normalized = normalize_text(text)
    return any(pattern.search(normalized) for pattern in _ADVERSE_LIMITATION_PATTERNS)


def _core_term_coverage(claim_text: str, evidence_text: str) -> float:
    claim_terms = _core_terms(claim_text)
    if not claim_terms:
        return 0.0
    evidence_terms = term_set(evidence_text)
    return len(claim_terms & evidence_terms) / len(claim_terms)


def _core_terms(text: str) -> set[str]:
    return term_set(text) - _DIRECT_SUPPORT_TRIGGER_WORDS


def _explanation(
    support_label: SupportLabel,
    flags: list[RuleFlag],
    has_direct_support: bool,
) -> str:
    if support_label == "supported":
        return "The supplied evidence directly supports the claim."
    if support_label == "needs_source":
        return "The claim needs supplied source evidence before it can be assessed."
    if support_label == "unsupported":
        return "The supplied evidence does not support the claim as written."
    if support_label == "overstated":
        return "The claim is stronger than the supplied evidence can support."
    if has_direct_support:
        return "The supplied evidence supports part of the claim, but rule checks found limits."
    if flags:
        return "Rule checks found limits in the supplied evidence for this claim."
    return "Candidate evidence was related, but not strong enough for direct support."


def _limitations(flags: list[RuleFlag]) -> list[str]:
    if not flags:
        return []
    return ["Deterministic rule checks use supplied evidence only."]


__all__ = ["assess_claim_support"]
