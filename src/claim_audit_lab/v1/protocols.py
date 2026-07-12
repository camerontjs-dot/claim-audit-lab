"""Swappable layer protocols for the CAL v1 pipeline.

Each protocol defines the interface a layer implementation must satisfy.
Implementations live in ``claim_audit_lab.v1.impl``. Swapping a layer for
benchmarking — for example, replacing the bi-encoder retriever with a
hybrid BM25+dense one — must not require touching any other layer.

See DECISIONS.md § 2026-06-21 § 1.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from claim_audit_lab.v1.models import (
    AuditConfig,
    EntailResult,
    ExtractedFeatures,
    Passage,
    RetrievalResult,
    RuleFired,
    SupportSignal,
    Verdict,
)


@runtime_checkable
class Retriever(Protocol):
    """Recall-only: admit candidate passages for a claim."""

    def retrieve(
        self,
        claim: str,
        passages: list[Passage],
        top_k: int,
    ) -> list[RetrievalResult]:
        """Return up to ``top_k`` passages ranked by relevance score.

        Does not decide support. Retrieval scores are recorded in the trace
        but are not the support signal.
        """
        ...


@runtime_checkable
class Entailer(Protocol):
    """NLI: score a single (claim, premise) pair."""

    def entail(self, claim: str, premise: str, passage_id: str) -> EntailResult:
        """Return the NLI label + score + raw logits for this pair.

        Implementations must be deterministic on a fixed model revision; the
        raw logits are recorded in the trace so a downstream consumer can
        re-derive label assignment under different thresholds.
        """
        ...


@runtime_checkable
class Aggregator(Protocol):
    """Combine per-passage entailment results into a claim-level signal."""

    def aggregate(self, entailment_results: list[EntailResult]) -> SupportSignal:
        """Return the aggregated support signal across candidate passages.

        v1 default: max-entailment over candidates. Other strategies
        (concatenated-premise, M×N) are documented in
        ``AggregationStrategy`` but deferred to v2.
        """
        ...


@runtime_checkable
class Rules(Protocol):
    """Deterministic verdict layer with the glass-box rationale."""

    def apply(
        self,
        *,
        claim: str,
        features: ExtractedFeatures,
        passages: list[Passage],
        retrieval: list[RetrievalResult],
        entailment: list[EntailResult],
        support_signal: SupportSignal,
        audit_config: AuditConfig,
    ) -> tuple[Verdict, list[RuleFired]]:
        """Return the final verdict and the trace of rules that fired.

        This is the only layer that produces a final verdict. It applies the
        canonical Decision C order (gates → degree → adjustments) over the
        aggregated NLI support signal, the extracted claim ``features``, and the
        retrieved ``passages`` — whose text the numeric, source-scope, and
        negation rules inspect. See ``plans/adr-v1-rule-order.md`` and
        DECISIONS.md § 2026-06-21 § 5.
        """
        ...


__all__ = ["Aggregator", "Entailer", "Retriever", "Rules"]
