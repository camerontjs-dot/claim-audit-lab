# Validation Package

status: verified
last_updated: 2026-05-04

Purpose: make Claim Audit Lab's validation approach visible as part of the project, not only as planning notes. This package adapts pharma equipment qualification habits for a deterministic software portfolio asset without claiming GxP, GMP, CSV, FDA, or regulated validation status.

## Boundary

Claim Audit Lab validates its own behavior.

It does not validate whether outside-world claims are true. A passing validation artifact means the tool behaved as expected for a defined requirement, fixture, command, or generated report.

## Validation Package Map

| File | Purpose | Current state |
| --- | --- | --- |
| `qualification-plan.md` | Overall qualification strategy, acceptance rules, deviations, and revalidation triggers. | verified strategy |
| `iq-installation.md` | Installation qualification protocol and record. | verified |
| `oq-operational.md` | Operational qualification protocol and record for edge cases and operating ranges. | verified |
| `pq-performance.md` | Performance qualification protocol and record for representative full example runs. | verified with v1 limitations |
| `deviation-log.md` | Visible log for validation failures, accepted limitations, and follow-up actions. | open; accepted v1 limitations recorded |
| `../docs/validation-matrix-reference.md` | Requirement traceability matrix and status source of truth. | active |
| `../docs/verification.md` | Public release verification summary and command results. | active |

## How This Should Be Used

During implementation, add or update validation matrix rows before adding public capability claims.

The validation package was executed on 2026-05-04:

1. IQ verified clean local installation, editable install, CLI availability, ignored artifacts, and README setup alignment.
2. OQ verified the deterministic operating range through the current automated suite, generated reports, and CLI checks.
3. PQ verified two representative fictional example families and recorded research-use and production-data limitations.
4. Outcomes are recorded in the protocol files and `../docs/verification.md`.
5. `../docs/validation-matrix-reference.md` was updated only from current evidence.
6. Accepted limitations are visible in `deviation-log.md`.

## Pass Standard

The validation package is acceptable for a public portfolio release when:

- README capability claims trace to validation matrix rows
- core labels and rule families are covered by tests, examples, or explicit deferred statuses
- checked-in examples can run without network access, API keys, or private data
- generated Markdown and JSON reports are stable and inspectable
- outputs include trace links, limitations, and no truth-verification language
- deviations and accepted limitations are visible

The validation package meets this pass standard for the v1 portfolio release. Research-use calibration and production-data qualification remain outside v1.

## Compliance Language Guardrail

Use:

- validation-inspired
- qualification-style
- IQ/OQ/PQ-inspired
- traceable
- reproducible

Avoid:

- validated to GxP
- GMP compliant
- CSV compliant
- FDA validated
- regulated validation package
