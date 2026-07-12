"""Claim Audit Lab package."""

from claim_audit_lab.auditor import audit_claims, audit_document
from claim_audit_lab.classifiers import classify_claim_text

__version__ = "0.2.0"

__all__ = ["__version__", "audit_claims", "audit_document", "classify_claim_text"]
