from __future__ import annotations

from copy import deepcopy
import json

import pytest
from pydantic import ValidationError

from portable_bound_authority_receipt_rc3 import (
    issue_portable_warrant,
    serialize_portable_warrant,
    verify_and_derive_categorical_relation,
)
from proposition_claim_binding_rc4 import (
    ComparisonProposition,
    PropositionBindingRefusal,
    compose_categorical_relations,
    issue_proposition_binding,
    proposition_semantic_digest,
    serialize_proposition_binding,
    verify_bound_claim_warrant_and_derive_relation,
    verify_proposition_binding,
)


WARRANT_KEY = b"w" * 32
PROP_KEY = b"p" * 32


def _authority(_: dict) -> dict[str, str]:
    return {
        "authority_status": "WARRANTED",
        "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
    }


def _case() -> dict:
    subject = "subject:comparison"
    return {
        "execution_state": "completed",
        "evidence_admitted": True,
        "authority_subject_id": subject,
        "raw_source_id": "source:1",
        "authority_subject_source_id": "source:1",
        "raw_bundle_id": "bundle:1",
        "authority_subject_bundle_id": "bundle:1",
        "raw_passage_id": "passage:1",
        "authority_subject_passage_id": "passage:1",
        "admitted_passage_span": [0, 20],
        "raw_claim_id": "claim:comparison",
        "authority_subject_claim_id": "claim:comparison",
        "target_atom_id": "atom:a-gt-b",
        "authority_subject_atom_id": "atom:a-gt-b",
        "proposal": {
            "authority_subject_id": subject,
            "family": "comparison",
            "source_span": [0, 20],
            "fields": {
                "lhs_entity": "A",
                "rhs_entity": "B",
                "comparison_direction": "greater_than",
            },
            "extra_modifiers": [],
        },
        "assertion": {
            "authority_subject_id": subject,
            "state": "asserted",
        },
        "operator": {
            "authority_subject_id": subject,
            "domain": "comparison",
            "applicability": "applicable",
            "governed_span": [0, 20],
            "jurisdiction_fields": [
                "lhs_entity",
                "rhs_entity",
                "comparison_direction",
            ],
        },
        "field_warrants": {
            "lhs_entity": {
                "authority_subject_id": subject,
                "span": [0, 20],
                "status": "established",
                "value": "A",
            },
            "rhs_entity": {
                "authority_subject_id": subject,
                "span": [0, 20],
                "status": "established",
                "value": "B",
            },
            "comparison_direction": {
                "authority_subject_id": subject,
                "span": [0, 20],
                "status": "established",
                "value": "greater_than",
            },
        },
        "required_fields": ["lhs_entity", "rhs_entity", "comparison_direction"],
        "composition": {
            "authority_subject_id": subject,
            "required": False,
            "state": "not_required",
        },
        "aperture": {
            "authority_subject_id": subject,
            "required": False,
            "state": "not_required",
        },
        "case_id": "diagnostic",
        "instrument_ids": ["diagnostic"],
        "reader_agreement_count": 1,
    }


def _prop(
    *,
    claim_id: str = "claim:comparison",
    lhs: str = "A",
    rhs: str = "B",
    direction: str = "greater_than",
) -> ComparisonProposition:
    return ComparisonProposition(
        claim_id=claim_id,
        family="comparison",
        lhs_entity=lhs,
        rhs_entity=rhs,
        comparison_direction=direction,
    )


def _warrant(case: dict) -> str:
    receipt = issue_portable_warrant(
        case=case,
        authority_evaluator=_authority,
        key=WARRANT_KEY,
        key_id="warrant-key",
    )
    return serialize_portable_warrant(receipt)


def _prop_receipt(prop: ComparisonProposition) -> str:
    receipt = issue_proposition_binding(
        proposition=prop,
        key=PROP_KEY,
        key_id="prop-key",
    )
    return serialize_proposition_binding(receipt)


def test_weak_rc3_same_claim_substitution_changes_conclusion():
    case = _case()
    warrant = _warrant(case)
    baseline = _prop()
    substituted = _prop(direction="less_than")

    first = verify_and_derive_categorical_relation(
        case=case,
        proposition=baseline,
        receipt_transport=warrant,
        trusted_keys={"warrant-key": WARRANT_KEY},
    )
    second = verify_and_derive_categorical_relation(
        case=case,
        proposition=substituted,
        receipt_transport=warrant,
        trusted_keys={"warrant-key": WARRANT_KEY},
    )
    assert first.relation == "SUPPORTS"
    assert second.relation == "REFUTES"
    assert compose_categorical_relations(baseline, (first,)).verdict == "supported"
    assert compose_categorical_relations(substituted, (second,)).verdict == "contradicted"


def test_stale_proposition_receipt_refuses_same_claim_direction_substitution():
    case = _case()
    baseline = _prop()
    substituted = _prop(direction="less_than")
    with pytest.raises(PropositionBindingRefusal, match="PROPOSITION_DIGEST_MISMATCH"):
        verify_bound_claim_warrant_and_derive_relation(
            case=case,
            proposition=substituted,
            warrant_receipt_transport=_warrant(case),
            warrant_trusted_keys={"warrant-key": WARRANT_KEY},
            proposition_receipt_transport=_prop_receipt(baseline),
            proposition_trusted_keys={"prop-key": PROP_KEY},
        )


def test_recomputed_digest_with_stale_mac_is_refused():
    baseline = _prop()
    substituted = _prop(direction="less_than")
    payload = json.loads(_prop_receipt(baseline))
    payload["body"]["proposition_digest"] = proposition_semantic_digest(substituted)
    forged = json.dumps(payload)
    with pytest.raises(PropositionBindingRefusal, match="MAC_MISMATCH"):
        verify_proposition_binding(
            proposition=substituted,
            receipt_transport=forged,
            trusted_keys={"prop-key": PROP_KEY},
        )


@pytest.mark.parametrize(
    "substituted",
    [
        _prop(lhs="X", rhs="B"),
        _prop(lhs="A", rhs="Y"),
        _prop(claim_id="claim:replacement"),
        _prop(lhs="B", rhs="A", direction="less_than"),
    ],
)
def test_exact_identity_substitutions_are_refused(substituted: ComparisonProposition):
    baseline = _prop()
    expected = "CLAIM_ID_MISMATCH" if substituted.claim_id != baseline.claim_id else "PROPOSITION_DIGEST_MISMATCH"
    with pytest.raises(PropositionBindingRefusal, match=expected):
        verify_proposition_binding(
            proposition=substituted,
            receipt_transport=_prop_receipt(baseline),
            trusted_keys={"prop-key": PROP_KEY},
        )


def test_swapped_inverse_can_be_separately_bound_and_remains_supported():
    case = _case()
    swapped = _prop(lhs="B", rhs="A", direction="less_than")
    relation = verify_bound_claim_warrant_and_derive_relation(
        case=case,
        proposition=swapped,
        warrant_receipt_transport=_warrant(case),
        warrant_trusted_keys={"warrant-key": WARRANT_KEY},
        proposition_receipt_transport=_prop_receipt(swapped),
        proposition_trusted_keys={"prop-key": PROP_KEY},
    )
    assert relation.relation == "SUPPORTS"
    assert compose_categorical_relations(swapped, (relation,)).verdict == "supported"


def test_wrong_key_and_mac_mutation_are_refused():
    baseline = _prop()
    transport = _prop_receipt(baseline)
    with pytest.raises(PropositionBindingRefusal, match="MAC_MISMATCH"):
        verify_proposition_binding(
            proposition=baseline,
            receipt_transport=transport,
            trusted_keys={"prop-key": b"x" * 32},
        )

    payload = json.loads(transport)
    payload["mac"] = ("0" if payload["mac"][0] != "0" else "1") + payload["mac"][1:]
    with pytest.raises(PropositionBindingRefusal, match="MAC_MISMATCH"):
        verify_proposition_binding(
            proposition=baseline,
            receipt_transport=json.dumps(payload),
            trusted_keys={"prop-key": PROP_KEY},
        )


def test_strict_receipt_schema_and_duplicate_keys():
    baseline = _prop()
    payload = json.loads(_prop_receipt(baseline))

    partial = deepcopy(payload)
    del partial["body"]["proposition_digest"]
    with pytest.raises(PropositionBindingRefusal, match="INVALID_RECEIPT_SCHEMA"):
        verify_proposition_binding(
            proposition=baseline,
            receipt_transport=json.dumps(partial),
            trusted_keys={"prop-key": PROP_KEY},
        )

    unknown = deepcopy(payload)
    unknown["unexpected"] = True
    with pytest.raises(PropositionBindingRefusal, match="INVALID_RECEIPT_SCHEMA"):
        verify_proposition_binding(
            proposition=baseline,
            receipt_transport=json.dumps(unknown),
            trusted_keys={"prop-key": PROP_KEY},
        )

    duplicate = '{"body":{},"body":{},"auth_algorithm":"hmac-sha256","mac":"' + ("0" * 64) + '"}'
    with pytest.raises(PropositionBindingRefusal, match="DUPLICATE_JSON_KEY"):
        verify_proposition_binding(
            proposition=baseline,
            receipt_transport=duplicate,
            trusted_keys={"prop-key": PROP_KEY},
        )


def test_pretty_reordered_json_and_model_reconstruction_verify():
    baseline = _prop()
    receipt = issue_proposition_binding(
        proposition=baseline,
        key=PROP_KEY,
        key_id="prop-key",
    )
    pretty = serialize_proposition_binding(receipt, pretty=True)
    reconstructed = ComparisonProposition.model_validate(
        {
            "comparison_direction": "greater_than",
            "rhs_entity": "B",
            "lhs_entity": "A",
            "family": "comparison",
            "claim_id": "claim:comparison",
        }
    )
    assert proposition_semantic_digest(reconstructed) == proposition_semantic_digest(baseline)
    verified = verify_proposition_binding(
        proposition=reconstructed,
        receipt_transport=pretty,
        trusted_keys={"prop-key": PROP_KEY},
    )
    assert verified.body.claim_id == baseline.claim_id


def test_forbidden_scalar_and_polarity_inputs_remain_rejected():
    base = _prop().model_dump(mode="json")
    for key, value in (
        ("score", 0.9),
        ("confidence", 0.9),
        ("threshold", 0.5),
        ("channel", "support"),
        ("relation_hint", "SUPPORTS"),
    ):
        with pytest.raises(ValidationError):
            ComparisonProposition.model_validate({**base, key: value})
