"""Deterministic verdict layer for CAL v1 (``cal-rules-v1.5.0``).

The rules layer is the only stage that produces a final verdict. It applies the
canonical **Decision C** order (``plans/adr-v1-rule-order.md``) over the
aggregated NLI support signal, the extracted claim features, and the retrieved
passages, with the **Decision F** semantics
(``plans/adr-v1-rules-v1.4.0-semantic-fixes.md``) inside the **Decision H**
eligibility suppression loop (``plans/adr-v1-absence-route.md``):

* **Phase A — gates** (short-circuit, first match stops): ``A1`` scope,
  ``A2`` retrieval-empty, ``A3`` negation/absence backstop, ``A4``
  hard-contradiction.
* **Phase B — degree** maps the support signal to a provisional degree.
* **Phase C — adjustments** all run, each evaluated against the *provisional*
  degree; the final degree is the most-adverse proposal (order-independent;
  ``contradicted`` is terminal). Flags are always settable. ``6a`` numeric,
  ``6b`` strength/scope, ``6c`` inferred, ``6d`` source-scope, ``6f`` false
  caution.

Decision F invariant: **no rule flips or downgrades a degree on a
lexical-overlap signal** — overlap may set a flag (6c ``inferred``), never
decide. The degree-changing rules read semantic/structural evidence only:
``A3`` compares negation *expression* between claim and passage (asymmetric
detectors — narrow clause-level on the claim, broad constituent/lexical
absence on the passage); ``6b`` compares claim deontic/scope strength against
the passage's (gold H2/H3, "required-on-recommended") and stays silent over
plain assertive evidence; ``6a`` compares only unit-and-year-comparable
quantities, with approximation-marker-aware tolerance.

Decision H invariant (extends Decision F): **eligibility gates adverse
decisions; ineligible or self-agreeing evidence may flag, never decide.**
:meth:`VerdictRules.apply` wraps the Decision-C classifier
(:meth:`VerdictRules._classify_once`) in a suppression loop: an adverse degree
whose contributing passage is an ineligible source (``trust_level`` present and
not ``primary`` — ``P1``) or is an A3 negation mirror (a negated claim whose
contradicting passage itself expresses the negation — ``P2``) is not allowed to
stand; that passage's result is dropped and the still-eligible pool
re-aggregated. The verdict falls through to the best remaining eligible signal,
or — over an empty / all-neutral pool — to ``not_checkable/no_entail_signal``
(never adverse). The source ``trust_level`` is the provenance the intake join
carries (``v1/intake.py``, D1); consuming it does not breach the independence
lock — it is what a document *is*, not a per-claim support judgment.

Every rule that fires appends a ``RuleFired(rule_id, reason)``; no degree
changes without one. See DECISIONS.md § 2026-06-21 § 5, § Phase 1 Unit 2,
§ 2026-07-02, and § 2026-07-07.

Interpretations carried from the v1.3.0 ratification (unchanged): a
``contradict`` signal *below* ``contradicted_threshold`` maps to
``unsupported``; ``6e`` ``citation_status`` stays deferred (no citation in the
v1 input contract); gate-3 absence routing (gold 4b/4c/4d) stays deferred —
only the MoNLI backstop is coded.
"""

from __future__ import annotations

from dataclasses import dataclass

from claim_audit_lab.v1.features import (
    content_lemma_set,
    deontic_strength,
    expresses_negation,
    has_approximation_marker,
    has_numerical_value,
    scope_strength,
)
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.models import (
    AuditConfidence,
    AuditConfig,
    AuditFlag,
    EntailResult,
    ExtractedFeatures,
    Passage,
    Quantity,
    RetrievalResult,
    RuleFired,
    SupportSignal,
    SupportVerdict,
    Verdict,
    VerdictReason,
)

_MIN_CLAIM_TOKENS = 5

# Severity ordering for the Phase C composition rule: adjustments may only move
# the degree toward *more adverse*, and ``contradicted`` is terminal.
_SEVERITY: dict[SupportVerdict, int] = {
    "not_checkable": 0,
    "supported": 0,
    "partially_supported": 1,
    "unsupported": 2,
    "contradicted": 3,
}

# Source trust tiers that mark background content presented as fact (the 6d
# source-scope flag). The C-B vocabulary is primary / secondary / background
# (``contracts/cb_models.py`` ``TrustLevel``); ``"fictional"`` is not a real tier
# — a valid bundle can never carry it — so it is deliberately absent here.
_BACKGROUND_TRUST_LEVELS = frozenset({"background"})

# Terminal adverse degrees the Decision-H eligibility precondition guards.
_ADVERSE = frozenset({"unsupported", "contradicted"})

# Flags that presuppose support; dropped when the final degree is adverse
# (Decision F6). ``overstated`` stays — an overreaching claim can also be
# contradicted, and the composition fixture locks that pairing.
_SUPPORT_ONLY_FLAGS = frozenset({"inferred", "false_caution"})

# A unitless integer in this range is treated as a year for comparability:
# years compare only against years (Decision F3).
_YEAR_RANGE = (1900, 2100)


def _passage_by_id(passages: list[Passage], passage_id: str | None) -> Passage | None:
    if passage_id is None:
        return None
    return next((passage for passage in passages if passage.passage_id == passage_id), None)


def _most_adverse(degrees: list[SupportVerdict]) -> SupportVerdict:
    return max(degrees, key=lambda degree: _SEVERITY[degree])


def _add_flag(flags: list[AuditFlag], flag: AuditFlag) -> None:
    if flag not in flags:
        flags.append(flag)


def _within_tolerance(claim_value: float, passage_value: float, tolerance: float) -> bool:
    if tolerance == 0.0:
        return claim_value == passage_value
    scale = max(abs(claim_value), abs(passage_value), 1.0)
    return abs(claim_value - passage_value) <= tolerance * scale


def _year_like(quantity: Quantity) -> bool:
    low, high = _YEAR_RANGE
    return (
        quantity.unit is None
        and float(quantity.value).is_integer()
        and low <= quantity.value <= high
    )


def _comparable(claim_quantity: Quantity, passage_quantity: Quantity) -> bool:
    """Same unit (both None or equal names) and same year-likeness (Decision F3)."""
    return claim_quantity.unit == passage_quantity.unit and _year_like(
        claim_quantity
    ) == _year_like(passage_quantity)


def _claim_kind(claim: str) -> str:
    return "prescriptive" if deontic_strength(claim) == "strong" else "universal"


def _not_checkable(reason: VerdictReason, confidence: AuditConfidence) -> Verdict:
    return Verdict(
        support_verdict="not_checkable",
        support_verdict_reason=reason,
        audit_confidence=confidence,
    )


def _contradicted(confidence: AuditConfidence) -> Verdict:
    return Verdict(support_verdict="contradicted", audit_confidence=confidence)


def _eligibility_guard(
    verdict: Verdict,
    signal: SupportSignal,
    contributing: Passage | None,
    features: ExtractedFeatures,
) -> RuleFired | None:
    """Return a suppression ``RuleFired`` if an adverse degree may not stand, else ``None``.

    The Decision-H invariant: **eligibility gates adverse decisions; ineligible or
    self-agreeing evidence may flag, never decide.** P1 (eligibility) is checked
    before P2 (the A3 negation mirror); at most one suppression per iteration. A
    source is ineligible when its ``trust_level`` is *present and not* ``primary``;
    an absent ``trust_level`` — a directly-constructed, non-bundle passage — is
    treated as eligible, so the gate never fires outside the apparatus intake path.
    """
    if verdict.support_verdict not in _ADVERSE or contributing is None:
        return None
    trust = contributing.source_meta.get("trust_level")
    if trust is not None and trust != "primary":  # P1 — eligibility precondition (D2)
        return RuleFired(
            rule_id="P1_eligibility_suppressed",
            reason=(
                f"{signal.label} {signal.max_entailment_score:.2f} from "
                f"{contributing.passage_id} (trust_level={trust!r}) may not "
                "solo-decide an adverse degree → suppressed, re-aggregating"
            ),
        )
    if (
        features.has_explicit_negation
        and signal.label == "contradict"
        and expresses_negation(contributing.text)
    ):  # P2 — A3 negation mirror (D3)
        return RuleFired(
            rule_id="P2_absence_mirror_suppressed",
            reason=(
                f"negated claim; contradicting passage {contributing.passage_id} "
                "itself expresses the negation (agrees with the claim) — MoNLI "
                "mirror → suppressed, re-aggregating"
            ),
        )
    return None


@dataclass(frozen=True)
class VerdictRules:
    """v1 deterministic verdict layer (``cal-rules-v1.5.0``)."""

    rules_file_sha: str

    def apply(
        self,
        *,
        claim: str,
        features: ExtractedFeatures,
        passages: list[Passage],
        retrieval: list[RetrievalResult],
        entailment: list[EntailResult],
        support_signal: SupportSignal,
        audit_config: AuditConfig,
    ) -> tuple[Verdict, list[RuleFired]]:
        """Apply the Decision-C rules under the Decision-H eligibility suppression loop.

        The loop starts from the pipeline's raw ``support_signal`` (the stock
        max-entailment signal over the full floor-admitted pool, stamped into the
        trace) and runs the Decision-C classifier (:meth:`_classify_once`). When the
        resulting degree is adverse and its contributing passage may not decide it —
        an ineligible (non-``primary``) source (P1) or an A3 negation mirror (P2) —
        that passage's entailment result is dropped from the eligible pool and the
        pool is **re-aggregated** with the stock ``MaxEntailmentAggregator`` for the
        next pass. Ineligible passages stay in the trace and may still set flags;
        they just cannot *decide*. Landing is emergent: an empty / all-neutral pool
        aggregates to a neutral signal → B5 → ``not_checkable/no_entail_signal``
        (never adverse), so the loop always terminates (the pool strictly shrinks on
        every suppression). Because the pipeline passes ``support_signal ==
        aggregate(entailment)``, seeding the first pass with the given signal is
        identical to re-aggregating it; the seed only matters to unit tests that
        exercise the classifier with a hand-set signal.
        """
        if audit_config.rules_file_sha != self.rules_file_sha:
            raise ValueError(
                "audit_config is pinned to a different rules file than these rules: "
                f"{audit_config.rules_file_sha!r} != {self.rules_file_sha!r}"
            )

        aggregator = MaxEntailmentAggregator()
        signal = support_signal
        pool = list(entailment)
        suppressions: list[RuleFired] = []
        while True:
            verdict, fired = self._classify_once(
                claim=claim,
                features=features,
                passages=passages,
                retrieval=retrieval,
                entailment=pool,
                support_signal=signal,
                audit_config=audit_config,
            )
            suppression = _eligibility_guard(
                verdict,
                signal,
                _passage_by_id(passages, signal.contributing_passage_id),
                features,
            )
            if suppression is None:
                return verdict, [*suppressions, *fired]
            suppressions.append(suppression)
            pool = [r for r in pool if r.passage_id != signal.contributing_passage_id]
            signal = aggregator.aggregate(pool)

    def _classify_once(
        self,
        *,
        claim: str,
        features: ExtractedFeatures,
        passages: list[Passage],
        retrieval: list[RetrievalResult],
        entailment: list[EntailResult],
        support_signal: SupportSignal,
        audit_config: AuditConfig,
    ) -> tuple[Verdict, list[RuleFired]]:
        """One Decision-C classification pass over a fixed ``support_signal``.

        This is the v1.4.0 verdict body, unchanged: the Decision-H suppression loop
        in :meth:`apply` re-aggregates the eligible pool and re-invokes it per
        iteration. ``entailment`` is accepted for protocol symmetry but not read —
        the classifier decides on ``support_signal`` alone.
        """
        fired: list[RuleFired] = []

        # ----- Phase A — gates (short-circuit) -----
        if (
            features.sentence_type in ("opinion", "question", "imperative")
            or features.claim_token_count < _MIN_CLAIM_TOKENS
        ):
            fired.append(
                RuleFired(
                    rule_id="A1_scope",
                    reason=(
                        f"out-of-scope input (sentence_type={features.sentence_type}, "
                        f"tokens={features.claim_token_count})"
                    ),
                )
            )
            return _not_checkable("out_of_scope", "high"), fired

        if not any(result.score >= audit_config.retrieval_floor for result in retrieval):
            fired.append(
                RuleFired(
                    rule_id="A2_retrieval_empty",
                    reason=f"no passage cleared retrieval_floor={audit_config.retrieval_floor}",
                )
            )
            return _not_checkable("no_evidence", "high"), fired

        contributing = _passage_by_id(passages, support_signal.contributing_passage_id)
        contributing_text = contributing.text if contributing is not None else ""

        if features.has_explicit_negation:
            if support_signal.label == "entail" and not expresses_negation(contributing_text):
                fired.append(
                    RuleFired(
                        rule_id="A3_negation_backstop",
                        reason=(
                            "claim carries clause-level negation but the supporting passage "
                            "asserts the un-negated content (MoNLI backstop) → contradicted"
                        ),
                    )
                )
                return _contradicted("high"), fired
            # A passage that itself expresses the negation — clause-level,
            # constituent ("no X"), or lexical absence ("X-free") — agrees with
            # the claim; the entailer's signal stands (Decision F1). Absence
            # routing (gold 4b/4c/4d) needs an absence-claim feature + topic
            # scope signal v1 lacks; deferred to an ADR rather than guessed.

        if (
            support_signal.label == "contradict"
            and support_signal.max_entailment_score >= audit_config.contradicted_threshold
        ):
            fired.append(
                RuleFired(
                    rule_id="A4_hard_contradiction",
                    reason=(
                        f"NLI contradiction at {support_signal.max_entailment_score:.2f} "
                        f">= contradicted_threshold={audit_config.contradicted_threshold}"
                    ),
                )
            )
            return _contradicted("high"), fired

        # ----- Phase B — degree mapping -----
        score = support_signal.max_entailment_score
        if support_signal.label == "entail" and score >= audit_config.supported_threshold:
            provisional: SupportVerdict = "supported"
            degree_reason = (
                f"entail {score:.2f} >= supported_threshold={audit_config.supported_threshold}"
            )
        elif support_signal.label == "entail":
            provisional = "partially_supported"
            degree_reason = f"entail {score:.2f} < supported_threshold → partial"
        elif support_signal.label == "contradict":
            provisional = "unsupported"
            degree_reason = (
                f"contradiction {score:.2f} < contradicted_threshold → evidence leans against"
            )
        else:
            fired.append(
                RuleFired(rule_id="B5_degree", reason="neutral support signal — no entailment")
            )
            return _not_checkable("no_entail_signal", "low"), fired
        fired.append(RuleFired(rule_id="B5_degree", reason=degree_reason))

        # ----- Phase C — adjustments (evaluated against the provisional degree; the final
        # degree is the most-adverse proposal — order-independent, contradicted terminal). -----
        proposals: list[SupportVerdict] = [provisional]
        flags: list[AuditFlag] = []

        claim_lemmas = content_lemma_set(claim)
        verbatim = bool(claim_lemmas) and claim_lemmas <= content_lemma_set(contributing_text)
        claim_strong = deontic_strength(claim) == "strong" or features.has_universal_quantifier

        # 6a — numeric / date agreement over comparable quantities (Decision F3)
        if features.numerical_values:
            passage_quantities = has_numerical_value(contributing_text)
            tolerance = audit_config.numeric_tolerance
            if has_approximation_marker(claim):
                tolerance = max(tolerance, audit_config.approx_numeric_tolerance)
            unmatched: list[float] = []
            for quantity in features.numerical_values:
                comparable = [p for p in passage_quantities if _comparable(quantity, p)]
                if comparable and not any(
                    _within_tolerance(quantity.value, p.value, tolerance) for p in comparable
                ):
                    unmatched.append(quantity.value)
            if unmatched and len(features.numerical_values) == 1:
                proposals.append("contradicted")
                fired.append(
                    RuleFired(
                        rule_id="C6a_numeric",
                        reason=(
                            f"claim quantity {unmatched[0]} not matched by any comparable "
                            f"supporting-passage quantity (crux) → contradicted"
                        ),
                    )
                )
            elif unmatched:
                proposals.append("partially_supported")
                fired.append(
                    RuleFired(
                        rule_id="C6a_numeric",
                        reason=(
                            f"{len(unmatched)} claim quantity(ies) unmatched by comparable "
                            f"passage quantities → partial"
                        ),
                    )
                )

        # 6b — strength / scope overreach: claim strength vs passage strength
        # (Decision F2). Fires only on positive evidence of a weaker-scoped
        # passage; plain assertive evidence never triggers a downgrade.
        overreach = claim_strong and scope_strength(contributing_text) == "weak"
        if overreach and provisional == "supported":
            proposals.append("partially_supported")
            _add_flag(flags, "overstated")
            fired.append(
                RuleFired(
                    rule_id="C6b_strength_scope",
                    reason=(
                        f"{_claim_kind(claim)} claim over weaker-scoped evidence "
                        f"→ partial + overstated"
                    ),
                )
            )
        elif overreach and provisional == "partially_supported":
            _add_flag(flags, "overstated")
            fired.append(
                RuleFired(
                    rule_id="C6b_strength_scope",
                    reason=(
                        f"{_claim_kind(claim)} claim over weaker-scoped partial evidence "
                        f"→ overstated"
                    ),
                )
            )

        # 6c — inferred (plain claim supported by inference, not verbatim).
        # Lexical overlap may set this flag; it never decides a degree
        # (Decision F5 / the Decision F invariant).
        if provisional == "supported" and not verbatim and not claim_strong:
            _add_flag(flags, "inferred")
            fired.append(
                RuleFired(
                    rule_id="C6c_inferred",
                    reason="entailment holds but the claim is not stated verbatim → inferred",
                )
            )

        # 6d — source-scope
        if (
            contributing is not None
            and contributing.source_meta.get("trust_level") in _BACKGROUND_TRUST_LEVELS
        ):
            _add_flag(flags, "source_scope_error")
            fired.append(
                RuleFired(
                    rule_id="C6d_source_scope",
                    reason=(
                        "supporting passage trust_level="
                        f"{contributing.source_meta.get('trust_level')!r} presented as fact "
                        "→ source_scope_error"
                    ),
                )
            )

        # 6e — citation_status deferred (no citation in the v1 input contract).

        # 6f — false caution
        if (
            provisional == "supported"
            and features.modal_strength == "hedges"
            and score >= audit_config.supported_threshold
        ):
            _add_flag(flags, "false_caution")
            fired.append(
                RuleFired(
                    rule_id="C6f_false_caution",
                    reason="claim hedges but the evidence strongly supports it → false_caution",
                )
            )

        final_degree = _most_adverse(proposals)
        if final_degree in ("unsupported", "contradicted"):
            # Decision F6 — support-presupposing flags are incoherent on an
            # adverse degree; drop them (overstated is deliberately retained).
            flags = [flag for flag in flags if flag not in _SUPPORT_ONLY_FLAGS]

        return (
            Verdict(
                support_verdict=final_degree,
                audit_flags=flags,
                citation_status="not_applicable",
                audit_confidence="medium",
            ),
            fired,
        )


__all__ = ["VerdictRules"]
