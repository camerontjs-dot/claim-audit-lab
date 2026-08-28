"""Research-only Contract-C RC1 semantic package projector.

This module is deliberately outside ``src/``. It observes frozen CAL outputs and
materializes a candidate semantic package without changing the production audit
path. The package shape is experimental and carries no Contract-C version.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

REQUIRED_FAMILIES = (
    "identity",
    "evidence",
    "measurements",
    "assessments",
    "conclusion",
    "reassessment",
    "execution",
)

ASSESSMENT_STATES = {
    "not_performed",
    "performed",
    "failed",
    "not_applicable",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _stable_id(payload: dict[str, Any]) -> str:
    return sha256_text(canonical_json(payload))


def _assessment_not_performed() -> dict[str, str]:
    return {"state": "not_performed"}


def project_production_trace(
    trace: dict[str, Any],
    *,
    contract_b_binding: dict[str, str],
    cal_code_sha: str,
) -> dict[str, Any]:
    """Project one frozen production ``AuditTrace`` into candidate C1.

    ``contract_b_binding`` is supplied separately because the production
    ``AuditTrace`` does not contain the exact Contract-B bundle identity. That is
    itself an RC1 observation: trace-only projection cannot satisfy exact lineage
    without boundary context CAL legitimately has at execution time.
    """

    claim_id = str(trace["claim_id"])
    claim_text = str(trace["claim_text"])
    verdict = dict(trace["verdict"])
    support_signal = dict(trace["support_signal"])

    evidence_refs: list[dict[str, Any]] = []
    measurements: list[dict[str, Any]] = []
    seen: set[str] = set()
    for result in trace.get("entailment", []):
        passage_id = str(result["passage_id"])
        if passage_id not in seen:
            evidence_refs.append({"evidence_id": passage_id, "source": "contract_b"})
            seen.add(passage_id)
        measurements.append(
            {
                "measurement_id": f"relation:{passage_id}",
                "kind": "claim_passage_relation",
                "evidence_id": passage_id,
                "relation": result["label"],
                "score": result["score"],
            }
        )

    contributing = support_signal.get("contributing_passage_id")
    if contributing and contributing not in seen:
        evidence_refs.append({"evidence_id": contributing, "source": "contract_b"})
        seen.add(contributing)

    measurements.append(
        {
            "measurement_id": "aggregate:relation",
            "kind": "aggregated_relation",
            "relation": support_signal["label"],
            "score": support_signal["max_entailment_score"],
            "evidence_id": contributing,
        }
    )

    rule_ids = [str(item["rule_id"]) for item in trace.get("rules_fired", [])]
    counterevidence_ids = [
        str(item["passage_id"])
        for item in trace.get("entailment", [])
        if item.get("label") == "contradict"
    ]
    unresolved_ids = [
        str(item["passage_id"])
        for item in trace.get("entailment", [])
        if item.get("label") == "neutral"
    ]

    payload: dict[str, Any] = {
        "candidate_profile": "contract-c-rc1-semantic-package",
        "identity": {
            "producer": "claim-audit-lab",
            "producer_code_sha": cal_code_sha,
            "cal_library_version": trace["library_version"],
            "contract_b": copy.deepcopy(contract_b_binding),
            "proposition": {
                "proposition_id": claim_id,
                "text": claim_text,
                "text_sha256": sha256_text(claim_text),
            },
            "audit_config_sha256": trace["audit_config_hash"],
        },
        "evidence": {
            "refs": sorted(evidence_refs, key=lambda item: item["evidence_id"]),
            "counterevidence_ids": sorted(set(counterevidence_ids)),
            "unresolved_evidence_ids": sorted(set(unresolved_ids)),
        },
        "measurements": measurements,
        "assessments": {
            "citation": {"state": "performed", "value": verdict["citation_status"]},
            "eligibility": _assessment_not_performed(),
            "semantic_validity": _assessment_not_performed(),
            "aperture": _assessment_not_performed(),
            "temporal_applicability": _assessment_not_performed(),
        },
        "conclusion": {
            "reported_verdict": verdict["support_verdict"],
            "reason_code": verdict.get("support_verdict_reason"),
            "audit_flags": list(verdict.get("audit_flags", [])),
            "basis": {
                "evidence_ids": [contributing] if contributing else [],
                "rule_ids": rule_ids,
            },
            "residual": {
                "counterevidence_ids": sorted(set(counterevidence_ids)),
                "unresolved_evidence_ids": sorted(set(unresolved_ids)),
            },
        },
        "reassessment": {
            "relation": "original",
            "prior_result_id": None,
        },
        "execution": {
            "status": "completed",
            "failures": [],
            "deviations": [],
        },
    }
    package = copy.deepcopy(payload)
    package["result_id"] = _stable_id(payload)
    return package


def thin_projection(package: dict[str, Any]) -> dict[str, Any]:
    """C2 control: deliberately overfit thin projection."""
    proposition = package["identity"]["proposition"]
    conclusion = package["conclusion"]
    return {
        "proposition_id": proposition["proposition_id"],
        "reported_verdict": conclusion["reported_verdict"],
    }


def render_human_report(package: dict[str, Any], *, renderer_policy_id: str) -> str:
    """C3 control: deterministic human Markdown derived from C1 only."""
    errors = validate_package(package)
    if errors:
        raise ValueError("invalid semantic package: " + "; ".join(errors))
    proposition = package["identity"]["proposition"]
    conclusion = package["conclusion"]
    execution = package["execution"]
    lines = [
        f"# CAL semantic audit: {proposition['proposition_id']}",
        "",
        f"Renderer policy: `{renderer_policy_id}`",
        f"Result ID: `{package['result_id']}`",
        f"Execution: `{execution['status']}`",
        "",
        f"> {proposition['text']}",
        "",
        f"Reported CAL verdict: `{conclusion['reported_verdict']}`",
        f"Reason: `{conclusion.get('reason_code') or 'none'}`",
        "",
        "## Decision basis",
        "",
        "Evidence: " + (", ".join(conclusion["basis"]["evidence_ids"]) or "none"),
        "Rules: " + (", ".join(conclusion["basis"]["rule_ids"]) or "none"),
        "",
        "## Residual state",
        "",
        "Counterevidence: "
        + (", ".join(conclusion["residual"]["counterevidence_ids"]) or "none"),
        "Unresolved evidence: "
        + (", ".join(conclusion["residual"]["unresolved_evidence_ids"]) or "none"),
        "",
        "## Assessment state",
        "",
    ]
    for name in sorted(package["assessments"]):
        item = package["assessments"][name]
        rendered = item["state"]
        if "value" in item:
            rendered += f" / {item['value']}"
        lines.append(f"- {name}: `{rendered}`")
    if execution["failures"]:
        lines.extend(["", "## Execution failures", ""])
        for failure in execution["failures"]:
            lines.append(f"- `{failure['code']}`: {failure['message']}")
    return "\n".join(lines).rstrip() + "\n"


def validate_package(package: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for family in REQUIRED_FAMILIES:
        if family not in package:
            errors.append(f"missing family: {family}")
    if errors:
        return errors

    identity = package["identity"]
    if not identity.get("contract_b", {}).get("bundle_sha256"):
        errors.append("missing exact Contract-B bundle binding")
    proposition = identity.get("proposition", {})
    if not proposition.get("text_sha256"):
        errors.append("missing proposition text hash")
    elif proposition.get("text") is not None and proposition["text_sha256"] != sha256_text(
        str(proposition["text"])
    ):
        errors.append("proposition text hash mismatch")
    if not identity.get("audit_config_sha256"):
        errors.append("missing audit config identity")

    body = copy.deepcopy(package)
    result_id = body.pop("result_id", None)
    if result_id is None:
        errors.append("missing result identity")
    elif result_id != _stable_id(body):
        errors.append("result identity mismatch")

    known_evidence = {item["evidence_id"] for item in package["evidence"].get("refs", [])}
    for measurement in package["measurements"]:
        evidence_id = measurement.get("evidence_id")
        if evidence_id is not None and evidence_id not in known_evidence:
            errors.append(f"measurement references missing evidence: {evidence_id}")
    basis = package["conclusion"].get("basis", {})
    for evidence_id in basis.get("evidence_ids", []):
        if evidence_id not in known_evidence:
            errors.append(f"decision basis references missing evidence: {evidence_id}")

    for name, assessment in package["assessments"].items():
        state = assessment.get("state")
        if state not in ASSESSMENT_STATES:
            errors.append(f"invalid assessment state for {name}: {state}")
        if state == "performed" and "value" not in assessment:
            errors.append(f"performed assessment missing value: {name}")
        if state == "failed" and not assessment.get("failure"):
            errors.append(f"failed assessment missing failure: {name}")

    status = package["execution"].get("status")
    if status not in {"completed", "partial", "failed"}:
        errors.append(f"invalid execution status: {status}")
    if status == "completed" and package["execution"].get("failures"):
        errors.append("completed execution may not carry failures")
    return errors


def with_result_identity(payload: dict[str, Any]) -> dict[str, Any]:
    """Recompute immutable identity after a deliberate research mutation."""
    body = copy.deepcopy(payload)
    body.pop("result_id", None)
    body["result_id"] = _stable_id(body)
    return body


def build_result_set(
    results: list[dict[str, Any]],
    *,
    contract_b_binding: dict[str, str],
    run_execution: dict[str, Any],
) -> dict[str, Any]:
    """Build a research-only multi-proposition envelope.

    The envelope deduplicates input binding at run scope but does not remove the
    per-result binding yet. That redundancy is deliberate in RC1 so compression
    can be measured rather than assumed.
    """
    payload: dict[str, Any] = {
        "candidate_profile": "contract-c-rc1-result-set",
        "contract_b": copy.deepcopy(contract_b_binding),
        "results": copy.deepcopy(results),
        "execution": copy.deepcopy(run_execution),
    }
    envelope = copy.deepcopy(payload)
    envelope["result_set_id"] = _stable_id(payload)
    return envelope


def validate_result_set(result_set: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not result_set.get("contract_b", {}).get("bundle_sha256"):
        errors.append("result set missing exact Contract-B bundle binding")
    results = result_set.get("results")
    if not isinstance(results, list) or not results:
        errors.append("result set has no proposition results")
        return errors

    run_binding = result_set.get("contract_b", {})
    for index, result in enumerate(results):
        for error in validate_package(result):
            errors.append(f"result[{index}]: {error}")
        if result.get("identity", {}).get("contract_b") != run_binding:
            errors.append(f"result[{index}]: Contract-B binding differs from result set")

    execution = result_set.get("execution", {})
    status = execution.get("status")
    if status not in {"completed", "partial", "failed"}:
        errors.append(f"invalid result-set execution status: {status}")
    result_statuses = {result.get("execution", {}).get("status") for result in results}
    if status == "completed" and result_statuses != {"completed"}:
        errors.append("completed result set contains incomplete proposition result")
    if status == "partial" and not (
        "completed" in result_statuses and ({"partial", "failed"} & result_statuses)
    ):
        errors.append(
            "partial result set must contain completed and incomplete proposition results"
        )
    if status == "failed" and "completed" in result_statuses:
        errors.append("failed result set contains completed proposition result")

    body = copy.deepcopy(result_set)
    result_set_id = body.pop("result_set_id", None)
    if result_set_id is None:
        errors.append("missing result-set identity")
    elif result_set_id != _stable_id(body):
        errors.append("result-set identity mismatch")
    return errors
