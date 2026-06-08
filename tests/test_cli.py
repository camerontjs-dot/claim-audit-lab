"""Tests for the Phase 8 command-line interface."""

from __future__ import annotations

import json
import re
from pathlib import Path
from shutil import copytree

from typer.testing import CliRunner

from claim_audit_lab.cli import app
from claim_audit_lab.contracts.bundle_loader import load_bundle
from claim_audit_lab.models import AuditReport

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = PROJECT_ROOT / "examples"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"
CB_FIXTURE_BUNDLE = FIXTURE_ROOT / "cb" / "evidence-bundle-minimal"
SLICE_MARKDOWN = EXAMPLES_ROOT / "reports" / "ai-research-note.slice.md"
FORBIDDEN_CAPABILITY_PATTERNS = (
    r"\bfact checked\b",
    r"\bverified\b",
    r"\bproven\b",
    r"\btrue\b",
    r"\bfalse\b",
)

runner = CliRunner()


def test_help_lists_audit_and_demo_subcommands() -> None:
    """Root help exposes both public CLI commands."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "audit" in result.output
    assert "audit-bundle" in result.output
    assert "demo" in result.output


def test_command_help_documents_options() -> None:
    """Subcommand help documents the planned input and output options."""
    audit_result = runner.invoke(app, ["audit", "--help"])
    audit_bundle_result = runner.invoke(app, ["audit-bundle", "--help"])
    demo_result = runner.invoke(app, ["demo", "--help"])

    assert audit_result.exit_code == 0
    assert "--evidence" in audit_result.output
    assert "--out" in audit_result.output
    assert "--json-out" in audit_result.output
    assert audit_bundle_result.exit_code == 0
    assert "--out-dir" in audit_bundle_result.output
    assert demo_result.exit_code == 0
    assert "--out-dir" in demo_result.output


def test_audit_writes_markdown_and_json(tmp_path: Path) -> None:
    """Happy-path CLI runs write both report formats."""
    markdown_out = tmp_path / "reports" / "audit.md"
    json_out = tmp_path / "reports" / "audit.json"

    result = _run_ai_research_audit(markdown_out, json_out)

    assert result.exit_code == 0
    assert "Wrote Markdown report" in result.stdout
    assert "Wrote JSON report" in result.stdout
    markdown = markdown_out.read_text(encoding="utf-8")
    assert "## Executive summary" in markdown
    assert "## Claim register" in markdown
    parsed = AuditReport.model_validate(json.loads(json_out.read_text(encoding="utf-8")))
    assert parsed.summary.total_claims == 4


def test_audit_markdown_only_when_json_out_omitted(tmp_path: Path) -> None:
    """Omitting --json-out writes only the requested Markdown report."""
    markdown_out = tmp_path / "audit.md"
    stray_json = tmp_path / "audit.json"

    result = _run_ai_research_audit(markdown_out)

    assert result.exit_code == 0
    assert markdown_out.exists()
    assert not stray_json.exists()
    assert "Wrote JSON report" not in result.stdout


def test_audit_creates_missing_output_directories(tmp_path: Path) -> None:
    """Output parents are created for public CLI runs."""
    markdown_out = tmp_path / "nested" / "reports" / "audit.md"

    result = _run_ai_research_audit(markdown_out)

    assert result.exit_code == 0
    assert markdown_out.exists()


def test_audit_missing_draft_file_exits_nonzero(tmp_path: Path) -> None:
    """Missing draft paths are input failures, not audit findings."""
    result = runner.invoke(
        app,
        [
            "audit",
            str(tmp_path / "missing.md"),
            "--evidence",
            str(EXAMPLES_ROOT / "evidence" / "ai-research-evidence.yml"),
            "--out",
            str(tmp_path / "audit.md"),
        ],
    )

    assert result.exit_code == 1
    assert "missing.md" in _error_output(result)
    assert "File does not exist" in _error_output(result)


def test_audit_missing_evidence_file_exits_nonzero(tmp_path: Path) -> None:
    """Missing evidence paths fail clearly and nonzero."""
    result = runner.invoke(
        app,
        [
            "audit",
            str(EXAMPLES_ROOT / "drafts" / "ai-research-note.md"),
            "--evidence",
            str(tmp_path / "missing.yml"),
            "--out",
            str(tmp_path / "audit.md"),
        ],
    )

    assert result.exit_code == 1
    assert "missing.yml" in _error_output(result)
    assert "File does not exist" in _error_output(result)


def test_audit_unsupported_draft_type_exits_nonzero(tmp_path: Path) -> None:
    """Unsupported draft suffixes fail before parsing."""
    unsupported_draft = tmp_path / "draft.pdf"
    unsupported_draft.write_text("placeholder", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "audit",
            str(unsupported_draft),
            "--evidence",
            str(EXAMPLES_ROOT / "evidence" / "ai-research-evidence.yml"),
            "--out",
            str(tmp_path / "audit.md"),
        ],
    )

    assert result.exit_code == 1
    assert "draft.pdf" in _error_output(result)
    assert "Unsupported draft file type" in _error_output(result)


def test_audit_malformed_yaml_evidence_exits_nonzero(tmp_path: Path) -> None:
    """Malformed evidence bundles are clear CLI input failures."""
    result = runner.invoke(
        app,
        [
            "audit",
            str(EXAMPLES_ROOT / "drafts" / "ai-research-note.md"),
            "--evidence",
            str(FIXTURE_ROOT / "evidence" / "malformed-evidence.yml"),
            "--out",
            str(tmp_path / "audit.md"),
        ],
    )

    assert result.exit_code == 1
    assert "malformed-evidence.yml" in _error_output(result)
    assert "Could not parse YAML" in _error_output(result)


def test_audit_invalid_evidence_schema_exits_nonzero(tmp_path: Path) -> None:
    """Evidence validation failures remain loader errors in the CLI."""
    result = runner.invoke(
        app,
        [
            "audit",
            str(EXAMPLES_ROOT / "drafts" / "ai-research-note.md"),
            "--evidence",
            str(FIXTURE_ROOT / "evidence" / "missing-required-field.yml"),
            "--out",
            str(tmp_path / "audit.md"),
        ],
    )

    assert result.exit_code == 1
    assert "missing-required-field.yml" in _error_output(result)
    assert "Validation failed for evidence bundle" in _error_output(result)


def test_audit_high_risk_findings_exit_success(tmp_path: Path) -> None:
    """High-risk findings are completed audit results, not process failures."""
    result = _run_ai_research_audit(tmp_path / "audit.md")

    assert result.exit_code == 0
    assert re.search(r"\b[1-9]\d* high-risk\b", result.stdout)


def test_audit_bundle_writes_audited_copy_and_summary(tmp_path: Path) -> None:
    """The C-B CLI path audits extracted claims and writes a reloadable copy."""
    bundle_dir = _copy_cb_fixture(tmp_path)
    out_dir = tmp_path / "cb-output"

    result = runner.invoke(app, ["audit-bundle", str(bundle_dir), "--out-dir", str(out_dir)])

    audited_bundle = out_dir / f"{bundle_dir.name}-audited"
    assert result.exit_code == 0
    assert audited_bundle.exists()
    assert "1 claims audited" in result.stdout
    assert "0 retrieval seeds skipped" in result.stdout
    assert f"Wrote audited C-B bundle: {audited_bundle}" in result.stdout

    original = load_bundle(bundle_dir, deviations_dir=tmp_path / "original-deviations")
    reloaded = load_bundle(audited_bundle, deviations_dir=tmp_path / "audited-deviations")
    assert original.claims[0].audit.audit_run_id is None
    assert reloaded.claims[0].audit.audit_run_id is not None
    assert reloaded.claims[0].audit.audit_support_verdict == "supported"


def test_audit_bundle_intake_failure_exits_nonzero_and_writes_deviation(
    tmp_path: Path,
) -> None:
    """C-B intake failures are process failures and leave a typed deviation record."""
    bundle_dir = _copy_cb_fixture(tmp_path)
    (bundle_dir / "CONTRACT_VERSION").unlink()
    out_dir = tmp_path / "cb-output"

    result = runner.invoke(app, ["audit-bundle", str(bundle_dir), "--out-dir", str(out_dir)])

    assert result.exit_code == 1
    assert "C-B intake failed" in _error_output(result)
    deviations = sorted((out_dir / "deviations").glob("*.yaml"))
    assert len(deviations) == 1
    assert "missing_required_field" in deviations[0].read_text(encoding="utf-8")
    assert not (out_dir / f"{bundle_dir.name}-audited").exists()


def test_demo_writes_reports_to_requested_dir(tmp_path: Path) -> None:
    """The demo subcommand gives reviewers a one-command report path."""
    result = runner.invoke(app, ["demo", "--out-dir", str(tmp_path)])

    markdown_out = tmp_path / "ai-research-note.cli.md"
    json_out = tmp_path / "ai-research-note.cli.json"
    assert result.exit_code == 0
    assert markdown_out.exists()
    assert json_out.exists()
    assert "## Executive summary" in markdown_out.read_text(encoding="utf-8")
    parsed = AuditReport.model_validate(json.loads(json_out.read_text(encoding="utf-8")))
    assert parsed.summary.total_claims == 4


def test_demo_does_not_overwrite_checked_in_fixtures(tmp_path: Path) -> None:
    """Demo output stays away from tracked slice fixtures."""
    before = SLICE_MARKDOWN.read_text(encoding="utf-8")

    result = runner.invoke(app, ["demo", "--out-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert SLICE_MARKDOWN.read_text(encoding="utf-8") == before


def test_cli_does_not_emit_forbidden_capability_language(tmp_path: Path) -> None:
    """CLI summaries preserve supplied-evidence boundary language."""
    result = _run_ai_research_audit(tmp_path / "audit.md")

    assert result.exit_code == 0
    _assert_no_forbidden_capability_language(result.stdout)


def _run_ai_research_audit(markdown_out: Path, json_out: Path | None = None):
    args = [
        "audit",
        str(EXAMPLES_ROOT / "drafts" / "ai-research-note.md"),
        "--evidence",
        str(EXAMPLES_ROOT / "evidence" / "ai-research-evidence.yml"),
        "--out",
        str(markdown_out),
    ]
    if json_out is not None:
        args.extend(["--json-out", str(json_out)])
    return runner.invoke(app, args)


def _copy_cb_fixture(tmp_path: Path) -> Path:
    destination = tmp_path / "evidence-bundle-minimal"
    copytree(CB_FIXTURE_BUNDLE, destination)
    return destination


def _assert_no_forbidden_capability_language(text: str) -> None:
    lowered = text.lower()
    for pattern in FORBIDDEN_CAPABILITY_PATTERNS:
        assert re.search(pattern, lowered) is None


def _error_output(result) -> str:
    return getattr(result, "stderr", "") or result.output
