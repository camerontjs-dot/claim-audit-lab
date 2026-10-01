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
