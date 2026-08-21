"""Self-contained HTML audit reports.

The HTML report is the human-readable deliverable — the surface handed to a
reviewer or a client. It is deliberately *one file*: the stylesheet is inlined
from package data, there are no scripts, and nothing is fetched at view time. A
report that needs a network to render correctly is a report that renders
differently a year from now.

**PDF** is the browser's print dialog over this file. `assets/report.css` carries
an ``@media print`` block that forces a light sheet, keeps a claim off a page
break, and expands link targets. That keeps CAL free of a PDF toolchain, and it
keeps the artifact honest: a PDF writer would stamp ``/CreationDate`` and
``/ID`` into every run, so a generated PDF could not be byte-reproducible even
though the audit that produced it is.

**Determinism.** Nothing here reads the clock. ``run_id`` and ``audited_at`` are
passed in by the caller or omitted entirely, so rendering the same audit twice
produces byte-identical HTML.

**Provenance is not optional.** Every report states the engine, the rules
version, the rules-file SHA, the audit-config hash, and the library version. A
report that cannot say what produced it is not evidence of anything, and this is
the surface most likely to be read by someone who never opens the README — which
is also why the status band is the first thing under the title.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from claim_audit_lab.models import AuditReport
from claim_audit_lab.resources import read_package_text

if TYPE_CHECKING:
    # v1.models pulls the inference stack at import time; the v0.2 path must not
    # load torch just to render a report.
    from claim_audit_lab.v1.models import AuditTrace

_STYLESHEET_RESOURCE = "assets/report.css"

_STATUS_BAND = (
    "<strong>Engineering build. Mechanisms verified, accuracy not validated.</strong>",
    "This report audits whether the <em>supplied</em> evidence carries each claim. It does "
    "not assess whether a claim is true of the world, and it does not search for evidence "
    "that was not supplied.",
    "Not validated software. Not a GxP capability claim. Not a tagged <code>v1.0.0</code> "
    "release. Verdicts are review inputs; a human disposes consequential claims.",
)

# Ordered so the register reads worst-first; a reviewer's attention should land on
# the adverse verdicts before the clean ones.
_VERDICT_ORDER = (
    "contradicted",
    "unsupported",
    "overstated",
    "needs_source",
    "partially_supported",
    "not_checkable",
    "supported",
)


@dataclass(frozen=True)
class ReportProvenance:
    """What produced a report. Every field is printed; none is inferred at render time."""

    engine: str
    rules_version: str
    library_version: str
    rules_file_sha: str | None = None
    audit_config_hash: str | None = None
    document_id: str | None = None
    run_id: str | None = None
    audited_at_utc: str | None = None
    extra: dict[str, str] = field(default_factory=dict)

    def rows(self) -> list[tuple[str, str]]:
        """Provenance as label/value pairs, skipping what the caller did not supply."""
        pairs: list[tuple[str, str | None]] = [
            ("document", self.document_id),
            ("engine", self.engine),
            ("rules version", self.rules_version),
            ("rules file sha256", self.rules_file_sha),
            ("audit config hash", self.audit_config_hash),
            ("library version", self.library_version),
            ("audit run id", self.run_id),
            ("audited at (UTC)", self.audited_at_utc),
        ]
        pairs.extend((k, v) for k, v in sorted(self.extra.items()))
        return [(label, value) for label, value in pairs if value]


def render_v1_html_report(
    document_id: str,
    traces: list[AuditTrace],
    provenance: ReportProvenance,
    *,
    limits: list[str] | None = None,
) -> str:
    """Render the v1 retrieve→entail engine's traces as a standalone HTML report."""
    counts = _verdict_counts(traces)
    body: list[str] = [
        _title_block(document_id, "retrieve → entail → rules over supplied evidence"),
        _status_band(),
        _pins(provenance),
        "<h2>Executive summary</h2>",
        _summary_list(len(traces), counts),
    ]

    if not traces:
        body.append("<p>No claims were extracted from the draft.</p>")
    else:
        body.append("<h2>Claim register</h2>")
        body.append(_v1_register(traces))
        body.append("<h2>Claim details</h2>")
        body.extend(_v1_claim_card(trace) for trace in traces)

    body.append("<h2>Known limits</h2>")
    body.append(_limits_list(limits if limits is not None else []))
    body.append(_footer(provenance))
    return _document(f"Claim audit: {document_id}", body)


def render_html_report(report: AuditReport, provenance: ReportProvenance | None = None) -> str:
    """Render a v0.2 ``AuditReport`` as a standalone HTML report.

    ``provenance`` is optional only because ``AuditReport`` predates it. Callers on
    the v0.2 path should supply it; a report rendered without it says so rather
    than quietly omitting the question.
    """
    summary = report.summary
    counts = {
        "supported": summary.supported_claims,
        "partially_supported": summary.partially_supported_claims,
        "unsupported": summary.unsupported_claims,
        "not_checkable": summary.not_checkable_claims,
        "overstated": summary.overstated_claims,
        "needs_source": summary.needs_source_claims,
    }
    body: list[str] = [
        _title_block(report.document_id, "deterministic supplied-evidence rules"),
        _status_band(),
    ]
    if provenance is not None:
        body.append(_pins(provenance))
    else:
        body.append(
            '<div class="status-band"><p><strong>Provenance not recorded.</strong> '
            "This report does not state which engine or configuration produced it, so it "
            "cannot be used as evidence of a particular run.</p></div>"
        )
    body.extend(
        [
            "<h2>Executive summary</h2>",
            _summary_list(summary.total_claims, counts),
        ]
    )

    if report.evidence_bundle_warnings:
        body.append("<h2>Evidence bundle warnings</h2>")
        body.append(_bullets(report.evidence_bundle_warnings))

    if report.claims:
        body.append("<h2>Claim register</h2>")
        body.append(_v02_register(report))

    body.append("<h2>Limitations</h2>")
    body.append(_bullets(report.limitations))
    body.append(_footer(provenance))
    return _document(f"Claim audit: {report.document_id}", body)


# --- shared shell -----------------------------------------------------------


def _document(title: str, body: list[str]) -> str:
    css = read_package_text(_STYLESHEET_RESOURCE)
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_esc(title)}</title>\n"
        f"<style>\n{css}</style>\n"
        "</head>\n"
        "<body>\n"
        '<div class="wrap">\n' + "\n".join(body) + "\n</div>\n"
        "</body>\n"
        "</html>\n"
    )


def _title_block(document_id: str, method: str) -> str:
    return (
        f"<h1>Claim Audit Lab report: <code>{_esc(document_id)}</code></h1>\n"
        f'<p class="subtitle">Generated by Claim Audit Lab using {_esc(method)}.</p>'
    )


def _status_band() -> str:
    paragraphs = "\n".join(f"<p>{p}</p>" for p in _STATUS_BAND)
    return f'<div class="status-band">\n{paragraphs}\n</div>'


def _pins(provenance: ReportProvenance) -> str:
    rows = "\n".join(
        f"<dt>{_esc(label)}</dt><dd>{_esc(value)}</dd>" for label, value in provenance.rows()
    )
    return f'<dl class="pins">\n{rows}\n</dl>'


def _summary_list(total: int, counts: dict[str, int]) -> str:
    items = [f"<li><b>{total}</b> claims assessed</li>"]
    for verdict in _VERDICT_ORDER:
        if verdict in counts:
            items.append(
                f'<li><span class="pill {_esc(verdict)}">{_esc(verdict)}</span> '
                f"<b>{counts[verdict]}</b></li>"
            )
    return '<ul class="summary-grid">\n' + "\n".join(items) + "\n</ul>"


def _limits_list(limits: list[str]) -> str:
    if not limits:
        return "<p>None recorded.</p>"
    return '<ul class="limits">\n' + "\n".join(f"<li>{_inline(x)}</li>" for x in limits) + "\n</ul>"


def _bullets(items: list[str]) -> str:
    if not items:
        return "<p>None recorded.</p>"
    return '<ul class="limits">\n' + "\n".join(f"<li>{_inline(x)}</li>" for x in items) + "\n</ul>"


def _footer(provenance: ReportProvenance | None) -> str:
    tail = ""
    if provenance is not None:
        tail = (
            f" Engine <code>{_esc(provenance.engine)}</code>, rules "
            f"<code>{_esc(provenance.rules_version)}</code>."
        )
    return (
        "<footer>Claim Audit Lab, supplied-evidence claim audit. Engineering build; "
        "not validated software and not a GxP capability claim." + tail + "</footer>"
    )


# --- v1 -----------------------------------------------------------------------


def _v1_register(traces: list[AuditTrace]) -> str:
    rows = []
    for trace in traces:
        verdict = str(trace.verdict.support_verdict)
        reason = str(trace.verdict.support_verdict_reason or "—")
        contributing = str(trace.support_signal.contributing_passage_id or "none")
        rows.append(
            "<tr>"
            f'<td class="mono">{_esc(str(trace.claim_id))}</td>'
            f'<td><span class="pill {_esc(verdict)}">{_esc(verdict)}</span></td>'
            f'<td class="mono">{_esc(reason)}</td>'
            f'<td class="mono">{_esc(str(trace.verdict.audit_confidence))}</td>'
            f'<td class="mono">{_esc(contributing)}</td>'
            "</tr>"
        )
    head = (
        "<tr><th>Claim ID</th><th>Support</th><th>Reason</th>"
        "<th>Confidence</th><th>Contributing passage</th></tr>"
    )
    return (
        '<div class="table-scroll"><table>\n<thead>'
        + head
        + "</thead>\n<tbody>\n"
        + "\n".join(rows)
        + "\n</tbody>\n</table></div>"
    )


def _v1_claim_card(trace: AuditTrace) -> str:
    verdict = str(trace.verdict.support_verdict)
    reason = str(trace.verdict.support_verdict_reason or "—")
    fired = ", ".join(f"<code>{_esc(str(r.rule_id))}</code>" for r in trace.rules_fired) or "none"
    contributing = str(trace.support_signal.contributing_passage_id or "none")
    admitted = len(trace.entailment)
    meta = [
        ("support", f'<span class="pill {_esc(verdict)}">{_esc(verdict)}</span>'),
        ("reason", f"<code>{_esc(reason)}</code>"),
        ("confidence", _esc(str(trace.verdict.audit_confidence))),
        ("contributing passage", f"<code>{_esc(contributing)}</code>"),
        ("passages entailed", str(admitted)),
        ("rules fired", fired),
    ]
    rows = "\n".join(f"<dt>{_esc(k)}</dt><dd>{v}</dd>" for k, v in meta)
    return (
        f'<div class="claim {_esc(verdict)}">\n'
        f"<h3>{_esc(str(trace.claim_id))}</h3>\n"
        f'<div class="claim-text">{_esc(str(trace.claim_text))}</div>\n'
        f'<dl class="claim-meta">\n{rows}\n</dl>\n'
        "</div>"
    )


# --- v0.2 ---------------------------------------------------------------------


def _v02_register(report: AuditReport) -> str:
    rows = []
    for assessment in report.claims:
        verdict = str(assessment.support_label)
        signal = (
            f"{assessment.support_signal:.2f}" if assessment.support_signal is not None else "—"
        )
        rows.append(
            "<tr>"
            f'<td class="mono">{_esc(str(assessment.claim.id))}</td>'
            f'<td><span class="pill {_esc(verdict)}">{_esc(verdict)}</span></td>'
            f'<td class="mono">{_esc(str(assessment.risk_label))}</td>'
            f'<td class="mono">{_esc(signal)}</td>'
            f'<td class="mono">{len(assessment.candidate_evidence)}</td>'
            "</tr>"
        )
    head = (
        "<tr><th>Claim ID</th><th>Support</th><th>Risk</th><th>Signal</th><th>Candidates</th></tr>"
    )
    return (
        '<div class="table-scroll"><table>\n<thead>'
        + head
        + "</thead>\n<tbody>\n"
        + "\n".join(rows)
        + "\n</tbody>\n</table></div>"
    )


def _verdict_counts(traces: list[AuditTrace]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for trace in traces:
        verdict = str(trace.verdict.support_verdict)
        counts[verdict] = counts.get(verdict, 0) + 1
    return counts


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _inline(value: str) -> str:
    """Escape, then promote Markdown backtick spans to ``<code>``.

    The limits and limitation strings are authored once and rendered into both
    Markdown and HTML. Without this the HTML shows literal backticks, which is how
    a shared source list usually announces that it was written for one format and
    reused in the other. Escaping happens first, so nothing inside a span can
    close a tag.
    """
    escaped = _esc(value)
    parts = escaped.split("`")
    if len(parts) % 2 == 0:  # unbalanced backticks — leave the text alone
        return escaped
    return "".join(
        part if index % 2 == 0 else f"<code>{part}</code>" for index, part in enumerate(parts)
    )


__all__ = ["ReportProvenance", "render_html_report", "render_v1_html_report"]
