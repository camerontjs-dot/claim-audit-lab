"""Focused no-inference checks for the preregistered SLG-09 negation-consistency trial."""

from __future__ import annotations

from scripts.slg09_negation_consistency_trial import negate_claim, probe_decision


# --- negator: the preregistered rule shapes ---------------------------------
def test_negator_auxiliary_insertion_parcel_shape() -> None:
    assert negate_claim("The parcel was sealed.") == "The parcel was not sealed."


def test_negator_universal_prefix_not_verb_scope() -> None:
    # ¬(every x: P) must be "Not every…", never "…did not pass" (wrong proposition).
    assert (
        negate_claim("Every listed valve passed inspection.")
        == "Not every listed valve passed inspection."
    )


def test_negator_copular_root_insertion() -> None:
    assert negate_claim("The brass key is in drawer A.") == "The brass key is not in drawer A."


def test_negator_removes_clause_level_negation() -> None:
    assert negate_claim("The batch was not released.") == "The batch was released."


def test_negator_do_support_for_finite_lexical_root() -> None:
    negated = negate_claim("The guidance links annual reviews to trend analysis.")
    assert negated == "The guidance does not link annual reviews to trend analysis."


def test_negator_abstains_on_semicolon_compound() -> None:
    claim = "The guidance promotes risk-based approaches; a fixed cycle is required."
    assert negate_claim(claim) is None


def test_negator_abstains_on_coordinated_assertions() -> None:
    assert negate_claim("The system validates inputs and archives records.") is None


# --- decision mapping --------------------------------------------------------
def test_probe_decision_entail_retains() -> None:
    assert probe_decision("entail") == "retain-confirmed"


def test_probe_decision_non_entail_demotes() -> None:
    assert probe_decision("neutral") == "demote"
    assert probe_decision("contradict") == "demote"


def test_probe_decision_abstention_retains() -> None:
    assert probe_decision(None) == "retain-abstained"
