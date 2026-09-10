"""Bounded Phase-3 temporal conclusion -> unchanged Contract C 1.0 projection.

Research-only. This projector does not amend Contract C and does not perform a
Decision or Authorization. It refuses to invent support/counterevidence polarity
for temporal relations that Phase 3 classified as UNRESOLVED or IRRELEVANT.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping

from research.cal_event_order_relation_rc0 import candidate as temporal

CONTRACT_C_VERSION = "1.0.0"
SEMANTIC_IMPLEMENTATION_SHA = "94ea0c7531aeb852520f34bd56393b63a4b5ac75"
POLICY_CANONICAL: dict[str, Any] = {
    "profile": "cal-temporal-contract-c-decision-rc0",
    "semantic_family": "event_ordering",
    "relation_candidate_freeze": SEMANTIC_IMPLEMENTATION_SHA,
    "terminal_semantics": "scoreless_categorical",
    "negative_event_deciding": False,
    "contract_c_projection": "temporal-conclusion-v1",
}


class ProjectionRefusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


@dataclass(frozen=True, slots=True)
class ProjectionResult:
    contract_c: dict[str, Any]
    contract_b_index: dict[str, Any]
    projection_status: str
    omitted_relation_ids: tuple[str, ...]
    carried_relation_ids: tuple[str, ...]


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _stable_id(namespace: str, value: Any) -> str:
    return f"{namespace}:{sha256_hex(canonical_bytes(value))}"


def claim_text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def with_result_set_id(value: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(value)
    payload.pop("result_set_id", None)
    payload["result_set_id"] = "result-set:" + sha256_hex(canonical_bytes(payload))
    return payload


def _require_sha256_prefixed(value: str, label: str) -> None:
    if not isinstance(value, str) or len(value) != 71 or not value.startswith("sha256:"):
        raise ProjectionRefusal("INVALID_DIGEST", label)
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise ProjectionRefusal("INVALID_DIGEST", label) from exc
    if value[7:] != value[7:].lower():
        raise ProjectionRefusal("INVALID_DIGEST", label)


def _validate_binding(binding: Mapping[str, str]) -> dict[str, str]:
    if set(binding) != {"contract_version", "bundle_id", "bundle_hash"}:
        raise ProjectionRefusal("INVALID_CONTRACT_B_BINDING", "unexpected keys")
    contract_version = binding["contract_version"]
    bundle_id = binding["bundle_id"]
    bundle_hash = binding["bundle_hash"]
    if not contract_version or not bundle_id:
        raise ProjectionRefusal("INVALID_CONTRACT_B_BINDING", "empty identity")
    _require_sha256_prefixed(bundle_hash, "bundle_hash")
    return {
        "contract_version": contract_version,
        "bundle_id": bundle_id,
        "bundle_hash": bundle_hash,
    }


def _validate_evidence_index(
    evidence_index: Mapping[str, Mapping[str, str]],
) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for passage_id, value in evidence_index.items():
        if not isinstance(passage_id, str) or not passage_id:
            raise ProjectionRefusal("INVALID_EVIDENCE_INDEX", "empty passage id")
        if set(value) != {"source_id", "passage_sha256"}:
            raise ProjectionRefusal("INVALID_EVIDENCE_INDEX", passage_id)
        source_id = value["source_id"]
        passage_sha256 = value["passage_sha256"]
        if not source_id:
            raise ProjectionRefusal("INVALID_EVIDENCE_INDEX", passage_id)
        _require_sha256_prefixed(passage_sha256, f"passage:{passage_id}")
        out[passage_id] = {
            "source_id": source_id,
            "passage_sha256": passage_sha256,
        }
    return out


def _contribution_for_relation(
    relation: temporal.TemporalRelationRecord,
    evidence_index: Mapping[str, Mapping[str, str]],
) -> tuple[dict[str, Any] | None, bool]:
    if relation.relation == "SUPPORTS":
        channel = "support"
    elif relation.relation == "REFUTES":
        channel = "counterevidence"
    elif relation.relation in {"UNRESOLVED", "IRRELEVANT"}:
        return None, True
    else:
        raise ProjectionRefusal("UNKNOWN_TEMPORAL_RELATION", relation.relation)

    passage_id = relation.evidence_ref.get("passage_id")
    source_id = relation.evidence_ref.get("source_id")
    if not isinstance(passage_id, str) or not isinstance(source_id, str):
        raise ProjectionRefusal("INVALID_RELATION_EVIDENCE_REF", relation.relation_id)
    indexed = evidence_index.get(passage_id)
    if indexed is None:
        raise ProjectionRefusal("EVIDENCE_NOT_INDEXED", passage_id)
    if indexed["source_id"] != source_id:
        raise ProjectionRefusal("EVIDENCE_SOURCE_MISMATCH", passage_id)
    evidence_ref = {
        "source_id": source_id,
        "passage_id": passage_id,
        "passage_sha256": indexed["passage_sha256"],
    }
    contribution_id = _stable_id(
        "contribution",
        {
            "relation_id": relation.relation_id,
            "channel": channel,
            "evidence_ref": evidence_ref,
        },
    )
    return {
        "contribution_id": contribution_id,
        "channel": channel,
        "evidence_ref": evidence_ref,
    }, False


def _validate_phase3_objects(
    *,
    proposition: temporal.TemporalProposition,
    relations: tuple[temporal.TemporalRelationRecord, ...],
    conclusion: temporal.TemporalConclusion,
) -> None:
    if not isinstance(proposition, temporal.TemporalProposition):
        raise ProjectionRefusal("INVALID_TEMPORAL_PROPOSITION", type(proposition).__name__)
    if not isinstance(conclusion, temporal.TemporalConclusion):
        raise ProjectionRefusal("INVALID_TEMPORAL_CONCLUSION", type(conclusion).__name__)
    if conclusion.claim_id != proposition.claim_id:
        raise ProjectionRefusal("CONCLUSION_CLAIM_MISMATCH", conclusion.claim_id)
    if not relations:
        raise ProjectionRefusal("NO_TEMPORAL_RELATIONS", proposition.claim_id)
    expected_projection = temporal.proposition_projection(proposition)
    ids: set[str] = set()
    for row in relations:
        if not isinstance(row, temporal.TemporalRelationRecord):
            raise ProjectionRefusal("INVALID_TEMPORAL_RELATION", type(row).__name__)
        if row.relation_id in ids:
            raise ProjectionRefusal("DUPLICATE_TEMPORAL_RELATION", row.relation_id)
        ids.add(row.relation_id)
        if row.claim_id != proposition.claim_id:
            raise ProjectionRefusal("RELATION_CLAIM_MISMATCH", row.relation_id)
        if row.proposition_projection != expected_projection:
            raise ProjectionRefusal("RELATION_PROPOSITION_MISMATCH", row.relation_id)
        if row.relation in {"SUPPORTS", "REFUTES"} and not row.warranted:
            raise ProjectionRefusal("NONWARRANTED_DECIDING_RELATION", row.relation_id)
    if not set(conclusion.basis_relation_ids) <= ids:
        raise ProjectionRefusal("CONCLUSION_BASIS_UNKNOWN", proposition.claim_id)

    expected = temporal.compose_temporal_relations(
        proposition=proposition,
        relations=relations,
    )
    if expected != conclusion:
        raise ProjectionRefusal("CONCLUSION_RECOMPOSITION_MISMATCH", proposition.claim_id)


def project_temporal_contract_c(
    *,
    proposition: temporal.TemporalProposition,
    relations: Iterable[temporal.TemporalRelationRecord],
    conclusion: temporal.TemporalConclusion,
    contract_b_binding: Mapping[str, str],
    evidence_index: Mapping[str, Mapping[str, str]],
) -> ProjectionResult:
    """Project a frozen Phase-3 temporal conclusion into unchanged Contract C 1.0."""
    rows = tuple(relations)
    _validate_phase3_objects(
        proposition=proposition,
        relations=rows,
        conclusion=conclusion,
    )
    binding = _validate_binding(contract_b_binding)
    indexed_evidence = _validate_evidence_index(evidence_index)

    contributions: list[dict[str, Any]] = []
    contribution_by_relation: dict[str, str] = {}
    omitted: list[str] = []
    for row in sorted(rows, key=lambda item: item.relation_id):
        contribution, omitted_for_channel = _contribution_for_relation(row, indexed_evidence)
        if omitted_for_channel:
            omitted.append(row.relation_id)
            continue
        assert contribution is not None
        contributions.append(contribution)
        contribution_by_relation[row.relation_id] = contribution["contribution_id"]

    basis_ids = tuple(conclusion.basis_relation_ids)
    if conclusion.disposition == "decided" and conclusion.verdict in {"supported", "contradicted"}:
        missing = [relation_id for relation_id in basis_ids if relation_id not in contribution_by_relation]
        if missing:
            raise ProjectionRefusal("DECIDING_BASIS_NOT_PROJECTABLE", ",".join(missing))
        basis_members = [
            {"namespace": "contribution", "id": contribution_by_relation[relation_id]}
            for relation_id in basis_ids
        ]
        causal_form = (
            "single_necessary" if len(basis_members) == 1 else "independent_sufficient_alternatives"
        )
        completion = "assessed"
        reported_verdict = conclusion.verdict
    elif (
        conclusion.disposition == "abstained"
        and conclusion.verdict is None
        and conclusion.reason_code == "mixed_categorical_relations"
    ):
        missing = [relation_id for relation_id in basis_ids if relation_id not in contribution_by_relation]
        if missing or len(basis_ids) < 2:
            raise ProjectionRefusal("MIXED_BASIS_NOT_PROJECTABLE", ",".join(missing))
        basis_members = [
            {"namespace": "contribution", "id": contribution_by_relation[relation_id]}
            for relation_id in basis_ids
        ]
        causal_form = "jointly_sufficient"
        completion = "not_checkable"
        reported_verdict = "not_checkable"
    elif conclusion.disposition == "abstained" and conclusion.verdict is None:
        state_material = {
            "claim_id": proposition.claim_id,
            "reason_code": conclusion.reason_code,
            "basis_relation_ids": sorted(basis_ids),
        }
        basis_members = [{"namespace": "state", "id": _stable_id("state", state_material)}]
        causal_form = "single_necessary"
        completion = "not_checkable"
        reported_verdict = "not_checkable"
    else:
        raise ProjectionRefusal(
            "UNSUPPORTED_TEMPORAL_CONCLUSION_SHAPE",
            f"{conclusion.disposition}/{conclusion.verdict}/{conclusion.reason_code}",
        )

    causal_contribution_ids = {
        member["id"] for member in basis_members if member["namespace"] == "contribution"
    }
    residual_ids = sorted(
        contribution["contribution_id"]
        for contribution in contributions
        if contribution["contribution_id"] not in causal_contribution_ids
    )

    policy_sha = sha256_hex(canonical_bytes(POLICY_CANONICAL))
    contract_c = {
        "contract_c_version": CONTRACT_C_VERSION,
        "input": {"contract_b": binding},
        "producer": {
            "semantic_implementation_sha": SEMANTIC_IMPLEMENTATION_SHA,
            "policy": {
                "sha256": policy_sha,
                "canonical": deepcopy(POLICY_CANONICAL),
            },
        },
        "execution": {"state": "completed"},
        "propositions": [
            {
                "proposition": {
                    "proposition_id": proposition.claim_id,
                    "text_sha256": claim_text_sha256(proposition.claim_text),
                },
                "execution": {"state": "completed", "completion": completion},
                "assessments": {
                    "eligibility": {"state": "not_performed"},
                    "semantic_validity": {"state": "not_performed"},
                    "aperture_completeness": {"state": "not_performed"},
                    "temporal_applicability": {"state": "not_performed"},
                },
                "contributions": contributions,
                "measurement": None,
                "conclusion": {
                    "reported_verdict": reported_verdict,
                    "terminal_branch": conclusion.reason_code,
                    "causal_form": causal_form,
                    "basis_members": basis_members,
                    "residual_contribution_ids": residual_ids,
                    "rule_roles": [],
                },
            }
        ],
    }
    contract_c = with_result_set_id(contract_c)

    contract_b_index = {
        **binding,
        "propositions": {
            proposition.claim_id: claim_text_sha256(proposition.claim_text),
        },
        "passages": deepcopy(indexed_evidence),
    }
    carried = tuple(sorted(contribution_by_relation))
    status = (
        "VALID_WITH_PROVENANCE_COMPRESSION"
        if omitted
        else "LOSSLESS_TERMINAL_AND_DECIDING_PROVENANCE"
    )
    return ProjectionResult(
        contract_c=contract_c,
        contract_b_index=contract_b_index,
        projection_status=status,
        omitted_relation_ids=tuple(sorted(omitted)),
        carried_relation_ids=carried,
    )


__all__ = [
    "CONTRACT_C_VERSION",
    "POLICY_CANONICAL",
    "ProjectionRefusal",
    "ProjectionResult",
    "SEMANTIC_IMPLEMENTATION_SHA",
    "canonical_bytes",
    "claim_text_sha256",
    "project_temporal_contract_c",
    "sha256_hex",
    "with_result_set_id",
]
