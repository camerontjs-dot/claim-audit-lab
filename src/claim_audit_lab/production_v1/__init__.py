"""Production-intent CAL V1 execution surface."""

from __future__ import annotations

from claim_audit_lab.production_v1.semantic.models import SemanticFamily

DISTRIBUTION_VERSION = "0.6.0"
PROFILE = "cal-v1-integration-candidate-v1"
# Exact polarity-successor semantic implementation. The scientific implementation
# was frozen at this commit before the later findings/identity-binding commits.
SEMANTIC_IMPLEMENTATION_SHA = "caa0048f8f511ec3c4aa1ce713766f2219a04bc1"
QUALIFIED_RC1_PARENT_SHA = "a902621e8baea3063dddd7f92ba975aade305464"
CONTRACT_B_VERSION = "1.2.0"
PACKET_SCHEMA_RESOURCE = "production_v1/schema/packet.schema.json"
TARGET_SCHEMA_RESOURCE = "production_v1/schema/target.schema.json"
RESULT_SCHEMA_RESOURCE = "production_v1/schema/result-v2.schema.json"
MANIFEST_SCHEMA_RESOURCE = "production_v1/schema/manifest-v2.schema.json"
SUPPORTED_SEMANTIC_FAMILIES = (
    SemanticFamily.STRICT_COMPARISON.value,
    SemanticFamily.DIRECT_EVENT_ORDER.value,
)

__all__ = [
    "CONTRACT_B_VERSION",
    "DISTRIBUTION_VERSION",
    "MANIFEST_SCHEMA_RESOURCE",
    "PACKET_SCHEMA_RESOURCE",
    "PROFILE",
    "QUALIFIED_RC1_PARENT_SHA",
    "RESULT_SCHEMA_RESOURCE",
    "SEMANTIC_IMPLEMENTATION_SHA",
    "SUPPORTED_SEMANTIC_FAMILIES",
    "TARGET_SCHEMA_RESOURCE",
]
