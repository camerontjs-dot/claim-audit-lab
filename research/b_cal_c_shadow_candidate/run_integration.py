"""Execute the frozen Contract-B 1.2.0 -> CAL shadow -> Contract-C 1.0.0 run.

The runner deliberately generates the Contract-B corpus through the same
Evidence Bundler production path used by the Contract-B promotion gate. It
executes released CAL unchanged, then executes research measurements as
non-authoritative observations and validates the conservative shadow projection
against the frozen Contract-C validator.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml

from claim_audit_lab.auditor import audit_claims
from claim_audit_lab.contracts.adapter import adapt_bundle_to_pipeline, build_claim_evidence_scopes
from claim_audit_lab.contracts.contract_c import export_contract_c_bytes
from claim_audit_lab.contracts.factual_context import load_contract_b_intake

from shadow_candidate import (
    INSTRUMENT_EVIDENCE,
    MeasurementInstrument,
    candidate_internal_record,
    canonical_bytes,
    classify_legacy_shadow_divergence,
    measure_text,
    project_shadow_contract_c,
    sha256_hex,
)

B_AUTHORITY_SHA = "c314e53bd91c0736aa4370a364673b069aceb43e"
C_AUTHORITY_SHA = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
EB_PRODUCTION_PIN = "c8189c31adbab11729c31430c2070126224a2d42"
CAL_PRODUCTION_BASE = "53f0885b111676794d1bd20e10b91aa58b07e9d4"
CAL_EXPORTER_LINEAGE = "a069707e5031cef5b82af02d08b0f1a47ea8752e"


def _yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected mapping in {path}")
    return value


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def _assert_dep_identity(path: Path, expected: str) -> None:
    actual = _git_head(path)
    if actual != expected:
        raise AssertionError(f"dependency identity mismatch at {path}: {actual} != {expected}")


def _verify_contract_b(apparatus_b: Path, bundle_dir: Path) -> None:
    env = os.environ.copy()
    prior = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(apparatus_b) if not prior else f"{apparatus_b}{os.pathsep}{prior}"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "validators.verify_contract_integrity",
            str(bundle_dir),
            "--against-pin",
            "1.2.0",
        ],
        cwd=apparatus_b,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(
            "frozen Contract-B validator rejected corpus:\n" + proc.stdout + "\n" + proc.stderr
        )


def _bundle_ids(bundle_dir: Path) -> tuple[list[str], dict[str, str], dict[str, dict[str, Any]]]:
    claim_ids: list[str] = []
    claim_docs: dict[str, dict[str, Any]] = {}
    for path in sorted((bundle_dir / "claims").glob("*.yaml")):
        row = _yaml(path)
        claim_id = str(row["claim_id"])
        claim_ids.append(claim_id)
        claim_docs[claim_id] = row
    passage_source: dict[str, str] = {}
    for path in sorted((bundle_dir / "evidence").glob("*/passages/*.yaml")):
        row = _yaml(path)
        passage_source[str(row["passage_id"])] = str(row["source_id"])
    return claim_ids, passage_source, claim_docs


def _claim_nominees(claim_doc: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for field in ("evidence_passages", "counterevidence_passages"):
        rows = claim_doc.get(field, [])
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict) and isinstance(row.get("passage_id"), str):
                    values.append(row["passage_id"])
    return list(dict.fromkeys(values))


def _production_acceptance_extension(bundle_dir: Path) -> dict[str, Any]:
    claim_ids, passage_source, claim_docs = _bundle_ids(bundle_dir)
    if not claim_ids:
        raise AssertionError("fresh production Contract-B bundle has no claims")
    claim_id = claim_ids[0]
    nominees = _claim_nominees(claim_docs[claim_id])
    all_passages = list(passage_source)
    if len(nominees) < 2:
        nominees.extend(pid for pid in all_passages if pid not in nominees)
    nominees = list(dict.fromkeys(nominees))
    if len(nominees) < 2:
        raise AssertionError("need two canonical passages for accepted/rejected control")
    accepted_passage, rejected_passage = nominees[:2]
    accepted_source = passage_source[accepted_passage]
    return {
        "schema": "contract-b-factual-context-v1",
        "history_complete": True,
        "claims": [
            {
                "claim_id": claim_id,
                "origin": {"state": "known", "value": {"surface": "fresh-production-bundle"}},
                "atomicity": {"state": "unknown", "value": None},
            }
        ],
        "sources": [
            {
                "source_id": accepted_source,
                "context_facts": [
                    {
                        "fact_id": "fact-effective-date-001",
                        "predicate": "effective_date",
                        "value": "2026-01-15",
                        "assertion_mode": "source_declared",
                        "provenance_passage_id": accepted_passage,
                    }
                ],
            }
        ],
        "passages": [
            {
                "passage_id": accepted_passage,
                "anchors": [{"type": "character_range", "value": {"start": 0, "end": 16}}],
            },
            {
                "passage_id": rejected_passage,
                "anchors": [{"type": "character_range", "value": {"start": 0, "end": 8}}],
            },
        ],
        "history": [
            {
                "link_id": "history-accepted-001",
                "claim_id": claim_id,
                "passage_id": accepted_passage,
                "nomination": {"method": "bm25", "rank": 1, "variant": "shadow-integration"},
                "review": {"decision": "accepted", "reviewer": "contract-b-production-recipe"},
            },
            {
                "link_id": "history-rejected-001",
                "claim_id": claim_id,
                "passage_id": rejected_passage,
                "nomination": {"method": "bm25", "rank": 2, "variant": "shadow-integration"},
                "review": {"decision": "rejected", "reviewer": "contract-b-production-recipe"},
            },
        ],
        "history_count_checks": [
            {"claim_id": claim_id, "candidate": 2, "reviewed": 2, "admitted": 1}
        ],
        "aperture": [
            {
                "claim_id": claim_id,
                "search_scope": {"retrieval_method": "bm25", "top_k": 5},
                "outcome": {"state": "unknown", "value": None},
                "limitations": ["No proposition-specific completeness conclusion is asserted."],
            }
        ],
    }


def _build_corpus(*, eb_root: Path, apparatus_b: Path, out: Path) -> dict[str, Path]:
    from evidence_bundler.contracts.factual_context import (
        ContractBFactualContext,
        attach_factual_context,
    )
    from evidence_bundler.contracts.writer import build_retrieval_bundle, validate_bundle_tree
    from evidence_bundler.models.retrieval import RetrievalConfig

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    absent = out / "fresh-b12-absent"
    build_retrieval_bundle(
        eb_root / "examples" / "handoff-demo" / "scaffold-run-bm25-handoff-demo",
        absent,
        config=RetrievalConfig(retrieval_method="bm25", top_k=5, lexical_score_floor=0.0),
    )
    producer_errors = validate_bundle_tree(absent)
    if producer_errors:
        raise AssertionError(f"Evidence Bundler rejected fresh B corpus: {producer_errors}")
    if (absent / "CONTRACT_VERSION").read_text(encoding="utf-8").strip() != "1.2.0":
        raise AssertionError("production Evidence Bundler did not generate Contract B 1.2.0")
    _verify_contract_b(apparatus_b, absent)
    load_contract_b_intake(absent)

    present = out / "fresh-b12-present"
    shutil.copytree(absent, present)
    raw = _production_acceptance_extension(absent)
    extension = ContractBFactualContext.model_validate(raw)
    attach_factual_context(present, extension)
    producer_errors = validate_bundle_tree(present)
    if producer_errors:
        raise AssertionError(f"Evidence Bundler rejected factual-context B corpus: {producer_errors}")
    _verify_contract_b(apparatus_b, present)
    intake = load_contract_b_intake(present)
    if intake.extension_state != "present" or intake.semantic_context is None:
        raise AssertionError("CAL production intake did not expose the promoted B semantic context")
    return {"absent": absent, "present": present}


def _load_instruments(deps: Path) -> list[MeasurementInstrument]:
    specs = [
        ("comparison", deps / "rc7fb1" / INSTRUMENT_EVIDENCE["comparison"]["module"]),
        ("event_ordering", deps / "rc7fc" / INSTRUMENT_EVIDENCE["event_ordering"]["module"]),
        (
            "permission_composition",
            deps / "rc7fd" / INSTRUMENT_EVIDENCE["permission_composition"]["module"],
        ),
    ]
    instruments: list[MeasurementInstrument] = []
    for family, path in specs:
        module = _load_module(path, f"shadow_{family}")
        instruments.append(
            MeasurementInstrument(
                family=family,
                measure=module.measure,
                implementation_commit=INSTRUMENT_EVIDENCE[family]["commit"],
            )
        )
    return instruments


def _passage_map(intake: Any) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for passages in intake.bundle.passages.values():
        for passage in passages:
            if passage.passage_id in rows:
                raise AssertionError(f"non-unique passage id: {passage.passage_id}")
            rows[passage.passage_id] = passage
    return rows


def _core_ids_by_claim(intake: Any) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for claim in intake.bundle.claims:
        values = [row.passage_id for row in claim.evidence_passages]
        values.extend(row.passage_id for row in claim.counterevidence_passages)
        result[claim.claim_id] = list(dict.fromkeys(values))
    return result


def _selection(intake: Any, claim_id: str) -> tuple[list[str], list[str], str, dict[str, Any] | None]:
    core = _core_ids_by_claim(intake).get(claim_id, [])
    if intake.extension_state != "present":
        return core, [], "contract_b_core_claim_evidence_extension_absent", None

    ledger = intake.intake_ledger or {}
    covered = {
        row["claim_id"] for row in ledger.get("claims", []) if isinstance(row, dict)
    }
    covered.update(
        row["claim_id"] for row in ledger.get("history", []) if isinstance(row, dict)
    )
    covered.update(
        row["claim_id"] for row in ledger.get("aperture", []) if isinstance(row, dict)
    )
    if claim_id not in covered:
        return core, [], "contract_b_core_claim_evidence_no_extension_row", None

    semantic_rows = {
        row["claim_id"]: row for row in (intake.semantic_context or {}).get("claims", [])
    }
    admitted = [
        row["passage_id"] for row in semantic_rows.get(claim_id, {}).get("admitted_passages", [])
    ]
    excluded = [
        row["passage_id"]
        for row in ledger.get("history", [])
        if row.get("claim_id") == claim_id and row.get("review", {}).get("decision") == "rejected"
    ]
    aperture = next(
        (row for row in ledger.get("aperture", []) if row.get("claim_id") == claim_id), None
    )
    return admitted, excluded, "contract_b_promoted_semantic_context_admitted_only", aperture


def _contract_b_index(intake: Any) -> dict[str, Any]:
    propositions = {
        claim.claim_id: sha256(claim.claim_text.encode("utf-8")).hexdigest()
        for claim in intake.bundle.claims
        if claim.claim_type == "extracted_claim"
    }
    passages: dict[str, Any] = {}
    for source_rows in intake.bundle.passages.values():
        for passage in source_rows:
            passages[passage.passage_id] = {
                "source_id": passage.source_id,
                "passage_sha256": passage.passage_hash,
            }
    return {
        "contract_version": intake.bundle.manifest.schema_version,
        "bundle_id": intake.bundle.manifest.bundle_id,
        "bundle_hash": intake.bundle.manifest.bundle.bundle_hash,
        "propositions": propositions,
        "passages": passages,
    }


def _validate_c(module: Any, raw: bytes, index: dict[str, Any]) -> list[str]:
    return module.validate_contract_c_bytes(raw, contract_b_index=index)


def _run_case(
    *,
    name: str,
    bundle_dir: Path,
    instruments: list[MeasurementInstrument],
    c_validator: Any,
    candidate_sha: str,
    out: Path,
) -> dict[str, Any]:
    intake = load_contract_b_intake(bundle_dir)
    claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(intake.bundle)
    scopes = build_claim_evidence_scopes(intake.bundle)
    assessments = audit_claims(
        claims, evidence_bundle, audit_config, evidence_scopes=scopes
    )
    legacy_raw = export_contract_c_bytes(
        contents=intake.bundle,
        assessments=assessments,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
    )
    legacy = json.loads(legacy_raw)
    index = _contract_b_index(intake)
    legacy_errors = _validate_c(c_validator, legacy_raw, index)
    if legacy_errors:
        raise AssertionError(f"released CAL Contract-C output failed frozen C validation: {legacy_errors}")

    passage_map = _passage_map(intake)
    internal: dict[str, dict[str, Any]] = {}
    for prop in legacy["propositions"]:
        claim_id = prop["proposition"]["proposition_id"]
        selected, excluded, basis, aperture = _selection(intake, claim_id)
        observations: list[dict[str, Any]] = []
        for passage_id in selected:
            passage = passage_map[passage_id]
            observations.extend(
                measure_text(
                    passage.passage_text,
                    instruments,
                    passage_id=passage_id,
                )
            )
        internal[claim_id] = candidate_internal_record(
            claim_id=claim_id,
            selection_basis=basis,
            observations=observations,
            excluded_passage_ids=excluded,
            aperture_observation=aperture,
        )

    shadow = project_shadow_contract_c(
        legacy,
        semantic_implementation_sha=candidate_sha,
        internal_records=internal,
    )
    shadow_raw = canonical_bytes(shadow)
    shadow_errors = _validate_c(c_validator, shadow_raw, index)
    if shadow_errors:
        raise AssertionError(f"shadow Contract-C output failed frozen C validation: {shadow_errors}")

    shadow_again = project_shadow_contract_c(
        legacy,
        semantic_implementation_sha=candidate_sha,
        internal_records=internal,
    )
    if shadow_raw != canonical_bytes(shadow_again):
        raise AssertionError("shadow projection is not byte deterministic")

    case_out = out / name
    case_out.mkdir(parents=True, exist_ok=True)
    (case_out / "legacy-contract-c.json").write_bytes(legacy_raw)
    (case_out / "shadow-contract-c.json").write_bytes(shadow_raw)
    (case_out / "candidate-internal.json").write_bytes(canonical_bytes(internal))
    divergences = classify_legacy_shadow_divergence(legacy, shadow)
    (case_out / "differential.json").write_bytes(canonical_bytes(divergences))
    (case_out / "contract-b-index.json").write_bytes(canonical_bytes(index))

    statuses = Counter()
    authority_states = Counter()
    proposal_count = 0
    for record in internal.values():
        proposal_count += record["proposal_count"]
        for obs in record["semantic_measurements"]:
            measurement = obs.get("measurement")
            statuses[(measurement or {}).get("status", "EXECUTION_FAILURE")] += 1
            authority_states[obs["authority"]["state"]] += 1

    legacy_verdicts = Counter(
        row["conclusion"]["reported_verdict"] for row in legacy["propositions"]
    )
    shadow_verdicts = Counter(
        row["conclusion"]["reported_verdict"] for row in shadow["propositions"]
    )
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
        "legacy_contract_c": {
            "frozen_validator": "PASS",
            "sha256": sha256_hex(legacy_raw),
            "verdict_counts": dict(sorted(legacy_verdicts.items())),
        },
        "candidate": {
            "proposal_count": proposal_count,
            "measurement_status_counts": dict(sorted(statuses.items())),
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
            "verdict_counts": dict(sorted(shadow_verdicts.items())),
        },
        "divergences": divergences,
    }


def _microfixtures(instruments: list[MeasurementInstrument]) -> dict[str, Any]:
    fixtures = {
        "comparison": "The revised process is more effective than the baseline process.",
        "event_ordering": "After the inspection finished, the release review began.",
        "permission_composition": "Operators may enter the room after training, except during maintenance.",
        "neutral": "The document describes a routine review process.",
    }
    rows: list[dict[str, Any]] = []
    for fixture_id, text in fixtures.items():
        observations = measure_text(text, instruments, passage_id=f"micro:{fixture_id}")
        rows.append(
            {
                "fixture_id": fixture_id,
                "text_sha256": sha256(text.encode("utf-8")).hexdigest(),
                "observations": observations,
            }
        )
    return {
        "status": "controlled_measurement_microfixtures_not_contract_b_corpus",
        "purpose": "exercise instrument integration where the real B corpus lacks a discriminating cue",
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deps", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--candidate-sha", required=True)
    args = parser.parse_args()

    deps = args.deps.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    identities = {
        "apparatus_b": B_AUTHORITY_SHA,
        "apparatus_c": C_AUTHORITY_SHA,
        "evidence_bundler": EB_PRODUCTION_PIN,
        "cal_production_base": CAL_PRODUCTION_BASE,
        "cal_exporter_lineage": CAL_EXPORTER_LINEAGE,
        "candidate_sha": args.candidate_sha,
        "instruments": {family: row["commit"] for family, row in INSTRUMENT_EVIDENCE.items()},
    }
    _assert_dep_identity(deps / "apparatus-b", B_AUTHORITY_SHA)
    _assert_dep_identity(deps / "apparatus-c", C_AUTHORITY_SHA)
    _assert_dep_identity(deps / "evidence-bundler", EB_PRODUCTION_PIN)
    _assert_dep_identity(deps / "rc7fb1", INSTRUMENT_EVIDENCE["comparison"]["commit"])
    _assert_dep_identity(deps / "rc7fc", INSTRUMENT_EVIDENCE["event_ordering"]["commit"])
    _assert_dep_identity(deps / "rc7fd", INSTRUMENT_EVIDENCE["permission_composition"]["commit"])

    c_validator = _load_module(
        deps / "apparatus-c" / "validators" / "contract_c.py", "frozen_contract_c_validator"
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

    projection_losses = [
        {
            "distinction": "bounded structured measurement proposals and per-instrument authority states",
            "contract_c_representation": "semantic_validity=performed/unknown plus not_checkable only",
            "loss": True,
            "legitimate_collapse_for_this_run": True,
            "downstream_relevant_difference_demonstrated": False,
            "consequence": "keep detailed proposals internal; no Contract-C successor escalation",
        },
        {
            "distinction": "Contract-B accepted/rejected nomination history and aperture observation",
            "contract_c_representation": "not duplicated; exact B object is bound by identity",
            "loss": False,
            "legitimate_collapse_for_this_run": True,
            "downstream_relevant_difference_demonstrated": False,
            "consequence": "consume upstream observation without inventing a CAL completeness assessment",
        },
    ]
    coverage = {
        "real_contract_b_cases": ["fresh-b12-absent", "fresh-b12-present"],
        "represented": [
            "valid Contract-B 1.2.0 intake",
            "optional factual-context absent",
            "accepted/admitted passage identity",
            "rejected/excluded passage identity",
            "aperture outcome explicitly unknown",
            "legacy CAL result",
            "candidate insufficient semantic authority",
            "Contract-C not_checkable projection",
        ],
        "not_claimed_from_real_b_corpus": [
            "semantic support/refutation truth label",
            "semantic neutral truth label",
            "aperture completeness conclusion",
            "source-established semantic unknown",
            "extraction authority",
            "authorized typed population mapping",
            "authorized numeric assertion/scope mapping",
            "multi-passage composition authority",
        ],
        "controlled_internal_only": [
            "comparison measurement proposal",
            "explicit event-ordering measurement proposal",
            "permission/exception/temporal measurement proposal",
            "operator inapplicability/measurement unresolved states",
        ],
    }
    receipt = {
        "identities": identities,
        "cases": cases,
        "measurement_microfixtures": {
            "path": "measurement-microfixtures.json",
            "not_contract_b_corpus": True,
        },
        "projection_losses": projection_losses,
        "coverage": coverage,
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
        "terminal_disposition": "AUTHORITY_MACHINERY_DEMONSTRATED_BLOCKER_TO_STRONGER_SHADOW_CONCLUSION",
        "production_promotion": "NO",
    }
    (out / "RUN-RECEIPT.json").write_bytes(canonical_bytes(receipt))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
