"""Unit tests for deterministic Interval Algebra Operator (CAL v2)."""

from __future__ import annotations

import pytest

from claim_audit_lab.v1.interval_algebra import (
    Interval,
    evaluate_interval_containment,
    extract_interval_from_text,
    extract_intervals_from_text,
    normalize_delta_to_base,
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


# ---------------------------------------------------------------------------
# Regressions. Each names the defect it pins.
# ---------------------------------------------------------------------------


def test_tolerance_on_fahrenheit_is_a_width_not_a_position() -> None:
    """A tolerance is a difference, so the affine offset must not apply to it.

    `normalize_quantity_to_base(2, "F")` is -16.67 °C, which made `98 ± 2 °F`
    construct `[53.33, 20.0]` — an inverted interval — and raise ValueError out
    of the public entry point.
    """
    delta_f, dim = normalize_delta_to_base(2, "F")
    assert dim == "temp_c"
    assert delta_f == pytest.approx(1.111, abs=1e-3)

    iv = extract_interval_from_text("98 +/- 2 F")
    assert iv is not None
    assert iv.dimension == "temp_c"
    # 98 °F is 36.67 °C; ±2 °F is ±1.11 °C.
    assert iv.lower == pytest.approx(35.556, abs=1e-3)
    assert iv.upper == pytest.approx(37.778, abs=1e-3)


def test_tolerance_on_kelvin_is_a_width_not_a_position() -> None:
    iv = extract_interval_from_text("300 +/- 5 K")
    assert iv is not None
    assert iv.lower == pytest.approx(21.85, abs=1e-2)
    assert iv.upper == pytest.approx(31.85, abs=1e-2)


def test_evaluate_never_raises_on_a_temperature_tolerance() -> None:
    """The public entry point is total."""
    res = evaluate_interval_containment("must hold at 98 +/- 2 F", "shipper recorded 99 F")
    assert res.status in ("satisfied", "violated", "inconclusive", "incomparable", "ambiguous")


def test_two_bounds_on_the_claim_dimension_abstain_rather_than_support() -> None:
    """The false-supported case: no measurand binding, so abstain.

    The evidence records a 40 °C excursion, which violates the claim. A
    first-match extractor read the *ambient lab* bound instead and returned
    satisfied/supported — a false substantiation on evidence of a violation.
    """
    res = evaluate_interval_containment(
        "Product storage must not exceed 25 C.",
        "Ambient lab temperature must not exceed 22 C. The product excursion reached 40 C.",
    )
    assert res.status == "ambiguous"
    assert res.verdict_impact is None
    assert "measurand" in res.reason


def test_a_single_comparable_bound_still_decides() -> None:
    """Abstention is scoped to genuine ambiguity, not to any extra number.

    The passage also carries a duration; it is on another dimension and so does
    not make the temperature reading ambiguous.
    """
    res = evaluate_interval_containment(
        "Reagent must not exceed 25 C.",
        "Batch 12 was held at 5 C for 30 days.",
    )
    assert res.status == "satisfied"
    assert res.verdict_impact == "supported"


def test_containment_does_not_depend_on_which_spelling_is_the_claim() -> None:
    """Unit conversion is lossy, so `==` on endpoints made containment asymmetric.

    2.5 % normalizes to 0.025 and 25000 ppm to 0.024999999999999998. One
    direction was `satisfied`, the reverse `inconclusive`, for one physical fact.
    """
    forward = evaluate_interval_containment(
        "impurity at most 2.5 percent", "impurity at most 25000 ppm"
    )
    reverse = evaluate_interval_containment(
        "impurity at most 25000 ppm", "impurity at most 2.5 percent"
    )
    assert forward.status == reverse.status == "satisfied"

    mass_forward = evaluate_interval_containment("mass at least 1005 g", "mass at least 1.005 kg")
    mass_reverse = evaluate_interval_containment("mass at least 1.005 kg", "mass at least 1005 g")
    assert mass_forward.status == mass_reverse.status == "satisfied"


def test_extraction_follows_text_order_not_pattern_table_order() -> None:
    """`within` sat earlier in the pattern table than `less than`, so a mass
    bound stated first in the sentence lost to a duration stated second."""
    text = "The assay used less than 5 mg of reagent, completed within 30 days."
    intervals = extract_intervals_from_text(text)
    assert [i.dimension for i in intervals] == ["mass_g", "time_s"]

    first = extract_interval_from_text(text)
    assert first is not None
    assert first.dimension == "mass_g"


def test_a_bare_number_is_a_measurement_only_with_a_recognized_unit() -> None:
    """The point fallback treated the next word as a unit, so `Batch 12 was`
    extracted a quantity on a `was` dimension."""
    assert extract_intervals_from_text("Part 11 requires review.") == []
    assert extract_intervals_from_text("Section 5 of the protocol applies.") == []
    assert extract_intervals_from_text("Building 4, Suite 12.") == []

    # A recognized unit is still a measurement.
    held = extract_intervals_from_text("Batch 12 was held at 5 C.")
    assert [i.dimension for i in held] == ["temp_c"]


def test_incomparable_dimensions_are_not_disjoint() -> None:
    """Disjointness is a positive claim. Returning True for a unit mismatch let
    `not subset and disjoint -> contradiction` fire on incomparable quantities."""
    mass = Interval.point(5, dimension="mass_g")
    duration = Interval.point(5, dimension="time_s")

    assert mass.is_comparable_with(duration) is False
    assert mass.is_subset_of(duration) is False
    assert mass.is_disjoint_from(duration) is False


def test_within_on_an_anchorless_dimension_yields_no_bound() -> None:
    """`within 5 %` is a tolerance around a target the text does not name; it was
    read as the upper bound `(-inf, 0.05]`."""
    assert extract_interval_from_text("tolerance within 5 percent") is None

    # On a non-negative dimension "within X" is the range [0, X] and still works.
    days = extract_interval_from_text("report within 30 days")
    assert days is not None
    assert days.lower == 0.0
    assert days.dimension == "time_s"
