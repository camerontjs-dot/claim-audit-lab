from __future__ import annotations

from .rc8c_cohort import build_rc8c_cases


def test_rc8c_cohort_holds_everything_except_raw_source_identity_constant() -> None:
    cases = build_rc8c_cases()
    assert len(cases) == 3
    assert len({case["case_id"] for case in cases}) == 3

    positive, substituted, missing = cases
    assert positive["expected_authority"] == "WARRANTED"
    assert substituted["expected_authority"] == "REJECTED"
    assert missing["expected_authority"] == "UNRESOLVED"

    ignored = {"case_id", "mutation_axis", "expected_authority", "expected_reason", "raw_source_id"}
    for case in (substituted, missing):
        for key, value in positive.items():
            if key in ignored:
                continue
            assert case[key] == value

    assert positive["raw_source_id"] == "source:prospective:alpha"
    assert substituted["raw_source_id"] == "source:prospective:beta"
    assert "raw_source_id" not in missing
    assert positive["evidence_admitted"] is True
    assert substituted["evidence_admitted"] is True
    assert missing["evidence_admitted"] is True
