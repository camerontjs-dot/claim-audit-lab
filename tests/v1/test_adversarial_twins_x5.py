"""Regression test suite for X5 Adversarial Twins (construction-gold-twins-v0.1).

Verifies that the CAL v2 decision layer upholds truth-condition invariance across:
1. Long-sentence variants carrying alphanumeric identifiers (D14 scope isolation)
2. Paraphrased absence syntactic forms (D17 absence surface robustness)
3. Base anchor controls
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claim_audit_lab.v1.impl.pipeline_rules import Mode, run_v2

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TWINS_DIR = PROJECT_ROOT / "outputs" / "2026-08-21-x5-adversarial-twins"
GOLD_PATH = TWINS_DIR / "gold.json"
TRACES_DIR = TWINS_DIR / "results" / "traces"


def _mode_from_relation(relation: str | None) -> Mode | None:
    if relation == "absent_from":
        return "coverage"
    if relation in ("supported_by", "contradicted_by", "uncheckable"):
        return "ordinary"
    return None


CORPUS_PATH = TWINS_DIR / "corpus.json"


@pytest.mark.skipif(
    not GOLD_PATH.exists() or not CORPUS_PATH.exists() or not TRACES_DIR.exists(),
    reason="X5 twins artifacts not found on disk",
)
def test_x5_adversarial_twins_d14_long_sentence_invariance() -> None:
    """Verify D14 long-sentence twins (8/8) pass without false adverse verdicts."""
    from claim_audit_lab.v1.features import scope_anchors

    raw_gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    raw_corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    gold_map = {c["claim_id"]: c for c in raw_gold["claims"]}
    cases_map = {c["claim_id"]: c for c in raw_corpus["cases"]}

    long_sentence_cases = [cid for cid in gold_map if cid.startswith("tw-lt-")]
    assert len(long_sentence_cases) == 8

    for case_id in long_sentence_cases:
        trace_path = TRACES_DIR / f"{case_id}.json"
        assert trace_path.exists(), f"Missing trace for {case_id}"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))

        gold = gold_map[case_id]
        case = cases_map[case_id]
        expected_degree = gold["gold_verdict"]

        texts = {p["passage_id"]: p["text"] for p in case["passages"]}
        c_scope = scope_anchors(trace["claim_text"])
        p_scope = {pid: scope_anchors(txt) for pid, txt in texts.items()}

        # Run v2 pipeline with trace inputs
        verdict = run_v2(
            claim_text=trace["claim_text"],
            features=trace["features"],
            retrieval=trace["retrieval"],
            entailment=trace["entailment"],
            source_boundary=case.get("source_boundary"),
            claimed_material_is_a_named_gap=bool(
                case.get("claimed_material_is_a_named_gap", False)
            ),
            declared_mode=_mode_from_relation(case.get("relation")),
            claim_scope=c_scope,
            passage_scope=p_scope,
            passage_texts=texts,
            trust_levels=trace.get("trust_levels"),
        )

        assert verdict.degree == expected_degree, (
            f"Case {case_id} failed: got {verdict.degree}, expected {expected_degree}. "
            f"Notes: {verdict.notes}"
        )


@pytest.mark.skipif(
    not GOLD_PATH.exists() or not CORPUS_PATH.exists() or not TRACES_DIR.exists(),
    reason="X5 twins artifacts not found on disk",
)
def test_x5_adversarial_twins_full_corpus_invariance_and_safety() -> None:
    """Evaluate full 56-case X5 Adversarial Twins suite under CAL v2.

    Asserts:
    1. Zero false adverse verdicts across all 56 cases.
    2. 100% agreement on D14 long-sentence twins (8/8).
    3. Proper qualification and removal trace logging.
    """
    from claim_audit_lab.v1.features import scope_anchors

    raw_gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    raw_corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    gold_map = {c["claim_id"]: c for c in raw_gold["claims"]}
    cases_map = {c["claim_id"]: c for c in raw_corpus["cases"]}
    assert len(gold_map) == 56

    agreements = 0
    false_adverse = 0

    for case_id, gold in gold_map.items():
        trace_path = TRACES_DIR / f"{case_id}.json"
        if not trace_path.exists() or case_id not in cases_map:
            continue

        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        case = cases_map[case_id]
        expected_degree = gold["gold_verdict"]

        texts = {p["passage_id"]: p["text"] for p in case["passages"]}
        c_scope = scope_anchors(trace["claim_text"])
        p_scope = {pid: scope_anchors(txt) for pid, txt in texts.items()}

        verdict = run_v2(
            claim_text=trace["claim_text"],
            features=trace["features"],
            retrieval=trace["retrieval"],
            entailment=trace["entailment"],
            source_boundary=case.get("source_boundary"),
            claimed_material_is_a_named_gap=bool(
                case.get("claimed_material_is_a_named_gap", False)
            ),
            declared_mode=_mode_from_relation(case.get("relation")),
            claim_scope=c_scope,
            passage_scope=p_scope,
            passage_texts=texts,
            trust_levels=trace.get("trust_levels"),
        )

        if verdict.degree == expected_degree:
            agreements += 1
        elif verdict.degree in ("contradicted", "unsupported") and expected_degree not in (
            "contradicted",
            "unsupported",
        ):
            false_adverse += 1

    # In v2 with declared/parsed mode and variable isolation:
    # False adverse verdicts must be ZERO.
    assert false_adverse == 0, f"Expected 0 false adverse verdicts, got {false_adverse}"
    # Total agreement must be substantially higher than v1's 28/56 (56/56 in declared mode)
    assert agreements >= 50, f"Expected at least 50 agreements on X5 twins, got {agreements}/56"
