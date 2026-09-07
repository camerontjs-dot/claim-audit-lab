"""Research-only CAL RC0 strict-comparison vertical.

Normal-context Draft Research Infrastructure. This module intentionally does not
modify production CAL. It composes frozen/reconciled research boundaries through
injected exact dependencies:

RC7F-B1 comparison measurement -> complete strict-comparison atom -> frozen RC8J
-> atom-bound authenticated receipt -> exact claim/proposition binding ->
proposition-relative categorical relation -> scoreless fail-closed composition
-> conservative Contract C 1.0.0 projection.

The new semantic seam in RC0 is deliberately narrow: RC7F-B1 may make a bounded
measurement proposal, but RC0 refuses authority unless every field required by
its strict-comparison atom is established from the admitted passage. No score,
confidence, vote, reader count, retrieval rank, or caller polarity can repair an
incomplete atom or change a terminal categorical relation.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
import re
from typing import Any, Callable, Iterable, Mapping

PROFILE_ID = "cal-research-profile-rc0-strict-comparison"
PROFILE_SEMANTIC_FAMILY = "strict_comparison"
RC8J_AUTHORITY_FAMILY = "comparison"
RC8J_FREEZE_COMMIT = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_IMPLEMENTATION_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"
CONTRACT_B_VERSION = "1.2.0"
CONTRACT_B_AUTHORITY_COMMIT = "c314e53bd91c0736aa4370a364673b069aceb43e"
CONTRACT_C_VERSION = "1.0.0"
CONTRACT_C_AUTHORITY_COMMIT = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
RC7FB1_COMMIT = "0ecdedc5cea970485a635508255f3670ab231c33"
RC7FB1_BLOB = "33820f55e2a87c4de6336fca6b5e5b93a2bccde3"

ATOM_WARRANT_SCHEMA = "cal.rc8j.portable-warrant.v1"
PROPOSITION_BINDING_SCHEMA = "cal.bound-proposition.rc0.v1"
AUTH_ALGORITHM = "hmac-sha256"
WARRANTED_REASON = "ALL_REQUIRED_WARRANT_ESTABLISHED"

MeasureFn = Callable[[str], dict[str, Any]]
AuthorityEvaluator = Callable[[dict[str, Any]], dict[str, Any]]
TrustedKeys = Mapping[str, bytes]

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

_DECIDING_RELATIONS = {"SUPPORTS", "REFUTES"}
_ALLOWED_RELATIONS = {"SUPPORTS", "REFUTES", "IRRELEVANT", "UNRESOLVED"}
_STRICT_DIRECTIONS = {"greater_than", "less_than"}
_RELATION_TO_DIRECTION = {
    "MORE_THAN": "greater_than",
    "GREATER_THAN": "greater_than",
    "FEWER_THAN": "less_than",
    "LESS_THAN": "less_than",
}
_UNSAFE_ASSERTION_CUES = re.compile(
    r"\b(?:not|never|may|might|could|would|suggested|suggests|estimate|estimated|"
    r"preliminary|projected|forecast|reportedly|allegedly|approximately|about)\b",
    re.IGNORECASE,
)


class RC0Refusal(ValueError):
    """Fail-closed research refusal with a typed code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True)
class BoundProposition:
    claim_id: str
    claim_text: str
    family: str
    lhs_entity: str
    rhs_entity: str
    comparison_direction: str

    def __post_init__(self) -> None:
        if not self.claim_id or not self.claim_text:
            raise ValueError("proposition requires exact claim identity and text")
        if self.family != PROFILE_SEMANTIC_FAMILY:
            raise ValueError("RC0 proposition family must be strict_comparison")
        if self.comparison_direction not in _STRICT_DIRECTIONS:
            raise ValueError("RC0 proposition requires a strict comparison direction")
        if not self.lhs_entity or not self.rhs_entity or self.lhs_entity == self.rhs_entity:
            raise ValueError("RC0 proposition requires two distinct entities")


@dataclass(frozen=True)
class StrictComparisonAtom:
    atom_id: str
    claim_id: str
    source_id: str
    bundle_id: str
    passage_id: str
    lhs_entity: str
    rhs_entity: str
    comparison_direction: str
    source_span: tuple[int, int]
    lhs_span: tuple[int, int]
    rhs_span: tuple[int, int]
    direction_span: tuple[int, int]
    polarity: str
    measure_surface: str | None
    measure_span: tuple[int, int] | None
    quantity_surface: str | None
    quantity_span: tuple[int, int] | None
    unit_surface: str | None
    unit_span: tuple[int, int] | None
    measurement_version: str
    measurement_proposal: dict[str, Any]

    def __post_init__(self) -> None:
        if self.comparison_direction not in _STRICT_DIRECTIONS:
            raise ValueError("strict comparison atom requires greater_than or less_than")
        if self.polarity != "affirmative":
            raise ValueError("RC0 only constructs affirmative strict-comparison atoms")
        if self.lhs_entity == self.rhs_entity:
            raise ValueError("strict comparison atom requires distinct entities")


@dataclass(frozen=True)
class EvidenceInput:
    source_id: str
    bundle_id: str
    passage_id: str
    passage_text: str
    passage_sha256: str
    semantic_family: str = PROFILE_SEMANTIC_FAMILY
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class RelationRecord:
    relation_id: str
    claim_id: str
    atom_id: str | None
    relation: str
    warranted: bool
    reason: str
    evidence_ref: dict[str, str] | None
    proposition_projection: dict[str, Any]


@dataclass(frozen=True)
class CategoricalConclusion:
    claim_id: str
    disposition: str
    verdict: str | None
    reason_code: str
    basis_relation_ids: tuple[str, ...]


def canonical_json_bytes(value: Any, *, trailing_newline: bool = False) -> bytes:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    if trailing_newline:
        text += "\n"
    return text.encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stable_id(namespace: str, value: Any) -> str:
    return f"{namespace}:{sha256_hex(canonical_json_bytes(value))}"


def claim_text_sha256(text: str) -> str:
    return sha256_hex(text.encode("utf-8"))


def proposition_projection(proposition: BoundProposition) -> dict[str, Any]:
    return {
        "family": proposition.family,
        "lhs_entity": proposition.lhs_entity,
        "rhs_entity": proposition.rhs_entity,
        "comparison_direction": proposition.comparison_direction,
        "claim_text_sha256": claim_text_sha256(proposition.claim_text),
    }


def _unique_casefold_span(text: str, surface: str) -> tuple[int, int] | None:
    needle = surface.strip()
    if not needle:
        return None
    lowered = text.casefold()
    target = needle.casefold()
    starts: list[int] = []
    pos = 0
    while True:
        found = lowered.find(target, pos)
        if found < 0:
            break
        starts.append(found)
        pos = found + 1
    if len(starts) != 1:
        return None
    start = starts[0]
    return start, start + len(needle)


def _split_delta(delta: str) -> tuple[str, str | None] | None:
    match = re.fullmatch(
        r"(?P<quantity>\d+(?:\.\d+)?)"
        r"(?:\s+(?P<unit>percentage\s+points?|percent|%|files?|samples?|units?|items?))?",
        delta.strip(),
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    return match.group("quantity"), (match.group("unit") or None)


def complete_strict_comparison_atom(
    *, claim_id: str, evidence: EvidenceInput, measurement: dict[str, Any]
) -> tuple[StrictComparisonAtom | None, str]:
    """Complete a strict comparison atom without guessing any material field."""
    if evidence.semantic_family != PROFILE_SEMANTIC_FAMILY:
        return None, "UNSUPPORTED_SEMANTIC_FAMILY"
    if not isinstance(measurement, dict):
        return None, "MEASUREMENT_INVALID"
    if measurement.get("status") != "CLAIMED":
        return None, "MEASUREMENT_MISS_SAFE"
    proposals = measurement.get("proposals")
    if not isinstance(proposals, list) or len(proposals) != 1 or not isinstance(proposals[0], dict):
        return None, "ATOM_INCOMPLETE"
    proposal = deepcopy(proposals[0])
    direction = _RELATION_TO_DIRECTION.get(str(proposal.get("relation")))
    if direction is None:
        return None, "ATOM_INCOMPLETE"
    text = evidence.passage_text
    if not text.strip() or _UNSAFE_ASSERTION_CUES.search(text):
        return None, "ATOM_INCOMPLETE"
    lhs_surface = str(proposal.get("left") or "").strip()
    rhs_surface = str(proposal.get("right") or "").strip()
    lhs_span = _unique_casefold_span(text, lhs_surface)
    rhs_span = _unique_casefold_span(text, rhs_surface)
    raw_direction_span = proposal.get("span")
    if (
        lhs_span is None
        or rhs_span is None
        or not isinstance(raw_direction_span, list)
        or len(raw_direction_span) != 2
        or not all(isinstance(v, int) and not isinstance(v, bool) for v in raw_direction_span)
    ):
        return None, "ATOM_INCOMPLETE"
    direction_span = (raw_direction_span[0], raw_direction_span[1])
    if not (0 <= direction_span[0] <= direction_span[1] <= len(text)):
        return None, "ATOM_INCOMPLETE"
    measure_surface = proposal.get("measure_surface")
    measure_span: tuple[int, int] | None = None
    if measure_surface is not None:
        if not isinstance(measure_surface, str):
            return None, "ATOM_INCOMPLETE"
        measure_span = _unique_casefold_span(text, measure_surface)
        if measure_span is None:
            return None, "ATOM_INCOMPLETE"
    delta_surface = proposal.get("delta_surface")
    quantity_surface: str | None = None
    quantity_span: tuple[int, int] | None = None
    unit_surface: str | None = None
    unit_span: tuple[int, int] | None = None
    if delta_surface is not None:
        if not isinstance(delta_surface, str):
            return None, "ATOM_INCOMPLETE"
        split = _split_delta(delta_surface)
        if split is None:
            return None, "ATOM_INCOMPLETE"
        quantity_surface, unit_surface = split
        quantity_span = _unique_casefold_span(text, quantity_surface)
        if quantity_span is None:
            return None, "ATOM_INCOMPLETE"
        if unit_surface is not None:
            unit_span = _unique_casefold_span(text, unit_surface)
            if unit_span is None:
                return None, "ATOM_INCOMPLETE"
    lhs = lhs_surface.casefold()
    rhs = rhs_surface.casefold()
    material = {
        "profile": PROFILE_ID,
        "claim_id": claim_id,
        "bundle_id": evidence.bundle_id,
        "source_id": evidence.source_id,
        "passage_id": evidence.passage_id,
        "lhs_entity": lhs,
        "rhs_entity": rhs,
        "comparison_direction": direction,
        "source_span": [0, len(text)],
        "lhs_span": list(lhs_span),
        "rhs_span": list(rhs_span),
        "direction_span": list(direction_span),
        "polarity": "affirmative",
        "measure_surface": measure_surface,
        "measure_span": list(measure_span) if measure_span else None,
        "quantity_surface": quantity_surface,
        "quantity_span": list(quantity_span) if quantity_span else None,
        "unit_surface": unit_surface,
        "unit_span": list(unit_span) if unit_span else None,
        "measurement_version": str(measurement.get("version") or "UNKNOWN"),
    }
    return StrictComparisonAtom(
        atom_id=stable_id("atom", material),
        claim_id=claim_id,
        source_id=evidence.source_id,
        bundle_id=evidence.bundle_id,
        passage_id=evidence.passage_id,
        lhs_entity=lhs,
        rhs_entity=rhs,
        comparison_direction=direction,
        source_span=(0, len(text)),
        lhs_span=lhs_span,
        rhs_span=rhs_span,
        direction_span=direction_span,
        polarity="affirmative",
        measure_surface=measure_surface if isinstance(measure_surface, str) else None,
        measure_span=measure_span,
        quantity_surface=quantity_surface,
        quantity_span=quantity_span,
        unit_surface=unit_surface,
        unit_span=unit_span,
        measurement_version=str(measurement.get("version") or "UNKNOWN"),
        measurement_proposal=proposal,
    ), "COMPLETE"


def build_rc8j_case(*, atom: StrictComparisonAtom, evidence: EvidenceInput) -> dict[str, Any]:
    if atom.passage_id != evidence.passage_id or atom.source_id != evidence.source_id:
        raise RC0Refusal("ATOM_BINDING_FAILURE", "atom/evidence identity mismatch")
    subject_id = stable_id(
        "authority-subject",
        {
            "claim_id": atom.claim_id,
            "atom_id": atom.atom_id,
            "bundle_id": atom.bundle_id,
            "source_id": atom.source_id,
            "passage_id": atom.passage_id,
        },
    )
    fields = {
        "lhs_entity": atom.lhs_entity,
        "rhs_entity": atom.rhs_entity,
        "comparison_direction": atom.comparison_direction,
    }
    field_spans = {
        "lhs_entity": atom.lhs_span,
        "rhs_entity": atom.rhs_span,
        "comparison_direction": atom.direction_span,
    }
    warrants = {
        field: {
            "authority_subject_id": subject_id,
            "span": list(field_spans[field]),
            "status": "established",
            "value": value,
        }
        for field, value in fields.items()
    }
    return {
        "execution_state": "completed",
        "evidence_admitted": True,
        "authority_subject_id": subject_id,
        "raw_source_id": atom.source_id,
        "authority_subject_source_id": atom.source_id,
        "raw_bundle_id": atom.bundle_id,
        "authority_subject_bundle_id": atom.bundle_id,
        "raw_passage_id": atom.passage_id,
        "authority_subject_passage_id": atom.passage_id,
        "admitted_passage_span": list(atom.source_span),
        "raw_claim_id": atom.claim_id,
        "authority_subject_claim_id": atom.claim_id,
        "target_atom_id": atom.atom_id,
        "authority_subject_atom_id": atom.atom_id,
        "proposal": {
            "authority_subject_id": subject_id,
            "family": RC8J_AUTHORITY_FAMILY,
            "source_span": list(atom.source_span),
            "extra_modifiers": [],
            "fields": fields,
        },
        "assertion": {"authority_subject_id": subject_id, "state": "asserted"},
        "operator": {
            "authority_subject_id": subject_id,
            "domain": RC8J_AUTHORITY_FAMILY,
            "applicability": "applicable",
            "governed_span": list(atom.source_span),
            "jurisdiction_fields": list(fields),
        },
        "field_warrants": warrants,
        "required_fields": list(fields),
        "composition": {"authority_subject_id": subject_id, "required": False, "state": "not_required"},
        "aperture": {"authority_subject_id": subject_id, "required": False, "state": "not_required"},
    }


def authority_binding_projection(case: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in AUTHORITY_BINDING_FIELDS if field not in case]
    if missing:
        raise RC0Refusal("ATOM_BINDING_FAILURE", "missing:" + ",".join(missing))
    return {field: deepcopy(case[field]) for field in AUTHORITY_BINDING_FIELDS}


def authority_subject_digest(case: dict[str, Any]) -> str:
    return sha256_hex(canonical_json_bytes(authority_binding_projection(case)))


def _require_key(key: bytes) -> None:
    if not isinstance(key, bytes) or len(key) < 32:
        raise RC0Refusal("INVALID_RESEARCH_KEY", "HMAC key must be at least 32 bytes")


def issue_atom_warrant(*, case: dict[str, Any], authority_evaluator: AuthorityEvaluator, key: bytes, key_id: str) -> dict[str, Any]:
    _require_key(key)
    observed = authority_evaluator(deepcopy(case))
    if not isinstance(observed, dict):
        raise RC0Refusal("APPARATUS_FAILURE", "RC8J returned non-object")
    status = observed.get("authority_status")
    reason = observed.get("reason")
    if status != "WARRANTED" or reason != WARRANTED_REASON:
        raise RC0Refusal("WARRANT_UNRESOLVED", f"{status}/{reason}")
    body = {
        "schema_version": ATOM_WARRANT_SCHEMA,
        "issuer_rc8j_commit": RC8J_FREEZE_COMMIT,
        "issuer_rc8j_blob": RC8J_IMPLEMENTATION_BLOB,
        "key_id": key_id,
        "authority_status": "WARRANTED",
        "authority_reason": WARRANTED_REASON,
        "claim_id": case["raw_claim_id"],
        "atom_id": case["target_atom_id"],
        "subject_digest_algorithm": "sha256",
        "subject_digest": authority_subject_digest(case),
    }
    mac = hmac.new(key, canonical_json_bytes(body), hashlib.sha256).hexdigest()
    return {"body": body, "auth_algorithm": AUTH_ALGORITHM, "mac": mac}


def verify_atom_warrant(*, case: dict[str, Any], receipt: dict[str, Any], trusted_keys: TrustedKeys) -> dict[str, Any]:
    try:
        body = receipt["body"]
        mac = receipt["mac"]
    except (KeyError, TypeError) as exc:
        raise RC0Refusal("ATOM_BINDING_FAILURE", "invalid receipt shape") from exc
    if receipt.get("auth_algorithm") != AUTH_ALGORITHM or body.get("schema_version") != ATOM_WARRANT_SCHEMA:
        raise RC0Refusal("ATOM_BINDING_FAILURE", "receipt algorithm/schema mismatch")
    if body.get("issuer_rc8j_commit") != RC8J_FREEZE_COMMIT or body.get("issuer_rc8j_blob") != RC8J_IMPLEMENTATION_BLOB:
        raise RC0Refusal("ATOM_BINDING_FAILURE", "RC8J identity mismatch")
    key = trusted_keys.get(str(body.get("key_id")))
    if key is None:
        raise RC0Refusal("ATOM_BINDING_FAILURE", "untrusted key")
    _require_key(key)
    expected = hmac.new(key, canonical_json_bytes(body), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(mac), expected):
        raise RC0Refusal("ATOM_BINDING_FAILURE", "MAC mismatch")
    if body.get("authority_status") != "WARRANTED" or body.get("authority_reason") != WARRANTED_REASON:
        raise RC0Refusal("ATOM_BINDING_FAILURE", "non-warranted receipt")
    if body.get("subject_digest") != authority_subject_digest(case):
        raise RC0Refusal("ATOM_BINDING_FAILURE", "subject digest mismatch")
    if body.get("claim_id") != case.get("raw_claim_id") or body.get("atom_id") != case.get("target_atom_id"):
        raise RC0Refusal("ATOM_BINDING_FAILURE", "claim/atom mismatch")
    return receipt


def issue_proposition_binding(*, proposition: BoundProposition, key: bytes, key_id: str) -> dict[str, Any]:
    _require_key(key)
    projection = proposition_projection(proposition)
    body = {
        "schema_version": PROPOSITION_BINDING_SCHEMA,
        "key_id": key_id,
        "claim_id": proposition.claim_id,
        "claim_text_sha256": projection["claim_text_sha256"],
        "proposition_digest_algorithm": "sha256",
        "proposition_digest": sha256_hex(canonical_json_bytes(projection)),
    }
    mac = hmac.new(key, b"cal.bound-proposition.rc0.v1\x00" + canonical_json_bytes(body), hashlib.sha256).hexdigest()
    return {"body": body, "auth_algorithm": AUTH_ALGORITHM, "mac": mac}


def verify_proposition_binding(*, proposition: BoundProposition, receipt: dict[str, Any], trusted_keys: TrustedKeys) -> dict[str, Any]:
    try:
        body = receipt["body"]
        mac = receipt["mac"]
    except (KeyError, TypeError) as exc:
        raise RC0Refusal("PROPOSITION_BINDING_FAILURE", "invalid receipt shape") from exc
    if receipt.get("auth_algorithm") != AUTH_ALGORITHM or body.get("schema_version") != PROPOSITION_BINDING_SCHEMA:
        raise RC0Refusal("PROPOSITION_BINDING_FAILURE", "receipt algorithm/schema mismatch")
    key = trusted_keys.get(str(body.get("key_id")))
    if key is None:
        raise RC0Refusal("PROPOSITION_BINDING_FAILURE", "untrusted key")
    expected = hmac.new(key, b"cal.bound-proposition.rc0.v1\x00" + canonical_json_bytes(body), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(mac), expected):
        raise RC0Refusal("PROPOSITION_BINDING_FAILURE", "MAC mismatch")
    projection = proposition_projection(proposition)
    if body.get("claim_id") != proposition.claim_id:
        raise RC0Refusal("PROPOSITION_BINDING_FAILURE", "claim id mismatch")
    if body.get("claim_text_sha256") != projection["claim_text_sha256"]:
        raise RC0Refusal("PROPOSITION_BINDING_FAILURE", "claim text mismatch")
    if body.get("proposition_digest") != sha256_hex(canonical_json_bytes(projection)):
        raise RC0Refusal("PROPOSITION_BINDING_FAILURE", "typed proposition mismatch")
    return receipt


def derive_categorical_relation(
    *, case: dict[str, Any], proposition: BoundProposition, atom_warrant: dict[str, Any], atom_trusted_keys: TrustedKeys,
    proposition_binding: dict[str, Any], proposition_trusted_keys: TrustedKeys, evidence_ref: dict[str, str]
) -> RelationRecord:
    verify_proposition_binding(proposition=proposition, receipt=proposition_binding, trusted_keys=proposition_trusted_keys)
    verify_atom_warrant(case=case, receipt=atom_warrant, trusted_keys=atom_trusted_keys)
    if case.get("raw_claim_id") != proposition.claim_id:
        raise RC0Refusal("PROPOSITION_BINDING_FAILURE", "atom claim differs from proposition claim")
    proposal = case.get("proposal")
    fields = proposal.get("fields") if isinstance(proposal, dict) else None
    if not isinstance(fields, dict):
        raise RC0Refusal("ATOM_BINDING_FAILURE", "missing atom fields")
    atom_lhs = fields.get("lhs_entity")
    atom_rhs = fields.get("rhs_entity")
    atom_direction = fields.get("comparison_direction")
    family = proposal.get("family")
    if not all(isinstance(v, str) and v for v in (atom_lhs, atom_rhs, atom_direction, family)):
        raise RC0Refusal("ATOM_BINDING_FAILURE", "incomplete consumed atom")
    if family != RC8J_AUTHORITY_FAMILY:
        relation, reason = "UNRESOLVED", "warranted atom family outside RC0 strict-comparison relation operator"
    else:
        same_pair = atom_lhs == proposition.lhs_entity and atom_rhs == proposition.rhs_entity
        swapped_pair = atom_lhs == proposition.rhs_entity and atom_rhs == proposition.lhs_entity
        if not (same_pair or swapped_pair):
            relation, reason = "IRRELEVANT", "warranted strict comparison concerns a different entity pair"
        elif atom_direction not in _STRICT_DIRECTIONS:
            relation, reason = "UNRESOLVED", "warranted atom direction outside strict-order relation table"
        elif same_pair:
            if atom_direction == proposition.comparison_direction:
                relation, reason = "SUPPORTS", "same ordered pair and same strict direction"
            else:
                relation, reason = "REFUTES", "same ordered pair and opposite strict direction"
        else:
            if atom_direction != proposition.comparison_direction:
                relation, reason = "SUPPORTS", "swapped pair with logically inverse strict direction"
            else:
                relation, reason = "REFUTES", "swapped pair with same strict direction opposes proposition"
    payload = {
        "claim_id": proposition.claim_id,
        "atom_id": case["target_atom_id"],
        "relation": relation,
        "proposition": proposition_projection(proposition),
        "evidence_ref": evidence_ref,
    }
    return RelationRecord(
        relation_id=stable_id("relation", payload), claim_id=proposition.claim_id, atom_id=case["target_atom_id"],
        relation=relation, warranted=True, reason=reason, evidence_ref=deepcopy(evidence_ref),
        proposition_projection=proposition_projection(proposition),
    )


def unresolved_relation(*, proposition: BoundProposition, evidence: EvidenceInput | None, reason: str) -> RelationRecord:
    evidence_ref = None
    if evidence is not None:
        evidence_ref = {"source_id": evidence.source_id, "passage_id": evidence.passage_id, "passage_sha256": evidence.passage_sha256}
    payload = {"claim_id": proposition.claim_id, "relation": "UNRESOLVED", "reason": reason, "evidence_ref": evidence_ref,
               "proposition": proposition_projection(proposition)}
    return RelationRecord(stable_id("relation", payload), proposition.claim_id, None, "UNRESOLVED", False, reason,
                          evidence_ref, proposition_projection(proposition))


def compose_categorical_relations(
    *, proposition: BoundProposition, relations: Iterable[RelationRecord], required_relation_count: int | None = None
) -> CategoricalConclusion:
    rows = tuple(relations)
    if required_relation_count is not None and len(rows) < required_relation_count:
        return CategoricalConclusion(proposition.claim_id, "abstained", None, "incomplete_required_composition",
                                     tuple(sorted(item.relation_id for item in rows)))
    ids = [item.relation_id for item in rows]
    if len(set(ids)) != len(ids):
        raise RC0Refusal("COMPOSITION_WRONG", "duplicate relation identities")
    for item in rows:
        if item.claim_id != proposition.claim_id or item.proposition_projection != proposition_projection(proposition):
            raise RC0Refusal("PROPOSITION_BINDING_FAILURE", "foreign proposition relation")
        if item.relation not in _ALLOWED_RELATIONS:
            raise RC0Refusal("COMPOSITION_WRONG", "unknown relation")
        if item.relation in _DECIDING_RELATIONS and not item.warranted:
            raise RC0Refusal("COMPOSITION_WRONG", "non-warranted deciding relation attempted participation")
    ordered = tuple(sorted(rows, key=lambda item: item.relation_id))
    unresolved = tuple(item for item in ordered if item.relation == "UNRESOLVED")
    supports = tuple(item for item in ordered if item.relation == "SUPPORTS")
    refutes = tuple(item for item in ordered if item.relation == "REFUTES")
    if unresolved:
        return CategoricalConclusion(proposition.claim_id, "abstained", None, "unresolved_categorical_relation",
                                     tuple(item.relation_id for item in unresolved))
    if supports and refutes:
        return CategoricalConclusion(proposition.claim_id, "abstained", None, "mixed_categorical_relations",
                                     tuple(item.relation_id for item in (*supports, *refutes)))
    if supports:
        return CategoricalConclusion(proposition.claim_id, "decided", "supported", "categorical_support",
                                     tuple(item.relation_id for item in supports))
    if refutes:
        return CategoricalConclusion(proposition.claim_id, "decided", "contradicted", "categorical_refutation",
                                     tuple(item.relation_id for item in refutes))
    return CategoricalConclusion(proposition.claim_id, "abstained", None, "no_deciding_categorical_relation",
                                 tuple(item.relation_id for item in ordered))


def _contract_c_policy() -> dict[str, Any]:
    return {
        "profile_id": PROFILE_ID,
        "decision_semantics": "scoreless_categorical",
        "deciding_semantic_families": [PROFILE_SEMANTIC_FAMILY],
        "measurement_only_semantic_families": ["event_ordering", "permission_composition"],
        "unsupported_family_behavior": "unresolved",
        "thresholds": [],
        "scalar_terminal_influence": False,
        "reader_count_terminal_influence": False,
    }


def _contribution_for_relation(*, proposition: BoundProposition, relation: RelationRecord) -> dict[str, Any] | None:
    if relation.relation not in _DECIDING_RELATIONS or relation.evidence_ref is None:
        return None
    channel = "support" if relation.relation == "SUPPORTS" else "counterevidence"
    cid = stable_id("contribution", {"proposition_id": proposition.claim_id, "channel": channel,
                                     "evidence_ref": relation.evidence_ref, "relation_id": relation.relation_id})
    return {"contribution_id": cid, "channel": channel, "evidence_ref": relation.evidence_ref}


def project_contract_c(
    *, proposition: BoundProposition, conclusion: CategoricalConclusion, relations: Iterable[RelationRecord],
    contract_b_binding: dict[str, str], semantic_implementation_sha: str
) -> tuple[bytes, dict[str, Any]]:
    if not re.fullmatch(r"[0-9a-f]{40}", semantic_implementation_sha):
        raise RC0Refusal("APPARATUS_FAILURE", "Contract C producer identity must be exact 40-hex SHA")
    policy = _contract_c_policy()
    policy_sha = sha256_hex(canonical_json_bytes(policy, trailing_newline=True))
    rows = tuple(relations)
    contribution_by_relation: dict[str, dict[str, Any]] = {}
    for row in rows:
        contribution = _contribution_for_relation(proposition=proposition, relation=row)
        if contribution is not None:
            contribution_by_relation[row.relation_id] = contribution
    if conclusion.disposition == "decided":
        basis = [contribution_by_relation[rid] for rid in conclusion.basis_relation_ids if rid in contribution_by_relation]
        if len(basis) != 1:
            completion, reported, terminal_branch = "not_checkable", "not_checkable", "rc0_projection_loss_unestablished_multiplicity"
            all_contrib = list(contribution_by_relation.values())
            conclusion_obj = {"reported_verdict": reported, "terminal_branch": terminal_branch,
                              "causal_form": "redundant_non_deciding", "basis_members": [],
                              "residual_contribution_ids": sorted(c["contribution_id"] for c in all_contrib), "rule_roles": []}
        else:
            completion, reported = "assessed", conclusion.verdict
            terminal_branch = "rc0_strict_comparison_support" if conclusion.verdict == "supported" else "rc0_strict_comparison_refutation"
            all_contrib = list(contribution_by_relation.values())
            basis_id = basis[0]["contribution_id"]
            conclusion_obj = {"reported_verdict": reported, "terminal_branch": terminal_branch,
                              "causal_form": "single_necessary", "basis_members": [{"namespace": "contribution", "id": basis_id}],
                              "residual_contribution_ids": sorted(c["contribution_id"] for c in all_contrib if c["contribution_id"] != basis_id),
                              "rule_roles": []}
    else:
        completion, reported, terminal_branch = "not_checkable", "not_checkable", "rc0_internal_abstention_projection"
        all_contrib = list(contribution_by_relation.values())
        conclusion_obj = {"reported_verdict": reported, "terminal_branch": terminal_branch,
                          "causal_form": "redundant_non_deciding", "basis_members": [],
                          "residual_contribution_ids": sorted(c["contribution_id"] for c in all_contrib), "rule_roles": []}
    proposition_result = {
        "proposition": {"proposition_id": proposition.claim_id, "text_sha256": claim_text_sha256(proposition.claim_text)},
        "execution": {"state": "completed", "completion": completion},
        "assessments": {name: {"state": "not_performed"} for name in
                        ("eligibility", "semantic_validity", "aperture_completeness", "temporal_applicability")},
        "contributions": sorted(all_contrib, key=lambda item: item["contribution_id"]),
        "measurement": None,
        "conclusion": conclusion_obj,
    }
    value = {
        "contract_c_version": CONTRACT_C_VERSION,
        "input": {"contract_b": deepcopy(contract_b_binding)},
        "producer": {"semantic_implementation_sha": semantic_implementation_sha,
                     "policy": {"canonical": policy, "sha256": policy_sha}},
        "execution": {"state": "completed"},
        "propositions": [proposition_result],
    }
    identity_payload = deepcopy(value)
    value["result_set_id"] = "result-set:" + sha256_hex(canonical_json_bytes(identity_payload, trailing_newline=True))
    raw = canonical_json_bytes(value, trailing_newline=True)
    projection = {
        "internal_disposition": conclusion.disposition,
        "internal_verdict": conclusion.verdict,
        "contract_c_completion": completion,
        "contract_c_reported_verdict": reported,
        "projection_loss": None if conclusion.disposition == "decided" and completion == "assessed" else {
            "internal_reason_code": conclusion.reason_code,
            "detail": "Contract C 1.0.0 does not preserve the RC0 internal categorical abstention distinction",
        },
    }
    if conclusion.disposition == "abstained" and reported != "not_checkable":
        raise RC0Refusal("CONTRACT_C_PROJECTION_FAILURE", "projection strengthened abstention")
    return raw, projection


def execute_rc0_case(
    *, proposition: BoundProposition, admitted_evidence: list[EvidenceInput], contract_b_validation: dict[str, Any],
    contract_b_binding: dict[str, str], measure_fn: MeasureFn, authority_evaluator: AuthorityEvaluator,
    atom_key: bytes, atom_key_id: str, proposition_key: bytes, proposition_key_id: str,
    semantic_implementation_sha: str, baseline_diagnostic: dict[str, Any] | None = None
) -> dict[str, Any]:
    if contract_b_validation != {"contract_version": CONTRACT_B_VERSION, "authority_commit": CONTRACT_B_AUTHORITY_COMMIT, "status": "PASS"}:
        raise RC0Refusal("APPARATUS_FAILURE", "exact Contract B 1.2 validation receipt required")
    if not admitted_evidence:
        relations = [unresolved_relation(proposition=proposition, evidence=None, reason="NO_ADMITTED_EVIDENCE")]
        conclusion = compose_categorical_relations(proposition=proposition, relations=relations, required_relation_count=1)
        c_raw, c_projection = project_contract_c(proposition=proposition, conclusion=conclusion, relations=relations,
                                                  contract_b_binding=contract_b_binding,
                                                  semantic_implementation_sha=semantic_implementation_sha)
        return {"contract_b_validation": contract_b_validation, "admitted_evidence_ids": [], "stages": [],
                "composition": asdict(conclusion), "internal_cal_conclusion": asdict(conclusion),
                "contract_c_projection": c_projection, "contract_c_bytes": c_raw.decode("utf-8"),
                "baseline_only": baseline_diagnostic or {"status": "NOT_RUN", "causal_influence": False}}
    proposition_binding = issue_proposition_binding(proposition=proposition, key=proposition_key, key_id=proposition_key_id)
    relations: list[RelationRecord] = []
    stages: list[dict[str, Any]] = []
    for evidence in admitted_evidence:
        stage: dict[str, Any] = {
            "passage_id": evidence.passage_id,
            "contract_b_admitted": True,
            "measurement": None,
            "typed_atom": None,
            "warrant_status": None,
            "warrant_atom_receipt_identity": None,
            "proposition_binding_identity": stable_id("proposition-binding", proposition_binding),
            "categorical_relation": None,
            "failure_category": None,
        }
        if evidence.semantic_family != PROFILE_SEMANTIC_FAMILY:
            relation = unresolved_relation(proposition=proposition, evidence=evidence, reason="UNSUPPORTED_SEMANTIC_FAMILY")
            relations.append(relation)
            stage["measurement"] = {"status": "NOT_RUN_UNSUPPORTED_FAMILY"}
            stage["categorical_relation"] = asdict(relation)
            stage["failure_category"] = "SAFE_ABSTENTION"
            stages.append(stage)
            continue
        measurement = measure_fn(evidence.passage_text)
        stage["measurement"] = deepcopy(measurement)
        atom, atom_state = complete_strict_comparison_atom(claim_id=proposition.claim_id, evidence=evidence, measurement=measurement)
        if atom is None:
            relation = unresolved_relation(proposition=proposition, evidence=evidence, reason=atom_state)
            relations.append(relation)
            stage["categorical_relation"] = asdict(relation)
            stage["failure_category"] = "MEASUREMENT_MISS_SAFE" if atom_state == "MEASUREMENT_MISS_SAFE" else "ATOM_INCOMPLETE"
            stages.append(stage)
            continue
        stage["typed_atom"] = asdict(atom)
        case = build_rc8j_case(atom=atom, evidence=evidence)
        authority_observation = authority_evaluator(deepcopy(case))
        stage["warrant_status"] = deepcopy(authority_observation)
        if authority_observation.get("authority_status") != "WARRANTED":
            relation = unresolved_relation(proposition=proposition, evidence=evidence,
                                           reason=f"WARRANT_{authority_observation.get('authority_status')}:{authority_observation.get('reason')}")
            relations.append(relation)
            stage["categorical_relation"] = asdict(relation)
            stage["failure_category"] = "WARRANT_UNRESOLVED"
            stages.append(stage)
            continue
        atom_warrant = issue_atom_warrant(case=case, authority_evaluator=authority_evaluator, key=atom_key, key_id=atom_key_id)
        stage["warrant_atom_receipt_identity"] = stable_id("warrant-receipt", atom_warrant)
        evidence_ref = {"source_id": evidence.source_id, "passage_id": evidence.passage_id, "passage_sha256": evidence.passage_sha256}
        relation = derive_categorical_relation(
            case=case, proposition=proposition, atom_warrant=atom_warrant, atom_trusted_keys={atom_key_id: atom_key},
            proposition_binding=proposition_binding, proposition_trusted_keys={proposition_key_id: proposition_key}, evidence_ref=evidence_ref)
        relations.append(relation)
        stage["categorical_relation"] = asdict(relation)
        stages.append(stage)
    conclusion = compose_categorical_relations(proposition=proposition, relations=relations,
                                               required_relation_count=len(admitted_evidence))
    c_raw, c_projection = project_contract_c(proposition=proposition, conclusion=conclusion, relations=relations,
                                              contract_b_binding=contract_b_binding,
                                              semantic_implementation_sha=semantic_implementation_sha)
    return {
        "contract_b_validation": deepcopy(contract_b_validation),
        "admitted_evidence_ids": [item.passage_id for item in admitted_evidence],
        "stages": stages,
        "composition": asdict(conclusion),
        "internal_cal_conclusion": asdict(conclusion),
        "contract_c_projection": c_projection,
        "contract_c_bytes": c_raw.decode("utf-8"),
        "baseline_only": baseline_diagnostic or {
            "status": "NOT_RUN",
            "reason": "released v1 optional inference stack intentionally absent from bounded RC0 apparatus",
            "causal_influence": False,
        },
    }


__all__ = [
    "AUTHORITY_BINDING_FIELDS", "BoundProposition", "CategoricalConclusion", "EvidenceInput", "PROFILE_ID",
    "PROFILE_SEMANTIC_FAMILY", "RC0Refusal", "RelationRecord", "StrictComparisonAtom", "authority_subject_digest",
    "build_rc8j_case", "canonical_json_bytes", "claim_text_sha256", "complete_strict_comparison_atom",
    "compose_categorical_relations", "derive_categorical_relation", "execute_rc0_case", "issue_atom_warrant",
    "issue_proposition_binding", "project_contract_c", "proposition_projection", "sha256_hex", "stable_id",
    "unresolved_relation", "verify_atom_warrant", "verify_proposition_binding",
]
