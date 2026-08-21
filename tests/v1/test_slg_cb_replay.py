"""Focused no-inference checks for the E4 Unit 4 C-B replay comparison."""

from __future__ import annotations

from scripts.slg_cb_replay_run import compare

_DIRECT = {
    "atoms": [
        {
            "atom_id": "SLG-01-a1",
            "expected_relation": "supports",
            "cal_observed_relation": "supports",
        },
        {
            "atom_id": "SLG-09-a2",
            "expected_relation": "insufficient",
            "cal_observed_relation": "insufficient",
        },
    ]
}


def _cb(relation_by_atom: dict[str, str]) -> dict[str, dict[str, object]]:
    return {
        atom_id: {
            "cb_observed_relation": relation,
            "cb_support_verdict_reason": None,
            "cb_flags": [],
        }
        for atom_id, relation in relation_by_atom.items()
    }


def test_compare_reports_full_parity_with_no_diagnostics() -> None:
    result = compare(_DIRECT, _cb({"SLG-01-a1": "supports", "SLG-09-a2": "insufficient"}))
    assert result["summary"] == {"atoms": 2, "same_outcome": 2, "differences": 0}
    assert result["diagnostics"] == []


def test_compare_lists_differences_as_diagnostics_not_merged() -> None:
    result = compare(_DIRECT, _cb({"SLG-01-a1": "refutes", "SLG-09-a2": "insufficient"}))
    assert result["summary"] == {"atoms": 2, "same_outcome": 1, "differences": 1}
    (diagnostic,) = result["diagnostics"]
    assert diagnostic["atom_id"] == "SLG-01-a1"
    assert diagnostic["direct_observed"] == "supports"
    assert diagnostic["cb_observed"] == "refutes"
    assert "not merged" in diagnostic["note"]
