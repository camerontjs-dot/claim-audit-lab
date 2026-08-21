"""Explicit caller-declared claim structure for CAL v1.

This additive API does not decompose claim text.  A caller supplies stable,
provenance-bound atoms, CAL audits each atom through the existing atomic path,
and this module derives a parent verdict from the declared operator.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Final, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

from claim_audit_lab import __version__
from claim_audit_lab.contracts.serialization import hash_text
from claim_audit_lab.v1.config import hash_audit_config
from claim_audit_lab.v1.models import (
    AuditConfidence,
    AuditConfig,
    AuditFlag,
    AuditRequest,
    AuditTrace,
    CitationStatus,
    Passage,
    SupportVerdict,
    Verdict,
)

EXPLICIT_CLAIM_SCHEMA_VERSION: Final = "cal-explicit-claim-v1"
EXPLICIT_CLAIM_TRACE_SCHEMA_VERSION: Final = "cal-explicit-claim-trace-v1"

_SHA256_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
_FLAG_ORDER: tuple[AuditFlag, ...] = (
    "overstated",
    "inferred",
    "source_scope_error",
    "false_caution",
    "missed_counterevidence",
    "coverage_loss",
)
_CONFIDENCE_ORDER: dict[AuditConfidence, int] = {"low": 0, "medium": 1, "high": 2}
_CITATION_WORST_ORDER: tuple[CitationStatus, ...] = (
    "missing_needed",
    "wrong_source",
    "not_cited",
    "partial",
    "correct",
)


class _StrictExplicitClaimModel(BaseModel):
    """Strict, frozen base model for the explicit-claim public contract."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


def _normalized_nonblank(value: str, field_name: str) -> str:
    """Return boundary-whitespace-normalized ``value`` or raise an input error."""
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


class AtomProvenance(_StrictExplicitClaimModel):
    """Authority and immutable reference binding for one declared atom."""

    origin: Literal["operator_declared", "source_contract"]
    reference_id: str
    reference_sha256: str

    @field_validator("reference_id")
    @classmethod
    def normalize_reference_id(cls, value: str) -> str:
        """Normalize only boundary whitespace in a provenance reference ID."""
        return _normalized_nonblank(value, "reference_id")

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        """Reject blank references and non-canonical SHA-256 values."""
        _normalized_nonblank(self.reference_id, "reference_id")
        if not _SHA256_PATTERN.fullmatch(self.reference_sha256):
            raise ValueError("reference_sha256 must use lowercase sha256:<64 hex> form")
        return self


class ExplicitClaimAtom(_StrictExplicitClaimModel):
    """A stable atomic claim explicitly supplied by the caller."""

    atom_id: str
    claim_text: str
    provenance: AtomProvenance

    @field_validator("atom_id", "claim_text")
    @classmethod
    def normalize_atom_strings(cls, value: str, info: ValidationInfo) -> str:
        """Normalize boundary whitespace while preserving internal claim text."""
        return _normalized_nonblank(value, str(info.field_name))

    @model_validator(mode="after")
    def validate_atom(self) -> Self:
        """Reject blank identifiers and claim text."""
        _normalized_nonblank(self.atom_id, "atom_id")
        _normalized_nonblank(self.claim_text, "claim_text")
        return self


class ExplicitClaimRequest(_StrictExplicitClaimModel):
    """Versioned caller-declared atom structure plus shared audit inputs."""

    schema_version: Literal["cal-explicit-claim-v1"] = EXPLICIT_CLAIM_SCHEMA_VERSION
    parent_claim_id: str
    parent_claim_text: str
    operator: Literal["single", "all_of"]
    atoms: list[ExplicitClaimAtom] = Field(min_length=1)
    passages: list[Passage]
    audit_config: AuditConfig

    @field_validator("parent_claim_id", "parent_claim_text")
    @classmethod
    def normalize_parent_strings(cls, value: str, info: ValidationInfo) -> str:
        """Normalize parent boundary whitespace before hashing or atom comparison."""
        return _normalized_nonblank(value, str(info.field_name))

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        """Enforce the fail-closed structure and identity invariants from E2."""
        parent_id = _normalized_nonblank(self.parent_claim_id, "parent_claim_id")
        parent_text = _normalized_nonblank(self.parent_claim_text, "parent_claim_text")
        atom_ids = [atom.atom_id.strip() for atom in self.atoms]
        atom_texts = [atom.claim_text.strip() for atom in self.atoms]
        passage_ids = [passage.passage_id.strip() for passage in self.passages]

        if self.operator == "single" and len(self.atoms) != 1:
            raise ValueError("single requires exactly one atom")
        if self.operator == "all_of" and len(self.atoms) < 2:
            raise ValueError("all_of requires at least two atoms")
        if parent_id in atom_ids:
            raise ValueError("an atom_id cannot equal parent_claim_id")
        if len(atom_ids) != len(set(atom_ids)):
            raise ValueError("atom_ids must be unique")
        if len(atom_texts) != len(set(atom_texts)):
            raise ValueError("atom claim_text values must be unique")
        if any(not passage_id for passage_id in passage_ids):
            raise ValueError("passage_id values must be non-empty")
        if len(passage_ids) != len(set(passage_ids)):
            raise ValueError("passage_ids must be unique")
        if self.operator == "single" and parent_text != atom_texts[0]:
            raise ValueError("single requires exact parent/atom text identity after normalization")
        return self


class AtomAuditTrace(_StrictExplicitClaimModel):
    """One provenance-bound atomic trace in declared request order."""

    atom_id: str
    claim_text: str
    provenance: AtomProvenance
    audit_trace: AuditTrace

    @field_validator("atom_id", "claim_text")
    @classmethod
    def normalize_atomic_trace_strings(cls, value: str, info: ValidationInfo) -> str:
        """Normalize parsed trace bindings before comparing them to the atomic trace."""
        return _normalized_nonblank(value, str(info.field_name))

    @model_validator(mode="after")
    def validate_atomic_binding(self) -> Self:
        """Prevent an atomic receipt from describing a different claim."""
        _normalized_nonblank(self.atom_id, "atom_id")
        _normalized_nonblank(self.claim_text, "claim_text")
        if self.audit_trace.claim_id != self.atom_id:
            raise ValueError("atomic trace claim_id does not match atom_id")
        if self.audit_trace.claim_text != self.claim_text:
            raise ValueError("atomic trace claim_text does not match atom claim_text")
        return self


class ParentAggregationTrace(_StrictExplicitClaimModel):
    """Deterministic parent-decision receipt derived from ordered atom degrees."""

    operator: Literal["single", "all_of"]
    atom_support_verdicts: list[SupportVerdict] = Field(min_length=1)
    rule_id: str
    reason: str
    verdict: Verdict

    @model_validator(mode="after")
    def validate_aggregation_receipt(self) -> Self:
        """Reject an aggregation receipt without an explainable deterministic rule."""
        _normalized_nonblank(self.rule_id, "rule_id")
        _normalized_nonblank(self.reason, "reason")
        if self.operator == "single" and len(self.atom_support_verdicts) != 1:
            raise ValueError("single aggregation requires exactly one atomic degree")
        if self.operator == "all_of" and len(self.atom_support_verdicts) < 2:
            raise ValueError("all_of aggregation requires at least two atomic degrees")
        return self


class ExplicitClaimTrace(_StrictExplicitClaimModel):
    """Replayable output for a caller-declared explicit claim structure."""

    schema_version: Literal["cal-explicit-claim-trace-v1"] = EXPLICIT_CLAIM_TRACE_SCHEMA_VERSION
    request_sha256: str
    parent_claim_id: str
    parent_claim_text: str
    operator: Literal["single", "all_of"]
    atom_audits: list[AtomAuditTrace] = Field(min_length=1)
    parent_aggregation: ParentAggregationTrace
    verdict: Verdict
    audit_config_hash: str
    library_version: str

    @field_validator("parent_claim_id", "parent_claim_text", "library_version")
    @classmethod
    def normalize_trace_strings(cls, value: str, info: ValidationInfo) -> str:
        """Normalize trace boundary strings so parsed traces cannot retain drift."""
        return _normalized_nonblank(value, str(info.field_name))

    @model_validator(mode="after")
    def validate_trace_binding(self) -> Self:
        """Ensure the parent receipt cannot drift from its aggregation record."""
        if not _SHA256_PATTERN.fullmatch(self.request_sha256):
            raise ValueError("request_sha256 must use lowercase sha256:<64 hex> form")
        if not _SHA256_PATTERN.fullmatch(self.audit_config_hash):
            raise ValueError("audit_config_hash must use lowercase sha256:<64 hex> form")
        _normalized_nonblank(self.parent_claim_id, "parent_claim_id")
        _normalized_nonblank(self.parent_claim_text, "parent_claim_text")
        if self.verdict != self.parent_aggregation.verdict:
            raise ValueError("trace verdict must match parent_aggregation verdict")
        if self.operator != self.parent_aggregation.operator:
            raise ValueError("trace operator must match parent_aggregation operator")
        if len(self.atom_audits) != len(self.parent_aggregation.atom_support_verdicts):
            raise ValueError("atom audit count must match parent aggregation degrees")
        if any(
            audit.audit_trace.audit_config_hash != self.audit_config_hash
            for audit in self.atom_audits
        ):
            raise ValueError("atomic trace audit_config_hash must match parent trace")
        if self.parent_aggregation.atom_support_verdicts != [
            audit.audit_trace.verdict.support_verdict for audit in self.atom_audits
        ]:
            raise ValueError("parent aggregation degrees must match ordered atomic trace verdicts")
        if any(
            audit.audit_trace.library_version != self.library_version for audit in self.atom_audits
        ):
            raise ValueError("atomic trace library_version must match parent trace")

        atom_ids = [audit.atom_id for audit in self.atom_audits]
        atom_texts = [audit.claim_text for audit in self.atom_audits]
        if len(atom_ids) != len(set(atom_ids)):
            raise ValueError("atom_ids must be unique")
        if len(atom_texts) != len(set(atom_texts)):
            raise ValueError("atom claim_text values must be unique")
        if self.parent_claim_id in atom_ids:
            raise ValueError("an atom_id cannot equal parent_claim_id")
        if self.operator == "single" and len(self.atom_audits) != 1:
            raise ValueError("single requires exactly one atom")
        if self.operator == "all_of" and len(self.atom_audits) < 2:
            raise ValueError("all_of requires at least two atoms")
        if self.operator == "single" and self.parent_claim_text != atom_texts[0]:
            raise ValueError("single requires exact parent/atom text identity after normalization")

        expected_aggregation = aggregate_explicit_claim_verdicts(
            self.operator,
            [audit.audit_trace.verdict for audit in self.atom_audits],
        )
        if self.parent_aggregation != expected_aggregation:
            raise ValueError("parent aggregation does not match the ordered atomic verdicts")
        return self


def canonical_explicit_claim_request_json(request: ExplicitClaimRequest) -> str:
    """Serialize ``request`` canonically for stable content hashing."""
    return json.dumps(
        request.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def hash_explicit_claim_request(request: ExplicitClaimRequest) -> str:
    """Return the canonical ``sha256:`` request binding for ``request``."""
    return hash_text(canonical_explicit_claim_request_json(request))


def serialize_explicit_claim_trace(trace: ExplicitClaimTrace) -> str:
    """Serialize an explicit-claim trace in deterministic canonical JSON."""
    return json.dumps(
        trace.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _union_flags(verdicts: list[Verdict]) -> list[AuditFlag]:
    flags = {flag for verdict in verdicts for flag in verdict.audit_flags}
    return [flag for flag in _FLAG_ORDER if flag in flags]


def _least_confident(verdicts: list[Verdict]) -> AuditConfidence:
    return min(
        (verdict.audit_confidence for verdict in verdicts), key=_CONFIDENCE_ORDER.__getitem__
    )


def _worst_citation_status(verdicts: list[Verdict]) -> CitationStatus:
    statuses = [verdict.citation_status for verdict in verdicts]
    applicable = [status for status in statuses if status != "not_applicable"]
    if not applicable:
        return "not_applicable"
    return next(status for status in _CITATION_WORST_ORDER if status in applicable)


def aggregate_explicit_claim_verdicts(
    operator: Literal["single", "all_of"], verdicts: list[Verdict]
) -> ParentAggregationTrace:
    """Aggregate atomic verdicts with the fixed E2 parent table and axis rules."""
    if operator not in {"single", "all_of"}:
        raise ValueError(f"unsupported explicit-claim operator: {operator!r}")
    if operator == "single":
        if len(verdicts) != 1:
            raise ValueError("single aggregation requires exactly one atomic verdict")
        return ParentAggregationTrace(
            operator=operator,
            atom_support_verdicts=[verdicts[0].support_verdict],
            rule_id="ECA-SINGLE-COPY",
            reason="The declared single claim copies its one atomic verdict exactly.",
            verdict=verdicts[0],
        )
    if len(verdicts) < 2:
        raise ValueError("all_of aggregation requires at least two atomic verdicts")

    degrees = [verdict.support_verdict for verdict in verdicts]
    if "contradicted" in degrees:
        degree: SupportVerdict = "contradicted"
        rule_id = "ECA-ALLOF-CONTRADICTED"
        reason = "At least one declared conjunct is contradicted."
    elif all(degree == "supported" for degree in degrees):
        degree = "supported"
        rule_id = "ECA-ALLOF-SUPPORTED"
        reason = "Every declared conjunct is supported."
    elif "supported" in degrees or "partially_supported" in degrees:
        degree = "partially_supported"
        rule_id = "ECA-ALLOF-PARTIAL"
        reason = (
            "At least one declared conjunct has positive support, but complete support is absent."
        )
    elif "unsupported" in degrees:
        degree = "unsupported"
        rule_id = "ECA-ALLOF-UNSUPPORTED"
        reason = "No declared conjunct has positive support and at least one is unsupported."
    else:
        degree = "not_checkable"
        rule_id = "ECA-ALLOF-NOT-CHECKABLE"
        reason = "Every declared conjunct is not checkable."

    shared_reason = verdicts[0].support_verdict_reason
    parent_reason = (
        shared_reason
        if degree == "not_checkable"
        and shared_reason is not None
        and all(verdict.support_verdict_reason == shared_reason for verdict in verdicts)
        else None
    )
    parent_verdict = Verdict(
        support_verdict=degree,
        support_verdict_reason=parent_reason,
        audit_flags=_union_flags(verdicts),
        citation_status=_worst_citation_status(verdicts),
        audit_confidence=_least_confident(verdicts),
    )
    return ParentAggregationTrace(
        operator=operator,
        atom_support_verdicts=degrees,
        rule_id=rule_id,
        reason=reason,
        verdict=parent_verdict,
    )


def run_explicit_claim_audit(
    request: ExplicitClaimRequest,
    *,
    auditor: Callable[[AuditRequest], AuditTrace],
) -> ExplicitClaimTrace:
    """Audit each declared atom independently and derive its parent deterministically.

    ``auditor`` is injected so this import-light orchestration path can run with
    test stubs or the heavy default inference wrapper.  Any returned claim or
    config binding drift aborts the complete request rather than aggregating a
    partial result.
    """
    expected_config_hash = hash_audit_config(request.audit_config)
    atom_audits: list[AtomAuditTrace] = []
    atomic_verdicts: list[Verdict] = []
    for atom in request.atoms:
        atomic_request = AuditRequest(
            claim_id=atom.atom_id,
            claim_text=atom.claim_text,
            passages=request.passages,
            audit_config=request.audit_config,
        )
        atomic_trace = auditor(atomic_request)
        if atomic_trace.claim_id != atom.atom_id:
            raise ValueError(f"auditor claim_id drift for atom {atom.atom_id!r}")
        if atomic_trace.claim_text != atom.claim_text:
            raise ValueError(f"auditor claim_text drift for atom {atom.atom_id!r}")
        if atomic_trace.audit_config_hash != expected_config_hash:
            raise ValueError(f"auditor audit_config_hash drift for atom {atom.atom_id!r}")
        if atomic_trace.library_version != __version__:
            raise ValueError(f"auditor library_version drift for atom {atom.atom_id!r}")
        atom_audits.append(
            AtomAuditTrace(
                atom_id=atom.atom_id,
                claim_text=atom.claim_text,
                provenance=atom.provenance,
                audit_trace=atomic_trace,
            )
        )
        atomic_verdicts.append(atomic_trace.verdict)

    parent_aggregation = aggregate_explicit_claim_verdicts(request.operator, atomic_verdicts)
    return ExplicitClaimTrace(
        request_sha256=hash_explicit_claim_request(request),
        parent_claim_id=request.parent_claim_id,
        parent_claim_text=request.parent_claim_text,
        operator=request.operator,
        atom_audits=atom_audits,
        parent_aggregation=parent_aggregation,
        verdict=parent_aggregation.verdict,
        audit_config_hash=expected_config_hash,
        library_version=__version__,
    )


__all__ = [
    "AtomAuditTrace",
    "AtomProvenance",
    "EXPLICIT_CLAIM_SCHEMA_VERSION",
    "EXPLICIT_CLAIM_TRACE_SCHEMA_VERSION",
    "ExplicitClaimAtom",
    "ExplicitClaimRequest",
    "ExplicitClaimTrace",
    "ParentAggregationTrace",
    "aggregate_explicit_claim_verdicts",
    "canonical_explicit_claim_request_json",
    "hash_explicit_claim_request",
    "run_explicit_claim_audit",
    "serialize_explicit_claim_trace",
]
