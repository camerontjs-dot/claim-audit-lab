"""Bring-up checks on invented sentences. This file does not read the seed cases."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_CANDIDATE = Path(__file__).resolve().parent
_REPO = _CANDIDATE.parents[1]
sys.path.insert(0, str(_CANDIDATE))
sys.path.insert(0, str(_REPO / "src"))

from codec import canonical
from comparison_relation import judge as compare
from constraint_guard import judge as guard
from dispatch import dispatch
from event_order import judge as events
from kernel_lane import judge as kernel
from lossy import lossy_text


def envelope(claim: str, passages: list[tuple[str, str]]) -> bytes:
    return canonical(
        {"claim": claim, "evidence": [{"id": pid, "text": text} for pid, text in passages]}
    )


def expect(label: str, actual: object, wanted: object) -> None:
    if actual != wanted:
        raise SystemExit(f"{label}: {actual!r} != {wanted!r}")


def main() -> int:
    same = envelope(
        "Gamma had a higher score than Delta.",
        [("p", "Gamma had a higher score than Delta.")],
    )
    expect("kernel-support", kernel(same)["conclusion"], "supports")
    expect("relation-support", compare(same)["conclusion"], "supports")

    negated = envelope(
        "Gamma had a higher score than Delta.",
        [("p", "Gamma did not have a higher score than Delta.")],
    )
    expect("kernel-refute", kernel(negated)["conclusion"], "refutes")
    expect("relation-refute", compare(negated)["conclusion"], "refutes")

    lower = envelope(
        "Gamma had a lower score than Delta.",
        [("p", "Gamma did not have a higher score than Delta.")],
    )
    expect("relation-not-lower", compare(lower)["abstention_cause"], "polarity_non_establishing")
    expect("kernel-not-lower", kernel(lower)["conclusion"], "unresolved")

    scoped = envelope(
        "In 2031, Gamma had a higher score than Delta.",
        [("p", "In 2031, Gamma had a higher score than Delta.")],
    )
    expect("kernel-year-refusal", kernel(scoped)["abstention_cause"], "authoring_refusal")
    scoped_relation = compare(scoped)
    expect("relation-year", scoped_relation["conclusion"], "supports")
    expect("year-kept", scoped_relation["claim_interpretation"]["time"], "2031")

    other_year = envelope(
        "In 2031, Gamma had a higher score than Delta.",
        [("p", "In 2030, Gamma had a higher score than Delta.")],
    )
    expect("year-mismatch", compare(other_year)["abstention_cause"], "scope_mismatch")
    expect("guard-year", guard(other_year)["conclusion"], "violated")

    property_claim = "Gamma had a higher marine reporting score than Delta."
    property_same = envelope(property_claim, [("p", property_claim)])
    property_other = envelope(
        property_claim,
        [("p", "Gamma had a higher inland reporting score than Delta.")],
    )
    expect("property-support", compare(property_same)["conclusion"], "supports")
    expect("property-kept", compare(property_same)["claim_interpretation"]["property"], "marine reporting")
    expect("property-mismatch", compare(property_other)["abstention_cause"], "scope_mismatch")

    universal = "Gamma had a higher score than Delta in all age groups."
    existential = envelope(universal, [("p", "Gamma had a higher score than Delta in some age groups.")])
    expect("quantifier-mismatch", compare(existential)["abstention_cause"], "scope_mismatch")
    expect(
        "quantifier-support",
        compare(envelope(universal, [("p", universal)]))["conclusion"],
        "supports",
    )

    swapped = envelope(
        "Delta had a lower score than Gamma.",
        [("p", "Gamma had a higher score than Delta.")],
    )
    expect("swap", compare(swapped)["conclusion"], "supports")
    expect("kernel-swap", kernel(swapped)["conclusion"], "supports")

    conflict = envelope(
        "Gamma had a higher score than Delta.",
        [
            ("p1", "Gamma had a higher score than Delta."),
            ("p2", "Gamma had a lower score than Delta."),
        ],
    )
    expect("conflict", compare(conflict)["local_material_conflict"], True)
    expect("kernel-conflict", kernel(conflict)["abstention_cause"], "material_conflict")

    missing = envelope("Gamma had a higher score than Delta.", [])
    expect("missing", compare(missing)["abstention_cause"], "missing_evidence")
    expect("kernel-missing", kernel(missing)["conclusion"], "unresolved")

    alleged = envelope(
        "Gamma had a higher score than Delta.",
        [("p", "A report alleged that Gamma had a higher score than Delta.")],
    )
    expect("allegation", compare(alleged)["abstention_cause"], "attribution")
    expect("kernel-allegation", kernel(alleged)["conclusion"], "unresolved")

    ordered = envelope(
        "Gamma reviewed Log before Delta approved Batch.",
        [("p", "Gamma reviewed Log before Delta approved Batch.")],
    )
    inverse = envelope(
        "Gamma reviewed Log before Delta approved Batch.",
        [("p", "Delta approved Batch before Gamma reviewed Log.")],
    )
    expect("event", events(ordered)["conclusion"], "supports")
    expect("kernel-event", kernel(ordered)["conclusion"], "supports")
    expect("event-inverse", events(inverse)["conclusion"], "refutes")
    expect("kernel-inverse", kernel(inverse)["conclusion"], "refutes")
    expect("guard-skips-event", guard(ordered)["conclusion"], "not_applicable")
    expect("relation-skips-event", compare(ordered)["conclusion"], "not_applicable")

    stripped = lossy_text(
        "In 2031, Gamma had a higher marine reporting score than Delta in all age groups."
    )
    expect("lossy", stripped, "Gamma had a higher score than Delta.")
    expect(
        "lossy-allegation",
        lossy_text("A report alleged that Gamma had a higher score than Delta."),
        "Gamma had a higher score than Delta.",
    )

    traced = dispatch(same, order=("original_relation",), trace_open=True)
    expect("subprocess", traced[0]["binding_ok"], True)
    expect("subprocess-conclusion", traced[0]["receipt"]["conclusion"], "supports")
    opened = set(traced[0]["open_classes"])
    expect("no-forbidden", traced[0]["forbidden_read"], False)
    allowed = {
        "candidate_module",
        "python_stdlib",
        "installed_dependency",
        "cal_product_package",
        "platform_runtime",
    }
    unexpected = opened - allowed
    if unexpected:
        raise SystemExit(f"unexpected open classes: {sorted(unexpected)}")
    print(json.dumps({"selfcheck": "passed", "open_classes": sorted(opened)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
