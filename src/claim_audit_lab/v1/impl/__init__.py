"""Implementations of the CAL v1 protocols.

Each module exposes one v1 implementation of its corresponding protocol:

- :mod:`retriever` — bi-encoder retriever (sentence-transformers).
- :mod:`entailer` — DeBERTa-v3-base-mnli-fever-anli NLI cross-encoder.
- :mod:`aggregator` — max-entailment over candidates.
- :mod:`rules` — deterministic verdict layer with the glass-box rationale.

Inference code is stubbed (``NotImplementedError``) until the build phase
wires the pinned models. The aggregator is the one layer that has no
external dependency, so its v1 implementation is concrete from the
skeleton.
"""

from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer
from claim_audit_lab.v1.impl.retriever import BiEncoderRetriever
from claim_audit_lab.v1.impl.rules import VerdictRules

__all__ = [
    "BiEncoderRetriever",
    "DeBERTaEntailer",
    "MaxEntailmentAggregator",
    "VerdictRules",
]
