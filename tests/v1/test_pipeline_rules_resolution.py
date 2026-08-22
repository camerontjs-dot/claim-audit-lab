"""Stage-4 resolution table, union eligibility, and verdict serialization (CAL v2).

The v2 branch landed the resolution table `R1..R8` and the whole union
eligibility path with no direct tests: `test_pipeline_rules.py` exercised R2, R3
and one end-to-end supported case, leaving R1, R4, R5, R6, R8, `qualify_union`
and `V2Verdict.as_dict` unmeasured. CAL-REQ-054 holds `src/` to 95% branch
coverage, and a decision layer's precedence table is the part of it least
tolerable to leave unpinned: the order *is* the policy.
"""

from __future__ import annotations

from claim_audit_lab.v1.impl.pipeline_rules import (
    CONTRADICTED_THRESHOLD,
    SUPPORTED_THRESHOLD,
    ClaimFrame,
    PassageEvidence,
    qualify_union,
    resolve,
    run_v2,
)


def _frame(**kw: object) -> ClaimFrame:
    defaults: dict[str, object] = {
        "text": "Retention samples are held for six months.",
        "mode": "ordinary",
        "mode_source": "declared",
        "polarity": "affirmative",
        "admissible": True,
        "quantities": [],
        "token_count": 7,
        "sentence_type": "declarative",
    }
    defaults.update(kw)
    return ClaimFrame(**defaults)  # type: ignore[arg-type]


def _passage(
    pid: str,
    label: str,
    score: float,
    *,
    roles: frozenset[str] = frozenset({"support", "refute"}),
    members: tuple[str, ...] = (),
    retrieval: float = 0.9,
) -> PassageEvidence:
    return PassageEvidence(
        passage_id=pid,
        retrieval_score=retrieval,
        label=label,
        score=score,
        p_entail=None,
        p_contradict=None,
        eligible_for=roles,  # type: ignore[arg-type]
        members=members,
    )


# ---------------------------------------------------------------------------
# Stage 4 — the precedence table
# ---------------------------------------------------------------------------


def test_r1_named_gap_refutes_only_with_the_caller_flag() -> None:
    """The boundary alone does not refute; the flag is the whole discriminator."""
    frame = _frame(mode="coverage", polarity="negative")

    degree, null_reason, citations, notes = resolve(
        frame,
        [],
        source_boundary="named_missing_material",
        nothing_admitted=True,
        claimed_material_is_a_named_gap=True,
    )
    assert degree == "contradicted"
    assert null_reason is None
    assert any("R1_named_gap" in n for n in notes)

    # Same boundary, flag absent: R1 declines and a later rule decides.
    degree_without, _, _, notes_without = resolve(
        frame,
        [],
        source_boundary="named_missing_material",
        nothing_admitted=True,
        claimed_material_is_a_named_gap=False,
    )
    assert degree_without == "not_checkable"
    assert not any("R1_named_gap" in n for n in notes_without)


def test_r2_exhaustive_source_is_refuted_by_a_positive_complement() -> None:
    """Silence settles a coverage claim only while nothing entails the opposite."""
    frame = _frame(mode="coverage", polarity="negative")
    complement = [_passage("p1", "entail", 0.95)]

    degree, _, citations, notes = resolve(
        frame, complement, source_boundary="exhaustive", nothing_admitted=False
    )
    assert degree == "contradicted"
    assert citations == ("p1",)
    assert any("R2_coverage_exhaustive" in n for n in notes)


def test_r4_no_evidence_precedes_the_ordinary_rules() -> None:
    degree, null_reason, citations, notes = resolve(
        _frame(), [], source_boundary=None, nothing_admitted=True
    )
    assert (degree, null_reason) == ("not_checkable", "no_evidence")
    assert citations == ()
    assert any("R4_no_evidence" in n for n in notes)


def test_r5_conflicting_evidence_settles_nothing() -> None:
    """v1 aggregates to a maximum and picks one; this refuses to."""
    evidence = [
        _passage("p1", "entail", 0.95),
        _passage("p2", "contradict", 0.95),
    ]
    degree, null_reason, citations, notes = resolve(_frame(), evidence, source_boundary=None)
    assert (degree, null_reason) == ("not_checkable", "not_resolvable")
    assert set(citations) == {"p1", "p2"}
    assert any("R5_conflicting" in n for n in notes)


def test_r6_refuted_requires_eligibility_not_just_a_reading() -> None:
    """A passage that may not refute cannot produce a contradiction."""
    ineligible = [_passage("p1", "contradict", 0.99, roles=frozenset({"support"}))]
    degree, null_reason, _, _ = resolve(_frame(), ineligible, source_boundary=None)
    assert (degree, null_reason) == ("not_checkable", "no_signal")

    eligible = [_passage("p1", "contradict", 0.99)]
    degree, _, citations, notes = resolve(_frame(), eligible, source_boundary=None)
    assert degree == "contradicted"
    assert citations == ("p1",)
    assert any("R6_refuted" in n for n in notes)


def test_r8_no_signal_is_the_terminal_outcome() -> None:
    """Evidence admitted and eligible, nothing reading above threshold."""
    below = [_passage("p1", "entail", SUPPORTED_THRESHOLD - 0.01)]
    degree, null_reason, citations, notes = resolve(_frame(), below, source_boundary=None)
    assert (degree, null_reason) == ("not_checkable", "no_signal")
    assert citations == ()
    assert any("R8_no_signal" in n for n in notes)


def test_thresholds_are_inclusive_at_the_boundary() -> None:
    at_bound = [_passage("p1", "entail", SUPPORTED_THRESHOLD)]
    degree, _, _, _ = resolve(_frame(), at_bound, source_boundary=None)
    assert degree == "supported"

    at_contra = [_passage("p1", "contradict", CONTRADICTED_THRESHOLD)]
    degree, _, _, _ = resolve(_frame(), at_contra, source_boundary=None)
    assert degree == "contradicted"


def test_a_quantitative_verdict_carries_the_d12_note() -> None:
    frame = _frame(quantities=[6])
    _, _, _, notes = resolve(frame, [_passage("p1", "entail", 0.95)], source_boundary=None)
    assert any("D12" in n for n in notes)


def test_citation_prefers_the_narrowest_evidence() -> None:
    """A union verdict should send a reviewer to the single passage that decides."""
    evidence = [
        _passage("p1+p2", "entail", 0.96, members=("p1", "p2")),
        _passage("p1", "entail", 0.95),
    ]
    degree, _, citations, _ = resolve(_frame(), evidence, source_boundary=None)
    assert degree == "supported"
    assert citations == ("p1",)


def test_citation_falls_back_to_the_union_when_only_a_union_decides() -> None:
    evidence = [_passage("p1+p2", "entail", 0.96, members=("p1", "p2"))]
    _, _, citations, _ = resolve(_frame(), evidence, source_boundary=None)
    assert citations == ("p1+p2",)


# ---------------------------------------------------------------------------
# Union eligibility — inherited, never recomputed
# ---------------------------------------------------------------------------


def test_a_union_inherits_the_least_eligible_member() -> None:
    members = [
        _passage("p1", "contradict", 0.95),
        _passage("p2", "contradict", 0.95, roles=frozenset({"support"})),
    ]
    roles, removals = qualify_union(_frame(), members, "p1+p2")

    assert roles == frozenset({"support"})
    inherits = [r for r in removals if r.predicate == "Q3_union_inherits"]
    assert len(inherits) == 1
    assert inherits[0].detail["member"] == "p2"


def test_a_union_may_support_a_universal_but_may_not_refute_one() -> None:
    """Refuting a universal needs a counterexample the source actually affirms."""
    members = [_passage("p1", "contradict", 0.95), _passage("p2", "contradict", 0.95)]
    roles, removals = qualify_union(_frame(universal=True), members, "p1+p2")

    assert "refute" not in roles
    assert "support" in roles
    assert any(r.predicate == "Q4_union_universal" for r in removals)


def test_an_empty_union_is_eligible_for_nothing() -> None:
    roles, removals = qualify_union(_frame(), [], "empty")
    assert roles == frozenset()
    assert removals == []


def test_run_v2_composes_unions_from_caller_supplied_readings() -> None:
    verdict = run_v2(
        claim_text="Retention samples are held for six months.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 7,
            "sentence_type": "declarative",
        },
        retrieval=[{"passage_id": "p1", "score": 0.8}, {"passage_id": "p2", "score": 0.8}],
        entailment=[
            {"passage_id": "p1", "label": "neutral", "score": 0.6},
            {"passage_id": "p2", "label": "neutral", "score": 0.6},
        ],
        trust_levels={"p1": "primary", "p2": "primary"},
        unions=[{"members": ["p1", "p2"], "label": "entail", "score": 0.94}],
    )
    # Neither single passage reads above threshold; the union does.
    assert verdict.degree == "supported"
    assert verdict.deciding_passages == ("p1+p2",)


def test_a_union_naming_one_present_member_is_skipped() -> None:
    verdict = run_v2(
        claim_text="Retention samples are held for six months.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 7,
            "sentence_type": "declarative",
        },
        retrieval=[{"passage_id": "p1", "score": 0.8}],
        entailment=[{"passage_id": "p1", "label": "neutral", "score": 0.6}],
        unions=[{"members": ["p1", "absent"], "label": "entail", "score": 0.99}],
    )
    assert verdict.degree == "not_checkable"
    assert verdict.null_reason == "no_signal"


# ---------------------------------------------------------------------------
# Stage boundaries and the record
# ---------------------------------------------------------------------------


def test_an_admitted_passage_with_no_entailment_is_recorded() -> None:
    """Admitted-but-never-entailed is a stage-3 gap, not an empty retrieval.

    The passage cleared the floor, so `nothing_admitted` is False and R4 declines;
    the set is simply empty by the time stage 4 runs, which is `no_signal`. The
    distinction is the point of the record: a reviewer can see that a passage was
    held and then lost, rather than that nothing was retrieved.
    """
    verdict = run_v2(
        claim_text="Retention samples are held for six months.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 7,
            "sentence_type": "declarative",
        },
        retrieval=[{"passage_id": "p1", "score": 0.9}],
        entailment=[],
    )
    dropped = [r for r in verdict.removals if r.predicate == "entailment_present"]
    assert len(dropped) == 1
    assert dropped[0].stage == "3-score"
    assert verdict.null_reason == "no_signal"


def test_a_held_but_wholly_ineligible_set_stops_at_stage_two() -> None:
    """`all_ineligible` needs every role gone, which is Q3's both-ways drop.

    Q1 and Q2 only ever remove `refute`, so a background or out-of-scope passage
    stays eligible to support. A passage that entails the claim *and* its
    negation establishes neither, and that is the one predicate that empties the
    set.
    """
    verdict = run_v2(
        claim_text="Chamber CH-04 recorded no excursions this quarter.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 8,
            "sentence_type": "declarative",
        },
        retrieval=[{"passage_id": "p1", "score": 0.9}],
        entailment=[{"passage_id": "p1", "label": "entail", "score": 0.95}],
        negated_entailment=[{"passage_id": "p1", "label": "entail", "score": 0.95}],
        trust_levels={"p1": "primary"},
    )
    assert verdict.degree == "not_checkable"
    assert verdict.null_reason == "all_ineligible"
    assert verdict.stage_reached == "2-qualify"


def test_q1_and_q2_leave_a_passage_able_to_support() -> None:
    """One bit cannot say "may not refute, may still support"; two roles can."""
    verdict = run_v2(
        claim_text="Chamber CH-04 recorded no excursions this quarter.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 8,
            "sentence_type": "declarative",
        },
        retrieval=[{"passage_id": "p1", "score": 0.9}],
        entailment=[{"passage_id": "p1", "label": "contradict", "score": 0.98}],
        trust_levels={"p1": "background"},
        claim_scope=frozenset({"CH-04"}),
        passage_scope={"p1": frozenset({"CH-07"})},
    )
    # Refutation withheld by both Q1 and Q2, but the passage is not ineligible.
    assert verdict.degree == "not_checkable"
    assert verdict.null_reason == "no_signal"
    assert {r.predicate for r in verdict.removals} >= {"Q1_provenance", "Q2_scope"}


def test_near_miss_passages_are_reported_distinctly_from_an_empty_retrieval() -> None:
    verdict = run_v2(
        claim_text="Retention samples are held for six months.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 7,
            "sentence_type": "declarative",
        },
        retrieval=[{"passage_id": "p1", "score": 0.39}, {"passage_id": "p2", "score": 0.05}],
        entailment=[],
    )
    assert verdict.null_reason == "no_evidence"
    assert any("near-miss band" in n for n in verdict.notes)


def test_an_inadmissible_claim_stops_at_stage_zero() -> None:
    verdict = run_v2(
        claim_text="Is the sample retained?",
        features={"claim_token_count": 4, "sentence_type": "question"},
        retrieval=[{"passage_id": "p1", "score": 0.9}],
        entailment=[{"passage_id": "p1", "label": "entail", "score": 0.99}],
    )
    assert verdict.degree == "not_checkable"
    assert verdict.null_reason == "out_of_form"
    assert verdict.stage_reached == "0-frame"


def test_a_parsed_mode_is_recorded_as_guessed() -> None:
    guessed = run_v2(
        claim_text="Retention samples are held for six months.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 7,
            "sentence_type": "declarative",
        },
        retrieval=[],
        entailment=[],
    )
    assert guessed.mode_was_guessed is True

    declared = run_v2(
        claim_text="Retention samples are held for six months.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 7,
            "sentence_type": "declarative",
        },
        retrieval=[],
        entailment=[],
        declared_mode="ordinary",
    )
    assert declared.mode_was_guessed is False


def test_as_dict_is_a_complete_serializable_record() -> None:
    verdict = run_v2(
        claim_text="Chamber CH-04 recorded no excursions this quarter.",
        features={
            "has_explicit_negation": False,
            "claim_token_count": 8,
            "sentence_type": "declarative",
        },
        retrieval=[
            {"passage_id": "p1", "score": 0.9},
            {"passage_id": "p2", "score": 0.9},  # admitted, never entailed -> no detail
            {"passage_id": "p3", "score": 0.30},  # below floor -> carries detail
        ],
        entailment=[{"passage_id": "p1", "label": "contradict", "score": 0.98}],
        trust_levels={"p1": "background"},
    )
    payload = verdict.as_dict()

    assert payload["degree"] == verdict.degree
    assert payload["stage_reached"] == verdict.stage_reached
    assert payload["n_removed"] == len(verdict.removals)
    assert isinstance(payload["deciding_passages"], list)
    assert isinstance(payload["notes"], list)

    # A removal carrying detail keeps it; one without omits the key entirely.
    with_detail = [r for r in payload["removals"] if "detail" in r]
    without_detail = [r for r in payload["removals"] if "detail" not in r]
    assert with_detail and without_detail

    import json

    json.dumps(payload)  # the record must survive a trace write
