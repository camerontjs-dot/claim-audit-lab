"""Maintained research-backed CAL V1 candidate.

This package is intentionally separate from the released v0.5 ``claim_audit_lab.v1``
retrieve→entail→rules implementation during convergence.
"""

from .engine import AuditResult, PassageTrace, audit, compose
from .models import (
    AdmittedPassage,
    AuditContext,
    CategoricalRelation,
    Conclusion,
    EvidenceWorld,
    FailureCode,
    SemanticFamily,
    TypedProposition,
)
from .projection import CONTRACT_C_RESEARCH_SENTINEL, project_contract_c_successor
from .report import PROFILE, render_markdown

__all__ = [
    "AdmittedPassage",
    "AuditContext",
    "AuditResult",
    "CategoricalRelation",
    "Conclusion",
    "CONTRACT_C_RESEARCH_SENTINEL",
    "EvidenceWorld",
    "FailureCode",
    "PROFILE",
    "PassageTrace",
    "SemanticFamily",
    "TypedProposition",
    "audit",
    "compose",
    "project_contract_c_successor",
    "render_markdown",
]
