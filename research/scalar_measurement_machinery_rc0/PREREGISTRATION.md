# CAL Scalar Measurement Machinery RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

Parent: terminal scalar Gate-0 branch head `43bd155f3dee17d4b7271412927466c904a7f2fd`.
Qualified typed-contract authority remains exact Gate-0 head `c3b7e13d8940f20fcd476eb6b96f276e78e309ec`.

## Question

Given a typed scalar target `(entity, metric, unit)`, what measurement machinery can safely recover exact points or bounded intervals from ordinary evidence text without turning unrelated numbers, unit conversions, quantitative-change statements, uncertainty, attribution, or modal language into scalar authority?

Candidate mechanisms will compare:

1. target-aware bounded numeric grammar;
2. broad first-number extraction;
3. a safety-gated numeric hybrid.

The target context is an input to measurement. A number does not become a scalar fact merely by occurring in an admitted passage.

## Claim-shape buckets

### MUST_HANDLE

- exact integer and decimal percentages;
- exact counts;
- exact temperature, mass, and duration values;
- closed `between X and Y` and `from X to Y` intervals;
- alternate direct verb `measured`.

### DIAGNOSTIC

- `approximately` / `about` with exactness preserved as false;
- written `percent`;
- terse field notation;
- alternate possessive/of syntax;
- plus/minus uncertainty represented conservatively as a non-exact bounded interval.

### FAIL_CLOSED

- dates and version numbers;
- quantitative change statements;
- percentage-point change;
- open inequalities not representable by the Gate-0 finite interval contract;
- reporting/attribution;
- epistemic modal values;
- disjunctions;
- multiple temporal states;
- wrong metric/entity;
- unit conversion or mismatch;
- mixed-unit ranges.

## Frozen proposal type

A claimed proposal contains:

- entity;
- metric;
- unit;
- low exact rational value;
- high exact rational value;
- `exact: bool`.

`exact=False` means the surface itself does not establish exact equality. It does not encode a probability distribution.

## Acceptance rule

A machinery path is `QUALIFIABLE_FOR_GATE1B` only if:

- every MUST_HANDLE case is exact;
- no FAIL_CLOSED case is claimed;
- every claimed DIAGNOSTIC is exact against its frozen proposal;
- deterministic replay is exact;
- frozen metamorphic controls pass;
- production `src/` is unchanged.

Diagnostic recall cannot offset unsafe claims.

## Weak strategies

The evaluator must kill at least:

- first-number-as-target-value;
- unit erasure;
- metric/entity erasure;
- approximation-as-exact;
- range-midpoint collapse.

## Non-claims

This experiment does not establish unit conversion, tolerance policy, significant figures, uncertainty propagation, source-completion warrant, quantitative-change composition, production plugin behavior, Contract C/Decision behavior, merge, or release.
