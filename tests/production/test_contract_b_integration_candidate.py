from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from claim_audit_lab.contracts.bundle_loader import BundleContents
from claim_audit_lab.contracts.cb_models import (
    CBAuditConfig,
    CBAuditRulePolicies,
    CBAuditScoringConfig,
    CBBundleManifest,
    CBBundleStats,
    CBClaim,
    CBClaimEvidencePassage,
    CBEvidenceBuilderInfo,
    CBPassage,
    CBPassageProvenance,
    CBQualityGates,
    CBReviewerSignOff,
    CBSourceBibliographic,
    CBSourceProfile,
    CBValidationSetRef,
)
from claim_audit_lab.contracts.factual_context import ContractBIntakeView
from claim_audit_lab.production_v1.bundle_input import (
    BundleTargetValidationError,
    prepare_contract_b_input,
)


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _tagged(value: str) -> str:
    return f"sha256:{_hex(value)}"


def _view() -> ContractBIntakeView:
    claim_text = "Women had a higher rate than Men."
    accepted_text = "Women had a higher rate than Men."
    rejected_text = "Cats had a higher rate than Dogs."
    source_hash = _tagged(accepted_text + rejected_text)
    accepted = CBPassage(
        passage_id="p-accepted",
        source_id="source-1",
        bundle_id="bundle-1",
        schema_version="1.2.0",
        passage_text=accepted_text,
        section=None,
        paragraph_index=0,
        char_start=0,
        char_end=len(accepted_text),
        passage_hash=_tagged(accepted_text),
        cited_by_claims=["claim-1"],
        extraction_method="auto_retrieved",
        provenance=CBPassageProvenance(
            source_url="https://example.invalid/source",
            source_access_date_utc="2026-09-15T00:00:00Z",
            source_content_hash=source_hash,
            scaffold_run_id="run-1",
            evidence_builder_version="eb-v1",
            bundle_created_at_utc="2026-09-15T00:00:00Z",
        ),
    )
    rejected = CBPassage(
        passage_id="p-rejected",
        source_id="source-1",
        bundle_id="bundle-1",
        schema_version="1.2.0",
        passage_text=rejected_text,
        section=None,
        paragraph_index=1,
        char_start=len(accepted_text) + 1,
        char_end=len(accepted_text) + 1 + len(rejected_text),
        passage_hash=_tagged(rejected_text),
        cited_by_claims=[],
        extraction_method="auto_retrieved",
        provenance=CBPassageProvenance(
            source_url="https://example.invalid/source",
            source_access_date_utc="2026-09-15T00:00:00Z",
            source_content_hash=source_hash,
            scaffold_run_id="run-1",
            evidence_builder_version="eb-v1",
            bundle_created_at_utc="2026-09-15T00:00:00Z",
        ),
    )
    claim_passage = CBClaimEvidencePassage(
        passage_id=accepted.passage_id,
        source_id=accepted.source_id,
        passage_text=accepted.passage_text,
        section=None,
        char_start=accepted.char_start,
        char_end=accepted.char_end,
        source_trust_level="background",
        passage_hash=accepted.passage_hash,
    )
    claim = CBClaim(
        claim_id="claim-1",
        bundle_id="bundle-1",
        schema_version="1.2.0",
        claim_text=claim_text,
        claim_type="retrieval_seed",
        workflow_condition="baseline",
        task_id="task-1",
        scaffold_support_status="uncertain",
        scaffold_claim_strength=0.0,
        scaffold_extraction_fidelity=0.0,
        scaffold_counterevidence_found=False,
        scaffold_downgraded=False,
        evidence_passages=[claim_passage],
        counterevidence_passages=[],
    )
    source = CBSourceProfile(
        source_id="source-1",
        schema_version="1.2.0",
        bibliographic=CBSourceBibliographic(
            source_type="other",
            title="Fixture source",
            authors=[],
            publication_date=None,
            pmid=None,
            doi=None,
            url="https://example.invalid/source",
            access_date_utc="2026-09-15T00:00:00Z",
        ),
        trust_level="background",
        content_hash=source_hash,
        retrieved_for=["claim-1"],
        retrieval_query=claim_text,
        retrieval_rank=1,
        notes="fixture",
    )
    manifest = CBBundleManifest(
        bundle_id="bundle-1",
        schema_version="1.2.0",
        generated_at_utc="2026-09-15T00:00:00Z",
        source_run_id="run-1",
        source_contract_version="1.2.0",
        source_corpus_hash=_tagged("corpus"),
        evidence_builder=CBEvidenceBuilderInfo(
            version="eb-v1",
            config_hash=_tagged("config"),
            operator="fixture",
            build_timestamp_utc="2026-09-15T00:00:00Z",
        ),
        bundle=CBBundleStats(
            total_claims_in_source=1,
            claims_included=1,
            claims_excluded=0,
            exclusion_rationale="",
            total_evidence_passages=2,
            bundle_hash=_tagged("bundle-1"),
        ),
        transformations=[],
        quality_gates=CBQualityGates(
            every_claim_has_at_least_one_passage=True,
            every_passage_links_to_source_profile=True,
            source_hashes_verified=True,
            bundle_integrity_verified=True,
        ),
        audit_config_version="cal-rules-v1.2.0",
        audit_config_hash=_tagged("audit-config"),
        validation_set_version="fixture-v1",
        validation_set_hash=_tagged("validation"),
        reviewer_sign_off=CBReviewerSignOff(required=False),
    )
    audit_config = CBAuditConfig(
        config_id="cal-rules-v1.2.0",
        config_hash=_tagged("audit-config"),
        schema_version="1.2.0",
        frozen_at_utc="2026-09-15T00:00:00Z",
        scoring=CBAuditScoringConfig(
            support_threshold_sourced=0.8,
            support_threshold_partial=0.5,
            counterevidence_weight=1.0,
        ),
        rule_policies=CBAuditRulePolicies(
            require_passage_level_match=True,
            flag_unsupported_threshold=0.5,
            false_caution_detection=True,
            false_caution_threshold=0.5,
            overstated_detection=True,
            needs_source_detection=True,
        ),
        known_limitations=[],
        change_log=[],
    )
    validation = CBValidationSetRef(
        schema_version="1.2.0",
        validation_set_version="fixture-v1",
        validation_set_hash=_tagged("validation"),
        frozen_at_utc="2026-09-15T00:00:00Z",
        description="fixture",
        notes="",
    )
    bundle = BundleContents(
        manifest=manifest,
        audit_config=audit_config,
        validation_set_ref=validation,
        claims=[claim],
        passages={"source-1": [accepted, rejected]},
        source_profiles={"source-1": source},
    )
    intake_ledger = {
        "schema": "contract-b-factual-context-v1",
        "history_complete": True,
        "claims": [],
        "sources": [],
        "passages": [],
        "history": [
            {
                "link_id": "h-accepted",
                "claim_id": "claim-1",
                "passage_id": "p-accepted",
                "nomination": {"rank": 1},
                "review": {"decision": "accepted"},
            },
            {
                "link_id": "h-rejected",
                "claim_id": "claim-1",
                "passage_id": "p-rejected",
                "nomination": {"rank": 2},
                "review": {"decision": "rejected"},
            },
        ],
        "history_count_checks": [],
        "aperture": [
            {
                "claim_id": "claim-1",
                "search_scope": {"profile": "fixture"},
                "outcome": {"state": "unknown", "value": None},
                "limitations": ["fixture only"],
            }
        ],
    }
    semantic_context = {
        "schema": "contract-b-cal-semantic-context-v1",
        "claims": [
            {
                "claim_id": "claim-1",
                "origin": None,
                "atomicity": None,
                "admitted_passages": [
                    {
                        "passage_id": "p-accepted",
                        "source_id": "source-1",
                        "anchors": [],
                        "context_facts": [],
                    }
                ],
            }
        ],
    }
    return ContractBIntakeView(
        bundle=bundle,
        extension_state="present",
        intake_ledger=intake_ledger,
        semantic_context=semantic_context,
    )


def _target(path: Path, *, text_sha256: str | None = None) -> bytes:
    claim = "Women had a higher rate than Men."
    value = {
        "claim_id": "claim-1",
        "proposition": {
            "proposition_id": "claim-1",
            "text_sha256": text_sha256 or _hex(claim),
            "semantic_family": "strict_comparison",
            "fields": {
                "lhs_entity": "Women",
                "rhs_entity": "Men",
                "comparison_direction": "MORE_THAN",
            },
        },
    }
    raw = (json.dumps(value, indent=2) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def test_prepared_input_preserves_full_ledger_but_semantics_use_only_accepted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    view = _view()
    import claim_audit_lab.production_v1.bundle_input as bundle_input

    monkeypatch.setattr(bundle_input, "load_contract_b_intake", lambda _path: view)
    target = tmp_path / "target.json"
    raw = _target(target)

    prepared = prepare_contract_b_input(tmp_path / "bundle", target)

    assert prepared.target_bytes == raw
    assert prepared.intake is view
    assert prepared.context.original_claim == "Women had a higher rate than Men."
    assert [row.passage_id for row in prepared.context.evidence_world.admitted_passages] == [
        "p-accepted"
    ]
    assert prepared.context.evidence_world.aperture_observation() == {
        "contract_b_factual_context_state": "present",
        "observation": view.intake_ledger["aperture"][0],
    }
    assert {row["passage_id"] for row in prepared.intake_snapshot["passages"]} == {
        "p-accepted",
        "p-rejected",
    }
    assert prepared.intake_snapshot["factual_context_intake_ledger"] == view.intake_ledger
    assert prepared.intake_snapshot["semantic_context"] == view.semantic_context


def test_target_text_hash_must_bind_exact_contract_b_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    view = _view()
    import claim_audit_lab.production_v1.bundle_input as bundle_input

    monkeypatch.setattr(bundle_input, "load_contract_b_intake", lambda _path: view)
    target = tmp_path / "target.json"
    _target(target, text_sha256=_hex("different text"))

    with pytest.raises(BundleTargetValidationError, match="exact Contract B claim text"):
        prepare_contract_b_input(tmp_path / "bundle", target)
