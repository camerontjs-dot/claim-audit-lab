"""Command-line interface for Claim Audit Lab."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from claim_audit_lab.auditor import audit_document
from claim_audit_lab.loader import LoaderError, load_draft, load_evidence_bundle
from claim_audit_lab.models import AuditReport
from claim_audit_lab.report import render_json_report, render_markdown_report

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DEMO_DRAFT = PROJECT_ROOT / "examples" / "drafts" / "ai-research-note.md"
DEFAULT_DEMO_EVIDENCE = PROJECT_ROOT / "examples" / "evidence" / "ai-research-evidence.yml"
DEFAULT_DEMO_OUT_DIR = PROJECT_ROOT / "build" / "reports"
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
        report = _run_audit(DEFAULT_DEMO_DRAFT, DEFAULT_DEMO_EVIDENCE)
    except LoaderError as exc:
        _exit_with_loader_error(exc)

    markdown_out = out_dir / f"{DEMO_STEM}.md"
    json_out = out_dir / f"{DEMO_STEM}.json"

    _write_text(markdown_out, render_markdown_report(report))
    _write_text(json_out, render_json_report(report))

    typer.echo(f"Wrote Markdown report: {markdown_out}")
    typer.echo(f"Wrote JSON report: {json_out}")
    typer.echo(_format_summary(report))


def _run_audit(draft_path: Path, evidence_path: Path) -> AuditReport:
    draft = load_draft(draft_path)
    evidence_bundle = load_evidence_bundle(evidence_path)
    return audit_document(draft, evidence_bundle)


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
        f"{summary.not_audit_ready_claims} not audit-ready",
    ]
    if report.evidence_bundle_warnings:
        parts.append(f"{len(report.evidence_bundle_warnings)} evidence bundle warnings")
    return "; ".join(parts) + "."


def _exit_with_loader_error(error: LoaderError) -> None:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
