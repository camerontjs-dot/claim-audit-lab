"""Claim Audit Lab.

Three version strings identify different things, and they are not
interchangeable:

===========================  =========================  ========================
axis                          value                      identifies
===========================  =========================  ========================
distribution ``__version__``  ``0.5.0``                  the Python package
engine                        ``v1-retrieve-entail`` (ordinary
                              ``audit`` / ``demo`` path)
                              ``v0.2-lexical`` (selectable)
rules version                 ``cal-rules-v1.13.0``      the frozen decision
                                                         layer inside the v1
                                                         engine, SHA-pinned
===========================  =========================  ========================

The distribution version is **not** the engine name. Package ``0.2.0`` and
engine ``v0.2-lexical`` shared a number by accident, which read as though the
whole package were the retired lexical matcher; the bump broke that collision.
``0.3.0`` was declared but never released, and named several different trees
while the v1 work was in flight, so the first public tag was ``0.4.0`` — one
version string, one tree. ``0.5.0`` adds the public Contract C 1.0.0 exporter
without changing the frozen CAL semantic implementation or verdict policy
promoted by the Contract C evidence program.
Engine and rules version both travel in every v1 ``AuditTrace``
(``library_version`` and ``audit_config_hash``), so a trace always says which
code produced it.
"""

from claim_audit_lab.auditor import audit_claims, audit_document
from claim_audit_lab.classifiers import classify_claim_text

__version__ = "0.5.0"

__all__ = ["__version__", "audit_claims", "audit_document", "classify_claim_text"]
