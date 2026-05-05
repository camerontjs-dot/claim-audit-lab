# OQ: Operational Qualification

status: verified
last_updated: 2026-05-04

Purpose: verify that Claim Audit Lab behaves as expected across its defined operating range and known edge cases.

This is a validation-inspired record for a non-regulated portfolio context. It is not intended to demonstrate FDA, EMA, GxP, GMP, CSV, or regulated-compliance status.

## Scope

This protocol covers the deterministic audit path:

- draft loading
- evidence loading
- claim extraction
- evidence matching
- rule checks
- audit orchestration
- report rendering
- CLI success and failure semantics

## Protocol

| Step | Behavior | Evidence target | Expected result | Date run | Result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| OQ-001 | Load valid Markdown and plain-text drafts. | `tests/test_loader.py` | Drafts produce stable IDs, titles, content, and source paths. | 2026-05-04 | Covered in `pytest`: 108 passed. | verified |
| OQ-002 | Load valid YAML and JSON evidence bundles. | `tests/test_loader.py` | Evidence bundles validate into typed models. | 2026-05-04 | Covered in `pytest`: 108 passed. | verified |
| OQ-003 | Reject malformed or missing-field evidence with path-aware errors. | `tests/test_loader.py`, `tests/test_cli.py` | Bad inputs fail before audit output is generated. | 2026-05-04 | Covered in `pytest`: 108 passed. | verified |
| OQ-004 | Extract explicit claims conservatively. | `tests/test_claim_extraction.py` | Vague or non-claim text is ignored; auditable claims get stable IDs and types. | 2026-05-04 | Covered in `pytest`: 108 passed. | verified |
| OQ-005 | Match numeric claims to agreeing evidence. | `tests/test_evidence_matching.py` | Matching evidence receives candidate links with traceable source and excerpt IDs. | 2026-05-04 | Covered in `pytest`: 108 passed. | verified |
| OQ-006 | Preserve differences across multiple candidate evidence sources. | `tests/test_evidence_matching.py`, `tests/test_rules.py`, `tests/test_report.py` | Source reliability and support differences remain visible in candidate metadata, rule behavior, and report tables. | 2026-05-04 | Covered in `pytest`; generated reports show reliability/date/URL columns. | verified |
| OQ-007 | Flag numeric mismatches, causal overstatement, unsupported comparisons, stale evidence, and overconfident wording. | `tests/test_rules.py`, `tests/test_auditor.py` | Claims receive appropriate labels, flags, and limitations. | 2026-05-04 | Covered in `pytest`; generated reports include overstatement and high-risk flags. | verified |
| OQ-008 | Produce useful output for empty evidence bundles. | `tests/test_auditor.py`, `tests/test_report.py` | Claims receive `needs_source` or similar non-supported outcomes with a clear warning. | 2026-05-04 | Covered in `pytest`: 108 passed. | verified |
| OQ-009 | Render Markdown and JSON reports. | `tests/test_report.py`, `examples/reports/`, ignored `build/reports/` outputs | Reports include required sections, trace links, limitations, and no placeholder values. | 2026-05-04 | Markdown reports generated for demo, AI research, and Product README; JSON outputs validated through `AuditReport`. | verified |
| OQ-010 | Preserve CLI error semantics. | `tests/test_cli.py`, `claim-audit --help`, `claim-audit demo` | Bad inputs exit nonzero; completed audits with findings exit successfully. | 2026-05-04 | CLI help displayed `audit` and `demo`; demo generated Markdown/JSON and completed with expected summary. | verified |

## Acceptance Criteria

OQ passes when current tests and inspections prove operation across the defined requirements and edge cases, or any gaps have explicit accepted deviations in `deviation-log.md`.

## Record

OQ passed on 2026-05-04. Evidence came from the current automated test suite, generated reports, JSON model validation, CLI smoke checks, and public-copy/network scans recorded in `../docs/verification.md`.
