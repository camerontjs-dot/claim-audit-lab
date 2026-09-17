# ruff: noqa: I001, E501
from research.deontic_norm_contract_rc0.candidate import relate
from research.deontic_norm_contract_rc0.cohort import CASES, CASE_BY_ID, METAMORPHIC_PAIRS
from research.deontic_norm_contract_rc0.evaluator import oracle_relation


def test_candidate_matches_frozen_oracle_on_every_case() -> None:
    disagreements = []
    for case in CASES:
        observed = relate(case.source, case.query)
        expected = oracle_relation(case.source, case.query)
        if observed != expected:
            disagreements.append((case.case_id, observed, expected))
    assert disagreements == []


def test_candidate_replays_deterministically() -> None:
    first = tuple((case.case_id, relate(case.source, case.query)) for case in CASES)
    second = tuple((case.case_id, relate(case.source, case.query)) for case in CASES)
    assert first == second


def test_candidate_preserves_every_metamorphic_relation_change() -> None:
    for left_id, right_id in METAMORPHIC_PAIRS:
        left = CASE_BY_ID[left_id]
        right = CASE_BY_ID[right_id]
        assert relate(left.source, left.query) != relate(right.source, right.query), (
            left_id,
            right_id,
        )


def test_candidate_does_not_strengthen_obligation_or_restriction_into_permission() -> None:
    for case_id in ("D09", "D11", "D31", "D32"):
        case = CASE_BY_ID[case_id]
        assert relate(case.source, case.query) == oracle_relation(case.source, case.query)


def test_candidate_does_not_erase_modifier_scope() -> None:
    for case_id in ("D16", "D17", "D19", "D20", "D22", "D23", "D24", "D26", "D27", "D28"):
        case = CASE_BY_ID[case_id]
        assert relate(case.source, case.query) == oracle_relation(case.source, case.query)
