# Semantic Authority Machinery RC8 — Preregistration

## Classification

Draft Research Infrastructure / authority-architecture discrimination.

No production CAL semantics, Contract B, Contract C, release, downstream policy, or production branch is in scope.

## Live authority at programme start

- CAL production `main`: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- parent capability synthesis: `b628f8c35fe803ea6fba99449af5de313f0e2935`
- Contract B 1.2.0 canonical promotion: `c314e53bd91c0736aa4370a364673b069aceb43e`
- Contract C 1.0.0 immutable release: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`

## Decision question

Is the smallest formally sufficient CAL semantic-authority gate a typed, domain-bound receipt with:

1. evidence admission/binding;
2. source assertion/scope status;
3. operator domain, governed span, and applicability;
4. per-material-field interpretation status/value binding;
5. explicit composition state when composition is required;
6. explicit aperture state when aperture is required;
7. a separate execution state;
8. an authority result of `WARRANTED`, `REJECTED`, or `UNRESOLVED` with typed reasons?

The competing weak hypotheses are that authority can be safely granted by evidence presence, family recognition, collapsed unknown state, reader/instrument agreement, or one scalar/boolean authority signal.

## Development-aperture deviation

Before this durable preregistration, a local prototype of the formal gate and the open qualification mutations was executed during apparatus development. That prototype run is **not scientific evidence and is not counted**. It means the qualification fixtures are acceptance controls, not a blind cohort.

The prospective evidence phase therefore begins only after the candidate gate is durably frozen in GitHub. A fresh held-out authority-mutation cohort must be added only after that freeze, and candidate bytes must not change after held-out reveal. Any candidate change after reveal requires a successor experiment.

## Why this experiment is smaller than another language experiment

The current failure is not lack of semantic proposal coverage. RC7D/RC7E show that additional readers/instruments can increase proposal recall while increasing unsafe authorization. RC7F-A1 shows high scope-path accuracy can coexist with unsafe false permits. This experiment therefore freezes language discovery out of the question and tests only the authority transition over explicit typed receipts.

## Authority state model under test

Execution is orthogonal:

- `completed`: authority may be assessed;
- `failed`: no authority assessment exists.

When execution completes, authority is exactly one of:

- `WARRANTED`: the proposed atom is fully supported within the tested authority boundary;
- `REJECTED`: positive evidence establishes that the proposal exceeds or conflicts with the source/operator warrant;
- `UNRESOLVED`: the source/operator/interpretation/composition state does not justify either warrant or rejection.

`semantic_unknown` is a source-established typed value, not an extraction failure. It may participate in a warranted atom only when the proposal itself is the matching unknown-valued semantic fact.

The following remain distinct fail-closed reasons even when their immediate consequence is the same:

- source assertion unresolved;
- operator applicability unknown;
- extraction unresolved;
- insufficient interpretation authority;
- composition unresolved;
- aperture unresolved.

Execution failure is not one of these reasons; it prevents authority assessment.

## Qualification controls

The open qualification cohort mutates one authority-relevant axis at a time, including:

- source span;
- narrator/assertion scope;
- entity;
- population;
- predicate;
- polarity;
- role direction;
- subclass direction;
- quantifier;
- permission status;
- exception attachment;
- temporal attachment;
- numeric value;
- unit;
- comparison direction;
- necessary/sufficient direction;
- unsupported extra modifier;
- out-of-jurisdiction family;
- operator applicability;
- extraction unresolved;
- insufficient authority;
- source-established semantic unknown;
- required-field absence;
- composition state;
- aperture dependence;
- execution failure;
- evidence admission;
- irrelevant instrument/reader-bank growth.

Qualification succeeds only if every intentionally weak authority architecture produces at least one unsafe warranted atom.

## Candidate freeze

After qualification, add exactly one model-free candidate gate. Freeze it in GitHub before adding the held-out cohort. Record the candidate commit and file digest. The held-out workflow must verify the candidate file is byte-identical to that freeze.

## Prospective held-out phase

The held-out corpus must:

- use explicit typed authority receipts rather than natural-language extraction;
- contain multiple bounded semantic families;
- include fresh single-axis and combined authority mutations;
- include direct assertion, embedded/non-asserted, and unresolved assertion controls;
- include applicability, field-status, per-field value, composition, and aperture controls;
- include irrelevant-instrument and agreement-bank expansions;
- never let reader count, confidence, or instrument count establish authority;
- score execution state separately from authority state.

## Primary hard success criterion

**Unsafe warranted atoms = 0.**

Any semantically unsupported atom receiving `WARRANTED` falsifies the candidate, regardless of aggregate accuracy.

## Secondary metrics

Report separately:

- warranted precision;
- warranted recall;
- unsafe warranted atoms;
- false warranted semantic dimensions;
- unresolved rate;
- incorrect rejection rate;
- field/reason localization;
- mutation behavior;
- applicability errors;
- composition errors;
- authority-monotonicity violations under instrument/reader-bank growth.

## Authority monotonicity invariant

Adding an irrelevant instrument, an additional reader, or agreement about the same proposal must not strengthen authority unless the new input contributes a separately legitimate source/warrant fact. Reader count and instrument count are not authority-bearing fields in the candidate.

## Stopping rule

- If any held-out unsupported atom becomes `WARRANTED`, preserve the counterexample and stop this candidate as falsified.
- If the formal gate passes, the result supports only the typed authority-transition architecture. It does not establish natural-language recovery of receipts or production readiness.
- Do not repair the frozen candidate after held-out reveal.
- A fresh independent implementation is a later gate only if this formal architecture survives and an independence claim becomes material.
