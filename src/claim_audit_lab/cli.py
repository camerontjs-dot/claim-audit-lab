"""Command-line interface for Claim Audit Lab."""

from __future__ import annotations

from contextlib import ExitStack
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated
from uuid import uuid4

import typer

from claim_audit_lab.auditor import audit_claims, audit_document, build_audit_report
from claim_audit_lab.contracts.adapter import (
    adapt_bundle_to_pipeline,
    build_claim_evidence_scopes,
)
from claim_audit_lab.contracts.bundle_loader import (
    BundleContents,
    BundleIntegrityError,
    load_bundle,
)
from claim_audit_lab.contracts.output_writer import write_audited_bundle
from claim_audit_lab.loader import LoaderError, load_draft, load_evidence_bundle
from claim_audit_lab.models import AuditReport, ClaimAssessment
from claim_audit_lab.report import render_json_report, render_markdown_report
from claim_audit_lab.resources import PackageResourceError, package_file

if TYPE_CHECKING:
    from claim_audit_lab.v1.models import AuditTrace

DEFAULT_DEMO_DRAFT = "examples/drafts/ai-research-note.md"
DEFAULT_DEMO_EVIDENCE = "examples/evidence/ai-research-evidence.yml"
DEFAULT_DEMO_OUT_DIR = Path("build") / "reports"
DEMO_STEM = "ai-research-note.cli"

app = typer.Typer(
    help="Audit whether draft claims are supported by supplied evidence.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Run the Claim Audit Lab command group."""


@app.command()
def audit(
    draft: Annotated[Path, typer.Argument(help="Markdown or plain text draft to audit.")],
    evidence: Annotated[
        Path,
        typer.Option(
            "--evidence",
            help="YAML or JSON evidence bundle supplied for the audit.",
        ),
    ],
    out: Annotated[
        Path,
        typer.Option(
            "--out",
            help="Markdown report output path.",
        ),
    ],
    json_out: Annotated[
        Path | None,
        typer.Option(
            "--json-out",
            help="Optional JSON report output path.",
        ),
    ] = None,
) -> None:
    """Audit a draft against a supplied evidence bundle."""
    try:
        report = _run_audit(draft, evidence)
    except LoaderError as exc:
        _exit_with_loader_error(exc)

    _write_text(out, render_markdown_report(report))
    typer.echo(f"Wrote Markdown report: {out}")

    if json_out is not None:
        _write_text(json_out, render_json_report(report))
        typer.echo(f"Wrote JSON report: {json_out}")

    typer.echo(_format_summary(report))


@app.command()
def demo(
    out_dir: Annotated[
        Path,
        typer.Option(
            "--out-dir",
            help="Directory for generated AI research fixture reports.",
        ),
    ] = DEFAULT_DEMO_OUT_DIR,
) -> None:
    """Run the built-in AI research fixture demo."""
    try:
        with ExitStack() as stack:
            draft_path = stack.enter_context(package_file(DEFAULT_DEMO_DRAFT))
            evidence_path = stack.enter_context(package_file(DEFAULT_DEMO_EVIDENCE))
            report = _run_audit(draft_path, evidence_path)
    except (LoaderError, PackageResourceError) as exc:
        _exit_with_loader_error(exc)

    markdown_out = out_dir / f"{DEMO_STEM}.md"
    json_out = out_dir / f"{DEMO_STEM}.json"

    _write_text(markdown_out, render_markdown_report(report))
    _write_text(json_out, render_json_report(report))

    typer.echo(f"Wrote Markdown report: {markdown_out}")
    typer.echo(f"Wrote JSON report: {json_out}")
    typer.echo(_format_summary(report))


@app.command()
def audit_bundle(
    bundle_dir: Annotated[
        Path,
        typer.Argument(help="C-B evidence-bundle directory to audit."),
    ],
    out_dir: Annotated[
        Path,
        typer.Option(
            "--out-dir",
            help="Directory where the audited C-B bundle copy and deviations are written.",
        ),
    ],
    audit_run_id: Annotated[
        str | None,
        typer.Option(
            "--audit-run-id",
            help="Stable audit run ID; must be supplied with --audited-at.",
        ),
    ] = None,
    audited_at: Annotated[
        str | None,
        typer.Option(
            "--audited-at",
            help="Pinned UTC audit timestamp; must be supplied with --audit-run-id.",
        ),
    ] = None,
) -> None:
    """Audit a locked C-B evidence bundle and write an audited copy."""
    if (audit_run_id is None) != (audited_at is None):
        typer.echo(
            "--audit-run-id and --audited-at must be supplied together.",
            err=True,
        )
        raise typer.Exit(code=2)

    deviations_dir = out_dir / "deviations"
    try:
        contents = load_bundle(bundle_dir, deviations_dir=deviations_dir)
    except BundleIntegrityError as exc:
        typer.echo(f"C-B intake failed: {exc}", err=True)
        typer.echo(f"Deviation records: {deviations_dir}", err=True)
        raise typer.Exit(code=1) from exc

    run_id = audit_run_id or _new_audit_run_id()
    audited_at_utc = audited_at or _utc_now()

    if contents.audit_config.pipeline == "v1-retrieve-entail":
        _audit_bundle_v1(contents, bundle_dir, out_dir, run_id, audited_at_utc)
    else:
        _audit_bundle_v0_2(contents, bundle_dir, out_dir, run_id, audited_at_utc)


def _audit_bundle_v0_2(
    contents: BundleContents,
    bundle_dir: Path,
    out_dir: Path,
    run_id: str,
    audited_at_utc: str,
) -> None:
    """Default path: the v0.2 lexical auditor (apparatus consumers pin here)."""
    cal_claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(contents)
    assessments = audit_claims(
        cal_claims,
        evidence_bundle,
        audit_config,
        evidence_scopes=build_claim_evidence_scopes(contents),
    )
    assessments_by_claim_id = _assessments_by_claim_id(assessments)
    output_bundle_dir = out_dir / f"{bundle_dir.name}-audited"
    report = build_audit_report(contents.manifest.bundle_id, assessments, evidence_bundle)
    report_path = out_dir / f"{bundle_dir.name}-audit-report.md"

    write_audited_bundle(
        bundle_dir,
        output_bundle_dir,
        contents.claims,
        assessments_by_claim_id,
        audit_run_id=run_id,
        audited_at_utc=audited_at_utc,
        audit_config=contents.audit_config,
    )
    _write_text(report_path, render_markdown_report(report))

    skipped_retrieval_seeds = sum(claim.claim_type == "retrieval_seed" for claim in contents.claims)
    typer.echo(f"Wrote audited C-B bundle: {output_bundle_dir}")
    typer.echo(f"Wrote Markdown report: {report_path}")
    typer.echo(
        f"{len(assessments)} claims audited; "
        f"{skipped_retrieval_seeds} retrieval seeds skipped; "
        f"output location: {output_bundle_dir}."
    )


def _audit_bundle_v1(
    contents: BundleContents,
    bundle_dir: Path,
    out_dir: Path,
    run_id: str,
    audited_at_utc: str,
) -> None:
    """v1 retrieve→entail path. Selected by ``audit_config.pipeline``.

    Heavy inference imports are local so the v0.2 path never loads torch.
    """
    from claim_audit_lab.v1 import bundle_to_requests, load_default_audit_config
    from claim_audit_lab.v1.cb_writeback import write_audited_bundle_v1
    from claim_audit_lab.v1.runner import run_default_audit

    requests = bundle_to_requests(contents, load_default_audit_config())
    traces = {request.claim_id: run_default_audit(request) for request in requests}

    output_bundle_dir = out_dir / f"{bundle_dir.name}-audited"
    write_audited_bundle_v1(
        bundle_dir,
        output_bundle_dir,
        traces,
        contents.claims,
        audit_run_id=run_id,
        audited_at_utc=audited_at_utc,
    )

    skipped = sum(claim.claim_type != "extracted_claim" for claim in contents.claims)
    typer.echo(f"Wrote audited C-B bundle: {output_bundle_dir}")
    typer.echo(
        f"{len(traces)} claims audited (v1 retrieve-entail); "
        f"{skipped} non-auditable claims skipped; "
        f"output location: {output_bundle_dir}."
    )


@app.command()
def calibrate(
    packet: Annotated[
        Path,
        typer.Option("--packet", help="Directory whose subdirectories are C-B bundles to audit."),
    ],
    gold: Annotated[
        Path,
        typer.Option("--gold", help="Calibration gold YAML scored against the v1 verdicts."),
    ],
    config: Annotated[
        Path,
        typer.Option("--config", help="Operational audit_config YAML (thresholds from rules)."),
    ],
    out: Annotated[
        Path,
        typer.Option("--out", help="Markdown calibration-report output path."),
    ],
    traces_out: Annotated[
        Path,
        typer.Option("--traces-out", help="Directory for per-claim AuditTrace JSON."),
    ],
    pinned_at: Annotated[
        str,
        typer.Option("--pinned-at", help="Deterministic ISO timestamp stamped in the report."),
    ],
) -> None:
    """Run the v1 pipeline over a calibration packet and write a report + traces.

    Synthetic-boundary command (Phase 4 Unit 1 / B17). It does not run the sealed
    PILOT-001 gate and applies no pass/fail thresholds — it produces the
    instrument the gate later reads.
    """
    from claim_audit_lab.v1.calibrate import load_gold, render_report, run_calibration
    from claim_audit_lab.v1.config import load_audit_config

    try:
        audit_config = load_audit_config(config)
        gold_data = load_gold(gold)
    except (OSError, ValueError) as exc:
        typer.echo(f"calibrate: invalid --config or --gold: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    # Heavy inference imports are local so the v0.2 path never loads torch.
    from claim_audit_lab.v1.runner import run_default_audit

    try:
        result, traces = run_calibration(
            packet,
            gold_data,
            audit_config,
            auditor=run_default_audit,
            deviations_dir=out.parent / "deviations",
        )
    except (BundleIntegrityError, ValueError) as exc:
        typer.echo(f"calibrate: packet audit failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    _write_text(out, render_report(result, pinned_at=pinned_at))
    _write_traces(traces_out, traces)

    agreement = result.agreement
    typer.echo(f"Wrote calibration report: {out}")
    typer.echo(f"Wrote {len(traces)} traces: {traces_out}")
    typer.echo(
        f"Exact agreement {agreement.n_agree}/{agreement.n_total}; "
        f"Cohen's kappa {agreement.cohens_kappa:.4f}; "
        f"recall floor {result.recall_floor.supported}/{result.recall_floor.starved_total}."
    )


def _write_traces(traces_out: Path, traces: dict[str, AuditTrace]) -> None:
    """Write one deterministic ``{claim_id}.json`` trace per audited claim."""
    traces_out.mkdir(parents=True, exist_ok=True)
    for claim_id in sorted(traces):
        trace_path = traces_out / f"{claim_id}.json"
        trace_path.write_text(traces[claim_id].model_dump_json(indent=2) + "\n", encoding="utf-8")


def _run_audit(draft_path: Path, evidence_path: Path) -> AuditReport:
    draft = load_draft(draft_path)
    evidence_bundle = load_evidence_bundle(evidence_path)
    return audit_document(draft, evidence_bundle)


def _assessments_by_claim_id(
    assessments: list[ClaimAssessment],
) -> dict[str, ClaimAssessment]:
    return {assessment.claim.id: assessment for assessment in assessments}


def _new_audit_run_id() -> str:
    return f"cal-audit-{uuid4()}"


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _format_summary(report: AuditReport) -> str:
    summary = report.summary
    parts = [
        f"{summary.total_claims} claims assessed",
        f"{summary.high_risk_claims} high-risk",
        f"{summary.supported_claims} supported by supplied evidence",
        f"{summary.partially_supported_claims} partially supported",
        f"{summary.unsupported_claims} unsupported",
        f"{summary.overstated_claims} overstated",
        f"{summary.needs_source_claims} needing supplied source",
        f"{summary.not_checkable_claims} not checkable",
    ]
    if report.evidence_bundle_warnings:
        parts.append(f"{len(report.evidence_bundle_warnings)} evidence bundle warnings")
    return "; ".join(parts) + "."


def _exit_with_loader_error(error: LoaderError | PackageResourceError) -> None:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
