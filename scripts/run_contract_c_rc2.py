#!/usr/bin/env python3
"""Execute the preregistered Contract-C RC2-A producer experiment."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import yaml

from claim_audit_lab import __version__
from claim_audit_lab.auditor import audit_claims, build_audit_report
from claim_audit_lab.contracts.adapter import adapt_bundle_to_pipeline, build_claim_evidence_scopes
from claim_audit_lab.contracts.bundle_loader import BundleIntegrityError
from claim_audit_lab.contracts.factual_context import (
    FactualContextIntakeError,
    load_contract_b_intake,
)
from claim_audit_lab.contracts.output_writer import write_audited_bundle
from claim_audit_lab.models import ClaimAssessment
from claim_audit_lab.policy import CAL_RULES_V1_2_0
from claim_audit_lab.report import render_markdown_report
from contract_c_rc2_research.experiment import (
    ablation_matrix,
    candidate_diagnostics,
    canonical_bytes,
    count_structural_fields,
    field_justification_registry,
    producer_gate,
    project_real_boundary,
    render_derived_report,
    repeated_scalar_count,
    semantic_firewall_receipts,
    sha256_bytes,
    sha256_text,
    stable_id,
    validate_candidate,
)
from evidence_bundler.contracts.writer import build_retrieval_bundle

AUDIT_RUN_ID = "contract-c-rc2-a-real-boundary-001"
AUDITED_AT_UTC = "2026-08-28T02:30:00Z"


def _file_manifest(root: Path) -> tuple[list[dict[str, Any]], str]:
    rows: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        raw = path.read_bytes()
        file_sha = hashlib.sha256(raw).hexdigest()
        rows.append({"path": rel, "size": len(raw), "sha256": f"sha256:{file_sha}"})
        rel_bytes = rel.encode("utf-8")
        digest.update(len(rel_bytes).to_bytes(8, "big"))
        digest.update(rel_bytes)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
    return rows, "sha256:" + digest.hexdigest()


def _mutate_excluded_telemetry(assessments: list[ClaimAssessment]) -> list[ClaimAssessment]:
    mutated: list[ClaimAssessment] = []
    for assessment in assessments:
        raw = assessment.model_dump(mode="json")
        raw["explanation"] = "presentation prose changed by telemetry invariance control"
        raw["rewrite_guidance"] = ["presentation-only mutation"]
        raw["risk_label"] = "low" if raw["risk_label"] != "low" else "high"
        for candidate in raw.get("candidate_evidence", []):
            candidate["score"] = 0.123456789
            candidate["rationale"] = "debug rationale mutated"
            candidate["source_reliability"] = "unknown"
        for candidate in raw.get("counterevidence", []):
            candidate["score"] = 0.987654321
            candidate["rationale"] = "counter debug rationale mutated"
            candidate["source_reliability"] = "unknown"
        mutated.append(ClaimAssessment.model_validate(raw))
    return mutated


def _subset_candidate(candidate: dict[str, Any], count: int) -> dict[str, Any]:
    body = copy.deepcopy(candidate)
    body.pop("result_set_id", None)
    body["propositions"] = body["propositions"][:count]
    result = copy.deepcopy(body)
    result["result_set_id"] = stable_id("result-set", body)
    return result


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def _boundary_source_inventory(contents: Any) -> dict[str, Any]:
    claims = [
        {
            "proposition_id": claim.claim_id,
            "text_sha256": sha256_text(claim.claim_text),
            "claim_type": claim.claim_type,
        }
        for claim in contents.claims
        if claim.claim_type == "extracted_claim"
    ]
    sources = []
    passages = []
    for source_id, profile in sorted(contents.source_profiles.items()):
        sources.append(
            {
                "source_id": source_id,
                "content_sha256": profile.content_hash,
            }
        )
        for passage in contents.passages.get(source_id, []):
            passages.append(
                {
                    "source_id": source_id,
                    "passage_id": passage.passage_id,
                    "passage_sha256": passage.passage_hash,
                }
            )
    return {"propositions": claims, "sources": sources, "passages": passages}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eb-root", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cal-production-sha", required=True)
    parser.add_argument("--eb-production-sha", required=True)
    parser.add_argument("--apparatus-production-sha", required=True)
    parser.add_argument("--rc1-cal-sha", required=True)
    parser.add_argument("--rc1-apparatus-sha", required=True)
    args = parser.parse_args()

    out = args.out.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    b_dir = out / "real-contract-b-1.2.0"
    retrieval_report = out / "eb-retrieval-report.md"
    build_result = build_retrieval_bundle(
        args.fixture.resolve(),
        b_dir,
        report_out=retrieval_report,
    )

    # Real fail-closed CAL 1.2 intake, including extension-state observation.
    intake = load_contract_b_intake(b_dir, deviations_dir=out / "intake-deviations")
    contents = intake.bundle

    contract_version = (b_dir / "CONTRACT_VERSION").read_text(encoding="utf-8").strip()
    if contract_version != "1.2.0":
        raise AssertionError(f"expected real Contract B 1.2.0, got {contract_version!r}")
    if build_result.manifest.bundle_id != contents.manifest.bundle_id:
        raise AssertionError("validated CAL manifest identity differs from EB producer result")

    files, artifact_sha256 = _file_manifest(b_dir)
    binding = {
        "contract_version": contract_version,
        "bundle_id": contents.manifest.bundle_id,
        "bundle_hash": contents.manifest.bundle.bundle_hash,
        "artifact_sha256": artifact_sha256,
        "sha256sums_sha256": sha256_bytes((b_dir / "SHA256SUMS").read_bytes()),
    }

    raw_audit_config = yaml.safe_load((b_dir / "audit_config.yaml").read_text(encoding="utf-8"))
    if not isinstance(raw_audit_config, dict):
        raise AssertionError("audit_config.yaml did not parse as a mapping")
    raw_has_pipeline = "pipeline" in raw_audit_config
    selection_origin = (
        "contract_b_bytes"
        if raw_has_pipeline
        else "cal_compatibility_default_not_present_in_contract_b_bytes"
    )

    # Execute the current production Contract-B audit path with the exact loaded
    # bundle. This mirrors cli._audit_bundle_v0_2 without altering semantics.
    cal_claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(contents)
    assessments = audit_claims(
        cal_claims,
        evidence_bundle,
        audit_config,
        evidence_scopes=build_claim_evidence_scopes(contents),
    )
    assessments_by_id = {assessment.claim.id: assessment for assessment in assessments}
    report = build_audit_report(contents.manifest.bundle_id, assessments, evidence_bundle)
    report_markdown = render_markdown_report(report)

    audited_bundle_dir = out / "compatibility-writeback"
    write_audited_bundle(
        b_dir,
        audited_bundle_dir,
        contents.claims,
        assessments_by_id,
        audit_run_id=AUDIT_RUN_ID,
        audited_at_utc=AUDITED_AT_UTC,
        audit_config=contents.audit_config,
    )
    writeback_files, writeback_artifact_sha256 = _file_manifest(audited_bundle_dir)

    candidate = project_real_boundary(
        contents=contents,
        assessments=assessments,
        contract_b_binding=binding,
        cal_code_sha=args.cal_production_sha,
        cal_library_version=__version__,
        engine_id=contents.audit_config.pipeline,
        engine_selection_origin=selection_origin,
        cal_policy_id=CAL_RULES_V1_2_0.config_id,
        audit_run_id=AUDIT_RUN_ID,
        factual_context_state=intake.extension_state,
    )
    candidate_errors = validate_candidate(candidate)
    if candidate_errors:
        raise AssertionError("RC2 candidate structural validation failed: " + "; ".join(candidate_errors))

    # Telemetry/presentation invariance: mutate fields deliberately omitted from
    # RC2 while holding stable aggregate measurement and semantic conclusion fixed.
    telemetry_mutated = _mutate_excluded_telemetry(assessments)
    telemetry_candidate = project_real_boundary(
        contents=contents,
        assessments=telemetry_mutated,
        contract_b_binding=binding,
        cal_code_sha=args.cal_production_sha,
        cal_library_version=__version__,
        engine_id=contents.audit_config.pipeline,
        engine_selection_origin=selection_origin,
        cal_policy_id=CAL_RULES_V1_2_0.config_id,
        audit_run_id=AUDIT_RUN_ID,
        factual_context_state=intake.extension_state,
    )
    telemetry_invariant = canonical_bytes(telemetry_candidate) == canonical_bytes(candidate)
    if not telemetry_invariant:
        raise AssertionError("excluded telemetry mutation changed RC2 candidate bytes")

    # Integrity negative control. A byte mutation must fail before projection.
    tampered = out / "tampered-contract-b-control"
    shutil.copytree(b_dir, tampered)
    first_claim = sorted((tampered / "claims").glob("*.yaml"))[0]
    first_claim.write_text(first_claim.read_text(encoding="utf-8") + "\n# rc2 integrity control\n", encoding="utf-8")
    integrity_detected = False
    integrity_error = ""
    try:
        load_contract_b_intake(tampered, deviations_dir=out / "tamper-deviations")
    except (BundleIntegrityError, FactualContextIntakeError) as exc:
        integrity_detected = True
        integrity_error = str(exc)
    if not integrity_detected:
        raise AssertionError("tampered Contract-B bytes were accepted")

    firewall = semantic_firewall_receipts(candidate)
    if not firewall["identical"]:
        raise AssertionError("downstream authority/forecast context mutated Contract C")

    derived_report = render_derived_report(candidate)
    derived_report_2 = render_derived_report(candidate)
    if derived_report != derived_report_2:
        raise AssertionError("derived report is not deterministic")

    gate, gate_blockers = producer_gate(candidate)

    real_c0 = {
        "validated_input_boundary": {
            "contract_b_binding": binding,
            "contract_b_inventory": _boundary_source_inventory(contents),
            "audit_config": contents.audit_config.model_dump(mode="json"),
            "factual_context_state": intake.extension_state,
        },
        "production_assessments": [item.model_dump(mode="json") for item in assessments],
        "structured_audit_report": report.model_dump(mode="json"),
    }

    subsets = [_subset_candidate(candidate, n) for n in range(1, len(candidate["propositions"]) + 1)]
    subset_bytes = [len(canonical_bytes(item)) for item in subsets]
    empty_body = copy.deepcopy(candidate)
    empty_body.pop("result_set_id", None)
    empty_body["propositions"] = []
    empty_envelope = copy.deepcopy(empty_body)
    empty_envelope["result_set_id"] = stable_id("result-set", empty_body)
    run_level_overhead = len(canonical_bytes(empty_envelope))
    marginal = [subset_bytes[0] - run_level_overhead]
    marginal.extend(subset_bytes[index] - subset_bytes[index - 1] for index in range(1, len(subset_bytes)))

    compression = {
        "rc1_frozen_controls": {
            "source_cal_rc1_sha": args.rc1_cal_sha,
            "c0_vs_c1_canonical_bytes": {
                "c0-no-entail.json": {"c0": 902, "rc1_c1": 1730},
                "c0-inf-02-contradicted-logging.json": {"c0": 1713, "rc1_c1": 1930},
                "c0-inf-03-numeric-uptime.json": {"c0": 1582, "rc1_c1": 1729},
            },
            "note": "reused frozen RC1 diagnostic measurements; semantic falsifiers are rerun separately without changing RC1",
        },
        "real_production_boundary_c0": {
            "canonical_bytes": len(canonical_bytes(real_c0)),
            "structural_fields": count_structural_fields(real_c0),
            "repeated_scalar_values": repeated_scalar_count(real_c0),
        },
        "rc2_candidate": candidate_diagnostics(candidate),
        "multi_proposition_scaling": {
            "proposition_count": len(candidate["propositions"]),
            "run_level_overhead_bytes": run_level_overhead,
            "subset_canonical_bytes": subset_bytes,
            "marginal_proposition_bytes": marginal,
        },
        "interpretation_rule": "byte counts are diagnostics only; semantic obligations govern minimality",
    }

    obligation_availability = [
        {"obligation": "exact Contract-B input binding", "available": True, "source": "validated manifest + exact frozen bytes"},
        {"obligation": "proposition identity/text hash", "available": True, "source": "validated CBClaim + deterministic hash"},
        {"obligation": "retained evidence/counterevidence references", "available": True, "source": "ClaimAssessment candidate lists mapped to validated CB passages"},
        {"obligation": "stable aggregate measurement outcome", "available": True, "source": "ClaimAssessment.support_signal"},
        {"obligation": "headline epistemic conclusion", "available": True, "source": "ClaimAssessment.support_label"},
        {"obligation": "exact deciding contribution basis receipt", "available": False, "source": "not exposed by production ClaimAssessment"},
        {"obligation": "typed eligibility assessment state", "available": False, "source": "not exposed by production ClaimAssessment"},
        {"obligation": "typed semantic-validity assessment state", "available": False, "source": "not exposed by production ClaimAssessment"},
        {"obligation": "typed aperture/completeness assessment state", "available": False, "source": "not exposed by production ClaimAssessment"},
        {"obligation": "typed temporal/applicability assessment state", "available": False, "source": "not exposed by production ClaimAssessment"},
        {"obligation": "typed citation assessment state", "available": False, "source": "not exposed by production ClaimAssessment"},
        {"obligation": "execution state", "available": True, "source": "research wrapper around completed production call"},
        {"obligation": "reassessment/supersession lineage", "available": False, "source": "no immutable result lineage object at production boundary"},
    ]

    capture = {
        "pins": {
            "cal_production_sha": args.cal_production_sha,
            "evidence_bundler_production_sha": args.eb_production_sha,
            "apparatus_production_sha": args.apparatus_production_sha,
            "cal_rc1_sha": args.rc1_cal_sha,
            "apparatus_rc1_sha": args.rc1_apparatus_sha,
        },
        "pre_audit_boundary": {
            "contract_b_binding": binding,
            "contract_b_files": files,
            "identity_inventory": _boundary_source_inventory(contents),
            "factual_context_state": intake.extension_state,
            "raw_contract_b_audit_config_has_pipeline": raw_has_pipeline,
            "loaded_cal_pipeline": contents.audit_config.pipeline,
            "pipeline_selection_origin": selection_origin,
            "contract_b_audit_config": contents.audit_config.model_dump(mode="json"),
        },
        "post_audit_boundary": {
            "claim_assessments": [item.model_dump(mode="json") for item in assessments],
            "structured_report": report.model_dump(mode="json"),
            "production_audit_trace": {
                "state": "not_produced_on_selected_contract_b_production_path",
                "engine": contents.audit_config.pipeline,
            },
            "compatibility_writeback": {
                "artifact_sha256": writeback_artifact_sha256,
                "files": writeback_files,
            },
        },
    }

    summary = {
        "producer_gate": gate,
        "gate_blockers": gate_blockers,
        "claim_under_review": "real current-production CAL boundary is sufficient for a frozen semantically justified Contract-C RC2 candidate",
        "real_contract_b_binding": binding,
        "real_proposition_count": len(candidate["propositions"]),
        "engine_observation": {
            "contract_b_bytes_have_pipeline": raw_has_pipeline,
            "cal_loaded_pipeline": contents.audit_config.pipeline,
            "selection_origin": selection_origin,
        },
        "telemetry_invariance": telemetry_invariant,
        "integrity_negative_control": integrity_detected,
        "semantic_firewalls": firewall["identical"],
        "derived_report_sha256": sha256_bytes(derived_report.encode("utf-8")),
        "candidate_sha256": sha256_bytes(canonical_bytes(candidate)),
        "candidate_result_set_id": candidate["result_set_id"],
        "obligation_availability": obligation_availability,
        "non_claims": [
            "not an overall Contract-C disposition",
            "not production promotion evidence",
            "not an independent-consumer result",
            "not a Contract-C version assignment",
        ],
    }

    _write_json(out / "frozen-contract-b-hashes.json", {"binding": binding, "files": files})
    _write_json(out / "real-producer-boundary-capture.json", capture)
    _write_json(out / "contract-c-rc2-candidate.json", candidate)
    _write_json(out / "field-justification-registry.json", field_justification_registry())
    _write_json(out / "field-ablation-matrix.json", ablation_matrix(candidate))
    _write_json(out / "semantic-firewall.json", firewall)
    _write_json(
        out / "telemetry-invariance.json",
        {
            "invariant": telemetry_invariant,
            "mutated_full_boundary_fields": [
                "candidate_evidence.score",
                "candidate_evidence.rationale",
                "candidate_evidence.source_reliability",
                "counterevidence.score",
                "counterevidence.rationale",
                "counterevidence.source_reliability",
                "risk_label",
                "explanation",
                "rewrite_guidance",
            ],
            "candidate_sha256": sha256_bytes(canonical_bytes(candidate)),
        },
    )
    _write_json(
        out / "integrity-negative-control.json",
        {"tamper_detected": integrity_detected, "error": integrity_error},
    )
    _write_json(out / "compression-diagnostics.json", compression)
    _write_json(out / "obligation-availability.json", obligation_availability)
    _write_json(out / "summary.json", summary)
    (out / "production-audit-report.md").write_text(report_markdown, encoding="utf-8")
    (out / "derived-rc2-report.md").write_text(derived_report, encoding="utf-8")

    print("RC2_SUMMARY_JSON=" + json.dumps(summary, sort_keys=True, separators=(",", ":")))
    print("RC2_CANDIDATE_JSON=" + json.dumps(candidate, sort_keys=True, separators=(",", ":")))
    print("RC2_COMPRESSION_JSON=" + json.dumps(compression, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
