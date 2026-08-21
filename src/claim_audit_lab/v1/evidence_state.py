"""Additive two-channel evidence-state projection and shadow decision table.

This module is measurement-only.  It reads the per-passage probabilities already
recorded in an :class:`AuditTrace`; it does not alter aggregation, rules, or the
production verdict.  The shadow table is deliberately operator-blind in Stages
1-2: numeric, negation, eligibility, and compound semantics remain production-rule
concerns and are reported as diffs rather than repaired here.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from claim_audit_lab.v1.models import AuditTrace, EntailResult

EvidenceState = Literal[
    "unmeasured",
    "no_evidence",
    "read_silent",
    "support_only",
    "refutation_only",
    "mixed",
]


class _StrictModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class ChannelCandidate(_StrictModel):
    """One passage's measured score on one evidence channel."""

    passage_id: str
    score: float = Field(ge=0.0, le=1.0)


class EvidenceStateProjection(_StrictModel):
    """Two-channel measurement projected from one immutable audit trace."""

    state: EvidenceState
    signal_floor: float = Field(ge=0.0, le=1.0)
    admitted_passage_ids: tuple[str, ...]
    support_candidates: tuple[ChannelCandidate, ...]
    refutation_candidates: tuple[ChannelCandidate, ...]


def _softmax(logits: tuple[float, float, float]) -> tuple[float, float, float]:
    highest = max(logits)
    exponentials = tuple(math.exp(value - highest) for value in logits)
    total = sum(exponentials)
    return (
        exponentials[0] / total,
        exponentials[1] / total,
        exponentials[2] / total,
    )


def with_derived_channel_probabilities(traces: list[AuditTrace]) -> tuple[AuditTrace, ...]:
    """Return legacy traces with channel probabilities derived from recorded logits.

    Modern traces already record both probabilities and are returned unchanged.
    For a legacy batch, the argmax label votes recover the model's native logit
    slots without importing or running the model.  The input traces remain frozen.
    """
    results = [result for trace in traces for result in trace.entailment]
    if all(result.p_entail is not None and result.p_contradict is not None for result in results):
        return tuple(traces)

    votes: dict[str, Counter[int]] = defaultdict(Counter)
    for result in results:
        argmax = max(range(3), key=lambda index: result.raw_logits[index])
        votes[result.label][argmax] += 1
    slots: dict[str, int] = {}
    for label in ("entail", "contradict"):
        if not votes[label]:
            raise ValueError(f"cannot recover {label} logit slot: batch has no {label} argmax")
        slot, count = votes[label].most_common(1)[0]
        if count != sum(votes[label].values()):
            raise ValueError(f"inconsistent {label} argmax slot in legacy trace batch")
        slots[label] = slot

    enriched: list[AuditTrace] = []
    for trace in traces:
        entailment: list[EntailResult] = []
        for result in trace.entailment:
            probabilities = _softmax(result.raw_logits)
            entailment.append(
                result.model_copy(
                    update={
                        "p_entail": probabilities[slots["entail"]],
                        "p_contradict": probabilities[slots["contradict"]],
                    }
                )
            )
        enriched.append(trace.model_copy(update={"entailment": entailment}))
    return tuple(enriched)


def _candidates(
    results: list[EntailResult], *, channel: Literal["support", "refutation"], floor: float
) -> tuple[ChannelCandidate, ...]:
    field = "p_entail" if channel == "support" else "p_contradict"
    measured = [
        ChannelCandidate(passage_id=result.passage_id, score=score)
        for result in results
        if (score := getattr(result, field)) is not None and score >= floor
    ]
    return tuple(sorted(measured, key=lambda candidate: (-candidate.score, candidate.passage_id)))


def project_evidence_state(
    trace: AuditTrace, *, signal_floor: float = 0.20
) -> EvidenceStateProjection:
    """Project B1/B2a/B2b/B3/B4 as one production-independent state."""
    admitted = tuple(result.passage_id for result in trace.entailment)
    measured = all(
        result.p_entail is not None and result.p_contradict is not None
        for result in trace.entailment
    )
    support = _candidates(trace.entailment, channel="support", floor=signal_floor)
    refutation = _candidates(trace.entailment, channel="refutation", floor=signal_floor)

    if not admitted:
        state: EvidenceState = "no_evidence"
    elif not measured:
        state = "unmeasured"
    elif support and refutation:
        state = "mixed"
    elif support:
        state = "support_only"
    elif refutation:
        state = "refutation_only"
    else:
        state = "read_silent"
    return EvidenceStateProjection(
        state=state,
        signal_floor=signal_floor,
        admitted_passage_ids=admitted,
        support_candidates=support,
        refutation_candidates=refutation,
    )


__all__ = [
    "ChannelCandidate",
    "EvidenceState",
    "EvidenceStateProjection",
    "project_evidence_state",
    "with_derived_channel_probabilities",
]
