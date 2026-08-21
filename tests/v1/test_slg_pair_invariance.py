"""Focused no-inference checks for the domain freeze and pair-invariance tooling."""

from __future__ import annotations

import pytest

from scripts.slg_domain_freeze import build_domain_frozen
from scripts.slg_pair_invariance_run import classify

_PLAIN = {
    "freeze_identifier": "plain-freeze",
    "frozen_cases": [
        {
            "base_case_id": "SLG-01",
            "plain_claim": "The brass key is in drawer A.",
            "operator": "single",
            "parent_verdict": "supported",
            "source_boundary": "bounded",
            "source_boundary_note": "The one listed observation is complete.",
            "facts": [{"fact_id": "f-1", "text": "The brass key is in drawer A."}],
            "atoms": [
                {
                    "atom_id": "SLG-01-a1",
                    "claim": "The brass key is in drawer A.",
                    "relation": "supports",
                    "derivation": "identity",
                }
            ],
        }
    ],
}


def _renderings(relation: str = "supports") -> dict[str, object]:
    return {
        "renderings": [
            {
                "base_case_id": "SLG-01",
                "domain_case_id": "SLG-01-d",
                "domain_claim": "The retained sample is in cabinet A.",
                "facts": [
                    {
                        "fact_id": "d-1",
                        "maps_to": "f-1",
                        "text": "The retained sample is in cabinet A.",
                    }
                ],
                "atoms": [
                    {
                        "atom_id": "SLG-01-d-a1",
                        "maps_to": "SLG-01-a1",
                        "claim": "The retained sample is in cabinet A.",
                        "relation": relation,
                    }
                ],
            }
        ]
    }


def test_freeze_substitutes_texts_and_inherits_structure() -> None:
    payload = build_domain_frozen(_PLAIN, _renderings())
    case = payload["frozen_cases"][0]
    assert case["base_case_id"] == "SLG-01-d"
    assert case["paired_base_case_id"] == "SLG-01"
    assert case["operator"] == "single"
    assert case["parent_verdict"] == "supported"
    assert case["atoms"][0]["derivation"] == "identity"
    assert case["facts"][0]["text"] == "The retained sample is in cabinet A."


def test_freeze_rejects_a_changed_relation() -> None:
    with pytest.raises(ValueError, match="changed the frozen relation"):
        build_domain_frozen(_PLAIN, _renderings(relation="refutes"))


def test_freeze_rejects_incomplete_maps_to_coverage() -> None:
    bad = _renderings()
    bad["renderings"][0]["facts"][0]["maps_to"] = "f-unknown"  # type: ignore[index]
    with pytest.raises(ValueError, match="fact maps_to set mismatch"):
        build_domain_frozen(_PLAIN, bad)


@pytest.mark.parametrize(
    ("plain_match", "domain_match", "expected"),
    [
        (True, True, "both-match"),
        (False, False, "wrong-on-both"),
        (False, True, "plain-only-miss"),
        (True, False, "domain-only-miss"),
        (None, None, "noncomparable"),
        (None, True, "noncomparable"),
    ],
)
def test_classify_covers_the_unit3_green_boundary(
    plain_match: bool | None, domain_match: bool | None, expected: str
) -> None:
    assert classify(plain_match, domain_match) == expected
