"""Test-only stub layers for end-to-end CAL v1 pipeline tests.

Placed under ``tests`` (not ``src``) per DECISIONS.md § Phase 1 Unit 3: the
doubles are test-only and never ship in the wheel. Promotion to an importable
``src/claim_audit_lab/v1/testing`` is deferred until a real library consumer
(apparatus host / DecisionEngine) needs it.
"""

from .stubs import EntailSpec, StubEntailer, StubRetriever

__all__ = ["EntailSpec", "StubEntailer", "StubRetriever"]
