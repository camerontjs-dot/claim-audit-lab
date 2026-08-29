"""Minimal producer for Apparatus Contract C 1.0.0 from CAL v0.2 state."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import asdict
from typing import Any, Literal

from claim_audit_lab.contracts.bundle_loader import BundleContents
from claim_audit_lab.models import (
    AuditConfig,
    ClaimAssessment,
    EvidenceBundle,
    EvidenceCandidate,
)
from claim_audit_lab.policy import CAL_RULES_V1_2_0, AuditPolicy
from claim_audit_lab.rules import assess_claim_support

CONTRACT_C_VERSION = "1.0.0"
CONTRACT_C_SEMANTIC_IMPLEMENTATION_SHA = "33a928db97316a3652d57df9cafb8ca240305233"
MEASUREMENT_KIND = "cal_v0_2_aggregate_support_signal"

_ASSESSMENT_STAGES = (
    "eligibility",
    "semantic_validity",
    "aperture_completeness",
    "temporal_applicability",
)
_SUPPORTED_RULE_CODES = {
    "credential_missing_source",
    "counterevidence_present",
    "future_certainty",
    "low_reliability_only",
    "overconfident_wording",
}


class ContractCExportError(ValueError):
    """Raised when current CAL state cannot be exported without inventing semantics."""


def canonical_bytes(value: Any) -> bytes:
    """Return the Contract-C deterministic JSON representation."""
    _reject_non_finite(value)
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


def export_contract_c(
    *,
    contents: BundleContents,
    assessments: list[ClaimAssessment],
    evidence_bundle: EvidenceBundle,
    audit_config: AuditConfig,
    policy: AuditPolicy = CAL_RULES_V1_2_0,
) -> dict[str, Any]:
    """Export the bounded CAL v0.2 producer state as Contract C 1.0.0.

    The exporter performs only the intervention-derived attribution already
    supported for this frozen CAL policy. Unsupported rule/multiplicity shapes
    fail closed rather than widening the contract or inventing a basis.
    """
    canonical_policy = asdict(policy)
    if policy != CAL_RULES_V1_2_0:
        raise ContractCExportError(
            "Contract C 1.0.0 exporter supports only CAL_RULES_V1_2_0"
        )

    result: dict[str, Any] = {
        "contract_c_version": CONTRACT_C_VERSION,
        "input": {
            "contract_b": {
                "contract_version": contents.manifest.schema_version,
                "bundle_id": contents.manifest.bundle_id,
                "bundle_hash": contents.manifest.bundle.bundle_hash,
            }
        },
        "producer": {
            "semantic_implementation_sha": CONTRACT_C_SEMANTIC_IMPLEMENTATION_SHA,
            "policy": {
                "canonical": canonical_policy,
                "sha256": _sha256(canonical_bytes(canonical_policy)),
            },
        },
        "execution": {"state": "completed"},
        "propositions": [
            _project_assessment(
                assessment=assessment,
                contents=contents,
                evidence_bundle=evidence_bundle,
                audit_config=audit_config,
                policy=policy,
            )
            for assessment in assessments
        ],
    }
    if not result["propositions"]:
        raise ContractCExportError(
            "completed Contract C result set requires proposition results"
        )
    result["result_set_id"] = _result_set_id(result)
    return result


def export_contract_c_bytes(
    *,
    contents: BundleContents,
    assessments: list[ClaimAssessment],
    evidence_bundle: EvidenceBundle,
    audit_config: AuditConfig,
    policy: AuditPolicy = CAL_RULES_V1_2_0,
) -> bytes:
    """Export canonical Contract-C bytes."""
    return canonical_bytes(
        export_contract_c(
            contents=contents,
            assessments=assessments,
            evidence_bundle=evidence_bundle,
            audit_config=audit_config,
            policy=policy,
        )
    )


def _project_assessment(
    *,
    assessment: ClaimAssessment,
    contents: BundleContents,
    evidence_bundle: EvidenceBundle,
    audit_config: AuditConfig,
    policy: AuditPolicy,
) -> dict[str, Any]:
    rows = _contribution_rows(assessment, contents)
    contribution_ids = [row["contribution_id"] for row in rows]
    measurement_basis = _measurement_basis(rows)
    rule_codes = {flag.code for flag in assessment.rule_flags}
    unsupported_rules = rule_codes - _SUPPORTED_RULE_CODES
    if unsupported_rules:
        raise ContractCExportError(
            "Contract C 1.0.0 has no promoted attribution for rule codes: "
            + ",".join(sorted(unsupported_rules))
        )

    branch = _terminal_branch(assessment, policy)
    basis_members: list[dict[str, str]]
    causal_form: str
    residual_ids: list[str]
    rule_roles: list[dict[str, str]]

    if (
        assessment.support_label == "not_checkable"
        and assessment.claim.claim_type == "unclassified"
    ):
        if rows:
            raise ContractCExportError(
                "unclassified early-return with retained candidates is not promoted"
            )
        causal_form = "single_necessary"
        basis_members = [
            {"namespace": "state", "id": "state:claim_type:unclassified"}
        ]
        residual_ids = []
        rule_roles = []
        measurement: dict[str, Any] | None = None
        completion = "not_checkable"
    elif (
        assessment.support_label == "overstated"
        and {"future_certainty", "overconfident_wording"} <= rule_codes
        and assessment.counterevidence
    ):
        causal_form = "jointly_sufficient"
        basis_members = [
            {"namespace": "state", "id": "state:absolute_lexical_trigger"},
            {
                "namespace": "state",
                "id": "state:counterevidence_contexts_nonempty",
            },
        ]
        residual_ids = sorted(contribution_ids)
        rule_roles = _rule_roles_for_overstatement(assessment)
        measurement = _measurement(assessment, measurement_basis)
        completion = "assessed"
    elif (
        assessment.support_label == "needs_source"
        and "credential_missing_source" in rule_codes
    ):
        causal_form = "single_necessary"
        basis_members = [
            {
                "namespace": "state",
                "id": "state:direct_support_contexts_empty",
            }
        ]
        residual_ids = sorted(contribution_ids)
        rule_roles = [
            {
                "rule_id": (
                    f"rule-role:{assessment.claim.id}:credential_missing_source"
                ),
                "code": "credential_missing_source",
                "terminal_role": "causal",
            }
        ]
        measurement = _measurement(assessment, measurement_basis)
        completion = "assessed"
    else:
        causal_form, causal_ids, residual_ids = _contribution_attribution(
            assessment=assessment,
            rows=rows,
            evidence_bundle=evidence_bundle,
            audit_config=audit_config,
            policy=policy,
        )
        basis_members = [
            {"namespace": "contribution", "id": contribution_id}
            for contribution_id in sorted(causal_ids)
        ]
        rule_roles = _generic_rule_roles(
            assessment=assessment,
            evidence_bundle=evidence_bundle,
            audit_config=audit_config,
            policy=policy,
        )
        measurement = _measurement(assessment, measurement_basis)
        completion = "assessed"

    return {
        "proposition": {
            "proposition_id": assessment.claim.id,
            "text_sha256": _sha256(assessment.claim.text.encode("utf-8")),
        },
        "execution": {"state": "completed", "completion": completion},
        "assessments": {
            name: {"state": "not_performed"} for name in _ASSESSMENT_STAGES
        },
        "contributions": [
            {
                "contribution_id": row["contribution_id"],
                "channel": row["channel"],
                "evidence_ref": row["evidence_ref"],
            }
            for row in rows
        ],
        "measurement": measurement,
        "conclusion": {
            "reported_verdict": assessment.support_label,
            "terminal_branch": branch,
            "causal_form": causal_form,
            "basis_members": basis_members,
            "residual_contribution_ids": residual_ids,
            "rule_roles": rule_roles,
        },
    }


def _contribution_rows(
    assessment: ClaimAssessment,
    contents: BundleContents,
) -> list[dict[str, Any]]:
    lookup = {
        (source_id, f"{source_id}/{passage.passage_id}"): passage
        for source_id, passages in contents.passages.items()
        for passage in passages
    }
    rows: list[dict[str, Any]] = []
    for channel, candidates in (
        ("support", assessment.candidate_evidence),
        ("counterevidence", assessment.counterevidence),
    ):
        for candidate in candidates:
            passage = lookup.get((candidate.source_id, candidate.excerpt_id))
            if passage is None:
                raise ContractCExportError(
                    "candidate cannot be resolved to Contract B: "
                    f"{candidate.source_id}/{candidate.excerpt_id}"
                )
            ref = {
                "source_id": candidate.source_id,
                "passage_id": passage.passage_id,
                "passage_sha256": passage.passage_hash,
            }
            rows.append(
                {
                    "contribution_id": _stable_id(
                        "contribution",
                        {
                            "proposition_id": assessment.claim.id,
                            "channel": channel,
                            "evidence_ref": ref,
                        },
                    ),
                    "channel": channel,
                    "evidence_ref": ref,
                    "candidate": candidate,
                }
            )
    return rows


def _measurement_basis(rows: list[dict[str, Any]]) -> list[str]:
    support = [row for row in rows if row["channel"] == "support"]
    counters = [row for row in rows if row["channel"] == "counterevidence"]
    basis: list[str] = []
    if support:
        maximum = max(row["candidate"].score for row in support)
        basis.extend(
            row["contribution_id"]
            for row in support
            if row["candidate"].score == maximum
        )
    if counters:
        maximum = max(row["candidate"].score for row in counters)
        basis.extend(
            row["contribution_id"]
            for row in counters
            if row["candidate"].score == maximum
        )
    return basis


def _measurement(
    assessment: ClaimAssessment,
    basis: list[str],
) -> dict[str, Any] | None:
    if not basis:
        return None
    return {
        "kind": MEASUREMENT_KIND,
        "value": assessment.support_signal,
        "basis_contribution_ids": basis,
    }


def _contribution_attribution(
    *,
    assessment: ClaimAssessment,
    rows: list[dict[str, Any]],
    evidence_bundle: EvidenceBundle,
    audit_config: AuditConfig,
    policy: AuditPolicy,
) -> tuple[str, list[str], list[str]]:
    if not rows:
        raise ContractCExportError(
            "no promoted causal basis for contribution-free "
            f"{assessment.support_label} result"
        )

    support_rows = [row for row in rows if row["channel"] == "support"]
    counter_rows = [
        row for row in rows if row["channel"] == "counterevidence"
    ]
    support_source = [row["candidate"] for row in support_rows]
    counter_source = [row["candidate"] for row in counter_rows]
    target = assessment.support_label
    all_ids = [row["contribution_id"] for row in rows]

    necessary: list[str] = []
    for row in rows:
        support = list(support_source)
        counters = list(counter_source)
        if row["channel"] == "support":
            support.remove(row["candidate"])
        else:
            counters.remove(row["candidate"])
        if (
            _replay_label(
                assessment,
                evidence_bundle,
                support,
                counters,
                audit_config,
                policy,
            )
            != target
        ):
            necessary.append(row["contribution_id"])

    if len(necessary) == 1:
        causal = sorted(necessary)
        return "single_necessary", causal, sorted(set(all_ids) - set(causal))

    if len(necessary) >= 2:
        isolated_target = []
        for row in rows:
            if row["contribution_id"] not in necessary:
                continue
            if row["channel"] == "support":
                support = [row["candidate"]]
                counters: list[EvidenceCandidate] = []
            else:
                support = []
                counters = [row["candidate"]]
            isolated_target.append(
                _replay_label(
                    assessment,
                    evidence_bundle,
                    support,
                    counters,
                    audit_config,
                    policy,
                )
                == target
            )
        if not any(isolated_target):
            causal = sorted(necessary)
            return (
                "jointly_sufficient",
                causal,
                sorted(set(all_ids) - set(causal)),
            )
        raise ContractCExportError(
            "necessary contributors show an unsupported mixed multiplicity"
        )

    # RC2-D explicitly falsified terminal-replay-alone as causal evidence:
    # residual state can reproduce an already-adverse terminal verdict in
    # isolation without deciding that verdict. Independent alternatives are
    # therefore recognized only for the demonstrated tied/co-maximal shape.
    measurement_basis = set(_measurement_basis(rows))
    tied_support = [
        row
        for row in support_rows
        if row["contribution_id"] in measurement_basis
    ]
    if len(tied_support) >= 2:
        isolated_target = [
            _replay_label(
                assessment,
                evidence_bundle,
                [row["candidate"]],
                [],
                audit_config,
                policy,
            )
            == target
            for row in tied_support
        ]
        none_target = (
            _replay_label(
                assessment,
                evidence_bundle,
                [],
                counter_source,
                audit_config,
                policy,
            )
            == target
        )
        if all(isolated_target) and not none_target:
            causal = sorted(
                row["contribution_id"] for row in tied_support
            )
            return (
                "independent_sufficient_alternatives",
                causal,
                sorted(set(all_ids) - set(causal)),
            )

    return "redundant_non_deciding", [], sorted(all_ids)


def _replay_label(
    assessment: ClaimAssessment,
    evidence_bundle: EvidenceBundle,
    support: list[EvidenceCandidate],
    counters: list[EvidenceCandidate],
    audit_config: AuditConfig,
    policy: AuditPolicy,
) -> str:
    return assess_claim_support(
        assessment.claim,
        evidence_bundle,
        support,
        audit_config,
        counterevidence=counters,
        policy=policy,
    ).support_label


def _generic_rule_roles(
    *,
    assessment: ClaimAssessment,
    evidence_bundle: EvidenceBundle,
    audit_config: AuditConfig,
    policy: AuditPolicy,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for code in sorted(flag.code for flag in assessment.rule_flags):
        if code != "low_reliability_only":
            raise ContractCExportError(
                f"no promoted generic rule-role control for {code}"
            )
        high_support = [
            candidate.model_copy(update={"source_reliability": "high"})
            for candidate in assessment.candidate_evidence
        ]
        high_counters = [
            candidate.model_copy(update={"source_reliability": "high"})
            for candidate in assessment.counterevidence
        ]
        high_bundle = evidence_bundle.model_copy(
            update={
                "sources": [
                    source.model_copy(update={"reliability": "high"})
                    for source in evidence_bundle.sources
                ]
            }
        )
        mutated = assess_claim_support(
            assessment.claim,
            high_bundle,
            high_support,
            audit_config,
            counterevidence=high_counters,
            policy=policy,
        )
        rows.append(
            {
                "rule_id": f"rule-role:{assessment.claim.id}:{code}",
                "code": code,
                "terminal_role": (
                    "causal"
                    if mutated.support_label != assessment.support_label
                    else "residual"
                ),
            }
        )
    return rows


def _rule_roles_for_overstatement(
    assessment: ClaimAssessment,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for code in sorted(flag.code for flag in assessment.rule_flags):
        if code in {"future_certainty", "overconfident_wording"}:
            role: Literal["causal", "residual"] = "causal"
        elif code == "counterevidence_present":
            role = "residual"
        else:
            raise ContractCExportError(
                f"unsupported overstatement rule combination: {code}"
            )
        rows.append(
            {
                "rule_id": f"rule-role:{assessment.claim.id}:{code}",
                "code": code,
                "terminal_role": role,
            }
        )
    return rows


def _terminal_branch(
    assessment: ClaimAssessment,
    policy: AuditPolicy,
) -> str:
    verdict = assessment.support_label
    if verdict == "not_checkable":
        return "unclassified_early_return"
    if verdict == "needs_source":
        return "needs_source_rule_family"
    if verdict == "overstated":
        return "overstated_rule_family"
    if verdict == "unsupported":
        return "support_below_partial_threshold"
    if verdict == "partially_supported":
        if (
            assessment.support_signal is not None
            and assessment.support_signal < policy.sourced_support
        ):
            return "support_between_thresholds"
        return "residual_or_counter_limit_branch"
    if verdict == "supported":
        return "supported_score_branch"
    raise ContractCExportError(f"unsupported CAL verdict: {verdict}")


def _result_set_id(value: dict[str, Any]) -> str:
    payload = copy.deepcopy(value)
    payload.pop("result_set_id", None)
    return "result-set:" + _sha256(canonical_bytes(payload))


def _stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}:" + _sha256(canonical_bytes(value))


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _reject_non_finite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractCExportError(
            "non-finite number is not permitted in Contract C"
        )
    if isinstance(value, dict):
        for child in value.values():
            _reject_non_finite(child)
    elif isinstance(value, list):
        for child in value:
            _reject_non_finite(child)


__all__ = [
    "CONTRACT_C_SEMANTIC_IMPLEMENTATION_SHA",
    "CONTRACT_C_VERSION",
    "ContractCExportError",
    "canonical_bytes",
    "export_contract_c",
    "export_contract_c_bytes",
]
