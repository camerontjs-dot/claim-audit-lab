"""Research-only proposition-content / claim-identity binding for RC3 consumption.

RC4 adds a second authenticated boundary beside the frozen RC3 atom warrant:
an exact typed proposition payload must be authenticated to its claim_id before
that proposition may be used in proposition-relative categorical relation
derivation.

The HMAC mechanism is a bounded research trust model only. It does not establish
production claim registries, key management, semantic-equivalence normalization,
or production cryptographic architecture.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from categorical_warranted_relation_rc1 import (
    ComparisonProposition,
    WarrantedRelationReceipt,
    compose_categorical_relations,
)
from portable_bound_authority_receipt_rc3 import verify_and_derive_categorical_relation


SCHEMA_VERSION = "cal.bound-proposition.v1"
AUTH_ALGORITHM = "hmac-sha256"
DIGEST_ALGORITHM = "sha256"
MAC_DOMAIN = b"cal.bound-proposition.v1\x00"

TrustedKeys = Mapping[str, bytes]


class _StrictModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class PropositionBindingBody(_StrictModel):
    schema_version: Literal["cal.bound-proposition.v1"]
    key_id: str = Field(min_length=1)
    claim_id: str = Field(min_length=1)
    proposition_digest_algorithm: Literal["sha256"]
    proposition_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class PropositionBindingReceipt(_StrictModel):
    body: PropositionBindingBody
    auth_algorithm: Literal["hmac-sha256"]
    mac: str = Field(pattern=r"^[0-9a-f]{64}$")


class PropositionBindingRefusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise PropositionBindingRefusal("DUPLICATE_JSON_KEY", key)
        out[key] = value
    return out


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise PropositionBindingRefusal("NON_CANONICALIZABLE_JSON", str(exc)) from exc
    return text.encode("utf-8")


def proposition_semantic_projection(proposition: ComparisonProposition) -> dict[str, str]:
    """Return the exact bounded proposition semantics governed by this RC."""
    if not isinstance(proposition, ComparisonProposition):
        raise TypeError("RC4 proposition binding requires ComparisonProposition")
    return {
        "family": proposition.family,
        "lhs_entity": proposition.lhs_entity,
        "rhs_entity": proposition.rhs_entity,
        "comparison_direction": proposition.comparison_direction,
    }


def proposition_semantic_digest(proposition: ComparisonProposition) -> str:
    return hashlib.sha256(
        _canonical_json_bytes(proposition_semantic_projection(proposition))
    ).hexdigest()


def _body_bytes(body: PropositionBindingBody) -> bytes:
    return _canonical_json_bytes(body.model_dump(mode="json"))


def _mac_for_body(body: PropositionBindingBody, key: bytes) -> str:
    if not isinstance(key, bytes) or len(key) < 32:
        raise PropositionBindingRefusal(
            "INVALID_VERIFICATION_KEY", "HMAC key must be at least 32 bytes"
        )
    return hmac.new(key, MAC_DOMAIN + _body_bytes(body), hashlib.sha256).hexdigest()


def issue_proposition_binding(
    *,
    proposition: ComparisonProposition,
    key: bytes,
    key_id: str,
) -> PropositionBindingReceipt:
    """Authenticate an exact typed proposition payload to its claim identity."""
    if not isinstance(proposition, ComparisonProposition):
        raise TypeError("proposition binding producer requires ComparisonProposition")
    if not isinstance(key_id, str) or not key_id:
        raise ValueError("proposition binding producer requires non-empty key_id")

    body = PropositionBindingBody(
        schema_version=SCHEMA_VERSION,
        key_id=key_id,
        claim_id=proposition.claim_id,
        proposition_digest_algorithm=DIGEST_ALGORITHM,
        proposition_digest=proposition_semantic_digest(proposition),
    )
    return PropositionBindingReceipt(
        body=body,
        auth_algorithm=AUTH_ALGORITHM,
        mac=_mac_for_body(body, key),
    )


def serialize_proposition_binding(
    receipt: PropositionBindingReceipt,
    *,
    pretty: bool = False,
) -> str:
    payload = receipt.model_dump(mode="json")
    if pretty:
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return _canonical_json_bytes(payload).decode("utf-8")


def parse_proposition_binding(transport: str | bytes) -> PropositionBindingReceipt:
    if isinstance(transport, bytes):
        try:
            transport = transport.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PropositionBindingRefusal("INVALID_UTF8", str(exc)) from exc
    if not isinstance(transport, str):
        raise PropositionBindingRefusal(
            "INVALID_TRANSPORT", "proposition receipt transport must be str or bytes"
        )
    try:
        payload = json.loads(transport, object_pairs_hook=_reject_duplicate_pairs)
    except PropositionBindingRefusal:
        raise
    except json.JSONDecodeError as exc:
        raise PropositionBindingRefusal("INVALID_JSON", str(exc)) from exc
    try:
        return PropositionBindingReceipt.model_validate(payload)
    except ValidationError as exc:
        raise PropositionBindingRefusal("INVALID_RECEIPT_SCHEMA", str(exc)) from exc


def verify_proposition_binding(
    *,
    proposition: ComparisonProposition,
    receipt_transport: str | bytes,
    trusted_keys: TrustedKeys,
) -> PropositionBindingReceipt:
    """Require authenticated exact-content binding for the proposition and claim ID."""
    receipt = parse_proposition_binding(receipt_transport)
    body = receipt.body

    key = trusted_keys.get(body.key_id)
    if key is None:
        raise PropositionBindingRefusal("UNTRUSTED_KEY_ID", body.key_id)

    expected_mac = _mac_for_body(body, key)
    if not hmac.compare_digest(receipt.mac, expected_mac):
        raise PropositionBindingRefusal("MAC_MISMATCH", "proposition receipt authentication failed")

    if body.claim_id != proposition.claim_id:
        raise PropositionBindingRefusal("CLAIM_ID_MISMATCH", proposition.claim_id)

    observed_digest = proposition_semantic_digest(proposition)
    if not hmac.compare_digest(body.proposition_digest, observed_digest):
        raise PropositionBindingRefusal("PROPOSITION_DIGEST_MISMATCH", observed_digest)

    return receipt


def verify_bound_claim_warrant_and_derive_relation(
    *,
    case: dict[str, Any],
    proposition: ComparisonProposition,
    warrant_receipt_transport: str | bytes,
    warrant_trusted_keys: TrustedKeys,
    proposition_receipt_transport: str | bytes,
    proposition_trusted_keys: TrustedKeys,
) -> WarrantedRelationReceipt:
    """Require exact claim/proposition identity and RC3 atom authority before relation."""
    verify_proposition_binding(
        proposition=proposition,
        receipt_transport=proposition_receipt_transport,
        trusted_keys=proposition_trusted_keys,
    )
    return verify_and_derive_categorical_relation(
        case=case,
        proposition=proposition,
        receipt_transport=warrant_receipt_transport,
        trusted_keys=warrant_trusted_keys,
    )


__all__ = [
    "ComparisonProposition",
    "PropositionBindingBody",
    "PropositionBindingReceipt",
    "PropositionBindingRefusal",
    "compose_categorical_relations",
    "issue_proposition_binding",
    "parse_proposition_binding",
    "proposition_semantic_digest",
    "proposition_semantic_projection",
    "serialize_proposition_binding",
    "verify_bound_claim_warrant_and_derive_relation",
    "verify_proposition_binding",
]
