"""Offline tests for the T3 candidate screen; no CAL inference."""

from __future__ import annotations

import pytest

from scripts.slg_scaled_t3_candidate import (
    PARAGRAPH_COUNT,
    TITLE,
    render_target_blind_fixture,
    screen,
    split_raw,
    validate_p2,
)


def _raw() -> str:
    paragraph = (
        "routine calendar entries list room names dates times corridors labels airflow humidity "
        "and cleaning notes for staff meetings "
        * 2
        + (
            "daily report records follow routine monthly room review notes beside each calendar "
            "entry today"
        )
    )
    return TITLE + "\n\n" + "\n\n".join(paragraph.strip() for _ in range(PARAGRAPH_COUNT)) + "\n"


def test_t3_clean_shape_reaches_p2_boundary() -> None:
    result = screen(_raw())
    assert result["paragraph_count"] == 30
    assert result["body_word_count_ok"] is True
    assert result["decision"] == "continue_to_p2"


def test_deterministic_renderer_is_target_blind_and_screen_clean() -> None:
    raw = render_target_blind_fixture()
    assert raw.startswith(TITLE)
    assert screen(raw)["decision"] == "continue_to_p2"


def test_t3_subject_or_outcome_morphology_rejects_candidate() -> None:
    result = screen(_raw().replace("calendar", "sample", 1).replace("entries", "verified", 1))
    assert result["decision"] == "reject_deterministic_screen"
    assert result["forbidden_subject_hits"] == ["sample"]
    assert "verify" in result["banned_outcome_or_derivation_hits"]


def test_t3_shape_is_fail_closed() -> None:
    with pytest.raises(ValueError, match="title plus 30"):
        split_raw(TITLE + "\n\nshort\n")


def test_p2_requires_all_frozen_rows_unrelated() -> None:
    payload = {
        "overall": "clean",
        "reviews": [{"id": f"P{i:02d}", "relation": "unrelated"} for i in range(1, 26)],
    }
    assert validate_p2(payload)
    payload["reviews"][10]["relation"] = "ambiguous"
    assert not validate_p2(payload)
