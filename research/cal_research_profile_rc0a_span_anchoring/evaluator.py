"""Frozen evaluator for the CAL RC0A span-anchoring experiment."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from span_anchor import (
    lexical_spans,
    unique_lexical_span,
    weak_first_lexical_span,
    weak_parent_unique_substring_span,
)

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "CASES.json"


def _span_json(span: tuple[int, int] | None) -> list[int] | None:
    return list(span) if span is not None else None


def main() -> None:
    cohort = json.loads(CASES.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    unsafe_selection_ids: list[str] = []
    mismatch_ids: list[str] = []

    for case in cohort["cases"]:
        text = case["text"]
        surface = case["surface"]
        expected = case["expected_span"]
        observed = _span_json(unique_lexical_span(text, surface))
        all_eligible = [list(span) for span in lexical_spans(text, surface)]
        exact = observed == expected

        returned_slice_valid = True
        if observed is not None:
            start, end = observed
            returned_slice_valid = (
                0 <= start <= end <= len(text)
                and text[start:end].casefold() == surface.strip().casefold()
            )

        if expected is None and observed is not None:
            unsafe_selection_ids.append(case["id"])
        if not exact or not returned_slice_valid:
            mismatch_ids.append(case["id"])

        rows.append(
            {
                "id": case["id"],
                "surface": surface,
                "expected_span": expected,
                "observed_span": observed,
                "eligible_lexical_spans": all_eligible,
                "returned_slice_valid": returned_slice_valid,
                "exact": exact and returned_slice_valid,
            }
        )

    overlap_text = "Women trailed Men by 11 percentage points."
    repeat_text = "Alpha exceeded Beta after Alpha recovered."
    weak_controls = {
        "parent_unique_substring_reproduces_overlap_miss": (
            weak_parent_unique_substring_span(overlap_text, "Men") is None
        ),
        "candidate_resolves_overlap_exactly": (
            _span_json(unique_lexical_span(overlap_text, "Men")) == [14, 17]
        ),
        "first_lexical_weak_control_selects_ambiguous_duplicate": (
            _span_json(weak_first_lexical_span(repeat_text, "Alpha")) == [0, 5]
        ),
        "candidate_refuses_ambiguous_duplicate": (
            unique_lexical_span(repeat_text, "Alpha") is None
        ),
    }
    weak_controls_pass = all(weak_controls.values())
    exact_count = sum(1 for row in rows if row["exact"])
    supported = (
        exact_count == len(rows)
        and not unsafe_selection_ids
        and weak_controls_pass
    )

    result = {
        "experiment": "cal-rc0a-exact-entity-span-anchoring",
        "cohort_id": cohort["cohort_id"],
        "parent_head": cohort["parent_head"],
        "case_count": len(rows),
        "exact_count": exact_count,
        "mismatch_ids": mismatch_ids,
        "unsafe_selection_ids": unsafe_selection_ids,
        "weak_controls": weak_controls,
        "weak_controls_pass": weak_controls_pass,
        "cases": rows,
        "production_promotion_authorized": False,
        "next_step_authorized": "RC0B_INTEGRATION_REGRESSION" if supported else None,
        "research_disposition": "SUPPORTED_WITH_BOUNDS" if supported else "FALSIFIED",
    }
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
