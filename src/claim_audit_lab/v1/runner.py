"""Construct and run the default real v1 pipeline.

This module wires the pinned production layers — `DefaultFeatureExtractor`,
`BiEncoderRetriever`, `DeBERTaEntailer`, `MaxEntailmentAggregator`, `VerdictRules`
— into :func:`claim_audit_lab.v1.pipeline.run_audit`, reading the model revisions
and rules-file SHA off the request's own ``audit_config``.

It is deliberately separate from ``pipeline.py`` so the orchestrator stays
import-light (protocols only): importing this module pulls in ``torch`` and
``transformers`` via the impl layers, so callers (the CLI) import it lazily on
the v1 branch only — the v0.2 path never pays that cost. The layer constructors
cache model weights at process level (`functools.cache` keyed by model id +
revision), so repeated `run_default_audit` calls in one process load each model
once.
"""

from __future__ import annotations

from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer
from claim_audit_lab.v1.impl.features import DefaultFeatureExtractor
from claim_audit_lab.v1.impl.retriever import BiEncoderRetriever
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import AuditRequest, AuditTrace
from claim_audit_lab.v1.pipeline import run_audit


def run_default_audit(request: AuditRequest) -> AuditTrace:
    """Run ``request`` through the pinned default v1 pipeline and return the trace.

    The model revisions (`retriever`, `entailer`) and `rules_file_sha` come from
    ``request.audit_config`` — typically the pinned
    :func:`claim_audit_lab.v1.config.load_default_audit_config`. Deterministic given
    that config, so the trace is byte-reproducible across runs.
    """
    config = request.audit_config
    return run_audit(
        request,
        feature_extractor=DefaultFeatureExtractor(),
        retriever=BiEncoderRetriever(revision=config.retriever),
        entailer=DeBERTaEntailer(revision=config.entailer),
        aggregator=MaxEntailmentAggregator(),
        rules=VerdictRules(rules_file_sha=config.rules_file_sha),
    )


__all__ = ["run_default_audit"]
