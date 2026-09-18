# CAL Scalar Gate-1B Authority RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / independent source-completion and warrant qualification.

Parent: terminal Scalar Gate-1A head `4f2c6718a1cea5b0c92d00b10266794135be3c77`.
Selected measurement path: `conservative_numeric_hybrid`.

## Question

Can an independent scalar authority layer reconstruct the exact typed scalar state from source text and target context, preserving entity, metric, unit, interval bounds, and exactness, and refuse a measured atom with any material field changed?

## Frozen clean jurisdiction

Representative qualified forms include:
- exact integer and decimal percentage points;
- closed numeric range;
- exact count;
- exact Celsius and Fahrenheit values;
- approximate percentage with `exact=False`;
- terse field notation;
- plus/minus uncertainty represented as a non-exact closed interval.

## Frozen mismatch falsifiers

Starting from a legitimately CLAIMED Gate-1A measurement, the evaluator mutates:
- entity;
- metric;
- unit;
- point value;
- interval low bound;
- interval high bound;
- exactness flag.

## Warrant contract

A candidate receives source text, the typed scalar target, and the measured `ScalarAtom`.
It may warrant only if it independently reconstructs the same exact `ScalarAtom` without calling the Gate-1A measurement function.

No unit conversion is allowed in RC0. Exactness is semantic state, not metadata that may be dropped.

## Acceptance

`SUPPORTED_GATE1B_SCALAR_RC0` requires every clean case to warrant, every frozen mutation to refuse, replay to be deterministic, a trust-measurement weak authority to be detected, and Gate-1A / production files to remain unchanged.

Broad pressure testing is deferred until all families are finalized.
