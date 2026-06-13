"""Command-line interface for Claim Audit Lab."""

from __future__ import annotations

from contextlib import ExitStack
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import typer

from claim_audit_lab.auditor import _build_assessments, audit_document
from claim_audit_lab.contracts.adapter import adapt_bundle_to_pipeline
from claim_audit_lab.contracts.bundle_loader import BundleIntegrityError, load_bundle
from claim_audit_lab.contracts.output_writer import write_audited_bundle
from claim_audit_lab.evidence_matching import match_claims_to_evidence
from claim_audit_lab.loader import LoaderError, load_draft, load_evidence_bundle
from claim_audit_lab.models import AuditReport, ClaimAssessment
from claim_audit_lab.report import render_json_report, render_markdown_report
from claim_audit_lab.resources import PackageResourceError, package_file

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
) -> None:
    """Audit a locked C-B evidence bundle and write an audited copy."""
    deviations_dir = out_dir / "deviations"
    try:
        contents = load_bundle(bundle_dir, deviations_dir=deviations_dir)
    except BundleIntegrityError as exc:
        typer.echo(f"C-B intake failed: {exc}", err=True)
        typer.echo(f"Deviation records: {deviations_dir}", err=True)
        raise typer.Exit(code=1) from exc

    cal_claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(contents)
    candidate_map = match_claims_to_evidence(cal_claims, evidence_bundle, audit_config)
    assessments = _build_assessments(cal_claims, evidence_bundle, candidate_map, audit_config)
    assessments_by_claim_id = _assessments_by_claim_id(assessments)
    output_bundle_dir = out_dir / f"{bundle_dir.name}-audited"

    write_audited_bundle(
        bundle_dir,
        output_bundle_dir,
        contents.claims,
        assessments_by_claim_id,
        audit_run_id=_new_audit_run_id(),
        audited_at_utc=_utc_now(),
        audit_config=contents.audit_config,
    )

    skipped_retrieval_seeds = sum(claim.claim_type == "retrieval_seed" for claim in contents.claims)
    typer.echo(f"Wrote audited C-B bundle: {output_bundle_dir}")
    typer.echo(
        f"{len(assessments)} claims audited; "
        f"{skipped_retrieval_seeds} retrieval seeds skipped; "
        f"output location: {output_bundle_dir}."
    )


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
