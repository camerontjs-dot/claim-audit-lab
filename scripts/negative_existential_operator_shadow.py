#!/usr/bin/env python3
"""DEV-only shadow contract for quantifier-aware negation validity.

This module does not alter production parsing or verdicts.  It tests the smallest
explicit semantic contract needed by D5: the complement of ``No X was P`` is an
existential-positive proposition, not a second surface negation.  Shapes outside
that deliberately narrow grammar remain unknown and therefore non-deciding.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict

from claim_audit_lab.v1.features import negate_claim
from scripts.evidence_state_operator_shadow import OperatorJudgment

NegationKind = Literal["negative_existential", "ordinary", "unknown"]

_NEGATIVE_EXISTENTIAL = re.compile(
    r"^No (?P<subject>[A-Za-z][A-Za-z -]*?) (?P<predicate>was|were) "
    r"(?P<remainder>[^.]+)\.?$"
)


class NegationProjection(BaseModel):
    """Auditable semantic target; unknown targets may not decide."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    kind: NegationKind
    complement: str | None
    reason: str


def project_negation(claim: str) -> NegationProjection:
    """Project only two explicit, fixture-gated logical forms.

    This is intentionally not a general English negator.  In particular, a
    negative existential already containing clause-level ``not`` is rejected
    instead of manufacturing the D5 double-negation failure.
    """
    match = _NEGATIVE_EXISTENTIAL.fullmatch(claim.strip())
    if match:
        if match.group("subject").lower().startswith(("more than ", "less than ")):
            return NegationProjection(
                kind="unknown",
                complement=None,
                reason="bounded no-more/no-less quantifier is outside this operator",
            )
        remainder = match.group("remainder")
        if re.search(r"\bnot\b", remainder, flags=re.IGNORECASE):
            return NegationProjection(
                kind="unknown",
                complement=None,
                reason="negative-existential predicate already contains negation",
            )
        subject = match.group("subject")
        predicate = match.group("predicate")
        return NegationProjection(
            kind="negative_existential",
            complement=f"At least one {subject} {predicate} {remainder}.",
            reason="not(no X P) projects to an existential-positive proposition",
        )

    ordinary = negate_claim(claim)
    if ordinary is not None:
        return NegationProjection(
            kind="ordinary",
            complement=ordinary,
            reason="existing production structural negator supplied the ordinary complement",
        )

    return NegationProjection(
        kind="unknown",
        complement=None,
        reason="claim is outside the preregistered shadow grammar",
    )


def judgment_from_probe(
    *,
    claim_id: str,
    passage_id: str,
    claim: str,
    probed_hypothesis: str | None,
    probe_label: Literal["entail", "contradict", "neutral"] | None,
) -> OperatorJudgment:
    """Convert a deterministic probe receipt into a channel-validity judgment."""
    projection = project_negation(claim)
    if projection.complement is None or probed_hypothesis != projection.complement:
        return OperatorJudgment(
            claim_id=claim_id,
            channel="refutation",
            passage_ids=(passage_id,),
            status="unknown",
            operator="quantifier_aware_negation",
            reason=projection.reason + "; no matching semantic probe receipt",
            evidence_path="DEV negative-existential fixture",
        )
    return OperatorJudgment(
        claim_id=claim_id,
        channel="refutation",
        passage_ids=(passage_id,),
        status="valid" if probe_label == "entail" else "invalid",
        operator="quantifier_aware_negation",
        reason=(
            "passage entails the canonical complement"
            if probe_label == "entail"
            else "passage does not entail the canonical complement"
        ),
        evidence_path="DEV negative-existential fixture",
    )
