"""Claim Audit Lab v1 — retrieve→entail→aggregate+rules verifier.

v1 is the post-falsification redesign locked in DECISIONS.md § 2026-06-21.
This subpackage is purely additive while v0.2 remains the shipped surface;
v0.2 stays in place until v1 clears the calibration acceptance gate.

Top-level pieces:

- ``protocols`` defines the swappable layer interfaces
  (``Retriever`` / ``Entailer`` / ``Aggregator`` / ``Rules``).
- ``models`` defines the pydantic ``AuditRequest`` / ``AuditTrace`` contract
  and the supporting value types.
- ``features`` defines the deterministic claim-feature extractors that
  replace the v0.2 regex taxonomy.
- ``config`` loads the pinned default ``AuditConfig`` from package data.
- ``intake`` normalizes a loaded C-B bundle into ``AuditRequest`` objects at
  the apparatus boundary (Phase 3).
- ``impl`` carries the v1 implementations of each protocol; inference
  code is stubbed (``NotImplementedError``) during the skeleton phase.
"""

from claim_audit_lab.v1 import config, features, intake, models, protocols
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.intake import (
    AuditedBundleContents,
    AuditedBundleError,
    bundle_to_requests,
    load_audited,
)

__all__ = [
    "AuditedBundleContents",
    "AuditedBundleError",
    "bundle_to_requests",
    "config",
    "features",
    "intake",
    "load_default_audit_config",
    "load_audited",
    "models",
    "protocols",
]
