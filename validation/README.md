# Validation Package

status: verified for v0.2 engineering release; research qualification pending
last_updated: 2026-06-13

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
| `pq-performance.md` | Performance qualification protocol and record for representative full example runs. | verified for v1 |
| `deviation-log.md` | Visible log for validation failures, accepted limitations, and follow-up actions. | no open v1 failures; future-use gates recorded |
| `../docs/validation-matrix-reference.md` | Requirement traceability matrix and status source of truth. | active |
| `../docs/verification.md` | Public release verification summary and command results. | active |

## How This Should Be Used

During implementation, add or update validation matrix rows before adding public capability claims.

The validation package was executed for the public v1 scope on 2026-05-04 and closed on 2026-05-05 after the public-tree cleanup:

1. IQ verified clean local installation, editable install, CLI availability, ignored artifacts, and README setup alignment.
2. OQ verified the deterministic operating range through the current automated suite, generated reports, and CLI checks.
3. PQ verified two representative fictional example families and recorded real-data and research-use validation as future-use gates.
4. Outcomes are recorded in the protocol files and `../docs/verification.md`.
5. `../docs/validation-matrix-reference.md` was updated only from current evidence.
6. Accepted future-use gates are visible in `deviation-log.md`.

## Pass Standard

The validation package is acceptable for a public portfolio release when:

- README capability claims trace to validation matrix rows
- core labels and rule families are covered by tests or examples
- checked-in examples can run without network access, API keys, or private data
- generated Markdown and JSON reports are stable and inspectable
- outputs include trace links, limitations, and no truth-verification language
- there are no open v1 validation failures
- future validation gates are visible before real data or research-use runs

The validation package meets this pass standard for the v0.2 engineering release.
Human-review calibration and real-data fixture qualification must be completed before
Claim Audit Lab is used on real cases, sensitive materials, or research measurement
runs.

## C-B Accommodation Addendum

On 2026-05-11, the validation package was extended for the Apparatus Contracts C-B path. The addendum covers:

- local contract-version and vocabulary pinning
- fail-closed C-B intake with typed deviations
- adapter behavior from locked C-B records into CAL-native claims and evidence
- audited output-copy writing without mutating the sealed input bundle
- `claim-audit audit-bundle` CLI success and failure semantics
- a synthetic C-A -> Evidence Bundler C-B -> CAL audited-output command sequence

This addendum verifies the engineering handoff path against synthetic fixtures. It does not validate Evidence Bundler retrieval quality, external truth, or Claim Audit Lab as a calibrated research measurement instrument.

## v0.2 Stabilization Addendum

On 2026-06-13, the package was requalified after the v0.2 classifier, scoring, policy,
API, CLI, resource-packaging, and report changes.

The pass evidence includes:

- 213 passing tests
- Ruff lint and formatting, strict mypy, and compileall
- 96% source branch coverage
- clean-wheel `--help`, `demo`, and `audit-bundle` execution
- exact `cal-rules-v1.2.0` policy enforcement
- boundary tests at `0.40`, `0.55`, `0.80`, and `0.85`
- claim-scoped evidence, separate counterevidence, and reproducibility checks
- byte-identical checked-in examples
- the synthetic apparatus round trip
- a pinned, byte-identical replay of the sealed 98-claim pilot

The pilot replay is engineering evidence only. Blind human calibration remains `0/98`.
Research qualification requires coarse-label agreement >=80%, Cohen's kappa >=0.60,
adverse-claim recall >=85%, and per-condition adverse-rate error <=10 percentage
points.

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
