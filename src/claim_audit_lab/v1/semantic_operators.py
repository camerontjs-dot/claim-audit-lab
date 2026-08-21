"""Guarded semantic operators for contribution-validity assessments.

Only the preregistered D5 negative-existential form is added here.  It is not a
general English quantifier parser: unsupported or ambiguous scope returns explicit
``unknown`` so the contribution-ledger candidate cannot decide from it.
"""

from __future__ import annotations

import re
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from claim_audit_lab.v1.decision_model import Sha256Receipt, ValidityAssessment
from claim_audit_lab.v1.features import negate_claim
from claim_audit_lab.v1.models import EntailLabel

NegationKind = Literal["negative_existential", "ordinary", "unknown"]

_NEGATIVE_EXISTENTIAL = re.compile(
    r"^No (?P<subject>[A-Za-z][A-Za-z -]*?) (?P<predicate>was|were) "
    r"(?P<remainder>[^.]+)\.?$"
)


class NegationProjection(BaseModel):
    """Canonical semantic target for a guarded contradiction probe."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    kind: NegationKind
    complement: str | None
    reason: str


class SemanticProbeReceipt(BaseModel):
    """Exact passage-set and hypothesis receipt used by a validity assessment."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    passage_ids: tuple[str, ...]
    hypothesis: str | None
    label: EntailLabel | None
    abstained: bool
    evidence_path: str = Field(min_length=1)
    receipt_sha256: Sha256Receipt

    @field_validator("passage_ids")
    @classmethod
    def _canonical_passage_set(cls, passage_ids: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(passage_id.strip() for passage_id in passage_ids)
        if not normalized or any(not passage_id for passage_id in normalized):
            raise ValueError("a semantic probe receipt requires passage provenance")
        if len(set(normalized)) != len(normalized):
            raise ValueError("semantic probe passage IDs may not be duplicated")
        return tuple(sorted(normalized))

    @model_validator(mode="after")
    def _validate_abstention_pairing(self) -> Self:
        if self.abstained and (self.hypothesis is not None or self.label is not None):
            raise ValueError("an abstained semantic probe may not carry a result")
        if not self.abstained and (self.hypothesis is None or self.label is None):
            raise ValueError("a completed semantic probe requires a hypothesis and label")
        return self


def project_negation(claim: str) -> NegationProjection:
    """Project the pinned D5 grammar, otherwise preserve safe ordinary behavior."""
    normalized_claim = claim.strip()
    match = _NEGATIVE_EXISTENTIAL.fullmatch(normalized_claim)
    if match:
        subject = match.group("subject")
        predicate = match.group("predicate")
        remainder = match.group("remainder")
        if predicate != "was":
            return NegationProjection(
                kind="unknown",
                complement=None,
                reason="plural agreement is outside the pinned No X was P grammar",
            )
        if subject.lower() == "one":
            return NegationProjection(
                kind="unknown",
                complement=None,
                reason="No one has different quantifier scope from the pinned grammar",
            )
        if subject.lower().startswith(("more than ", "less than ")):
            return NegationProjection(
                kind="unknown",
                complement=None,
                reason="bounded no-more/no-less quantifier is outside this operator",
            )
        if re.search(r"\b(?:and|or)\b", subject + " " + remainder, flags=re.IGNORECASE):
            return NegationProjection(
                kind="unknown",
                complement=None,
                reason="compound negative-existential scope is outside this operator",
            )
        if re.search(r"\b(?:not|never)\b", remainder, flags=re.IGNORECASE):
            return NegationProjection(
                kind="unknown",
                complement=None,
                reason="negative-existential predicate already contains negation",
            )
        return NegationProjection(
            kind="negative_existential",
            complement=f"At least one {subject} was {remainder}.",
            reason="the complement of no X P is an existential-positive proposition",
        )

    if normalized_claim.lower().startswith(("no ", "none ")):
        return NegationProjection(
            kind="unknown",
            complement=None,
            reason="negative-quantifier shape is outside the pinned No X was P grammar",
        )
    ordinary = negate_claim(claim)
    if ordinary is not None:
        return NegationProjection(
            kind="ordinary",
            complement=ordinary,
            reason="the existing structural negator supplied the ordinary complement",
        )
    return NegationProjection(
        kind="unknown",
        complement=None,
        reason="claim is outside the guarded semantic-operator grammar",
    )


def assess_negation_probe(
    *,
    claim: str,
    contribution_passage_ids: tuple[str, ...],
    receipt: SemanticProbeReceipt,
) -> ValidityAssessment:
    """Assess an exact, hash-bound probe without inferring validity from score."""
    projection = project_negation(claim)
    expected_passages = tuple(sorted(contribution_passage_ids))
    if receipt.passage_ids != expected_passages:
        return ValidityAssessment(
            status="unknown",
            operator="quantifier_aware_negation",
            reason="semantic probe passage provenance does not match the contribution",
            evidence_path=receipt.evidence_path,
            receipt_sha256=receipt.receipt_sha256,
        )
    if projection.complement is None:
        return ValidityAssessment(
            status="unknown",
            operator="quantifier_aware_negation",
            reason=projection.reason + "; no canonical probe can be matched",
            evidence_path=receipt.evidence_path,
            receipt_sha256=receipt.receipt_sha256,
        )
    if receipt.abstained or receipt.hypothesis != projection.complement or receipt.label is None:
        return ValidityAssessment(
            status="unknown",
            operator="quantifier_aware_negation",
            reason=projection.reason + "; no matching semantic probe receipt",
            evidence_path=receipt.evidence_path,
            receipt_sha256=receipt.receipt_sha256,
        )
    if receipt.label == "entail":
        return ValidityAssessment(
            status="valid",
            operator="quantifier_aware_negation",
            reason="the passage entails the exact canonical complement",
            evidence_path=receipt.evidence_path,
            receipt_sha256=receipt.receipt_sha256,
        )
    return ValidityAssessment(
        status="invalid",
        operator="quantifier_aware_negation",
        reason="the passage does not entail the exact canonical complement",
        evidence_path=receipt.evidence_path,
        receipt_sha256=receipt.receipt_sha256,
    )


__all__ = [
    "NegationKind",
    "NegationProjection",
    "SemanticProbeReceipt",
    "assess_negation_probe",
    "project_negation",
]
