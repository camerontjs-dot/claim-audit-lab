from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from claim_audit_lab.cal_v1_candidate import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
    audit,
    project_contract_c_successor,
)
from claim_audit_lab.cal_v1_candidate.authority import complete_and_warrant
from claim_audit_lab.cal_v1_candidate.cli import context_from_packet
from claim_audit_lab.cal_v1_candidate.measurements import measure_strict_comparison
from claim_audit_lab.cal_v1_candidate.models import stable_id
from claim_audit_lab.cal_v1_candidate.relations import derive_relation

_ROOT = Path(__file__).resolve().parents[1]
_RECORD_DIR = _ROOT / "research" / "cal_v1_rc1_qualification_20260912"
_COHORT = json.loads((_RECORD_DIR / "COHORT.json").read_text(encoding="utf-8"))
_GOLD = json.loads((_RECORD_DIR / "GOLD.json").read_text(encoding="utf-8"))
_FROZEN_SHA = "a902621e8baea3063dddd7f92ba975aade305464"


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _context(case: dict[str, Any], *, bundle_id: str | None = None) -> AuditContext:
    case_id = str(case["id"])
    passages = tuple(
        AdmittedPassage.create(
            f"{case_id.lower()}-p{index}",
            f"{case_id.lower()}-source",
            str(text),
        )
        for index, text in enumerate(case["passages"], start=1)
    )
    actual_bundle = bundle_id or f"{case_id.lower()}-bundle"
    world = EvidenceWorld.create(
        "1.2.0",
        actual_bundle,
        _tagged(actual_bundle),
        passages,
        {
            "search_scope": {"cohort": _COHORT["cohort_id"], "case": case_id},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        str(case["proposition_id"]),
        SemanticFamily(str(case["semantic_family"])),
        {str(key): str(value) for key, value in case["fields"].items()},
        text_sha256=_hex(str(case["proposition_text"])),
    )
    return AuditContext(str(case["proposition_text"]), proposition, world)


def _failure_value(value: Any) -> str | None:
    return None if value is None else str(value.value)


def _atom_material(atom: Any) -> dict[str, object]:
    return {
        "semantic_family": atom.semantic_family.value,
        "audit_context_sha256": atom.audit_context_sha256,
        "evidence_world_sha256": atom.evidence_world_sha256,
        "passage_id": atom.passage_id,
        "source_id": atom.source_id,
        "fields": atom.field_map(),
        "measurement_receipt_id": atom.measurement_receipt_id,
    }


def _authority_material(authority: Any) -> dict[str, object]:
    return {
        "atom_id": authority.atom.atom_id,
        "audit_context_sha256": authority.audit_context_sha256,
        "evidence_world_sha256": authority.evidence_world_sha256,
        "status": authority.status,
        "reason": authority.reason,
    }


def _projection_observation(case: dict[str, Any]) -> dict[str, Any]:
    context = _context(case)
    result = audit(context)
    payload = project_contract_c_successor(
        context,
        result,
        semantic_implementation_sha=_FROZEN_SHA,
    )
    proposition = payload["propositions"][0]
    return {
        "outcome": "RETURNED",
        "conclusion": result.conclusion.value,
        "failure_code": _failure_value(result.failure_code),
        "contract_c_version": payload["contract_c_version"],
        "reported_verdict": proposition["conclusion"]["reported_verdict"],
        "channels": [item["channel"] for item in proposition["contributions"]],
        "causal_form": proposition["conclusion"]["causal_form"],
        "result_set_id": payload["result_set_id"],
        "payload": payload,
    }


def _reject_observation(call: Any) -> dict[str, Any]:
    try:
        relation = call()
    except Exception as exc:
        return {
            "outcome": "REJECTED",
            "exception": type(exc).__name__,
            "exception_is_value_error": isinstance(exc, ValueError),
            "detail": str(exc),
        }
    return {
        "outcome": "ACCEPTED",
        "categorical_relation": relation.categorical_relation.value,
    }


def _strict_authority(context: AuditContext) -> Any:
    passage_id = context.evidence_world.admitted_passages[0].passage_id
    receipt = measure_strict_comparison(context, passage_id)
    return complete_and_warrant(context, receipt, passage_id)


def _run_authority_mutation(case: dict[str, Any], kind: str) -> dict[str, Any]:
    if kind == "stale_authority_world":
        source = _context(case, bundle_id=str(case["source_bundle"]))
        target = _context(case, bundle_id=str(case["target_bundle"]))
        authority = _strict_authority(source)
        return _reject_observation(lambda: derive_relation(target, authority))

    if kind in {"rebound_stale_identities", "partial_rehash_stale_authority"}:
        source = _context(case, bundle_id=str(case["source_bundle"]))
        target = _context(case, bundle_id=str(case["target_bundle"]))
        authority = _strict_authority(source)
        atom = replace(
            authority.atom,
            audit_context_sha256=target.context_sha256,
            evidence_world_sha256=target.evidence_world.evidence_world_sha256,
        )
        if kind == "partial_rehash_stale_authority":
            atom = replace(atom, atom_id=stable_id("semantic-atom", _atom_material(atom)))
        rebound = replace(
            authority,
            audit_context_sha256=target.context_sha256,
            evidence_world_sha256=target.evidence_world.evidence_world_sha256,
            atom=atom,
        )
        return _reject_observation(lambda: derive_relation(target, rebound))

    context = _context(case)
    authority = _strict_authority(context)
    if kind == "rehashed_source_semantic_forgery":
        fields = authority.atom.field_map()
        fields["relation"] = str(case["forged_relation"])
        atom = replace(authority.atom, fields=tuple(sorted(fields.items())))
    elif kind == "rehashed_semantic_family_mutation":
        atom = replace(
            authority.atom,
            semantic_family=SemanticFamily(str(case["mutated_family"])),
        )
    else:
        raise AssertionError(f"unsupported authority mutation kind: {kind}")

    atom = replace(atom, atom_id=stable_id("semantic-atom", _atom_material(atom)))
    mutated = replace(authority, atom=atom)
    mutated = replace(
        mutated,
        authority_id=stable_id("semantic-authority", _authority_material(mutated)),
    )
    return _reject_observation(lambda: derive_relation(context, mutated))


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    kind = str(case["kind"])
    if kind == "audit":
        result = audit(_context(case))
        return {
            "outcome": "RETURNED",
            "conclusion": result.conclusion.value,
            "failure_code": _failure_value(result.failure_code),
            "trace_failure_codes": [
                _failure_value(trace.failure_code) for trace in result.traces
            ],
        }

    if kind == "projection":
        return _projection_observation(case)

    if kind == "same_id_proposition_substitution":
        context = _context(case)
        authority = _strict_authority(context)
        substituted = AuditContext(
            context.original_claim,
            TypedProposition.create(
                context.proposition.proposition_id,
                context.proposition.semantic_family,
                {
                    str(key): str(value)
                    for key, value in case["substituted_fields"].items()
                },
                text_sha256=context.proposition.text_sha256,
            ),
            context.evidence_world,
        )
        return _reject_observation(lambda: derive_relation(substituted, authority))

    if kind == "passage_substitution_stale_hash":
        text = str(case["passages"][0])
        source_id = f"{str(case['id']).lower()}-source"
        packet: dict[str, Any] = {
            "original_claim": str(case["proposition_text"]),
            "proposition": {
                "proposition_id": str(case["proposition_id"]),
                "text_sha256": _hex(str(case["proposition_text"])),
                "semantic_family": str(case["semantic_family"]),
                "fields": case["fields"],
            },
            "evidence_world": {
                "contract_b_version": "1.2.0",
                "bundle_id": "r10-stale-hash",
                "bundle_hash": _tagged("r10-stale-hash"),
                "aperture_observation": {
                    "search_scope": {"cohort": _COHORT["cohort_id"]},
                    "outcome": {"state": "unknown", "value": None},
                    "limitations": [],
                },
                "admitted_passages": [
                    {
                        "passage_id": "r10-p1",
                        "source_id": source_id,
                        "text": str(case["substituted_passage"]),
                        "text_sha256": _tagged(text),
                        "source_sha256": _tagged(source_id),
                    }
                ],
            },
        }
        try:
            context_from_packet(packet)
        except Exception as exc:
            return {
                "outcome": "REJECTED",
                "exception": type(exc).__name__,
                "exception_is_value_error": isinstance(exc, ValueError),
                "detail": str(exc),
            }
        return {"outcome": "ACCEPTED"}

    authority_kinds = {
        "stale_authority_world",
        "rebound_stale_identities",
        "partial_rehash_stale_authority",
        "rehashed_source_semantic_forgery",
        "rehashed_semantic_family_mutation",
    }
    if kind in authority_kinds:
        return _run_authority_mutation(case, kind)

    raise AssertionError(f"unknown qualification case kind: {kind}")


def _keys_recursive(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).casefold())
            keys.update(_keys_recursive(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_keys_recursive(child))
    return keys


def _compare(case_id: str, observed: dict[str, Any]) -> list[str]:
    expected = _GOLD["cases"][case_id]
    failures: list[str] = []
    if expected["expected"] == "REJECT":
        if observed.get("outcome") != "REJECTED":
            failures.append(f"expected rejection, observed {observed.get('outcome')}")
        if not observed.get("exception_is_value_error", False):
            failures.append("rejection was not a ValueError-compatible fail-closed surface")
        match = expected.get("match")
        if match is not None and str(match) not in str(observed.get("detail", "")):
            failures.append(f"rejection detail did not contain {match!r}")
        return failures

    for key in (
        "conclusion",
        "failure_code",
        "contract_c_version",
        "reported_verdict",
        "channels",
        "causal_form",
    ):
        if key in expected and observed.get(key) != expected[key]:
            failures.append(
                f"{key}: expected {expected[key]!r}, observed {observed.get(key)!r}"
            )
    trace_failure = expected.get("trace_failure_code")
    if trace_failure is not None and trace_failure not in observed.get(
        "trace_failure_codes", []
    ):
        failures.append(
            f"trace failure {trace_failure!r} absent from "
            f"{observed.get('trace_failure_codes')!r}"
        )
    forbidden = expected.get("forbidden_keys_recursive", [])
    if forbidden:
        present = _keys_recursive(observed.get("payload"))
        leaked = sorted(str(key) for key in forbidden if str(key).casefold() in present)
        if leaked:
            failures.append(f"forbidden scalar/winner keys present: {leaked!r}")
    return failures


def test_cal_v1_rc1_fresh_qualification_cohort() -> None:
    assert _COHORT["frozen_candidate_sha"] == _FROZEN_SHA
    assert _GOLD["frozen_candidate_sha"] == _FROZEN_SHA
    assert _COHORT["cohort_id"] == _GOLD["cohort_id"]
    assert len(_COHORT["cases"]) == 19

    observations: dict[str, Any] = {}
    failures: dict[str, list[str]] = {}
    for case in _COHORT["cases"]:
        case_id = str(case["id"])
        observed = _run_case(case)
        observations[case_id] = observed
        case_failures = _compare(case_id, observed)
        if case_failures:
            failures[case_id] = case_failures

    summary = {
        "schema": "cal-v1-rc1-fresh-qualification-observation-v1",
        "cohort_id": _COHORT["cohort_id"],
        "frozen_candidate_sha": _FROZEN_SHA,
        "case_count": len(_COHORT["cases"]),
        "failure_count": len(failures),
        "observations": observations,
        "failures": failures,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    assert not failures, json.dumps(failures, sort_keys=True)
