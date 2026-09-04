from __future__ import annotations

from copy import deepcopy
import inspect

import pytest
from pydantic import ValidationError

from atomic_warranted_relation_rc2 import (
    AtomicAuthorityRefusal,
    ComparisonProposition,
    assess_and_derive_categorical_relation,
    compose_categorical_relations,
)


def _target() -> ComparisonProposition:
    return ComparisonProposition(
        claim_id="claim:comparison",
        family="comparison",
        lhs_entity="A",
        rhs_entity="B",
        comparison_direction="greater_than",
    )


def _case(direction: str = "greater_than") -> dict:
    return {
        "raw_claim_id": "claim:comparison",
        "authority_subject_claim_id": "claim:comparison",
        "target_atom_id": "atom:comparison",
        "authority_subject_atom_id": "atom:comparison",
        "proposal": {
            "family": "comparison",
            "fields": {
                "lhs_entity": "A",
                "rhs_entity": "B",
                "comparison_direction": direction,
            },
        },
        "field_warrants": {
            "comparison_direction": {"value": "greater_than"},
        },
    }


def _stub_rc8j(case: dict) -> dict:
    if case["target_atom_id"] != case["authority_subject_atom_id"]:
        return {"authority_status": "REJECTED", "reason": "AUTHORITY_ATOM_IDENTITY_MISMATCH"}
    if case["raw_claim_id"] != case["authority_subject_claim_id"]:
        return {"authority_status": "REJECTED", "reason": "AUTHORITY_CLAIM_MISMATCH"}
    if (
        case["proposal"]["fields"]["comparison_direction"]
        != case["field_warrants"]["comparison_direction"]["value"]
    ):
        return {"authority_status": "REJECTED", "reason": "FIELD_VALUE_MISMATCH:comparison_direction"}
    return {"authority_status": "WARRANTED", "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED"}


def test_public_interface_has_no_authority_result_parameter():
    params = inspect.signature(assess_and_derive_categorical_relation).parameters
    assert "authority_result" not in params
    assert set(params) == {"case", "proposition", "authority_evaluator"}


def test_warranted_support_and_refutation_remain_scoreless():
    target = _target()
    support = assess_and_derive_categorical_relation(
        case=_case("greater_than"), proposition=target, authority_evaluator=_stub_rc8j
    )
    refute_case = _case("less_than")
    refute_case["field_warrants"]["comparison_direction"]["value"] = "less_than"
    refute = assess_and_derive_categorical_relation(
        case=refute_case, proposition=target, authority_evaluator=_stub_rc8j
    )
    assert support.relation == "SUPPORTS"
    assert refute.relation == "REFUTES"
    assert compose_categorical_relations(target, (support,)).verdict == "supported"
    assert compose_categorical_relations(target, (refute,)).verdict == "contradicted"


def test_exact_rc1a_payload_replay_is_refused():
    mutated = _case("less_than")
    # Keep the stale field-warrant value from the formerly warranted A > B atom.
    assert mutated["field_warrants"]["comparison_direction"]["value"] == "greater_than"
    with pytest.raises(AtomicAuthorityRefusal) as exc:
        assess_and_derive_categorical_relation(
            case=mutated, proposition=_target(), authority_evaluator=_stub_rc8j
        )
    assert exc.value.status == "REJECTED"
    assert exc.value.reason == "FIELD_VALUE_MISMATCH:comparison_direction"


def test_identity_and_claim_substitutions_are_refused():
    identity = _case()
    identity["target_atom_id"] = "atom:replacement"
    with pytest.raises(AtomicAuthorityRefusal, match="AUTHORITY_ATOM_IDENTITY_MISMATCH"):
        assess_and_derive_categorical_relation(
            case=identity, proposition=_target(), authority_evaluator=_stub_rc8j
        )

    claim = _case()
    claim["raw_claim_id"] = "claim:replacement"
    with pytest.raises(AtomicAuthorityRefusal, match="AUTHORITY_CLAIM_MISMATCH"):
        assess_and_derive_categorical_relation(
            case=claim, proposition=_target(), authority_evaluator=_stub_rc8j
        )


def test_relation_uses_untouched_snapshot_even_if_evaluator_mutates_its_input():
    caller_case = _case()

    def mutating_evaluator(seen: dict) -> dict:
        observed = _stub_rc8j(seen)
        seen["proposal"]["fields"]["comparison_direction"] = "less_than"
        return observed

    receipt = assess_and_derive_categorical_relation(
        case=caller_case,
        proposition=_target(),
        authority_evaluator=mutating_evaluator,
    )
    assert receipt.relation == "SUPPORTS"
    assert receipt.atom_comparison_direction == "greater_than"


def test_post_call_caller_mutation_cannot_change_receipt():
    caller_case = _case()
    receipt = assess_and_derive_categorical_relation(
        case=caller_case, proposition=_target(), authority_evaluator=_stub_rc8j
    )
    frozen_dump = receipt.model_dump(mode="json")
    caller_case["proposal"]["fields"]["comparison_direction"] = "less_than"
    caller_case["target_atom_id"] = "atom:replacement"
    assert receipt.model_dump(mode="json") == frozen_dump


def test_scalar_and_polarity_inputs_remain_forbidden():
    base = _target().model_dump(mode="json")
    for forbidden in (
        {"score": 0.9},
        {"confidence": 0.9},
        {"threshold": 0.7},
        {"channel": "support"},
        {"relation_hint": "SUPPORTS"},
    ):
        with pytest.raises(ValidationError):
            ComparisonProposition.model_validate({**base, **forbidden})


def test_diagnostic_caller_metadata_does_not_change_relation_under_same_authority():
    baseline = _case()
    baseline["instrument_ids"] = ["one"]
    baseline["reader_agreement_count"] = 1
    mutated = deepcopy(baseline)
    mutated["instrument_ids"] = ["one", "two", "three"]
    mutated["reader_agreement_count"] = 99

    first = assess_and_derive_categorical_relation(
        case=baseline, proposition=_target(), authority_evaluator=_stub_rc8j
    )
    second = assess_and_derive_categorical_relation(
        case=mutated, proposition=_target(), authority_evaluator=_stub_rc8j
    )
    assert first == second
