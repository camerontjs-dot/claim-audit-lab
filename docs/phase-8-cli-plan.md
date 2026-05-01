# Phase 8 CLI Plan

status: complete
last_updated: 2026-05-01
phase: Phase 8

Purpose: implement the public `claim-audit` CLI on top of the verified loader, auditor, and report renderer. The CLI is the first surface a public reviewer sees, so it must wire existing layers together cleanly, fail clearly on bad input, and treat audit findings (including high-risk claims) as completed audits rather than process failures.

## Phase 7 Tie-Off Baseline

Phase 7 is complete and rechecked as of 2026-05-01.

Current verified baseline:

- `loader.load_draft(...)` and `loader.load_evidence_bundle(...)` raise `LoaderError` (a `ValueError` subclass) for missing files, unsupported file types, malformed YAML/JSON, and Pydantic validation failures, with path-aware messages.
- `auditor.audit_document(draft, evidence_bundle, config=None) -> AuditReport` returns a typed report and never raises for audit findings (empty bundles, no-claim drafts, and high-risk findings all return successfully).
- `report.render_markdown_report(report)` returns a human-review Markdown string with metadata, executive summary, limitations, claim register, claim details, evidence links, and suggested rewrite guidance.
- `report.render_json_report(report)` returns a JSON string tied to the `AuditReport` schema.
- `scripts/run_demo.py` shows the canonical end-to-end wiring (load → audit → render → write) and remains the reviewer-friendly demo entry point.
- `pyproject.toml` already declares the CLI entry point: `claim-audit = "claim_audit_lab.cli:app"`. Required dependencies (`typer>=0.12`, `rich>=13.7`) are present.
- Test suite: 90 pytest tests passing, 96% total coverage.

Known limits to preserve until later phases:

- Candidate evidence scores remain ranking signals, not support scores.
- The second fixture family does not yet have generated Markdown/JSON reports (Phase 9).
- No support score, source discovery, network calls, or LLM calls.

## Requirements Owned

Phase 8 owns these validation matrix rows:

- `CAL-REQ-015`: CLI malformed-input failures must be clear and nonzero.
- `CAL-REQ-016`: CLI high-risk findings must still exit successfully when the audit completes. The auditor-level portion was covered in Phase 6; the CLI portion completes this row.
- `CAL-REQ-026`: the project must install locally and expose the planned CLI command.

Related rows to avoid overclaiming:

- `CAL-REQ-017`, `CAL-REQ-028`: example-family completeness belongs to Phase 9.
- `CAL-REQ-018`: README-vs-implementation alignment belongs to Phase 11.
- `CAL-REQ-036`: post-build qualification belongs to Phase 12.

## Primary Files

- `src/claim_audit_lab/cli.py` (new)
- `tests/test_cli.py` (new)

Touch only if a CLI integration test exposes a narrow bug:

- `src/claim_audit_lab/loader.py` (only to expose error structure if needed)
- `src/claim_audit_lab/auditor.py` (no expected changes)
- `src/claim_audit_lab/report.py` (no expected changes)

Documentation updates after implementation are listed in the final section.

## CLI Contract

Use **Typer** for the CLI (consistent with the declared `app` entry point and the project's existing `typer` dependency). Layout:

```python
import typer
app = typer.Typer(help="Claim Audit Lab — audit support from supplied evidence.")

@app.command()
def audit(draft: Path, evidence: Path, out: Path, json_out: Path | None = None) -> None: ...

@app.command()
def demo(out_dir: Path | None = None) -> None: ...
```

### `audit` subcommand

Invocation:

```
claim-audit audit <draft> --evidence <bundle> --out <report.md> [--json-out <report.json>]
```

- `<draft>`: positional `Path`, required. Markdown or plain text.
- `--evidence`: `Path`, required. YAML or JSON evidence bundle.
- `--out`: `Path`, required. Markdown report output path.
- `--json-out`: `Path`, optional. JSON report output path; only written when provided.

Pipeline (mirror `scripts/run_demo.py`):

1. `draft = load_draft(draft_path)`
2. `evidence_bundle = load_evidence_bundle(evidence_path)`
3. `report = audit_document(draft, evidence_bundle)`
4. Write `render_markdown_report(report)` to `--out`.
5. If `--json-out` is set, write `render_json_report(report)` to that path.
6. Print one-line confirmations to stdout (file paths written) plus a brief summary line (`{n} claims assessed; {k} high-risk`).
7. Exit 0.

### `demo` subcommand

Invocation:

```
claim-audit demo [--out-dir <dir>]
```

- Runs the AI research fixture (`examples/drafts/ai-research-note.md` + `examples/evidence/ai-research-evidence.yml`) and writes Markdown + JSON to `--out-dir` (default: a temp dir or `build/reports/`).
- Useful for public reviewers who do not want to assemble a draft + evidence pair before seeing the tool work.
- Does not write to checked-in fixture paths. Fixture refresh remains `scripts/run_demo.py --update-fixture`.

### Error semantics

| Condition | Behavior | Exit code |
| --- | --- | --- |
| `LoaderError` (missing file, bad type, malformed YAML/JSON, model validation) | Print `Error: {LoaderError message}` to stderr | 1 |
| Typer/Click argument parsing failure (missing required flag, etc.) | Typer's standard error output | 2 |
| `audit_document(...)` returns a report with high-risk claims | Normal output; mention high-risk count in summary | 0 |
| `audit_document(...)` returns a zero-claim or empty-bundle report | Normal output; mention warnings | 0 |
| Unexpected exception (not `LoaderError`) | Re-raise, full traceback (genuine bug) | nonzero |

Use `typer.Exit(code=1)` after printing the loader error to stderr via `typer.echo(..., err=True)`. Do not swallow unexpected exceptions.

### Output discipline

- All writes are local files. No network, no API keys, no LLM calls.
- Report content is produced by existing `render_*` functions; the CLI does not synthesize report text.
- Stdout summary preserves boundary language ("supported by supplied evidence", never "verified" / "fact checked").
- Candidate scores are not surfaced as success indicators — the summary uses claim counts and label/risk counts only.

## Required Behavior

- `claim-audit --help` works after `python -m pip install -e ".[dev]"` and lists `audit` and `demo` subcommands.
- `claim-audit audit --help` and `claim-audit demo --help` work and document each option.
- Normal fixture run writes Markdown and JSON reports to requested paths and exits 0.
- Markdown-only runs (omit `--json-out`) work and do not create a stray JSON file.
- Output paths' parent directories are created if missing (`Path.mkdir(parents=True, exist_ok=True)`), matching `scripts/run_demo.py`'s pattern.
- Missing draft path: clear stderr error referencing the path, exit 1.
- Missing evidence path: clear stderr error referencing the path, exit 1.
- Unsupported draft type (e.g., `.pdf`): clear stderr error, exit 1.
- Malformed YAML/JSON evidence: clear stderr error including the path and the underlying parser/validator detail, exit 1.
- Evidence bundle that fails Pydantic validation (duplicate IDs, blank required fields, etc.): clear stderr error, exit 1.
- Completed audits with high-risk findings exit 0.
- The AI research fixture run produces the same labels and high-risk counts as `tests/test_auditor.py` and `tests/test_report.py` baselines (the CLI is a thin wrapper, not a re-implementation).
- Local-only: no network, no API keys, no live LLM calls in normal CLI runs.

## Required Tests

Create `tests/test_cli.py`. Use `typer.testing.CliRunner` with `mix_stderr=False` so stderr is inspectable.

Minimum tests:

- `test_help_lists_audit_and_demo_subcommands` — `claim-audit --help` exits 0, mentions both subcommands.
- `test_audit_writes_markdown_and_json` — happy path against the AI research fixture, both files exist, Markdown contains `## Executive summary` + `## Claim register`, JSON parses and round-trips through `AuditReport.model_validate(...)`.
- `test_audit_markdown_only_when_json_out_omitted` — without `--json-out`, no JSON file is created.
- `test_audit_creates_missing_output_directories` — `--out` path with non-existent parent directory still succeeds.
- `test_audit_missing_draft_file_exits_nonzero` — fake path; stderr includes the missing path and "does not exist"; exit code 1.
- `test_audit_missing_evidence_file_exits_nonzero` — fake path; same shape as above; exit code 1.
- `test_audit_unsupported_draft_type_exits_nonzero` — pass a `.pdf` (no need for real content); stderr explains the unsupported type; exit code 1.
- `test_audit_malformed_yaml_evidence_exits_nonzero` — use existing malformed YAML fixture under `tests/fixtures/evidence/`; stderr mentions parse failure; exit code 1.
- `test_audit_invalid_evidence_schema_exits_nonzero` — use an evidence fixture that fails Pydantic validation (duplicate IDs or missing required field); stderr mentions validation failure; exit code 1.
- `test_audit_high_risk_findings_exit_success` — AI research fixture is known to produce overstated/high-risk claims; assert exit code 0 and summary mentions a non-zero high-risk count.
- `test_demo_writes_reports_to_requested_dir` — `claim-audit demo --out-dir <tmp>` writes Markdown + JSON; exit code 0; outputs match the AI research fixture shape.
- `test_demo_does_not_overwrite_checked_in_fixtures` — run `demo` and assert that `examples/reports/ai-research-note.slice.md` is not modified (compare mtime or content snapshot).
- `test_cli_does_not_emit_forbidden_capability_language` — stdout summary contains none of `true`, `false`, `verified`, `fact checked`, `proven` as standalone capability words. (Reuse the language-gate pattern from `tests/test_report.py`.)

Test infrastructure notes:

- Use `tmp_path` (pytest fixture) for output paths.
- Use `EXAMPLES_ROOT` and `FIXTURE_ROOT` constants paralleling `tests/test_loader.py`.
- For tests that need a malformed YAML evidence fixture and one does not exist under `tests/fixtures/evidence/`, reuse the closest existing malformed fixture rather than adding new ones; if a new one is unavoidable, keep it minimal and fictional.

## Non-Goals

- Do not add a support score or assessment-confidence score.
- Do not expand deterministic rule taxonomy.
- Do not modify the Markdown or JSON renderer (unless an integration test exposes a narrow bug).
- Do not generate the second fixture report family. That is Phase 9 work.
- Do not add source discovery, web search, or LLM calls.
- Do not implement research-use paired-draft metrics.
- Do not change the `AuditReport` contract.
- Do not introduce a config-file flag (`--config foo.toml`); `AuditConfig` defaults are sufficient for v1 CLI.
- Do not add coloured Rich output beyond what Typer provides by default. Keep stdout/stderr text plain enough for CI parsing.

## Acceptance Criteria

Phase 8 is complete when:

- `tests/test_cli.py` covers help output, happy path (both renderers), markdown-only output, missing-output-directory creation, missing-file errors, unsupported draft types, malformed YAML, schema-invalid evidence, high-risk-findings success, demo subcommand behavior, and forbidden language gates.
- `claim-audit --help` works after `python -m pip install -e ".[dev]"` from a clean checkout.
- All previous tests still pass (loader, models, extraction, matching, rules, auditor, report, vertical slice).
- `CAL-REQ-015`, `CAL-REQ-016`, and `CAL-REQ-026` flip to `verified` in `docs/validation-matrix-reference.md`.
- Generated CLI output preserves boundary language; no forbidden capability words appear in summaries.
- Local-only: tests do not require network, API keys, or LLM calls.
- Phase 8 tie-off is recorded in `docs/master-plan.md` (status: complete + tie-off line) and `docs/verification.md`.
- The next best step is updated to Phase 9 (example families) or Phase 10 (validation sweep), whichever the master plan prefers at tie-off time.

## Verification Commands

Run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m pip install -e ".[dev]"
claim-audit --help
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff format src/claim_audit_lab/cli.py tests/test_cli.py
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Only include other source files in the formatting command if Phase 8 changes them.

## Documentation Updates After Implementation

After Phase 8 implementation:

- Update `docs/master-plan.md` Phase 8 status (`complete`), tie-off line with test/coverage counts, and the `Current State` paragraph to mention the working CLI.
- Update `docs/verification.md` with checks run, outcomes, and any gaps.
- Update `docs/validation-matrix-reference.md`: flip `CAL-REQ-015`, `CAL-REQ-016`, `CAL-REQ-026` to `verified` with `tests/test_cli.py` and CLI demonstration as evidence.
- Update `README.md`:
  - Replace "The CLI workflow has not been built yet." with a verified-CLI line.
  - Add a `## Quick start` or `## Usage` section showing `claim-audit audit ...` against the AI research fixture.
  - Update the "Next implementation step" line to the next phase.
- Update `docs/handoff-prompt.md` so the next session starts the next phase (Phase 9 example families or Phase 10 validation sweep, per master-plan order).
- Update `/Users/gammaquantum/My Drive/projects/job-hunt/log/job-hunt-log.md` with a Phase 8 session entry and bump the activity table.
- Add `## Implementation Result` to this plan file recording what was actually built (mirroring how Phase 6 plan was tied off).

## Implementation Result

Implemented on 2026-05-01.

Built:

- `claim-audit audit <draft> --evidence <bundle> --out <report.md> [--json-out <report.json>]`
- `claim-audit demo [--out-dir <dir>]`
- Path creation for requested output files.
- Clear `LoaderError` handling with stderr output and exit code 1.
- Successful exit behavior for completed audits with high-risk findings.
- Plain stdout summaries using supplied-evidence language and label/risk counts only.

Tests:

- Added `tests/test_cli.py` with 14 CLI tests for help output, successful Markdown/JSON output, Markdown-only output, output-directory creation, missing files, unsupported draft type, malformed YAML, evidence schema validation failure, high-risk-finding success, demo output, checked-in fixture protection, and forbidden capability wording.
- Refreshed the generated AI research slice report header after the CLI became available so public reports no longer state that CLI work is planned.

Verification:

- `.venv/bin/python -m compileall -q src tests`: passed.
- `.venv/bin/python -m pytest`: 104 passed.
- `.venv/bin/python -m ruff check .`: passed.
- `.venv/bin/python -m ruff format --check .`: passed.
- `.venv/bin/python -m mypy src`: passed across 9 source files.
- `.venv/bin/python -m coverage run --branch -m pytest` plus coverage report: 104 passed, 96% total coverage.
- `.venv/bin/python -m pip install -e ".[dev]"`: editable install succeeded.
- Activated `claim-audit --help`: showed `audit` and `demo`.
- Activated `claim-audit demo --out-dir build/reports/cli-demo`: wrote ignored Markdown/JSON outputs and exited 0.

Validation rows advanced:

- `CAL-REQ-015`: verified.
- `CAL-REQ-016`: verified.
- `CAL-REQ-026`: verified.

Next step:

- Phase 9 example families: generate Product README Markdown/JSON reports, check public fixture data, and keep audit semantics stable.

## Open Decisions

| Decision | Current leaning | When to decide |
| --- | --- | --- |
| `claim-audit demo` subcommand | Include in Phase 8 — single fixture run is cheap and gives reviewers a one-command path before they assemble their own inputs. | This plan. |
| `--out` default vs required | Required for `audit`, optional with sensible default for `demo`. | This plan. |
| Coloured Rich output | Skip for v1; plain text only. | This plan. |
| Config-file flag | Skip for v1 CLI; revisit if Phase 9/10 fixtures need non-default `AuditConfig`. | Phase 9 or later. |
| Stdout vs stderr for the post-run summary | Stdout for the success summary; stderr only for errors. | This plan. |
