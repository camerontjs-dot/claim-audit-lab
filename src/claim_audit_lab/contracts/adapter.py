"""Adapt C-B BundleContents to CAL-native audit pipeline types.

Type boundary (must never be crossed)
--------------------------------------
C-B  claim_type  →  "retrieval_seed" | "extracted_claim"  (bundle contract)
CAL  Claim.claim_type  →  "numeric" | "causal" | …         (semantic, pipeline)

Only ``extracted_claim`` records become CAL Claims.
``retrieval_seed`` records are topic prompts, not auditable statements;
they are silently skipped.

CAL semantic claim_type is always derived from claim_text via
classify_claim_text(); the C-B claim_type field is never copied into this slot.
"""

from __future__ import annotations

from datetime import date as Date

from claim_audit_lab.classifiers import classify_claim_text
from claim_audit_lab.contracts.bundle_loader import BundleContents
from claim_audit_lab.contracts.cb_models import (
    CBAuditConfig,
    CBClaim,
    CBPassage,
    CBSourceProfile,
    CBSourceType,
    TrustLevel,
)
from claim_audit_lab.evidence_matching import ClaimEvidenceScope
from claim_audit_lab.models import (
    AuditConfig,
    Claim,
    EvidenceBundle,
    EvidenceExcerpt,
    EvidenceSource,
    SourceReliability,
    SourceType,
)

# Map C-B source_type strings to the closest CAL SourceType literal.
# CAL's SourceType vocabulary does not match C-B's; best-effort mapping,
# fallback to "unknown".
_SOURCE_TYPE_MAP: dict[CBSourceType, SourceType] = {
    "journal_article": "article",
    "regulatory_guidance": "report",
    "preprint": "article",
    "web_page": "documentation",
    "book": "report",
    "other": "unknown",
}

_TRUST_LEVEL_RELIABILITY: dict[TrustLevel, SourceReliability] = {
    "primary": "high",
    "secondary": "medium",
    "background": "low",
}


def adapt_bundle_to_pipeline(
    contents: BundleContents,
) -> tuple[list[Claim], EvidenceBundle, AuditConfig]:
    """Return ``(cal_claims, evidence_bundle, audit_config)`` for the CAL auditor.

    Only ``extracted_claim`` records are adapted as auditable CAL Claims.
    """
    cal_claims = [_adapt_claim(cb) for cb in contents.claims if cb.claim_type == "extracted_claim"]

    cal_sources = [
        _adapt_source(src_id, profile, contents.passages.get(src_id, []))
        for src_id, profile in contents.source_profiles.items()
    ]

    return (
        cal_claims,
        EvidenceBundle(sources=cal_sources),
        _adapt_audit_config(contents),
    )


def build_claim_evidence_scopes(
    contents: BundleContents,
) -> dict[str, ClaimEvidenceScope]:
    """Return explicit support and counterevidence passage scopes by claim ID."""
    return {
        claim.claim_id: ClaimEvidenceScope(
            support_excerpt_ids=frozenset(
                _excerpt_id(passage.source_id, passage.passage_id)
                for passage in claim.evidence_passages
            ),
            counter_excerpt_ids=frozenset(
                _excerpt_id(passage.source_id, passage.passage_id)
                for passage in claim.counterevidence_passages
            ),
        )
        for claim in contents.claims
        if claim.claim_type == "extracted_claim"
    }


def _adapt_claim(cb: CBClaim) -> Claim:
    return Claim(
        id=cb.claim_id,
        text=cb.claim_text,
        # Semantic type derived from text — NOT copied from cb.claim_type
        claim_type=classify_claim_text(cb.claim_text),
        location=_claim_location(cb),
    )


def _adapt_source(
    src_id: str,
    profile: CBSourceProfile,
    passages: list[CBPassage],
) -> EvidenceSource:
    bibliographic = profile.bibliographic
    cal_source_type = _SOURCE_TYPE_MAP.get(bibliographic.source_type, "unknown")
    excerpts = [
        EvidenceExcerpt(
            id=_excerpt_id(src_id, passage.passage_id),
            text=passage.passage_text,
            notes=_passage_notes(passage),
        )
        for passage in passages
    ]
    return EvidenceSource(
        id=src_id,
        title=bibliographic.title,
        source_type=cal_source_type,
        reliability=_TRUST_LEVEL_RELIABILITY.get(profile.trust_level, "unknown"),
        url=bibliographic.url,
        date=_parse_date(bibliographic.publication_date),
        excerpts=excerpts,
    )


def _adapt_audit_config(contents: BundleContents) -> AuditConfig:
    cb_cfg: CBAuditConfig = contents.audit_config
    return AuditConfig(
        reference_date=_parse_date(contents.manifest.generated_at_utc),
        min_overlap_score=cb_cfg.rule_policies.flag_unsupported_threshold,
        max_candidate_evidence=max(contents.manifest.bundle.total_evidence_passages, 1),
    )


def _claim_location(cb: CBClaim) -> str:
    return (
        f"C-B bundle {cb.bundle_id}; "
        f"workflow_condition={cb.workflow_condition}; "
        f"task_id={cb.task_id}; "
        f"scaffold_support_status={cb.scaffold_support_status}; "
        f"scaffold_claim_strength={cb.scaffold_claim_strength:.2f}; "
        f"scaffold_extraction_fidelity={cb.scaffold_extraction_fidelity:.2f}; "
        f"scaffold_counterevidence_found={cb.scaffold_counterevidence_found}; "
        f"scaffold_downgraded={cb.scaffold_downgraded}"
    )


def _excerpt_id(source_id: str, passage_id: str) -> str:
    return f"{source_id}/{passage_id}"


def _passage_notes(passage: CBPassage) -> str:
    notes = [
        f"c_b_passage_id={passage.passage_id}",
        f"section={passage.section or 'not recorded'}",
        f"paragraph_index={passage.paragraph_index}",
        f"char_range={passage.char_start}-{passage.char_end}",
        f"extraction_method={passage.extraction_method}",
        f"passage_hash={passage.passage_hash}",
        f"source_content_hash={passage.provenance.source_content_hash}",
        f"scaffold_run_id={passage.provenance.scaffold_run_id}",
        f"evidence_builder_version={passage.provenance.evidence_builder_version}",
    ]
    return "; ".join(notes)


def _parse_date(value: str | None) -> Date | None:
    if value is None:
        return None
    try:
        return Date.fromisoformat(value[:10])
    except ValueError:
        return None


__all__ = ["adapt_bundle_to_pipeline", "build_claim_evidence_scopes"]
