"""Command-line interface for Claim Audit Lab."""

from __future__ import annotations

import json
from collections import Counter
from contextlib import ExitStack
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, NoReturn
from uuid import uuid4

import typer

from claim_audit_lab import __version__
from claim_audit_lab.auditor import audit_claims, audit_document, build_audit_report
from claim_audit_lab.claim_extraction import extract_claims
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
from claim_audit_lab.models import AuditReport, ClaimAssessment, EvidenceBundle
from claim_audit_lab.policy import AuditPolicy
from claim_audit_lab.report import render_json_report, render_markdown_report
from claim_audit_lab.report_html import (
    ReportProvenance,
    render_html_report,
    render_v1_html_report,
)
from claim_audit_lab.resources import PackageResourceError, package_file

if TYPE_CHECKING:
    from claim_audit_lab.v1.explanation import Explanation
    from claim_audit_lab.v1.models import AuditTrace, Passage

DEFAULT_DEMO_DRAFT = "examples/drafts/ai-research-note.md"
DEFAULT_DEMO_EVIDENCE = "examples/evidence/ai-research-evidence.yml"
DEFAULT_DEMO_OUT_DIR = Path("build") / "reports"
DEMO_STEM = "ai-research-note.cli"
ENGINE_V1 = "v1-retrieve-entail"
ENGINE_V02 = "v0.2-lexical"
DEFAULT_ENGINE = ENGINE_V1
# Literal, not imported from v1.config: importing claim_audit_lab.v1 pulls spaCy.
RULES_VERSION_V1 = "cal-rules-v1.13.0"
_VALID_ENGINES = (ENGINE_V1, ENGINE_V02)
_ENGINE_OPTION_HELP = (
    "Audit engine. Default is v1-retrieve-entail (retrieve → entail → rules). "
    "Pass v0.2-lexical to run the retired lexical matcher."
)

app = typer.Typer(
    help="Audit whether draft claims are supported by supplied evidence.",
    no_args_is_help=True,
    # Keep CLI help on Click's plain formatter. Rich's optional formatter has
    # changed help rendering across Click releases, while this public CLI's
    # help text is itself a tested compatibility surface.
    rich_markup_mode=None,
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
    html_out: Annotated[
        Path | None,
        typer.Option(
            "--html-out",
            help=(
                "Optional standalone HTML report output path. This is the human-readable "
                "deliverable; print it from a browser for PDF."
            ),
        ),
    ] = None,
    engine: Annotated[
        str,
        typer.Option("--engine", help=_ENGINE_OPTION_HELP),
    ] = DEFAULT_ENGINE,
) -> None:
    """Audit a draft against a supplied evidence bundle."""
    selected = _parse_engine(engine)
    if selected == ENGINE_V1:
        try:
            document_id, traces = _run_v1_audit(draft, evidence)
        except LoaderError as exc:
            _exit_with_loader_error(exc)
        _write_text(out, _render_v1_markdown(document_id, traces))
        typer.echo(f"Wrote Markdown report: {out}")
        if json_out is not None:
            _write_text(json_out, _render_v1_json(document_id, traces))
            typer.echo(f"Wrote JSON report: {json_out}")
        if html_out is not None:
            _write_text(html_out, _render_v1_html(document_id, traces))
            typer.echo(f"Wrote HTML report: {html_out}")
        typer.echo(_format_v1_summary(traces))
        return

    try:
        report = _run_audit(draft, evidence)
    except LoaderError as exc:
        _exit_with_loader_error(exc)

    _write_text(out, render_markdown_report(report))
    typer.echo(f"Wrote Markdown report: {out}")

    if json_out is not None:
        _write_text(json_out, render_json_report(report))
        typer.echo(f"Wrote JSON report: {json_out}")

    if html_out is not None:
        _write_text(html_out, render_html_report(report, _v02_provenance(report.document_id)))
        typer.echo(f"Wrote HTML report: {html_out}")

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
    engine: Annotated[
        str,
        typer.Option("--engine", help=_ENGINE_OPTION_HELP),
    ] = DEFAULT_ENGINE,
) -> None:
    """Run the built-in AI research fixture demo."""
    selected = _parse_engine(engine)
    markdown_out = out_dir / f"{DEMO_STEM}.md"
    json_out_path = out_dir / f"{DEMO_STEM}.json"
    html_out_path = out_dir / f"{DEMO_STEM}.html"
    try:
        with ExitStack() as stack:
            draft_path = stack.enter_context(package_file(DEFAULT_DEMO_DRAFT))
            evidence_path = stack.enter_context(package_file(DEFAULT_DEMO_EVIDENCE))
            if selected == ENGINE_V1:
                document_id, traces = _run_v1_audit(draft_path, evidence_path)
                _write_text(markdown_out, _render_v1_markdown(document_id, traces))
                _write_text(json_out_path, _render_v1_json(document_id, traces))
                _write_text(html_out_path, _render_v1_html(document_id, traces))
                typer.echo(f"Wrote Markdown report: {markdown_out}")
                typer.echo(f"Wrote JSON report: {json_out_path}")
                typer.echo(f"Wrote HTML report: {html_out_path}")
                typer.echo(_format_v1_summary(traces))
                return
            report = _run_audit(draft_path, evidence_path)
    except (LoaderError, PackageResourceError) as exc:
        _exit_with_loader_error(exc)

    _write_text(markdown_out, render_markdown_report(report))
    _write_text(json_out_path, render_json_report(report))
    _write_text(html_out_path, render_html_report(report, _v02_provenance(report.document_id)))

    typer.echo(f"Wrote Markdown report: {markdown_out}")
    typer.echo(f"Wrote JSON report: {json_out_path}")
    typer.echo(f"Wrote HTML report: {html_out_path}")
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
    html_report: Annotated[
        bool,
        typer.Option(
            "--html-report/--no-html-report",
            help=(
                "Also write a standalone HTML report for human review. Off by default on "
                "the v1 path, where the audited bundle is the artifact and a report is a "
                "second copy of it; turn it on for a run someone will read."
            ),
        ),
    ] = False,
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
        _audit_bundle_v1(contents, bundle_dir, out_dir, run_id, audited_at_utc, html_report)
    else:
        _audit_bundle_v0_2(contents, bundle_dir, out_dir, run_id, audited_at_utc, html_report)


def _audit_bundle_v0_2(
    contents: BundleContents,
    bundle_dir: Path,
    out_dir: Path,
    run_id: str,
    audited_at_utc: str,
    html_report: bool = False,
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
    html_report_path = out_dir / f"{bundle_dir.name}-audit-report.html"
    if html_report:
        _write_text(
            html_report_path,
            render_html_report(
                report,
                _v02_provenance(
                    contents.manifest.bundle_id, run_id=run_id, audited_at_utc=audited_at_utc
                ),
            ),
        )

    skipped_retrieval_seeds = sum(claim.claim_type == "retrieval_seed" for claim in contents.claims)
    typer.echo(f"Wrote audited C-B bundle: {output_bundle_dir}")
    typer.echo(f"Wrote Markdown report: {report_path}")
    if html_report:
        typer.echo(f"Wrote HTML report: {html_report_path}")
    typer.echo(
        f"{len(assessments)} claims audited (engine {ENGINE_V02}); "
        f"{skipped_retrieval_seeds} retrieval seeds skipped; "
        f"output location: {output_bundle_dir}."
    )


def _audit_bundle_v1(
    contents: BundleContents,
    bundle_dir: Path,
    out_dir: Path,
    run_id: str,
    audited_at_utc: str,
    html_report: bool = False,
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

    # No report by default on this path: the audited bundle *is* the artifact, and
    # apparatus consumers read the traces. A human-readable copy is opt-in, for a run
    # someone will actually read.
    html_report_path = out_dir / f"{bundle_dir.name}-audit-report.html"
    if html_report:
        ordered = [traces[request.claim_id] for request in requests]
        _write_text(
            html_report_path,
            _render_v1_html(
                contents.manifest.bundle_id,
                ordered,
                run_id=run_id,
                audited_at_utc=audited_at_utc,
            ),
        )

    skipped = sum(claim.claim_type != "extracted_claim" for claim in contents.claims)
    typer.echo(f"Wrote audited C-B bundle: {output_bundle_dir}")
    if html_report:
        typer.echo(f"Wrote HTML report: {html_report_path}")
    typer.echo(
        f"{len(traces)} claims audited (engine {ENGINE_V1}, rules {RULES_VERSION_V1}); "
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


@app.command()
def explain(
    traces_dir: Annotated[
        Path,
        typer.Argument(help="Directory of per-claim AuditTrace JSON files to explain."),
    ],
    out_dir: Annotated[
        Path,
        typer.Option("--out-dir", help="Directory for explanations.json and explanations.md."),
    ] = Path("build") / "explanations",
    signal_floor: Annotated[
        float,
        typer.Option(
            "--signal-floor",
            help="Support-signal floor separating read-silent from ambiguous-support.",
        ),
    ] = 0.20,
    source_boundary: Annotated[
        str | None,
        typer.Option(
            "--source-boundary",
            help=(
                "How completely the bundle covers its source: exhaustive, bounded, or "
                "named_missing_material. Declaring it says whether an abstention on an "
                "absence claim is a miss or the correct answer. Omitted means undeclared."
            ),
        ),
    ] = None,
) -> None:
    """Name the reason behind every recorded verdict, especially the abstentions.

    Read-only. This re-reads traces CAL already wrote and reports what each
    verdict means and what a reviewer should do next; it runs no model and
    re-decides nothing. Traces predating the support-signal instrumentation are
    handled by recovering the logit slot mapping from the corpus itself.
    """
    from claim_audit_lab.v1.explanation import explain as explain_trace
    from claim_audit_lab.v1.explanation import recover_logit_slots
    from claim_audit_lab.v1.models import AuditTrace as _AuditTrace

    trace_paths = sorted(traces_dir.glob("*.json"))
    if not trace_paths:
        typer.echo(f"explain: no trace JSON found in {traces_dir}", err=True)
        raise typer.Exit(code=2)

    traces: list[_AuditTrace] = []
    for path in trace_paths:
        try:
            traces.append(_AuditTrace.model_validate_json(path.read_text(encoding="utf-8")))
        except ValueError as exc:
            typer.echo(f"explain: malformed trace {path.name}: {exc}", err=True)
            raise typer.Exit(code=2) from exc

    # Pre-instrumentation corpora carry raw_logits but no p_entail; recovering the
    # slot mapping once per corpus is what lets those classify finer than read_silent.
    slots = recover_logit_slots(traces)

    valid_boundaries = ("exhaustive", "bounded", "named_missing_material")
    if source_boundary is not None and source_boundary not in valid_boundaries:
        typer.echo(
            f"explain: --source-boundary must be one of {', '.join(valid_boundaries)}",
            err=True,
        )
        raise typer.Exit(code=2)

    explanations = [
        explain_trace(
            t,
            signal_floor=signal_floor,
            logit_slots=slots,
            source_boundary=source_boundary,  # type: ignore[arg-type]
        )
        for t in traces
    ]

    out_dir.mkdir(parents=True, exist_ok=True)
    payload = [e.model_dump(mode="json") for e in explanations]
    _write_text(out_dir / "explanations.json", json.dumps(payload, indent=2, sort_keys=True) + "\n")
    _write_text(out_dir / "explanations.md", _render_explanations(explanations, traces_dir, slots))

    verdicts = Counter(e.verdict for e in explanations)
    classes = Counter(e.abstention_class for e in explanations if e.abstention_class)
    n_abstain = sum(1 for e in explanations if e.abstention_class)

    typer.echo(f"Explained {len(explanations)} traces from {traces_dir}")
    typer.echo(f"Logit slots: {'recovered' if slots else 'not recoverable; classes limited'}")
    typer.echo(f"Source boundary: {source_boundary or 'undeclared; no absence reasoning licensed'}")
    typer.echo("Verdicts:")
    for verdict, count in verdicts.most_common():
        typer.echo(f"  {count:>4}  {verdict}")
    if n_abstain:
        pct = 100.0 * n_abstain / len(explanations)
        typer.echo(f"Abstentions: {n_abstain}/{len(explanations)} ({pct:.1f}%)")
        for name, count in classes.most_common():
            typer.echo(f"  {count:>4}  {name}")
    typer.echo(f"Wrote: {out_dir / 'explanations.json'}, {out_dir / 'explanations.md'}")


def _render_explanations(
    explanations: list[Explanation],
    traces_dir: Path,
    slots: object | None,
) -> str:
    """Render a reviewer-facing Markdown account of every explained verdict."""
    verdicts = Counter(e.verdict for e in explanations)
    classes = Counter(e.abstention_class for e in explanations if e.abstention_class)
    n = len(explanations)

    lines = [
        "# Claim Audit Lab: verdict explanations",
        "",
        f"Source traces: `{traces_dir}`  ",
        f"Claims explained: {n}  ",
        f"Logit slots: {'recovered from corpus' if slots else 'not recoverable'}",
        "",
        "Read-only. Every line below is a reading of a verdict CAL already recorded.",
        "No model was run and no verdict was re-decided.",
        "",
        "## Verdict distribution",
        "",
        "| Verdict | n | % |",
        "| --- | ---: | ---: |",
    ]
    for verdict, count in verdicts.most_common():
        lines.append(f"| `{verdict}` | {count} | {100.0 * count / n:.1f}% |")

    if classes:
        n_abstain = sum(classes.values())
        lines += [
            "",
            "## Why it abstained",
            "",
            f"{n_abstain} of {n} claims ({100.0 * n_abstain / n:.1f}%) returned an abstaining",
            "verdict. These are the named reasons, not one undifferentiated bucket.",
            "",
            "| Reason | n | % of abstentions |",
            "| --- | ---: | ---: |",
        ]
        for name, count in classes.most_common():
            lines.append(f"| `{name}` | {count} | {100.0 * count / n_abstain:.1f}% |")

    lines += ["", "## Per-claim", ""]
    for e in explanations:
        lines.append(f"### `{e.claim_id}`: `{e.verdict}`")
        lines.append("")
        lines.append(f"{e.detail}")
        lines.append("")
        if e.abstention_class:
            lines.append(f"- **Reason:** `{e.abstention_class}`")
        if e.next_step:
            lines.append(f"- **Next step:** {e.next_step}")
        if e.audit_flags:
            lines.append(f"- **Flags:** {', '.join(f'`{f}`' for f in e.audit_flags)}")
        for provenance in e.rule_provenance:
            lines.append(f"- **Rule:** `{provenance}`")
        lines.append("")
    return "\n".join(lines)


def _write_traces(traces_out: Path, traces: dict[str, AuditTrace]) -> None:
    """Write one deterministic ``{claim_id}.json`` trace per audited claim."""
    traces_out.mkdir(parents=True, exist_ok=True)
    for claim_id in sorted(traces):
        trace_path = traces_out / f"{claim_id}.json"
        trace_path.write_text(traces[claim_id].model_dump_json(indent=2) + "\n", encoding="utf-8")


def _parse_engine(engine: str) -> str:
    selected = engine.strip()
    if selected not in _VALID_ENGINES:
        typer.echo(
            f"--engine must be {' or '.join(_VALID_ENGINES)}, got {engine!r}.",
            err=True,
        )
        raise typer.Exit(code=2)
    return selected


def _run_audit(draft_path: Path, evidence_path: Path) -> AuditReport:
    draft = load_draft(draft_path)
    evidence_bundle = load_evidence_bundle(evidence_path)
    return audit_document(draft, evidence_bundle)


def _run_v1_audit(draft_path: Path, evidence_path: Path) -> tuple[str, list[AuditTrace]]:
    """Run retrieve→entail→rules over an ordinary draft plus YAML evidence bundle.

    Heavy inference imports stay here so the v0.2-lexical path never loads torch.
    """
    try:
        from claim_audit_lab.v1.config import load_default_audit_config
        from claim_audit_lab.v1.models import AuditRequest
        from claim_audit_lab.v1.runner import run_default_audit
    except ImportError as exc:
        typer.echo(
            "v1-retrieve-entail requires the [v1] extra "
            "(pip install 'claim-audit-lab[v1]' and python -m spacy download en_core_web_sm).",
            err=True,
        )
        raise typer.Exit(code=1) from exc

    draft = load_draft(draft_path)
    evidence_bundle = load_evidence_bundle(evidence_path)
    claims = extract_claims(draft)
    passages = _evidence_to_passages(evidence_bundle)
    audit_config = load_default_audit_config()
    traces = [
        run_default_audit(
            AuditRequest(
                claim_id=claim.id,
                claim_text=claim.text,
                passages=passages,
                audit_config=audit_config,
            )
        )
        for claim in claims
    ]
    return draft.id, traces


def _evidence_to_passages(bundle: EvidenceBundle) -> list[Passage]:
    from claim_audit_lab.v1.models import Passage

    passages: list[Passage] = []
    for source in bundle.sources:
        for excerpt in source.excerpts:
            meta = {"source_id": source.id, "title": source.title}
            passages.append(Passage(passage_id=excerpt.id, text=excerpt.text, source_meta=meta))
    return passages


def _render_v1_markdown(document_id: str, traces: list[AuditTrace]) -> str:
    lines = [
        f'<a id="report-{document_id}"></a>',
        "",
        f"# Claim Audit Lab report: `{document_id}`",
        "",
        "*Generated by Claim Audit Lab using retrieve → entail → rules over supplied evidence.*",
        "",
        "## Metadata",
        "",
        f"- Document ID: `{document_id}`",
        f"- Engine: `{ENGINE_V1}`",
        f"- Rules: `{RULES_VERSION_V1}`",
        "- Audit boundary: supplied-evidence support only; no outside-world assessment.",
        "- External source lookup: not used.",
        "",
        "## Executive summary",
        "",
        _format_v1_summary(traces),
        "",
        "## Claim register",
        "",
        "| Claim ID | Support | Reason | Confidence | Contributing passage |",
        "| --- | --- | --- | --- | --- |",
    ]
    if not traces:
        lines.extend(["", "No claims were extracted from the draft.", ""])
        return "\n".join(lines)

    for trace in traces:
        reason = trace.verdict.support_verdict_reason or "—"
        contributing = trace.support_signal.contributing_passage_id or "none"
        lines.append(
            "| "
            f"`{trace.claim_id}` | "
            f"`{trace.verdict.support_verdict}` | "
            f"`{reason}` | "
            f"{trace.verdict.audit_confidence} | "
            f"`{contributing}` |"
        )

    lines.extend(["", "## Claim details", ""])
    for trace in traces:
        fired = ", ".join(f"`{item.rule_id}`" for item in trace.rules_fired) or "none"
        lines.extend(
            [
                f"### `{trace.claim_id}`",
                "",
                trace.claim_text,
                "",
                f"- Support: `{trace.verdict.support_verdict}`",
                f"- Engine: `{ENGINE_V1}`",
                f"- Rules: `{RULES_VERSION_V1}`",
                f"- Rules fired: {fired}",
                "",
            ]
        )
    lines.extend(["## Known limits", ""])
    lines.extend(f"- {limit}" for limit in _v1_known_limits())
    lines.append("")
    return "\n".join(lines)


def _v1_known_limits() -> list[str]:
    """Limits printed on every v1 report, Markdown and HTML alike.

    One list, so the two renderings cannot drift. Figures here are DEV-grade and
    carry their population; see the benchmarks page for the open defect register.
    """
    return [
        f"Distribution `{_library_version()}`; engine `{ENGINE_V1}`; rules "
        f"`{RULES_VERSION_V1}`. Not a tagged v1.0.0.",
        "Not validated. Not a GxP capability. Verdicts are review inputs; "
        "a human disposes consequential claims.",
        "Retrieval floor is 0.40. The entailer does not instantiate numeric bounds (D12).",
        "Numeric comparison (D1/D4/D12) and two-hop composition are v2 operators. "
        "CAL asks; it does not invent the comparison or the join.",
        "A7 withholds a contradiction when the passage names a different site "
        "than the claim, and asks which one the claim is about.",
        "A7 reads identifiers containing a numeral: equipment IDs, SOP numbers, batch and "
        "lot codes (D14, fixed in v1.13.0; the parser used to tag them as numbers, leaving "
        "the gate blind and letting a false adverse verdict through). Identifiers that are "
        "bare digits, or split across two tokens like `Line 3`, are still not read: on those "
        "confirm the cited passage names the same entity as the claim.",
        "Open: D6 (held), D7 (must not land alone). D5 abstains on negative-existentials.",
        "A6 reads `source_boundary`. D8 conjunct-scoped A3 and D13 next-step are in this surface.",
        "`not_checkable` currently covers both 'nothing was retrieved' and 'evidence was "
        "held but could not be used'. Read the reason field; the two need different action.",
        "Construction gold (probe, failure-concentrated): 26/33 exact, remaining "
        "misses are abstentions. Constructed twin of the 50-item shape: 47/50 vs "
        "derived keys (pre-A7).",
    ]


def _library_version() -> str:
    """The declared package version — the same value the pipeline stamps on every trace.

    Deliberately ``__version__`` rather than ``importlib.metadata``: installed
    distribution metadata goes stale in an editable checkout, and a report whose
    version string depends on how the package happens to be installed is not
    byte-reproducible across environments.
    """
    return __version__


def _v02_provenance(
    document_id: str,
    *,
    run_id: str | None = None,
    audited_at_utc: str | None = None,
) -> ReportProvenance:
    """Provenance for the falsified v0.2 lexical engine, which apparatus consumers pin."""
    return ReportProvenance(
        engine=ENGINE_V02,
        rules_version=AuditPolicy().config_id,
        library_version=_library_version(),
        document_id=document_id,
        run_id=run_id,
        audited_at_utc=audited_at_utc,
        extra={
            "engine note": (
                "v0.2-lexical was falsified as a measurement instrument by blind "
                "calibration on 2026-06-18 (4/98 exact agreement). It is retained for "
                "pinned apparatus consumers, not recommended for new audits."
            )
        },
    )


def _v1_provenance(
    document_id: str,
    traces: list[AuditTrace],
    *,
    run_id: str | None = None,
    audited_at_utc: str | None = None,
) -> ReportProvenance:
    """Collect what produced this v1 run, reading pins off the traces themselves."""
    from claim_audit_lab.v1 import load_default_audit_config

    config = load_default_audit_config()
    config_hashes = {trace.audit_config_hash for trace in traces}
    # Every claim in a run shares one config. If that ever stops being true the
    # report must say so rather than print one hash and imply the rest.
    audit_config_hash = config_hashes.pop() if len(config_hashes) == 1 else None
    if config_hashes:
        audit_config_hash = "mixed; traces do not share one audit config"
    return ReportProvenance(
        engine=ENGINE_V1,
        rules_version=RULES_VERSION_V1,
        library_version=_library_version(),
        rules_file_sha=config.rules_file_sha,
        audit_config_hash=audit_config_hash,
        document_id=document_id,
        run_id=run_id,
        audited_at_utc=audited_at_utc,
    )


def _render_v1_html(
    document_id: str,
    traces: list[AuditTrace],
    *,
    run_id: str | None = None,
    audited_at_utc: str | None = None,
) -> str:
    return render_v1_html_report(
        document_id,
        traces,
        _v1_provenance(document_id, traces, run_id=run_id, audited_at_utc=audited_at_utc),
        limits=_v1_known_limits(),
    )


def _render_v1_json(document_id: str, traces: list[AuditTrace]) -> str:
    payload = {
        "document_id": document_id,
        "engine": ENGINE_V1,
        "rules_version": RULES_VERSION_V1,
        "traces": [trace.model_dump(mode="json") for trace in traces],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _format_v1_summary(traces: list[AuditTrace]) -> str:
    counts = Counter(trace.verdict.support_verdict for trace in traces)
    parts = [
        f"{len(traces)} claims assessed",
        f"engine {ENGINE_V1}",
        f"rules {RULES_VERSION_V1}",
        f"{counts.get('supported', 0)} supported",
        f"{counts.get('partially_supported', 0)} partially supported",
        f"{counts.get('unsupported', 0)} unsupported",
        f"{counts.get('contradicted', 0)} contradicted",
        f"{counts.get('not_checkable', 0)} not checkable",
    ]
    return "; ".join(parts) + "."


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


def _exit_with_loader_error(error: LoaderError | PackageResourceError) -> NoReturn:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
