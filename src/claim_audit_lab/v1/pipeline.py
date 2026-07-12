"""End-to-end CAL v1 audit orchestrator (dependency-injected).

:func:`run_audit` wires the deterministic layers — feature extraction,
retrieval, entailment, aggregation, and the verdict rules — into a single call
that produces a replayable :class:`~claim_audit_lab.v1.models.AuditTrace`.

The orchestrator is layer-agnostic: it depends only on the protocols
(``FeatureExtractor`` / ``Retriever`` / ``Entailer`` / ``Aggregator`` /
``Rules``), so the *same* function drives the Phase-1 stub layers
(``StubRetriever`` / ``StubEntailer`` under ``tests/v1/testing``) and the
Phase-2 real models (``BiEncoderRetriever`` / ``DeBERTaEntailer``) without
changing. Determinism is a property of the injected layers; given deterministic
layers, ``run_audit`` is byte-reproducible — the property the trace fixtures
assert. The ``audit_config_hash`` is computed by
:func:`claim_audit_lab.v1.config.hash_audit_config`; ``library_version`` records
the installed package version. See DECISIONS.md § 2026-06-21 § 3 and § 9 and
§ Phase 1 Unit 3.
"""

from __future__ import annotations

from claim_audit_lab import __version__
from claim_audit_lab.v1.config import hash_audit_config
from claim_audit_lab.v1.features import FeatureExtractor
from claim_audit_lab.v1.models import (
    AuditRequest,
    AuditTrace,
    EntailResult,
    RetrievalResult,
)
from claim_audit_lab.v1.protocols import Aggregator, Entailer, Retriever, Rules


def run_audit(
    request: AuditRequest,
    *,
    feature_extractor: FeatureExtractor,
    retriever: Retriever,
    entailer: Entailer,
    aggregator: Aggregator,
    rules: Rules,
) -> AuditTrace:
    """Run the full deterministic audit pipeline and return the trace.

    The layers are injected so the assembly is identical for stub and real
    implementations. Each retrieved passage **at or above the retrieval floor**
    is entailed in retrieval order (Decision F4: NLI is miscalibrated on
    off-topic premises, so a passage retrieval already rejected must not be
    able to produce the winning support signal); the full floor-unfiltered
    retrieval ranking is still recorded in the trace, and the A2 gate still
    reads it. The aggregator condenses the per-passage results into the support
    signal the rules layer reads. Nothing here decides a verdict — that is
    solely the ``rules`` layer.
    """
    features = feature_extractor.extract(request.claim_text)

    retrieval: list[RetrievalResult] = retriever.retrieve(
        request.claim_text, request.passages, request.audit_config.top_k
    )
    admitted = [
        result for result in retrieval if result.score >= request.audit_config.retrieval_floor
    ]

    passages_by_id = {passage.passage_id: passage for passage in request.passages}
    entailment: list[EntailResult] = [
        entailer.entail(
            request.claim_text,
            passages_by_id[result.passage_id].text,
            result.passage_id,
        )
        for result in admitted
    ]

    support_signal = aggregator.aggregate(entailment)

    verdict, rules_fired = rules.apply(
        claim=request.claim_text,
        features=features,
        passages=request.passages,
        retrieval=retrieval,
        entailment=entailment,
        support_signal=support_signal,
        audit_config=request.audit_config,
    )

    return AuditTrace(
        claim_id=request.claim_id,
        claim_text=request.claim_text,
        retrieval=retrieval,
        entailment=entailment,
        features=features,
        support_signal=support_signal,
        rules_fired=rules_fired,
        verdict=verdict,
        audit_config_hash=hash_audit_config(request.audit_config),
        library_version=__version__,
    )


__all__ = ["run_audit"]
