"""Normalize a loaded C-B bundle into v1 ``AuditRequest`` objects.

This is the apparatus-intake boundary (DECISIONS.md § 2026-06-21 § 3): YAML is
parsed exactly once — by :func:`claim_audit_lab.contracts.bundle_loader.load_bundle`,
which fail-closes on the vocabulary pin, ``SHA256SUMS``, the audit-config hash,
and schema — and everything downstream of :func:`bundle_to_requests` touches only
the frozen pydantic v1 contract types. The inference pipeline never sees YAML.

Two design choices are load-bearing:

* **The retriever, not the bundler, picks candidates** (DECISIONS.md § 2026-06-21
  § 2). Every request therefore carries the bundle's *full* passage set; the C-B
  ``evidence_passages`` / ``counterevidence_passages`` curation is not used to
  pre-filter what v1 sees.
* **Only ``extracted_claim`` records are auditable.** ``retrieval_seed`` records
  are topic prompts, not checkable statements, and are skipped — mirroring the
  v0.2 adapter (``contracts/adapter.py``) and the C-B type boundary documented in
  ``contracts/cb_models.py``.

The selector that decides whether a bundle reaches v1 at all
(``CBAuditConfig.pipeline``) is read by the CLI router, not here: this normalizer
is pipeline-agnostic so the same request shape is available whichever path runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from claim_audit_lab.contracts.bundle_loader import (
    BundleContents,
    BundleIntegrityError,
    load_bundle,
)
from claim_audit_lab.contracts.cb_models import CBPassage
from claim_audit_lab.v1.models import AuditConfig, AuditRequest, AuditTrace, Passage

_TRACE_SUFFIX = ".audit-trace.json"


class AuditedBundleError(BundleIntegrityError):
    """Raised when a verified C-B bundle has invalid v1 audit traces."""


@dataclass
class AuditedBundleContents(BundleContents):
    """Verified C-B contents plus one typed v1 trace per auditable claim.

    This is an additive subtype of :class:`BundleContents`: callers retain the
    existing manifest/config/claim/passage fields and gain ``traces`` keyed by
    ``claim_id``.
    """

    traces: dict[str, AuditTrace]


def bundle_to_requests(
    bundle: BundleContents,
    audit_config: AuditConfig,
) -> list[AuditRequest]:
    """Return one :class:`AuditRequest` per auditable claim in ``bundle``.

    ``audit_config`` is the pinned v1 inference config (typically
    :func:`claim_audit_lab.v1.config.load_default_audit_config`); it is stamped
    into every request unchanged. The bundle's own ``CBAuditConfig`` thresholds
    are a v0.2 artifact and are deliberately *not* consulted — v1 sources its
    thresholds from the versioned rules file, not from per-bundle data.

    Each request's ``passages`` is the bundle's full passage set in a
    deterministic order (sorted by ``source_id``, then by load order within a
    source), so the trace is byte-reproducible. ``retrieval_seed`` claims are
    skipped; if a bundle has none auditable, the result is empty.
    """
    passages = _normalize_passages(bundle)
    return [
        AuditRequest(
            claim_id=claim.claim_id,
            claim_text=claim.claim_text,
            passages=passages,
            audit_config=audit_config,
        )
        for claim in bundle.claims
        if claim.claim_type == "extracted_claim"
    ]


def load_audited(
    bundle_dir: Path,
    *,
    deviations_dir: Path | None = None,
) -> AuditedBundleContents:
    """Fail-closed load of a C-B audited copy with typed v1 traces.

    The existing :func:`load_bundle` remains the sole C-B/YAML loader and runs
    first, so contract version, schema, policy, ``SHA256SUMS``, bundle hash, and
    audit-config hash are verified before any trace is trusted. This helper then
    validates each ``claims/*.audit-trace.json`` directly into the strict,
    extra-forbidding :class:`AuditTrace` model and checks its C-B claim binding.
    """
    bundle_dir = bundle_dir.resolve()
    contents = load_bundle(bundle_dir, deviations_dir=deviations_dir)
    claims_by_id = {
        claim.claim_id: claim for claim in contents.claims if claim.claim_type == "extracted_claim"
    }
    traces: dict[str, AuditTrace] = {}

    for trace_path in sorted((bundle_dir / "claims").glob(f"*{_TRACE_SUFFIX}")):
        file_claim_id = trace_path.name.removesuffix(_TRACE_SUFFIX)
        try:
            trace = AuditTrace.model_validate_json(trace_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValidationError) as exc:
            raise AuditedBundleError(f"Invalid v1 audit trace {trace_path.name}: {exc}") from exc

        claim = claims_by_id.get(file_claim_id)
        if claim is None:
            raise AuditedBundleError(
                f"Audit trace {trace_path.name} does not bind to an extracted C-B claim"
            )
        if trace.claim_id != file_claim_id:
            raise AuditedBundleError(
                f"Audit trace {trace_path.name} claim_id mismatch: {trace.claim_id}"
            )
        if trace.claim_text != claim.claim_text:
            raise AuditedBundleError(
                f"Audit trace {trace_path.name} claim_text does not match the C-B claim"
            )
        traces[file_claim_id] = trace

    missing_trace_ids = sorted(set(claims_by_id) - set(traces))
    if missing_trace_ids:
        raise AuditedBundleError(
            "Missing v1 audit traces for extracted claims: " + ", ".join(missing_trace_ids)
        )

    return AuditedBundleContents(
        manifest=contents.manifest,
        audit_config=contents.audit_config,
        validation_set_ref=contents.validation_set_ref,
        claims=contents.claims,
        passages=contents.passages,
        source_profiles=contents.source_profiles,
        traces=traces,
    )


def _normalize_passages(bundle: BundleContents) -> list[Passage]:
    """Flatten every source's passages into one deterministically ordered list.

    Each passage is joined to its source's ``trust_level`` (Decision H / D1,
    ``cal-rules-v1.5.0``): the provenance attribute the eligibility rules read at
    verdict time. The fail-closed loader guarantees every ``source_id`` in
    ``bundle.passages`` has a matching ``source_profiles`` entry, so a missing key
    here is a real invariant break, not a soft-defaulted case.
    """
    return [
        _to_passage(passage, bundle.source_profiles[source_id].trust_level)
        for source_id in sorted(bundle.passages)
        for passage in bundle.passages[source_id]
    ]


def _to_passage(passage: CBPassage, trust_level: str) -> Passage:
    """Convert one C-B passage record into a v1 :class:`Passage`.

    The v1 ``passage_id`` is the globally-unique ``{source_id}/{passage_id}``
    handle (C-B ``passage_id`` is only unique *within* a source — see
    ``bundle_loader._verify_loaded_consistency`` — and the pipeline keys passages
    by this id). The raw C-B coordinates plus the passage hash are preserved in
    ``source_meta`` so a trace entry cross-references back to
    ``evidence/{source_id}/passages/{passage_id}.yaml`` and its integrity hash.
    The source's ``trust_level`` (provenance tier — ``primary`` / ``secondary`` /
    ``background``) is carried in ``source_meta`` too, so the eligibility rules can
    read provenance at verdict time without re-loading the source profile
    (Decision H / D1). Bundle passages therefore *always* carry ``trust_level``;
    only directly-constructed (non-intake) passages may lack it.
    """
    source_meta = {
        "source_id": passage.source_id,
        "passage_id": passage.passage_id,
        "passage_hash": passage.passage_hash,
        "trust_level": trust_level,
    }
    if passage.section is not None:
        source_meta["section"] = passage.section
    return Passage(
        passage_id=f"{passage.source_id}/{passage.passage_id}",
        text=passage.passage_text,
        source_meta=source_meta,
    )


__all__ = [
    "AuditedBundleContents",
    "AuditedBundleError",
    "bundle_to_requests",
    "load_audited",
]
