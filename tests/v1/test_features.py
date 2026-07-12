"""Behaviour tests for the v1 deterministic feature extractors.

Edge cases are drawn from phases/phase-1-deterministic-core.md § Unit 1 and
the input-contract ADR. The point is the *scope* discipline — clause-level vs
constituent negation, subject-scoped vs object quantifiers — not just keyword
presence.
"""

from __future__ import annotations

from claim_audit_lab.v1 import features
from claim_audit_lab.v1.features import FeatureExtractor
from claim_audit_lab.v1.impl.features import DefaultFeatureExtractor
from claim_audit_lab.v1.models import ExtractedFeatures


# --- has_numerical_value ---------------------------------------------------
def test_numeric_percent_forms_collapse() -> None:
    for text in ("A 5% reduction was observed.", "A 5 percent reduction was observed."):
        qs = features.has_numerical_value(text)
        assert len(qs) == 1
        assert qs[0].value == 5.0


def test_numeric_decimal() -> None:
    qs = features.has_numerical_value("The rate is 0.05 of the total.")
    assert any(q.value == 0.05 for q in qs)


def test_numeric_none() -> None:
    assert features.has_numerical_value("No numeric value appears in this sentence.") == []


def test_numeric_multiple() -> None:
    qs = features.has_numerical_value("There were 3 errors and 7 warnings.")
    values = {q.value for q in qs}
    assert {3.0, 7.0} <= values


def test_numeric_range_collapses_to_one() -> None:
    # quantulum3 treats "between X and Y" as a single (averaged) range quantity.
    qs = features.has_numerical_value("Levels rose between 5% and 10%.")
    assert len(qs) == 1


def test_no_classifier_mode_is_forced() -> None:
    # Core guard: CAL pins quantulum3 to deterministic no-classifier mode rather
    # than its bundled ML unit classifier, which runs under a version-mismatched
    # scikit-learn that the library flags as possibly invalid. Importing
    # v1.features sets this flag. See DECISIONS.md § Phase 1 Unit 3 (addendum).
    from quantulum3 import classifier as q3_classifier

    assert q3_classifier.USE_CLF is False


def test_numeric_ambiguous_unit_value_is_correct_and_deterministic() -> None:
    # Ambiguous unit surfaces ("mg/kg") route through quantulum3's unit
    # disambiguation. In no-classifier mode the value CAL actually uses (rule 6a)
    # parses correctly and is byte-identical across runs.
    claim = "The dose was 5 mg/kg."
    first = features.has_numerical_value(claim)
    assert [q.value for q in first] == [5.0]
    assert features.has_numerical_value(claim) == first


def test_numeric_ambiguous_unit_volume() -> None:
    qs = features.has_numerical_value("The reaction produced 250 mL of solution.")
    assert any(q.value == 250.0 for q in qs)


def test_numeric_unit_phrase_recovers_value() -> None:
    # "900 records per hour" surfaced the fragility during B9 probing; the value
    # (the only thing rule 6a uses) parses cleanly in no-classifier mode.
    qs = features.has_numerical_value("The system processes 900 records per hour.")
    assert any(q.value == 900.0 for q in qs)


# --- has_explicit_negation -------------------------------------------------
def test_negation_clause_level_true() -> None:
    assert features.has_explicit_negation("The system does not validate.") is True


def test_negation_cannot_true() -> None:
    assert features.has_explicit_negation("It cannot be shown that X holds.") is True


def test_negation_constituent_false() -> None:
    # "not" scopes the quantifier/subject, not the clause verb.
    assert features.has_explicit_negation("Not all systems pass.") is False


def test_negation_lexical_false() -> None:
    # "unable" is lexical negation, not a syntactic neg edge.
    assert features.has_explicit_negation("The system is unable to validate.") is False


def test_negation_plain_false() -> None:
    assert features.has_explicit_negation("The system validates inputs.") is False


# --- has_universal_quantifier ----------------------------------------------
def test_quantifier_subject_true() -> None:
    assert features.has_universal_quantifier("All systems pass.") is True


def test_quantifier_object_false() -> None:
    assert features.has_universal_quantifier("We test all systems.") is False


def test_quantifier_adverb_true() -> None:
    assert features.has_universal_quantifier("The log is never updated.") is True


def test_quantifier_no_determiner_true() -> None:
    assert features.has_universal_quantifier("No defects were found.") is True


def test_quantifier_absent_false() -> None:
    assert features.has_universal_quantifier("The system passes its checks.") is False


# --- has_modal_strength ----------------------------------------------------
def test_modal_asserts() -> None:
    assert features.has_modal_strength("The system is compliant.") == "asserts"


def test_modal_hedges_may() -> None:
    assert features.has_modal_strength("The system may be compliant.") == "hedges"


def test_modal_hedges_likely() -> None:
    assert features.has_modal_strength("The result is likely correct.") == "hedges"


def test_modal_prescribes_must() -> None:
    assert features.has_modal_strength("The system must be validated.") == "prescribes"


def test_modal_prescribes_required() -> None:
    assert features.has_modal_strength("The vendor is required to audit suppliers.") == "prescribes"


def test_modal_prescribes_should() -> None:
    assert features.has_modal_strength("The system should be validated.") == "prescribes"


# --- claim_token_count -----------------------------------------------------
def test_token_count_positive() -> None:
    assert features.claim_token_count("The system validates inputs.") >= 4


def test_token_count_within_input_contract_bound() -> None:
    # The PILOT-001 packet sits inside 5–80 tokens; a normal claim is well within.
    n = features.claim_token_count("Equipment qualification and calibration are mandated.")
    assert 5 <= n <= 80


# --- is_compound_claim -----------------------------------------------------
def test_compound_true() -> None:
    assert features.is_compound_claim("Trend analysis and monitoring are involved.") is True


def test_compound_false() -> None:
    assert features.is_compound_claim("Senior management evaluates improvement processes.") is False


# --- sentence_type ---------------------------------------------------------
def test_sentence_type_opinion() -> None:
    assert features.sentence_type("I think the system works well.") == "opinion"


def test_sentence_type_question() -> None:
    assert features.sentence_type("Does the system validate inputs?") == "question"


def test_sentence_type_imperative() -> None:
    assert features.sentence_type("Validate the system before release.") == "imperative"


def test_sentence_type_declarative() -> None:
    assert features.sentence_type("The system validates inputs.") == "declarative"


def test_sentence_type_opinion_is_token_aware_not_substring() -> None:
    # "to me" / "i feel" must not fire inside "to meet" / "to measure" / "feels".
    assert features.sentence_type("We need to meet the requirement.") == "declarative"
    assert features.sentence_type("The system has to measure latency.") == "declarative"
    assert features.sentence_type("Sushi feels fresh today.") == "declarative"


def test_sentence_type_opinion_phrase_still_matches() -> None:
    assert features.sentence_type("According to me, the system works.") == "opinion"


def test_sentence_type_pii_claim_is_audited_not_opinion() -> None:
    # 20_live finance claims mention "personally identifiable information";
    # `personally` was dropped from the lexicon so these stay in scope to be
    # audited, not routed to out_of_scope. See plans/adr-v1-lexicons.md.
    for claim in (
        "Personally identifiable information must be encrypted.",
        "The system stores personally identifiable information.",
    ):
        assert features.sentence_type(claim) == "declarative"


# --- DefaultFeatureExtractor -----------------------------------------------
def test_extractor_satisfies_protocol() -> None:
    assert isinstance(DefaultFeatureExtractor(), FeatureExtractor)


def test_extractor_composes_all_features() -> None:
    feats = DefaultFeatureExtractor().extract("All vendors must report 5% deviations and audits.")
    assert isinstance(feats, ExtractedFeatures)
    assert feats.has_universal_quantifier is True
    assert feats.modal_strength == "prescribes"
    assert feats.compound_claim is True
    assert any(q.value == 5.0 for q in feats.numerical_values)
    assert feats.sentence_type == "declarative"


def test_extractor_is_deterministic() -> None:
    claim = "The packet does not establish support for several claims."
    assert DefaultFeatureExtractor().extract(claim) == DefaultFeatureExtractor().extract(claim)


# --- Decision F extractors (adr-v1-rules-v1.4.0-semantic-fixes.md) -----------
def test_expresses_negation_clause_level() -> None:
    assert features.expresses_negation("The system does not validate inputs.") is True


def test_expresses_negation_constituent_det_no() -> None:
    assert features.expresses_negation("The product contains no latex.") is True


def test_expresses_negation_absence_lexemes() -> None:
    assert features.expresses_negation("The product is shipped without preservatives.") is True
    assert features.expresses_negation("The absence of latex was confirmed.") is True
    assert features.expresses_negation("The kit lacks a calibration standard.") is True


def test_expresses_negation_free_forms() -> None:
    assert features.expresses_negation("The product is latex-free.") is True
    assert features.expresses_negation("The formulation is free of latex.") is True
    # Bare `free` is never an absence marker (Decision F interpretation 3).
    assert features.expresses_negation("The free tier includes reporting.") is False


def test_expresses_negation_plain_false() -> None:
    assert features.expresses_negation("The system validates inputs.") is False


def test_deontic_strength_split() -> None:
    assert features.deontic_strength("Records must be retained.") == "strong"
    assert features.deontic_strength("The SOP requires sign-off.") == "strong"
    assert features.deontic_strength("Records should be retained.") == "weak"
    assert features.deontic_strength("We recommend retaining records.") == "weak"
    assert features.deontic_strength("Records are retained.") is None


def test_should_stays_prescribes_in_the_trace() -> None:
    # The deontic split feeds only 6b; the trace's modal_strength is unchanged.
    assert features.has_modal_strength("Records should be retained.") == "prescribes"


def test_scope_strength_strong_weak_none() -> None:
    assert features.scope_strength("All records shall be kept.") == "strong"
    assert features.scope_strength("Records are usually encrypted.") == "weak"
    assert features.scope_strength("Some batches passed early.") == "weak"
    assert features.scope_strength("Records may be archived.") == "weak"
    assert features.scope_strength("The unit approves reports.") is None


def test_scope_strength_strong_wins_over_weak() -> None:
    assert features.scope_strength("All records are usually encrypted.") == "strong"


def test_approximation_marker() -> None:
    assert features.has_approximation_marker("Approximately 40 percent showed uptake.") is True
    assert features.has_approximation_marker("Roughly half the sites responded.") is True
    assert features.has_approximation_marker("The rate was 40 percent.") is False


def test_content_lemma_set_unifies_inflection_and_drops_function_words() -> None:
    assert features.content_lemma_set("All deviation reports must be approved.") == {
        "approve",
        "deviation",
        "report",
    }
    # The v0.2 light_stem failure pair unifies under lemmas.
    assert features.content_lemma_set("approved") == features.content_lemma_set("approves")


def test_content_lemma_set_excludes_numerals() -> None:
    assert "40" not in features.content_lemma_set("Uptake was 40 percent.")
    assert "percent" in features.content_lemma_set("Uptake was 40 percent.")
