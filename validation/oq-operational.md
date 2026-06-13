# OQ: Operational Qualification

status: verified
last_updated: 2026-06-13

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
- C-B fail-closed intake, adapter boundary, audited output-copy writing, and `audit-bundle` CLI semantics

## Protocol

| Step | Behavior | Evidence target | Expected result | Date run | Result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| OQ-001 | Load valid Markdown and plain-text drafts. | `tests/test_loader.py` | Drafts produce stable IDs, titles, content, and source paths. | 2026-05-04 | Covered in `pytest`: 112 passed. | verified |
| OQ-002 | Load valid YAML and JSON evidence bundles. | `tests/test_loader.py` | Evidence bundles validate into typed models. | 2026-05-04 | Covered in `pytest`: 112 passed. | verified |
| OQ-003 | Reject malformed or missing-field evidence with path-aware errors. | `tests/test_loader.py`, `tests/test_cli.py` | Bad inputs fail before audit output is generated. | 2026-05-04 | Covered in `pytest`: 112 passed. | verified |
| OQ-004 | Extract explicit claims conservatively. | `tests/test_claim_extraction.py` | Vague or non-claim text is ignored; auditable claims get stable IDs and types. | 2026-05-04 | Covered in `pytest`: 112 passed. | verified |
| OQ-005 | Match numeric claims to agreeing evidence. | `tests/test_evidence_matching.py` | Matching evidence receives candidate links with traceable source and excerpt IDs. | 2026-05-04 | Covered in `pytest`: 112 passed. | verified |
| OQ-006 | Preserve differences across multiple candidate evidence sources. | `tests/test_evidence_matching.py`, `tests/test_rules.py`, `tests/test_report.py` | Source reliability and support differences remain visible in candidate metadata, rule behavior, and report tables. | 2026-05-04 | Covered in `pytest`; generated reports show reliability/date/URL columns. | verified |
| OQ-007 | Flag numeric mismatches, causal overstatement, unsupported comparisons, stale evidence, and overconfident wording. | `tests/test_rules.py`, `tests/test_auditor.py` | Claims receive appropriate labels, flags, and limitations. | 2026-05-04 | Covered in `pytest`; generated reports include overstatement and high-risk flags. | verified |
| OQ-008 | Produce useful output for empty evidence bundles. | `tests/test_auditor.py`, `tests/test_report.py` | Claims receive `needs_source` or similar non-supported outcomes with a clear warning. | 2026-05-04 | Covered in `pytest`: 112 passed. | verified |
| OQ-009 | Render Markdown and JSON reports. | `tests/test_report.py`, `examples/reports/`, ignored `build/reports/` outputs | Reports include required sections, trace links, limitations, and no placeholder values. | 2026-05-04 | Markdown reports generated for demo, AI research, and Product README; JSON outputs validated through `AuditReport`. | verified |
| OQ-010 | Preserve CLI error semantics. | `tests/test_cli.py`, `claim-audit --help`, `claim-audit demo` | Bad inputs exit nonzero; completed audits with findings exit successfully. | 2026-05-04 | CLI help displayed `audit` and `demo`; demo generated Markdown/JSON and completed with expected summary. | verified |
| OQ-011 | Verify locked C-B read models and vocabulary boundaries. | `tests/test_cb_models.py` | Locked C-B v1.0.0 tree loads and stale draft shapes / legacy labels are rejected. | 2026-05-11 | Covered in C-B model tests: 5 passed. | verified |
| OQ-012 | Fail closed on invalid C-B intake. | `tests/test_cb_bundle_loader.py` | Missing required files, schema errors, hash mismatches, audit-config hash mismatch, and vocabulary drift halt with typed deviations. | 2026-05-11 | Covered in C-B bundle-loader tests: 7 passed. | verified |
| OQ-013 | Adapt only auditable C-B claims into CAL pipeline inputs. | `tests/test_cb_adapter.py` | `retrieval_seed` records are skipped and C-B `claim_type` never becomes CAL semantic `Claim.claim_type`. | 2026-05-11 | Covered in C-B adapter tests: 5 passed. | verified |
| OQ-014 | Write audited C-B results to a copied, resealed bundle. | `tests/test_cb_output_writer.py` | Input bundle remains byte-stable; output copy receives `audit.*`, reseals hashes, reloads through fail-closed loader, and leaves unassessed retrieval seeds untouched. | 2026-05-11 | Covered in C-B output-writer tests: 4 passed. | verified |
| OQ-015 | Preserve C-B CLI success and failure semantics. | `tests/test_cli.py`; `claim-audit audit-bundle` smoke command | Valid C-B fixture writes audited output; invalid intake exits nonzero and writes a deviation record. | 2026-05-11 | CLI tests: 16 passed; `audit-bundle` smoke command wrote an audited copy. | verified |
| OQ-016 | Enforce the exact frozen C-B policy. | `tests/test_cb_bundle_loader.py`; `tests/test_rules.py` | Changed policy IDs, values, or switches fail closed; exact `cal-rules-v1.2.0` loads. | 2026-06-13 | Covered in the 213-test suite. | verified |
| OQ-017 | Bind each C-B claim to its linked support and counterevidence. | `tests/test_cb_adapter.py`; `tests/test_rules.py` | Unrelated passages cannot rematch; counterevidence is separate, penalizes the signal, and prevents `supported`. | 2026-06-13 | Covered in the 213-test suite. | verified |
| OQ-018 | Verify frozen score and false-caution boundaries. | `tests/test_rules.py`; `tests/test_cb_output_writer.py` | Exact boundary behavior is covered at `0.40`, `0.55`, `0.80`, and `0.85`. | 2026-06-13 | Boundary tests passed. | verified |
| OQ-019 | Preserve classifier parity and unclassified behavior. | `tests/test_classifiers.py`; `tests/test_claim_extraction.py`; `tests/test_rules.py` | The governed classifier priority is shared; native extraction skips unclassified text; C-B returns `not_checkable`. | 2026-06-13 | Classifier and extraction tests passed. | verified |
| OQ-020 | Preserve reproducible C-B outputs. | `tests/test_cli.py`; sealed-pilot replay | Paired run metadata produces byte-identical audited bundles and reports. | 2026-06-13 | Unit reproducibility test and second 98-claim replay were byte-identical. | verified |

## Acceptance Criteria

OQ passes when current tests and inspections prove operation across the defined requirements and edge cases, or any gaps have explicit accepted deviations in `deviation-log.md`.

## Record

OQ passed on 2026-05-04 for the public fictional-fixture report workflow, on
2026-05-11 for the initial C-B accommodation, and on 2026-06-13 for the bound v0.2
policy, evidence scope, classifier, and reproducibility semantics. Evidence came from
the 213-test suite and the checks recorded in `../docs/verification.md`.
