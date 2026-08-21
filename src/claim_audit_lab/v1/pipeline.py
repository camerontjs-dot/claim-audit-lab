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
from claim_audit_lab.v1.features import FeatureExtractor, negate_claim, source_coverage_claim
from claim_audit_lab.v1.models import (
    AuditRequest,
    AuditTrace,
    EntailResult,
    NegationProbe,
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

    # A4 negation-consistency probe (adr-v1-slg09-negation-consistency.md,
    # cal-rules-v1.7.0): when the aggregated signal is a hard-contradiction
    # candidate, entail the structurally negated claim against the same
    # contributing premise and record the outcome. The rules layer applies the
    # confirmation deterministically from this record; an abstention (negator
    # declined) or an absent probe never demotes.
    negation_probe: NegationProbe | None = None
    if (
        support_signal.label == "contradict"
        and support_signal.max_entailment_score >= request.audit_config.contradicted_threshold
    ):
        negated = negate_claim(request.claim_text)
        contributing_id = support_signal.contributing_passage_id
        contributing = passages_by_id.get(contributing_id) if contributing_id else None
        if negated is None or contributing is None:
            negation_probe = NegationProbe(negated_claim=negated, abstained=True, result=None)
        else:
            negation_probe = NegationProbe(
                negated_claim=negated,
                abstained=False,
                result=entailer.entail(negated, contributing.text, contributing.passage_id),
            )

    absence_complement_entailed = False
    if (
        request.source_boundary == "exhaustive"
        and features.has_explicit_negation
        and source_coverage_claim(request.claim_text) is not None
    ):
        complement = negate_claim(request.claim_text)
        if complement is not None:
            for result in admitted:
                probed = entailer.entail(
                    complement,
                    passages_by_id[result.passage_id].text,
                    result.passage_id,
                )
                if (
                    probed.label == "entail"
                    and probed.score >= request.audit_config.supported_threshold
                ):
                    absence_complement_entailed = True
                    break

    verdict, rules_fired = rules.apply(
        claim=request.claim_text,
        features=features,
        passages=request.passages,
        retrieval=retrieval,
        entailment=entailment,
        support_signal=support_signal,
        audit_config=request.audit_config,
        negation_probe=negation_probe,
        source_boundary=request.source_boundary,
        claimed_material_is_a_named_gap=request.claimed_material_is_a_named_gap,
        absence_complement_entailed=absence_complement_entailed,
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
        negation_probe=negation_probe,
    )


__all__ = ["run_audit"]
