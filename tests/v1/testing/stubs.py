"""Deterministic stub layers for exercising the CAL v1 pipeline in tests.

``StubRetriever`` and ``StubEntailer`` satisfy the ``Retriever`` / ``Entailer``
protocols with canned, fixture-parameterized responses, so the deterministic
core (features -> rules) can be driven end-to-end without loading the real ML
models. They are **test-only** — never imported by production code (DECISIONS.md
§ Phase 1 Unit 3). Phase 2 swaps in ``BiEncoderRetriever`` / ``DeBERTaEntailer``
through the same injection points in :func:`claim_audit_lab.v1.pipeline.run_audit`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from claim_audit_lab.v1.models import EntailLabel, EntailResult, Passage, RetrievalResult

# A canned NLI response: (label, score, raw_logits).
EntailSpec = tuple[EntailLabel, float, tuple[float, float, float]]

_NEUTRAL: EntailSpec = ("neutral", 0.0, (0.0, 0.0, 0.0))


@dataclass(frozen=True)
class StubRetriever:
    """Return canned retrieval scores; rank by score and take ``top_k``.

    Scores come from the ``scores`` mapping (``passage_id -> score``); a passage
    absent from the mapping scores ``0.0``. No retrieval-floor filtering happens
    here — that is the rules-layer ``A2`` gate's job — so a fixture drives the
    no-evidence path simply by setting every score below the floor. The sort is
    stable, so equal scores keep input order: deterministic by construction.
    """

    scores: Mapping[str, float] = field(default_factory=dict)

    def retrieve(self, claim: str, passages: list[Passage], top_k: int) -> list[RetrievalResult]:
        ranked = sorted(passages, key=lambda p: self.scores.get(p.passage_id, 0.0), reverse=True)
        return [
            RetrievalResult(passage_id=p.passage_id, score=self.scores.get(p.passage_id, 0.0))
            for p in ranked[:top_k]
        ]


@dataclass(frozen=True)
class StubEntailer:
    """Return canned NLI results keyed by ``passage_id``.

    ``responses`` maps ``passage_id -> (label, score, raw_logits)``; a passage
    not listed falls back to ``default`` (neutral, ``0.0``). Deterministic by
    construction — the same fixture yields the same entailment on every run.
    """

    responses: Mapping[str, EntailSpec] = field(default_factory=dict)
    default: EntailSpec = _NEUTRAL

    def entail(self, claim: str, premise: str, passage_id: str) -> EntailResult:
        label, score, logits = self.responses.get(passage_id, self.default)
        return EntailResult(passage_id=passage_id, label=label, score=score, raw_logits=logits)


__all__ = ["EntailSpec", "StubEntailer", "StubRetriever"]
