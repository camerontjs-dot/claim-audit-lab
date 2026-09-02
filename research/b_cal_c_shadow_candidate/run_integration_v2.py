"""Successor integration runner after the preserved v1 boundary failure.

The v1 runner assumed released Contract-C export was available as a structural
base. Fresh valid Contract-B 1.2.0 disproved that assumption: released CAL can
return an unclassified/not-checkable assessment with retained candidates that
its Contract-C exporter intentionally refuses to attribute.

This successor preserves that released exporter failure as evidence and builds
the shadow Contract-C object directly from released CAL observations that do
not require terminal causal attribution: proposition identity, retained
contributions, and the released scalar measurement. It then removes all causal
strength and reports the candidate as not_checkable because semantic warrant is
unresolved.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from claim_audit_lab.auditor import audit_claims
from claim_audit_lab.contracts import contract_c as released_c
from claim_audit_lab.contracts.adapter import adapt_bundle_to_pipeline, build_claim_evidence_scopes
from claim_audit_lab.contracts.factual_context import load_contract_b_intake

from run_integration import (
    B_AUTHORITY_SHA,
    CAL_EXPORTER_LINEAGE,
    CAL_PRODUCTION_BASE,
    C_AUTHORITY_SHA,
    EB_PRODUCTION_PIN,
    _assert_dep_identity,
    _build_corpus,
    _contract_b_index,
    _load_instruments,
    _load_module,
    _microfixtures,
    _passage_map,
    _selection,
    _validate_c,
)
from shadow_candidate import (
    INSTRUMENT_EVIDENCE,
    _shadow_policy,
    candidate_internal_record,
    canonical_bytes,
    measure_text,
    result_set_identity,
    sha256_hex,
)


def _candidate_contract_c(
    *,
    intake: Any,
    assessments: list[Any],
    evidence_bundle: Any,
    audit_config: Any,
    candidate_sha: str,
    internal: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    policy = _shadow_policy()
    propositions: list[dict[str, Any]] = []
    for assessment in assessments:
        claim_id = assessment.claim.id
        if claim_id not in internal:
            raise AssertionError(f"missing candidate internal record for {claim_id}")

        # These helpers are part of the exact released exporter lineage pinned by
        # this experiment. We reuse only observation construction. We do not call
        # its terminal attribution machinery after it has already failed closed.
        rows = released_c._contribution_rows(assessment, intake.bundle)
        measurement = released_c._measurement(
            assessment,
            released_c._measurement_basis(rows),
        )
        contribution_ids = sorted(row["contribution_id"] for row in rows)
        propositions.append(
            {
                "proposition": {
                    "proposition_id": claim_id,
                    "text_sha256": released_c._sha256(assessment.claim.text.encode("utf-8")),
                },
                "execution": {"state": "completed", "completion": "not_checkable"},
                "assessments": {
                    "eligibility": {"state": "not_performed"},
                    "semantic_validity": {"state": "performed", "value": "unknown"},
                    "aperture_completeness": {"state": "not_performed"},
                    "temporal_applicability": {"state": "not_performed"},
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
                    "reported_verdict": "not_checkable",
                    "terminal_branch": "shadow_authority_unresolved",
                    "causal_form": "redundant_non_deciding",
                    "basis_members": [],
                    "residual_contribution_ids": contribution_ids,
                    "rule_roles": [],
                },
            }
        )

    result: dict[str, Any] = {
        "contract_c_version": "1.0.0",
        "input": {
            "contract_b": {
                "contract_version": intake.bundle.manifest.schema_version,
                "bundle_id": intake.bundle.manifest.bundle_id,
                "bundle_hash": intake.bundle.manifest.bundle.bundle_hash,
            }
        },
        "producer": {
            "semantic_implementation_sha": candidate_sha,
            "policy": {
                "sha256": sha256_hex(canonical_bytes(policy)),
                "canonical": policy,
            },
        },
        "execution": {"state": "completed"},
        "propositions": propositions,
    }
    if not propositions:
        raise AssertionError("candidate completed result set requires propositions")
    result["result_set_id"] = result_set_identity(result)
    return result


def _internal_records(intake: Any, assessments: list[Any], instruments: list[Any]) -> dict[str, Any]:
    passages = _passage_map(intake)
    records: dict[str, Any] = {}
    for assessment in assessments:
        claim_id = assessment.claim.id
        selected, excluded, basis, aperture = _selection(intake, claim_id)
        observations: list[dict[str, Any]] = []
        for passage_id in selected:
            passage = passages[passage_id]
            observations.extend(
                measure_text(
                    passage.passage_text,
                    instruments,
                    passage_id=passage_id,
                )
            )
        records[claim_id] = candidate_internal_record(
            claim_id=claim_id,
            selection_basis=basis,
            observations=observations,
            excluded_passage_ids=excluded,
            aperture_observation=aperture,
        )
    return records


def _legacy_snapshot(assessments: list[Any]) -> list[dict[str, Any]]:
    return [assessment.model_dump(mode="json") for assessment in assessments]


def _run_case(
    *,
    name: str,
    bundle_dir: Path,
    instruments: list[Any],
    c_validator: Any,
    candidate_sha: str,
    out: Path,
) -> dict[str, Any]:
    intake = load_contract_b_intake(bundle_dir)
    claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(intake.bundle)
    scopes = build_claim_evidence_scopes(intake.bundle)
    assessments = audit_claims(claims, evidence_bundle, audit_config, evidence_scopes=scopes)
    index = _contract_b_index(intake)

    case_out = out / name
    case_out.mkdir(parents=True, exist_ok=True)
    legacy_snapshot = _legacy_snapshot(assessments)
    (case_out / "legacy-assessments.json").write_bytes(canonical_bytes(legacy_snapshot))

    legacy_export: dict[str, Any]
    legacy_c_object: dict[str, Any] | None = None
    try:
        legacy_raw = released_c.export_contract_c_bytes(
            contents=intake.bundle,
            assessments=assessments,
            evidence_bundle=evidence_bundle,
            audit_config=audit_config,
        )
    except released_c.ContractCExportError as exc:
        legacy_export = {
            "state": "failed_closed",
            "error_type": type(exc).__name__,
            "message": str(exc),
        }
        (case_out / "legacy-contract-c-export-failure.json").write_bytes(
            canonical_bytes(legacy_export)
        )
    else:
        errors = _validate_c(c_validator, legacy_raw, index)
        if errors:
            raise AssertionError(
                f"released Contract-C artifact failed frozen C validation: {errors}"
            )
        legacy_c_object = json.loads(legacy_raw)
        legacy_export = {
            "state": "emitted",
            "frozen_validator": "PASS",
            "sha256": sha256_hex(legacy_raw),
        }
        (case_out / "legacy-contract-c.json").write_bytes(legacy_raw)

    internal = _internal_records(intake, assessments, instruments)
    (case_out / "candidate-internal.json").write_bytes(canonical_bytes(internal))
    shadow = _candidate_contract_c(
        intake=intake,
        assessments=assessments,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
        candidate_sha=candidate_sha,
        internal=internal,
    )
    shadow_raw = canonical_bytes(shadow)
    shadow_errors = _validate_c(c_validator, shadow_raw, index)
    if shadow_errors:
        raise AssertionError(f"shadow Contract-C output failed frozen C validation: {shadow_errors}")
    shadow_again = _candidate_contract_c(
        intake=intake,
        assessments=assessments,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
        candidate_sha=candidate_sha,
        internal=internal,
    )
    if shadow_raw != canonical_bytes(shadow_again):
        raise AssertionError("shadow Contract-C projection is not byte deterministic")
    (case_out / "shadow-contract-c.json").write_bytes(shadow_raw)
    (case_out / "contract-b-index.json").write_bytes(canonical_bytes(index))

    divergences: list[dict[str, Any]] = []
    if legacy_c_object is None:
        divergences.append(
            {
                "scope": "contract_c_export",
                "primary_class": "likely legacy compression",
                "legacy": legacy_export,
                "shadow": "valid Contract C 1.0.0 emitted without causal strengthening",
            }
        )
    for assessment in assessments:
        if assessment.support_label != "not_checkable":
            divergences.append(
                {
                    "scope": "proposition_terminal_verdict",
                    "claim_id": assessment.claim.id,
                    "primary_class": "authority unresolved",
                    "legacy_verdict": assessment.support_label,
                    "shadow_verdict": "not_checkable",
                }
            )
    (case_out / "differential.json").write_bytes(canonical_bytes(divergences))

    measurement_statuses: Counter[str] = Counter()
    authority_states: Counter[str] = Counter()
    proposal_count = 0
    selected_count = 0
    excluded_count = 0
    for record in internal.values():
        proposal_count += record["proposal_count"]
        selected_count += len({row["passage_id"] for row in record["semantic_measurements"]})
        excluded_count += len(record["excluded_passage_ids"])
        for obs in record["semantic_measurements"]:
            measurement = obs.get("measurement")
            measurement_statuses[(measurement or {}).get("status", "EXECUTION_FAILURE")] += 1
            authority_states[obs["authority"]["state"]] += 1

    legacy_verdicts = Counter(assessment.support_label for assessment in assessments)
    return {
        "case": name,
        "contract_b": {
            "version": intake.bundle.manifest.schema_version,
            "bundle_id": intake.bundle.manifest.bundle_id,
            "bundle_hash": intake.bundle.manifest.bundle.bundle_hash,
            "extension_state": intake.extension_state,
            "frozen_validator": "PASS",
            "cal_production_intake": "PASS",
        },
        "released_cal": {
            "assessment_count": len(assessments),
            "verdict_counts": dict(sorted(legacy_verdicts.items())),
            "contract_c_export": legacy_export,
        },
        "candidate": {
            "selected_passage_count": selected_count,
            "excluded_passage_count": excluded_count,
            "proposal_count": proposal_count,
            "measurement_status_counts": dict(sorted(measurement_statuses.items())),
            "authority_state_counts": dict(sorted(authority_states.items())),
            "all_measurements_non_authoritative": all(
                not obs["authority"]["may_strengthen_conclusion"]
                for record in internal.values()
                for obs in record["semantic_measurements"]
            ),
        },
        "shadow_contract_c": {
            "frozen_validator": "PASS",
            "sha256": sha256_hex(shadow_raw),
            "result_set_id": shadow["result_set_id"],
            "byte_deterministic": True,
            "verdict_counts": {"not_checkable": len(assessments)},
        },
        "divergences": divergences,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--deps", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--candidate-sha", required=True)
    args = parser.parse_args()

    deps = args.deps.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    _assert_dep_identity(deps / "apparatus-b", B_AUTHORITY_SHA)
    _assert_dep_identity(deps / "apparatus-c", C_AUTHORITY_SHA)
    _assert_dep_identity(deps / "evidence-bundler", EB_PRODUCTION_PIN)
    _assert_dep_identity(deps / "rc7fb1", INSTRUMENT_EVIDENCE["comparison"]["commit"])
    _assert_dep_identity(deps / "rc7fc", INSTRUMENT_EVIDENCE["event_ordering"]["commit"])
    _assert_dep_identity(deps / "rc7fd", INSTRUMENT_EVIDENCE["permission_composition"]["commit"])

    c_validator = _load_module(
        deps / "apparatus-c" / "validators" / "contract_c.py",
        "frozen_contract_c_validator_v2",
    )
    corpus = _build_corpus(
        eb_root=deps / "evidence-bundler",
        apparatus_b=deps / "apparatus-b",
        out=out / "corpus",
    )
    instruments = _load_instruments(deps)
    cases = [
        _run_case(
            name=name,
            bundle_dir=path,
            instruments=instruments,
            c_validator=c_validator,
            candidate_sha=args.candidate_sha,
            out=out / "cases",
        )
        for name, path in sorted(corpus.items())
    ]

    micro = _microfixtures(instruments)
    (out / "measurement-microfixtures.json").write_bytes(canonical_bytes(micro))

    receipt = {
        "identities": {
            "apparatus_b": B_AUTHORITY_SHA,
            "apparatus_c": C_AUTHORITY_SHA,
            "evidence_bundler": EB_PRODUCTION_PIN,
            "cal_production_base": CAL_PRODUCTION_BASE,
            "cal_exporter_lineage": CAL_EXPORTER_LINEAGE,
            "candidate_sha": args.candidate_sha,
            "instruments": {
                family: row["commit"] for family, row in INSTRUMENT_EVIDENCE.items()
            },
        },
        "preserved_predecessor_failure": {
            "runner": "run_integration.py",
            "finding": (
                "fresh valid B 1.2.0 produced released unclassified/not_checkable state with "
                "retained candidates that released Contract-C exporter refuses to attribute"
            ),
            "repair_scope": (
                "no production repair; successor preserves exporter failure and projects "
                "noncausal shadow C directly from released observation helpers"
            ),
        },
        "cases": cases,
        "measurement_microfixtures": {
            "path": "measurement-microfixtures.json",
            "not_contract_b_corpus": True,
        },
        "projection_losses": [
            {
                "distinction": (
                    "bounded structured measurement proposals and per-instrument authority states"
                ),
                "contract_c_representation": (
                    "semantic_validity=performed/unknown plus completed not_checkable"
                ),
                "loss": True,
                "legitimate_collapse_for_this_run": True,
                "downstream_relevant_difference_demonstrated": False,
                "consequence": (
                    "keep proposal/authority detail internal; no Contract-C successor escalation"
                ),
            },
            {
                "distinction": (
                    "Contract-B review history and aperture observation used for measurement selection"
                ),
                "contract_c_representation": "not duplicated; exact Contract-B object is identity-bound",
                "loss": False,
                "legitimate_collapse_for_this_run": True,
                "downstream_relevant_difference_demonstrated": False,
                "consequence": (
                    "do not turn upstream aperture observation into CAL completeness assessment"
                ),
            },
        ],
        "coverage": {
            "real_contract_b_cases": ["fresh-b12-absent", "fresh-b12-present"],
            "represented": [
                "valid Contract-B 1.2.0 intake",
                "optional factual-context absent",
                "promoted semantic-context admission",
                "rejected/excluded passage",
                "aperture outcome explicitly unknown",
                "released CAL assessment behavior",
                "released Contract-C export failure where encountered",
                "candidate insufficient semantic authority",
                "valid Contract-C not_checkable projection",
            ],
            "not_claimed_from_real_b_corpus": [
                "semantic support/refutation truth label",
                "semantic neutral truth label",
                "aperture completeness conclusion",
                "source-established semantic unknown",
                "authorized extraction",
                "authorized typed population mapping",
                "authorized numeric assertion/scope mapping",
                "authorized multi-passage composition",
            ],
            "controlled_internal_only": [
                "comparison measurement proposal",
                "explicit event-ordering measurement proposal",
                "permission/exception/temporal measurement proposal",
                "operator inapplicability or measurement-unresolved state",
            ],
        },
        "authority_interface": {
            "required_states": [
                "established",
                "semantic_unknown",
                "extraction_unresolved",
                "insufficient_authority",
            ],
            "required_binding": [
                "claim/proposition identity",
                "evidence passage identity",
                "semantic family and normalized proposal identity",
                "authority source/issuer identity",
                "jurisdiction/applicability result",
            ],
            "established_receipt_verification_in_this_track": False,
            "default_when_missing": "insufficient_authority",
        },
        "terminal_disposition": (
            "SHADOW_BOUNDARY_OPERABLE_FAIL_CLOSED; AUTHORITY_MACHINERY_BLOCKS_STRONGER_CONCLUSION"
        ),
        "production_promotion": "NO",
    }
    (out / "RUN-RECEIPT.json").write_bytes(canonical_bytes(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
