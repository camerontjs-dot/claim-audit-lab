# Claim Audit Lab Qualification Plan

status: verified for v0.2 engineering release; research qualification pending
last_updated: 2026-06-13
applies_after: first CLI-first public version

Purpose: define the validation package for Claim Audit Lab as a visible project artifact. This document adapts pharma equipment qualification patterns for a software portfolio project. It is not a regulated validation package and should not be described as GxP, GMP, CSV, or FDA-compliant software.

## Intended Use

Claim Audit Lab is intended to audit whether draft claims are supported by supplied evidence.

It is not intended to:

- verify external truth
- replace human source review
- certify research outcomes
- act as a regulated quality system
- make compliance claims about itself

The qualification package should answer one practical question:

Can a reviewer see, from checked-in evidence, that the tool consistently behaves within its stated boundary?

## Qualification Model

Use a lightweight IQ/OQ/PQ structure after the first usable version exists.

| Qualification layer | Claim Audit Lab meaning | Minimum evidence |
| --- | --- | --- |
| Intended use | The README, reports, and CLI describe supplied-evidence support, not truth verification. | README inspection, report-quality tests, validation matrix row coverage. |
| IQ: installation qualification | The project installs and exposes the expected command in a clean local environment. | Editable install command, documented dependency set, `claim-audit --help`, no hidden API key or network requirement. |
| OQ: operational qualification | The tool handles its expected operating range and known edge cases. | Automated tests for valid evidence, malformed evidence, empty evidence, numeric mismatch, causal overstatement, comparative claims, stale or low-reliability evidence, and report language. |
| PQ: performance qualification | Representative full audit runs produce stable, inspectable reports from checked-in fictional or sanitized data. | At least two complete draft/evidence/report families, JSON report validation, Markdown report inspection, and public-data hygiene review. |
| C-B accommodation addendum | CAL consumes a locked C-B bundle under the exact frozen policy, audits claim-scoped evidence, and writes an audited copy without mutating the sealed input. | C-B model/loader/adapter/writer/CLI tests, clean-wheel verification, synthetic Evidence Bundler round trip, audited output reload check, and validation-matrix rows. |

## Acceptance Rules

The post-build qualification pass is acceptable when:

- every README capability claim maps to at least one validation matrix row
- every core support label appears in at least one test or example report
- every v1 rule family has an automated test or checked-in example evidence
- the CLI can run checked-in examples without network access or private credentials
- Markdown and JSON reports include trace links from claims to evidence, flags, labels, and limitations
- report language avoids claiming that the tool proves truth
- there are no open v1 validation failures
- future-use gates are documented before real data, sensitive materials, or research measurement runs

## Future Validation Gates

The v0.2 engineering release is qualified only for deterministic local runs against
checked-in fixtures and supplied C-B evidence bundles.

Before testing real data fixtures, sensitive materials, production-like drafts, or research measurement outputs, the project must complete a separate validation pass that includes:

- real-data or production-like fixture qualification
- representative Evidence Bundler retrieval/review qualification beyond synthetic fixtures
- human-review calibration and disagreement analysis
- privacy/sensitivity review for all new fixtures
- acceptance criteria for false positives, false cautions, and missed unsupported claims
- a refreshed validation matrix and deviation log

Research qualification additionally requires:

- coarse-label agreement at least 80%
- Cohen's kappa at least 0.60
- adverse-claim recall at least 85%
- per-condition adverse-rate error within 10 percentage points

## Deviation Handling

Treat any of the following as qualification deviations:

- a public claim in the README without a validation matrix row
- a matrix row marked `verified` without current evidence
- a generated report that uses truth-verification language
- a test or fixture removed without updating the matrix
- a support label that appears in docs but cannot be produced by tests or examples
- a CLI failure that hides whether the issue is bad input or an audit finding

Each deviation should be recorded in `deviation-log.md`, fixed or explicitly accepted as a known limitation, and reflected in `../docs/validation-matrix-reference.md`.

## Revalidation Triggers

Re-run the affected qualification checks when changing:

- claim extraction logic
- evidence matching logic
- support labels or scoring rules
- report rendering language
- CLI behavior or exit semantics
- fixture families used for public examples
- real-data fixture qualification
- research-use measurement rules, if Claim Audit Lab is later used as a measurement instrument
- C-B handoff contract version, vocabulary, or bundle layout
- dependency versions that affect parsing, validation, or report output

## Visibility Requirements

Keep this validation package linked from:

- `../README.md`
- `../docs/validation-matrix-reference.md`

The repo made the validation approach visible before public packaging, then executed the
IQ/OQ/PQ-inspired pass after the CLI-first version was built. The v0.2 engineering pass
is complete. Real-data, full retrieval/review, and research-measurement use remain
gated.
