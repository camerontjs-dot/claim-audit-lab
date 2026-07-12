"""Tests for the v1→C-B writeback + verdict crosswalk (``v1.cb_writeback``).

These build :class:`AuditTrace` objects by hand so the crosswalk and writeback
are exercised without loading inference models (the CLI end-to-end path lives in
``test_cli_v1.py``).
"""

from __future__ import annotations

import json
from pathlib import Path
from shutil import copytree

import pytest

from claim_audit_lab.contracts.bundle_loader import load_bundle
from claim_audit_lab.v1.cb_writeback import cb_support_verdict, write_audited_bundle_v1
from claim_audit_lab.v1.models import (
    AuditFlag,
    AuditTrace,
    ExtractedFeatures,
    SupportSignal,
    SupportVerdict,
    Verdict,
)

CB_FIXTURE = Path(__file__).parents[1] / "fixtures" / "cb" / "evidence-bundle-minimal"


def _trace(
    *,
    claim_id: str = "clm-001",
    support_verdict: SupportVerdict = "supported",
    audit_flags: list[AuditFlag] | None = None,
    signal_label: str = "entail",
    signal_score: float = 0.93,
) -> AuditTrace:
    return AuditTrace(
        claim_id=claim_id,
        claim_text="Accelerated approval applications should include 30-day stability data.",
        retrieval=[],
        entailment=[],
        features=ExtractedFeatures(),
        support_signal=SupportSignal(
            label=signal_label,  # type: ignore[arg-type]
            max_entailment_score=signal_score,
            contributing_passage_id="src-001/pass-001",
        ),
        rules_fired=[],
        verdict=Verdict(
            support_verdict=support_verdict,
            audit_flags=audit_flags or [],
        ),
        audit_config_hash="sha256:" + "a" * 64,
        library_version="test",
    )


@pytest.mark.parametrize(
    ("support_verdict", "flags", "expected"),
    [
        ("supported", [], "supported"),
        ("supported", ["overstated"], "overstated"),
        ("partially_supported", [], "partially_supported"),
        ("partially_supported", ["overstated"], "overstated"),
        ("unsupported", [], "unsupported"),
        ("contradicted", [], "unsupported"),
        ("not_checkable", [], "not_checkable"),
        # overstated only collapses a *positive* degree; it never rewrites a negative one
        ("unsupported", ["overstated"], "unsupported"),
        ("not_checkable", ["overstated"], "not_checkable"),
    ],
)
def test_cb_support_verdict_crosswalk(
    support_verdict: SupportVerdict, flags: list[AuditFlag], expected: str
) -> None:
    verdict = Verdict(support_verdict=support_verdict, audit_flags=flags)
    assert cb_support_verdict(verdict) == expected


def test_writeback_emits_trace_and_populates_yaml_and_reloads(tmp_path: Path) -> None:
    source = tmp_path / "evidence-bundle-minimal"
    copytree(CB_FIXTURE, source)
    contents = load_bundle(source, deviations_dir=tmp_path / "src-dev")
    out_dir = tmp_path / "audited"

    write_audited_bundle_v1(
        source,
        out_dir,
        {"clm-001": _trace()},
        contents.claims,
        audit_run_id="cal-v1-run",
        audited_at_utc="2026-06-29T00:00:00Z",
    )

    # the new replay-sufficient artifact, round-trippable back to an AuditTrace
    trace_path = out_dir / "claims" / "clm-001.audit-trace.json"
    assert trace_path.exists()
    reparsed = AuditTrace.model_validate(json.loads(trace_path.read_text()))
    assert reparsed.verdict.support_verdict == "supported"

    # the audited copy still loads through the fail-closed C-B loader (resealed)
    reloaded = load_bundle(out_dir, deviations_dir=tmp_path / "out-dev")
    audited = reloaded.claims[0].audit
    assert audited.audit_run_id == "cal-v1-run"
    assert audited.audit_support_verdict == "supported"
    assert audited.audit_confidence == pytest.approx(0.93)
    assert "claims/clm-001.audit-trace.json" in (audited.audit_notes or "")

    # the source bundle is never mutated
    assert contents.claims[0].audit.audit_run_id is None


def test_writeback_flags_material_deviation(tmp_path: Path) -> None:
    source = tmp_path / "evidence-bundle-minimal"
    copytree(CB_FIXTURE, source)
    contents = load_bundle(source, deviations_dir=tmp_path / "src-dev")
    out_dir = tmp_path / "audited"

    # fixture claim is scaffold_support_status=sourced; an unsupported verdict is a
    # material disagreement per the shared _MATERIAL_DISAGREE set
    write_audited_bundle_v1(
        source,
        out_dir,
        {"clm-001": _trace(support_verdict="unsupported", signal_label="neutral")},
        contents.claims,
        audit_run_id="cal-v1-run",
        audited_at_utc="2026-06-29T00:00:00Z",
    )

    reloaded = load_bundle(out_dir, deviations_dir=tmp_path / "out-dev")
    audited = reloaded.claims[0].audit
    assert audited.audit_support_verdict == "unsupported"
    assert audited.deviation_flag is True
    assert "Material disagreement" in (audited.deviation_notes or "")


def test_writeback_leaves_unaudited_claims_untouched(tmp_path: Path) -> None:
    source = tmp_path / "evidence-bundle-minimal"
    copytree(CB_FIXTURE, source)
    contents = load_bundle(source, deviations_dir=tmp_path / "src-dev")
    out_dir = tmp_path / "audited"

    # no trace for clm-001 → its YAML audit block stays null, no trace file written
    write_audited_bundle_v1(
        source,
        out_dir,
        {},
        contents.claims,
        audit_run_id="cal-v1-run",
        audited_at_utc="2026-06-29T00:00:00Z",
    )

    assert not (out_dir / "claims" / "clm-001.audit-trace.json").exists()
    reloaded = load_bundle(out_dir, deviations_dir=tmp_path / "out-dev")
    assert reloaded.claims[0].audit.audit_support_verdict is None


def test_writeback_rejects_blank_run_metadata(tmp_path: Path) -> None:
    source = tmp_path / "evidence-bundle-minimal"
    copytree(CB_FIXTURE, source)
    contents = load_bundle(source, deviations_dir=tmp_path / "src-dev")

    with pytest.raises(ValueError, match="audit_run_id must be non-blank"):
        write_audited_bundle_v1(
            source,
            tmp_path / "audited",
            {"clm-001": _trace()},
            contents.claims,
            audit_run_id="   ",
            audited_at_utc="2026-06-29T00:00:00Z",
        )


def test_writeback_rejects_output_inside_source(tmp_path: Path) -> None:
    source = tmp_path / "evidence-bundle-minimal"
    copytree(CB_FIXTURE, source)
    contents = load_bundle(source, deviations_dir=tmp_path / "src-dev")

    with pytest.raises(ValueError, match="out_dir must not be"):
        write_audited_bundle_v1(
            source,
            source / "nested-audited",
            {"clm-001": _trace()},
            contents.claims,
            audit_run_id="cal-v1-run",
            audited_at_utc="2026-06-29T00:00:00Z",
        )
