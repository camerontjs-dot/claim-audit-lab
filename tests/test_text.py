"""Tests for shared text normalization and scoring boundaries."""

from __future__ import annotations

from claim_audit_lab.scoring import (
    DIRECT_NUMERIC_SCORE,
    MISMATCHED_NUMERIC_SCORE_CAP,
)
from claim_audit_lab.text import (
    light_stem,
    normalize_vocabulary,
    term_set,
)


def test_light_stem_preserves_words_ending_in_double_s() -> None:
    assert light_stem("process") == "process"


def test_normalized_trigger_vocabulary_is_reachable_from_text_terms() -> None:
    triggers = normalize_vocabulary({"published", "repositories", "reduced"})

    assert triggers <= term_set("Published repositories reduced review time.")


def test_numeric_mismatch_cap_stays_below_direct_support_boundary() -> None:
    assert MISMATCHED_NUMERIC_SCORE_CAP == DIRECT_NUMERIC_SCORE - 0.01
    assert MISMATCHED_NUMERIC_SCORE_CAP < DIRECT_NUMERIC_SCORE
