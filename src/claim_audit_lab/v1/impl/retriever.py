"""Bi-encoder retriever implementation for CAL v1.

Real ``sentence-transformers/all-MiniLM-L6-v2`` inference, pinned to the HF
revision SHA in ``AuditConfig.retriever.hf_revision_sha``. CPU only, deterministic
(see :mod:`claim_audit_lab.v1.impl._determinism`). The claim and every candidate
passage are embedded once per call; the retrieval score is the cosine similarity
between the claim embedding and each passage embedding (embeddings are
L2-normalized, so cosine is a plain dot product). The top ``top_k`` passages by
score become candidates for the entailer.

Like the Phase-1 stub, this layer does **not** apply ``retrieval_floor`` — the
protocol's ``retrieve`` signature carries only ``top_k``, and floor filtering is
the rules-layer ``A2`` gate's job (DECISIONS.md § 2026-06-21 § 5). Retrieval
scores are recorded in the trace but are not the support signal.

The model is loaded once per process (module-level cache keyed by model id +
revision) so repeated audits do not reload weights. See DECISIONS.md
§ 2026-06-21 § 1 and § 9, and ``plans/phases/phase-2-inference-layers.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import cast

from sentence_transformers import SentenceTransformer

from claim_audit_lab.v1.impl._determinism import enforce_cpu_determinism
from claim_audit_lab.v1.models import ModelRevision, Passage, RetrievalResult

enforce_cpu_determinism()


@cache
def _load_model(model_id: str, revision_sha: str) -> SentenceTransformer:
    """Load (and cache) the pinned ``SentenceTransformer`` on CPU."""
    return cast(
        SentenceTransformer,
        SentenceTransformer(model_id, revision=revision_sha, device="cpu"),
    )


@dataclass(frozen=True)
class BiEncoderRetriever:
    """Bi-encoder retriever pinned to a specific HF model revision."""

    revision: ModelRevision

    def retrieve(
        self,
        claim: str,
        passages: list[Passage],
        top_k: int,
    ) -> list[RetrievalResult]:
        """Return up to ``top_k`` passages ranked by claim-passage cosine.

        Embeds the claim and all passages in a single normalized batch, scores
        each passage by cosine similarity to the claim, and returns the top
        ``top_k`` by descending score. The sort is stable, so equal scores keep
        input order — deterministic by construction on a fixed model revision.
        """
        if not self.revision.hf_revision_sha.strip():
            raise ValueError(
                "BiEncoderRetriever requires a pinned hf_revision_sha; refusing to "
                "load an unpinned model revision (trace reproducibility depends on it)."
            )
        if not passages:
            return []

        model = _load_model(self.revision.model_id, self.revision.hf_revision_sha)
        embeddings = model.encode(
            [claim, *(passage.text for passage in passages)],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        claim_embedding = embeddings[0]
        scored = [
            RetrievalResult(
                passage_id=passage.passage_id,
                score=float(embeddings[index + 1] @ claim_embedding),
            )
            for index, passage in enumerate(passages)
        ]
        ranked = sorted(scored, key=lambda result: result.score, reverse=True)
        return ranked[:top_k]


__all__ = ["BiEncoderRetriever"]
