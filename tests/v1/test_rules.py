"""Behaviour tests for the v1 deterministic verdict layer (Decision C).

Each gate, degree exit, and Phase C adjustment branch is exercised on synthetic
inputs (hand-built features / passages / support signals — no model loads), per
the phase-1 "no unreachable branch" rule. The Phase C composition rule and the
rules-file integrity guard get dedicated tests.

The rule layer reads pre-extracted ``features`` (it does not re-parse the claim),
so feature values are set directly; passage *text* is real, since 6a parses it
with quantulum3 and the negation backstop parses it with spaCy.
"""

from __future__ import annotations

import pytest

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import (
    AuditConfig,
    EntailLabel,
    EntailResult,
    ExtractedFeatures,
    ModalStrength,
    NegationProbe,
    Passage,
    Quantity,
    RetrievalResult,
    RuleFired,
    SentenceType,
    SupportSignal,
    Verdict,
)

_CONFIG = load_default_audit_config()
_RULES = VerdictRules(rules_file_sha=_CONFIG.rules_file_sha)


def _features(
    *,
    sentence_type: SentenceType = "declarative",
    claim_token_count: int = 8,
    has_explicit_negation: bool = False,
    has_universal_quantifier: bool = False,
    compound_claim: bool = False,
    modal_strength: ModalStrength = "asserts",
    numerical_values: list[Quantity] | None = None,
) -> ExtractedFeatures:
    return ExtractedFeatures(
        sentence_type=sentence_type,
        claim_token_count=claim_token_count,
        has_explicit_negation=has_explicit_negation,
        has_universal_quantifier=has_universal_quantifier,
        compound_claim=compound_claim,
        modal_strength=modal_strength,
        numerical_values=numerical_values or [],
    )


def _run(
    *,
    claim: str = "The platform validates submitted input records.",
    features: ExtractedFeatures | None = None,
    passages: list[Passage] | None = None,
    retrieval: list[RetrievalResult] | None = None,
    support_signal: SupportSignal | None = None,
    entailment: list[EntailResult] | None = None,
    rules: VerdictRules = _RULES,
    config: AuditConfig | None = None,
    negation_probe: NegationProbe | None = None,
    source_boundary: str | None = None,
    claimed_material_is_a_named_gap: bool = False,
    absence_complement_entailed: bool = False,
) -> tuple[Verdict, list[RuleFired]]:
    passage_text = claim
    if features is None:
        features = _features()
    if passages is None:
        passages = [Passage(passage_id="p-1", text=passage_text)]
    if retrieval is None:
        retrieval = [RetrievalResult(passage_id="p-1", score=0.90)]
    if support_signal is None:
        support_signal = SupportSignal(
            label="entail", max_entailment_score=0.90, contributing_passage_id="p-1"
        )
    # The suppression loop re-aggregates the pool after a P1/P2 drop; ``entailment``
    # defaults to empty (classifier-only tests seed via ``support_signal``), and the
    # eligibility tests pass a pool consistent with that seed.
    return rules.apply(
        claim=claim,
        features=features,
        passages=passages,
        retrieval=retrieval,
        entailment=entailment if entailment is not None else [],
        support_signal=support_signal,
        audit_config=config or _CONFIG,
        negation_probe=negation_probe,
        source_boundary=source_boundary,  # type: ignore[arg-type]
        claimed_material_is_a_named_gap=claimed_material_is_a_named_gap,
        absence_complement_entailed=absence_complement_entailed,
    )


def _ids(fired: list[RuleFired]) -> set[str]:
    return {rule.rule_id for rule in fired}


# --- Phase A gate 1: scope -------------------------------------------------
@pytest.mark.parametrize("sentence_type", ["opinion", "question", "imperative"])
def test_scope_gate_routes_non_declarative_out_of_scope(sentence_type: SentenceType) -> None:
    verdict, fired = _run(features=_features(sentence_type=sentence_type))
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "out_of_scope"
    assert "A1_scope" in _ids(fired)


def test_scope_gate_routes_too_short_out_of_scope() -> None:
    verdict, fired = _run(features=_features(claim_token_count=3))
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "out_of_scope"
    assert "A1_scope" in _ids(fired)


# --- Phase A gate 2: retrieval-empty ---------------------------------------
def test_retrieval_empty_gate_routes_no_evidence() -> None:
    verdict, fired = _run(retrieval=[RetrievalResult(passage_id="p-1", score=0.10)])
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "no_evidence"
    assert "A2_retrieval_empty" in _ids(fired)


# --- Phase A gate 3: negation / absence backstop ---------------------------
def test_negation_backstop_contradicts_when_passage_asserts_unnegated_content() -> None:
    verdict, fired = _run(
        claim="The system does not validate inputs.",
        features=_features(has_explicit_negation=True),
        passages=[Passage(passage_id="p-1", text="The system validates inputs.")],
    )
    assert verdict.support_verdict == "contradicted"
    assert "A3_negation_backstop" in _ids(fired)


def test_negation_backstop_stands_down_for_negated_conjunct_only() -> None:
    verdict, fired = _run(
        claim=(
            "The guidance mentions trend analyses and continual monitoring for annual "
            "product reviews but doesn't specify a volume threshold."
        ),
        features=_features(has_explicit_negation=True, compound_claim=True),
        passages=[
            Passage(
                passage_id="p-1",
                text=("Annual product reviews include trend analyses and continual monitoring."),
            )
        ],
    )
    assert verdict.support_verdict == "supported"
    assert "A3_negation_backstop" not in _ids(fired)
    assert "A3_conjunct_negation_suppressed" in _ids(fired)


@pytest.mark.parametrize(
    "claim",
    [
        "The system does not validate inputs or archive records.",
        "The system does not validate inputs and does not archive records.",
    ],
)
def test_negation_backstop_preserves_whole_compound_contradiction(claim: str) -> None:
    verdict, fired = _run(
        claim=claim,
        features=_features(has_explicit_negation=True, compound_claim=True),
        passages=[
            Passage(passage_id="p-1", text="The system validates inputs and archives records.")
        ],
    )
    assert verdict.support_verdict == "contradicted"
    assert "A3_negation_backstop" in _ids(fired)
    assert "A3_conjunct_negation_suppressed" not in _ids(fired)


def test_negation_backstop_skipped_when_passage_also_negated() -> None:
    # Claim and passage agree on the negation → the entailer's "entail" is correct;
    # fall through to ordinary degree mapping rather than flipping to contradicted.
    verdict, fired = _run(
        claim="The system does not validate inputs.",
        features=_features(has_explicit_negation=True),
        passages=[Passage(passage_id="p-1", text="The system does not validate inputs.")],
    )
    assert verdict.support_verdict == "supported"
    assert "A3_negation_backstop" not in _ids(fired)


@pytest.mark.parametrize(
    "passage_text",
    [
        "The product contains no animal-derived ingredients.",  # determiner `no`
        "The product is latex-free.",  # X-free compound
        "The formulation is free of animal-derived ingredients.",  # free of
        "The product is shipped without preservatives.",  # absence lexeme
    ],
    ids=["det-no", "hyphen-free", "free-of", "without"],
)
def test_negation_backstop_skipped_when_passage_expresses_absence(passage_text: str) -> None:
    # Decision F1 regression (the review probe's false contradiction): a passage
    # expressing the same absence constituently or lexically AGREES with the
    # negated claim — the broad passage-side detector must suppress the backstop.
    verdict, fired = _run(
        claim="The product does not contain restricted ingredients.",
        features=_features(has_explicit_negation=True),
        passages=[Passage(passage_id="p-1", text=passage_text)],
    )
    assert verdict.support_verdict == "supported"
    assert "A3_negation_backstop" not in _ids(fired)


def test_negated_claim_without_entail_signal_falls_through_to_no_entail() -> None:
    verdict, _ = _run(
        features=_features(has_explicit_negation=True),
        support_signal=SupportSignal(
            label="neutral", max_entailment_score=0.0, contributing_passage_id=None
        ),
    )
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "no_entail_signal"


# --- Phase A gate 4: hard contradiction ------------------------------------
def test_hard_contradiction_gate() -> None:
    verdict, fired = _run(
        support_signal=SupportSignal(
            label="contradict", max_entailment_score=0.85, contributing_passage_id="p-1"
        )
    )
    assert verdict.support_verdict == "contradicted"
    assert "A4_hard_contradiction" in _ids(fired)


# --- Phase B: degree mapping -----------------------------------------------
def test_degree_supported_clean_baseline() -> None:
    verdict, fired = _run()
    assert verdict.support_verdict == "supported"
    assert verdict.audit_flags == []
    assert verdict.citation_status == "not_applicable"
    assert verdict.audit_confidence == "medium"
    assert "B5_degree" in _ids(fired)


def test_degree_partial_when_entail_below_threshold() -> None:
    verdict, _ = _run(
        support_signal=SupportSignal(
            label="entail", max_entailment_score=0.55, contributing_passage_id="p-1"
        )
    )
    assert verdict.support_verdict == "partially_supported"


def test_degree_unsupported_on_weak_contradiction() -> None:
    verdict, _ = _run(
        support_signal=SupportSignal(
            label="contradict", max_entailment_score=0.50, contributing_passage_id="p-1"
        )
    )
    assert verdict.support_verdict == "unsupported"


def test_degree_no_entail_signal_on_neutral() -> None:
    verdict, _ = _run(
        support_signal=SupportSignal(
            label="neutral", max_entailment_score=0.20, contributing_passage_id=None
        )
    )
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "no_entail_signal"
    assert verdict.audit_confidence == "low"


# --- Phase C 6a: numeric agreement -----------------------------------------
def test_numeric_crux_mismatch_contradicts() -> None:
    verdict, fired = _run(
        claim="The error rate is 5 percent.",
        features=_features(
            numerical_values=[Quantity(value=5.0, unit="percentage", surface_text="5 percent")]
        ),
        passages=[Passage(passage_id="p-1", text="The error rate is 10 percent.")],
    )
    assert verdict.support_verdict == "contradicted"
    assert "C6a_numeric" in _ids(fired)


def test_numeric_noncrux_mismatch_downgrades_to_partial() -> None:
    verdict, fired = _run(
        claim="There were 5 hits and 3 misses.",
        features=_features(
            numerical_values=[
                Quantity(value=5.0, surface_text="5"),
                Quantity(value=3.0, surface_text="3"),
            ]
        ),
        passages=[Passage(passage_id="p-1", text="There were 5 hits and 9 misses.")],
    )
    assert verdict.support_verdict == "partially_supported"
    assert "C6a_numeric" in _ids(fired)


def test_numeric_agreement_leaves_degree_supported() -> None:
    verdict, fired = _run(
        claim="The error rate is 5 percent.",
        features=_features(
            numerical_values=[Quantity(value=5.0, unit="percentage", surface_text="5 percent")]
        ),
        passages=[Passage(passage_id="p-1", text="The error rate is 5 percent.")],
    )
    assert verdict.support_verdict == "supported"
    assert "C6a_numeric" not in _ids(fired)


def test_numeric_skipped_when_passage_has_no_number() -> None:
    verdict, fired = _run(
        claim="The error rate is 5 percent.",
        features=_features(
            numerical_values=[Quantity(value=5.0, unit="percentage", surface_text="5 percent")]
        ),
        passages=[Passage(passage_id="p-1", text="The error rate is acceptable.")],
    )
    assert verdict.support_verdict == "supported"
    assert "C6a_numeric" not in _ids(fired)


def test_numeric_abstains_when_units_are_not_comparable() -> None:
    # Decision F3: a percent claim quantity is never compared against the
    # passage's hour quantity — incomparability is not evidence of mismatch.
    verdict, fired = _run(
        claim="The batch yield was 92 percent.",
        features=_features(
            numerical_values=[Quantity(value=92.0, unit="percentage", surface_text="92 percent")]
        ),
        passages=[Passage(passage_id="p-1", text="The batch completed in 92 hours.")],
    )
    assert verdict.support_verdict == "supported"
    assert "C6a_numeric" not in _ids(fired)


def test_numeric_year_compares_only_against_years() -> None:
    # Decision F3 regression (the review's "claim year vs unrelated numbers"
    # class): 2024 is year-like, the passage's 39.6 percent is not — abstain.
    abstained, fired_abstained = _run(
        claim="In 2024 the facility processed batches.",
        features=_features(numerical_values=[Quantity(value=2024.0, surface_text="2024")]),
        passages=[Passage(passage_id="p-1", text="Throughput reached 39.6 percent in review.")],
    )
    assert abstained.support_verdict == "supported"
    assert "C6a_numeric" not in _ids(fired_abstained)

    # A genuinely mismatched year against another year still contradicts.
    mismatched, fired_mismatched = _run(
        claim="The audit took place in 2024.",
        features=_features(numerical_values=[Quantity(value=2024.0, surface_text="2024")]),
        passages=[Passage(passage_id="p-1", text="The audit took place in 2023.")],
    )
    assert mismatched.support_verdict == "contradicted"
    assert "C6a_numeric" in _ids(fired_mismatched)


def test_numeric_approximation_marker_widens_tolerance() -> None:
    # Decision F3 regression (the review probe's "approximately 40 vs 39.6"):
    # the claim-level approximation marker applies approx_numeric_tolerance.
    approx, fired_approx = _run(
        claim="Approximately 40 percent of samples showed uptake.",
        features=_features(
            numerical_values=[Quantity(value=40.0, unit="percentage", surface_text="40 percent")]
        ),
        passages=[
            Passage(passage_id="p-1", text="Uptake was observed in 39.6 percent of samples.")
        ],
    )
    assert approx.support_verdict == "supported"
    assert "C6a_numeric" not in _ids(fired_approx)

    # The same numbers WITHOUT the marker keep the exact default → contradicted.
    exact, fired_exact = _run(
        claim="40 percent of samples showed uptake this cycle.",
        features=_features(
            numerical_values=[Quantity(value=40.0, unit="percentage", surface_text="40 percent")]
        ),
        passages=[
            Passage(passage_id="p-1", text="Uptake was observed in 39.6 percent of samples.")
        ],
    )
    assert exact.support_verdict == "contradicted"
    assert "C6a_numeric" in _ids(fired_exact)

    # Beyond even the approx tolerance, the marker does not save the claim.
    far, fired_far = _run(
        claim="Approximately 40 percent of samples showed uptake.",
        features=_features(
            numerical_values=[Quantity(value=40.0, unit="percentage", surface_text="40 percent")]
        ),
        passages=[Passage(passage_id="p-1", text="Uptake was observed in 25 percent of samples.")],
    )
    assert far.support_verdict == "contradicted"
    assert "C6a_numeric" in _ids(fired_far)


def test_numeric_tolerance_admits_close_values_and_rejects_far_ones() -> None:
    tolerant = _CONFIG.model_copy(update={"numeric_tolerance": 0.1})
    near, fired_near = _run(
        claim="The reading was 5.",
        features=_features(numerical_values=[Quantity(value=5.0, surface_text="5")]),
        passages=[Passage(passage_id="p-1", text="The reading was 5.4 on average.")],
        config=tolerant,
    )
    assert near.support_verdict == "supported"
    assert "C6a_numeric" not in _ids(fired_near)

    far, fired_far = _run(
        claim="The reading was 5.",
        features=_features(numerical_values=[Quantity(value=5.0, surface_text="5")]),
        passages=[Passage(passage_id="p-1", text="The reading was 7 on average.")],
        config=tolerant,
    )
    assert far.support_verdict == "contradicted"
    assert "C6a_numeric" in _ids(fired_far)


# --- Phase C 6b: strength / scope overreach --------------------------------
def test_strong_claim_inferential_support_downgrades_and_overstates() -> None:
    verdict, fired = _run(
        claim="All deployments pass the security review.",
        features=_features(has_universal_quantifier=True),
        passages=[Passage(passage_id="p-1", text="Deployments generally pass review.")],
    )
    assert verdict.support_verdict == "partially_supported"
    assert "overstated" in verdict.audit_flags
    assert "C6b_strength_scope" in _ids(fired)


def test_strong_claim_over_partial_evidence_is_overstated() -> None:
    verdict, fired = _run(
        claim="Every record must be encrypted.",
        features=_features(modal_strength="prescribes"),
        support_signal=SupportSignal(
            label="entail", max_entailment_score=0.55, contributing_passage_id="p-1"
        ),
        passages=[Passage(passage_id="p-1", text="Records are usually encrypted.")],
    )
    assert verdict.support_verdict == "partially_supported"
    assert "overstated" in verdict.audit_flags
    assert "C6b_strength_scope" in _ids(fired)


def test_strong_claim_with_equal_strength_support_is_not_overstated() -> None:
    # The passage carries its own universal scope ("All") → equal strength,
    # no overreach (Decision F2: passage-strong suppresses).
    claim = "All deployments pass the security review."
    verdict, fired = _run(
        claim=claim,
        features=_features(has_universal_quantifier=True),
        passages=[Passage(passage_id="p-1", text=claim)],
    )
    assert verdict.support_verdict == "supported"
    assert "overstated" not in verdict.audit_flags
    assert "C6b_strength_scope" not in _ids(fired)


def test_strong_claim_over_plain_assertive_evidence_is_not_overstated() -> None:
    # Decision F2 regression (the review probe's false downgrade): descriptive
    # practice grounding a prescriptive claim is packet-relative support — a
    # passage with NO weakness markers must not trigger the downgrade, however
    # non-verbatim the paraphrase is.
    verdict, fired = _run(
        claim="All deviation reports must be approved by the quality unit.",
        features=_features(has_universal_quantifier=True, modal_strength="prescribes"),
        passages=[Passage(passage_id="p-1", text="The quality unit approves deviation reports.")],
    )
    assert verdict.support_verdict == "supported"
    assert "overstated" not in verdict.audit_flags
    assert "C6b_strength_scope" not in _ids(fired)


def test_weak_deontic_claim_is_not_strong_for_6b() -> None:
    # `should` moved to the weak-deontic set: a should-claim is not an
    # overreaching claim even over hedged evidence (trace modal_strength stays
    # `prescribes`; only 6b's strength comparison changed).
    verdict, fired = _run(
        claim="Records should be reviewed by the site lead.",
        features=_features(modal_strength="prescribes"),
        passages=[Passage(passage_id="p-1", text="Records are usually reviewed by a site lead.")],
    )
    assert verdict.support_verdict == "supported"
    assert "overstated" not in verdict.audit_flags
    assert "C6b_strength_scope" not in _ids(fired)


# --- Phase C 6c: inferred --------------------------------------------------
def test_inferred_flag_when_support_is_not_verbatim() -> None:
    verdict, fired = _run(
        claim="The platform encrypts stored records.",
        passages=[
            Passage(passage_id="p-1", text="Data is protected with storage-level cryptography.")
        ],
    )
    assert verdict.support_verdict == "supported"
    assert "inferred" in verdict.audit_flags
    assert "C6c_inferred" in _ids(fired)


def test_no_inferred_flag_when_support_is_verbatim() -> None:
    verdict, _ = _run()
    assert "inferred" not in verdict.audit_flags


# --- Phase C 6d: source-scope ----------------------------------------------
def test_source_scope_error_flag_for_background_passage() -> None:
    verdict, fired = _run(
        passages=[
            Passage(
                passage_id="p-1",
                text="The platform validates submitted input records.",
                source_meta={"trust_level": "background"},
            )
        ]
    )
    assert verdict.support_verdict == "supported"
    assert "source_scope_error" in verdict.audit_flags
    assert "C6d_source_scope" in _ids(fired)


# --- Decision H: eligibility suppression loop (P1 / P2) ---------------------
def _er(passage_id: str, label: EntailLabel, score: float) -> EntailResult:
    return EntailResult(passage_id=passage_id, label=label, score=score, raw_logits=(0.0, 0.0, 0.0))


_BACKGROUND = {"trust_level": "background"}
_PRIMARY = {"trust_level": "primary"}


def test_p1_suppresses_ineligible_contradiction_so_eligible_entail_wins() -> None:
    # c016 shape: a background source contradicts louder than a primary source
    # entails. P1 refuses the ineligible solo-decision; the eligible entail wins.
    verdict, fired = _run(
        claim="The guidance addresses supplier audit timing.",
        passages=[
            Passage(passage_id="bg", text="No fixed timing is imposed.", source_meta=_BACKGROUND),
            Passage(
                passage_id="prim",
                text="The guidance addresses supplier audit timing.",
                source_meta=_PRIMARY,
            ),
        ],
        retrieval=[
            RetrievalResult(passage_id="bg", score=0.90),
            RetrievalResult(passage_id="prim", score=0.90),
        ],
        support_signal=SupportSignal(
            label="contradict", max_entailment_score=0.99, contributing_passage_id="bg"
        ),
        entailment=[_er("bg", "contradict", 0.99), _er("prim", "entail", 0.95)],
    )
    assert verdict.support_verdict == "supported"
    assert "P1_eligibility_suppressed" in _ids(fired)
    assert "A4_hard_contradiction" not in _ids(fired)


def test_p1_lands_not_checkable_when_only_signal_is_ineligible() -> None:
    # c008 shape: the only non-neutral signal is an ineligible contradiction. P1
    # suppresses it and, with nothing eligible left, the verdict lands off-scale.
    #
    # The subject is deliberately a system rather than a document. The original
    # fixture said "The guidance does not prescribe...", which cal-rules-v1.10.0
    # classifies as a source-coverage claim, so A6 would gate the adverse degree
    # before P1 ever ran and this test would silently stop exercising P1. The
    # A6/P1 ordering is pinned by its own test below.
    verdict, fired = _run(
        claim="The platform does not enforce a fixed interval.",
        features=_features(has_explicit_negation=True),
        passages=[
            Passage(
                passage_id="bg", text="A fixed 30-day interval applies.", source_meta=_BACKGROUND
            )
        ],
        retrieval=[RetrievalResult(passage_id="bg", score=0.90)],
        support_signal=SupportSignal(
            label="contradict", max_entailment_score=0.99, contributing_passage_id="bg"
        ),
        entailment=[_er("bg", "contradict", 0.99)],
    )
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "no_entail_signal"
    assert "P1_eligibility_suppressed" in _ids(fired)


def test_p2_absence_mirror_suppresses_self_negating_contradiction() -> None:
    # A negated claim whose eligible contradicting passage itself expresses the
    # negation AGREES with the claim (MoNLI double-negation); P2 suppresses it so
    # a same-negation passage cannot drive a contradiction.
    verdict, fired = _run(
        claim="The product does not contain latex.",
        features=_features(has_explicit_negation=True),
        passages=[
            Passage(passage_id="prim", text="The product is latex-free.", source_meta=_PRIMARY)
        ],
        retrieval=[RetrievalResult(passage_id="prim", score=0.90)],
        support_signal=SupportSignal(
            label="contradict", max_entailment_score=0.98, contributing_passage_id="prim"
        ),
        entailment=[_er("prim", "contradict", 0.98)],
    )
    assert "P2_absence_mirror_suppressed" in _ids(fired)
    assert verdict.support_verdict != "contradicted"


# --- Phase C 6f: false caution ---------------------------------------------
def test_false_caution_flag_when_hedged_claim_is_strongly_supported() -> None:
    claim = "The platform may validate submitted input records."
    verdict, fired = _run(
        claim=claim,
        features=_features(modal_strength="hedges"),
        passages=[Passage(passage_id="p-1", text=claim)],
    )
    assert verdict.support_verdict == "supported"
    assert "false_caution" in verdict.audit_flags
    assert "C6f_false_caution" in _ids(fired)


# --- Phase C composition rule ----------------------------------------------
def test_composition_contradicted_is_terminal_over_6b_downgrade() -> None:
    # 6a sets contradicted (numeric crux) AND 6b proposes partial (universal
    # claim over weaker-scoped evidence): the most-adverse rule keeps it
    # contradicted; `overstated` survives the adverse-degree flag guard.
    verdict, fired = _run(
        claim="All releases hit 99 percent uptime.",
        features=_features(
            has_universal_quantifier=True,
            numerical_values=[Quantity(value=99.0, unit="percentage", surface_text="99 percent")],
        ),
        passages=[Passage(passage_id="p-1", text="Releases typically hit 95 percent uptime.")],
    )
    assert verdict.support_verdict == "contradicted"
    assert "overstated" in verdict.audit_flags
    assert {"C6a_numeric", "C6b_strength_scope"} <= _ids(fired)


def test_flag_guard_drops_support_flags_on_adverse_final_degree() -> None:
    # Decision F6: a numeric-crux contradiction with a hedged, non-verbatim claim
    # would otherwise carry `inferred` + `false_caution` — both presuppose
    # support and are dropped once the final degree is adverse.
    verdict, fired = _run(
        claim="The measured yield was likely 90 percent overall.",
        features=_features(
            modal_strength="hedges",
            numerical_values=[Quantity(value=90.0, unit="percentage", surface_text="90 percent")],
        ),
        passages=[Passage(passage_id="p-1", text="The final yield measured 70 percent.")],
    )
    assert verdict.support_verdict == "contradicted"
    assert verdict.audit_flags == []
    assert {"C6a_numeric", "C6c_inferred", "C6f_false_caution"} <= _ids(fired)


# --- Cross-cutting guarantees ----------------------------------------------
def test_every_support_verdict_label_is_producible() -> None:
    produced = {
        _run()[0].support_verdict,  # supported
        _run(
            support_signal=SupportSignal(
                label="entail", max_entailment_score=0.55, contributing_passage_id="p-1"
            )
        )[0].support_verdict,  # partially_supported
        _run(
            support_signal=SupportSignal(
                label="contradict", max_entailment_score=0.50, contributing_passage_id="p-1"
            )
        )[0].support_verdict,  # unsupported
        _run(
            support_signal=SupportSignal(
                label="contradict", max_entailment_score=0.90, contributing_passage_id="p-1"
            )
        )[0].support_verdict,  # contradicted
        _run(
            support_signal=SupportSignal(
                label="neutral", max_entailment_score=0.0, contributing_passage_id=None
            )
        )[0].support_verdict,  # not_checkable
    }
    assert produced == {
        "supported",
        "partially_supported",
        "unsupported",
        "contradicted",
        "not_checkable",
    }


def test_every_verdict_records_at_least_one_rule() -> None:
    for signal in (
        SupportSignal(label="entail", max_entailment_score=0.90, contributing_passage_id="p-1"),
        SupportSignal(label="neutral", max_entailment_score=0.0, contributing_passage_id=None),
    ):
        _, fired = _run(support_signal=signal)
        assert len(fired) >= 1


def test_apply_rejects_config_pinned_to_a_different_rules_file() -> None:
    mismatched = VerdictRules(rules_file_sha="0" * 64)
    with pytest.raises(ValueError, match="different rules file"):
        _run(rules=mismatched)


# --- D2: A3 over bound instantiation (cal-rules-v1.8.0) ---


def test_negation_backstop_suppressed_over_bound_instantiation() -> None:
    # A negated *consequence* instantiating a stated bound follows correctly
    # from a positively-stated rule, which need not express any negation. A3's
    # mirror test has no valid operator over a bound, so it stands down.
    verdict, fired = _run(
        claim="A batch below 40% yield cannot pass release.",
        features=_features(
            has_explicit_negation=True,
            numerical_values=[Quantity(value=40.0, unit=None, surface_text="40%")],
        ),
        passages=[
            Passage(passage_id="p-1", text="Batches must achieve at least 40% yield to pass.")
        ],
    )
    assert verdict.support_verdict == "supported"
    assert "A3_negation_backstop" not in _ids(fired)
    assert "A3_bound_instantiation_suppressed" in _ids(fired)


def test_negation_backstop_still_fires_when_claim_carries_no_quantity() -> None:
    # The suppression is narrow by construction: without a claim quantity there
    # is no bound instantiation, so A3's MoNLI purpose is untouched.
    verdict, fired = _run(
        claim="The system does not validate inputs.",
        features=_features(has_explicit_negation=True),
        passages=[
            Passage(passage_id="p-1", text="The system validates inputs, up to a maximum of 5.")
        ],
    )
    assert verdict.support_verdict == "contradicted"
    assert "A3_negation_backstop" in _ids(fired)


def test_negation_backstop_still_fires_over_a_stated_value() -> None:
    # Passage states a value, not a bound → A3's operator is valid, no suppression.
    verdict, fired = _run(
        claim="The cycle does not run for 6 hours.",
        features=_features(
            has_explicit_negation=True,
            numerical_values=[Quantity(value=6.0, unit="hour", surface_text="6 hours")],
        ),
        passages=[Passage(passage_id="p-1", text="The cycle runs for 6 hours.")],
    )
    assert verdict.support_verdict == "contradicted"
    assert "A3_negation_backstop" in _ids(fired)


# --- A5: conflicting evidence (cal-rules-v1.9.0, D9) -----------------------
# The aggregator reports one label — the strongest position any passage takes.
# When two different passages take opposite positions and both clear their
# thresholds, that label is whichever scored higher, by a margin that carries no
# information about which passage governs. A5 refuses to resolve it by score.


def _two_sided(*, entail: float, contradict: float, label: EntailLabel) -> SupportSignal:
    """A signal whose two channels disagree, as the real aggregator records it."""
    top = entail if label == "entail" else contradict
    return SupportSignal(
        label=label,
        max_entailment_score=top,
        contributing_passage_id="p-1" if label == "entail" else "p-2",
        best_entail=entail,
        best_entail_passage_id="p-1",
        best_contradict=contradict,
        best_contradict_passage_id="p-2",
    )


def _two_passages() -> tuple[list[Passage], list[RetrievalResult]]:
    return (
        [
            Passage(passage_id="p-1", text="The platform validates submitted input records."),
            Passage(passage_id="p-2", text="The platform discards submitted input records."),
        ],
        [
            RetrievalResult(passage_id="p-1", score=0.90),
            RetrievalResult(passage_id="p-2", score=0.88),
        ],
    )


def test_a5_abstains_when_both_channels_clear_their_thresholds() -> None:
    passages, retrieval = _two_passages()
    verdict, fired = _run(
        passages=passages,
        retrieval=retrieval,
        support_signal=_two_sided(entail=0.948, contradict=0.964, label="contradict"),
    )
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "conflicting_evidence"
    assert "A5_conflicting_evidence" in _ids(fired)
    # Both passages must be named: the point of the abstention is that a human
    # has to read them, so an explanation that cites one is not actionable.
    reason = next(r.reason for r in fired if r.rule_id == "A5_conflicting_evidence")
    assert "p-1" in reason and "p-2" in reason


def test_a5_fires_in_the_entail_direction_too() -> None:
    """The false-`supported` direction is the expensive one, and A5 covers it.

    With the entail channel on top the aggregated label is ``entail``, which
    would otherwise reach the degree mapping and land ``supported`` on a claim a
    second admitted passage refutes above threshold.
    """
    passages, retrieval = _two_passages()
    verdict, fired = _run(
        passages=passages,
        retrieval=retrieval,
        support_signal=_two_sided(entail=0.964, contradict=0.948, label="entail"),
    )
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "conflicting_evidence"
    assert "A5_conflicting_evidence" in _ids(fired)
    assert "B5_degree" not in _ids(fired)


@pytest.mark.parametrize(
    ("entail", "contradict"),
    [(0.948, 0.60), (0.60, 0.964), (0.60, 0.60)],
    ids=["only-entail-clears", "only-contradict-clears", "neither-clears"],
)
def test_a5_stands_down_unless_both_channels_clear(entail: float, contradict: float) -> None:
    passages, retrieval = _two_passages()
    label: EntailLabel = "entail" if entail >= contradict else "contradict"
    _, fired = _run(
        passages=passages,
        retrieval=retrieval,
        support_signal=_two_sided(entail=entail, contradict=contradict, label=label),
    )
    assert "A5_conflicting_evidence" not in _ids(fired)


def test_a5_stands_down_when_the_channels_were_never_measured() -> None:
    """A trace written before the channels existed must not be read as agreement."""
    _, fired = _run(
        support_signal=SupportSignal(
            label="contradict", max_entailment_score=0.95, contributing_passage_id="p-1"
        )
    )
    assert "A5_conflicting_evidence" not in _ids(fired)


# --- A7: disjoint location phrases may not solo-decide a contradiction -----

_A7_CLAIM = "Packaging sites shall record deviations within two hours."
_A7_PASSAGE = (
    "At the Building 4 manufacturing site, an excursion from a validated "
    "process parameter shall be recorded as a deviation within one business "
    "day of detection."
)


def test_a7_stands_down_a_disjoint_site_contradiction() -> None:
    verdict, fired = _run(
        claim=_A7_CLAIM,
        passages=[Passage(passage_id="p-1", text=_A7_PASSAGE)],
        support_signal=SupportSignal(
            label="contradict",
            max_entailment_score=0.80,
            contributing_passage_id="p-1",
        ),
    )
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "out_of_scope"
    assert "A7_scope_mismatch" in _ids(fired)
    assert "A4_hard_contradiction" not in _ids(fired)
    reason = next(r.reason for r in fired if r.rule_id == "A7_scope_mismatch")
    assert "which" in reason.lower()


def test_a7_does_not_stand_down_a_subject_level_contradiction() -> None:
    """Relocation vs requalification is a real contradiction, not a site clash."""
    claim = "Relocation of qualified equipment does not require requalification."
    passage = (
        "Requalification shall be performed following any change that affects "
        "the qualified state, including relocation, major repair, or modification "
        "of a critical component."
    )
    verdict, fired = _run(
        claim=claim,
        passages=[Passage(passage_id="p-1", text=passage)],
        support_signal=SupportSignal(
            label="contradict",
            max_entailment_score=0.99,
            contributing_passage_id="p-1",
        ),
    )
    assert "A7_scope_mismatch" not in _ids(fired)
    assert verdict.support_verdict == "contradicted"
    assert "A4_hard_contradiction" in _ids(fired)


def test_a7_does_not_stand_down_a_same_site_contradiction() -> None:
    claim = (
        "At the Building 4 manufacturing site, an excursion shall be recorded "
        "within five business days of detection."
    )
    _, fired = _run(
        claim=claim,
        passages=[Passage(passage_id="p-1", text=_A7_PASSAGE)],
        support_signal=SupportSignal(
            label="contradict",
            max_entailment_score=0.96,
            contributing_passage_id="p-1",
        ),
    )
    assert "A7_scope_mismatch" not in _ids(fired)


# --- A4: the negation probe needs standing to veto (cal-rules-v1.9.0, D10) ---


_PROBE_LOGITS: dict[EntailLabel, tuple[float, float, float]] = {
    "entail": (2.0, -1.0, -1.0),
    "neutral": (0.0, 0.0, 0.0),
    "contradict": (-1.0, -1.0, 2.0),
}


def _probe(label: EntailLabel, score: float, *, passage_id: str = "p-1") -> NegationProbe:
    return NegationProbe(
        negated_claim="The platform does not validate submitted input records.",
        abstained=False,
        result=EntailResult(
            passage_id=passage_id,
            label=label,
            score=score,
            raw_logits=_PROBE_LOGITS[label],
        ),
    )


def _contradiction_signal(score: float) -> SupportSignal:
    return SupportSignal(
        label="contradict", max_entailment_score=score, contributing_passage_id="p-1"
    )


def test_a4_demotes_when_the_probe_is_at_least_as_confident() -> None:
    """The PILOT-001 c009 shape — primary 0.766, probe neutral 0.996 — still demotes."""
    verdict, fired = _run(
        support_signal=_contradiction_signal(0.766),
        negation_probe=_probe("neutral", 0.996),
    )
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "no_entail_signal"
    assert "A4_negation_consistency" in _ids(fired)


def test_a4_does_not_demote_on_a_probe_less_confident_than_the_contradiction() -> None:
    """The construction-corpus shape — primary 0.995, probe neutral 0.43.

    A second reading of a machine-negated sentence, at a confidence the primary
    measurement beats by half, is not evidence the primary is spurious.
    """
    verdict, fired = _run(
        support_signal=_contradiction_signal(0.995),
        negation_probe=_probe("neutral", 0.43),
    )
    assert verdict.support_verdict == "contradicted"
    assert "A4_negation_consistency" not in _ids(fired)
    assert "A4_hard_contradiction" in _ids(fired)


def test_a4_records_the_probe_it_disregarded() -> None:
    """A non-firing that leaves no trace is a non-firing nobody can audit."""
    _, fired = _run(
        support_signal=_contradiction_signal(0.995),
        negation_probe=_probe("neutral", 0.43),
    )
    assert "A4_negation_probe_uninformative" in _ids(fired)
    reason = next(r.reason for r in fired if r.rule_id == "A4_negation_probe_uninformative")
    assert "0.43" in reason and "0.99" in reason


def test_a4_demotes_on_an_exactly_equal_probe() -> None:
    """The boundary is inclusive: an equally confident probe still has standing."""
    verdict, fired = _run(
        support_signal=_contradiction_signal(0.90),
        negation_probe=_probe("neutral", 0.90),
    )
    assert verdict.support_verdict == "not_checkable"
    assert "A4_negation_consistency" in _ids(fired)


def test_a4_ignores_a_probe_computed_against_a_different_premise() -> None:
    verdict, fired = _run(
        support_signal=_contradiction_signal(0.80),
        negation_probe=_probe("neutral", 0.99, passage_id="p-2"),
    )
    assert verdict.support_verdict == "contradicted"
    assert "A4_negation_consistency" not in _ids(fired)
    assert "A4_negation_probe_uninformative" not in _ids(fired)


# --- A6: a claim about what a document does not say (cal-rules-v1.10.0, D11) ---
# Silence in the bundle is exactly what such a claim asserts, so passages
# excerpted from that document cannot refute it. The gate is claim-side and
# structural — it never compares claim terms to passage terms, which Decision F
# forbids from deciding a degree.

_COVERAGE_CLAIM = "The procedure does not cover deviations detected after batch release."
_OBJECT_CLAIM = "Relocation of qualified equipment does not require requalification."


def _refuting(score: float = 0.98) -> SupportSignal:
    return SupportSignal(
        label="contradict", max_entailment_score=score, contributing_passage_id="p-1"
    )


def test_a6_withholds_the_adverse_verdict_on_a_source_coverage_claim() -> None:
    verdict, fired = _run(
        claim=_COVERAGE_CLAIM,
        features=_features(has_explicit_negation=True),
        passages=[
            Passage(
                passage_id="p-1",
                text=(
                    "A deviation classified as critical shall trigger a Quality Hold on "
                    "the affected batch until the investigation is closed."
                ),
            )
        ],
        support_signal=_refuting(),
    )
    # The landing is emergent, exactly as P1's and P2's are: the contributing
    # passage is dropped, the pool re-aggregates, and an empty pool falls out of
    # B5. The rule id carries the specificity, so a reviewer can still see which
    # gate withheld the verdict.
    assert verdict.support_verdict == "not_checkable"
    assert verdict.support_verdict_reason == "no_entail_signal"
    assert "A6_absence_not_decidable" in _ids(fired)
    assert "A4_hard_contradiction" not in _ids(fired)


def test_a6_leaves_an_object_level_negated_claim_refutable() -> None:
    """The discriminator has to keep true contradictions, or it is just suppression."""
    verdict, fired = _run(
        claim=_OBJECT_CLAIM,
        features=_features(has_explicit_negation=True),
        passages=[
            Passage(
                passage_id="p-1",
                text=(
                    "Requalification shall be performed following any change that affects "
                    "the qualified state, including relocation, major repair, or "
                    "modification of a critical component."
                ),
            )
        ],
        support_signal=_refuting(0.99),
    )
    assert verdict.support_verdict == "contradicted"
    assert "A6_absence_not_decidable" not in _ids(fired)


@pytest.mark.parametrize(
    ("claim", "gated"),
    [
        ("The guidance does not address retention sample storage.", True),
        # Document subject, but an object-level predicate a passage can refute.
        ("The guidance does not apply to biologics.", False),
        # Coverage predicate, but the subject is a thing, not a text.
        ("The final formulation does not contain animal-derived ingredients.", False),
    ],
    ids=["document+coverage", "document+object-verb", "object+coverage-verb"],
)
def test_a6_requires_both_a_document_subject_and_a_coverage_predicate(
    claim: str, gated: bool
) -> None:
    """Either condition alone over-fires, so both are load-bearing."""
    _, fired = _run(
        claim=claim,
        features=_features(has_explicit_negation=True),
        passages=[Passage(passage_id="p-1", text="Retention samples are stored at 25 degrees.")],
        support_signal=_refuting(),
    )
    assert ("A6_absence_not_decidable" in _ids(fired)) is gated


def test_a6_does_not_touch_a_supported_verdict() -> None:
    """The gate withholds adverse verdicts only; it must not suppress support."""
    verdict, fired = _run(
        claim=_COVERAGE_CLAIM,
        features=_features(has_explicit_negation=True),
        passages=[Passage(passage_id="p-1", text="The procedure covers no post-release work.")],
        support_signal=SupportSignal(
            label="entail", max_entailment_score=0.95, contributing_passage_id="p-1"
        ),
    )
    assert verdict.support_verdict == "supported"
    assert "A6_absence_not_decidable" not in _ids(fired)


def test_a6_exhaustive_coverage_claim_is_supported() -> None:
    """A complete source that is silent on a coverage claim supports the absence."""
    verdict, fired = _run(
        claim=_COVERAGE_CLAIM,
        features=_features(has_explicit_negation=True),
        passages=[
            Passage(
                passage_id="p-1",
                text=(
                    "A deviation classified as critical shall trigger a Quality Hold on "
                    "the affected batch until the investigation is closed."
                ),
            )
        ],
        support_signal=_refuting(),
        source_boundary="exhaustive",
    )
    assert verdict.support_verdict == "supported"
    assert "A6_absence_decidable" in _ids(fired)
    assert "A6_absence_not_decidable" not in _ids(fired)


def test_a6_exhaustive_complement_entailment_refutes_absence() -> None:
    verdict, fired = _run(
        claim=_COVERAGE_CLAIM,
        features=_features(has_explicit_negation=True),
        passages=[Passage(passage_id="p-1", text="The procedure covers post-release deviations.")],
        support_signal=_refuting(),
        source_boundary="exhaustive",
        absence_complement_entailed=True,
    )
    assert verdict.support_verdict == "contradicted"
    assert "A6_absence_refuted" in _ids(fired)


def test_a6_named_gap_is_contradicted() -> None:
    verdict, fired = _run(
        claim="The guidance does not address storage conditions for retention samples.",
        features=_features(has_explicit_negation=True),
        passages=[Passage(passage_id="p-1", text="Long-term testing covers 12 months.")],
        support_signal=_refuting(),
        source_boundary="named_missing_material",
        claimed_material_is_a_named_gap=True,
    )
    assert verdict.support_verdict == "contradicted"
    assert "A6_named_gap_present" in _ids(fired)


def test_a6_bounded_coverage_claim_still_withholds() -> None:
    verdict, fired = _run(
        claim=_COVERAGE_CLAIM,
        features=_features(has_explicit_negation=True),
        passages=[
            Passage(
                passage_id="p-1",
                text=(
                    "A deviation classified as critical shall trigger a Quality Hold on "
                    "the affected batch until the investigation is closed."
                ),
            )
        ],
        support_signal=_refuting(),
        source_boundary="bounded",
    )
    assert verdict.support_verdict == "not_checkable"
    assert "A6_absence_not_decidable" in _ids(fired)


def test_a6_does_not_short_circuit_the_eligibility_loop() -> None:
    """A6 suppresses and re-aggregates; it must not terminate the loop.

    This is the property that PILOT-001 `c002` bought. As a terminal verdict, A6
    landed `not_checkable` by pre-empting the P1 drop that recovers a
    `partially_supported` — against a human gold of `supported`, strictly worse.
    Here P1 is checked first and still governs, so the recovery path survives.
    """
    verdict, fired = _run(
        claim="The guidance does not prescribe a fixed interval.",
        features=_features(has_explicit_negation=True),
        passages=[
            Passage(
                passage_id="bg", text="A fixed 30-day interval applies.", source_meta=_BACKGROUND
            )
        ],
        retrieval=[RetrievalResult(passage_id="bg", score=0.90)],
        support_signal=SupportSignal(
            label="contradict", max_entailment_score=0.99, contributing_passage_id="bg"
        ),
        entailment=[_er("bg", "contradict", 0.99)],
    )
    assert verdict.support_verdict == "not_checkable"
    assert "P1_eligibility_suppressed" in _ids(fired)
    assert "B5_degree" in _ids(fired)
