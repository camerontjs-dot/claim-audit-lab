"""Fast tests for the A1 imperative-prefix DEV prototype."""

from __future__ import annotations

from scripts.pilot001_a1_imperative_run05 import candidate_sentence_type


def test_candidate_retains_clean_and_discourse_prefixed_imperatives() -> None:
    assert candidate_sentence_type("Validate the system before release.") == "imperative"
    assert candidate_sentence_type("Please validate the system before release.") == "imperative"
    assert candidate_sentence_type("Kindly validate the system before release.") == "imperative"


def test_candidate_rejects_the_two_dev_false_imperative_shapes() -> None:
    assert (
        candidate_sentence_type(
            "The guidance links annual reviews to statistical process control and trend analysis."
        )
        == "declarative"
    )
    assert (
        candidate_sentence_type(
            "Change control systems must document impacts and involve the quality unit."
        )
        == "declarative"
    )


def test_candidate_preserves_other_sentence_types() -> None:
    assert candidate_sentence_type("Does the system validate inputs?") == "question"
    assert candidate_sentence_type("I think the system works well.") == "opinion"
    assert candidate_sentence_type("The system validates inputs.") == "declarative"
