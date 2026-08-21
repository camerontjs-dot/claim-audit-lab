"""Verdict explanation and abstention classification for CAL v1.

Additive and derived. This module reads what the pipeline already recorded and
says what it means. It never re-decides: every field is a reading of
``trace.verdict``, ``trace.support_signal``, ``trace.rules_fired`` and the pinned
``AuditConfig``. No rule, threshold, or verdict changes here, and nothing in this
module is on the verdict path.

Why it exists in core rather than in a presentation layer: an explanation that a
consumer derives for itself is a second decision procedure, and a second decision
procedure disagrees with the first. That failure was observed on 2026-08-18 — a UI
helper recomputed a decision from raw probabilities and announced
``DIRECT_CONTRADICTION`` on claims the rules layer had deliberately stood down.
The audited explanation must ship with the audited verdict.

## The abstention classification

``not_checkable`` is CAL's most common output — 64.3% of claims on scaled-30 — and
the 2026-08-05 decomposition established it is not one state. Evidence was admitted
and read in **128 of 135** abstentions (94.8%); only 7 were genuinely unevidenced.
The classes below are that finding, plus its 2026-08-05 amendment, made first-class.

| class | admitted | support signal | refutation signal | scaled-30 n |
| --- | --- | --- | --- | --- |
| ``out_of_scope``           | any | any | any | eligibility-decided |
| ``no_evidence_admitted``   | no  | --  | --  | 7 |
| ``read_silent``            | yes | low | low | 112 |
| ``refutation_stood_down``  | yes | low | elevated | 9 |
| ``ambiguous_support``      | yes | elevated | low | 7 |
| ``conflicting_signal``     | yes | elevated | elevated | 0 |

Two results drive the split. ``ambiguous_support`` is 5.2% of abstentions and holds
**50% of the authored-supported misses** — roughly 26x enriched — so it is the
population worth routing. ``refutation_stood_down`` is the cell the original method
missed entirely: 9 of the 121 claims filed as "confidently silent" carried a
refutation signal, 5 of them ``A4_negation_consistency`` demotions the rules layer
saw and stood down on. Calling those silent was false.

**On ``signal_floor``.** The boundary between "low" and "elevated" is a reporting
convention, not a discovered threshold. The source analysis is explicit: at
alpha = 0.20 the boundary fell in an empty stretch (B2 max 0.170, B3 min 0.208) and
"a 0.04-wide gap at this n is luck, not structure, and should not be cited as a
natural threshold." Class *membership* moves with alpha; the enrichment does not.
So the raw scores always travel with the class, the floor is an explicit parameter,
and no rule reads either.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Iterable
from typing import Final, Literal, NamedTuple

from pydantic import BaseModel, ConfigDict, Field

from claim_audit_lab.v1.explicit_claims import ExplicitClaimTrace
from claim_audit_lab.v1.models import (
    AuditConfig,
    AuditTrace,
    SourceBoundary,
    SupportVerdict,
)

EXPLANATION_SCHEMA_VERSION: Final[Literal["cal-explanation-v1"]] = "cal-explanation-v1"

AbstentionClass = Literal[
    "out_of_scope",
    "no_evidence_admitted",
    "read_silent",
    "refutation_stood_down",
    "ambiguous_support",
    "conflicting_signal",
]

CertaintyBand = Literal["low", "medium", "high"]

#: Reporting convention only — see the module docstring. Not a rule input.
DEFAULT_SIGNAL_FLOOR = 0.20

_ABSTENTION_MEANING: dict[str, str] = {
    "out_of_scope": (
        "The admitted evidence is not about this claim's subject, so it cannot bear on it."
    ),
    "no_evidence_admitted": (
        "No passage cleared the retrieval floor. Nothing was read, so nothing could be established."
    ),
    "read_silent": (
        "Evidence was admitted and read, and it is silent in both directions — "
        "it neither supports nor refutes the claim."
    ),
    "refutation_stood_down": (
        "Evidence was admitted and carries a refutation signal, but the rules layer "
        "declined to act on it. The abstention is a deliberate stand-down, not silence."
    ),
    "ambiguous_support": (
        "Evidence was admitted and carries real support signal that sat below the "
        "supported threshold. Historically this is the small, heavily enriched bucket "
        "where true support most often hides."
    ),
    "conflicting_signal": (
        "Evidence was admitted carrying both support and refutation signal above the "
        "reporting floor. The record disagrees with itself."
    ),
}

_NEXT_STEP: dict[str, str] = {
    "out_of_scope": (
        "These passages appear to govern a different site or subject than the claim. "
        "Which one is the claim about?"
    ),
    "no_evidence_admitted": "Supply a source that mentions the claim's terms, or widen retrieval.",
    "read_silent": (
        "No single admitted passage entails this claim. Read the admitted passages "
        "as a set before concluding the record is silent or seeking a different source."
    ),
    "refutation_stood_down": (
        "Read the refuting passage yourself — the stand-down may be correct or may be a miss."
    ),
    "ambiguous_support": (
        "Read the highest-support passage. This is the bucket most likely to be a false abstention."
    ),
    "conflicting_signal": (
        "These passages appear to govern different sites or subjects. Which one is the claim about?"
    ),
}


def _next_step_for(abstention: AbstentionClass | None, trace: AuditTrace) -> str | None:
    """Reviewer next step. Ask, do not invent a decision.

    Family-specific questions outrank the class default: scope mismatch, numeric
    mismatch, and two-hop silence each need a different question. A generic
    "find another source" is the last resort, not the first.
    """
    rule_ids = {item.rule_id for item in trace.rules_fired}
    if "A7_scope_mismatch" in rule_ids or "A5_conflicting_evidence" in rule_ids:
        return (
            "These passages appear to govern different sites or subjects. "
            "Which one is the claim about?"
        )
    if "C6a_numeric" in rule_ids:
        return (
            "The wording was entailed, but a recorded quantity did not match. "
            "Confirm which number the claim is using."
        )
    if abstention is None:
        return None
    if abstention == "read_silent":
        if trace.features.numerical_values:
            return (
                "The claim contains a quantity. CAL cannot instantiate numeric bounds; "
                "confirm the recorded threshold against the claimed value."
            )
        if len(trace.entailment) >= 2:
            return (
                "No single admitted passage entails this claim. The bundle may still "
                "settle it as a set; read the admitted passages together before seeking "
                "a different source."
            )
        return _NEXT_STEP["read_silent"]
    return _NEXT_STEP[abstention]


_VERDICT_HEADLINE: dict[str, str] = {
    "supported": "The supplied evidence establishes this claim.",
    "partially_supported": "The supplied evidence establishes part of this claim.",
    "unsupported": "Evidence was read and it leans against this claim.",
    "contradicted": "The supplied evidence refutes this claim.",
    "not_checkable": "Support was not established either way.",
}


class _Strict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Certainty(_Strict):
    """How firm the verdict is, and the measurements behind that word.

    ``band`` is the pipeline's own ``audit_confidence``, carried through
    unchanged. The remaining fields exist because a three-value band cannot
    express how close a call was: ``margin_to_threshold`` is the distance from
    the deciding signal to the bar it had to clear, so a verdict decided at
    0.6035 against a 0.70 bar is legible as the near-miss it is.
    """

    band: CertaintyBand
    best_support: float | None = None
    best_refutation: float | None = None
    deciding_threshold: float | None = None
    margin_to_threshold: float | None = Field(
        default=None,
        description="Deciding signal minus the threshold it was measured against. "
        "Negative means the signal fell short. None when nothing was measured.",
    )
    near_call: bool = Field(
        default=False,
        description="True when |margin| <= 0.10. A reporting flag, never a rule input.",
    )


class Explanation(_Strict):
    """A verdict-consistent account of one audited claim."""

    schema_version: Literal["cal-explanation-v1"] = EXPLANATION_SCHEMA_VERSION
    claim_id: str
    verdict: SupportVerdict
    headline: str
    detail: str
    abstention_class: AbstentionClass | None = None
    certainty: Certainty
    audit_flags: list[str] = Field(default_factory=list)
    rule_provenance: list[str] = Field(default_factory=list)
    next_step: str | None = None
    atom_breakdown: list[str] = Field(default_factory=list)
    source_boundary: SourceBoundary | None = None
    boundary_note: str | None = None


def _softmax(logits: tuple[float, float, float]) -> tuple[float, float, float]:
    m = max(logits)
    e = [math.exp(x - m) for x in logits]
    t = sum(e)
    return (e[0] / t, e[1] / t, e[2] / t)


class LogitSlots(NamedTuple):
    """Which raw-logit index carries entailment and which carries contradiction."""

    entail: int
    contradict: int


def recover_logit_slots(traces: Iterable[AuditTrace]) -> LogitSlots | None:
    """Recover the logit slot mapping by voting across a corpus of traces.

    A single abstaining trace usually labels every passage ``neutral``, which
    leaves two candidate slots and no way to tell entail from contradict. The
    mapping is therefore a property of the *corpus*, recovered the way
    ``outputs/2026-08-05-abstention-decomposition/METHOD.md`` froze it: each
    passage votes its argmax slot for its recorded label, and the majority wins.

    Returns ``None`` when the corpus cannot settle it — never a guess.
    """
    votes: dict[str, Counter[int]] = defaultdict(Counter)
    for trace in traces:
        for result in trace.entailment:
            probs = _softmax(result.raw_logits)
            votes[result.label][max(range(3), key=probs.__getitem__)] += 1

    if "entail" not in votes or "contradict" not in votes:
        return None
    i_e = votes["entail"].most_common(1)[0][0]
    i_c = votes["contradict"].most_common(1)[0][0]
    if i_e == i_c:
        return None
    return LogitSlots(entail=i_e, contradict=i_c)


def _signals_from_logits(
    trace: AuditTrace,
    slots: LogitSlots | None = None,
) -> tuple[float | None, float | None]:
    """Recover support/refutation probabilities from a pre-instrumentation trace.

    Traces written before the 2026-08-05 support-signal instrumentation carry
    ``raw_logits`` but no ``p_entail`` / ``best_entail``. Every sealed corpus is
    in that shape, so refusing to read them would make the classification
    unusable exactly where the research was done.

    The slot mapping is *recovered* from each trace's own recorded labels — the
    argmax slot of a passage labelled ``entail`` is the entail slot — never
    assumed. This mirrors the method frozen in
    ``outputs/2026-08-05-abstention-decomposition/METHOD.md``. Returns
    ``(None, None)`` when the mapping cannot be recovered, so an unreadable
    trace stays unreadable rather than being guessed at.
    """
    if not trace.entailment:
        # B1: nothing was admitted, so there is no measurement to recover.
        return (None, None)
    if slots is None:
        slots = recover_logit_slots([trace])
    if slots is None:
        return (None, None)
    i_e, i_c = slots.entail, slots.contradict

    best_e = max(_softmax(r.raw_logits)[i_e] for r in trace.entailment)
    best_c = max(_softmax(r.raw_logits)[i_c] for r in trace.entailment)
    return (best_e, best_c)


def _recorded_signals(
    trace: AuditTrace,
    slots: LogitSlots | None = None,
) -> tuple[float | None, float | None]:
    """Best support/refutation probability, from whichever field recorded it."""
    support = trace.support_signal.best_entail
    refute = trace.support_signal.best_contradict
    if support is not None or refute is not None:
        return (support, refute)

    measured = [r.p_entail for r in trace.entailment if r.p_entail is not None]
    if measured:
        return (
            max(measured),
            max(
                (r.p_contradict for r in trace.entailment if r.p_contradict is not None),
                default=None,
            ),
        )
    return _signals_from_logits(trace, slots)


def classify_abstention(
    trace: AuditTrace,
    signal_floor: float = DEFAULT_SIGNAL_FLOOR,
    logit_slots: LogitSlots | None = None,
) -> AbstentionClass | None:
    """Name which abstention state produced a ``not_checkable`` verdict.

    Returns ``None`` for any other verdict. Reads only recorded signals; the
    ``signal_floor`` is a reporting convention (see module docstring).
    """
    if trace.verdict.support_verdict != "not_checkable":
        return None

    # The eligibility layer's own answer outranks signal geometry: if the
    # evidence was ruled off-subject, that is why, whatever the scores say.
    if trace.verdict.support_verdict_reason == "out_of_scope":
        return "out_of_scope"

    # cal-rules-v1.9.0: A5 already decided this was a two-sided disagreement, at
    # the configured verdict thresholds. Re-deriving it from the reporting floor
    # could disagree with the rule that actually produced the verdict, so the
    # recorded reason wins.
    if trace.verdict.support_verdict_reason == "conflicting_evidence":
        return "conflicting_signal"

    if not trace.entailment:
        return "no_evidence_admitted"

    support, refute = _recorded_signals(trace, logit_slots)
    if support is None and refute is None:
        # Nothing measurable was recorded and the logit slots could not be
        # recovered. Fall back to the coarsest true statement rather than
        # inventing a cell.
        return "read_silent"

    support_high = (support or 0.0) >= signal_floor
    refute_high = (refute or 0.0) >= signal_floor

    if support_high and refute_high:
        return "conflicting_signal"
    if support_high:
        return "ambiguous_support"
    if refute_high:
        return "refutation_stood_down"
    return "read_silent"


def _certainty(
    trace: AuditTrace,
    config: AuditConfig | None,
    slots: LogitSlots | None = None,
) -> Certainty:
    verdict = trace.verdict.support_verdict
    support, refute = _recorded_signals(trace, slots)

    deciding: float | None = None
    threshold: float | None = None
    if config is not None:
        if verdict == "contradicted":
            deciding, threshold = refute, config.contradicted_threshold
        else:
            deciding, threshold = support, config.supported_threshold

    margin = None if (deciding is None or threshold is None) else deciding - threshold
    return Certainty(
        band=trace.verdict.audit_confidence,
        best_support=support,
        best_refutation=refute,
        deciding_threshold=threshold,
        margin_to_threshold=margin,
        near_call=margin is not None and abs(margin) <= 0.10,
    )


# Abstentions whose correctness depends on how completely the bundle covers its
# source. An absence is only informative when the bundle *is* the source.
_BOUNDARY_SENSITIVE = frozenset({"read_silent", "no_evidence_admitted"})


def _boundary_note(
    abstention: AbstentionClass | None,
    boundary: SourceBoundary | None,
) -> str | None:
    """Say what the declared source boundary makes of this abstention.

    Undeclared returns ``None`` rather than a guess: an undeclared boundary is
    exactly the ambiguity this field exists to remove, and inventing a default
    here would reintroduce it one layer down.
    """
    if abstention not in _BOUNDARY_SENSITIVE or boundary is None:
        return None
    if boundary == "exhaustive":
        return (
            "The bundle is declared the complete source, so this silence is itself "
            "informative: the source does not address the claim. An absence claim is "
            "decidable here, and abstaining understates what the evidence shows."
        )
    if boundary == "named_missing_material":
        return (
            "The bundle is declared an excerpt that names what is missing. Check the "
            "named gaps before reading this silence as an absence in the source."
        )
    return (
        "The bundle is declared an excerpt, so silence here is not absence in the "
        "source. Abstaining is the correct answer, not a miss — the claim cannot be "
        "settled from a partial source."
    )


def explain(
    trace: AuditTrace | ExplicitClaimTrace,
    config: AuditConfig | None = None,
    signal_floor: float = DEFAULT_SIGNAL_FLOOR,
    logit_slots: LogitSlots | None = None,
    source_boundary: SourceBoundary | None = None,
) -> Explanation:
    """Explain a verdict using only what CAL recorded when it produced it.

    ``logit_slots`` lets a caller classify pre-instrumentation traces; recover it
    once per corpus with :func:`recover_logit_slots`. Without it, such traces
    classify no finer than ``read_silent``.
    """
    if isinstance(trace, ExplicitClaimTrace):
        return _explain_explicit(trace, config, signal_floor, logit_slots)

    verdict = trace.verdict.support_verdict
    abstention = classify_abstention(trace, signal_floor, logit_slots)
    detail = _ABSTENTION_MEANING[abstention] if abstention else _VERDICT_HEADLINE[verdict]

    return Explanation(
        claim_id=trace.claim_id,
        verdict=verdict,
        headline=_VERDICT_HEADLINE[verdict],
        detail=detail,
        abstention_class=abstention,
        certainty=_certainty(trace, config, logit_slots),
        audit_flags=list(trace.verdict.audit_flags),
        rule_provenance=[f"{r.rule_id}: {r.reason}" for r in trace.rules_fired],
        next_step=_next_step_for(abstention, trace),
        source_boundary=source_boundary,
        boundary_note=_boundary_note(abstention, source_boundary),
    )


def _explain_explicit(
    trace: ExplicitClaimTrace,
    config: AuditConfig | None,
    signal_floor: float,
    logit_slots: LogitSlots | None = None,
) -> Explanation:
    """Explain a declared-structure parent verdict from its aggregation receipt."""
    agg = trace.parent_aggregation
    verdict = trace.verdict.support_verdict

    breakdown = []
    for atom in trace.atom_audits:
        atom_verdict = atom.audit_trace.verdict.support_verdict
        atom_class = classify_abstention(atom.audit_trace, signal_floor, logit_slots)
        suffix = f" [{atom_class}]" if atom_class else ""
        breakdown.append(f"{atom_verdict}{suffix}: {atom.claim_text}")

    return Explanation(
        claim_id=trace.parent_claim_id,
        verdict=verdict,
        headline=_VERDICT_HEADLINE[verdict],
        # CAL's own aggregation receipt is the explanation. No parallel wording.
        detail=agg.reason,
        abstention_class=None,
        certainty=Certainty(band=trace.verdict.audit_confidence),
        audit_flags=list(trace.verdict.audit_flags),
        rule_provenance=[f"{agg.rule_id}: {agg.reason}"],
        atom_breakdown=breakdown,
    )
