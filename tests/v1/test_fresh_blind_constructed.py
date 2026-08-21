"""Validator for the fresh-blind constructed twin. No model, no rater."""

from __future__ import annotations

from scripts.build_fresh_blind_constructed import build, derive_twin_verdict, validate


def test_twin_is_fifty_split_and_derived() -> None:
    corpus = build()
    assert corpus["n_cases"] == 50
    assert corpus["by_register"]["pharma_regulatory"] == 25
    assert corpus["by_register"]["plain_narrative"] == 25
    assert validate(corpus) == []


def test_every_label_re_derives() -> None:
    corpus = build()
    for case in corpus["cases"]:
        verdict, derivation = derive_twin_verdict(
            case["relation"],
            case["source_boundary"],
            claimed_material_is_a_named_gap=bool(
                case.get("claimed_material_is_a_named_gap", False)
            ),
        )
        assert case["expected_verdict"] == verdict
        assert case["derivation"] == derivation
        assert "human" not in case
        assert "coder" not in case


def test_unaddressed_is_always_not_checkable() -> None:
    corpus = build()
    unaddressed = [c for c in corpus["cases"] if c["relation"] == "unaddressed"]
    assert len(unaddressed) == 12
    assert {c["expected_verdict"] for c in unaddressed} == {"not_checkable"}


def test_starved_term_absent_from_bundle() -> None:
    corpus = build()
    for case in corpus["cases"]:
        if case["relation"] not in {"unaddressed", "absent_from"}:
            continue
        bundle = " ".join(p["text"].lower() for p in case["passages"])
        term = case["claimed_absent_term"].lower()
        assert term not in bundle
        if case["relation"] == "unaddressed":
            assert term in case["claim_text"].lower()
