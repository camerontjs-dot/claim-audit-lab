"""Research-only semantic-operator applicability contract.

This module does not change CAL production semantics.  It distinguishes an
operator being *inapplicable* from an applicable operator returning an unknown
validity assessment.  Either state is non-deciding unless another applicable
operator supplies a receipt-bound validity assessment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from claim_audit_lab.v1.decision_model import Sha256Receipt, ValidityAssessment
from claim_audit_lab.v1.semantic_operators import (
    SemanticProbeReceipt,
    assess_negation_probe,
    project_negation,
)

Applicability = Literal["applicable", "inapplicable"]
Phenomenon = Literal[
    "direct_entailment",
    "direct_contradiction",
    "explicit_negation",
    "numeric_mismatch",
    "threshold_mismatch",
    "quantity_mismatch",
    "categorical_incompatibility",
    "scope_mismatch",
    "quantifier_mismatch",
    "degree_mismatch",
    "multi_passage_composition",
    "mixed_support_refutation",
    "out_of_scope",
    "no_applicable_operator",
]


@dataclass(frozen=True)
class OperatorApplication:
    applicability: Applicability
    operator: str
    projection_kind: str
    canonical_hypothesis: str | None
    reason: str
    validity: ValidityAssessment | None

    @property
    def may_supply_decision_authority(self) -> bool:
        return (
            self.applicability == "applicable"
            and self.validity is not None
            and self.validity.status in {"valid", "invalid"}
        )


def a4_application(
    *,
    claim: str,
    contribution_passage_ids: tuple[str, ...],
    receipt: SemanticProbeReceipt,
) -> OperatorApplication:
    """Apply A4 only when a canonical structural complement exists.

    The existing shared semantic operator returns ``unknown`` when it cannot
    construct a canonical complement.  For reconciliation we first expose that
    as operator *inapplicability*, so an abstained structural negator cannot be
    mistaken for a semantic measurement over a different phenomenon.
    """
    projection = project_negation(claim)
    if projection.complement is None:
        return OperatorApplication(
            applicability="inapplicable",
            operator="A4_negation_consistency",
            projection_kind=projection.kind,
            canonical_hypothesis=None,
            reason=projection.reason,
            validity=None,
        )
    assessment = assess_negation_probe(
        claim=claim,
        contribution_passage_ids=contribution_passage_ids,
        receipt=receipt,
    )
    return OperatorApplication(
        applicability="applicable",
        operator="A4_negation_consistency",
        projection_kind=projection.kind,
        canonical_hypothesis=projection.complement,
        reason=assessment.reason,
        validity=assessment,
    )


def unresolved_refutation_validity(
    *, evidence_path: str, receipt_sha256: Sha256Receipt, reason: str
) -> ValidityAssessment:
    """Represent a refutation with no applicable terminal semantic operator."""
    return ValidityAssessment(
        status="unknown",
        operator="no_applicable_refutation_operator",
        reason=reason,
        evidence_path=evidence_path,
        receipt_sha256=receipt_sha256,
    )


def operator_contract_matrix() -> tuple[dict[str, object], ...]:
    """Frozen research interpretation of current measured/operator surfaces."""
    return (
        {
            "phenomenon": "direct_entailment",
            "measurement_available": "direct NLI p_entail per admitted passage",
            "semantic_operator_applicable": "direct_claim_identity",
            "operator_authority": "terminal for support identity; no polarity transform",
            "unknown_behavior": "missing measurement/eligibility/aperture remains unknown",
            "may_decide": "yes, only when eligible, valid, aperture-satisfied, and above threshold",
        },
        {
            "phenomenon": "direct_contradiction",
            "measurement_available": "direct NLI p_contradict per admitted passage",
            "semantic_operator_applicable": "none generically; A4 only if canonical complement exists and exact probe is receipt-bound",
            "operator_authority": "NLI score is a measurement, not by itself a terminal semantic-validity receipt in the explicit machinery",
            "unknown_behavior": "no applicable terminal operator => semantic validity unknown",
            "may_decide": "no unless an applicable operator validates the refutation",
        },
        {
            "phenomenon": "explicit_negation",
            "measurement_available": "direct NLI plus structural/quantifier-aware complement probe when constructible",
            "semantic_operator_applicable": "A4 / quantifier-aware negation under its guarded grammar",
            "operator_authority": "terminal only for exact canonical complement, exact contribution passage set, and completed probe",
            "unknown_behavior": "ambiguous scope, abstention, or receipt mismatch remains unknown",
            "may_decide": "conditional",
        },
        {
            "phenomenon": "numeric_mismatch",
            "measurement_available": "direct NLI; production also extracts quantities",
            "semantic_operator_applicable": "A4 only if a canonical complement actually exists; otherwise a typed numeric relation operator is required",
            "operator_authority": "structural-negation abstention has no numeric authority",
            "unknown_behavior": "numeric relation not independently validated => unknown",
            "may_decide": "conditional; e2e-08 has no applicable A4 receipt",
        },
        {
            "phenomenon": "threshold_mismatch",
            "measurement_available": "direct NLI plus extracted inequality/bound language",
            "semantic_operator_applicable": "structural negation only when it yields an exact complement; otherwise interval/bound semantics are required",
            "operator_authority": "no inequality conclusion may be inferred from a generic abstained negator",
            "unknown_behavior": "unvalidated bound relation remains unknown",
            "may_decide": "conditional",
        },
        {
            "phenomenon": "quantity_mismatch",
            "measurement_available": "direct NLI plus extracted values/units",
            "semantic_operator_applicable": "requires comparable quantity semantics; structural negation is only auxiliary when canonical",
            "operator_authority": "unit/value comparability must be measured, not assumed",
            "unknown_behavior": "unmatched or incomparable quantity remains unknown",
            "may_decide": "conditional",
        },
        {
            "phenomenon": "categorical_incompatibility",
            "measurement_available": "direct NLI",
            "semantic_operator_applicable": "A4 can test a canonical not-P complement when constructible, but category exclusivity itself is not a generic built-in operator",
            "operator_authority": "only the exact receipt-bound complement probe has authority",
            "unknown_behavior": "unmodeled category exclusivity remains unknown",
            "may_decide": "conditional",
        },
        {
            "phenomenon": "scope_mismatch",
            "measurement_available": "direct NLI plus current narrow scope-mismatch detector where applicable",
            "semantic_operator_applicable": "semantic contradiction operator cannot override scope/eligibility mismatch",
            "operator_authority": "scope gate takes precedence over contribution decision authority",
            "unknown_behavior": "unresolved scope remains abstention",
            "may_decide": "no while scope mismatch/unresolved scope holds",
        },
        {
            "phenomenon": "quantifier_mismatch",
            "measurement_available": "direct NLI; limited guarded negative-existential projection exists",
            "semantic_operator_applicable": "quantifier-aware negation only inside pinned grammar; other quantifier relations unmeasured",
            "operator_authority": "no general quantifier theorem prover",
            "unknown_behavior": "unsupported/ambiguous quantifier scope remains unknown",
            "may_decide": "conditional inside guarded grammar only",
        },
        {
            "phenomenon": "degree_mismatch",
            "measurement_available": "direct NLI and legacy B5 degree mapping",
            "semantic_operator_applicable": "no generic typed degree operator observed in the explicit path",
            "operator_authority": "legacy reporting degree is not a semantic-validity receipt",
            "unknown_behavior": "weak/adverse measurement without validation remains unknown",
            "may_decide": "no adverse epistemic decision from B5 reporting category alone",
        },
        {
            "phenomenon": "multi_passage_composition",
            "measurement_available": "per-passage channel measurements; some research set operators exist",
            "semantic_operator_applicable": "only explicit set/composition operators with exact passage-set receipts",
            "operator_authority": "no scalar aggregation may be invented when method is absent",
            "unknown_behavior": "unmeasured composition or incomplete passage-set coverage remains unknown",
            "may_decide": "conditional",
        },
        {
            "phenomenon": "mixed_support_refutation",
            "measurement_available": "independent support and refutation channels",
            "semantic_operator_applicable": "operators assess contributions independently",
            "operator_authority": "no operator may erase the opposite valid channel by score ordering alone",
            "unknown_behavior": "mixed valid state remains mixed",
            "may_decide": "no under current explicit resolve policy",
        },
        {
            "phenomenon": "out_of_scope",
            "measurement_available": "measurements may still be observable",
            "semantic_operator_applicable": "scope/eligibility gate precedes decision authority",
            "operator_authority": "semantic measurements cannot override out-of-scope status",
            "unknown_behavior": "scope unknown remains abstention",
            "may_decide": "no",
        },
        {
            "phenomenon": "no_applicable_operator",
            "measurement_available": "possibly direct NLI measurement only",
            "semantic_operator_applicable": "none",
            "operator_authority": "none",
            "unknown_behavior": "semantic validity remains unknown; absence is not contradiction or invalidity",
            "may_decide": "no",
        },
    )
