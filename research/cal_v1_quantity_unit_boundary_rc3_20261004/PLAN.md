# CAL V1 RC3 — quantity unit identity and dimension boundary

Status: research preparation only. Parent issue: CAL #212.

Predecessor: Draft PR #211 at `cd957e3ffe16c069bf74b84e88fa4b888d81239c`, disposition `FALSIFIED_NEW_CRITICAL_FALSE_DECISION`.

## Trigger

HOL-14 false-supported `less than 10 percentage points` against `less than 10%`.
The predecessor accepted `percent` as a prefix of `percentage points`. This is a unit identity/dimension failure, not a synthesis-weight failure.

## Required local representation

Every accepted quantitative measurement must independently bind:

- numeric value(s);
- exact lexical unit span(s);
- normalized unit identity;
- quantity role/dimension;
- measure/property;
- comparator/direction;
- time/scope;
- exact consumed spans;
- registered conversion identity if any;
- ambiguity/unresolved state;
- input and instrument identity.

Minimum RC3 vocabulary:

- `percent_level`
- `percent_relative_change`
- `percentage_point_change`
- `basis_point_change`
- `count`
- `rate`
- `unknown`
- `not_applicable`

`%` and `percent` may be lexical variants of percent.
`percentage point(s)` is not percent.
100 basis points = 1 percentage point only for compatible absolute rate/change measures.
Unknown abbreviations fail closed.

## Ordering

1. Freeze source identities/partitions before candidate changes.
2. Retrieve each selected source once and freeze raw bytes/provenance.
3. Keep held-out bodies/labels isolated from implementation through candidate/evaluator/policy freeze.
4. Use only exposed predecessor failures, the development matrix, and calibration material for implementation.
5. Burn calibration if it changes the candidate.
6. Expose held-out exactly once after all bytes/policy are frozen.

## Architecture and weighting

Keep the original-input independent-judge fan-out, first-pass sealing, failure-state distinctions, dependence controls, required guards, and predecessor synthesis weights unchanged unless independently falsified.

Do not retune weights to cure a unit parser failure.

## Acceptance

A development pass only authorizes fresh source-disjoint qualification.
Held-out acceptance requires zero critical false deciding results.

RC3 does not establish general natural-language usefulness, universal semantic coverage, Contract C suitability, or V1 release readiness.
