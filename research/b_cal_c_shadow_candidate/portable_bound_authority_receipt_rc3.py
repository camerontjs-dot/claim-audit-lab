"""Research-only portable authenticated RC8J authority receipt.

RC3 tests whether a WARRANTED result can cross a producer/consumer boundary
without rerunning RC8J while remaining bound to the exact authority-relevant
case projection. HMAC-SHA-256 is a bounded research trust mechanism only; this
module does not establish production key management or signing architecture.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import hmac
import json
from typing import Any, Callable, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from categorical_warranted_relation_rc1 import (
    ComparisonProposition,
    WarrantedRelationReceipt,
    compose_categorical_relations,
    derive_categorical_relation as _derive_frozen_rc1_relation,
)


RC8J_FREEZE_COMMIT = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_CANDIDATE_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"
SCHEMA_VERSION = "cal.rc8j.portable-warrant.v1"
AUTH_ALGORITHM = "hmac-sha256"
SUBJECT_DIGEST_ALGORITHM = "sha256"
WARRANTED_REASON = "ALL_REQUIRED_WARRANT_ESTABLISHED"

AUTHORITY_BINDING_FIELDS = (
    "execution_state",
    "evidence_admitted",
    "authority_subject_id",
    "raw_source_id",
    "authority_subject_source_id",
    "raw_bundle_id",
    "authority_subject_bundle_id",
    "raw_passage_id",
    "authority_subject_passage_id",
    "admitted_passage_span",
    "raw_claim_id",
    "authority_subject_claim_id",
    "target_atom_id",
    "authority_subject_atom_id",
    "proposal",
    "assertion",
    "operator",
    "field_warrants",
    "required_fields",
    "composition",
    "aperture",
)

AuthorityEvaluator = Callable[[dict[str, Any]], dict[str, Any]]
TrustedKeys = Mapping[str, bytes]


class _StrictModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class PortableWarrantBody(_StrictModel):
    schema_version: Literal["cal.rc8j.portable-warrant.v1"]
    issuer_rc8j_commit: str = Field(min_length=40, max_length=40)
    issuer_rc8j_blob: str = Field(min_length=40, max_length=40)
    key_id: str = Field(min_length=1)
    authority_status: Literal["WARRANTED"]
    authority_reason: Literal["ALL_REQUIRED_WARRANT_ESTABLISHED"]
    claim_id: str = Field(min_length=1)
    atom_id: str = Field(min_length=1)
    subject_digest_algorithm: Literal["sha256"]
    subject_digest: str = Field(pattern=r"^[0-9a-f]{64}$")


class PortableWarrantReceipt(_StrictModel):
    body: PortableWarrantBody
    auth_algorithm: Literal["hmac-sha256"]
    mac: str = Field(pattern=r"^[0-9a-f]{64}$")


class PortableReceiptRefusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


class PortableReceiptIssuanceRefusal(ValueError):
    def __init__(self, status: str, reason: str):
        self.status = status
        self.reason = reason
        super().__init__(f"portable warrant requires WARRANTED authority, got {status}/{reason}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise PortableReceiptRefusal("DUPLICATE_JSON_KEY", key)
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
        raise PortableReceiptRefusal("NON_CANONICALIZABLE_JSON", str(exc)) from exc
    return text.encode("utf-8")


def authority_binding_projection(case: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise PortableReceiptRefusal("INVALID_CASE", "case must be an object")
    missing = [field for field in AUTHORITY_BINDING_FIELDS if field not in case]
    if missing:
        raise PortableReceiptRefusal(
            "BINDING_FIELD_MISSING",
            ",".join(missing),
        )
    return {field: deepcopy(case[field]) for field in AUTHORITY_BINDING_FIELDS}


def authority_subject_digest(case: dict[str, Any]) -> str:
    projection = authority_binding_projection(case)
    return hashlib.sha256(_canonical_json_bytes(projection)).hexdigest()


def _receipt_body_bytes(body: PortableWarrantBody) -> bytes:
    return _canonical_json_bytes(body.model_dump(mode="json"))


def _mac_for_body(body: PortableWarrantBody, key: bytes) -> str:
    if not isinstance(key, bytes) or len(key) < 32:
        raise PortableReceiptRefusal("INVALID_VERIFICATION_KEY", "HMAC key must be at least 32 bytes")
    return hmac.new(key, _receipt_body_bytes(body), hashlib.sha256).hexdigest()


def issue_portable_warrant(
    *,
    case: dict[str, Any],
    authority_evaluator: AuthorityEvaluator,
    key: bytes,
    key_id: str,
) -> PortableWarrantReceipt:
    """Evaluate exact captured case with RC8J, then authenticate its warrant receipt."""
    if not isinstance(case, dict):
        raise TypeError("portable warrant producer requires a case object")
    if not isinstance(key_id, str) or not key_id:
        raise ValueError("portable warrant producer requires non-empty key_id")

    snapshot = deepcopy(case)
    observed = authority_evaluator(deepcopy(snapshot))
    if not isinstance(observed, dict):
        raise TypeError("RC8J authority evaluator returned a non-object")
    status = observed.get("authority_status")
    reason = observed.get("reason")
    if status != "WARRANTED" or reason != WARRANTED_REASON:
        raise PortableReceiptIssuanceRefusal(str(status), str(reason))

    claim_id = snapshot.get("raw_claim_id")
    atom_id = snapshot.get("target_atom_id")
    if not isinstance(claim_id, str) or not claim_id:
        raise PortableReceiptRefusal("INVALID_BOUND_CLAIM", repr(claim_id))
    if not isinstance(atom_id, str) or not atom_id:
        raise PortableReceiptRefusal("INVALID_BOUND_ATOM", repr(atom_id))

    body = PortableWarrantBody(
        schema_version=SCHEMA_VERSION,
        issuer_rc8j_commit=RC8J_FREEZE_COMMIT,
        issuer_rc8j_blob=RC8J_CANDIDATE_BLOB,
        key_id=key_id,
        authority_status="WARRANTED",
        authority_reason=WARRANTED_REASON,
        claim_id=claim_id,
        atom_id=atom_id,
        subject_digest_algorithm=SUBJECT_DIGEST_ALGORITHM,
        subject_digest=authority_subject_digest(snapshot),
    )
    return PortableWarrantReceipt(
        body=body,
        auth_algorithm=AUTH_ALGORITHM,
        mac=_mac_for_body(body, key),
    )


def serialize_portable_warrant(receipt: PortableWarrantReceipt, *, pretty: bool = False) -> str:
    payload = receipt.model_dump(mode="json")
    if pretty:
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return _canonical_json_bytes(payload).decode("utf-8")


def parse_portable_warrant(transport: str | bytes) -> PortableWarrantReceipt:
    if isinstance(transport, bytes):
        try:
            transport = transport.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PortableReceiptRefusal("INVALID_UTF8", str(exc)) from exc
    if not isinstance(transport, str):
        raise PortableReceiptRefusal("INVALID_TRANSPORT", "receipt transport must be str or bytes")
    try:
        payload = json.loads(transport, object_pairs_hook=_reject_duplicate_pairs)
    except PortableReceiptRefusal:
        raise
    except json.JSONDecodeError as exc:
        raise PortableReceiptRefusal("INVALID_JSON", str(exc)) from exc
    try:
        return PortableWarrantReceipt.model_validate(payload)
    except ValidationError as exc:
        raise PortableReceiptRefusal("INVALID_RECEIPT_SCHEMA", str(exc)) from exc


def verify_portable_warrant(
    *,
    case: dict[str, Any],
    receipt_transport: str | bytes,
    trusted_keys: TrustedKeys,
) -> PortableWarrantReceipt:
    """Verify issuer authenticity and exact authority-subject binding without RC8J."""
    receipt = parse_portable_warrant(receipt_transport)
    body = receipt.body

    if body.issuer_rc8j_commit != RC8J_FREEZE_COMMIT:
        raise PortableReceiptRefusal("ISSUER_COMMIT_MISMATCH", body.issuer_rc8j_commit)
    if body.issuer_rc8j_blob != RC8J_CANDIDATE_BLOB:
        raise PortableReceiptRefusal("ISSUER_BLOB_MISMATCH", body.issuer_rc8j_blob)

    key = trusted_keys.get(body.key_id)
    if key is None:
        raise PortableReceiptRefusal("UNTRUSTED_KEY_ID", body.key_id)
    expected_mac = _mac_for_body(body, key)
    if not hmac.compare_digest(receipt.mac, expected_mac):
        raise PortableReceiptRefusal("MAC_MISMATCH", "receipt authentication failed")

    observed_digest = authority_subject_digest(case)
    if not hmac.compare_digest(body.subject_digest, observed_digest):
        raise PortableReceiptRefusal("SUBJECT_DIGEST_MISMATCH", observed_digest)

    claim_id = case.get("raw_claim_id")
    atom_id = case.get("target_atom_id")
    if body.claim_id != claim_id:
        raise PortableReceiptRefusal("CLAIM_ID_MISMATCH", repr(claim_id))
    if body.atom_id != atom_id:
        raise PortableReceiptRefusal("ATOM_ID_MISMATCH", repr(atom_id))

    return receipt


def verify_and_derive_categorical_relation(
    *,
    case: dict[str, Any],
    proposition: ComparisonProposition,
    receipt_transport: str | bytes,
    trusted_keys: TrustedKeys,
) -> WarrantedRelationReceipt:
    """Consume a verified portable warrant, then reuse the frozen relation table."""
    verified = verify_portable_warrant(
        case=case,
        receipt_transport=receipt_transport,
        trusted_keys=trusted_keys,
    )
    body = verified.body
    internal_authority = {
        "authority": {
            "status": body.authority_status,
            "reason": body.authority_reason,
        }
    }
    return _derive_frozen_rc1_relation(
        case=deepcopy(case),
        authority_result=internal_authority,
        proposition=proposition,
    )


__all__ = [
    "AUTHORITY_BINDING_FIELDS",
    "PortableReceiptIssuanceRefusal",
    "PortableReceiptRefusal",
    "PortableWarrantBody",
    "PortableWarrantReceipt",
    "authority_binding_projection",
    "authority_subject_digest",
    "compose_categorical_relations",
    "issue_portable_warrant",
    "parse_portable_warrant",
    "serialize_portable_warrant",
    "verify_and_derive_categorical_relation",
    "verify_portable_warrant",
]
