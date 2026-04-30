# OQ: Operational Qualification

status: planned
last_updated: 2026-04-30

Purpose: verify that Claim Audit Lab behaves as expected across its defined operating range and known edge cases.

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

| Step | Behavior | Evidence target | Expected result | Status |
| --- | --- | --- | --- | --- |
| OQ-001 | Load valid Markdown and plain-text drafts. | `tests/test_loader.py` | Drafts produce stable IDs, titles, content, and source paths. | verified |
| OQ-002 | Load valid YAML and JSON evidence bundles. | `tests/test_loader.py` | Evidence bundles validate into typed models. | verified |
| OQ-003 | Reject malformed or missing-field evidence with path-aware errors. | `tests/test_loader.py` | Bad inputs fail before audit output is generated. | verified |
| OQ-004 | Extract explicit claims conservatively. | `tests/test_claim_extraction.py` | Vague or non-claim text is ignored; auditable claims get stable IDs and types. | verified |
| OQ-005 | Match numeric claims to agreeing evidence. | `tests/test_evidence_matching.py` | Matching evidence receives candidate links with traceable source and excerpt IDs. | planned |
| OQ-006 | Preserve differences across multiple candidate evidence sources. | `tests/test_evidence_matching.py`, `tests/test_rules.py` | Source reliability and support differences remain visible. | planned |
| OQ-007 | Flag numeric mismatches, causal overstatement, unsupported comparisons, stale evidence, and overconfident wording. | `tests/test_rules.py`, `tests/test_auditor.py` | Claims receive appropriate labels, flags, and limitations. | planned |
| OQ-008 | Produce useful output for empty evidence bundles. | `tests/test_auditor.py`, `tests/test_report.py` | Claims receive `needs_source` or similar non-supported outcomes with a clear warning. | planned |
| OQ-009 | Render Markdown and JSON reports. | `tests/test_report.py`, `examples/reports/` | Reports include required sections, trace links, limitations, and no placeholder values. | planned |
| OQ-010 | Preserve CLI error semantics. | `tests/test_cli.py` | Bad inputs exit nonzero; completed audits with findings exit successfully. | planned |

## Acceptance Criteria

OQ passes when all in-scope behaviors are verified by tests, example outputs, or accepted deviations.

## Record

Current verified items are inherited from existing tests. The full OQ pass remains planned until evidence matching, rules, audit orchestration, reports, and CLI behavior are implemented.
