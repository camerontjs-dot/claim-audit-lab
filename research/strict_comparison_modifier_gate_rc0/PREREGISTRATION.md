# CAL Strict Comparison Modifier Eligibility Gate RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / successor design after PR #141 pressure falsification.

## Frozen parent

- CAL V1 RC1 semantic implementation: `a902621e8baea3063dddd7f92ba975aade305464`
- parent pressure falsification: PR #141
- parent unsafe classes: relation negation, epistemic modality, attribution/reporting.

Production `src/` remains unchanged.

## Hypothesis

The strict-comparison family does not need a more permissive comparator. It needs a separate eligibility boundary that determines whether a measured comparison is a bounded direct narrator-level assertion eligible to proceed toward semantic warrant.

The candidate gate is intentionally conservative. It rejects text containing material states the current strict-comparison atom cannot represent:

- relation negation;
- epistemic modality / uncertainty;
- attribution / reporting;
- conditionality;
- unsupported conjunction/disjunction;
- quotation/question surfaces.

Degree modifiers that preserve comparison sign, such as `slightly` or `substantially`, are not rejected solely for being modifiers.

## Architecture under test

```
raw passage
  -> frozen RC1 strict-comparison measurement
  -> modifier/assertion eligibility gate
       reject -> NOT_CHECKABLE / no warrant
       admit  -> frozen RC1 source completion + authority
  -> proposition-relative relation
  -> composition
```

The eligibility gate is not semantic authority itself. It only establishes jurisdiction for the existing source-completion/warrant path.

## Development evidence allowed before freeze

The six PR #141 unsafe strings may be used to shape the candidate because they are already revealed failures. They cannot be used as fresh qualification evidence.

A fresh pressure cohort must be added only after this candidate is frozen.

## Falsifiers for the fresh cohort

The candidate is falsified if any fresh modifier/scope pressure case reaches a deciding SUPPORTS/REFUTES conclusion.

The candidate is also weakened if it blocks all fresh direct positive controls; fail-closed safety alone is insufficient if the bounded family becomes vacuous.

No post-reveal candidate repair is permitted inside RC0.
