"""Behaviour tests for the v1 deterministic feature extractors.

Edge cases are drawn from phases/phase-1-deterministic-core.md § Unit 1 and
the input-contract ADR. The point is the *scope* discipline — clause-level vs
constituent negation, subject-scoped vs object quantifiers — not just keyword
presence.
"""

from __future__ import annotations

import pytest

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


# The 17 fixed parser canaries promoted from the A1 combined-guard trials
# (adr-v1-a1-imperative-hardening.md / cal-rules-v1.6.0): noun-initial and
# valve-subject declaratives the parser mis-roots; clean, discourse-prefixed,
# negative, and auxiliary imperatives; declarative negatives; a question
# control. The set is frozen — extend it, never edit it.
_A1_CANARIES: tuple[tuple[str, str], ...] = (
    (
        "The guidance links annual reviews to statistical process control and trend analysis.",
        "declarative",
    ),
    (
        "Change control systems must document impacts and involve the quality unit.",
        "declarative",
    ),
    ("Valve V1 passed inspection.", "declarative"),
    ("Valve V2 passed inspection.", "declarative"),
    ("Valve V3 passed inspection.", "declarative"),
    ("Validate the system before release.", "imperative"),
    ("Please validate the system before release.", "imperative"),
    ("Kindly validate the system before release.", "imperative"),
    ("Never release the batch.", "imperative"),
    ("Do not release the batch.", "imperative"),
    ("Not all valves passed inspection.", "declarative"),
    ("No release occurred.", "declarative"),
    ("The batch was not released.", "declarative"),
    ("Do release the batch.", "imperative"),
    ("Please do not release the batch.", "imperative"),
    ("The system does not release the batch.", "declarative"),
    ("Can users release the batch?", "question"),
)


@pytest.mark.parametrize(("claim", "expected"), _A1_CANARIES)
def test_sentence_type_a1_fixed_parser_canaries(claim: str, expected: str) -> None:
    assert features.sentence_type(claim) == expected


# --- negate_claim (cal-rules-v1.7.0; adr-v1-slg09-negation-consistency.md) ---
def test_negate_claim_auxiliary_insertion() -> None:
    assert features.negate_claim("The parcel was sealed.") == "The parcel was not sealed."


@pytest.mark.parametrize(
    "claim",
    [
        "The guidance mentions trend analyses but does not specify a threshold.",
        "The guidance mentions trend analyses and continual monitoring for annual "
        "product reviews but doesn't specify a volume threshold.",
        "The system validates inputs but does not archive records.",
    ],
)
def test_conjunct_scoped_negation_detects_negated_non_root_conjunct(claim: str) -> None:
    assert features.has_conjunct_scoped_negation(claim) is True


@pytest.mark.parametrize(
    "claim",
    [
        "The system does not validate inputs or archive records.",
        "The system does not validate inputs and does not archive records.",
        "The system validates inputs and archives records.",
    ],
)
def test_conjunct_scoped_negation_rejects_root_or_absent_negation(claim: str) -> None:
    assert features.has_conjunct_scoped_negation(claim) is False


def test_negate_claim_universal_prefix_never_verb_scope() -> None:
    # ¬(every x: P) must be "Not every…", never "…did not pass" (wrong proposition).
    assert (
        features.negate_claim("Every listed valve passed inspection.")
        == "Not every listed valve passed inspection."
    )


def test_negate_claim_copular_root_insertion() -> None:
    assert (
        features.negate_claim("The brass key is in drawer A.")
        == "The brass key is not in drawer A."
    )


def test_negate_claim_removes_clause_level_negation() -> None:
    assert features.negate_claim("The batch was not released.") == "The batch was released."


def test_negate_claim_do_support_for_finite_lexical_root() -> None:
    assert (
        features.negate_claim("The guidance links annual reviews to trend analysis.")
        == "The guidance does not link annual reviews to trend analysis."
    )


def test_negate_claim_abstains_on_semicolon_compound() -> None:
    claim = "The guidance promotes risk-based approaches; a fixed cycle is required."
    assert features.negate_claim(claim) is None


def test_negate_claim_abstains_on_coordinated_assertions() -> None:
    assert features.negate_claim("The system validates inputs and archives records.") is None


@pytest.mark.parametrize(
    "claim",
    [
        "No leak was reported during the shift.",
        "No deviations were recorded.",
        "None of the samples passed.",
    ],
)
def test_negate_claim_abstains_on_negative_existential(claim: str) -> None:
    """D5: do not emit 'No X was not P'. An abstention never demotes."""
    assert features.negate_claim(claim) is None


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


# --- expresses_bound / citation_numbers (cal-rules-v1.8.0;
#     adr-v1-bound-instantiation.md) ---


def test_expresses_bound_detects_stated_bounds() -> None:
    assert features.expresses_bound("The defrost cycle shall not exceed a maximum of 6 hours.")
    assert features.expresses_bound("Batches must achieve at least 40% yield to pass.")
    assert features.expresses_bound("Storage is maintained between 2.0 and 8.0 C.")
    assert features.expresses_bound("Hold time may be up to 48 hours.")


def test_expresses_bound_is_silent_over_stated_values() -> None:
    assert not features.expresses_bound("The QC analyst recorded a result of 6 hours.")
    assert not features.expresses_bound("The batch was released on 2025-11-01 by QA.")


def test_expresses_bound_matches_phrases_spacy_tokenizes_apart() -> None:
    # `at least` / `no more than` are multi-word; a lexeme-only detector misses
    # them, which is why BOUND_PHRASES exists alongside BOUND_LEXEMES.
    assert features.expresses_bound("Sampling requires no more than 3 replicates.")
    assert not features.expresses_bound("Sampling requires 3 replicates.")


def test_citation_numbers_reads_title_and_locator() -> None:
    # `21 CFR Part 11` yields BOTH the title (21) and the locator (11); an
    # earlier pattern caught only the locator.
    assert features.citation_numbers(
        "Records fall under the regulatory scope of 21 CFR Part 11."
    ) == frozenset({21.0, 11.0})
    assert features.citation_numbers("Per ICH Q7 section 6.5, records are retained.") == frozenset(
        {7.0, 6.5}
    )
    assert features.citation_numbers("Compliant with EU GMP Annex 11.") == frozenset({11.0})


def test_citation_numbers_ignores_genuine_measurements() -> None:
    assert features.citation_numbers("The hold time is 11 hours.") == frozenset()
    assert features.citation_numbers("A maximum of 6 hours applies.") == frozenset()


# --- scope_mismatch (A7) ---------------------------------------------------

_PACKAGING_CLAIM = "Packaging sites shall record deviations within two hours."
_BUILDING4_PASSAGE = (
    "At the Building 4 manufacturing site, an excursion from a validated "
    "process parameter shall be recorded as a deviation within one business "
    "day of detection."
)
_RELOCATION_CLAIM = "Relocation of qualified equipment does not require requalification."
_REQUAL_PASSAGE = (
    "Requalification shall be performed following any change that affects "
    "the qualified state, including relocation, major repair, or modification "
    "of a critical component."
)


def test_scope_anchors_find_location_phrases() -> None:
    claim_scope = features.scope_anchors(_PACKAGING_CLAIM)
    passage_scope = features.scope_anchors(_BUILDING4_PASSAGE)
    assert "packaging" in claim_scope
    assert claim_scope.isdisjoint(passage_scope)
    assert passage_scope  # Building 4 / manufacturing leftover


def test_scope_mismatch_is_true_for_disjoint_sites() -> None:
    assert features.scope_mismatch(_PACKAGING_CLAIM, _BUILDING4_PASSAGE)


def test_scope_mismatch_is_false_without_location_phrases() -> None:
    assert not features.scope_mismatch(_RELOCATION_CLAIM, _REQUAL_PASSAGE)


# --- D14: identifiers must not be read as numbers --------------------------

_CH04_CLAIM = "Chamber CH-04 held 25 °C throughout the reporting period."
_CH07_PASSAGE = (
    "Chamber CH-07 recorded excursions above 25 degrees Celsius on three days in March 2026."
)
_CH04_PASSAGE = (
    "Chamber CH-04 recorded excursions above 25 degrees Celsius on three days in March 2026."
)


def test_identifier_is_found_where_the_raw_parse_loses_it() -> None:
    """D14 regression. The passage that produced a false adverse verdict.

    Before the fix spaCy tagged ``CH-07`` as a number, it attached as a modifier
    rather than heading the subject, and this returned nothing at all.
    """
    assert "ch-07" in features.scope_anchors(_CH07_PASSAGE)
    assert "ch-04" in features.scope_anchors(_CH04_CLAIM)


def test_scope_mismatch_catches_a_different_piece_of_equipment() -> None:
    """The verdict A7 exists to withhold, on the sentence shape that used to slip past."""
    assert features.scope_mismatch(_CH04_CLAIM, _CH07_PASSAGE)


def test_scope_mismatch_does_not_fire_on_the_same_equipment() -> None:
    """The fix must not buy its recall by abstaining on true contradictions."""
    assert not features.scope_mismatch(_CH04_CLAIM, _CH04_PASSAGE)


@pytest.mark.parametrize("verb", ["recorded", "logged", "showed", "reported", "exceeded", "was"])
def test_identifier_survives_whichever_verb_follows_it(verb: str) -> None:
    """The old failure was verb-dependent and unpredictable — CH-07 survived
    *showed* and failed *recorded*. Which verb follows must not decide whether
    the gate can see the scope."""
    passage = (
        f"Chamber CH-07 {verb} excursions above the approved limit during the reporting period."
    )
    assert "ch-07" in features.scope_anchors(passage)


@pytest.mark.parametrize(
    "identifier", ["CH-07", "CH-7", "CHAMBER-07", "SOP-014", "STB-2291", "B4", "CSV-SYS-1155"]
)
def test_identifier_shapes_are_recognised(identifier: str) -> None:
    assert features._is_identifier(identifier)


@pytest.mark.parametrize(
    "not_an_identifier", ["12-month", "25", "2026", "3rd", "211.22", "mg", "percent"]
)
def test_quantities_are_not_treated_as_identifiers(not_an_identifier: str) -> None:
    """Letter-initial is the whole guard. If a quantity were normalised the numeric
    features and D3's citation handling would silently change behaviour."""
    assert not features._is_identifier(not_an_identifier)


def test_normalisation_leaves_quantity_text_untouched() -> None:
    text = "The 12-month timepoint met 25 degrees Celsius under 21 CFR 211.22."
    normalised, mapping = features._normalise_identifiers(text)
    assert normalised == text
    assert mapping == {}


def test_normalisation_is_deterministic_and_maps_back() -> None:
    text = "Chamber CH-07 and chamber CH-04 were mapped, and CH-07 was requalified."
    first, mapping = features._normalise_identifiers(text)
    second, mapping_again = features._normalise_identifiers(text)
    assert first == second, "same text must normalise to the same string"
    assert mapping == mapping_again
    # One placeholder per distinct identifier, reused on repeat.
    assert sorted(mapping.values()) == ["ch-04", "ch-07"]
    assert "CH-07" not in first and "CH-04" not in first


def test_placeholders_do_not_leak_into_anchors() -> None:
    """Anchors are the real identifiers, never the internal placeholder."""
    anchors = features.scope_anchors(_CH07_PASSAGE)
    assert not any(word.startswith("zq") for word in anchors)


def test_scope_mismatch_is_false_when_the_same_site_is_named() -> None:
    claim = (
        "At the Building 4 manufacturing site, an excursion shall be recorded "
        "within five business days of detection."
    )
    assert not features.scope_mismatch(claim, _BUILDING4_PASSAGE)
