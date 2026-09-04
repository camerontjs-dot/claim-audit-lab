from __future__ import annotations

from copy import deepcopy

import pytest
from pydantic import ValidationError

from categorical_warranted_relation_rc1 import (
    ComparisonProposition,
    compose_categorical_relations,
    derive_categorical_relation,
)


def _authority(status: str = "WARRANTED", reason: str = "ALL_REQUIRED_WARRANT_ESTABLISHED"):
    return {"authority": {"status": status, "reason": reason}}


def _case(
    *,
    atom_id: str = "atom:a-gt-b",
    lhs: str = "A",
    rhs: str = "B",
    direction: str = "greater_than",
):
    return {
        "raw_claim_id": "claim:comparison",
        "target_atom_id": atom_id,
        "proposal": {
            "family": "comparison",
            "fields": {
                "lhs_entity": lhs,
                "rhs_entity": rhs,
                "comparison_direction": direction,
            },
        },
        "instrument_ids": ["diagnostic-only"],
        "reader_agreement_count": 1,
    }


def _target(direction: str = "greater_than", lhs: str = "A", rhs: str = "B"):
    return ComparisonProposition(
        claim_id="claim:comparison",
        family="comparison",
        lhs_entity=lhs,
        rhs_entity=rhs,
        comparison_direction=direction,
    )


def test_same_direction_supports_and_opposite_direction_refutes():
    target = _target()
    supports = derive_categorical_relation(case=_case(), authority_result=_authority(), proposition=target)
    refutes = derive_categorical_relation(
        case=_case(atom_id="atom:a-lt-b", direction="less_than"),
        authority_result=_authority(),
        proposition=target,
    )
    assert supports.relation == "SUPPORTS"
    assert refutes.relation == "REFUTES"
    assert compose_categorical_relations(target, (supports,)).verdict == "supported"
    assert compose_categorical_relations(target, (refutes,)).verdict == "contradicted"


def test_swapped_inverse_is_semantically_equivalent():
    atom = _case()
    swapped_target = _target(direction="less_than", lhs="B", rhs="A")
    receipt = derive_categorical_relation(
        case=atom,
        authority_result=_authority(),
        proposition=swapped_target,
    )
    assert receipt.relation == "SUPPORTS"
    assert compose_categorical_relations(swapped_target, (receipt,)).verdict == "supported"


def test_other_pair_is_irrelevant_and_non_deciding():
    target = _target()
    receipt = derive_categorical_relation(
        case=_case(atom_id="atom:x-gt-y", lhs="X", rhs="Y"),
        authority_result=_authority(),
        proposition=target,
    )
    assert receipt.relation == "IRRELEVANT"
    conclusion = compose_categorical_relations(target, (receipt,))
    assert conclusion.disposition == "abstained"
    assert conclusion.reason_code == "no_deciding_categorical_relation"


def test_unsupported_same_pair_direction_is_unresolved_and_fails_closed():
    target = _target()
    unresolved = derive_categorical_relation(
        case=_case(atom_id="atom:a-at-least-b", direction="at_least"),
        authority_result=_authority(),
        proposition=target,
    )
    support = derive_categorical_relation(
        case=_case(), authority_result=_authority(), proposition=target
    )
    assert unresolved.relation == "UNRESOLVED"
    conclusion = compose_categorical_relations(target, (support, unresolved))
    assert conclusion.disposition == "abstained"
    assert conclusion.reason_code == "unresolved_categorical_relation"


def test_support_plus_irrelevant_remains_supported():
    target = _target()
    support = derive_categorical_relation(
        case=_case(), authority_result=_authority(), proposition=target
    )
    irrelevant = derive_categorical_relation(
        case=_case(atom_id="atom:x-gt-y", lhs="X", rhs="Y"),
        authority_result=_authority(),
        proposition=target,
    )
    conclusion = compose_categorical_relations(target, (support, irrelevant))
    assert conclusion.verdict == "supported"
    assert conclusion.basis_relation_ids == (support.relation_id,)


def test_mixed_is_abstention_and_order_invariant():
    target = _target()
    support = derive_categorical_relation(
        case=_case(), authority_result=_authority(), proposition=target
    )
    refute = derive_categorical_relation(
        case=_case(atom_id="atom:a-lt-b", direction="less_than"),
        authority_result=_authority(),
        proposition=target,
    )
    forward = compose_categorical_relations(target, (support, refute))
    reverse = compose_categorical_relations(target, (refute, support))
    assert forward == reverse
    assert forward.disposition == "abstained"
    assert forward.reason_code == "mixed_categorical_relations"


def test_diagnostic_metadata_cannot_change_relation():
    target = _target()
    baseline_case = _case()
    mutated_case = deepcopy(baseline_case)
    mutated_case["instrument_ids"] = ["one", "two", "three"]
    mutated_case["reader_agreement_count"] = 99
    baseline = derive_categorical_relation(
        case=baseline_case, authority_result=_authority(), proposition=target
    )
    mutated = derive_categorical_relation(
        case=mutated_case, authority_result=_authority(), proposition=target
    )
    assert baseline == mutated


def test_non_warranted_authority_cannot_enter_relation_operator():
    with pytest.raises(ValueError, match="requires WARRANTED authority"):
        derive_categorical_relation(
            case=_case(),
            authority_result=_authority(
                "UNRESOLVED", "AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED"
            ),
            proposition=_target(),
        )


def test_caller_score_channel_and_relation_hint_are_forbidden():
    base = {
        "claim_id": "claim:comparison",
        "family": "comparison",
        "lhs_entity": "A",
        "rhs_entity": "B",
        "comparison_direction": "greater_than",
    }
    for forbidden in (
        {"score": 0.99},
        {"channel": "support"},
        {"relation_hint": "SUPPORTS"},
    ):
        with pytest.raises(ValidationError):
            ComparisonProposition.model_validate({**base, **forbidden})


def test_composer_rejects_receipts_for_different_exact_propositions():
    atom = _case()
    first = _target()
    second = _target(direction="less_than")
    receipt = derive_categorical_relation(
        case=atom, authority_result=_authority(), proposition=first
    )
    with pytest.raises(ValueError, match="exact same proposition"):
        compose_categorical_relations(second, (receipt,))
