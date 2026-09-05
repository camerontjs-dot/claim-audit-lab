from __future__ import annotations

from copy import deepcopy
import json

import pytest

from categorical_warranted_relation_rc1 import ComparisonProposition
from portable_bound_authority_receipt_rc3 import (
    PortableReceiptIssuanceRefusal,
    PortableReceiptRefusal,
    authority_subject_digest,
    issue_portable_warrant,
    parse_portable_warrant,
    serialize_portable_warrant,
    verify_and_derive_categorical_relation,
    verify_portable_warrant,
)


KEY = b"k" * 32
KEY_ID = "research-test-key"


def _case() -> dict:
    subject = "authority:subject:test"
    atom_id = "atom:test:a-gt-b"
    claim_id = "claim:test"
    return {
        "case_id": "test-case",
        "execution_state": "completed",
        "evidence_admitted": True,
        "authority_subject_id": subject,
        "raw_source_id": "source:test",
        "authority_subject_source_id": "source:test",
        "raw_bundle_id": "bundle:test",
        "authority_subject_bundle_id": "bundle:test",
        "raw_passage_id": "passage:test",
        "authority_subject_passage_id": "passage:test",
        "admitted_passage_span": [0, 100],
        "raw_claim_id": claim_id,
        "authority_subject_claim_id": claim_id,
        "target_atom_id": atom_id,
        "authority_subject_atom_id": atom_id,
        "proposal": {
            "authority_subject_id": subject,
            "family": "comparison",
            "source_span": [10, 20],
            "extra_modifiers": [],
            "fields": {
                "lhs_entity": "A",
                "rhs_entity": "B",
                "comparison_direction": "greater_than",
            },
        },
        "assertion": {"authority_subject_id": subject, "state": "asserted"},
        "operator": {
            "authority_subject_id": subject,
            "domain": "comparison",
            "applicability": "applicable",
            "governed_span": [0, 100],
            "jurisdiction_fields": ["lhs_entity", "rhs_entity", "comparison_direction"],
        },
        "field_warrants": {
            "lhs_entity": {
                "authority_subject_id": subject,
                "span": [10, 12],
                "status": "established",
                "value": "A",
            },
            "rhs_entity": {
                "authority_subject_id": subject,
                "span": [13, 15],
                "status": "established",
                "value": "B",
            },
            "comparison_direction": {
                "authority_subject_id": subject,
                "span": [16, 20],
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
        "instrument_ids": ["diagnostic"],
        "reader_agreement_count": 1,
    }


def _warranted(_: dict) -> dict:
    return {"authority_status": "WARRANTED", "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED"}


def _rejected(_: dict) -> dict:
    return {"authority_status": "REJECTED", "reason": "FIELD_VALUE_MISMATCH:comparison_direction"}


def _target() -> ComparisonProposition:
    return ComparisonProposition(
        claim_id="claim:test",
        family="comparison",
        lhs_entity="A",
        rhs_entity="B",
        comparison_direction="greater_than",
    )


def test_issue_serialize_parse_verify_and_derive_round_trip():
    case = _case()
    receipt = issue_portable_warrant(
        case=case,
        authority_evaluator=_warranted,
        key=KEY,
        key_id=KEY_ID,
    )
    transport = serialize_portable_warrant(receipt)
    parsed = parse_portable_warrant(transport)
    assert parsed == receipt
    verified = verify_portable_warrant(
        case=case,
        receipt_transport=transport,
        trusted_keys={KEY_ID: KEY},
    )
    assert verified == receipt
    relation = verify_and_derive_categorical_relation(
        case=case,
        proposition=_target(),
        receipt_transport=transport,
        trusted_keys={KEY_ID: KEY},
    )
    assert relation.relation == "SUPPORTS"


def test_stale_receipt_rejects_same_id_payload_mutation():
    case = _case()
    receipt = issue_portable_warrant(
        case=case,
        authority_evaluator=_warranted,
        key=KEY,
        key_id=KEY_ID,
    )
    mutated = deepcopy(case)
    mutated["proposal"]["fields"]["comparison_direction"] = "less_than"
    with pytest.raises(PortableReceiptRefusal, match="SUBJECT_DIGEST_MISMATCH"):
        verify_portable_warrant(
            case=mutated,
            receipt_transport=serialize_portable_warrant(receipt),
            trusted_keys={KEY_ID: KEY},
        )


def test_receipt_body_tamper_fails_mac_before_authority_use():
    case = _case()
    receipt = issue_portable_warrant(
        case=case,
        authority_evaluator=_warranted,
        key=KEY,
        key_id=KEY_ID,
    )
    payload = receipt.model_dump(mode="json")
    payload["body"]["subject_digest"] = "0" * 64
    tampered = json.dumps(payload)
    with pytest.raises(PortableReceiptRefusal, match="MAC_MISMATCH"):
        verify_portable_warrant(
            case=case,
            receipt_transport=tampered,
            trusted_keys={KEY_ID: KEY},
        )


def test_wrong_key_and_unknown_key_id_fail_closed():
    case = _case()
    receipt = issue_portable_warrant(
        case=case,
        authority_evaluator=_warranted,
        key=KEY,
        key_id=KEY_ID,
    )
    transport = serialize_portable_warrant(receipt)
    with pytest.raises(PortableReceiptRefusal, match="MAC_MISMATCH"):
        verify_portable_warrant(
            case=case,
            receipt_transport=transport,
            trusted_keys={KEY_ID: b"x" * 32},
        )
    with pytest.raises(PortableReceiptRefusal, match="UNTRUSTED_KEY_ID"):
        verify_portable_warrant(
            case=case,
            receipt_transport=transport,
            trusted_keys={"other-key": KEY},
        )


def test_nonwarranted_producer_cannot_issue():
    with pytest.raises(PortableReceiptIssuanceRefusal):
        issue_portable_warrant(
            case=_case(),
            authority_evaluator=_rejected,
            key=KEY,
            key_id=KEY_ID,
        )


def test_duplicate_json_keys_are_rejected():
    duplicate = '{"body":{},"body":{},"auth_algorithm":"hmac-sha256","mac":"' + ("0" * 64) + '"}'
    with pytest.raises(PortableReceiptRefusal, match="DUPLICATE_JSON_KEY"):
        parse_portable_warrant(duplicate)


def test_unknown_receipt_fields_are_rejected():
    receipt = issue_portable_warrant(
        case=_case(), authority_evaluator=_warranted, key=KEY, key_id=KEY_ID
    )
    payload = receipt.model_dump(mode="json")
    payload["unexpected"] = "nope"
    with pytest.raises(PortableReceiptRefusal, match="INVALID_RECEIPT_SCHEMA"):
        parse_portable_warrant(json.dumps(payload))


def test_transport_order_and_whitespace_do_not_change_verification():
    case = _case()
    receipt = issue_portable_warrant(
        case=case, authority_evaluator=_warranted, key=KEY, key_id=KEY_ID
    )
    payload = receipt.model_dump(mode="json")
    reordered_body = dict(reversed(list(payload["body"].items())))
    reordered = {
        "mac": payload["mac"],
        "auth_algorithm": payload["auth_algorithm"],
        "body": reordered_body,
    }
    transport = json.dumps(reordered, indent=4, ensure_ascii=False)
    verified = verify_portable_warrant(
        case=case,
        receipt_transport=transport,
        trusted_keys={KEY_ID: KEY},
    )
    assert verified == receipt


def test_case_dictionary_insertion_order_is_canonicalized():
    case = _case()
    reordered = dict(reversed(list(case.items())))
    reordered["proposal"] = dict(reversed(list(case["proposal"].items())))
    reordered["proposal"]["fields"] = dict(
        reversed(list(case["proposal"]["fields"].items()))
    )
    assert authority_subject_digest(reordered) == authority_subject_digest(case)


def test_diagnostic_metadata_is_not_in_binding_projection():
    case = _case()
    mutated = deepcopy(case)
    mutated["case_id"] = "different-case-id"
    mutated["instrument_ids"] = ["one", "two", "three"]
    mutated["reader_agreement_count"] = 999
    assert authority_subject_digest(mutated) == authority_subject_digest(case)


def test_missing_binding_field_fails_closed():
    case = _case()
    del case["operator"]
    with pytest.raises(PortableReceiptRefusal, match="BINDING_FIELD_MISSING"):
        authority_subject_digest(case)
