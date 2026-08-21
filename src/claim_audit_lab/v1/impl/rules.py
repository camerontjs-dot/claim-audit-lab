"""Deterministic verdict layer for CAL v1 (``cal-rules-v1.13.0``).

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

Decision I (``cal-rules-v1.8.0``, ``adr-v1-bound-instantiation.md``): **a rule
whose operator is invalid over the evidence in front of it says nothing.**
``A3`` mirrors negation between claim and passage, which presumes the passage
states a *fact*. A negated consequence instantiating a stated *bound* — "a
batch below 40% cannot pass" against "batches must achieve at least 40%" —
follows correctly from a positively-stated rule that need not express any
negation, so ``A3`` stands down (``A3_bound_instantiation_suppressed``). The
suppression is narrow: the claim must carry a quantity, leaving A3's MoNLI
purpose over non-numeric negation untouched. ``6a`` has the *same* defect over
bounds and is **not** fixed here — a suppression keyed on bound language was
built, preregistered, and rejected by its own gate (see
``outputs/2026-08-05-bound-instantiation-fix/``); replacing its operator with
interval containment is an open ADR.

The same invalid-operator rule applies narrowly to partial-conjunct negation:
when a compound claim asserts one conjunct and negates another (``P but not
Q``), A3 may not mirror the whole claim from support for ``P``. This does not
suppress compound claims generally. Root-scoped negation, including a root
predicate coordinated with another predicate, retains the A3 contradiction
guard.

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
    citation_numbers,
    content_lemma_set,
    deontic_strength,
    expresses_bound,
    expresses_negation,
    has_approximation_marker,
    has_conjunct_scoped_negation,
    has_numerical_value,
    scope_mismatch,
    scope_strength,
    source_coverage_claim,
)
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.models import (
    AuditConfidence,
    AuditConfig,
    AuditFlag,
    EntailResult,
    ExtractedFeatures,
    NegationProbe,
    Passage,
    Quantity,
    RetrievalResult,
    RuleFired,
    SourceBoundary,
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
    claim: str,
    source_boundary: SourceBoundary | None = None,
    claimed_material_is_a_named_gap: bool = False,
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
    # A6 — source-coverage claims (cal-rules-v1.10.0, D11). A claim that a
    # *document* does not say something is not refutable from passages excerpted
    # out of that document: silence in the bundle is exactly what the claim
    # asserts, and a passage on the adjacent topic neither confirms nor refutes
    # it. Measured, the entailer calls that a contradiction at 0.978 and the
    # score gives no warning at all.
    #
    # A6 still withholds refutation when the boundary is undeclared or bounded
    # (excerpts). Exhaustive and named-gap decisions happen in Phase A so they
    # do not re-enter this loop.
    if (
        features.has_explicit_negation
        and source_boundary != "exhaustive"
        and not (source_boundary == "named_missing_material" and claimed_material_is_a_named_gap)
    ):
        coverage = source_coverage_claim(claim)
        if coverage is not None:
            subject, predicate = coverage
            return RuleFired(
                rule_id="A6_absence_not_decidable",
                reason=(
                    f"the claim denies that the {subject} {predicate}s the material; "
                    "whether a source is silent is settled by that source's completeness, "
                    "not by passages excerpted from it → "
                    f"{contributing.passage_id} may not solo-decide an adverse degree, "
                    "re-aggregating"
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
    """v1 deterministic verdict layer (``cal-rules-v1.13.0``)."""

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
        negation_probe: NegationProbe | None = None,
        source_boundary: SourceBoundary | None = None,
        claimed_material_is_a_named_gap: bool = False,
        absence_complement_entailed: bool = False,
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
                negation_probe=negation_probe,
                source_boundary=source_boundary,
                claimed_material_is_a_named_gap=claimed_material_is_a_named_gap,
                absence_complement_entailed=absence_complement_entailed,
            )
            suppression = _eligibility_guard(
                verdict,
                signal,
                _passage_by_id(passages, signal.contributing_passage_id),
                features,
                claim,
                source_boundary=source_boundary,
                claimed_material_is_a_named_gap=claimed_material_is_a_named_gap,
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
        negation_probe: NegationProbe | None = None,
        source_boundary: SourceBoundary | None = None,
        claimed_material_is_a_named_gap: bool = False,
        absence_complement_entailed: bool = False,
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

        coverage = source_coverage_claim(claim) if features.has_explicit_negation else None
        if coverage is not None:
            if source_boundary == "named_missing_material" and claimed_material_is_a_named_gap:
                fired.append(
                    RuleFired(
                        rule_id="A6_named_gap_present",
                        reason=(
                            "the claim denies that a document addresses material the "
                            "caller declared is among the named gaps, so the source is "
                            "stipulated to address it → contradicted"
                        ),
                    )
                )
                return _contradicted("high"), fired
            if source_boundary == "exhaustive":
                if absence_complement_entailed:
                    fired.append(
                        RuleFired(
                            rule_id="A6_absence_refuted",
                            reason=(
                                "the bundle is the complete source and a passage entails "
                                "the positive complement of this coverage claim → contradicted"
                            ),
                        )
                    )
                    return _contradicted("high"), fired
                subject, predicate = coverage
                fired.append(
                    RuleFired(
                        rule_id="A6_absence_decidable",
                        reason=(
                            f"the bundle is the complete source and the claim denies that "
                            f"the {subject} {predicate}s the material; silence in the "
                            "source is a fact about the source → supported"
                        ),
                    )
                )
                return Verdict(support_verdict="supported", audit_confidence="high"), fired

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
            # D2 (cal-rules-v1.8.0): a negated *consequence* instantiating a
            # stated bound — "a batch below 40% cannot pass" against a passage
            # requiring >= 40% — follows correctly from a positively-stated
            # rule, which need not express any negation. A3's mirror test has
            # no valid operator over a bound, so it stands down. Narrow by
            # construction: the claim must carry a quantity, so A3's MoNLI
            # purpose over non-numeric negation is untouched.
            bound_instantiation = bool(features.numerical_values) and expresses_bound(
                contributing_text
            )
            # D8/X11: suppress only P-but-not-Q, where the parsed negation is
            # confined to a non-root conjunct.  A compound flag alone is not
            # sufficient; root-scoped negation keeps A3 active.
            conjunct_scoped_negation = features.compound_claim and has_conjunct_scoped_negation(
                claim
            )
            if (
                support_signal.label == "entail"
                and not expresses_negation(contributing_text)
                and not bound_instantiation
                and not conjunct_scoped_negation
            ):
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
            if conjunct_scoped_negation and support_signal.label == "entail":
                fired.append(
                    RuleFired(
                        rule_id="A3_conjunct_negation_suppressed",
                        reason=(
                            "negation is confined to one conjunct of a compound claim; "
                            "A3's whole-claim mirror is invalid, so the entailment signal "
                            "governs"
                        ),
                    )
                )
            if bound_instantiation and support_signal.label == "entail":
                fired.append(
                    RuleFired(
                        rule_id="A3_bound_instantiation_suppressed",
                        reason=(
                            "negated claim instantiates a bound stated by the supporting "
                            "passage; a positive rule need not express the negation → "
                            "A3 stands down, entailment signal governs"
                        ),
                    )
                )
            # A passage that itself expresses the negation — clause-level,
            # constituent ("no X"), or lexical absence ("X-free") — agrees with
            # the claim; the entailer's signal stands (Decision F1). Absence
            # routing (gold 4b/4c/4d) needs an absence-claim feature + topic
            # scope signal v1 lacks; deferred to an ADR rather than guessed.

        # A5 conflicting evidence (cal-rules-v1.9.0). The aggregator reports the
        # strongest *position* any passage takes, which is a single label. When
        # one passage entails above `supported_threshold` and a different one
        # contradicts above `contradicted_threshold`, that single label is
        # whichever scored higher — a margin that can be thousandths, and that
        # carries no information about which passage is the right one to read.
        #
        # Measured 2026-08-19 on the construction corpus: an out-of-scope passage
        # contradicting at 0.964 outranked the in-scope passage entailing at
        # 0.948 and silently drove the verdict. Both channels are already
        # recorded on the signal; nothing was reading them.
        #
        # Placed ahead of A4 and B5 so it covers both directions: a spurious
        # `contradict` label that would reach A4, and a spurious `entail` label
        # that would reach the degree mapping as `supported`. CAL cannot know
        # which passage governs — that needs a scope feature it does not have —
        # so it reports the disagreement instead of resolving it by score.
        if (
            support_signal.best_entail is not None
            and support_signal.best_contradict is not None
            and support_signal.best_entail >= audit_config.supported_threshold
            and support_signal.best_contradict >= audit_config.contradicted_threshold
        ):
            fired.append(
                RuleFired(
                    rule_id="A5_conflicting_evidence",
                    reason=(
                        f"{support_signal.best_entail_passage_id} entails at "
                        f"{support_signal.best_entail:.2f} and "
                        f"{support_signal.best_contradict_passage_id} contradicts at "
                        f"{support_signal.best_contradict:.2f}; both clear their "
                        "thresholds and they cannot both govern → not_checkable"
                    ),
                )
            )
            return _not_checkable("conflicting_evidence", "low"), fired

        # A7 scope mismatch (cal-rules-v1.13.0). A5 covers two passages that
        # disagree. This covers the one-passage case: the contradicting
        # passage names a *different location phrase* than the claim.
        # Eligibility only — CAL asks which site the claim is about rather
        # than emitting a false adverse. Same-site contradictions still fire
        # A4. Decision F: the operator is disjoint location-heads, not
        # bag-of-stems overlap deciding support.
        if (
            support_signal.label == "contradict"
            and support_signal.max_entailment_score >= audit_config.contradicted_threshold
            and contributing is not None
            and scope_mismatch(claim, contributing_text)
        ):
            fired.append(
                RuleFired(
                    rule_id="A7_scope_mismatch",
                    reason=(
                        f"{contributing.passage_id} contradicts at "
                        f"{support_signal.max_entailment_score:.2f} but names a "
                        "different site or subject than the claim; confirm which "
                        "one the claim is about → not_checkable"
                    ),
                )
            )
            return _not_checkable("out_of_scope", "low"), fired

        if (
            support_signal.label == "contradict"
            and support_signal.max_entailment_score >= audit_config.contradicted_threshold
        ):
            # A4 negation-consistency confirmation (cal-rules-v1.7.0,
            # adr-v1-slg09-negation-consistency.md): a true contradiction's
            # premise must also entail the structurally negated claim. The probe
            # only applies to the premise it was computed against (a suppression
            # re-aggregation may surface a different contributing passage — that
            # pass proceeds unprobed rather than misusing a stale record), and an
            # abstained or absent probe never demotes.
            #
            # cal-rules-v1.9.0 adds the confidence precondition below. The probe
            # is a second reading by the same model on a *harder* input — a
            # machine-negated sentence carrying modals, quantifiers or scope
            # prefixes — so it is systematically less reliable than the primary
            # measurement it is being used to overturn. Letting a 0.43 probe veto
            # a 0.995 contradiction is backwards.
            #
            # Measured 2026-08-19 on the construction corpus: the probe demoted
            # 7 of 7 correctly-detected contradictions, on probe readings of
            # 0.43-0.93 against primaries of 0.975-0.996. Requiring the veto to
            # be at least as confident as the signal it vetoes removes all seven
            # and preserves the single PILOT-001 case where the rule does real
            # work (c009: primary 0.766, probe neutral 0.996 — still demotes).
            probe_result = (
                negation_probe.result
                if (
                    negation_probe is not None
                    and not negation_probe.abstained
                    and negation_probe.result is not None
                    and negation_probe.result.passage_id == support_signal.contributing_passage_id
                    and negation_probe.result.label != "entail"
                )
                else None
            )
            if probe_result is not None:
                if probe_result.score >= support_signal.max_entailment_score:
                    fired.append(
                        RuleFired(
                            rule_id="A4_negation_consistency",
                            reason=(
                                f"NLI contradiction at "
                                f"{support_signal.max_entailment_score:.2f} is unconfirmed: "
                                "the premise does not entail the negated claim "
                                f"({probe_result.label} "
                                f"{probe_result.score:.2f}) → not_checkable"
                            ),
                        )
                    )
                    return _not_checkable("no_entail_signal", "low"), fired
                # Recorded, not decisive: a non-firing that leaves no trace is a
                # non-firing nobody can audit.
                fired.append(
                    RuleFired(
                        rule_id="A4_negation_probe_uninformative",
                        reason=(
                            f"negation probe ({probe_result.label} "
                            f"{probe_result.score:.2f}) is less confident than the "
                            f"contradiction it would demote "
                            f"({support_signal.max_entailment_score:.2f}), so it carries no "
                            "evidence that the contradiction is spurious → A4 stands down"
                        ),
                    )
                )
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
            # D3 (cal-rules-v1.8.0): a regulatory citation is an address, not a
            # measurement. quantulum3 reads `21 CFR Part 11` as 21 and 11.
            cited = citation_numbers(claim)
            unmatched: list[float] = []
            for quantity in features.numerical_values:
                if quantity.value in cited:
                    continue
                comparable = [p for p in passage_quantities if _comparable(quantity, p)]
                if comparable and not any(
                    _within_tolerance(quantity.value, p.value, tolerance) for p in comparable
                ):
                    unmatched.append(quantity.value)
            # D1 is NOT fixed here. A suppression keyed on bound *language* in
            # the passage was built, preregistered, and rejected by its own
            # gate: `maximum allowable X must remain at 24 hours` carries the
            # lexeme while the operative relation is equality, so suppressing
            # there promoted three authored-conflicting claims to `supported`.
            # Disabling 6a is not the fix — the operator has to be *replaced*
            # by the interval algebra the numeric-comparator probe built
            # (parse the claim's asserted region, parse the permitted region,
            # test containment). That is an ADR-sized change, not a guard.
            # See outputs/2026-08-05-bound-instantiation-fix/FINDINGS.md.
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
