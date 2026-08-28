"""RC2-B matched-input probe: Contract-B factual state vs CAL attribution.

Research-only. This module imports and exercises production APIs but changes none.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import yaml

from evidence_bundler.contracts.factual_context import (
    ContractBFactualContext as EBFactualContext,
    attach_factual_context,
)
from evidence_bundler.contracts.writer import build_retrieval_bundle, validate_bundle_tree
from evidence_bundler.models.retrieval import RetrievalConfig

from claim_audit_lab.auditor import audit_claims
from claim_audit_lab.contracts.adapter import adapt_bundle_to_pipeline, build_claim_evidence_scopes
from claim_audit_lab.contracts.bundle_loader import BundleContents, load_bundle
from claim_audit_lab.contracts.factual_context import load_contract_b_intake
from claim_audit_lab.models import ClaimAssessment

ROOT = Path(__file__).resolve().parents[1]
EB_ROOT = ROOT / "_deps" / "evidence-bundler"
OUT = ROOT / "build" / "research" / "contract-c-rc2-b"


def _yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), path
    return data


def _claim_and_passage_ids(
    bundle_dir: Path,
) -> tuple[str, list[str], dict[str, str], dict[str, Any]]:
    claim_paths = sorted((bundle_dir / "claims").glob("*.yaml"))
    assert claim_paths, "fresh Contract-B bundle contains no claims"
    claim_doc = _yaml(claim_paths[0])
    claim_id = str(claim_doc["claim_id"])

    passage_source: dict[str, str] = {}
    for path in sorted((bundle_dir / "evidence").glob("*/passages/*.yaml")):
        row = _yaml(path)
        passage_source[str(row["passage_id"])] = str(row["source_id"])

    nominees: list[str] = []
    for field in ("evidence_passages", "counterevidence_passages"):
        for row in claim_doc.get(field, []):
            if isinstance(row, dict) and isinstance(row.get("passage_id"), str):
                nominees.append(row["passage_id"])
    nominees.extend(passage_id for passage_id in passage_source if passage_id not in nominees)
    nominees = list(dict.fromkeys(nominees))
    assert nominees, "need at least one canonical passage"
    return claim_id, nominees, passage_source, claim_doc


def _extension(
    *,
    claim_id: str,
    accepted_passage: str,
    accepted_source: str,
) -> EBFactualContext:
    raw: dict[str, Any] = {
        "schema": "contract-b-factual-context-v1",
        "history_complete": True,
        "claims": [
            {
                "claim_id": claim_id,
                "origin": {
                    "state": "known",
                    "value": {"surface": "rc2-b-matched-production-input"},
                },
                "atomicity": {"state": "known", "value": "source_declared_atomic"},
            }
        ],
        "sources": [
            {
                "source_id": accepted_source,
                "context_facts": [
                    {
                        "fact_id": "fact-effective-date",
                        "predicate": "effective_date",
                        "value": "2026-01-15",
                        "assertion_mode": "source_declared",
                        "provenance_passage_id": accepted_passage,
                    },
                    {
                        "fact_id": "fact-version",
                        "predicate": "version",
                        "value": "7.2",
                        "assertion_mode": "source_declared",
                        "provenance_passage_id": accepted_passage,
                    },
                    {
                        "fact_id": "fact-status",
                        "predicate": "status",
                        "value": "effective",
                        "assertion_mode": "source_declared",
                        "provenance_passage_id": accepted_passage,
                    },
                    {
                        "fact_id": "fact-supplier",
                        "predicate": "supplier_identity",
                        "value": "supplier-fixture-a",
                        "assertion_mode": "source_declared",
                        "provenance_passage_id": accepted_passage,
                    },
                ],
            }
        ],
        "passages": [
            {
                "passage_id": accepted_passage,
                "anchors": [
                    {
                        "type": "character_range",
                        "value": {"start": 0, "end": 16},
                    }
                ],
            }
        ],
        "history": [
            {
                "link_id": "history-accepted-001",
                "claim_id": claim_id,
                "passage_id": accepted_passage,
                "nomination": {"method": "bm25", "rank": 1},
                "review": {"decision": "accepted", "reviewer": "rc2-b-fixture"},
            }
        ],
        "history_count_checks": [
            {"claim_id": claim_id, "candidate": 1, "reviewed": 1, "admitted": 1}
        ],
        "aperture": [
            {
                "claim_id": claim_id,
                "search_scope": {
                    "retrieval_method": "bm25",
                    "top_k": 5,
                    "scope_id": "same-corpus-same-query",
                },
                "outcome": {
                    "state": "known",
                    "value": {"search_completed": True},
                },
                "limitations": [
                    "Bounded top-k observation only; no completeness conclusion is asserted."
                ],
            }
        ],
    }
    return EBFactualContext.model_validate(raw)


def _core_digest(bundle_dir: Path) -> str:
    """Hash semantic core held fixed by the matched-input experiment."""
    h = hashlib.sha256()
    paths = [bundle_dir / "audit_config.yaml"]
    paths.extend(sorted((bundle_dir / "claims").glob("*.yaml")))
    paths.extend(sorted((bundle_dir / "evidence").glob("**/*.yaml")))
    for path in paths:
        rel = path.relative_to(bundle_dir).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(hashlib.sha256(path.read_bytes()).digest())
        h.update(b"\n")
    return h.hexdigest()


def _run_v02(contents: BundleContents) -> list[dict[str, Any]]:
    """Mirror the production `_audit_bundle_v0_2` computation before rendering/writeback."""
    claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(contents)
    assessments = audit_claims(
        claims,
        evidence_bundle,
        audit_config,
        evidence_scopes=build_claim_evidence_scopes(contents),
    )
    return [assessment.model_dump(mode="json") for assessment in assessments]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="contract-c-rc2-b-") as tmp_raw:
        tmp = Path(tmp_raw)
        absent = tmp / "matched-1.2-absent"
        build_retrieval_bundle(
            EB_ROOT / "examples" / "handoff-demo" / "scaffold-run-bm25-handoff-demo",
            absent,
            config=RetrievalConfig(
                retrieval_method="bm25",
                top_k=5,
                lexical_score_floor=0.0,
            ),
        )
        assert (absent / "CONTRACT_VERSION").read_text(encoding="utf-8").strip() == "1.2.0"
        assert not validate_bundle_tree(absent), validate_bundle_tree(absent)

        claim_id, nominees, passage_source, _ = _claim_and_passage_ids(absent)
        accepted_passage = nominees[0]
        accepted_source = passage_source[accepted_passage]

        present = tmp / "matched-1.2-present"
        shutil.copytree(absent, present)
        attach_factual_context(
            present,
            _extension(
                claim_id=claim_id,
                accepted_passage=accepted_passage,
                accepted_source=accepted_source,
            ),
        )
        assert not validate_bundle_tree(present), validate_bundle_tree(present)

        absent_intake = load_contract_b_intake(absent)
        present_intake = load_contract_b_intake(present)
        assert absent_intake.extension_state == "absent"
        assert absent_intake.intake_ledger is None
        assert absent_intake.semantic_context is None
        assert present_intake.extension_state == "present"
        assert present_intake.intake_ledger is not None
        assert present_intake.semantic_context is not None

        # Contract B 1.2 visibly transports the legal evidence-world facts.
        ledger = present_intake.intake_ledger
        semantic_context = present_intake.semantic_context
        assert ledger["aperture"][0]["search_scope"]["top_k"] == 5
        assert ledger["aperture"][0]["outcome"]["state"] == "known"
        assert "aperture" not in semantic_context
        semantic_text = json.dumps(semantic_context, sort_keys=True)
        for expected in ("effective_date", "version", "status", "supplier_identity"):
            assert expected in semantic_text

        # Attaching the extension reseals identity, but does not mutate the core claims/evidence/policy.
        absent_core = _core_digest(absent)
        present_core = _core_digest(present)
        assert absent_core == present_core

        absent_contents = load_bundle(absent)
        present_contents = load_bundle(present)
        assert absent_contents.claims == present_contents.claims
        assert absent_contents.source_profiles == present_contents.source_profiles
        assert absent_contents.passages == present_contents.passages
        assert absent_contents.audit_config == present_contents.audit_config

        absent_assessments = _run_v02(absent_contents)
        present_assessments = _run_v02(present_contents)
        assert absent_assessments == present_assessments
        assert absent_assessments, "matched production bundle yielded no CAL assessments"

        # A valid, populated extension does not cause v0.2 to emit the previously missing axes.
        fields = set(ClaimAssessment.model_fields)
        missing_axes = {
            "eligibility",
            "semantic_validity",
            "aperture",
            "temporal_applicability",
            "citation",
            "decision_basis",
            "supersedes",
        }
        assert not (fields & missing_axes)

        receipt = {
            "experiment": "contract-c-rc2-b-upstream-sufficiency",
            "contract_b_version": "1.2.0",
            "absent_extension_state": absent_intake.extension_state,
            "present_extension_state": present_intake.extension_state,
            "core_semantic_digest_absent": absent_core,
            "core_semantic_digest_present": present_core,
            "core_semantic_inputs_equal": absent_core == present_core,
            "present_ledger_has_aperture_observation": bool(ledger["aperture"]),
            "present_semantic_context_has_aperture": "aperture" in semantic_context,
            "present_semantic_context_fact_predicates": sorted(
                fact["predicate"]
                for claim in semantic_context["claims"]
                for passage in claim["admitted_passages"]
                for fact in passage["context_facts"]
            ),
            "v02_assessments_equal": absent_assessments == present_assessments,
            "assessment_count": len(absent_assessments),
            "assessment_fields": sorted(fields),
            "missing_rc2_a_axes_exposed": sorted(fields & missing_axes),
            "observed_support_labels": [row["support_label"] for row in absent_assessments],
            "observed_support_signals": [row["support_signal"] for row in absent_assessments],
        }
        (OUT / "matched-input-receipt.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
