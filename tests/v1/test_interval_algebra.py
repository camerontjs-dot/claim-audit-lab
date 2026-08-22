"""Unit tests for deterministic Interval Algebra Operator (CAL v2)."""

from __future__ import annotations

import pytest

from claim_audit_lab.v1.interval_algebra import (
    Interval,
    evaluate_interval_containment,
    extract_interval_from_text,
    normalize_quantity_to_base,
)


def test_unit_normalization_time() -> None:
    v_s, dim_s = normalize_quantity_to_base(120, "seconds")
    assert v_s == 120.0
    assert dim_s == "time_s"

    v_h, dim_h = normalize_quantity_to_base(2, "hours")
    assert v_h == 7200.0
    assert dim_h == "time_s"

    v_d, dim_d = normalize_quantity_to_base(1, "day")
    assert v_d == 86400.0
    assert dim_d == "time_s"

    v_m, dim_m = normalize_quantity_to_base(1, "month")
    assert v_m == 2592000.0
    assert dim_m == "time_s"


def test_unit_normalization_temperature() -> None:
    v_c, dim_c = normalize_quantity_to_base(25, "°C")
    assert v_c == 25.0
    assert dim_c == "temp_c"

    v_f, dim_f = normalize_quantity_to_base(77, "°F")
    assert pytest.approx(v_f, 0.1) == 25.0
    assert dim_f == "temp_c"


def test_interval_subset_logic() -> None:
    # [12, inf) is subset of [6, inf)
    i_claim = Interval.at_least(6, dimension="time_s")
    i_evidence = Interval.at_least(12, dimension="time_s")
    assert i_evidence.is_subset_of(i_claim) is True
    assert i_claim.is_subset_of(i_evidence) is False

    # [0, 1] is subset of [0, 5]
    i_claim_upper = Interval.closed(0, 5, dimension="time_s")
    i_evidence_upper = Interval.closed(0, 1, dimension="time_s")
    assert i_evidence_upper.is_subset_of(i_claim_upper) is True


def test_interval_disjoint_logic() -> None:
    # [0, 24] and [48, inf) are disjoint
    i_a = Interval.closed(0, 24, dimension="time_s")
    i_b = Interval.at_least(48, dimension="time_s")
    assert i_a.is_disjoint_from(i_b) is True


def test_evaluate_cg20_at_least_months() -> None:
    claim = "Retention samples must be stored for at least 6 months."
    evidence = "All retain samples shall be kept for a minimum of 12 months."
    res = evaluate_interval_containment(claim, evidence)
    assert res.status == "satisfied"
    assert res.verdict_impact == "supported"


def test_evaluate_cg12b_within_hours_vs_days() -> None:
    claim = "Deviations must be reported within 5 days."
    evidence = "Critical deviations must be logged within 24 hours."
    res = evaluate_interval_containment(claim, evidence)
    assert res.status == "satisfied"
    assert res.verdict_impact == "supported"


def test_evaluate_temperature_violation() -> None:
    claim = "Reagent must be stored between 2 and 8 °C."
    evidence = "Storage temperature of reagent reached 25°C."
    res = evaluate_interval_containment(claim, evidence)
    assert res.status == "violated"
    assert res.verdict_impact == "contradicted"


def test_evaluate_temperature_support() -> None:
    claim = "Reagent must not exceed 25 °C."
    evidence = "Storage condition is between 2 and 8 °C."
    res = evaluate_interval_containment(claim, evidence)
    assert res.status == "satisfied"
    assert res.verdict_impact == "supported"


def test_identifiers_and_citations_ignored() -> None:
    claim = "In accordance with 21 CFR Part 11 and Chamber CH-04."
    iv = extract_interval_from_text(claim)
    assert iv is None
