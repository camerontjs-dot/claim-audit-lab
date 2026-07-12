"""Default composition of the v1 feature extractors.

``DefaultFeatureExtractor`` satisfies the ``FeatureExtractor`` protocol by
running every extractor in :mod:`claim_audit_lab.v1.features` over a claim and
packing the results into one ``ExtractedFeatures``. The extractors are pure
and deterministic (a pinned spaCy model on CPU), so repeated calls on the same
claim produce identical features — the property the audit trace relies on.
"""

from __future__ import annotations

from claim_audit_lab.v1 import features
from claim_audit_lab.v1.models import ExtractedFeatures


class DefaultFeatureExtractor:
    """Compose the linguistic extractors into one ``ExtractedFeatures``."""

    def extract(self, claim: str) -> ExtractedFeatures:
        return ExtractedFeatures(
            numerical_values=features.has_numerical_value(claim),
            has_explicit_negation=features.has_explicit_negation(claim),
            has_universal_quantifier=features.has_universal_quantifier(claim),
            modal_strength=features.has_modal_strength(claim),
            claim_token_count=features.claim_token_count(claim),
            compound_claim=features.is_compound_claim(claim),
            sentence_type=features.sentence_type(claim),
        )


__all__ = ["DefaultFeatureExtractor"]
