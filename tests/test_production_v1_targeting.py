from __future__ import annotations

import hashlib

import pytest

from claim_audit_lab.production_v1.targeting import (
    TargetAuthoringError,
    author_target,
    canonical_target_bytes,
)


def test_strict_comparison_authoring_matches_frozen_trusted_shape() -> None:
    text = "Alpha had a higher rate than Beta."
    target = author_target("C1", text)
    assert target == {
        "claim_id": "C1",
        "proposition": {
            "proposition_id": "C1",
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "semantic_family": "strict_comparison",
            "fields": {
                "lhs_entity": "Alpha",
                "rhs_entity": "Beta",
                "comparison_direction": "MORE_THAN",
            },
        },
    }


def test_direct_event_order_authoring_matches_frozen_trusted_shape() -> None:
    text = "Alice reviewed dossier before Bob archived dossier."
    target = author_target("C2", text)
    assert target["proposition"]["semantic_family"] == "direct_event_order"
    assert target["proposition"]["fields"] == {
        "left_subject": "alice",
        "left_predicate": "review",
        "left_object": "dossier",
        "left_polarity": "positive",
        "temporal_relation": "BEFORE",
        "right_subject": "bob",
        "right_predicate": "archive",
        "right_object": "dossier",
        "right_polarity": "positive",
    }


def test_canonical_target_bytes_are_deterministic() -> None:
    text = "Alpha had a lower output than Beta."
    target = author_target("C1", text)
    assert canonical_target_bytes(target) == canonical_target_bytes(target)
    assert canonical_target_bytes(target).endswith(b"\n")


@pytest.mark.parametrize(
    "text",
    (
        "Alpha had a higher rate than Beta in 2025.",
        "alice had a higher rate than Beta.",
        "Alice did not review dossier before Bob archived dossier.",
        "Alice reviewed dossier while Bob archived dossier.",
        "The archive contains unrelated maintenance notes.",
    ),
)
def test_authoring_fails_closed_outside_bounded_grammar(text: str) -> None:
    with pytest.raises(TargetAuthoringError):
        author_target("X", text)


def test_copular_comparison_keeps_both_nominals_and_direction() -> None:
    text = "The rate of widget failure in Plant A in 2019 is lower than the rate in 2018."
    fields = author_target("S", text)["proposition"]["fields"]
    assert fields == {
        "lhs_entity": "The rate of widget failure in Plant A in 2019",
        "rhs_entity": "the rate in 2018",
        "comparison_direction": "LESS_THAN",
    }


def test_direction_flip_keeps_copular_sides() -> None:
    lower = (
        "The employment rate of group A in 2019 is lower than "
        "the employment rate of group B in 2019."
    )
    higher = (
        "The employment rate of group A in 2019 is higher than "
        "the employment rate of group B in 2019."
    )
    lower_fields = author_target("L", lower)["proposition"]["fields"]
    higher_fields = author_target("H", higher)["proposition"]["fields"]
    assert lower_fields["lhs_entity"] == higher_fields["lhs_entity"]
    assert lower_fields["rhs_entity"] == higher_fields["rhs_entity"]
    assert lower_fields["comparison_direction"] == "LESS_THAN"
    assert higher_fields["comparison_direction"] == "MORE_THAN"


def test_likelihood_side_swap_keeps_direction_and_drops_measured_property() -> None:
    forward = "During the study window, women were more likely than men to report condition A."
    reverse = "During the study window, men were more likely than women to report condition B."
    forward_fields = author_target("F", forward)["proposition"]["fields"]
    reverse_fields = author_target("R", reverse)["proposition"]["fields"]
    assert forward_fields == {
        "lhs_entity": "women",
        "rhs_entity": "men",
        "comparison_direction": "MORE_THAN",
    }
    assert reverse_fields == {
        "lhs_entity": "men",
        "rhs_entity": "women",
        "comparison_direction": "MORE_THAN",
    }


def test_unstored_scope_quantifier_and_trailing_adjunct_collide() -> None:
    scoped = (
        "In three regions, the adjusted rate of group A is higher than "
        "the corresponding rate of group B."
    )
    rescope = (
        "In nine regions, the adjusted rate of group A is higher than "
        "the corresponding rate of group B."
    )
    counted = (
        "In eight reported instances, the total count of process water was higher than "
        "its action limit."
    )
    recounted = (
        "In two reported instances, the total count of process water was higher than "
        "its action limit."
    )
    trailed = (
        "Northwood had a higher specific antibody rate than Southwood in almost all age groups."
    )
    retrail = "Northwood had a higher specific antibody rate than Southwood in all age groups."
    assert (
        author_target("A", scoped)["proposition"]["fields"]
        == (author_target("B", rescope)["proposition"]["fields"])
    )
    assert author_target("A", scoped)["proposition"]["fields"]["lhs_entity"] == (
        "the adjusted rate of group A"
    )
    assert (
        author_target("C", counted)["proposition"]["fields"]
        == (author_target("D", recounted)["proposition"]["fields"])
    )
    assert author_target("E", trailed)["proposition"]["fields"] == {
        "lhs_entity": "Northwood",
        "rhs_entity": "Southwood",
        "comparison_direction": "MORE_THAN",
    }
    assert (
        author_target("E", trailed)["proposition"]["fields"]
        == (author_target("F", retrail)["proposition"]["fields"])
    )


def test_harmless_spacing_keeps_fields_and_changes_claim_binding() -> None:
    text = (
        "The employment rate of group A in 2019 is higher than "
        "the employment rate of group B in 2019."
    )
    variant = "  ".join(text.rstrip(".").split())
    original = author_target("A", text)
    mutated = author_target("B", variant)
    assert original["proposition"]["fields"] == mutated["proposition"]["fields"]
    assert original["proposition"]["text_sha256"] != mutated["proposition"]["text_sha256"]


@pytest.mark.parametrize(
    "text",
    (
        "Alpha had the same rate as Beta.",
        "Alpha had a higher rate than Beta but a lower rate than Gamma.",
        "Alpha had a higher rate than.",
        "Alpha and Gamma had a higher rate than Beta.",
        "Alpha had a different rate than Beta.",
        "In 2019, Alpha had a higher rate than Beta.",
    ),
)
def test_comparison_extension_still_refuses_unbound_or_closed_frame_residue(text: str) -> None:
    with pytest.raises(TargetAuthoringError):
        author_target("X", text)
