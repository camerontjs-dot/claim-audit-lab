"""Write a v1 audit back into a C-B evidence-bundle copy.

The v1 inference pipeline produces an :class:`AuditTrace` per claim. This module
lands that result in an audited copy of the sealed C-B bundle without changing
the on-disk contract shape (DECISIONS.md § 2026-06-21 § 3):

* ``claims/{claim_id}.audit-trace.json`` — the full replay-sufficient v1 trace
  (the new artifact).
* ``claims/{claim_id}.yaml`` — the existing per-claim file, with its C-B
  ``audit`` block populated so a consumer reading the C-B contract sees a
  verdict in the six-value vocabulary.

The source bundle is never mutated (it is hash-sealed); a fresh copy is always
written. ``SHA256SUMS`` + ``bundle.bundle_hash`` are resealed over the augmented
file set (`audit_config.yaml` is untouched, so its hash is not recomputed).

v1→C-B verdict crosswalk (DECISIONS.md § 2026-06-29, Phase 3 Unit 2)
--------------------------------------------------------------------
The v1 verdict is two-axis (`support_verdict` degree + `audit_flags` +
`citation_status`); the C-B ``audit_support_verdict`` is the flat six-value
field. The mapping is deterministic:

* degree maps straight across where the vocabularies coincide
  (`supported`/`partially_supported`/`unsupported`/`not_checkable`);
* `contradicted` has no C-B degree → `unsupported` (the strongest C-B negative;
  the finer "contradicted" label survives in the trace);
* an `overstated` flag on a positive degree surfaces as the C-B `overstated`
  degree (the two-axis flag collapses onto the flat axis);
* `not_checkable` stays `not_checkable` regardless of reason — v1 deliberately
  collapses the retired `needs_source` into `not_checkable`/`no_evidence`
  (`models.VerdictReason`), and § 2026-06-21 § 8 keeps the finer reason in the
  trace, not the C-B field. So v1 never emits the C-B `needs_source` degree.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from claim_audit_lab.contracts.audit_flags import is_material_deviation
from claim_audit_lab.contracts.cb_models import AuditSupportVerdict, CBClaim
from claim_audit_lab.contracts.serialization import (
    load_yaml_mapping,
    reseal_bundle,
    yaml_to_string,
)
from claim_audit_lab.v1.models import AuditTrace, Verdict

_DEGREE_TO_CB: dict[str, AuditSupportVerdict] = {
    "supported": "supported",
    "partially_supported": "partially_supported",
    "unsupported": "unsupported",
    "contradicted": "unsupported",
    "not_checkable": "not_checkable",
}


def cb_support_verdict(verdict: Verdict) -> AuditSupportVerdict:
    """Map a two-axis v1 :class:`Verdict` to the flat C-B ``audit_support_verdict``."""
    if verdict.support_verdict in ("supported", "partially_supported") and (
        "overstated" in verdict.audit_flags
    ):
        return "overstated"
    return _DEGREE_TO_CB[verdict.support_verdict]


def write_audited_bundle_v1(
    source_bundle_dir: Path,
    out_dir: Path,
    traces: dict[str, AuditTrace],
    cb_claims: list[CBClaim],
    *,
    audit_run_id: str,
    audited_at_utc: str,
) -> Path:
    """Copy ``source_bundle_dir`` to ``out_dir`` and write the v1 audit results.

    Parameters
    ----------
    traces:
        ``{claim_id: AuditTrace}`` from the v1 pipeline. Claims absent from this
        dict (retrieval seeds / unaudited) are copied as-is.
    cb_claims:
        All C-B claims, used for the scaffold-vs-verdict deviation flag.
    """
    _require_non_blank("audit_run_id", audit_run_id)
    _require_non_blank("audited_at_utc", audited_at_utc)

    source_bundle_dir = source_bundle_dir.resolve()
    out_dir = out_dir.resolve()
    _guard_output_location(source_bundle_dir, out_dir)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(source_bundle_dir, out_dir)

    claims_out_dir = out_dir / "claims"
    for cb_claim in cb_claims:
        trace = traces.get(cb_claim.claim_id)
        if trace is None:
            continue  # retrieval_seed or unaudited claim — leave file as-is

        claim_path = claims_out_dir / f"{cb_claim.claim_id}.yaml"
        if not claim_path.exists():
            raise FileNotFoundError(f"Missing copied C-B claim file: {claim_path}")

        trace_path = claims_out_dir / f"{cb_claim.claim_id}.audit-trace.json"
        trace_path.write_text(trace.model_dump_json(indent=2) + "\n", encoding="utf-8")

        raw = load_yaml_mapping(claim_path)
        raw.setdefault("audit", {})
        raw["audit"].update(
            _cb_audit_block(
                trace,
                cb_claim,
                audit_run_id=audit_run_id,
                audited_at_utc=audited_at_utc,
            )
        )
        claim_path.write_text(yaml_to_string(raw), encoding="utf-8")

    reseal_bundle(out_dir)
    return out_dir


def _cb_audit_block(
    trace: AuditTrace,
    cb_claim: CBClaim,
    *,
    audit_run_id: str,
    audited_at_utc: str,
) -> dict[str, object]:
    verdict = trace.verdict
    cb_verdict = cb_support_verdict(verdict)
    deviation = is_material_deviation(cb_claim.scaffold_support_status, cb_verdict)
    context = (
        f"scaffold_support_status={cb_claim.scaffold_support_status}; "
        f"audit_support_verdict={cb_verdict}"
    )
    if deviation:
        deviation_notes = f"Material disagreement: {context}."
    else:
        deviation_notes = (
            f"No material disagreement between scaffold support status and CAL verdict: {context}."
        )
    return {
        "audit_run_id": audit_run_id,
        "audited_at_utc": audited_at_utc,
        "audit_support_verdict": cb_verdict,
        "audit_confidence": trace.support_signal.max_entailment_score,
        "audit_notes": _audit_notes(trace),
        "false_caution_flag": "false_caution" in verdict.audit_flags,
        "deviation_flag": deviation,
        "deviation_notes": deviation_notes,
    }


def _audit_notes(trace: AuditTrace) -> str:
    verdict = trace.verdict
    reason = f" ({verdict.support_verdict_reason})" if verdict.support_verdict_reason else ""
    flags = ",".join(verdict.audit_flags) if verdict.audit_flags else "none"
    return (
        f"CAL v1 retrieve-entail: {verdict.support_verdict}{reason}; "
        f"flags={flags}; citation_status={verdict.citation_status}; "
        f"entail_signal={trace.support_signal.label}"
        f"@{trace.support_signal.max_entailment_score:.4f}; "
        f"audit_confidence={verdict.audit_confidence}. "
        f"Full trace: claims/{trace.claim_id}.audit-trace.json"
    )


def _require_non_blank(field_name: str, value: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must be non-blank")


def _guard_output_location(source_bundle_dir: Path, out_dir: Path) -> None:
    if out_dir == source_bundle_dir or out_dir.is_relative_to(source_bundle_dir):
        raise ValueError("out_dir must not be the source bundle or inside it")


__all__ = ["cb_support_verdict", "write_audited_bundle_v1"]
