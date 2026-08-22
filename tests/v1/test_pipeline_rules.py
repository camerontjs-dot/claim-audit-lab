"""Unit tests for CAL v2 Total 5-Stage Epistemic Decision Engine."""

from __future__ import annotations

from claim_audit_lab.v1.impl.pipeline_rules import (
    ClaimFrame,
    QualifyContext,
    V2Verdict,
    admit,
    build_claim_frame,
    qualify,
    resolve,
    run_v2,
)


def test_stage_0_build_claim_frame() -> None:
    claim = "The procedure is silent on retention sample storage."
    features = {
        "has_explicit_negation": True,
        "claim_token_count": 8,
        "sentence_type": "declarative",
    }
    frame = build_claim_frame(claim, features)
    assert frame.mode == "coverage"
    assert frame.admissible is True
    assert frame.polarity == "negative"


def test_stage_1_admit_and_near_miss() -> None:
    retrieval = [
        {"passage_id": "p1", "score": 0.85},
        {"passage_id": "p2", "score": 0.38},  # near miss (floor 0.40)
        {"passage_id": "p3", "score": 0.10},  # below floor
    ]
    entailment: list[dict[str, float | str]] = []
    admitted, removals = admit(retrieval, entailment, floor=0.40)
    assert admitted == ["p1"]
    assert len(removals) == 2
    near = [r for r in removals if r.reason == "near_miss"]
    assert len(near) == 1
    assert near[0].passage_id == "p2"


def test_stage_2_qualify_provenance_drops_refute() -> None:
    frame = ClaimFrame(
        text="A batch shall be discarded.",
        mode="ordinary",
        mode_source="parsed",
        polarity="affirmative",
        admissible=True,
        quantities=[],
        token_count=6,
        sentence_type="declarative",
    )
    ctx = QualifyContext(
        frame=frame,
        passage_id="bg-p1",
        trust_level="background",
        passage_scope=None,
        negated_reading=None,
        claim_reading={"label": "contradict", "score": 0.95},
    )
    roles, removals = qualify(ctx)
    assert "refute" not in roles
    assert "support" in roles
    assert any(r.predicate == "Q1_provenance" for r in removals)


def test_stage_2_qualify_scope_mismatch_drops_refute() -> None:
    frame = ClaimFrame(
        text="Chamber CH-04 had no excursions.",
        mode="ordinary",
        mode_source="parsed",
        polarity="affirmative",
        admissible=True,
        quantities=[],
        token_count=6,
        sentence_type="declarative",
        scope_anchors=frozenset({"CH-04"}),
    )
    ctx = QualifyContext(
        frame=frame,
        passage_id="p-ch07",
        trust_level="primary",
        passage_scope=frozenset({"CH-07"}),
        negated_reading=None,
        claim_reading={"label": "contradict", "score": 0.98},
    )
    roles, removals = qualify(ctx)
    assert "refute" not in roles
    assert any(r.predicate == "Q2_scope" for r in removals)


def test_stage_2_qualify_negation_incoherence() -> None:
    frame = ClaimFrame(
        text="Batch release time is 12 hours.",
        mode="ordinary",
        mode_source="parsed",
        polarity="affirmative",
        admissible=True,
        quantities=[],
        token_count=6,
        sentence_type="declarative",
    )
    ctx = QualifyContext(
        frame=frame,
        passage_id="p1",
        trust_level="primary",
        passage_scope=None,
        negated_reading={"label": "contradict", "score": 0.99},
        claim_reading={"label": "contradict", "score": 0.85},
    )
    roles, removals = qualify(ctx)
    # Target contradicts at 0.85, missing mirror (veto) is 0.99 >= 0.85 -> refutation dropped
    assert "refute" not in roles


def test_stage_4_resolve_exhaustive_silence() -> None:
    frame = ClaimFrame(
        text="The procedure is silent on deviations.",
        mode="coverage",
        mode_source="declared",
        polarity="negative",
        admissible=True,
        quantities=[],
        token_count=6,
        sentence_type="declarative",
    )
    degree, null_reason, citations, notes = resolve(
        frame,
        evidence=[],
        source_boundary="exhaustive",
        nothing_admitted=True,
    )
    assert degree == "supported"
    assert null_reason is None


def test_stage_4_resolve_bounded_silence() -> None:
    frame = ClaimFrame(
        text="The procedure is silent on deviations.",
        mode="coverage",
        mode_source="declared",
        polarity="negative",
        admissible=True,
        quantities=[],
        token_count=6,
        sentence_type="declarative",
    )
    degree, null_reason, citations, notes = resolve(
        frame,
        evidence=[],
        source_boundary="bounded",
        nothing_admitted=True,
    )
    assert degree == "not_checkable"
    assert null_reason == "not_resolvable"


def test_end_to_end_run_v2() -> None:
    claim = "All batches in Suite S-12 must undergo double verification."
    features = {
        "has_explicit_negation": False,
        "claim_token_count": 9,
        "sentence_type": "declarative",
        "has_universal_quantifier": True,
    }
    retrieval = [{"passage_id": "p1", "score": 0.88}]
    entailment = [
        {
            "passage_id": "p1",
            "label": "entail",
            "score": 0.95,
            "p_entail": 0.95,
            "p_contradict": 0.01,
        }
    ]
    trust_levels = {"p1": "primary"}
    claim_scope = frozenset({"S-12"})
    passage_scope = {"p1": frozenset({"S-12"})}

    verdict = run_v2(
        claim_text=claim,
        features=features,
        retrieval=retrieval,
        entailment=entailment,
        trust_levels=trust_levels,
        claim_scope=claim_scope,
        passage_scope=passage_scope,
    )

    assert isinstance(verdict, V2Verdict)
    assert verdict.degree == "supported"
    assert verdict.null_reason is None
    assert verdict.deciding_passages == ("p1",)
    assert verdict.stage_reached == "4-resolve"
