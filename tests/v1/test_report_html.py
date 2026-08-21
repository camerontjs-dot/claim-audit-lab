"""The HTML report is the client-facing artifact, so its guarantees are tested.

Four properties matter more than layout, and layout is not tested here:

* it says what produced it,
* it says what it is not,
* it renders the same bytes for the same audit, and
* it needs nothing from the network.

A report that fails any of those is not evidence of anything, however it looks.
"""

from __future__ import annotations

import re

import pytest

from claim_audit_lab.auditor import audit_document
from claim_audit_lab.loader import load_draft, load_evidence_bundle
from claim_audit_lab.report_html import (
    ReportProvenance,
    render_html_report,
    render_v1_html_report,
)
from claim_audit_lab.resources import package_file
from claim_audit_lab.v1.models import (
    AuditTrace,
    ExtractedFeatures,
    SupportSignal,
    Verdict,
)

_CONFIG_HASH = "sha256:" + "a" * 64
_RULES_SHA = "e" * 64


def _trace(
    claim_id: str = "claim-001",
    claim_text: str = "The stability study ran for 30 days.",
    support_verdict: str = "supported",
    reason: str | None = None,
) -> AuditTrace:
    return AuditTrace(
        claim_id=claim_id,
        claim_text=claim_text,
        retrieval=[],
        entailment=[],
        features=ExtractedFeatures(),
        support_signal=SupportSignal(
            label="entail",
            max_entailment_score=0.94,
            contributing_passage_id="src-001/pass-001",
        ),
        rules_fired=[],
        verdict=Verdict(
            support_verdict=support_verdict,  # type: ignore[arg-type]
            support_verdict_reason=reason,  # type: ignore[arg-type]
        ),
        audit_config_hash=_CONFIG_HASH,
        library_version="0.3.0",
    )


def _provenance() -> ReportProvenance:
    return ReportProvenance(
        engine="v1-retrieve-entail",
        rules_version="cal-rules-v1.13.0",
        library_version="0.3.0",
        rules_file_sha=_RULES_SHA,
        audit_config_hash=_CONFIG_HASH,
        document_id="doc-1",
    )


def test_report_states_every_provenance_pin() -> None:
    """A reader must be able to answer 'what produced this?' without leaving the page."""
    html = render_v1_html_report("doc-1", [_trace()], _provenance())
    for pin in (
        "v1-retrieve-entail",
        "cal-rules-v1.13.0",
        _RULES_SHA,
        _CONFIG_HASH,
        "0.3.0",
    ):
        assert pin in html, pin


def test_report_states_what_it_is_not() -> None:
    """The status band is the whole reason this surface is safe to hand to a client."""
    html = render_v1_html_report("doc-1", [_trace()], _provenance())
    assert "not validated" in html.lower()
    assert "GxP" in html
    assert "review inputs" in html


def test_rendering_is_deterministic() -> None:
    """Same audit, same bytes. Nothing here may read the clock or a random source."""
    first = render_v1_html_report("doc-1", [_trace()], _provenance())
    second = render_v1_html_report("doc-1", [_trace()], _provenance())
    assert first == second


def test_report_is_self_contained() -> None:
    """No stylesheet link, no script, no remote asset — one file that renders offline."""
    html = render_v1_html_report("doc-1", [_trace()], _provenance())
    assert "<style>" in html
    assert "<link" not in html
    assert "<script" not in html
    assert not re.search(r'(src|href)\s*=\s*"https?://', html)


def test_claim_text_is_escaped() -> None:
    """Claim text is untrusted input; it is drafted by whoever wrote the document."""
    html = render_v1_html_report(
        "doc-1",
        [_trace(claim_text='<script>alert("x")</script> & more')],
        _provenance(),
    )
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
    assert "&amp; more" in html


def test_document_id_is_escaped_in_title_and_heading() -> None:
    html = render_v1_html_report("<b>doc</b>", [_trace()], _provenance())
    assert "<b>doc</b>" not in html
    assert "&lt;b&gt;doc&lt;/b&gt;" in html


def test_limits_render_backtick_spans_as_code() -> None:
    """The limits list is authored once and rendered into Markdown and HTML both."""
    html = render_v1_html_report(
        "doc-1",
        [_trace()],
        _provenance(),
        limits=["Rules are `cal-rules-v1.13.0`."],
    )
    assert "<code>cal-rules-v1.13.0</code>" in html
    assert "`" not in html


def test_unbalanced_backticks_are_left_alone() -> None:
    """A stray backtick must not open a code span that swallows the rest of the line."""
    html = render_v1_html_report(
        "doc-1", [_trace()], _provenance(), limits=["An unmatched ` backtick."]
    )
    assert "An unmatched ` backtick." in html


def test_verdict_is_always_spelled_out_not_only_coloured() -> None:
    """Colour is an accompaniment. The report has to survive greyscale and colour blindness."""
    html = render_v1_html_report(
        "doc-1",
        [_trace(support_verdict="contradicted", reason="conflicting_evidence")],
        _provenance(),
    )
    assert ">contradicted<" in html
    assert "conflicting_evidence" in html


def test_empty_trace_list_says_so() -> None:
    html = render_v1_html_report("doc-1", [], _provenance())
    assert "No claims were extracted" in html


@pytest.mark.parametrize("verdict", ["supported", "not_checkable", "contradicted"])
def test_every_verdict_class_reaches_the_markup(verdict: str) -> None:
    html = render_v1_html_report("doc-1", [_trace(support_verdict=verdict)], _provenance())
    assert f'class="pill {verdict}"' in html
    assert f'class="claim {verdict}"' in html


def test_v02_report_without_provenance_says_it_cannot_attest() -> None:
    """A v0.2 report rendered with no pins must not look like a report that has them."""
    with (
        package_file("examples/drafts/ai-research-note.md") as draft_path,
        package_file("examples/evidence/ai-research-evidence.yml") as evidence_path,
    ):
        report = audit_document(load_draft(draft_path), load_evidence_bundle(evidence_path))

    html = render_html_report(report)
    assert "Provenance not recorded" in html
    assert "cannot be used as evidence of a particular run" in html


def test_v02_report_with_provenance_names_the_falsified_engine() -> None:
    """v0.2 is retained for pinned consumers; a report on it should not hide that."""
    with (
        package_file("examples/drafts/ai-research-note.md") as draft_path,
        package_file("examples/evidence/ai-research-evidence.yml") as evidence_path,
    ):
        report = audit_document(load_draft(draft_path), load_evidence_bundle(evidence_path))

    provenance = ReportProvenance(
        engine="v0.2-lexical",
        rules_version="cal-rules-v1.2.0",
        library_version="0.3.0",
        document_id=report.document_id,
        extra={"engine note": "falsified as a measurement instrument"},
    )
    html = render_html_report(report, provenance)
    assert "Provenance not recorded" not in html
    assert "v0.2-lexical" in html
    assert "falsified" in html


def test_provenance_omits_fields_the_caller_did_not_supply() -> None:
    """Absent pins are absent, never rendered as an empty or invented value."""
    provenance = ReportProvenance(
        engine="v1-retrieve-entail",
        rules_version="cal-rules-v1.13.0",
        library_version="0.3.0",
    )
    labels = [label for label, _ in provenance.rows()]
    assert "audit run id" not in labels
    assert "rules file sha256" not in labels
    assert labels == ["engine", "rules version", "library version"]
