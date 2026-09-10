"""Authenticated proposition-relative relation for bounded event-order atoms.

Research-only. This module consumes an exact RC8J-warranted event-order case and
an independently authenticated exact temporal proposition. It introduces no
score, confidence, threshold, vote, or caller-supplied support/refutation hint.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import hmac
import json
from typing import Any, Callable, Iterable, Mapping

RC8J_FREEZE_COMMIT = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_IMPLEMENTATION_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"
WARRANTED_REASON = "ALL_REQUIRED_WARRANT_ESTABLISHED"
EVENT_FAMILY = "event_ordering"
ATOM_WARRANT_SCHEMA = "cal.event-order.portable-warrant.rc0.v1"
PROPOSITION_BINDING_SCHEMA = "cal.event-order.bound-proposition.rc0.v1"
AUTH_ALGORITHM = "hmac-sha256"

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
EVENT_FIELDS = (
    "left_subject",
    "left_predicate",
    "left_object",
    "left_polarity",
    "temporal_relation",
    "right_subject",
    "right_predicate",
    "right_object",
    "right_polarity",
)
_ALLOWED_RELATIONS = frozenset({"SUPPORTS", "REFUTES", "IRRELEVANT", "UNRESOLVED"})
_DECIDING_RELATIONS = frozenset({"SUPPORTS", "REFUTES"})
_TEMPORAL_DIRECTIONS = frozenset({"BEFORE", "AFTER"})
TrustedKeys = Mapping[str, bytes]
AuthorityEvaluator = Callable[[dict[str, Any]], dict[str, Any]]


class RelationRefusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True, slots=True)
class EventSemantics:
    subject: str
    predicate: str
    object: str
    polarity: str = "positive"

    def __post_init__(self) -> None:
        for name in ("subject", "predicate", "object", "polarity"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise RelationRefusal("INVALID_EVENT", f"{name} must be non-empty")
        if self.polarity not in {"positive", "negative"}:
            raise RelationRefusal("INVALID_EVENT_POLARITY", self.polarity)

    def payload(self) -> dict[str, str]:
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "polarity": self.polarity,
        }


@dataclass(frozen=True, slots=True)
class TemporalProposition:
    claim_id: str
    claim_text: str
    left_event: EventSemantics
    relation: str
    right_event: EventSemantics
    family: str = EVENT_FAMILY

    def __post_init__(self) -> None:
        if not isinstance(self.claim_id, str) or not self.claim_id:
            raise RelationRefusal("INVALID_PROPOSITION", "claim_id required")
        if not isinstance(self.claim_text, str) or not self.claim_text:
            raise RelationRefusal("INVALID_PROPOSITION", "claim_text required")
        if self.family != EVENT_FAMILY:
            raise RelationRefusal("INVALID_PROPOSITION_FAMILY", self.family)
        if self.relation not in _TEMPORAL_DIRECTIONS:
            raise RelationRefusal("INVALID_TEMPORAL_DIRECTION", self.relation)


@dataclass(frozen=True, slots=True)
class TemporalRelationRecord:
    relation_id: str
    claim_id: str
    atom_id: str
    relation: str
    warranted: bool
    reason: str
    evidence_ref: dict[str, str]
    proposition_projection: dict[str, Any]


@dataclass(frozen=True, slots=True)
class TemporalConclusion:
    claim_id: str
    disposition: str
    verdict: str | None
    reason_code: str
    basis_relation_ids: tuple[str, ...]


def canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RelationRefusal("NON_CANONICALIZABLE_JSON", str(exc)) from exc


def _stable_id(namespace: str, value: Any) -> str:
    return f"{namespace}:{hashlib.sha256(canonical_json_bytes(value)).hexdigest()}"


def _require_key(key: bytes) -> None:
    if not isinstance(key, bytes) or len(key) < 32:
        raise RelationRefusal("INVALID_KEY", "HMAC key must be at least 32 bytes")


def _mac(body: dict[str, Any], key: bytes, domain: bytes) -> str:
    _require_key(key)
    return hmac.new(key, domain + canonical_json_bytes(body), hashlib.sha256).hexdigest()


def claim_text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def proposition_projection(proposition: TemporalProposition) -> dict[str, Any]:
    return {
        "family": proposition.family,
        "left_event": proposition.left_event.payload(),
        "relation": proposition.relation,
        "right_event": proposition.right_event.payload(),
        "claim_text_sha256": claim_text_sha256(proposition.claim_text),
    }


def issue_proposition_binding(
    *, proposition: TemporalProposition, key: bytes, key_id: str
) -> dict[str, Any]:
    if not isinstance(key_id, str) or not key_id:
        raise RelationRefusal("INVALID_KEY_ID", "proposition key_id required")
    body = {
        "schema_version": PROPOSITION_BINDING_SCHEMA,
        "key_id": key_id,
        "claim_id": proposition.claim_id,
        "proposition_digest_algorithm": "sha256",
        "proposition_digest": hashlib.sha256(
            canonical_json_bytes(proposition_projection(proposition))
        ).hexdigest(),
    }
    return {
        "body": body,
        "auth_algorithm": AUTH_ALGORITHM,
        "mac": _mac(body, key, b"cal.event-order.bound-proposition.rc0.v1\x00"),
    }


def verify_proposition_binding(
    *, proposition: TemporalProposition, receipt: dict[str, Any], trusted_keys: TrustedKeys
) -> None:
    if not isinstance(receipt, dict) or set(receipt) != {"body", "auth_algorithm", "mac"}:
        raise RelationRefusal("INVALID_PROPOSITION_RECEIPT", "unexpected receipt shape")
    body = receipt.get("body")
    if not isinstance(body, dict) or set(body) != {
        "schema_version",
        "key_id",
        "claim_id",
        "proposition_digest_algorithm",
        "proposition_digest",
    }:
        raise RelationRefusal("INVALID_PROPOSITION_RECEIPT", "unexpected body shape")
    if body.get("schema_version") != PROPOSITION_BINDING_SCHEMA:
        raise RelationRefusal("INVALID_PROPOSITION_RECEIPT", "schema mismatch")
    if receipt.get("auth_algorithm") != AUTH_ALGORITHM:
        raise RelationRefusal("INVALID_PROPOSITION_RECEIPT", "algorithm mismatch")
    key_id = body.get("key_id")
    key = trusted_keys.get(str(key_id))
    if key is None:
        raise RelationRefusal("UNTRUSTED_PROPOSITION_KEY", str(key_id))
    expected = _mac(body, key, b"cal.event-order.bound-proposition.rc0.v1\x00")
    if not hmac.compare_digest(str(receipt.get("mac")), expected):
        raise RelationRefusal("PROPOSITION_MAC_MISMATCH", "authentication failed")
    if body.get("claim_id") != proposition.claim_id:
        raise RelationRefusal("PROPOSITION_CLAIM_ID_MISMATCH", proposition.claim_id)
    expected_digest = hashlib.sha256(
        canonical_json_bytes(proposition_projection(proposition))
    ).hexdigest()
    if not hmac.compare_digest(str(body.get("proposition_digest")), expected_digest):
        raise RelationRefusal("PROPOSITION_DIGEST_MISMATCH", expected_digest)


def authority_binding_projection(case: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise RelationRefusal("INVALID_AUTHORITY_CASE", "case must be an object")
    missing = [field for field in AUTHORITY_BINDING_FIELDS if field not in case]
    if missing:
        raise RelationRefusal("AUTHORITY_BINDING_FIELD_MISSING", ",".join(missing))
    return {field: deepcopy(case[field]) for field in AUTHORITY_BINDING_FIELDS}


def authority_subject_digest(case: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(authority_binding_projection(case))).hexdigest()


def _validate_event_case_shape(case: dict[str, Any]) -> None:
    proposal = case.get("proposal")
    operator = case.get("operator")
    if not isinstance(proposal, dict) or proposal.get("family") != EVENT_FAMILY:
        raise RelationRefusal("EVENT_CASE_FAMILY_MISMATCH", repr(proposal))
    if not isinstance(operator, dict) or operator.get("domain") != EVENT_FAMILY:
        raise RelationRefusal("EVENT_OPERATOR_DOMAIN_MISMATCH", repr(operator))
    fields = proposal.get("fields")
    if not isinstance(fields, dict) or set(fields) != set(EVENT_FIELDS):
        raise RelationRefusal("EVENT_FIELD_SET_MISMATCH", repr(fields))
    if tuple(case.get("required_fields") or ()) != EVENT_FIELDS:
        raise RelationRefusal("EVENT_REQUIRED_FIELDS_MISMATCH", repr(case.get("required_fields")))
    if fields.get("temporal_relation") not in _TEMPORAL_DIRECTIONS:
        raise RelationRefusal("EVENT_TEMPORAL_DIRECTION_INVALID", repr(fields.get("temporal_relation")))
    for side in ("left", "right"):
        for field in ("subject", "predicate", "object"):
            value = fields.get(f"{side}_{field}")
            if not isinstance(value, str) or not value:
                raise RelationRefusal("EVENT_FIELD_VALUE_INVALID", f"{side}_{field}")
        if fields.get(f"{side}_polarity") not in {"positive", "negative"}:
            raise RelationRefusal("EVENT_FIELD_VALUE_INVALID", f"{side}_polarity")


def issue_event_atom_warrant(
    *,
    case: dict[str, Any],
    authority_evaluator: AuthorityEvaluator,
    key: bytes,
    key_id: str,
) -> dict[str, Any]:
    _validate_event_case_shape(case)
    if not isinstance(key_id, str) or not key_id:
        raise RelationRefusal("INVALID_KEY_ID", "atom warrant key_id required")
    snapshot = deepcopy(case)
    observed = authority_evaluator(deepcopy(snapshot))
    if observed != {"authority_status": "WARRANTED", "reason": WARRANTED_REASON}:
        raise RelationRefusal(
            "ATOM_WARRANT_ISSUANCE_REFUSED",
            f"{observed.get('authority_status')}/{observed.get('reason')}",
        )
    body = {
        "schema_version": ATOM_WARRANT_SCHEMA,
        "issuer_rc8j_commit": RC8J_FREEZE_COMMIT,
        "issuer_rc8j_blob": RC8J_IMPLEMENTATION_BLOB,
        "key_id": key_id,
        "authority_status": "WARRANTED",
        "authority_reason": WARRANTED_REASON,
        "claim_id": snapshot.get("raw_claim_id"),
        "atom_id": snapshot.get("target_atom_id"),
        "subject_digest_algorithm": "sha256",
        "subject_digest": authority_subject_digest(snapshot),
    }
    return {
        "body": body,
        "auth_algorithm": AUTH_ALGORITHM,
        "mac": _mac(body, key, b"cal.event-order.portable-warrant.rc0.v1\x00"),
    }


def verify_event_atom_warrant(
    *, case: dict[str, Any], receipt: dict[str, Any], trusted_keys: TrustedKeys
) -> None:
    _validate_event_case_shape(case)
    if not isinstance(receipt, dict) or set(receipt) != {"body", "auth_algorithm", "mac"}:
        raise RelationRefusal("INVALID_ATOM_WARRANT", "unexpected receipt shape")
    body = receipt.get("body")
    expected_fields = {
        "schema_version",
        "issuer_rc8j_commit",
        "issuer_rc8j_blob",
        "key_id",
        "authority_status",
        "authority_reason",
        "claim_id",
        "atom_id",
        "subject_digest_algorithm",
        "subject_digest",
    }
    if not isinstance(body, dict) or set(body) != expected_fields:
        raise RelationRefusal("INVALID_ATOM_WARRANT", "unexpected body shape")
    if body.get("schema_version") != ATOM_WARRANT_SCHEMA:
        raise RelationRefusal("INVALID_ATOM_WARRANT", "schema mismatch")
    if body.get("issuer_rc8j_commit") != RC8J_FREEZE_COMMIT:
        raise RelationRefusal("ATOM_WARRANT_ISSUER_MISMATCH", str(body.get("issuer_rc8j_commit")))
    if body.get("issuer_rc8j_blob") != RC8J_IMPLEMENTATION_BLOB:
        raise RelationRefusal("ATOM_WARRANT_ISSUER_MISMATCH", str(body.get("issuer_rc8j_blob")))
    if body.get("authority_status") != "WARRANTED" or body.get("authority_reason") != WARRANTED_REASON:
        raise RelationRefusal("INVALID_ATOM_WARRANT", "non-warranted body")
    if receipt.get("auth_algorithm") != AUTH_ALGORITHM:
        raise RelationRefusal("INVALID_ATOM_WARRANT", "algorithm mismatch")
    key_id = str(body.get("key_id"))
    key = trusted_keys.get(key_id)
    if key is None:
        raise RelationRefusal("UNTRUSTED_ATOM_KEY", key_id)
    expected_mac = _mac(body, key, b"cal.event-order.portable-warrant.rc0.v1\x00")
    if not hmac.compare_digest(str(receipt.get("mac")), expected_mac):
        raise RelationRefusal("ATOM_WARRANT_MAC_MISMATCH", "authentication failed")
    if not hmac.compare_digest(str(body.get("subject_digest")), authority_subject_digest(case)):
        raise RelationRefusal("ATOM_WARRANT_SUBJECT_MISMATCH", authority_subject_digest(case))
    if body.get("claim_id") != case.get("raw_claim_id"):
        raise RelationRefusal("ATOM_WARRANT_CLAIM_MISMATCH", repr(case.get("raw_claim_id")))
    if body.get("atom_id") != case.get("target_atom_id"):
        raise RelationRefusal("ATOM_WARRANT_ATOM_MISMATCH", repr(case.get("target_atom_id")))


def _event_from_fields(fields: Mapping[str, Any], side: str) -> EventSemantics:
    return EventSemantics(
        subject=str(fields[f"{side}_subject"]),
        predicate=str(fields[f"{side}_predicate"]),
        object=str(fields[f"{side}_object"]),
        polarity=str(fields[f"{side}_polarity"]),
    )


def _derive_after_verified_bindings(
    *, case: dict[str, Any], proposition: TemporalProposition
) -> TemporalRelationRecord:
    if case.get("raw_claim_id") != proposition.claim_id:
        raise RelationRefusal(
            "ATOM_PROPOSITION_CLAIM_MISMATCH",
            f"{case.get('raw_claim_id')!r} != {proposition.claim_id!r}",
        )
    fields = case["proposal"]["fields"]
    atom_left = _event_from_fields(fields, "left")
    atom_right = _event_from_fields(fields, "right")
    atom_direction = str(fields["temporal_relation"])
    prop_projection = proposition_projection(proposition)
    evidence_ref = {
        "source_id": str(case["raw_source_id"]),
        "passage_id": str(case["raw_passage_id"]),
    }

    all_events = (atom_left, atom_right, proposition.left_event, proposition.right_event)
    if any(event.polarity != "positive" for event in all_events):
        relation = "UNRESOLVED"
        reason = "negative-event scope is outside RC0 deciding temporal relation semantics"
    else:
        same_pair = atom_left == proposition.left_event and atom_right == proposition.right_event
        swapped_pair = atom_left == proposition.right_event and atom_right == proposition.left_event
        if not same_pair and not swapped_pair:
            relation = "IRRELEVANT"
            reason = "warranted temporal atom concerns a different event pair"
        elif same_pair:
            if atom_direction == proposition.relation:
                relation = "SUPPORTS"
                reason = "same event pair and same temporal direction"
            else:
                relation = "REFUTES"
                reason = "same event pair and opposite temporal direction"
        else:
            if atom_direction != proposition.relation:
                relation = "SUPPORTS"
                reason = "swapped event pair with logically inverse temporal direction"
            else:
                relation = "REFUTES"
                reason = "swapped event pair with same temporal direction opposes proposition"

    material = {
        "claim_id": proposition.claim_id,
        "atom_id": str(case["target_atom_id"]),
        "relation": relation,
        "evidence_ref": evidence_ref,
        "proposition": prop_projection,
    }
    return TemporalRelationRecord(
        relation_id=_stable_id("temporal-relation", material),
        claim_id=proposition.claim_id,
        atom_id=str(case["target_atom_id"]),
        relation=relation,
        warranted=True,
        reason=reason,
        evidence_ref=evidence_ref,
        proposition_projection=prop_projection,
    )


def derive_temporal_relation(
    *,
    case: dict[str, Any],
    proposition: TemporalProposition,
    atom_warrant: dict[str, Any],
    atom_trusted_keys: TrustedKeys,
    proposition_binding: dict[str, Any],
    proposition_trusted_keys: TrustedKeys,
) -> TemporalRelationRecord:
    verify_proposition_binding(
        proposition=proposition,
        receipt=proposition_binding,
        trusted_keys=proposition_trusted_keys,
    )
    verify_event_atom_warrant(
        case=case,
        receipt=atom_warrant,
        trusted_keys=atom_trusted_keys,
    )
    return _derive_after_verified_bindings(case=case, proposition=proposition)


def weak_claim_id_only_relation(
    *,
    case: dict[str, Any],
    proposition: TemporalProposition,
    atom_warrant: dict[str, Any],
    atom_trusted_keys: TrustedKeys,
) -> TemporalRelationRecord:
    """Deliberately weak control: authenticate atom but not proposition semantics."""
    verify_event_atom_warrant(
        case=case,
        receipt=atom_warrant,
        trusted_keys=atom_trusted_keys,
    )
    return _derive_after_verified_bindings(case=case, proposition=proposition)


def compose_temporal_relations(
    *, proposition: TemporalProposition, relations: Iterable[TemporalRelationRecord]
) -> TemporalConclusion:
    rows = tuple(relations)
    for row in rows:
        if row.claim_id != proposition.claim_id:
            raise RelationRefusal("COMPOSITION_CLAIM_MISMATCH", row.claim_id)
        if row.relation not in _ALLOWED_RELATIONS:
            raise RelationRefusal("COMPOSITION_UNKNOWN_RELATION", row.relation)
        if row.relation in _DECIDING_RELATIONS and not row.warranted:
            raise RelationRefusal("COMPOSITION_NONWARRANTED_DECIDING_RELATION", row.relation_id)
    ordered = tuple(sorted(rows, key=lambda item: item.relation_id))
    unresolved = tuple(item for item in ordered if item.relation == "UNRESOLVED")
    supports = tuple(item for item in ordered if item.relation == "SUPPORTS")
    refutes = tuple(item for item in ordered if item.relation == "REFUTES")
    irrelevant = tuple(item for item in ordered if item.relation == "IRRELEVANT")
    if unresolved:
        return TemporalConclusion(
            proposition.claim_id,
            "abstained",
            None,
            "unresolved_categorical_relation",
            tuple(item.relation_id for item in unresolved),
        )
    if supports and refutes:
        return TemporalConclusion(
            proposition.claim_id,
            "abstained",
            None,
            "mixed_categorical_relations",
            tuple(item.relation_id for item in (*supports, *refutes)),
        )
    if supports:
        return TemporalConclusion(
            proposition.claim_id,
            "decided",
            "supported",
            "categorical_support",
            tuple(item.relation_id for item in supports),
        )
    if refutes:
        return TemporalConclusion(
            proposition.claim_id,
            "decided",
            "contradicted",
            "categorical_refutation",
            tuple(item.relation_id for item in refutes),
        )
    return TemporalConclusion(
        proposition.claim_id,
        "abstained",
        None,
        "no_deciding_categorical_relation",
        tuple(item.relation_id for item in irrelevant),
    )


__all__ = [
    "AUTHORITY_BINDING_FIELDS",
    "ATOM_WARRANT_SCHEMA",
    "EVENT_FIELDS",
    "EVENT_FAMILY",
    "EventSemantics",
    "PROPOSITION_BINDING_SCHEMA",
    "RelationRefusal",
    "TemporalConclusion",
    "TemporalProposition",
    "TemporalRelationRecord",
    "authority_binding_projection",
    "authority_subject_digest",
    "canonical_json_bytes",
    "compose_temporal_relations",
    "derive_temporal_relation",
    "issue_event_atom_warrant",
    "issue_proposition_binding",
    "proposition_projection",
    "verify_event_atom_warrant",
    "verify_proposition_binding",
    "weak_claim_id_only_relation",
]
