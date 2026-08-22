"""Unit tests for CAL v2 Total 5-Stage Epistemic Decision Engine."""

from __future__ import annotations

import pytest

from claim_audit_lab.v1.impl import pipeline_rules
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


def _frame(text: str, **kw: object) -> ClaimFrame:
    """A minimal admissible ordinary claim frame."""
    defaults: dict[str, object] = {
        "mode": "ordinary",
        "mode_source": "parsed",
        "polarity": "affirmative",
        "admissible": True,
        "quantities": [],
        "token_count": 6,
        "sentence_type": "declarative",
    }
    defaults.update(kw)
    return ClaimFrame(text=text, **defaults)  # type: ignore[arg-type]


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


# ---------------------------------------------------------------------------
# Stage 2 — Q4 interval containment. Advisory: it records, it does not remove.
# ---------------------------------------------------------------------------


def _quantitative_ctx(claim: str, passage: str) -> QualifyContext:
    return QualifyContext(
        frame=_frame(claim, quantities=[25]),
        passage_id="p1",
        trust_level="primary",
        passage_scope=None,
        negated_reading=None,
        claim_reading={"label": "contradict", "score": 0.95},
        passage_text=passage,
    )


def test_q4_records_its_reading_and_removes_no_role() -> None:
    """Q4 is advisory until a bound can be tied to a measurand.

    Dropping `refute` on `satisfied` is what produced a false substantiation: a
    passage recording a violation lost its standing to refute because the
    operator matched a bound belonging to something else.
    """
    roles, removals = qualify(
        _quantitative_ctx(
            "Reagent must not exceed 25 C.",
            "Storage condition is between 2 and 8 C.",
        )
    )
    assert roles == frozenset({"support", "refute"})

    q4 = [r for r in removals if r.predicate == "Q4_interval_containment"]
    assert len(q4) == 1
    assert q4[0].detail["advisory"] is True
    assert q4[0].detail["status"] == "satisfied"
    # The reading a caller would act on, once it may.
    assert q4[0].detail["verdict_impact_if_deciding"] == "supported"


def test_q4_records_a_violation_without_dropping_support() -> None:
    roles, removals = qualify(
        _quantitative_ctx(
            "Reagent must be stored between 2 and 8 C.",
            "Storage temperature of reagent reached 25 C.",
        )
    )
    assert "support" in roles

    q4 = [r for r in removals if r.predicate == "Q4_interval_containment"]
    assert q4[0].detail["status"] == "violated"
    assert q4[0].detail["verdict_impact_if_deciding"] == "contradicted"


def test_q4_is_silent_when_the_claim_carries_no_quantity() -> None:
    ctx = QualifyContext(
        frame=_frame("A batch shall be discarded."),
        passage_id="p1",
        trust_level="primary",
        passage_scope=None,
        negated_reading=None,
        claim_reading={"label": "entail", "score": 0.9},
        passage_text="Batches are discarded after review.",
    )
    _, removals = qualify(ctx)
    assert not [r for r in removals if r.predicate == "Q4_interval_containment"]


def test_advisory_records_are_not_counted_as_ineligibility() -> None:
    """A record that removed nothing is not a reason the passage may not decide."""
    verdict = run_v2(
        claim_text="Reagent must not exceed 25 C during storage.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 8,
            "sentence_type": "declarative",
            "numerical_values": [25],
        },
        retrieval=[{"passage_id": "p1", "score": 0.9}],
        entailment=[{"passage_id": "p1", "label": "entail", "score": 0.95}],
        trust_levels={"p1": "primary"},
        passage_texts={"p1": "Storage condition is between 2 and 8 C."},
    )
    assert verdict.degree == "supported"
    assert verdict.deciding_passages == ("p1",)


# ---------------------------------------------------------------------------
# Totality — a stage runs to completion even when a predicate fails.
# ---------------------------------------------------------------------------


def test_a_raising_predicate_marks_the_passage_and_removes_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The module header's first claim, as an executable one.

    Before this, a predicate raising left stage 2 through `run_v2` as an
    unhandled exception — the control-flow redirect the pipeline exists to
    remove.
    """

    def _boom(ctx: QualifyContext) -> tuple[frozenset[str], str | None, dict[str, object]]:
        raise RuntimeError("predicate exploded")

    monkeypatch.setattr(
        pipeline_rules,
        "ELIGIBILITY_PREDICATES",
        (("Q1_provenance", pipeline_rules._q1_provenance), ("Q_boom", _boom)),
    )

    roles, removals = qualify(
        QualifyContext(
            frame=_frame("A batch shall be discarded."),
            passage_id="p1",
            trust_level="primary",
            passage_scope=None,
            negated_reading=None,
            claim_reading={"label": "entail", "score": 0.9},
        )
    )

    # Removed nothing: a check that could not run must not disqualify a passage.
    assert roles == frozenset({"support", "refute"})

    boom = [r for r in removals if r.predicate == "Q_boom"]
    assert len(boom) == 1
    assert "RuntimeError" in boom[0].reason
    assert boom[0].detail["skipped"] is True
    assert "predicate exploded" in boom[0].detail["error"]


def test_run_v2_completes_when_a_predicate_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(ctx: QualifyContext) -> tuple[frozenset[str], str | None, dict[str, object]]:
        raise ValueError("Invalid interval: lower (53.3) > upper (20.0)")

    monkeypatch.setattr(pipeline_rules, "ELIGIBILITY_PREDICATES", (("Q_boom", _boom),))

    verdict = run_v2(
        claim_text="Storage must be maintained at 98 +/- 2 F throughout shipping.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 10,
            "sentence_type": "declarative",
            "numerical_values": [98, 2],
        },
        retrieval=[{"passage_id": "p1", "score": 0.9}],
        entailment=[{"passage_id": "p1", "label": "entail", "score": 0.95}],
        trust_levels={"p1": "primary"},
        passage_texts={"p1": "The shipper recorded 99 F on arrival."},
    )

    assert verdict.stage_reached == "4-resolve"
    assert verdict.degree == "supported"
    assert any("Q_boom" in r.predicate for r in verdict.removals)


def test_a_raising_resolution_rule_yields_to_the_next(monkeypatch: pytest.MonkeyPatch) -> None:
    """Precedence survives a failure: the next rule gets its turn."""

    def _boom(c: object) -> None:
        raise RuntimeError("rule exploded")

    monkeypatch.setattr(
        pipeline_rules,
        "RESOLUTION_RULES",
        (("R_boom", _boom), ("R7_supported", pipeline_rules._r_supported)),
    )

    frame = _frame("Reagent is stored cold.")
    evidence = [
        pipeline_rules.PassageEvidence(
            passage_id="p1",
            retrieval_score=0.9,
            label="entail",
            score=0.95,
            p_entail=0.95,
            p_contradict=0.01,
            eligible_for=frozenset({"support", "refute"}),
        )
    ]
    degree, null_reason, citations, notes = resolve(frame, evidence, source_boundary=None)

    assert degree == "supported"
    assert citations == ("p1",)
    assert any("R_boom" in n and "RuntimeError" in n for n in notes)
