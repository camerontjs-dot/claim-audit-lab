"""Engineering checks for the frozen strict-comparison polarity successor."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from claim_audit_lab.production_v1.semantic.models import CategoricalRelation
from claim_audit_lab.production_v1.semantic.relations import _derive_comparison
from claim_audit_lab.production_v1.targeting import author_target

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = (
    ROOT
    / "research"
    / "cal_v1_strict_comparison_polarity_rc0_20261002"
    / "decisive"
    / "evaluate.py"
)


def _evaluator():
    spec = importlib.util.spec_from_file_location("polarity_decisive_evaluator", EVALUATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _context(claim: str):
    target = author_target("polarity-unit", claim)
    from claim_audit_lab.production_v1.semantic.models import (
        AdmittedPassage,
        AuditContext,
        EvidenceWorld,
        SemanticFamily,
        TypedProposition,
    )

    proposition = TypedProposition.create(
        "polarity-unit",
        SemanticFamily.STRICT_COMPARISON,
        target["proposition"]["fields"],
        text_sha256=target["proposition"]["text_sha256"],
    )
    passage = AdmittedPassage.create("p0", "s0", claim, "sha256:" + "ab" * 32)
    world = EvidenceWorld.create(
        "1.2.0",
        "polarity-unit",
        "sha256:" + "cd" * 32,
        (passage,),
        {"contract_b_factual_context_state": "present", "observation": {"scope": "unit"}},
    )
    return AuditContext(claim, proposition, world)


def test_frozen_decisive_cases_match() -> None:
    module = _evaluator()
    report = module.evaluate(EVALUATOR.with_name("CASES.json"))
    assert report["apparatus_errors"] == []
    assert report["failed_count"] == 0
    assert report["mechanical_disposition"] == "SUPPORTED_FOR_POLARITY_SUCCESSOR_QUALIFICATION"


def test_missing_or_unknown_polarity_fails_closed() -> None:
    context = _context("Alpha had a higher rate than Beta.")
    base = {"left": "alpha", "relation": "MORE_THAN", "right": "beta"}
    assert _derive_comparison(context, base) is CategoricalRelation.UNRESOLVED
    assert (
        _derive_comparison(context, {**base, "assertion_polarity": "unknown"})
        is CategoricalRelation.UNRESOLVED
    )


def test_negation_does_not_invert_comparison_direction() -> None:
    higher = _context("Alpha had a higher rate than Beta.")
    lower = _context("Alpha had a lower rate than Beta.")
    negated_higher = {
        "left": "alpha",
        "relation": "MORE_THAN",
        "right": "beta",
        "assertion_polarity": "negative",
    }
    assert _derive_comparison(higher, negated_higher) is CategoricalRelation.REFUTES
    assert _derive_comparison(lower, negated_higher) is CategoricalRelation.UNRESOLVED
