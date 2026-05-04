# Validation Package

status: planned
last_updated: 2026-05-04

Purpose: make Claim Audit Lab's validation approach visible as part of the project, not only as planning notes. This package adapts pharma equipment qualification habits for a deterministic software portfolio asset without claiming GxP, GMP, CSV, FDA, or regulated validation status.

## Boundary

Claim Audit Lab validates its own behavior.

It does not validate whether outside-world claims are true. A passing validation artifact means the tool behaved as expected for a defined requirement, fixture, command, or generated report.

## Validation Package Map

| File | Purpose | Current state |
| --- | --- | --- |
| `qualification-plan.md` | Overall qualification strategy, acceptance rules, deviations, and revalidation triggers. | planned |
| `iq-installation.md` | Installation qualification protocol and future record. | planned |
| `oq-operational.md` | Operational qualification protocol and future record for edge cases and operating ranges. | protocol planned; current test evidence noted |
| `pq-performance.md` | Performance qualification protocol and future record for full example runs. | protocol planned; two report families ready |
| `deviation-log.md` | Visible log for validation failures, accepted limitations, and follow-up actions. | open |
| `../docs/validation-matrix-reference.md` | Requirement traceability matrix and status source of truth. | active |
| `../docs/verification.md` | Session-level verification notes and command results. | active |

## How This Should Be Used

During implementation, add or update validation matrix rows before adding public capability claims.

After Phase 11 public packaging:

1. Run the IQ protocol.
2. Run the OQ protocol.
3. Run the PQ protocol.
4. Record outcomes in the protocol files and `../docs/verification.md`.
5. Update `../docs/validation-matrix-reference.md` only from current evidence.
6. Add deviations to `deviation-log.md` instead of hiding gaps.

## Pass Standard

The validation package is acceptable for a public portfolio release when:

- README capability claims trace to validation matrix rows
- core labels and rule families are covered by tests, examples, or explicit deferred statuses
- checked-in examples can run without network access, API keys, or private data
- generated Markdown and JSON reports are stable and inspectable
- outputs include trace links, limitations, and no truth-verification language
- deviations and accepted limitations are visible

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
